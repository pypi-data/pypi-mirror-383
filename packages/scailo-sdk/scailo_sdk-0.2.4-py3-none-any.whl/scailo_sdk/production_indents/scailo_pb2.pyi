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

class PRODUCTION_INDENT_PRODUCTION_REF_FOR(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRODUCTION_INDENT_PRODUCTION_REF_FOR_ANY_UNSPECIFIED: _ClassVar[PRODUCTION_INDENT_PRODUCTION_REF_FOR]
    PRODUCTION_INDENT_PRODUCTION_REF_FOR_NONE: _ClassVar[PRODUCTION_INDENT_PRODUCTION_REF_FOR]
    PRODUCTION_INDENT_PRODUCTION_REF_FOR_PRODUCTION_PLAN: _ClassVar[PRODUCTION_INDENT_PRODUCTION_REF_FOR]

class PRODUCTION_INDENT_INDENT_REF_FOR(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRODUCTION_INDENT_INDENT_REF_FOR_ANY_UNSPECIFIED: _ClassVar[PRODUCTION_INDENT_INDENT_REF_FOR]
    PRODUCTION_INDENT_INDENT_REF_FOR_NONE: _ClassVar[PRODUCTION_INDENT_INDENT_REF_FOR]
    PRODUCTION_INDENT_INDENT_REF_FOR_FAMILY: _ClassVar[PRODUCTION_INDENT_INDENT_REF_FOR]
    PRODUCTION_INDENT_INDENT_REF_FOR_WORK_ORDER: _ClassVar[PRODUCTION_INDENT_INDENT_REF_FOR]

class PRODUCTION_INDENT_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRODUCTION_INDENT_SORT_KEY_ID_UNSPECIFIED: _ClassVar[PRODUCTION_INDENT_SORT_KEY]
    PRODUCTION_INDENT_SORT_KEY_CREATED_AT: _ClassVar[PRODUCTION_INDENT_SORT_KEY]
    PRODUCTION_INDENT_SORT_KEY_MODIFIED_AT: _ClassVar[PRODUCTION_INDENT_SORT_KEY]
    PRODUCTION_INDENT_SORT_KEY_APPROVED_ON: _ClassVar[PRODUCTION_INDENT_SORT_KEY]
    PRODUCTION_INDENT_SORT_KEY_APPROVED_BY: _ClassVar[PRODUCTION_INDENT_SORT_KEY]
    PRODUCTION_INDENT_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[PRODUCTION_INDENT_SORT_KEY]
    PRODUCTION_INDENT_SORT_KEY_COMPLETED_ON: _ClassVar[PRODUCTION_INDENT_SORT_KEY]
    PRODUCTION_INDENT_SORT_KEY_REFERENCE_ID: _ClassVar[PRODUCTION_INDENT_SORT_KEY]
    PRODUCTION_INDENT_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[PRODUCTION_INDENT_SORT_KEY]
    PRODUCTION_INDENT_SORT_KEY_LOCATION_ID: _ClassVar[PRODUCTION_INDENT_SORT_KEY]

class PRODUCTION_INDENT_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRODUCTION_INDENT_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[PRODUCTION_INDENT_ITEM_SORT_KEY]
    PRODUCTION_INDENT_ITEM_SORT_KEY_CREATED_AT: _ClassVar[PRODUCTION_INDENT_ITEM_SORT_KEY]
    PRODUCTION_INDENT_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[PRODUCTION_INDENT_ITEM_SORT_KEY]
    PRODUCTION_INDENT_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[PRODUCTION_INDENT_ITEM_SORT_KEY]
    PRODUCTION_INDENT_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[PRODUCTION_INDENT_ITEM_SORT_KEY]
    PRODUCTION_INDENT_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[PRODUCTION_INDENT_ITEM_SORT_KEY]
    PRODUCTION_INDENT_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[PRODUCTION_INDENT_ITEM_SORT_KEY]
    PRODUCTION_INDENT_ITEM_SORT_KEY_INTERNAL_QUANTITY: _ClassVar[PRODUCTION_INDENT_ITEM_SORT_KEY]

class PRODUCTION_INDENT_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRODUCTION_INDENT_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[PRODUCTION_INDENT_ITEM_STATUS]
    PRODUCTION_INDENT_ITEM_STATUS_APPROVED: _ClassVar[PRODUCTION_INDENT_ITEM_STATUS]
    PRODUCTION_INDENT_ITEM_STATUS_UNAPPROVED: _ClassVar[PRODUCTION_INDENT_ITEM_STATUS]
PRODUCTION_INDENT_PRODUCTION_REF_FOR_ANY_UNSPECIFIED: PRODUCTION_INDENT_PRODUCTION_REF_FOR
PRODUCTION_INDENT_PRODUCTION_REF_FOR_NONE: PRODUCTION_INDENT_PRODUCTION_REF_FOR
PRODUCTION_INDENT_PRODUCTION_REF_FOR_PRODUCTION_PLAN: PRODUCTION_INDENT_PRODUCTION_REF_FOR
PRODUCTION_INDENT_INDENT_REF_FOR_ANY_UNSPECIFIED: PRODUCTION_INDENT_INDENT_REF_FOR
PRODUCTION_INDENT_INDENT_REF_FOR_NONE: PRODUCTION_INDENT_INDENT_REF_FOR
PRODUCTION_INDENT_INDENT_REF_FOR_FAMILY: PRODUCTION_INDENT_INDENT_REF_FOR
PRODUCTION_INDENT_INDENT_REF_FOR_WORK_ORDER: PRODUCTION_INDENT_INDENT_REF_FOR
PRODUCTION_INDENT_SORT_KEY_ID_UNSPECIFIED: PRODUCTION_INDENT_SORT_KEY
PRODUCTION_INDENT_SORT_KEY_CREATED_AT: PRODUCTION_INDENT_SORT_KEY
PRODUCTION_INDENT_SORT_KEY_MODIFIED_AT: PRODUCTION_INDENT_SORT_KEY
PRODUCTION_INDENT_SORT_KEY_APPROVED_ON: PRODUCTION_INDENT_SORT_KEY
PRODUCTION_INDENT_SORT_KEY_APPROVED_BY: PRODUCTION_INDENT_SORT_KEY
PRODUCTION_INDENT_SORT_KEY_APPROVER_ROLE_ID: PRODUCTION_INDENT_SORT_KEY
PRODUCTION_INDENT_SORT_KEY_COMPLETED_ON: PRODUCTION_INDENT_SORT_KEY
PRODUCTION_INDENT_SORT_KEY_REFERENCE_ID: PRODUCTION_INDENT_SORT_KEY
PRODUCTION_INDENT_SORT_KEY_FINAL_REF_NUMBER: PRODUCTION_INDENT_SORT_KEY
PRODUCTION_INDENT_SORT_KEY_LOCATION_ID: PRODUCTION_INDENT_SORT_KEY
PRODUCTION_INDENT_ITEM_SORT_KEY_ID_UNSPECIFIED: PRODUCTION_INDENT_ITEM_SORT_KEY
PRODUCTION_INDENT_ITEM_SORT_KEY_CREATED_AT: PRODUCTION_INDENT_ITEM_SORT_KEY
PRODUCTION_INDENT_ITEM_SORT_KEY_MODIFIED_AT: PRODUCTION_INDENT_ITEM_SORT_KEY
PRODUCTION_INDENT_ITEM_SORT_KEY_APPROVED_ON: PRODUCTION_INDENT_ITEM_SORT_KEY
PRODUCTION_INDENT_ITEM_SORT_KEY_APPROVED_BY: PRODUCTION_INDENT_ITEM_SORT_KEY
PRODUCTION_INDENT_ITEM_SORT_KEY_APPROVER_ROLE_ID: PRODUCTION_INDENT_ITEM_SORT_KEY
PRODUCTION_INDENT_ITEM_SORT_KEY_FAMILY_ID: PRODUCTION_INDENT_ITEM_SORT_KEY
PRODUCTION_INDENT_ITEM_SORT_KEY_INTERNAL_QUANTITY: PRODUCTION_INDENT_ITEM_SORT_KEY
PRODUCTION_INDENT_ITEM_STATUS_ANY_UNSPECIFIED: PRODUCTION_INDENT_ITEM_STATUS
PRODUCTION_INDENT_ITEM_STATUS_APPROVED: PRODUCTION_INDENT_ITEM_STATUS
PRODUCTION_INDENT_ITEM_STATUS_UNAPPROVED: PRODUCTION_INDENT_ITEM_STATUS

class ProductionIndentsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "location_id", "supervisor", "production_ref_for", "production_ref_id", "indent_ref_for", "indent_ref_id", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_REF_FOR_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_REF_ID_FIELD_NUMBER: _ClassVar[int]
    INDENT_REF_FOR_FIELD_NUMBER: _ClassVar[int]
    INDENT_REF_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    location_id: int
    supervisor: str
    production_ref_for: PRODUCTION_INDENT_PRODUCTION_REF_FOR
    production_ref_id: int
    indent_ref_for: PRODUCTION_INDENT_INDENT_REF_FOR
    indent_ref_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., production_ref_for: _Optional[_Union[PRODUCTION_INDENT_PRODUCTION_REF_FOR, str]] = ..., production_ref_id: _Optional[int] = ..., indent_ref_for: _Optional[_Union[PRODUCTION_INDENT_INDENT_REF_FOR, str]] = ..., indent_ref_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class ProductionIndentsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "supervisor", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    supervisor: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., supervisor: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class ProductionIndentsServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid", "populate_using_equation_dependencies")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    POPULATE_USING_EQUATION_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    populate_using_equation_dependencies: bool
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ..., populate_using_equation_dependencies: _Optional[bool] = ...) -> None: ...

class ProductionIndent(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "location_id", "supervisor", "production_ref_for", "production_ref_id", "indent_ref_for", "indent_ref_id", "list", "form_data")
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
    PRODUCTION_REF_FOR_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_REF_ID_FIELD_NUMBER: _ClassVar[int]
    INDENT_REF_FOR_FIELD_NUMBER: _ClassVar[int]
    INDENT_REF_ID_FIELD_NUMBER: _ClassVar[int]
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
    production_ref_for: PRODUCTION_INDENT_PRODUCTION_REF_FOR
    production_ref_id: int
    indent_ref_for: PRODUCTION_INDENT_INDENT_REF_FOR
    indent_ref_id: int
    list: _containers.RepeatedCompositeFieldContainer[ProductionIndentItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., production_ref_for: _Optional[_Union[PRODUCTION_INDENT_PRODUCTION_REF_FOR, str]] = ..., production_ref_id: _Optional[int] = ..., indent_ref_for: _Optional[_Union[PRODUCTION_INDENT_INDENT_REF_FOR, str]] = ..., indent_ref_id: _Optional[int] = ..., list: _Optional[_Iterable[_Union[ProductionIndentItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class ProductionIndentsServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "production_indent_id", "family_id", "internal_quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_INDENT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    production_indent_id: int
    family_id: int
    internal_quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., production_indent_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ...) -> None: ...

class ProductionIndentsServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "internal_quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    internal_quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., internal_quantity: _Optional[int] = ...) -> None: ...

class ProductionIndentItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "production_indent_id", "family_id", "internal_quantity")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_INDENT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    production_indent_id: int
    family_id: int
    internal_quantity: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., production_indent_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ...) -> None: ...

class ProductionIndentsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ProductionIndent]
    def __init__(self, list: _Optional[_Iterable[_Union[ProductionIndent, _Mapping]]] = ...) -> None: ...

class ProductionIndentsItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ProductionIndentItem]
    def __init__(self, list: _Optional[_Iterable[_Union[ProductionIndentItem, _Mapping]]] = ...) -> None: ...

class ProductionIndentItemHistoryRequest(_message.Message):
    __slots__ = ("production_indent_id", "family_id")
    PRODUCTION_INDENT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    production_indent_id: int
    family_id: int
    def __init__(self, production_indent_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class ProductionIndentItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("production_indent_id", "family_id")
    PRODUCTION_INDENT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    production_indent_id: int
    family_id: int
    def __init__(self, production_indent_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class ProductionIndentsServicePaginationReq(_message.Message):
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
    sort_key: PRODUCTION_INDENT_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[PRODUCTION_INDENT_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class ProductionIndentsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[ProductionIndent]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[ProductionIndent, _Mapping]]] = ...) -> None: ...

class ProductionIndentsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "location_id", "supervisor", "production_ref_for", "production_ref_id", "indent_ref_for", "indent_ref_id", "family_id", "form_data")
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
    PRODUCTION_REF_FOR_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_REF_ID_FIELD_NUMBER: _ClassVar[int]
    INDENT_REF_FOR_FIELD_NUMBER: _ClassVar[int]
    INDENT_REF_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: PRODUCTION_INDENT_SORT_KEY
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
    production_ref_for: PRODUCTION_INDENT_PRODUCTION_REF_FOR
    production_ref_id: int
    indent_ref_for: PRODUCTION_INDENT_INDENT_REF_FOR
    indent_ref_id: int
    family_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[PRODUCTION_INDENT_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., production_ref_for: _Optional[_Union[PRODUCTION_INDENT_PRODUCTION_REF_FOR, str]] = ..., production_ref_id: _Optional[int] = ..., indent_ref_for: _Optional[_Union[PRODUCTION_INDENT_INDENT_REF_FOR, str]] = ..., indent_ref_id: _Optional[int] = ..., family_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class ProductionIndentsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "location_id", "supervisor", "production_ref_for", "production_ref_id", "indent_ref_for", "indent_ref_id", "family_id", "form_data")
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
    PRODUCTION_REF_FOR_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_REF_ID_FIELD_NUMBER: _ClassVar[int]
    INDENT_REF_FOR_FIELD_NUMBER: _ClassVar[int]
    INDENT_REF_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
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
    production_ref_for: PRODUCTION_INDENT_PRODUCTION_REF_FOR
    production_ref_id: int
    indent_ref_for: PRODUCTION_INDENT_INDENT_REF_FOR
    indent_ref_id: int
    family_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., production_ref_for: _Optional[_Union[PRODUCTION_INDENT_PRODUCTION_REF_FOR, str]] = ..., production_ref_id: _Optional[int] = ..., indent_ref_for: _Optional[_Union[PRODUCTION_INDENT_INDENT_REF_FOR, str]] = ..., indent_ref_id: _Optional[int] = ..., family_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class ProductionIndentsServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "location_id", "supervisor", "production_ref_for", "production_ref_id", "indent_ref_for", "indent_ref_id")
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
    PRODUCTION_REF_FOR_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_REF_ID_FIELD_NUMBER: _ClassVar[int]
    INDENT_REF_FOR_FIELD_NUMBER: _ClassVar[int]
    INDENT_REF_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: PRODUCTION_INDENT_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    location_id: int
    supervisor: str
    production_ref_for: PRODUCTION_INDENT_PRODUCTION_REF_FOR
    production_ref_id: int
    indent_ref_for: PRODUCTION_INDENT_INDENT_REF_FOR
    indent_ref_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[PRODUCTION_INDENT_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., production_ref_for: _Optional[_Union[PRODUCTION_INDENT_PRODUCTION_REF_FOR, str]] = ..., production_ref_id: _Optional[int] = ..., indent_ref_for: _Optional[_Union[PRODUCTION_INDENT_INDENT_REF_FOR, str]] = ..., indent_ref_id: _Optional[int] = ...) -> None: ...

class ProductionIndentItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "production_indent_id", "family_id", "search_key")
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
    PRODUCTION_INDENT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: PRODUCTION_INDENT_ITEM_SORT_KEY
    entity_uuid: str
    status: PRODUCTION_INDENT_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    production_indent_id: int
    family_id: int
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[PRODUCTION_INDENT_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[PRODUCTION_INDENT_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., production_indent_id: _Optional[int] = ..., family_id: _Optional[int] = ..., search_key: _Optional[str] = ...) -> None: ...

class ProductionIndentsServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[ProductionIndentItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[ProductionIndentItem, _Mapping]]] = ...) -> None: ...

class ProductionIndentIssuedStatistics(_message.Message):
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

class ProductionIndentIssuedStatisticsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ProductionIndentIssuedStatistics]
    def __init__(self, list: _Optional[_Iterable[_Union[ProductionIndentIssuedStatistics, _Mapping]]] = ...) -> None: ...
