import ast
import logging
import os
import pathlib
import tempfile
from concurrent import futures
from datetime import datetime
from datetime import timezone
from threading import Lock
from threading import Thread
from threading import Timer
from time import sleep
from types import FunctionType
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import grpc
import numpy
import pandas
import psutil
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2
from grpc_health.v1 import health_pb2_grpc
from grpc_reflection.v1alpha import reflection
from prometheus_client import Gauge
from prometheus_client import start_http_server
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor
from statsd import StatsClient

from tecton_core.realtime_context import RealtimeContext
from tecton_proto.args.pipeline__client_pb2 import Pipeline
from tecton_proto.args.transformation__client_pb2 import TransformationMode
from tecton_proto.common.id__client_pb2 import Id
from tecton_proto.feature_server.transform import transform_service__client_pb2 as transform_service_pb2
from tecton_proto.feature_server.transform import transform_service__client_pb2_grpc as transform_service_pb2_grpc
from tecton_proto.feature_server.transform import transform_value__client_pb2 as transform_value_pb2


logger = logging.getLogger(__name__)

# Prometheus Gauges for System Metrics
cpu_usage_gauge = Gauge("transform_server_cpu_usage_percentage", "CPU Usage of the Transform Server", ["group_name"])

memory_usage_gauge = Gauge(
    "transform_server_memory_usage_percentage", "Memory Usage of the Transform Server", ["group_name"]
)
memory_total_gauge = Gauge("transform_server_memory_total", "Total Memory of the Transform Server", ["group_name"])
memory_available_gauge = Gauge(
    "transform_server_memory_available", "Available Memory of the Transform Server", ["group_name"]
)
swap_memory_usage_gauge = Gauge(
    "transform_server_swap_memory_usage_percentage", "Swap Memory Usage of the Transform Server", ["group_name"]
)
swap_memory_used_gauge = Gauge(
    "transform_server_swap_memory_used", "Used Swap Memory of the Transform Server", ["group_name"]
)
disk_usage_gauge = Gauge("transform_server_disk_usage_percentage", "Disk Usage of the Transform Server", ["group_name"])
disk_total_gauge = Gauge(
    "transform_server_disk_usage_total", "Total Disk Space of the Transform Server", ["group_name"]
)
disk_free_gauge = Gauge("transform_server_disk_usage_free", "Free Disk Space of the Transform Server", ["group_name"])
process_count_gauge = Gauge("transform_server_process_count", "Process Count of the Transform Server", ["group_name"])
threadpool_utilization_gauge = Gauge(
    "transform_server_threadpool_utilization_percentage",
    "Threadpool Utilization Percentage of the Transform Server",
    ["group_name"],
)
total_threads_gauge = Gauge(
    "transform_server_total_threads", "Total Thread Count in the Transform Server", ["group_name"]
)
busy_threads_gauge = Gauge("transform_server_busy_threads", "Busy Thread Count in the Transform Server", ["group_name"])


class IngestionRecord:
    def __init__(self, proto_request: transform_service_pb2.IngestionRecord, is_python_mode: bool):
        self.proto_request: transform_service_pb2.IngestionRecord = proto_request
        self.id: Id = self.proto_request.push_source_id
        self.payload = map_transform_value_to_python(self.proto_request.payload)
        if not is_python_mode:
            # In pandas mode, convert the dictionaries to dataframes with one row. Also need to convert top-level "list"
            # type values to numpy arrays for consistency with the offline behavior.
            np_arrays = convert_list_values_to_numpy_arrays(self.payload)
            self.payload = pandas.DataFrame.from_records([np_arrays])


def to_string(_id_proto: Id) -> str:
    return f"{_id_proto.most_significant_bits:016x}{_id_proto.least_significant_bits:016x}"


class UDFError(Exception):
    """An error in the definition of a UDF that could not be detected by the SDK/MDS."""


def eval_node(
    node,
    request_ds,
    intermediate_data,
    transforms: Dict[str, FunctionType],
    request_timestamp: Optional[datetime],
    is_python_mode: bool,
    ingestion_record: Optional[IngestionRecord] = None,
):
    if node.HasField("request_data_source_node"):
        return request_ds
    elif node.HasField("feature_view_node"):
        return intermediate_data[node.feature_view_node.input_name]
    elif (
        node.HasField("data_source_node")
        and ingestion_record
        and node.data_source_node.virtual_data_source_id == ingestion_record.id
    ):
        return ingestion_record.payload
    elif node.HasField("transformation_node"):
        t = transforms[to_string(node.transformation_node.transformation_id)]
        args = []
        kwargs = {}
        for i in node.transformation_node.inputs:
            val = eval_node(
                i.node,
                request_ds,
                intermediate_data,
                transforms,
                request_timestamp,
                is_python_mode,
                ingestion_record=ingestion_record,
            )
            if i.HasField("arg_index"):
                args.append(val)
            elif i.HasField("arg_name"):
                kwargs[i.arg_name] = val
        return t(*args, **kwargs)
    elif node.HasField("context_node"):
        return RealtimeContext(_is_python_mode=is_python_mode, request_timestamp=request_timestamp)
    elif node.HasField("constant_node"):
        constant_node = node.constant_node
        if constant_node.HasField("string_const"):
            return constant_node.string_const
        elif constant_node.HasField("int_const"):
            return int(constant_node.int_const)
        elif constant_node.HasField("float_const"):
            return float(constant_node.float_const)
        elif constant_node.HasField("bool_const"):
            return constant_node.bool_constant
        elif constant_node.HasField("null_const"):
            return None
        msg = f"Unknown ConstantNode type: {constant_node}"
        raise KeyError(msg)
    else:
        msg = f"Found unexpected node type in pipeline {node}"
        raise Exception(msg)


# evaluate an individual rtfv in the feature service request
def transform(
    rtfv_request: transform_service_pb2.TransformRequest,
    request_context_input: Dict[str, Any],
    transforms: Dict[str, FunctionType],
    pipeline: Pipeline,
    is_python_mode: bool,
    request_timestamp: Optional[datetime],
) -> List:
    # Could be further optimized to clone rather than repeatedly convert from the transform proto.
    fv_intermediate_inputs: Dict[str, Any] = {
        k: map_transform_value_to_python(v) for k, v in rtfv_request.intermediate_data.items()
    }

    if not is_python_mode:
        # In pandas mode, convert the dictionaries to dataframes with one row. Also need to convert top-level "list"
        # type values to numpy arrays for consistency with the offline behavior.
        fv_intermediate_inputs = {k: convert_list_values_to_numpy_arrays(v) for k, v in fv_intermediate_inputs.items()}
        fv_intermediate_inputs = {k: pandas.DataFrame.from_records([v]) for k, v in fv_intermediate_inputs.items()}
        request_context_input = convert_list_values_to_numpy_arrays(request_context_input)
        request_context_input = pandas.DataFrame.from_records([request_context_input])

    _ingestion_record = (
        IngestionRecord(rtfv_request.ingestion_record, is_python_mode)
        if rtfv_request.HasField("ingestion_record")
        else None
    )

    out = eval_node(
        pipeline.root,
        request_context_input,
        fv_intermediate_inputs,
        transforms,
        request_timestamp,
        is_python_mode=is_python_mode,
        ingestion_record=_ingestion_record,
    )
    root_func_name = transforms[to_string(pipeline.root.transformation_node.transformation_id)].__name__

    if is_python_mode:
        if not isinstance(out, (dict, list, str)):
            msg = f"UDF for '{root_func_name}' returned type {type(out)}; expected one of type (`dict`, `list`, `str`)."
            raise UDFError(msg)
        # Prompt Feature Views can return a string
        if isinstance(out, str):
            out = {"prompt": out}
        if not isinstance(out, list):
            out = [out]
    else:
        # Convert the dataframe to a python dictionary.
        if len(out) != 1:
            root_func_name = transforms[to_string(pipeline.root.transformation_node.transformation_id)].__name__
            logger.warning(
                f"UDF for '{root_func_name}' returned a dataframe " f"with an unexpected number of rows: {len(out)}."
            )
        out = out.to_dict("records")

    return [python_to_transform_value(r, "").map_value for r in out]


# Note that this method mutates the input dictionary. It does not make a copy.
def convert_list_values_to_numpy_arrays(dictionary):
    for k, v in dictionary.items():
        if isinstance(v, list):
            dictionary[k] = numpy.array(v)
    return dictionary


class TransformServerException(Exception):
    def __init__(self, code: grpc.StatusCode, details: str):
        self.code = code
        self.details = details


# evaluate all rtfvs in the feature service request
def all_transforms(
    service_request: transform_service_pb2.ServiceRequest,
    loaded_transformations: Optional[Dict[str, FunctionType]] = None,
    loaded_transformation_modes: Optional[Dict[str, Any]] = None,
    should_cache_transformations: bool = False,
) -> transform_service_pb2.ServiceResponse:
    response = transform_service_pb2.ServiceResponse()

    transformation_modes: Dict[str, TransformationMode] = (
        loaded_transformation_modes if loaded_transformation_modes else {}
    )
    transformations: Dict[str, FunctionType] = loaded_transformations if loaded_transformations else {}

    post_processor_pipelines: Dict[str, Pipeline] = {}

    if not should_cache_transformations:
        transformations = transformations.copy()
        transformation_modes = transformation_modes.copy()

    if len(service_request.transformation_operations) > 0:
        for transformation_op in service_request.transformation_operations:
            transformation_id = to_string(transformation_op.transformation_id)
            if transformation_id in transformations:
                continue
            else:
                logger.debug(f"Encountered new transformation op {transformation_id}")
            op_scope: Dict[str, Any] = {}
            name = transformation_op.user_defined_function.name
            try:
                exec(transformation_op.user_defined_function.body, op_scope, op_scope)
            except Exception as e:
                logger.error(f"Error loading transformation {transformation_id}: {e}")
                raise TransformServerException(grpc.StatusCode.INVALID_ARGUMENT, str(e))
            transformations[transformation_id] = op_scope[name]
            print("Loaded transformation op ", transformation_id, op_scope[name])
            transformation_modes[transformation_id] = transformation_op.transformation_mode
            if transformation_op.is_post_processor_operation:
                post_processor_pipelines[to_string(transformation_op.transformation_id)] = _post_processor_pipeline(
                    transformation_op
                )

    else:
        for transformation in service_request.transformations:
            transformation_id = to_string(transformation.transformation_id)
            if transformation_id in transformations:
                logger.debug(f"Using cached transformation {transformation_id}, {transformations[transformation_id]}")
                continue
            else:
                logger.debug(f"Encountered new transformation {transformation_id}")
            scope: Dict[str, Any] = {}
            name = transformation.user_function.name
            try:
                exec(transformation.user_function.body, scope, scope)
            except Exception as e:
                logger.error(f"Error loading transformation {transformation_id}: {e}")
                raise TransformServerException(grpc.StatusCode.INVALID_ARGUMENT, str(e))
            logger.debug(f"Loaded transformation op {transformation_id}")
            transformations[transformation_id] = scope[name]
            transformation_modes[transformation_id] = transformation.transformation_mode

    request_contexts_dict = map_transform_value_to_python(service_request.request_context)

    for request in service_request.requests:
        start = datetime.now()
        fv_id: str = request.feature_view_id  # This is already a string
        pipeline = service_request.pipelines[fv_id]
        request_timestamp = None
        if service_request.HasField("request_timestamp"):
            request_timestamp = datetime.utcfromtimestamp(service_request.request_timestamp.seconds).replace(
                tzinfo=timezone.utc
            )
        try:
            output = []

            if request.HasField("post_processor_id"):
                post_processor_id = to_string(request.post_processor_id)
                post_processor_pipeline = post_processor_pipelines[post_processor_id]
                post_processor_mode = transformation_modes[post_processor_id]
                output = preprocess_request(
                    request=request,
                    request_contexts_dict=request_contexts_dict,
                    transformations=transformations,
                    post_processor_pipeline=post_processor_pipeline,
                    post_processor_mode=post_processor_mode,
                    request_timestamp=request_timestamp,
                )

            if request.HasField("feature_view_id"):
                # Post Processor is a row level transformation so the output should only have one record
                if output:
                    request.ingestion_record.payload.CopyFrom(output[0])

                # TODO(achal): Make less fragile
                root_transformation_id = to_string(pipeline.root.transformation_node.transformation_id)
                rtfv_mode = transformation_modes[root_transformation_id]
                is_python_mode = rtfv_mode == TransformationMode.TRANSFORMATION_MODE_PYTHON
                cloned_rc_input = request_contexts_dict.copy()
                output = transform(
                    request, cloned_rc_input, transformations, pipeline, is_python_mode, request_timestamp
                )

            for o in output:
                result = transform_service_pb2.TransformResponse(request_index=request.request_index, outputs=o)
                response.outputs.append(result)
        except UDFError as e:
            raise TransformServerException(grpc.StatusCode.FAILED_PRECONDITION, str(e))
        except Exception as e:
            logger.warning("Unexpected error executing ODFV", exc_info=True)
            root_func_name = transformations[
                to_string(service_request.pipelines[fv_id].root.transformation_node.transformation_id)
            ].__name__
            raise TransformServerException(
                grpc.StatusCode.INVALID_ARGUMENT, f"{type(e).__name__}: {str(e)} (when evaluating UDF {root_func_name})"
            )
        # Adds the amount of time that the actual rtfv transform took per transform request(per feature view)
        duration = datetime.now() - start
        response.execution_times[request.feature_view_id].FromTimedelta(duration)
    response.error_code = 0
    return response


def preprocess_request(
    request: transform_service_pb2.TransformRequest,
    request_contexts_dict: Dict[str, Any],
    transformations: Dict[str, FunctionType],
    post_processor_pipeline: Pipeline,
    post_processor_mode: TransformationMode,
    request_timestamp: Optional[datetime],
) -> transform_service_pb2.ServiceRequest:
    post_processor_output = []
    if request.HasField("ingestion_record") and request.HasField("post_processor_id"):
        is_python_mode = post_processor_mode == TransformationMode.TRANSFORMATION_MODE_PYTHON
        post_processor_output = transform(
            request,
            request_contexts_dict.copy(),
            transformations,
            post_processor_pipeline,
            is_python_mode,
            request_timestamp,
        )
    return post_processor_output


def map_transform_value_to_python(value: transform_value_pb2.MapTransformValue) -> Dict[str, Any]:
    return {k: transform_value_to_python(v, k) for k, v in value.value_map.items()}


def transform_value_to_python(value: transform_value_pb2.TransformValue, field_name: str):
    value_type = value.WhichOneof("value")
    if value_type == "float64_value":
        return value.float64_value
    elif value_type == "int64_value":
        return value.int64_value
    elif value_type == "timestamp_value":
        # Timestamps are always stored in UTC, so we can safely set the tzinfo explicitly here
        datetime_value = value.timestamp_value.ToDatetime()
        utc_datetime = datetime_value.replace(tzinfo=timezone.utc)
        return utc_datetime
    elif value_type == "bool_value":
        return value.bool_value
    elif value_type == "string_value":
        return value.string_value
    elif value_type == "null_value":
        return None
    elif value_type == "map_value":
        return {k: transform_value_to_python(v, k) for k, v in value.map_value.value_map.items()}
    elif value_type == "array_value":
        return [transform_value_to_python(v, field_name) for v in value.array_value.elements]
    else:
        msg = (
            f"Unexpected type `{value_type}` for field `{field_name}`: '{value}'; must be one of type `float64`, "
            f"`int64`, `bool`, `null`, `string`, `timestamp`, `array` or `map`."
        )
        raise UDFError(msg)


def python_to_transform_value(python_value, field_name: str) -> transform_value_pb2.TransformValue:
    python_type = type(python_value)
    value_proto = transform_value_pb2.TransformValue()
    if python_value is None:
        # Return nulls explicitly.
        value_proto.null_value.CopyFrom(transform_value_pb2.NullTransformValue())
    elif python_type in (float, numpy.float64, numpy.float32):
        value_proto.float64_value = python_value
    elif python_type in (int, numpy.int32, numpy.int64):
        value_proto.int64_value = python_value
    elif python_type == bool:
        value_proto.bool_value = python_value
    elif python_type == str:
        value_proto.string_value = python_value
    elif python_type in (list, numpy.ndarray):
        value_proto.array_value.elements.extend([python_to_transform_value(v, field_name) for v in python_value])
    elif python_type == dict:
        if python_value:
            for k, v in python_value.items():
                value_proto.map_value.value_map[k].CopyFrom(python_to_transform_value(v, k))
        else:
            # An empty map is distinct from null, so fill an empty map value.
            value_proto.map_value.CopyFrom(transform_value_pb2.MapTransformValue())
    elif python_type == pandas.Timestamp:
        value_proto.timestamp_value.FromMilliseconds(int(python_value.timestamp() * 1000))
    elif python_type == datetime:
        value_proto.timestamp_value.seconds = int(python_value.timestamp())
        value_proto.timestamp_value.nanos = int((python_value.timestamp() - value_proto.timestamp_value.seconds) * 1e9)
    elif pandas.api.types.is_scalar(python_value) and pandas.isna(python_value):
        # Handle pandas.NA
        # numpy.nan should not reach here. It should've been converted to Python float and handled above
        value_proto.null_value.CopyFrom(transform_value_pb2.NullTransformValue())
    else:
        msg = (
            f"Unexpected python type `{python_type}` for field `{field_name}`: '{python_value}'; must be one of type "
            f"`float`, `int`, `bool`, `str`, `list`, `dict`, `timestamp` or `datetime`."
        )
        raise UDFError(msg)
    return value_proto


class TransformServer(transform_service_pb2_grpc.TransformServiceServicer):
    def __init__(self):
        self.loaded_transformations: Dict[str, FunctionType] = {}
        self.loaded_transformation_modes: Dict[str, Any] = {}

    def Evaluate(self, request: transform_service_pb2.ServiceRequest, context):
        try:
            return all_transforms(
                request,
                loaded_transformations=self.loaded_transformations,
                loaded_transformation_modes=self.loaded_transformation_modes,
            )
        except TransformServerException as e:
            context.abort(e.code, e.details)


def _check_server_health(
    health_servicer: health.HealthServicer, server: grpc.Server, service: str, health_check_interval: int
):
    # Checks the status of the server, the different server are: STARTED, STOPPED, AND GRACE
    if server._state.stage == grpc._server._ServerStage.STARTED:
        status = health_pb2.HealthCheckResponse.SERVING
    else:
        status = health_pb2.HealthCheckResponse.NOT_SERVING

    health_servicer.set(service, status)
    Timer(
        health_check_interval, lambda: _check_server_health(health_servicer, server, service, health_check_interval)
    ).start()


class TrackingThreadPoolExecutor(futures.ThreadPoolExecutor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._busy_count = 0
        self._lock = Lock()

    def submit(self, *args, **kwargs):
        with self._lock:
            self._busy_count += 1
        future = super().submit(*args, **kwargs)
        future.add_done_callback(self._task_done)
        return future

    def _task_done(self, _):
        with self._lock:
            self._busy_count -= 1

    @property
    def busy_count(self):
        with self._lock:
            return self._busy_count


def calculate_optimal_workers():
    # Get CPU count
    cpu_count = psutil.cpu_count(logical=True)  # Use logical=True to count hyperthreads

    # Get total memory
    total_memory = psutil.virtual_memory().total
    memory_gb = total_memory / (1024**3)  # Convert bytes to GB

    # Base number of workers on CPU cores
    cpu_based_value = cpu_count + 1  # CPU cores + 1 for I/O operations

    # Memory-based calculation: Assume 512MB per worker
    memory_based_value = int(memory_gb * 2)

    # Take the minimum of CPU-based and memory-based calculations
    optimal_workers = min(cpu_based_value, memory_based_value)
    return optimal_workers


def main():
    log_filename = os.environ.get("TRANSFORM_SERVER_LOG_FILENAME")
    if log_filename is None:
        log_filename = tempfile.NamedTemporaryFile(prefix="transform_server_").name
        print(f"TRANSFORM_SERVER_LOG_DIR not set. Logging to {log_filename}")

    disable_console_logging = os.environ.get("TRANSFORM_SERVER_DISABLE_CONSOLE_LOGGING", "false") == "true"
    metrics_reporting_enabled = os.environ.get("TRANSFORM_SERVER_METRICS_REPORTING_ENABLED", "false") == "true"
    timing_historgam_enabled = os.environ.get("TRANSFORM_SERVER_TIMING_HISTOGRAM_ENABLED", "true") == "true"
    log_level = os.environ.get("TRANSFORM_SERVER_LOG_LEVEL", "INFO")
    prometheus_metrics_port = os.environ.get("TRANSFORM_SERVER_PROMETHEUS_METRICS_PORT", "50052")

    interceptors = None
    if metrics_reporting_enabled:
        start_http_server(int(prometheus_metrics_port))
        interceptors = (PromServerInterceptor(enable_handling_time_histogram=timing_historgam_enabled),)

    logging.basicConfig(
        filename=log_filename,
        level=logging.getLevelName(log_level),
        format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    if not disable_console_logging:
        console = logging.StreamHandler()
        console.setLevel(logging.getLevelName(log_level))
        # set a format which is simpler for console use
        formatter = logging.Formatter("[%(asctime)s] %(name)-12s: %(levelname)-8s %(message)s")
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger("").addHandler(console)

    if "TRANSFORM_SERVER_SOCKET" not in os.environ and "TRANSFORM_SERVER_ADDRESS" not in os.environ:
        listen = "[::]:50051"
        logger.warning(
            "Neither TRANSFORM_SERVER_SOCKET nor TRANSFORM_SERVER_ADDRESS set in the environment. Using default port 50051."
        )
    elif "TRANSFORM_SERVER_SOCKET" in os.environ:
        socket = pathlib.Path(os.environ["TRANSFORM_SERVER_SOCKET"])
        assert not socket.exists(), "TRANSFORM_SERVER_SOCKET points to an existing socket"
        listen = f"unix:/{socket.absolute()}"
    elif "TRANSFORM_SERVER_ADDRESS" in os.environ and os.environ["TRANSFORM_SERVER_ADDRESS"].isdigit():
        listen = f'[::]:{os.environ["TRANSFORM_SERVER_ADDRESS"]}'
    else:
        listen = os.environ["TRANSFORM_SERVER_ADDRESS"]

    options = []
    # Set the maximum size of a request the server can receive from the client. Defaults to 4MB.
    max_recv_length = os.environ.get("MAX_TRANSFORM_SERVICE_REQUEST_SIZE_BYTES", None)
    if max_recv_length is not None:
        options.append(("grpc.max_receive_message_length", int(max_recv_length)))

    logger.info(f"Python server starting at {listen}")

    transform_server_groups_enabled = os.environ.get("TRANSFORM_SERVER_GROUPS_ENABLED", "false") == "true"
    logger.info(f"Transform Server Groups Enabled: {transform_server_groups_enabled}")
    if transform_server_groups_enabled:
        max_workers = os.environ.get("TRANSFORM_SERVER_MAX_WORKERS", calculate_optimal_workers())
        try:
            max_workers = int(max_workers)
            logger.info(f"Using max_workers: {max_workers}")
        except ValueError:
            max_workers = calculate_optimal_workers()
            logger.warning(f"Invalid TRANSFORM_SERVER_MAX_WORKERS value. Using default: {max_workers}")
    else:
        max_workers = int(os.environ.get("TRANSFORM_SERVER_MAX_WORKERS", "2"))

    threadpool_executor = (
        TrackingThreadPoolExecutor(max_workers=max_workers)
        if transform_server_groups_enabled
        else futures.ThreadPoolExecutor(max_workers=max_workers)
    )
    server = grpc.server(
        threadpool_executor,
        options=options,
        interceptors=interceptors,
        maximum_concurrent_rpcs=max_workers if transform_server_groups_enabled else None,
    )
    server.add_insecure_port(listen)

    transform_service_pb2_grpc.add_TransformServiceServicer_to_server(TransformServer(), server)
    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)
    SERVICE_NAMES = (
        transform_service_pb2.DESCRIPTOR.services_by_name["TransformService"].full_name,
        health_pb2.DESCRIPTOR.services_by_name["Health"].full_name,
        reflection.SERVICE_NAME,
    )

    tsg_name = os.environ.get("TRANSFORM_SERVER_GROUP_NAME", "default")

    if transform_server_groups_enabled:
        health_check_interval = int(os.environ.get("TRANSFORM_SERVER_HEALTH_STATUS_UPDATE_INTERVAL", "60"))
        metrics_reporting_frequency = int(os.environ.get("TRANSFORM_SERVER_METRICS_REPORTING_FREQUENCY", "60"))

        def report_metrics(system_metrics_reporting_enabled=False):
            while True:
                statsd_client = StatsClient("host.docker.internal", 8125)
                # Threadpool Utilization Metrics
                busy_threads = threadpool_executor.busy_count
                busy_percentage = (busy_threads / max_workers) * 100
                statsd_client.gauge("transform_server.busy_percentage", busy_percentage)

                if system_metrics_reporting_enabled:
                    # Threadpool Utilization Metrics
                    total_threads_gauge.labels(group_name=tsg_name).set(max_workers)
                    busy_threads_gauge.labels(group_name=tsg_name).set(busy_threads)
                    threadpool_utilization_gauge.labels(group_name=tsg_name).set(busy_percentage)
                    # Memory Utilization Metrics
                    memory = psutil.virtual_memory()
                    memory_usage_gauge.labels(group_name=tsg_name).set(memory.percent)
                    memory_total_gauge.labels(group_name=tsg_name).set(memory.total)
                    memory_available_gauge.labels(group_name=tsg_name).set(memory.available)

                    # Swap Memory Utilization Metrics
                    swap_memory = psutil.swap_memory()
                    swap_memory_usage_gauge.labels(group_name=tsg_name).set(swap_memory.percent)
                    swap_memory_used_gauge.labels(group_name=tsg_name).set(swap_memory.used)

                    # Disk Utilization Metrics
                    disk = psutil.disk_usage("/")
                    disk_usage_gauge.labels(group_name=tsg_name).set(disk.percent)
                    disk_total_gauge.labels(group_name=tsg_name).set(disk.total)
                    disk_free_gauge.labels(group_name=tsg_name).set(disk.free)

                    # Process Count
                    process_count = len(psutil.pids())
                    process_count_gauge.labels(group_name=tsg_name).set(process_count)

                    # CPU Utilization Metrics
                    cpu_usage = psutil.cpu_percent()
                    cpu_usage_gauge.labels(group_name=tsg_name).set(cpu_usage)

                sleep(metrics_reporting_frequency)

        _check_server_health(
            health_servicer,
            server,
            transform_service_pb2.DESCRIPTOR.services_by_name["TransformService"].full_name,
            health_check_interval,
        )

        metrics_thread = Thread(target=report_metrics, args=(metrics_reporting_enabled,), daemon=True)
        metrics_thread.start()

    reflection.enable_server_reflection(SERVICE_NAMES, server)

    server.start()
    logger.info("Python server started")
    server.wait_for_termination()


def _post_processor_pipeline(post_processor: transform_service_pb2.TransformationOperation):
    pipeline = Pipeline()
    pipeline.root.transformation_node.transformation_id.CopyFrom(post_processor.transformation_id)
    input = pipeline.root.transformation_node.inputs.add()
    input.arg_name = _get_param_name_for_function(post_processor)
    input.node.data_source_node.virtual_data_source_id.CopyFrom(post_processor.transformation_id)
    return pipeline


def _get_param_name_for_function(post_processor):
    parsed_ast = ast.parse(post_processor.user_defined_function.body)
    input_name = next(node.args.args[0].arg for node in ast.walk(parsed_ast) if isinstance(node, ast.FunctionDef))
    return input_name


if __name__ == "__main__":
    main()
