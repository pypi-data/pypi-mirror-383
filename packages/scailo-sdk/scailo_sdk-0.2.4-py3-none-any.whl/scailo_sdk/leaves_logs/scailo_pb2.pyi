from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LEAVE_LOG_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LEAVE_LOG_SORT_KEY_ID_UNSPECIFIED: _ClassVar[LEAVE_LOG_SORT_KEY]
    LEAVE_LOG_SORT_KEY_CREATED_AT: _ClassVar[LEAVE_LOG_SORT_KEY]
    LEAVE_LOG_SORT_KEY_MODIFIED_AT: _ClassVar[LEAVE_LOG_SORT_KEY]
    LEAVE_LOG_SORT_KEY_USER_ID: _ClassVar[LEAVE_LOG_SORT_KEY]
    LEAVE_LOG_SORT_KEY_UOM_ID: _ClassVar[LEAVE_LOG_SORT_KEY]
    LEAVE_LOG_SORT_KEY_LEAVE_TYPE_ID: _ClassVar[LEAVE_LOG_SORT_KEY]
    LEAVE_LOG_SORT_KEY_QUANTITY: _ClassVar[LEAVE_LOG_SORT_KEY]
    LEAVE_LOG_SORT_KEY_REF_FROM: _ClassVar[LEAVE_LOG_SORT_KEY]
LEAVE_LOG_SORT_KEY_ID_UNSPECIFIED: LEAVE_LOG_SORT_KEY
LEAVE_LOG_SORT_KEY_CREATED_AT: LEAVE_LOG_SORT_KEY
LEAVE_LOG_SORT_KEY_MODIFIED_AT: LEAVE_LOG_SORT_KEY
LEAVE_LOG_SORT_KEY_USER_ID: LEAVE_LOG_SORT_KEY
LEAVE_LOG_SORT_KEY_UOM_ID: LEAVE_LOG_SORT_KEY
LEAVE_LOG_SORT_KEY_LEAVE_TYPE_ID: LEAVE_LOG_SORT_KEY
LEAVE_LOG_SORT_KEY_QUANTITY: LEAVE_LOG_SORT_KEY
LEAVE_LOG_SORT_KEY_REF_FROM: LEAVE_LOG_SORT_KEY

class LeavesLogsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_id", "uom_id", "ref_from", "ref_id", "leave_type_id", "quantity")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    LEAVE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_id: int
    uom_id: int
    ref_from: str
    ref_id: int
    leave_type_id: int
    quantity: int
    def __init__(self, entity_uuid: _Optional[str] = ..., user_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., leave_type_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class LeaveLog(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_id", "uom_id", "ref_from", "ref_id", "leave_type_id", "quantity")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    LEAVE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_id: int
    uom_id: int
    ref_from: str
    ref_id: int
    leave_type_id: int
    quantity: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., leave_type_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class LeavesLogsCountEmployeeLeavesRequest(_message.Message):
    __slots__ = ("user_id", "leave_type_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    LEAVE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: int
    leave_type_id: int
    def __init__(self, user_id: _Optional[int] = ..., leave_type_id: _Optional[int] = ...) -> None: ...

class LeavesLogsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[LeaveLog]
    def __init__(self, list: _Optional[_Iterable[_Union[LeaveLog, _Mapping]]] = ...) -> None: ...

class LeavesLogsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "user_id", "uom_id", "ref_from", "ref_id", "leave_type_id", "quantity_min", "quantity_max")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    LEAVE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_MIN_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_MAX_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: LEAVE_LOG_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    user_id: int
    uom_id: int
    ref_from: str
    ref_id: int
    leave_type_id: int
    quantity_min: int
    quantity_max: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[LEAVE_LOG_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., user_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., leave_type_id: _Optional[int] = ..., quantity_min: _Optional[int] = ..., quantity_max: _Optional[int] = ...) -> None: ...

class LeavesLogsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "user_id", "uom_id", "ref_from", "ref_id", "leave_type_id", "quantity_min", "quantity_max")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    LEAVE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_MIN_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_MAX_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    user_id: int
    uom_id: int
    ref_from: str
    ref_id: int
    leave_type_id: int
    quantity_min: int
    quantity_max: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., user_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., leave_type_id: _Optional[int] = ..., quantity_min: _Optional[int] = ..., quantity_max: _Optional[int] = ...) -> None: ...
