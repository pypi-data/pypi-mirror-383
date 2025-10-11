from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.spark_common import clusters__client_pb2 as _clusters__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor
JOB_METADATA_TABLE_TYPE_DYNAMO: JobMetadataTableType
JOB_METADATA_TABLE_TYPE_GCS: JobMetadataTableType
JOB_METADATA_TABLE_TYPE_UNSPECIFIED: JobMetadataTableType
OFFLINE_STORE_TYPE_DBFS: OfflineStoreType
OFFLINE_STORE_TYPE_GCS: OfflineStoreType
OFFLINE_STORE_TYPE_S3: OfflineStoreType
OFFLINE_STORE_TYPE_UNSPECIFIED: OfflineStoreType
ONLINE_STORE_TYPE_BIGTABLE: OnlineStoreType
ONLINE_STORE_TYPE_DYNAMO: OnlineStoreType
ONLINE_STORE_TYPE_REDIS: OnlineStoreType
ONLINE_STORE_TYPE_UNSPECIFIED: OnlineStoreType

class ComputeConsumptionInfo(_message.Message):
    __slots__ = ["compute_usage", "duration"]
    COMPUTE_USAGE_FIELD_NUMBER: ClassVar[int]
    DURATION_FIELD_NUMBER: ClassVar[int]
    compute_usage: _containers.RepeatedCompositeFieldContainer[ComputeUsage]
    duration: _duration_pb2.Duration
    def __init__(self, duration: Optional[Union[_duration_pb2.Duration, Mapping]] = ..., compute_usage: Optional[Iterable[Union[ComputeUsage, Mapping]]] = ...) -> None: ...

class ComputeUsage(_message.Message):
    __slots__ = ["instance_availability", "instance_count", "instance_type"]
    INSTANCE_AVAILABILITY_FIELD_NUMBER: ClassVar[int]
    INSTANCE_COUNT_FIELD_NUMBER: ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: ClassVar[int]
    instance_availability: _clusters__client_pb2.AwsAvailability
    instance_count: int
    instance_type: str
    def __init__(self, instance_availability: Optional[Union[_clusters__client_pb2.AwsAvailability, str]] = ..., instance_type: Optional[str] = ..., instance_count: Optional[int] = ...) -> None: ...

class JobMetadata(_message.Message):
    __slots__ = ["materialization_consumption_info", "online_store_copier_execution_info", "spark_execution_info", "tecton_managed_info"]
    MATERIALIZATION_CONSUMPTION_INFO_FIELD_NUMBER: ClassVar[int]
    ONLINE_STORE_COPIER_EXECUTION_INFO_FIELD_NUMBER: ClassVar[int]
    SPARK_EXECUTION_INFO_FIELD_NUMBER: ClassVar[int]
    TECTON_MANAGED_INFO_FIELD_NUMBER: ClassVar[int]
    materialization_consumption_info: MaterializationConsumptionInfo
    online_store_copier_execution_info: OnlineStoreCopierExecutionInfo
    spark_execution_info: SparkJobExecutionInfo
    tecton_managed_info: TectonManagedInfo
    def __init__(self, online_store_copier_execution_info: Optional[Union[OnlineStoreCopierExecutionInfo, Mapping]] = ..., spark_execution_info: Optional[Union[SparkJobExecutionInfo, Mapping]] = ..., tecton_managed_info: Optional[Union[TectonManagedInfo, Mapping]] = ..., materialization_consumption_info: Optional[Union[MaterializationConsumptionInfo, Mapping]] = ...) -> None: ...

class MaterializationConsumptionInfo(_message.Message):
    __slots__ = ["compute_consumption", "offline_store_consumption", "online_store_consumption"]
    COMPUTE_CONSUMPTION_FIELD_NUMBER: ClassVar[int]
    OFFLINE_STORE_CONSUMPTION_FIELD_NUMBER: ClassVar[int]
    ONLINE_STORE_CONSUMPTION_FIELD_NUMBER: ClassVar[int]
    compute_consumption: ComputeConsumptionInfo
    offline_store_consumption: OfflineStoreWriteConsumptionInfo
    online_store_consumption: OnlineStoreWriteConsumptionInfo
    def __init__(self, offline_store_consumption: Optional[Union[OfflineStoreWriteConsumptionInfo, Mapping]] = ..., online_store_consumption: Optional[Union[OnlineStoreWriteConsumptionInfo, Mapping]] = ..., compute_consumption: Optional[Union[ComputeConsumptionInfo, Mapping]] = ...) -> None: ...

class OfflineConsumptionBucket(_message.Message):
    __slots__ = ["features_written", "rows_written"]
    FEATURES_WRITTEN_FIELD_NUMBER: ClassVar[int]
    ROWS_WRITTEN_FIELD_NUMBER: ClassVar[int]
    features_written: int
    rows_written: int
    def __init__(self, rows_written: Optional[int] = ..., features_written: Optional[int] = ...) -> None: ...

class OfflineStoreWriteConsumptionInfo(_message.Message):
    __slots__ = ["consumption_info", "offline_store_type"]
    class ConsumptionInfoEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: int
        value: OfflineConsumptionBucket
        def __init__(self, key: Optional[int] = ..., value: Optional[Union[OfflineConsumptionBucket, Mapping]] = ...) -> None: ...
    CONSUMPTION_INFO_FIELD_NUMBER: ClassVar[int]
    OFFLINE_STORE_TYPE_FIELD_NUMBER: ClassVar[int]
    consumption_info: _containers.MessageMap[int, OfflineConsumptionBucket]
    offline_store_type: OfflineStoreType
    def __init__(self, consumption_info: Optional[Mapping[int, OfflineConsumptionBucket]] = ..., offline_store_type: Optional[Union[OfflineStoreType, str]] = ...) -> None: ...

class OnlineConsumptionBucket(_message.Message):
    __slots__ = ["features_written", "rows_written"]
    FEATURES_WRITTEN_FIELD_NUMBER: ClassVar[int]
    ROWS_WRITTEN_FIELD_NUMBER: ClassVar[int]
    features_written: int
    rows_written: int
    def __init__(self, rows_written: Optional[int] = ..., features_written: Optional[int] = ...) -> None: ...

class OnlineStoreCopierExecutionInfo(_message.Message):
    __slots__ = ["is_revoked"]
    IS_REVOKED_FIELD_NUMBER: ClassVar[int]
    is_revoked: bool
    def __init__(self, is_revoked: bool = ...) -> None: ...

class OnlineStoreWriteConsumptionInfo(_message.Message):
    __slots__ = ["consumption_info", "online_store_type"]
    class ConsumptionInfoEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: ClassVar[int]
        VALUE_FIELD_NUMBER: ClassVar[int]
        key: int
        value: OnlineConsumptionBucket
        def __init__(self, key: Optional[int] = ..., value: Optional[Union[OnlineConsumptionBucket, Mapping]] = ...) -> None: ...
    CONSUMPTION_INFO_FIELD_NUMBER: ClassVar[int]
    ONLINE_STORE_TYPE_FIELD_NUMBER: ClassVar[int]
    consumption_info: _containers.MessageMap[int, OnlineConsumptionBucket]
    online_store_type: OnlineStoreType
    def __init__(self, consumption_info: Optional[Mapping[int, OnlineConsumptionBucket]] = ..., online_store_type: Optional[Union[OnlineStoreType, str]] = ...) -> None: ...

class SparkJobExecutionInfo(_message.Message):
    __slots__ = ["is_revoked", "run_id", "stream_handoff_synchronization_info"]
    IS_REVOKED_FIELD_NUMBER: ClassVar[int]
    RUN_ID_FIELD_NUMBER: ClassVar[int]
    STREAM_HANDOFF_SYNCHRONIZATION_INFO_FIELD_NUMBER: ClassVar[int]
    is_revoked: bool
    run_id: str
    stream_handoff_synchronization_info: StreamHandoffSynchronizationInfo
    def __init__(self, run_id: Optional[str] = ..., is_revoked: bool = ..., stream_handoff_synchronization_info: Optional[Union[StreamHandoffSynchronizationInfo, Mapping]] = ...) -> None: ...

class StreamHandoffSynchronizationInfo(_message.Message):
    __slots__ = ["new_cluster_started", "query_cancellation_complete", "query_cancellation_requested", "stream_query_start_allowed"]
    NEW_CLUSTER_STARTED_FIELD_NUMBER: ClassVar[int]
    QUERY_CANCELLATION_COMPLETE_FIELD_NUMBER: ClassVar[int]
    QUERY_CANCELLATION_REQUESTED_FIELD_NUMBER: ClassVar[int]
    STREAM_QUERY_START_ALLOWED_FIELD_NUMBER: ClassVar[int]
    new_cluster_started: bool
    query_cancellation_complete: bool
    query_cancellation_requested: bool
    stream_query_start_allowed: bool
    def __init__(self, new_cluster_started: bool = ..., stream_query_start_allowed: bool = ..., query_cancellation_requested: bool = ..., query_cancellation_complete: bool = ...) -> None: ...

class TectonManagedInfo(_message.Message):
    __slots__ = ["stages", "state"]
    STAGES_FIELD_NUMBER: ClassVar[int]
    STATE_FIELD_NUMBER: ClassVar[int]
    stages: _containers.RepeatedCompositeFieldContainer[TectonManagedStage]
    state: TectonManagedStage.State
    def __init__(self, stages: Optional[Iterable[Union[TectonManagedStage, Mapping]]] = ..., state: Optional[Union[TectonManagedStage.State, str]] = ...) -> None: ...

class TectonManagedStage(_message.Message):
    __slots__ = ["compiled_sql_query", "description", "duration", "error_detail", "error_type", "external_link", "progress", "stage_type", "start_time", "state"]
    class ErrorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class StageType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
    AGGREGATE: TectonManagedStage.StageType
    BIGQUERY: TectonManagedStage.StageType
    BULK_LOAD: TectonManagedStage.StageType
    CANCELLED: TectonManagedStage.State
    COMPILED_SQL_QUERY_FIELD_NUMBER: ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: ClassVar[int]
    DURATION_FIELD_NUMBER: ClassVar[int]
    ERROR: TectonManagedStage.State
    ERROR_DETAIL_FIELD_NUMBER: ClassVar[int]
    ERROR_TYPE_FIELD_NUMBER: ClassVar[int]
    ERROR_TYPE_UNSPECIFIED: TectonManagedStage.ErrorType
    EXTERNAL_LINK_FIELD_NUMBER: ClassVar[int]
    OFFLINE_STORE: TectonManagedStage.StageType
    ONLINE_STORE: TectonManagedStage.StageType
    PENDING: TectonManagedStage.State
    PROGRESS_FIELD_NUMBER: ClassVar[int]
    PYTHON: TectonManagedStage.StageType
    RUNNING: TectonManagedStage.State
    SNOWFLAKE: TectonManagedStage.StageType
    STAGE_TYPE_FIELD_NUMBER: ClassVar[int]
    START_TIME_FIELD_NUMBER: ClassVar[int]
    STATE_FIELD_NUMBER: ClassVar[int]
    STATE_UNSPECIFIED: TectonManagedStage.State
    SUCCESS: TectonManagedStage.State
    UNEXPECTED_ERROR: TectonManagedStage.ErrorType
    USER_ERROR: TectonManagedStage.ErrorType
    compiled_sql_query: str
    description: str
    duration: _duration_pb2.Duration
    error_detail: str
    error_type: TectonManagedStage.ErrorType
    external_link: str
    progress: float
    stage_type: TectonManagedStage.StageType
    start_time: _timestamp_pb2.Timestamp
    state: TectonManagedStage.State
    def __init__(self, stage_type: Optional[Union[TectonManagedStage.StageType, str]] = ..., state: Optional[Union[TectonManagedStage.State, str]] = ..., external_link: Optional[str] = ..., progress: Optional[float] = ..., description: Optional[str] = ..., error_type: Optional[Union[TectonManagedStage.ErrorType, str]] = ..., error_detail: Optional[str] = ..., compiled_sql_query: Optional[str] = ..., duration: Optional[Union[_duration_pb2.Duration, Mapping]] = ..., start_time: Optional[Union[_timestamp_pb2.Timestamp, Mapping]] = ...) -> None: ...

class OnlineStoreType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class OfflineStoreType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []

class JobMetadataTableType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
