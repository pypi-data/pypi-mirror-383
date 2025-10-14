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

class GOAL_ITEM_INPUT_VALUE_TYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GOAL_ITEM_INPUT_VALUE_TYPE_NUMBER_ABSOLUTE_UNSPECIFIED: _ClassVar[GOAL_ITEM_INPUT_VALUE_TYPE]
    GOAL_ITEM_INPUT_VALUE_TYPE_NUMBER_PERCENTAGE: _ClassVar[GOAL_ITEM_INPUT_VALUE_TYPE]
    GOAL_ITEM_INPUT_VALUE_TYPE_TEXT_INPUT: _ClassVar[GOAL_ITEM_INPUT_VALUE_TYPE]
    GOAL_ITEM_INPUT_VALUE_TYPE_TEXT_DROPDOWN: _ClassVar[GOAL_ITEM_INPUT_VALUE_TYPE]

class GOAL_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GOAL_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[GOAL_ITEM_SORT_KEY]
    GOAL_ITEM_SORT_KEY_CREATED_AT: _ClassVar[GOAL_ITEM_SORT_KEY]
    GOAL_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[GOAL_ITEM_SORT_KEY]
    GOAL_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[GOAL_ITEM_SORT_KEY]
    GOAL_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[GOAL_ITEM_SORT_KEY]
    GOAL_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[GOAL_ITEM_SORT_KEY]
    GOAL_ITEM_SORT_KEY_LABEL_ID: _ClassVar[GOAL_ITEM_SORT_KEY]

class GOAL_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GOAL_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[GOAL_ITEM_STATUS]
    GOAL_ITEM_STATUS_APPROVED: _ClassVar[GOAL_ITEM_STATUS]
    GOAL_ITEM_STATUS_UNAPPROVED: _ClassVar[GOAL_ITEM_STATUS]

class GOAL_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GOAL_SORT_KEY_ID_UNSPECIFIED: _ClassVar[GOAL_SORT_KEY]
    GOAL_SORT_KEY_CREATED_AT: _ClassVar[GOAL_SORT_KEY]
    GOAL_SORT_KEY_MODIFIED_AT: _ClassVar[GOAL_SORT_KEY]
    GOAL_SORT_KEY_APPROVED_ON: _ClassVar[GOAL_SORT_KEY]
    GOAL_SORT_KEY_APPROVED_BY: _ClassVar[GOAL_SORT_KEY]
    GOAL_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[GOAL_SORT_KEY]
    GOAL_SORT_KEY_COMPLETED_ON: _ClassVar[GOAL_SORT_KEY]
    GOAL_SORT_KEY_REFERENCE_ID: _ClassVar[GOAL_SORT_KEY]
    GOAL_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[GOAL_SORT_KEY]
GOAL_ITEM_INPUT_VALUE_TYPE_NUMBER_ABSOLUTE_UNSPECIFIED: GOAL_ITEM_INPUT_VALUE_TYPE
GOAL_ITEM_INPUT_VALUE_TYPE_NUMBER_PERCENTAGE: GOAL_ITEM_INPUT_VALUE_TYPE
GOAL_ITEM_INPUT_VALUE_TYPE_TEXT_INPUT: GOAL_ITEM_INPUT_VALUE_TYPE
GOAL_ITEM_INPUT_VALUE_TYPE_TEXT_DROPDOWN: GOAL_ITEM_INPUT_VALUE_TYPE
GOAL_ITEM_SORT_KEY_ID_UNSPECIFIED: GOAL_ITEM_SORT_KEY
GOAL_ITEM_SORT_KEY_CREATED_AT: GOAL_ITEM_SORT_KEY
GOAL_ITEM_SORT_KEY_MODIFIED_AT: GOAL_ITEM_SORT_KEY
GOAL_ITEM_SORT_KEY_APPROVED_ON: GOAL_ITEM_SORT_KEY
GOAL_ITEM_SORT_KEY_APPROVED_BY: GOAL_ITEM_SORT_KEY
GOAL_ITEM_SORT_KEY_APPROVER_ROLE_ID: GOAL_ITEM_SORT_KEY
GOAL_ITEM_SORT_KEY_LABEL_ID: GOAL_ITEM_SORT_KEY
GOAL_ITEM_STATUS_ANY_UNSPECIFIED: GOAL_ITEM_STATUS
GOAL_ITEM_STATUS_APPROVED: GOAL_ITEM_STATUS
GOAL_ITEM_STATUS_UNAPPROVED: GOAL_ITEM_STATUS
GOAL_SORT_KEY_ID_UNSPECIFIED: GOAL_SORT_KEY
GOAL_SORT_KEY_CREATED_AT: GOAL_SORT_KEY
GOAL_SORT_KEY_MODIFIED_AT: GOAL_SORT_KEY
GOAL_SORT_KEY_APPROVED_ON: GOAL_SORT_KEY
GOAL_SORT_KEY_APPROVED_BY: GOAL_SORT_KEY
GOAL_SORT_KEY_APPROVER_ROLE_ID: GOAL_SORT_KEY
GOAL_SORT_KEY_COMPLETED_ON: GOAL_SORT_KEY
GOAL_SORT_KEY_REFERENCE_ID: GOAL_SORT_KEY
GOAL_SORT_KEY_FINAL_REF_NUMBER: GOAL_SORT_KEY

class GoalsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "user_id", "start_date", "end_date", "description", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    user_id: int
    start_date: str
    end_date: str
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., user_id: _Optional[int] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class GoalsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "start_date", "end_date", "description", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    start_date: str
    end_date: str
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class Goal(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "user_id", "start_date", "end_date", "description", "list", "form_data")
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
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
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
    start_date: str
    end_date: str
    description: str
    list: _containers.RepeatedCompositeFieldContainer[GoalItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., user_id: _Optional[int] = ..., start_date: _Optional[str] = ..., end_date: _Optional[str] = ..., description: _Optional[str] = ..., list: _Optional[_Iterable[_Union[GoalItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class GoalsServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "goal_id", "name", "label_id", "specifications", "input_value_type", "number_min_value", "number_max_value", "number_acceptable_value", "text_values", "text_acceptable_value")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    GOAL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    INPUT_VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_MIN_VALUE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_MAX_VALUE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_ACCEPTABLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    TEXT_VALUES_FIELD_NUMBER: _ClassVar[int]
    TEXT_ACCEPTABLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    goal_id: int
    name: str
    label_id: int
    specifications: str
    input_value_type: GOAL_ITEM_INPUT_VALUE_TYPE
    number_min_value: int
    number_max_value: int
    number_acceptable_value: int
    text_values: _containers.RepeatedScalarFieldContainer[str]
    text_acceptable_value: str
    def __init__(self, user_comment: _Optional[str] = ..., goal_id: _Optional[int] = ..., name: _Optional[str] = ..., label_id: _Optional[int] = ..., specifications: _Optional[str] = ..., input_value_type: _Optional[_Union[GOAL_ITEM_INPUT_VALUE_TYPE, str]] = ..., number_min_value: _Optional[int] = ..., number_max_value: _Optional[int] = ..., number_acceptable_value: _Optional[int] = ..., text_values: _Optional[_Iterable[str]] = ..., text_acceptable_value: _Optional[str] = ...) -> None: ...

class GoalsServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "name", "label_id", "specifications", "input_value_type", "number_min_value", "number_max_value", "number_acceptable_value", "text_values", "text_acceptable_value")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    INPUT_VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_MIN_VALUE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_MAX_VALUE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_ACCEPTABLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    TEXT_VALUES_FIELD_NUMBER: _ClassVar[int]
    TEXT_ACCEPTABLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    name: str
    label_id: int
    specifications: str
    input_value_type: GOAL_ITEM_INPUT_VALUE_TYPE
    number_min_value: int
    number_max_value: int
    number_acceptable_value: int
    text_values: _containers.RepeatedScalarFieldContainer[str]
    text_acceptable_value: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., name: _Optional[str] = ..., label_id: _Optional[int] = ..., specifications: _Optional[str] = ..., input_value_type: _Optional[_Union[GOAL_ITEM_INPUT_VALUE_TYPE, str]] = ..., number_min_value: _Optional[int] = ..., number_max_value: _Optional[int] = ..., number_acceptable_value: _Optional[int] = ..., text_values: _Optional[_Iterable[str]] = ..., text_acceptable_value: _Optional[str] = ...) -> None: ...

class GoalItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "goal_id", "name", "label_id", "specifications", "input_value_type", "number_min_value", "number_max_value", "number_acceptable_value", "text_values", "text_acceptable_value")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    GOAL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    INPUT_VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_MIN_VALUE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_MAX_VALUE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_ACCEPTABLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    TEXT_VALUES_FIELD_NUMBER: _ClassVar[int]
    TEXT_ACCEPTABLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    goal_id: int
    name: str
    label_id: int
    specifications: str
    input_value_type: GOAL_ITEM_INPUT_VALUE_TYPE
    number_min_value: int
    number_max_value: int
    number_acceptable_value: int
    text_values: _containers.RepeatedScalarFieldContainer[str]
    text_acceptable_value: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., goal_id: _Optional[int] = ..., name: _Optional[str] = ..., label_id: _Optional[int] = ..., specifications: _Optional[str] = ..., input_value_type: _Optional[_Union[GOAL_ITEM_INPUT_VALUE_TYPE, str]] = ..., number_min_value: _Optional[int] = ..., number_max_value: _Optional[int] = ..., number_acceptable_value: _Optional[int] = ..., text_values: _Optional[_Iterable[str]] = ..., text_acceptable_value: _Optional[str] = ...) -> None: ...

class GoalsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[Goal]
    def __init__(self, list: _Optional[_Iterable[_Union[Goal, _Mapping]]] = ...) -> None: ...

class GoalsItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[GoalItem]
    def __init__(self, list: _Optional[_Iterable[_Union[GoalItem, _Mapping]]] = ...) -> None: ...

class GoalItemHistoryRequest(_message.Message):
    __slots__ = ("goal_id", "name")
    GOAL_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    goal_id: int
    name: str
    def __init__(self, goal_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class GoalItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "goal_id", "label_id", "search_key")
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
    GOAL_ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: GOAL_ITEM_SORT_KEY
    entity_uuid: str
    status: GOAL_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    goal_id: int
    label_id: int
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[GOAL_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[GOAL_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., goal_id: _Optional[int] = ..., label_id: _Optional[int] = ..., search_key: _Optional[str] = ...) -> None: ...

class GoalsServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[GoalItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[GoalItem, _Mapping]]] = ...) -> None: ...

class GoalsServicePaginationReq(_message.Message):
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
    sort_key: GOAL_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[GOAL_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class GoalsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[Goal]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[Goal, _Mapping]]] = ...) -> None: ...

class GoalsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "user_id", "start_date_start", "start_date_end", "start_date_exact", "end_date_start", "end_date_end", "end_date_exact", "form_data")
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
    START_DATE_START_FIELD_NUMBER: _ClassVar[int]
    START_DATE_END_FIELD_NUMBER: _ClassVar[int]
    START_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    END_DATE_START_FIELD_NUMBER: _ClassVar[int]
    END_DATE_END_FIELD_NUMBER: _ClassVar[int]
    END_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: GOAL_SORT_KEY
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
    start_date_start: str
    start_date_end: str
    start_date_exact: str
    end_date_start: str
    end_date_end: str
    end_date_exact: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[GOAL_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., user_id: _Optional[int] = ..., start_date_start: _Optional[str] = ..., start_date_end: _Optional[str] = ..., start_date_exact: _Optional[str] = ..., end_date_start: _Optional[str] = ..., end_date_end: _Optional[str] = ..., end_date_exact: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class GoalsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "user_id", "start_date_start", "start_date_end", "start_date_exact", "end_date_start", "end_date_end", "end_date_exact", "form_data")
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
    START_DATE_START_FIELD_NUMBER: _ClassVar[int]
    START_DATE_END_FIELD_NUMBER: _ClassVar[int]
    START_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    END_DATE_START_FIELD_NUMBER: _ClassVar[int]
    END_DATE_END_FIELD_NUMBER: _ClassVar[int]
    END_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
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
    start_date_start: str
    start_date_end: str
    start_date_exact: str
    end_date_start: str
    end_date_end: str
    end_date_exact: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., user_id: _Optional[int] = ..., start_date_start: _Optional[str] = ..., start_date_end: _Optional[str] = ..., start_date_exact: _Optional[str] = ..., end_date_start: _Optional[str] = ..., end_date_end: _Optional[str] = ..., end_date_exact: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class GoalsServiceSearchAllReq(_message.Message):
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
    sort_key: GOAL_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    user_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[GOAL_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., user_id: _Optional[int] = ...) -> None: ...
