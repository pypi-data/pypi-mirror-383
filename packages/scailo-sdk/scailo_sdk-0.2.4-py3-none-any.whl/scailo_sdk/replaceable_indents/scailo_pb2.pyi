from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from families import scailo_pb2 as _scailo_pb2_1
from forms_fields_data import scailo_pb2 as _scailo_pb2_1_1
from magic_links import scailo_pb2 as _scailo_pb2_1_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class REPLACEABLE_INDENT_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REPLACEABLE_INDENT_SORT_KEY_ID_UNSPECIFIED: _ClassVar[REPLACEABLE_INDENT_SORT_KEY]
    REPLACEABLE_INDENT_SORT_KEY_CREATED_AT: _ClassVar[REPLACEABLE_INDENT_SORT_KEY]
    REPLACEABLE_INDENT_SORT_KEY_MODIFIED_AT: _ClassVar[REPLACEABLE_INDENT_SORT_KEY]
    REPLACEABLE_INDENT_SORT_KEY_APPROVED_ON: _ClassVar[REPLACEABLE_INDENT_SORT_KEY]
    REPLACEABLE_INDENT_SORT_KEY_APPROVED_BY: _ClassVar[REPLACEABLE_INDENT_SORT_KEY]
    REPLACEABLE_INDENT_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[REPLACEABLE_INDENT_SORT_KEY]
    REPLACEABLE_INDENT_SORT_KEY_COMPLETED_ON: _ClassVar[REPLACEABLE_INDENT_SORT_KEY]
    REPLACEABLE_INDENT_SORT_KEY_REFERENCE_ID: _ClassVar[REPLACEABLE_INDENT_SORT_KEY]
    REPLACEABLE_INDENT_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[REPLACEABLE_INDENT_SORT_KEY]
    REPLACEABLE_INDENT_SORT_KEY_LOCATION_ID: _ClassVar[REPLACEABLE_INDENT_SORT_KEY]

class REPLACEABLE_INDENT_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REPLACEABLE_INDENT_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[REPLACEABLE_INDENT_ITEM_SORT_KEY]
    REPLACEABLE_INDENT_ITEM_SORT_KEY_CREATED_AT: _ClassVar[REPLACEABLE_INDENT_ITEM_SORT_KEY]
    REPLACEABLE_INDENT_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[REPLACEABLE_INDENT_ITEM_SORT_KEY]
    REPLACEABLE_INDENT_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[REPLACEABLE_INDENT_ITEM_SORT_KEY]
    REPLACEABLE_INDENT_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[REPLACEABLE_INDENT_ITEM_SORT_KEY]
    REPLACEABLE_INDENT_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[REPLACEABLE_INDENT_ITEM_SORT_KEY]
    REPLACEABLE_INDENT_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[REPLACEABLE_INDENT_ITEM_SORT_KEY]
    REPLACEABLE_INDENT_ITEM_SORT_KEY_INTERNAL_QUANTITY: _ClassVar[REPLACEABLE_INDENT_ITEM_SORT_KEY]

class REPLACEABLE_INDENT_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    REPLACEABLE_INDENT_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[REPLACEABLE_INDENT_ITEM_STATUS]
    REPLACEABLE_INDENT_ITEM_STATUS_APPROVED: _ClassVar[REPLACEABLE_INDENT_ITEM_STATUS]
    REPLACEABLE_INDENT_ITEM_STATUS_UNAPPROVED: _ClassVar[REPLACEABLE_INDENT_ITEM_STATUS]
REPLACEABLE_INDENT_SORT_KEY_ID_UNSPECIFIED: REPLACEABLE_INDENT_SORT_KEY
REPLACEABLE_INDENT_SORT_KEY_CREATED_AT: REPLACEABLE_INDENT_SORT_KEY
REPLACEABLE_INDENT_SORT_KEY_MODIFIED_AT: REPLACEABLE_INDENT_SORT_KEY
REPLACEABLE_INDENT_SORT_KEY_APPROVED_ON: REPLACEABLE_INDENT_SORT_KEY
REPLACEABLE_INDENT_SORT_KEY_APPROVED_BY: REPLACEABLE_INDENT_SORT_KEY
REPLACEABLE_INDENT_SORT_KEY_APPROVER_ROLE_ID: REPLACEABLE_INDENT_SORT_KEY
REPLACEABLE_INDENT_SORT_KEY_COMPLETED_ON: REPLACEABLE_INDENT_SORT_KEY
REPLACEABLE_INDENT_SORT_KEY_REFERENCE_ID: REPLACEABLE_INDENT_SORT_KEY
REPLACEABLE_INDENT_SORT_KEY_FINAL_REF_NUMBER: REPLACEABLE_INDENT_SORT_KEY
REPLACEABLE_INDENT_SORT_KEY_LOCATION_ID: REPLACEABLE_INDENT_SORT_KEY
REPLACEABLE_INDENT_ITEM_SORT_KEY_ID_UNSPECIFIED: REPLACEABLE_INDENT_ITEM_SORT_KEY
REPLACEABLE_INDENT_ITEM_SORT_KEY_CREATED_AT: REPLACEABLE_INDENT_ITEM_SORT_KEY
REPLACEABLE_INDENT_ITEM_SORT_KEY_MODIFIED_AT: REPLACEABLE_INDENT_ITEM_SORT_KEY
REPLACEABLE_INDENT_ITEM_SORT_KEY_APPROVED_ON: REPLACEABLE_INDENT_ITEM_SORT_KEY
REPLACEABLE_INDENT_ITEM_SORT_KEY_APPROVED_BY: REPLACEABLE_INDENT_ITEM_SORT_KEY
REPLACEABLE_INDENT_ITEM_SORT_KEY_APPROVER_ROLE_ID: REPLACEABLE_INDENT_ITEM_SORT_KEY
REPLACEABLE_INDENT_ITEM_SORT_KEY_FAMILY_ID: REPLACEABLE_INDENT_ITEM_SORT_KEY
REPLACEABLE_INDENT_ITEM_SORT_KEY_INTERNAL_QUANTITY: REPLACEABLE_INDENT_ITEM_SORT_KEY
REPLACEABLE_INDENT_ITEM_STATUS_ANY_UNSPECIFIED: REPLACEABLE_INDENT_ITEM_STATUS
REPLACEABLE_INDENT_ITEM_STATUS_APPROVED: REPLACEABLE_INDENT_ITEM_STATUS
REPLACEABLE_INDENT_ITEM_STATUS_UNAPPROVED: REPLACEABLE_INDENT_ITEM_STATUS

class ReplaceableIndentsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "location_id", "supervisor", "family_id", "item_hash", "description", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    location_id: int
    supervisor: str
    family_id: int
    item_hash: str
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., family_id: _Optional[int] = ..., item_hash: _Optional[str] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class ReplaceableIndentsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "supervisor", "description", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    supervisor: str
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., supervisor: _Optional[str] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class ReplaceableIndentsServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid", "populate_using_equation_dependencies")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    POPULATE_USING_EQUATION_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    populate_using_equation_dependencies: bool
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ..., populate_using_equation_dependencies: _Optional[bool] = ...) -> None: ...

class ReplaceableIndent(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "location_id", "supervisor", "family_id", "item_hash", "description", "list", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
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
    location_id: int
    supervisor: str
    family_id: int
    item_hash: str
    description: str
    list: _containers.RepeatedCompositeFieldContainer[ReplaceableIndentItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., family_id: _Optional[int] = ..., item_hash: _Optional[str] = ..., description: _Optional[str] = ..., list: _Optional[_Iterable[_Union[ReplaceableIndentItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class ReplaceableIndentsServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "replaceable_indent_id", "family_id", "internal_quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    REPLACEABLE_INDENT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    replaceable_indent_id: int
    family_id: int
    internal_quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., replaceable_indent_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ...) -> None: ...

class ReplaceableIndentsServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "internal_quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    internal_quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., internal_quantity: _Optional[int] = ...) -> None: ...

class ReplaceableIndentItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "replaceable_indent_id", "family_id", "internal_quantity")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    REPLACEABLE_INDENT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    replaceable_indent_id: int
    family_id: int
    internal_quantity: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., replaceable_indent_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ...) -> None: ...

class ReplaceableIndentsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ReplaceableIndent]
    def __init__(self, list: _Optional[_Iterable[_Union[ReplaceableIndent, _Mapping]]] = ...) -> None: ...

class ReplaceableIndentsItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ReplaceableIndentItem]
    def __init__(self, list: _Optional[_Iterable[_Union[ReplaceableIndentItem, _Mapping]]] = ...) -> None: ...

class ReplaceableIndentItemHistoryRequest(_message.Message):
    __slots__ = ("replaceable_indent_id", "family_id")
    REPLACEABLE_INDENT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    replaceable_indent_id: int
    family_id: int
    def __init__(self, replaceable_indent_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class ReplaceableIndentItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("replaceable_indent_id", "family_id")
    REPLACEABLE_INDENT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    replaceable_indent_id: int
    family_id: int
    def __init__(self, replaceable_indent_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class ReplaceableIndentsServicePaginationReq(_message.Message):
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
    sort_key: REPLACEABLE_INDENT_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[REPLACEABLE_INDENT_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class ReplaceableIndentsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[ReplaceableIndent]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[ReplaceableIndent, _Mapping]]] = ...) -> None: ...

class ReplaceableIndentsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "location_id", "supervisor", "family_id", "item_hash", "constituent_family_id", "form_data")
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
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
    CONSTITUENT_FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: REPLACEABLE_INDENT_SORT_KEY
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
    location_id: int
    supervisor: str
    family_id: int
    item_hash: str
    constituent_family_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[REPLACEABLE_INDENT_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., family_id: _Optional[int] = ..., item_hash: _Optional[str] = ..., constituent_family_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class ReplaceableIndentsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "location_id", "supervisor", "family_id", "item_hash", "constituent_family_id", "form_data")
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
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
    CONSTITUENT_FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
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
    location_id: int
    supervisor: str
    family_id: int
    item_hash: str
    constituent_family_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., family_id: _Optional[int] = ..., item_hash: _Optional[str] = ..., constituent_family_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class ReplaceableIndentsServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "location_id", "supervisor", "family_id", "item_hash")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: REPLACEABLE_INDENT_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    location_id: int
    supervisor: str
    family_id: int
    item_hash: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[REPLACEABLE_INDENT_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., family_id: _Optional[int] = ..., item_hash: _Optional[str] = ...) -> None: ...

class ReplaceableIndentItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "replaceable_indent_id", "family_id", "search_key")
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
    REPLACEABLE_INDENT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: REPLACEABLE_INDENT_ITEM_SORT_KEY
    entity_uuid: str
    status: REPLACEABLE_INDENT_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    replaceable_indent_id: int
    family_id: int
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[REPLACEABLE_INDENT_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[REPLACEABLE_INDENT_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., replaceable_indent_id: _Optional[int] = ..., family_id: _Optional[int] = ..., search_key: _Optional[str] = ...) -> None: ...

class ReplaceableIndentsServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[ReplaceableIndentItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[ReplaceableIndentItem, _Mapping]]] = ...) -> None: ...

class ReplaceableIndentIssuedStatistics(_message.Message):
    __slots__ = ("family_id", "indented_quantity", "unapproved_issued_quantity", "approved_issued_quantity")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INDENTED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    UNAPPROVED_ISSUED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ISSUED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    indented_quantity: int
    unapproved_issued_quantity: int
    approved_issued_quantity: int
    def __init__(self, family_id: _Optional[int] = ..., indented_quantity: _Optional[int] = ..., unapproved_issued_quantity: _Optional[int] = ..., approved_issued_quantity: _Optional[int] = ...) -> None: ...

class ReplaceableIndentIssuedStatisticsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ReplaceableIndentIssuedStatistics]
    def __init__(self, list: _Optional[_Iterable[_Union[ReplaceableIndentIssuedStatistics, _Mapping]]] = ...) -> None: ...
