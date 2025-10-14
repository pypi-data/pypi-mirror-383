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

class WORK_ORDER_REF_FROM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WORK_ORDER_REF_FROM_ANY_UNSPECIFIED: _ClassVar[WORK_ORDER_REF_FROM]
    WORK_ORDER_REF_FROM_SALES_ORDER: _ClassVar[WORK_ORDER_REF_FROM]

class WORK_ORDER_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WORK_ORDER_SORT_KEY_ID_UNSPECIFIED: _ClassVar[WORK_ORDER_SORT_KEY]
    WORK_ORDER_SORT_KEY_CREATED_AT: _ClassVar[WORK_ORDER_SORT_KEY]
    WORK_ORDER_SORT_KEY_MODIFIED_AT: _ClassVar[WORK_ORDER_SORT_KEY]
    WORK_ORDER_SORT_KEY_APPROVED_ON: _ClassVar[WORK_ORDER_SORT_KEY]
    WORK_ORDER_SORT_KEY_APPROVED_BY: _ClassVar[WORK_ORDER_SORT_KEY]
    WORK_ORDER_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[WORK_ORDER_SORT_KEY]
    WORK_ORDER_SORT_KEY_COMPLETED_ON: _ClassVar[WORK_ORDER_SORT_KEY]
    WORK_ORDER_SORT_KEY_REFERENCE_ID: _ClassVar[WORK_ORDER_SORT_KEY]
    WORK_ORDER_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[WORK_ORDER_SORT_KEY]
    WORK_ORDER_SORT_KEY_LOCATION_ID: _ClassVar[WORK_ORDER_SORT_KEY]
    WORK_ORDER_SORT_KEY_AMENDMENT_COUNT: _ClassVar[WORK_ORDER_SORT_KEY]

class WORK_ORDER_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WORK_ORDER_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[WORK_ORDER_ITEM_SORT_KEY]
    WORK_ORDER_ITEM_SORT_KEY_CREATED_AT: _ClassVar[WORK_ORDER_ITEM_SORT_KEY]
    WORK_ORDER_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[WORK_ORDER_ITEM_SORT_KEY]
    WORK_ORDER_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[WORK_ORDER_ITEM_SORT_KEY]
    WORK_ORDER_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[WORK_ORDER_ITEM_SORT_KEY]
    WORK_ORDER_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[WORK_ORDER_ITEM_SORT_KEY]
    WORK_ORDER_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[WORK_ORDER_ITEM_SORT_KEY]
    WORK_ORDER_ITEM_SORT_KEY_QUANTITY: _ClassVar[WORK_ORDER_ITEM_SORT_KEY]
    WORK_ORDER_ITEM_SORT_KEY_DELIVERY_DATE: _ClassVar[WORK_ORDER_ITEM_SORT_KEY]

class WORK_ORDER_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WORK_ORDER_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[WORK_ORDER_ITEM_STATUS]
    WORK_ORDER_ITEM_STATUS_APPROVED: _ClassVar[WORK_ORDER_ITEM_STATUS]
    WORK_ORDER_ITEM_STATUS_UNAPPROVED: _ClassVar[WORK_ORDER_ITEM_STATUS]
WORK_ORDER_REF_FROM_ANY_UNSPECIFIED: WORK_ORDER_REF_FROM
WORK_ORDER_REF_FROM_SALES_ORDER: WORK_ORDER_REF_FROM
WORK_ORDER_SORT_KEY_ID_UNSPECIFIED: WORK_ORDER_SORT_KEY
WORK_ORDER_SORT_KEY_CREATED_AT: WORK_ORDER_SORT_KEY
WORK_ORDER_SORT_KEY_MODIFIED_AT: WORK_ORDER_SORT_KEY
WORK_ORDER_SORT_KEY_APPROVED_ON: WORK_ORDER_SORT_KEY
WORK_ORDER_SORT_KEY_APPROVED_BY: WORK_ORDER_SORT_KEY
WORK_ORDER_SORT_KEY_APPROVER_ROLE_ID: WORK_ORDER_SORT_KEY
WORK_ORDER_SORT_KEY_COMPLETED_ON: WORK_ORDER_SORT_KEY
WORK_ORDER_SORT_KEY_REFERENCE_ID: WORK_ORDER_SORT_KEY
WORK_ORDER_SORT_KEY_FINAL_REF_NUMBER: WORK_ORDER_SORT_KEY
WORK_ORDER_SORT_KEY_LOCATION_ID: WORK_ORDER_SORT_KEY
WORK_ORDER_SORT_KEY_AMENDMENT_COUNT: WORK_ORDER_SORT_KEY
WORK_ORDER_ITEM_SORT_KEY_ID_UNSPECIFIED: WORK_ORDER_ITEM_SORT_KEY
WORK_ORDER_ITEM_SORT_KEY_CREATED_AT: WORK_ORDER_ITEM_SORT_KEY
WORK_ORDER_ITEM_SORT_KEY_MODIFIED_AT: WORK_ORDER_ITEM_SORT_KEY
WORK_ORDER_ITEM_SORT_KEY_APPROVED_ON: WORK_ORDER_ITEM_SORT_KEY
WORK_ORDER_ITEM_SORT_KEY_APPROVED_BY: WORK_ORDER_ITEM_SORT_KEY
WORK_ORDER_ITEM_SORT_KEY_APPROVER_ROLE_ID: WORK_ORDER_ITEM_SORT_KEY
WORK_ORDER_ITEM_SORT_KEY_FAMILY_ID: WORK_ORDER_ITEM_SORT_KEY
WORK_ORDER_ITEM_SORT_KEY_QUANTITY: WORK_ORDER_ITEM_SORT_KEY
WORK_ORDER_ITEM_SORT_KEY_DELIVERY_DATE: WORK_ORDER_ITEM_SORT_KEY
WORK_ORDER_ITEM_STATUS_ANY_UNSPECIFIED: WORK_ORDER_ITEM_STATUS
WORK_ORDER_ITEM_STATUS_APPROVED: WORK_ORDER_ITEM_STATUS
WORK_ORDER_ITEM_STATUS_UNAPPROVED: WORK_ORDER_ITEM_STATUS

class WorkOrdersServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "ref_from", "ref_id", "location_id", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    ref_from: WORK_ORDER_REF_FROM
    ref_id: int
    location_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., ref_from: _Optional[_Union[WORK_ORDER_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., location_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class WorkOrdersServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class WorkOrdersServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid", "populate_using_equation_dependencies")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    POPULATE_USING_EQUATION_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    populate_using_equation_dependencies: bool
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ..., populate_using_equation_dependencies: _Optional[bool] = ...) -> None: ...

class WorkOrderAncillaryParameters(_message.Message):
    __slots__ = ("ref_uuid", "location_uuid")
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_UUID_FIELD_NUMBER: _ClassVar[int]
    ref_uuid: str
    location_uuid: str
    def __init__(self, ref_uuid: _Optional[str] = ..., location_uuid: _Optional[str] = ...) -> None: ...

class WorkOrder(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "ref_from", "ref_id", "location_id", "amendment_count", "list", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_COUNT_FIELD_NUMBER: _ClassVar[int]
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
    ref_from: WORK_ORDER_REF_FROM
    ref_id: int
    location_id: int
    amendment_count: int
    list: _containers.RepeatedCompositeFieldContainer[WorkOrderItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[WORK_ORDER_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., location_id: _Optional[int] = ..., amendment_count: _Optional[int] = ..., list: _Optional[_Iterable[_Union[WorkOrderItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class WorkOrdersServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "work_order_id", "family_id", "quantity", "delivery_date")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    WORK_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    work_order_id: int
    family_id: int
    quantity: int
    delivery_date: str
    def __init__(self, user_comment: _Optional[str] = ..., work_order_id: _Optional[int] = ..., family_id: _Optional[int] = ..., quantity: _Optional[int] = ..., delivery_date: _Optional[str] = ...) -> None: ...

class WorkOrdersServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "quantity", "delivery_date")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    quantity: int
    delivery_date: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., quantity: _Optional[int] = ..., delivery_date: _Optional[str] = ...) -> None: ...

class WorkOrderItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "work_order_id", "family_id", "quantity", "delivery_date")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    WORK_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    work_order_id: int
    family_id: int
    quantity: int
    delivery_date: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., work_order_id: _Optional[int] = ..., family_id: _Optional[int] = ..., quantity: _Optional[int] = ..., delivery_date: _Optional[str] = ...) -> None: ...

class WorkOrdersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[WorkOrder]
    def __init__(self, list: _Optional[_Iterable[_Union[WorkOrder, _Mapping]]] = ...) -> None: ...

class WorkOrdersItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[WorkOrderItem]
    def __init__(self, list: _Optional[_Iterable[_Union[WorkOrderItem, _Mapping]]] = ...) -> None: ...

class WorkOrderItemHistoryRequest(_message.Message):
    __slots__ = ("work_order_id", "family_id")
    WORK_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    work_order_id: int
    family_id: int
    def __init__(self, work_order_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class WorkOrderItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("work_order_id", "family_id")
    WORK_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    work_order_id: int
    family_id: int
    def __init__(self, work_order_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class WorkOrdersServicePaginationReq(_message.Message):
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
    sort_key: WORK_ORDER_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[WORK_ORDER_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class WorkOrdersServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[WorkOrder]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[WorkOrder, _Mapping]]] = ...) -> None: ...

class WorkOrdersServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "location_id", "family_id", "consignee_client_id", "buyer_client_id", "project_id", "form_data")
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
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: WORK_ORDER_SORT_KEY
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
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    reference_id: str
    final_ref_number: str
    ref_from: WORK_ORDER_REF_FROM
    ref_id: int
    location_id: int
    family_id: int
    consignee_client_id: int
    buyer_client_id: int
    project_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[WORK_ORDER_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[WORK_ORDER_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., location_id: _Optional[int] = ..., family_id: _Optional[int] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., project_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class WorkOrdersServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "location_id", "family_id", "consignee_client_id", "buyer_client_id", "project_id", "form_data")
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
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
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
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    reference_id: str
    final_ref_number: str
    ref_from: WORK_ORDER_REF_FROM
    ref_id: int
    location_id: int
    family_id: int
    consignee_client_id: int
    buyer_client_id: int
    project_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[WORK_ORDER_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., location_id: _Optional[int] = ..., family_id: _Optional[int] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., project_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class WorkOrdersServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "ref_from", "ref_id", "location_id", "consignee_client_id", "buyer_client_id")
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
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: WORK_ORDER_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    ref_from: WORK_ORDER_REF_FROM
    ref_id: int
    location_id: int
    consignee_client_id: int
    buyer_client_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[WORK_ORDER_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., ref_from: _Optional[_Union[WORK_ORDER_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., location_id: _Optional[int] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ...) -> None: ...

class WorkOrderItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "work_order_id", "family_id", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "search_key")
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
    WORK_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: WORK_ORDER_ITEM_SORT_KEY
    entity_uuid: str
    status: WORK_ORDER_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    work_order_id: int
    family_id: int
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[WORK_ORDER_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[WORK_ORDER_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., work_order_id: _Optional[int] = ..., family_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., search_key: _Optional[str] = ...) -> None: ...

class WorkOrdersServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[WorkOrderItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[WorkOrderItem, _Mapping]]] = ...) -> None: ...

class WorkOrderRequirementStatistics(_message.Message):
    __slots__ = ("family_id", "sales_order_quantity", "work_order_quantity")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    SALES_ORDER_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    WORK_ORDER_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    sales_order_quantity: int
    work_order_quantity: int
    def __init__(self, family_id: _Optional[int] = ..., sales_order_quantity: _Optional[int] = ..., work_order_quantity: _Optional[int] = ...) -> None: ...

class WorkOrderRequirementStatisticsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[WorkOrderRequirementStatistics]
    def __init__(self, list: _Optional[_Iterable[_Union[WorkOrderRequirementStatistics, _Mapping]]] = ...) -> None: ...

class WorkOrderProductionStatistics(_message.Message):
    __slots__ = ("family_id", "production_plan_quantity", "work_order_quantity", "produced_quantity")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_PLAN_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    WORK_ORDER_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRODUCED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    production_plan_quantity: int
    work_order_quantity: int
    produced_quantity: int
    def __init__(self, family_id: _Optional[int] = ..., production_plan_quantity: _Optional[int] = ..., work_order_quantity: _Optional[int] = ..., produced_quantity: _Optional[int] = ...) -> None: ...

class WorkOrderProductionStatisticsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[WorkOrderProductionStatistics]
    def __init__(self, list: _Optional[_Iterable[_Union[WorkOrderProductionStatistics, _Mapping]]] = ...) -> None: ...
