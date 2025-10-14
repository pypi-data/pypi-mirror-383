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

class PRODUCTION_PLAN_REF_FROM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRODUCTION_PLAN_REF_FROM_ANY_UNSPECIFIED: _ClassVar[PRODUCTION_PLAN_REF_FROM]
    PRODUCTION_PLAN_REF_FROM_WORK_ORDER: _ClassVar[PRODUCTION_PLAN_REF_FROM]

class PRODUCTION_PLAN_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRODUCTION_PLAN_SORT_KEY_ID_UNSPECIFIED: _ClassVar[PRODUCTION_PLAN_SORT_KEY]
    PRODUCTION_PLAN_SORT_KEY_CREATED_AT: _ClassVar[PRODUCTION_PLAN_SORT_KEY]
    PRODUCTION_PLAN_SORT_KEY_MODIFIED_AT: _ClassVar[PRODUCTION_PLAN_SORT_KEY]
    PRODUCTION_PLAN_SORT_KEY_APPROVED_ON: _ClassVar[PRODUCTION_PLAN_SORT_KEY]
    PRODUCTION_PLAN_SORT_KEY_APPROVED_BY: _ClassVar[PRODUCTION_PLAN_SORT_KEY]
    PRODUCTION_PLAN_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[PRODUCTION_PLAN_SORT_KEY]
    PRODUCTION_PLAN_SORT_KEY_COMPLETED_ON: _ClassVar[PRODUCTION_PLAN_SORT_KEY]
    PRODUCTION_PLAN_SORT_KEY_REFERENCE_ID: _ClassVar[PRODUCTION_PLAN_SORT_KEY]
    PRODUCTION_PLAN_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[PRODUCTION_PLAN_SORT_KEY]
    PRODUCTION_PLAN_SORT_KEY_LOCATION_ID: _ClassVar[PRODUCTION_PLAN_SORT_KEY]
    PRODUCTION_PLAN_SORT_KEY_STARTS_AT: _ClassVar[PRODUCTION_PLAN_SORT_KEY]
    PRODUCTION_PLAN_SORT_KEY_ENDS_AT: _ClassVar[PRODUCTION_PLAN_SORT_KEY]

class PRODUCTION_PLAN_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRODUCTION_PLAN_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[PRODUCTION_PLAN_ITEM_SORT_KEY]
    PRODUCTION_PLAN_ITEM_SORT_KEY_CREATED_AT: _ClassVar[PRODUCTION_PLAN_ITEM_SORT_KEY]
    PRODUCTION_PLAN_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[PRODUCTION_PLAN_ITEM_SORT_KEY]
    PRODUCTION_PLAN_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[PRODUCTION_PLAN_ITEM_SORT_KEY]
    PRODUCTION_PLAN_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[PRODUCTION_PLAN_ITEM_SORT_KEY]
    PRODUCTION_PLAN_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[PRODUCTION_PLAN_ITEM_SORT_KEY]
    PRODUCTION_PLAN_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[PRODUCTION_PLAN_ITEM_SORT_KEY]
    PRODUCTION_PLAN_ITEM_SORT_KEY_QUANTITY: _ClassVar[PRODUCTION_PLAN_ITEM_SORT_KEY]

class PRODUCTION_PLAN_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRODUCTION_PLAN_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[PRODUCTION_PLAN_ITEM_STATUS]
    PRODUCTION_PLAN_ITEM_STATUS_APPROVED: _ClassVar[PRODUCTION_PLAN_ITEM_STATUS]
    PRODUCTION_PLAN_ITEM_STATUS_UNAPPROVED: _ClassVar[PRODUCTION_PLAN_ITEM_STATUS]
PRODUCTION_PLAN_REF_FROM_ANY_UNSPECIFIED: PRODUCTION_PLAN_REF_FROM
PRODUCTION_PLAN_REF_FROM_WORK_ORDER: PRODUCTION_PLAN_REF_FROM
PRODUCTION_PLAN_SORT_KEY_ID_UNSPECIFIED: PRODUCTION_PLAN_SORT_KEY
PRODUCTION_PLAN_SORT_KEY_CREATED_AT: PRODUCTION_PLAN_SORT_KEY
PRODUCTION_PLAN_SORT_KEY_MODIFIED_AT: PRODUCTION_PLAN_SORT_KEY
PRODUCTION_PLAN_SORT_KEY_APPROVED_ON: PRODUCTION_PLAN_SORT_KEY
PRODUCTION_PLAN_SORT_KEY_APPROVED_BY: PRODUCTION_PLAN_SORT_KEY
PRODUCTION_PLAN_SORT_KEY_APPROVER_ROLE_ID: PRODUCTION_PLAN_SORT_KEY
PRODUCTION_PLAN_SORT_KEY_COMPLETED_ON: PRODUCTION_PLAN_SORT_KEY
PRODUCTION_PLAN_SORT_KEY_REFERENCE_ID: PRODUCTION_PLAN_SORT_KEY
PRODUCTION_PLAN_SORT_KEY_FINAL_REF_NUMBER: PRODUCTION_PLAN_SORT_KEY
PRODUCTION_PLAN_SORT_KEY_LOCATION_ID: PRODUCTION_PLAN_SORT_KEY
PRODUCTION_PLAN_SORT_KEY_STARTS_AT: PRODUCTION_PLAN_SORT_KEY
PRODUCTION_PLAN_SORT_KEY_ENDS_AT: PRODUCTION_PLAN_SORT_KEY
PRODUCTION_PLAN_ITEM_SORT_KEY_ID_UNSPECIFIED: PRODUCTION_PLAN_ITEM_SORT_KEY
PRODUCTION_PLAN_ITEM_SORT_KEY_CREATED_AT: PRODUCTION_PLAN_ITEM_SORT_KEY
PRODUCTION_PLAN_ITEM_SORT_KEY_MODIFIED_AT: PRODUCTION_PLAN_ITEM_SORT_KEY
PRODUCTION_PLAN_ITEM_SORT_KEY_APPROVED_ON: PRODUCTION_PLAN_ITEM_SORT_KEY
PRODUCTION_PLAN_ITEM_SORT_KEY_APPROVED_BY: PRODUCTION_PLAN_ITEM_SORT_KEY
PRODUCTION_PLAN_ITEM_SORT_KEY_APPROVER_ROLE_ID: PRODUCTION_PLAN_ITEM_SORT_KEY
PRODUCTION_PLAN_ITEM_SORT_KEY_FAMILY_ID: PRODUCTION_PLAN_ITEM_SORT_KEY
PRODUCTION_PLAN_ITEM_SORT_KEY_QUANTITY: PRODUCTION_PLAN_ITEM_SORT_KEY
PRODUCTION_PLAN_ITEM_STATUS_ANY_UNSPECIFIED: PRODUCTION_PLAN_ITEM_STATUS
PRODUCTION_PLAN_ITEM_STATUS_APPROVED: PRODUCTION_PLAN_ITEM_STATUS
PRODUCTION_PLAN_ITEM_STATUS_UNAPPROVED: PRODUCTION_PLAN_ITEM_STATUS

class ProductionPlansServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "project_id", "vault_folder_id", "reference_id", "ref_from", "ref_id", "location_id", "supervisor", "starts_at", "ends_at", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    project_id: int
    vault_folder_id: int
    reference_id: str
    ref_from: PRODUCTION_PLAN_REF_FROM
    ref_id: int
    location_id: int
    supervisor: str
    starts_at: int
    ends_at: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., project_id: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., ref_from: _Optional[_Union[PRODUCTION_PLAN_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., starts_at: _Optional[int] = ..., ends_at: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class ProductionPlansServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "project_id", "vault_folder_id", "reference_id", "supervisor", "starts_at", "ends_at", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    project_id: int
    vault_folder_id: int
    reference_id: str
    supervisor: str
    starts_at: int
    ends_at: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., project_id: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., supervisor: _Optional[str] = ..., starts_at: _Optional[int] = ..., ends_at: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class ProductionPlansServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid", "populate_using_equation_dependencies")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    POPULATE_USING_EQUATION_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    populate_using_equation_dependencies: bool
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ..., populate_using_equation_dependencies: _Optional[bool] = ...) -> None: ...

class ProductionPlanAncillaryParameters(_message.Message):
    __slots__ = ("ref_uuid", "location_uuid")
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_UUID_FIELD_NUMBER: _ClassVar[int]
    ref_uuid: str
    location_uuid: str
    def __init__(self, ref_uuid: _Optional[str] = ..., location_uuid: _Optional[str] = ...) -> None: ...

class ProductionPlan(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "project_id", "vault_folder_id", "reference_id", "final_ref_number", "ref_from", "ref_id", "location_id", "supervisor", "starts_at", "ends_at", "list", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    completed_on: int
    project_id: int
    vault_folder_id: int
    reference_id: str
    final_ref_number: str
    ref_from: PRODUCTION_PLAN_REF_FROM
    ref_id: int
    location_id: int
    supervisor: str
    starts_at: int
    ends_at: int
    list: _containers.RepeatedCompositeFieldContainer[ProductionPlanItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., project_id: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[PRODUCTION_PLAN_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., starts_at: _Optional[int] = ..., ends_at: _Optional[int] = ..., list: _Optional[_Iterable[_Union[ProductionPlanItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class ProductionPlansServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "production_plan_id", "family_id", "quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    production_plan_id: int
    family_id: int
    quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., production_plan_id: _Optional[int] = ..., family_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class ProductionPlansServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class ProductionPlanItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "production_plan_id", "family_id", "quantity")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    production_plan_id: int
    family_id: int
    quantity: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., production_plan_id: _Optional[int] = ..., family_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class ProductionPlansList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ProductionPlan]
    def __init__(self, list: _Optional[_Iterable[_Union[ProductionPlan, _Mapping]]] = ...) -> None: ...

class ProductionPlansItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ProductionPlanItem]
    def __init__(self, list: _Optional[_Iterable[_Union[ProductionPlanItem, _Mapping]]] = ...) -> None: ...

class ProductionPlanItemHistoryRequest(_message.Message):
    __slots__ = ("production_plan_id", "family_id")
    PRODUCTION_PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    production_plan_id: int
    family_id: int
    def __init__(self, production_plan_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class ProductionPlanItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("production_plan_id", "family_id")
    PRODUCTION_PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    production_plan_id: int
    family_id: int
    def __init__(self, production_plan_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class ProductionPlansServiceAlreadyAddedQuantityForSourceRequest(_message.Message):
    __slots__ = ("ref_from", "ref_id", "family_id")
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ref_from: PRODUCTION_PLAN_REF_FROM
    ref_id: int
    family_id: int
    def __init__(self, ref_from: _Optional[_Union[PRODUCTION_PLAN_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class ProductionPlansServicePaginationReq(_message.Message):
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
    sort_key: PRODUCTION_PLAN_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[PRODUCTION_PLAN_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class ProductionPlansServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[ProductionPlan]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[ProductionPlan, _Mapping]]] = ...) -> None: ...

class ProductionPlansServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "location_id", "supervisor", "starts_at_start", "starts_at_end", "ends_at_start", "ends_at_end", "family_id", "project_id", "buyer_client_id", "form_data")
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
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_START_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_END_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_START_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_END_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: PRODUCTION_PLAN_SORT_KEY
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
    ref_from: PRODUCTION_PLAN_REF_FROM
    ref_id: int
    location_id: int
    supervisor: str
    starts_at_start: int
    starts_at_end: int
    ends_at_start: int
    ends_at_end: int
    family_id: int
    project_id: int
    buyer_client_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[PRODUCTION_PLAN_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[PRODUCTION_PLAN_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., starts_at_start: _Optional[int] = ..., starts_at_end: _Optional[int] = ..., ends_at_start: _Optional[int] = ..., ends_at_end: _Optional[int] = ..., family_id: _Optional[int] = ..., project_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class ProductionPlansServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "location_id", "supervisor", "starts_at_start", "starts_at_end", "ends_at_start", "ends_at_end", "family_id", "project_id", "buyer_client_id", "form_data")
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
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_START_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_END_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_START_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_END_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
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
    ref_from: PRODUCTION_PLAN_REF_FROM
    ref_id: int
    location_id: int
    supervisor: str
    starts_at_start: int
    starts_at_end: int
    ends_at_start: int
    ends_at_end: int
    family_id: int
    project_id: int
    buyer_client_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[PRODUCTION_PLAN_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ..., starts_at_start: _Optional[int] = ..., starts_at_end: _Optional[int] = ..., ends_at_start: _Optional[int] = ..., ends_at_end: _Optional[int] = ..., family_id: _Optional[int] = ..., project_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class ProductionPlansServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "ref_from", "ref_id", "location_id", "supervisor")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: PRODUCTION_PLAN_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    ref_from: PRODUCTION_PLAN_REF_FROM
    ref_id: int
    location_id: int
    supervisor: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[PRODUCTION_PLAN_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., ref_from: _Optional[_Union[PRODUCTION_PLAN_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., location_id: _Optional[int] = ..., supervisor: _Optional[str] = ...) -> None: ...

class ProductionPlanItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "production_plan_id", "family_id", "family_type", "search_key")
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
    PRODUCTION_PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: PRODUCTION_PLAN_ITEM_SORT_KEY
    entity_uuid: str
    status: PRODUCTION_PLAN_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    production_plan_id: int
    family_id: int
    family_type: _scailo_pb2_1.FAMILY_TYPE
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[PRODUCTION_PLAN_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[PRODUCTION_PLAN_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., production_plan_id: _Optional[int] = ..., family_id: _Optional[int] = ..., family_type: _Optional[_Union[_scailo_pb2_1.FAMILY_TYPE, str]] = ..., search_key: _Optional[str] = ...) -> None: ...

class ProductionPlansServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[ProductionPlanItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[ProductionPlanItem, _Mapping]]] = ...) -> None: ...

class ProductionPlanProductionStatistics(_message.Message):
    __slots__ = ("family_id", "production_plan_quantity", "produced_quantity")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_PLAN_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRODUCED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    production_plan_quantity: int
    produced_quantity: int
    def __init__(self, family_id: _Optional[int] = ..., production_plan_quantity: _Optional[int] = ..., produced_quantity: _Optional[int] = ...) -> None: ...

class ProductionPlanProductionStatisticsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ProductionPlanProductionStatistics]
    def __init__(self, list: _Optional[_Iterable[_Union[ProductionPlanProductionStatistics, _Mapping]]] = ...) -> None: ...
