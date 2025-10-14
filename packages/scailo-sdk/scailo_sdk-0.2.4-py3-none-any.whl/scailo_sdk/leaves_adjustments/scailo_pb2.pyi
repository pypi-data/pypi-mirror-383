from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LEAVE_ADJUSTMENT_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LEAVE_ADJUSTMENT_SORT_KEY_ID_UNSPECIFIED: _ClassVar[LEAVE_ADJUSTMENT_SORT_KEY]
    LEAVE_ADJUSTMENT_SORT_KEY_CREATED_AT: _ClassVar[LEAVE_ADJUSTMENT_SORT_KEY]
    LEAVE_ADJUSTMENT_SORT_KEY_MODIFIED_AT: _ClassVar[LEAVE_ADJUSTMENT_SORT_KEY]
    LEAVE_ADJUSTMENT_SORT_KEY_APPROVED_ON: _ClassVar[LEAVE_ADJUSTMENT_SORT_KEY]
    LEAVE_ADJUSTMENT_SORT_KEY_APPROVED_BY: _ClassVar[LEAVE_ADJUSTMENT_SORT_KEY]
    LEAVE_ADJUSTMENT_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[LEAVE_ADJUSTMENT_SORT_KEY]
    LEAVE_ADJUSTMENT_SORT_KEY_COMPLETED_ON: _ClassVar[LEAVE_ADJUSTMENT_SORT_KEY]
    LEAVE_ADJUSTMENT_SORT_KEY_REFERENCE_ID: _ClassVar[LEAVE_ADJUSTMENT_SORT_KEY]
    LEAVE_ADJUSTMENT_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[LEAVE_ADJUSTMENT_SORT_KEY]
    LEAVE_ADJUSTMENT_SORT_KEY_USER_ID: _ClassVar[LEAVE_ADJUSTMENT_SORT_KEY]

class LEAVE_ADJUSTMENT_RECORD_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LEAVE_ADJUSTMENT_RECORD_SORT_KEY_ID_UNSPECIFIED: _ClassVar[LEAVE_ADJUSTMENT_RECORD_SORT_KEY]
    LEAVE_ADJUSTMENT_RECORD_SORT_KEY_CREATED_AT: _ClassVar[LEAVE_ADJUSTMENT_RECORD_SORT_KEY]
    LEAVE_ADJUSTMENT_RECORD_SORT_KEY_MODIFIED_AT: _ClassVar[LEAVE_ADJUSTMENT_RECORD_SORT_KEY]
    LEAVE_ADJUSTMENT_RECORD_SORT_KEY_APPROVED_ON: _ClassVar[LEAVE_ADJUSTMENT_RECORD_SORT_KEY]
    LEAVE_ADJUSTMENT_RECORD_SORT_KEY_APPROVED_BY: _ClassVar[LEAVE_ADJUSTMENT_RECORD_SORT_KEY]
    LEAVE_ADJUSTMENT_RECORD_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[LEAVE_ADJUSTMENT_RECORD_SORT_KEY]
    LEAVE_ADJUSTMENT_RECORD_SORT_KEY_LEAVE_TYPE_ID: _ClassVar[LEAVE_ADJUSTMENT_RECORD_SORT_KEY]
    LEAVE_ADJUSTMENT_RECORD_SORT_KEY_UOM_ID: _ClassVar[LEAVE_ADJUSTMENT_RECORD_SORT_KEY]
    LEAVE_ADJUSTMENT_RECORD_SORT_KEY_QUANTITY: _ClassVar[LEAVE_ADJUSTMENT_RECORD_SORT_KEY]

class LEAVE_ADJUSTMENT_RECORD_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    LEAVE_ADJUSTMENT_RECORD_STATUS_ANY_UNSPECIFIED: _ClassVar[LEAVE_ADJUSTMENT_RECORD_STATUS]
    LEAVE_ADJUSTMENT_RECORD_STATUS_APPROVED: _ClassVar[LEAVE_ADJUSTMENT_RECORD_STATUS]
    LEAVE_ADJUSTMENT_RECORD_STATUS_UNAPPROVED: _ClassVar[LEAVE_ADJUSTMENT_RECORD_STATUS]
LEAVE_ADJUSTMENT_SORT_KEY_ID_UNSPECIFIED: LEAVE_ADJUSTMENT_SORT_KEY
LEAVE_ADJUSTMENT_SORT_KEY_CREATED_AT: LEAVE_ADJUSTMENT_SORT_KEY
LEAVE_ADJUSTMENT_SORT_KEY_MODIFIED_AT: LEAVE_ADJUSTMENT_SORT_KEY
LEAVE_ADJUSTMENT_SORT_KEY_APPROVED_ON: LEAVE_ADJUSTMENT_SORT_KEY
LEAVE_ADJUSTMENT_SORT_KEY_APPROVED_BY: LEAVE_ADJUSTMENT_SORT_KEY
LEAVE_ADJUSTMENT_SORT_KEY_APPROVER_ROLE_ID: LEAVE_ADJUSTMENT_SORT_KEY
LEAVE_ADJUSTMENT_SORT_KEY_COMPLETED_ON: LEAVE_ADJUSTMENT_SORT_KEY
LEAVE_ADJUSTMENT_SORT_KEY_REFERENCE_ID: LEAVE_ADJUSTMENT_SORT_KEY
LEAVE_ADJUSTMENT_SORT_KEY_FINAL_REF_NUMBER: LEAVE_ADJUSTMENT_SORT_KEY
LEAVE_ADJUSTMENT_SORT_KEY_USER_ID: LEAVE_ADJUSTMENT_SORT_KEY
LEAVE_ADJUSTMENT_RECORD_SORT_KEY_ID_UNSPECIFIED: LEAVE_ADJUSTMENT_RECORD_SORT_KEY
LEAVE_ADJUSTMENT_RECORD_SORT_KEY_CREATED_AT: LEAVE_ADJUSTMENT_RECORD_SORT_KEY
LEAVE_ADJUSTMENT_RECORD_SORT_KEY_MODIFIED_AT: LEAVE_ADJUSTMENT_RECORD_SORT_KEY
LEAVE_ADJUSTMENT_RECORD_SORT_KEY_APPROVED_ON: LEAVE_ADJUSTMENT_RECORD_SORT_KEY
LEAVE_ADJUSTMENT_RECORD_SORT_KEY_APPROVED_BY: LEAVE_ADJUSTMENT_RECORD_SORT_KEY
LEAVE_ADJUSTMENT_RECORD_SORT_KEY_APPROVER_ROLE_ID: LEAVE_ADJUSTMENT_RECORD_SORT_KEY
LEAVE_ADJUSTMENT_RECORD_SORT_KEY_LEAVE_TYPE_ID: LEAVE_ADJUSTMENT_RECORD_SORT_KEY
LEAVE_ADJUSTMENT_RECORD_SORT_KEY_UOM_ID: LEAVE_ADJUSTMENT_RECORD_SORT_KEY
LEAVE_ADJUSTMENT_RECORD_SORT_KEY_QUANTITY: LEAVE_ADJUSTMENT_RECORD_SORT_KEY
LEAVE_ADJUSTMENT_RECORD_STATUS_ANY_UNSPECIFIED: LEAVE_ADJUSTMENT_RECORD_STATUS
LEAVE_ADJUSTMENT_RECORD_STATUS_APPROVED: LEAVE_ADJUSTMENT_RECORD_STATUS
LEAVE_ADJUSTMENT_RECORD_STATUS_UNAPPROVED: LEAVE_ADJUSTMENT_RECORD_STATUS

class LeavesAdjustmentsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "user_id", "description")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    user_id: int
    description: str
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., user_id: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class LeavesAdjustmentsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "description")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    description: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class LeaveAdjustment(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "user_id", "description", "list")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    completed_on: int
    vault_folder_id: int
    reference_id: str
    final_ref_number: str
    user_id: int
    description: str
    list: _containers.RepeatedCompositeFieldContainer[LeaveAdjustmentRecord]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., user_id: _Optional[int] = ..., description: _Optional[str] = ..., list: _Optional[_Iterable[_Union[LeaveAdjustmentRecord, _Mapping]]] = ...) -> None: ...

class LeavesAdjustmentsServiceRecordCreateRequest(_message.Message):
    __slots__ = ("user_comment", "leave_adjustment_id", "leave_type_id", "uom_id", "quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    LEAVE_ADJUSTMENT_ID_FIELD_NUMBER: _ClassVar[int]
    LEAVE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    leave_adjustment_id: int
    leave_type_id: int
    uom_id: int
    quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., leave_adjustment_id: _Optional[int] = ..., leave_type_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class LeavesAdjustmentsServiceRecordUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "leave_adjustment_id", "leave_type_id", "uom_id", "quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    LEAVE_ADJUSTMENT_ID_FIELD_NUMBER: _ClassVar[int]
    LEAVE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    leave_adjustment_id: int
    leave_type_id: int
    uom_id: int
    quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., leave_adjustment_id: _Optional[int] = ..., leave_type_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class LeaveAdjustmentRecord(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "leave_adjustment_id", "leave_type_id", "uom_id", "quantity")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    LEAVE_ADJUSTMENT_ID_FIELD_NUMBER: _ClassVar[int]
    LEAVE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    leave_adjustment_id: int
    leave_type_id: int
    uom_id: int
    quantity: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., leave_adjustment_id: _Optional[int] = ..., leave_type_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class LeavesAdjustmentsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[LeaveAdjustment]
    def __init__(self, list: _Optional[_Iterable[_Union[LeaveAdjustment, _Mapping]]] = ...) -> None: ...

class LeavesAdjustmentsRecordsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[LeaveAdjustmentRecord]
    def __init__(self, list: _Optional[_Iterable[_Union[LeaveAdjustmentRecord, _Mapping]]] = ...) -> None: ...

class LeavesAdjustmentsRecordsHistoryRequest(_message.Message):
    __slots__ = ("leave_adjustment_id", "leave_type_id")
    LEAVE_ADJUSTMENT_ID_FIELD_NUMBER: _ClassVar[int]
    LEAVE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    leave_adjustment_id: int
    leave_type_id: int
    def __init__(self, leave_adjustment_id: _Optional[int] = ..., leave_type_id: _Optional[int] = ...) -> None: ...

class LeavesAdjustmentsServicePaginationReq(_message.Message):
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
    sort_key: LEAVE_ADJUSTMENT_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[LEAVE_ADJUSTMENT_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class LeavesAdjustmentsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[LeaveAdjustment]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[LeaveAdjustment, _Mapping]]] = ...) -> None: ...

class LeavesAdjustmentsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "user_id")
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
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: LEAVE_ADJUSTMENT_SORT_KEY
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
    reference_id: str
    final_ref_number: str
    user_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[LEAVE_ADJUSTMENT_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

class LeavesAdjustmentsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "user_id")
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
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
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
    reference_id: str
    final_ref_number: str
    user_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...

class LeavesAdjustmentsServiceSearchAllReq(_message.Message):
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
    sort_key: LEAVE_ADJUSTMENT_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[LEAVE_ADJUSTMENT_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ...) -> None: ...

class LeaveAdjustmentRecordsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "leave_adjustment_id", "leave_type_id", "uom_id", "search_key")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_START_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_END_FIELD_NUMBER: _ClassVar[int]
    APPROVED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVER_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    LEAVE_ADJUSTMENT_ID_FIELD_NUMBER: _ClassVar[int]
    LEAVE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: LEAVE_ADJUSTMENT_RECORD_SORT_KEY
    entity_uuid: str
    status: LEAVE_ADJUSTMENT_RECORD_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    leave_adjustment_id: int
    leave_type_id: int
    uom_id: int
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[LEAVE_ADJUSTMENT_RECORD_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[LEAVE_ADJUSTMENT_RECORD_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., leave_adjustment_id: _Optional[int] = ..., leave_type_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., search_key: _Optional[str] = ...) -> None: ...

class LeavesAdjustmentsServicePaginatedRecordsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[LeaveAdjustmentRecord]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[LeaveAdjustmentRecord, _Mapping]]] = ...) -> None: ...
