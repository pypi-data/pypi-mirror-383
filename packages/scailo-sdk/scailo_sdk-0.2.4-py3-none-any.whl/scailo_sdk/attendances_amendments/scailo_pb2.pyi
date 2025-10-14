from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from forms_fields_data import scailo_pb2 as _scailo_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ATTENDANCE_AMENDMENT_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ATTENDANCE_AMENDMENT_SORT_KEY_ID_UNSPECIFIED: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
    ATTENDANCE_AMENDMENT_SORT_KEY_CREATED_AT: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
    ATTENDANCE_AMENDMENT_SORT_KEY_MODIFIED_AT: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
    ATTENDANCE_AMENDMENT_SORT_KEY_APPROVED_ON: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
    ATTENDANCE_AMENDMENT_SORT_KEY_APPROVED_BY: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
    ATTENDANCE_AMENDMENT_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
    ATTENDANCE_AMENDMENT_SORT_KEY_COMPLETED_ON: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
    ATTENDANCE_AMENDMENT_SORT_KEY_REFERENCE_ID: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
    ATTENDANCE_AMENDMENT_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
    ATTENDANCE_AMENDMENT_SORT_KEY_USER_ID: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
    ATTENDANCE_AMENDMENT_SORT_KEY_ATTENDANCE_ENTRY_TIMESTAMP: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
    ATTENDANCE_AMENDMENT_SORT_KEY_ATTENDANCE_EXIT_TIMESTAMP: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
    ATTENDANCE_AMENDMENT_SORT_KEY_AMENDMENT_ENTRY_TIMESTAMP: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
    ATTENDANCE_AMENDMENT_SORT_KEY_AMENDMENT_EXIT_TIMESTAMP: _ClassVar[ATTENDANCE_AMENDMENT_SORT_KEY]
ATTENDANCE_AMENDMENT_SORT_KEY_ID_UNSPECIFIED: ATTENDANCE_AMENDMENT_SORT_KEY
ATTENDANCE_AMENDMENT_SORT_KEY_CREATED_AT: ATTENDANCE_AMENDMENT_SORT_KEY
ATTENDANCE_AMENDMENT_SORT_KEY_MODIFIED_AT: ATTENDANCE_AMENDMENT_SORT_KEY
ATTENDANCE_AMENDMENT_SORT_KEY_APPROVED_ON: ATTENDANCE_AMENDMENT_SORT_KEY
ATTENDANCE_AMENDMENT_SORT_KEY_APPROVED_BY: ATTENDANCE_AMENDMENT_SORT_KEY
ATTENDANCE_AMENDMENT_SORT_KEY_APPROVER_ROLE_ID: ATTENDANCE_AMENDMENT_SORT_KEY
ATTENDANCE_AMENDMENT_SORT_KEY_COMPLETED_ON: ATTENDANCE_AMENDMENT_SORT_KEY
ATTENDANCE_AMENDMENT_SORT_KEY_REFERENCE_ID: ATTENDANCE_AMENDMENT_SORT_KEY
ATTENDANCE_AMENDMENT_SORT_KEY_FINAL_REF_NUMBER: ATTENDANCE_AMENDMENT_SORT_KEY
ATTENDANCE_AMENDMENT_SORT_KEY_USER_ID: ATTENDANCE_AMENDMENT_SORT_KEY
ATTENDANCE_AMENDMENT_SORT_KEY_ATTENDANCE_ENTRY_TIMESTAMP: ATTENDANCE_AMENDMENT_SORT_KEY
ATTENDANCE_AMENDMENT_SORT_KEY_ATTENDANCE_EXIT_TIMESTAMP: ATTENDANCE_AMENDMENT_SORT_KEY
ATTENDANCE_AMENDMENT_SORT_KEY_AMENDMENT_ENTRY_TIMESTAMP: ATTENDANCE_AMENDMENT_SORT_KEY
ATTENDANCE_AMENDMENT_SORT_KEY_AMENDMENT_EXIT_TIMESTAMP: ATTENDANCE_AMENDMENT_SORT_KEY

class AttendancesAmendmentsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "user_id", "attendance_id", "amendment_entry_timestamp", "amendment_exit_timestamp", "description", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_ID_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_ENTRY_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_EXIT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    user_id: int
    attendance_id: int
    amendment_entry_timestamp: int
    amendment_exit_timestamp: int
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., user_id: _Optional[int] = ..., attendance_id: _Optional[int] = ..., amendment_entry_timestamp: _Optional[int] = ..., amendment_exit_timestamp: _Optional[int] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class AttendancesAmendmentsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "amendment_entry_timestamp", "amendment_exit_timestamp", "description", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_ENTRY_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_EXIT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    amendment_entry_timestamp: int
    amendment_exit_timestamp: int
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., amendment_entry_timestamp: _Optional[int] = ..., amendment_exit_timestamp: _Optional[int] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class AttendanceAmendment(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "user_id", "attendance_id", "attendance_entry_timestamp", "attendance_exit_timestamp", "amendment_entry_timestamp", "amendment_exit_timestamp", "description", "form_data")
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
    ATTENDANCE_ID_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_ENTRY_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_EXIT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_ENTRY_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_EXIT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
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
    attendance_id: int
    attendance_entry_timestamp: int
    attendance_exit_timestamp: int
    amendment_entry_timestamp: int
    amendment_exit_timestamp: int
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., user_id: _Optional[int] = ..., attendance_id: _Optional[int] = ..., attendance_entry_timestamp: _Optional[int] = ..., attendance_exit_timestamp: _Optional[int] = ..., amendment_entry_timestamp: _Optional[int] = ..., amendment_exit_timestamp: _Optional[int] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class AttendancesAmendmentsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[AttendanceAmendment]
    def __init__(self, list: _Optional[_Iterable[_Union[AttendanceAmendment, _Mapping]]] = ...) -> None: ...

class AttendancesAmendmentsServicePaginationReq(_message.Message):
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
    sort_key: ATTENDANCE_AMENDMENT_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ATTENDANCE_AMENDMENT_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class AttendancesAmendmentsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[AttendanceAmendment]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[AttendanceAmendment, _Mapping]]] = ...) -> None: ...

class AttendancesAmendmentsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "user_id", "attendance_id", "attendance_entry_timestamp_start", "attendance_entry_timestamp_end", "attendance_exit_timestamp_start", "attendance_exit_timestamp_end", "amendment_entry_timestamp_start", "amendment_entry_timestamp_end", "amendment_exit_timestamp_start", "amendment_exit_timestamp_end", "form_data")
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
    ATTENDANCE_ID_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_ENTRY_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_ENTRY_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_EXIT_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_EXIT_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_ENTRY_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_ENTRY_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_EXIT_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_EXIT_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: ATTENDANCE_AMENDMENT_SORT_KEY
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
    attendance_id: int
    attendance_entry_timestamp_start: int
    attendance_entry_timestamp_end: int
    attendance_exit_timestamp_start: int
    attendance_exit_timestamp_end: int
    amendment_entry_timestamp_start: int
    amendment_entry_timestamp_end: int
    amendment_exit_timestamp_start: int
    amendment_exit_timestamp_end: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ATTENDANCE_AMENDMENT_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., user_id: _Optional[int] = ..., attendance_id: _Optional[int] = ..., attendance_entry_timestamp_start: _Optional[int] = ..., attendance_entry_timestamp_end: _Optional[int] = ..., attendance_exit_timestamp_start: _Optional[int] = ..., attendance_exit_timestamp_end: _Optional[int] = ..., amendment_entry_timestamp_start: _Optional[int] = ..., amendment_entry_timestamp_end: _Optional[int] = ..., amendment_exit_timestamp_start: _Optional[int] = ..., amendment_exit_timestamp_end: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class AttendancesAmendmentsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "user_id", "attendance_id", "attendance_entry_timestamp_start", "attendance_entry_timestamp_end", "attendance_exit_timestamp_start", "attendance_exit_timestamp_end", "amendment_entry_timestamp_start", "amendment_entry_timestamp_end", "amendment_exit_timestamp_start", "amendment_exit_timestamp_end", "form_data")
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
    ATTENDANCE_ID_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_ENTRY_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_ENTRY_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_EXIT_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_EXIT_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_ENTRY_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_ENTRY_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_EXIT_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_EXIT_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
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
    attendance_id: int
    attendance_entry_timestamp_start: int
    attendance_entry_timestamp_end: int
    attendance_exit_timestamp_start: int
    attendance_exit_timestamp_end: int
    amendment_entry_timestamp_start: int
    amendment_entry_timestamp_end: int
    amendment_exit_timestamp_start: int
    amendment_exit_timestamp_end: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., user_id: _Optional[int] = ..., attendance_id: _Optional[int] = ..., attendance_entry_timestamp_start: _Optional[int] = ..., attendance_entry_timestamp_end: _Optional[int] = ..., attendance_exit_timestamp_start: _Optional[int] = ..., attendance_exit_timestamp_end: _Optional[int] = ..., amendment_entry_timestamp_start: _Optional[int] = ..., amendment_entry_timestamp_end: _Optional[int] = ..., amendment_exit_timestamp_start: _Optional[int] = ..., amendment_exit_timestamp_end: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class AttendancesAmendmentsServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "user_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: ATTENDANCE_AMENDMENT_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    user_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ATTENDANCE_AMENDMENT_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...
