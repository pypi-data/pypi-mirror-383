from tecton_proto.args import basic_info__client_pb2 as _basic_info__client_pb2
from tecton_proto.args import data_source__client_pb2 as _data_source__client_pb2
from tecton_proto.args import diff_options__client_pb2 as _diff_options__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar, Iterable, Mapping, Optional, Union

DESCRIPTOR: _descriptor.FileDescriptor

class DiffTestArgs(_message.Message):
    __slots__ = ["info", "new_field", "old_field", "options", "passive_field", "recreate_suppressable_field", "recreate_suppressable_invalidate_checkpoints_field", "recreate_suppressable_invalidate_checkpoints_nested_field", "recreate_suppressable_nested_field", "recreate_suppressable_restart_stream_field", "renamed_message_field", "renamed_primitive_field", "test_args_id", "unannotated_needing_recreate"]
    INFO_FIELD_NUMBER: ClassVar[int]
    NEW_FIELD_FIELD_NUMBER: ClassVar[int]
    OLD_FIELD_FIELD_NUMBER: ClassVar[int]
    OPTIONS_FIELD_NUMBER: ClassVar[int]
    PASSIVE_FIELD_FIELD_NUMBER: ClassVar[int]
    RECREATE_SUPPRESSABLE_FIELD_FIELD_NUMBER: ClassVar[int]
    RECREATE_SUPPRESSABLE_INVALIDATE_CHECKPOINTS_FIELD_FIELD_NUMBER: ClassVar[int]
    RECREATE_SUPPRESSABLE_INVALIDATE_CHECKPOINTS_NESTED_FIELD_FIELD_NUMBER: ClassVar[int]
    RECREATE_SUPPRESSABLE_NESTED_FIELD_FIELD_NUMBER: ClassVar[int]
    RECREATE_SUPPRESSABLE_RESTART_STREAM_FIELD_FIELD_NUMBER: ClassVar[int]
    RENAMED_MESSAGE_FIELD_FIELD_NUMBER: ClassVar[int]
    RENAMED_PRIMITIVE_FIELD_FIELD_NUMBER: ClassVar[int]
    TEST_ARGS_ID_FIELD_NUMBER: ClassVar[int]
    UNANNOTATED_NEEDING_RECREATE_FIELD_NUMBER: ClassVar[int]
    info: _basic_info__client_pb2.BasicInfo
    new_field: DiffTestFoo
    old_field: DiffTestFoo
    options: _containers.RepeatedCompositeFieldContainer[_data_source__client_pb2.Option]
    passive_field: str
    recreate_suppressable_field: str
    recreate_suppressable_invalidate_checkpoints_field: str
    recreate_suppressable_invalidate_checkpoints_nested_field: DiffTestNestedInner
    recreate_suppressable_nested_field: DiffTestNestedInner
    recreate_suppressable_restart_stream_field: str
    renamed_message_field: DiffTestNestedInner
    renamed_primitive_field: str
    test_args_id: _id__client_pb2.Id
    unannotated_needing_recreate: str
    def __init__(self, test_args_id: Optional[Union[_id__client_pb2.Id, Mapping]] = ..., info: Optional[Union[_basic_info__client_pb2.BasicInfo, Mapping]] = ..., new_field: Optional[Union[DiffTestFoo, Mapping]] = ..., old_field: Optional[Union[DiffTestFoo, Mapping]] = ..., passive_field: Optional[str] = ..., recreate_suppressable_field: Optional[str] = ..., recreate_suppressable_nested_field: Optional[Union[DiffTestNestedInner, Mapping]] = ..., recreate_suppressable_invalidate_checkpoints_field: Optional[str] = ..., recreate_suppressable_invalidate_checkpoints_nested_field: Optional[Union[DiffTestNestedInner, Mapping]] = ..., recreate_suppressable_restart_stream_field: Optional[str] = ..., unannotated_needing_recreate: Optional[str] = ..., options: Optional[Iterable[Union[_data_source__client_pb2.Option, Mapping]]] = ..., renamed_primitive_field: Optional[str] = ..., renamed_message_field: Optional[Union[DiffTestNestedInner, Mapping]] = ...) -> None: ...

class DiffTestFoo(_message.Message):
    __slots__ = ["field_a", "field_b"]
    FIELD_A_FIELD_NUMBER: ClassVar[int]
    FIELD_B_FIELD_NUMBER: ClassVar[int]
    field_a: str
    field_b: str
    def __init__(self, field_a: Optional[str] = ..., field_b: Optional[str] = ...) -> None: ...

class DiffTestNestedInner(_message.Message):
    __slots__ = ["inplace_field", "recreate_suppressable_field", "recreate_suppressable_restart_stream_field", "unannotated_field"]
    INPLACE_FIELD_FIELD_NUMBER: ClassVar[int]
    RECREATE_SUPPRESSABLE_FIELD_FIELD_NUMBER: ClassVar[int]
    RECREATE_SUPPRESSABLE_RESTART_STREAM_FIELD_FIELD_NUMBER: ClassVar[int]
    UNANNOTATED_FIELD_FIELD_NUMBER: ClassVar[int]
    inplace_field: str
    recreate_suppressable_field: str
    recreate_suppressable_restart_stream_field: str
    unannotated_field: str
    def __init__(self, inplace_field: Optional[str] = ..., recreate_suppressable_field: Optional[str] = ..., recreate_suppressable_restart_stream_field: Optional[str] = ..., unannotated_field: Optional[str] = ...) -> None: ...

class DiffTestNestedOuter(_message.Message):
    __slots__ = ["args"]
    ARGS_FIELD_NUMBER: ClassVar[int]
    args: DiffTestArgs
    def __init__(self, args: Optional[Union[DiffTestArgs, Mapping]] = ...) -> None: ...
