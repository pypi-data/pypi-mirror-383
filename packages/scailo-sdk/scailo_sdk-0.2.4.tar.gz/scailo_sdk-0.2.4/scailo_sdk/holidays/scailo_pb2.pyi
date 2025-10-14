from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HOLIDAY_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    HOLIDAY_SORT_KEY_ID_UNSPECIFIED: _ClassVar[HOLIDAY_SORT_KEY]
    HOLIDAY_SORT_KEY_CREATED_AT: _ClassVar[HOLIDAY_SORT_KEY]
    HOLIDAY_SORT_KEY_MODIFIED_AT: _ClassVar[HOLIDAY_SORT_KEY]
    HOLIDAY_SORT_KEY_APPROVED_ON: _ClassVar[HOLIDAY_SORT_KEY]
    HOLIDAY_SORT_KEY_APPROVED_BY: _ClassVar[HOLIDAY_SORT_KEY]
    HOLIDAY_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[HOLIDAY_SORT_KEY]
    HOLIDAY_SORT_KEY_COMPLETED_ON: _ClassVar[HOLIDAY_SORT_KEY]
    HOLIDAY_SORT_KEY_TITLE: _ClassVar[HOLIDAY_SORT_KEY]
    HOLIDAY_SORT_KEY_DESCRIPTION: _ClassVar[HOLIDAY_SORT_KEY]
    HOLIDAY_SORT_KEY_START_ON: _ClassVar[HOLIDAY_SORT_KEY]
    HOLIDAY_SORT_KEY_END_ON: _ClassVar[HOLIDAY_SORT_KEY]
HOLIDAY_SORT_KEY_ID_UNSPECIFIED: HOLIDAY_SORT_KEY
HOLIDAY_SORT_KEY_CREATED_AT: HOLIDAY_SORT_KEY
HOLIDAY_SORT_KEY_MODIFIED_AT: HOLIDAY_SORT_KEY
HOLIDAY_SORT_KEY_APPROVED_ON: HOLIDAY_SORT_KEY
HOLIDAY_SORT_KEY_APPROVED_BY: HOLIDAY_SORT_KEY
HOLIDAY_SORT_KEY_APPROVER_ROLE_ID: HOLIDAY_SORT_KEY
HOLIDAY_SORT_KEY_COMPLETED_ON: HOLIDAY_SORT_KEY
HOLIDAY_SORT_KEY_TITLE: HOLIDAY_SORT_KEY
HOLIDAY_SORT_KEY_DESCRIPTION: HOLIDAY_SORT_KEY
HOLIDAY_SORT_KEY_START_ON: HOLIDAY_SORT_KEY
HOLIDAY_SORT_KEY_END_ON: HOLIDAY_SORT_KEY

class HolidaysServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "title", "description", "start_on", "end_on")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    START_ON_FIELD_NUMBER: _ClassVar[int]
    END_ON_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    title: str
    description: str
    start_on: int
    end_on: int
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., start_on: _Optional[int] = ..., end_on: _Optional[int] = ...) -> None: ...

class HolidaysServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "title", "description", "start_on", "end_on")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    START_ON_FIELD_NUMBER: _ClassVar[int]
    END_ON_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    title: str
    description: str
    start_on: int
    end_on: int
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., start_on: _Optional[int] = ..., end_on: _Optional[int] = ...) -> None: ...

class Holiday(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "title", "description", "start_on", "end_on", "list")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    START_ON_FIELD_NUMBER: _ClassVar[int]
    END_ON_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    completed_on: int
    vault_folder_id: int
    title: str
    description: str
    start_on: int
    end_on: int
    list: _containers.RepeatedCompositeFieldContainer[HolidayShiftGroup]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., start_on: _Optional[int] = ..., end_on: _Optional[int] = ..., list: _Optional[_Iterable[_Union[HolidayShiftGroup, _Mapping]]] = ...) -> None: ...

class HolidaysServiceShiftGroupCreateRequest(_message.Message):
    __slots__ = ("user_comment", "holiday_id", "shift_group_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    HOLIDAY_ID_FIELD_NUMBER: _ClassVar[int]
    SHIFT_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    holiday_id: int
    shift_group_id: int
    def __init__(self, user_comment: _Optional[str] = ..., holiday_id: _Optional[int] = ..., shift_group_id: _Optional[int] = ...) -> None: ...

class HolidaysServiceShiftGroupUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "holiday_id", "shift_group_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    HOLIDAY_ID_FIELD_NUMBER: _ClassVar[int]
    SHIFT_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    holiday_id: int
    shift_group_id: int
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., holiday_id: _Optional[int] = ..., shift_group_id: _Optional[int] = ...) -> None: ...

class HolidayShiftGroup(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "holiday_id", "shift_group_id")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    HOLIDAY_ID_FIELD_NUMBER: _ClassVar[int]
    SHIFT_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    holiday_id: int
    shift_group_id: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., holiday_id: _Optional[int] = ..., shift_group_id: _Optional[int] = ...) -> None: ...

class HolidaysList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[Holiday]
    def __init__(self, list: _Optional[_Iterable[_Union[Holiday, _Mapping]]] = ...) -> None: ...

class HolidaysShiftsGroupsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[HolidayShiftGroup]
    def __init__(self, list: _Optional[_Iterable[_Union[HolidayShiftGroup, _Mapping]]] = ...) -> None: ...

class HolidaysShiftsGroupsHistoryRequest(_message.Message):
    __slots__ = ("holiday_id", "shift_group_id")
    HOLIDAY_ID_FIELD_NUMBER: _ClassVar[int]
    SHIFT_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    holiday_id: int
    shift_group_id: int
    def __init__(self, holiday_id: _Optional[int] = ..., shift_group_id: _Optional[int] = ...) -> None: ...

class HolidaysServicePaginationReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "status")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: HOLIDAY_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[HOLIDAY_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class HolidaysServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[Holiday]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[Holiday, _Mapping]]] = ...) -> None: ...

class HolidaysServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "title", "description", "start_on_start", "start_on_end", "end_on_start", "end_on_end")
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
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_START_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_END_FIELD_NUMBER: _ClassVar[int]
    APPROVED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVER_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_START_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_END_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    START_ON_START_FIELD_NUMBER: _ClassVar[int]
    START_ON_END_FIELD_NUMBER: _ClassVar[int]
    END_ON_START_FIELD_NUMBER: _ClassVar[int]
    END_ON_END_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: HOLIDAY_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    completed_on_start: int
    completed_on_end: int
    title: str
    description: str
    start_on_start: int
    start_on_end: int
    end_on_start: int
    end_on_end: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[HOLIDAY_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., start_on_start: _Optional[int] = ..., start_on_end: _Optional[int] = ..., end_on_start: _Optional[int] = ..., end_on_end: _Optional[int] = ...) -> None: ...

class HolidaysServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "title", "description", "start_on_start", "start_on_end", "end_on_start", "end_on_end")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_START_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_END_FIELD_NUMBER: _ClassVar[int]
    APPROVED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVER_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_START_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_END_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    START_ON_START_FIELD_NUMBER: _ClassVar[int]
    START_ON_END_FIELD_NUMBER: _ClassVar[int]
    END_ON_START_FIELD_NUMBER: _ClassVar[int]
    END_ON_END_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    completed_on_start: int
    completed_on_end: int
    title: str
    description: str
    start_on_start: int
    start_on_end: int
    end_on_start: int
    end_on_end: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., start_on_start: _Optional[int] = ..., start_on_end: _Optional[int] = ..., end_on_start: _Optional[int] = ..., end_on_end: _Optional[int] = ...) -> None: ...

class HolidaysServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: HOLIDAY_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[HOLIDAY_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ...) -> None: ...

class HolidaysServiceViewHolidaysOnTimestampRequest(_message.Message):
    __slots__ = ("timestamp", "shift_group_id")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    SHIFT_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    shift_group_id: int
    def __init__(self, timestamp: _Optional[int] = ..., shift_group_id: _Optional[int] = ...) -> None: ...
