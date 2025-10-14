from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from forms_fields_data import scailo_pb2 as _scailo_pb2_1
from magic_links import scailo_pb2 as _scailo_pb2_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QUOTATION_REQUEST_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUOTATION_REQUEST_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[QUOTATION_REQUEST_ITEM_SORT_KEY]
    QUOTATION_REQUEST_ITEM_SORT_KEY_CREATED_AT: _ClassVar[QUOTATION_REQUEST_ITEM_SORT_KEY]
    QUOTATION_REQUEST_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[QUOTATION_REQUEST_ITEM_SORT_KEY]
    QUOTATION_REQUEST_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[QUOTATION_REQUEST_ITEM_SORT_KEY]
    QUOTATION_REQUEST_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[QUOTATION_REQUEST_ITEM_SORT_KEY]
    QUOTATION_REQUEST_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[QUOTATION_REQUEST_ITEM_SORT_KEY]
    QUOTATION_REQUEST_ITEM_SORT_KEY_NAME: _ClassVar[QUOTATION_REQUEST_ITEM_SORT_KEY]
    QUOTATION_REQUEST_ITEM_SORT_KEY_BASELINE_PRICE: _ClassVar[QUOTATION_REQUEST_ITEM_SORT_KEY]
    QUOTATION_REQUEST_ITEM_SORT_KEY_QUANTITY: _ClassVar[QUOTATION_REQUEST_ITEM_SORT_KEY]
    QUOTATION_REQUEST_ITEM_SORT_KEY_DELIVERY_DATE: _ClassVar[QUOTATION_REQUEST_ITEM_SORT_KEY]

class QUOTATION_REQUEST_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUOTATION_REQUEST_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[QUOTATION_REQUEST_ITEM_STATUS]
    QUOTATION_REQUEST_ITEM_STATUS_APPROVED: _ClassVar[QUOTATION_REQUEST_ITEM_STATUS]
    QUOTATION_REQUEST_ITEM_STATUS_UNAPPROVED: _ClassVar[QUOTATION_REQUEST_ITEM_STATUS]

class QUOTATION_REQUEST_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUOTATION_REQUEST_SORT_KEY_ID_UNSPECIFIED: _ClassVar[QUOTATION_REQUEST_SORT_KEY]
    QUOTATION_REQUEST_SORT_KEY_CREATED_AT: _ClassVar[QUOTATION_REQUEST_SORT_KEY]
    QUOTATION_REQUEST_SORT_KEY_MODIFIED_AT: _ClassVar[QUOTATION_REQUEST_SORT_KEY]
    QUOTATION_REQUEST_SORT_KEY_APPROVED_ON: _ClassVar[QUOTATION_REQUEST_SORT_KEY]
    QUOTATION_REQUEST_SORT_KEY_APPROVED_BY: _ClassVar[QUOTATION_REQUEST_SORT_KEY]
    QUOTATION_REQUEST_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[QUOTATION_REQUEST_SORT_KEY]
    QUOTATION_REQUEST_SORT_KEY_COMPLETED_ON: _ClassVar[QUOTATION_REQUEST_SORT_KEY]
    QUOTATION_REQUEST_SORT_KEY_REFERENCE_ID: _ClassVar[QUOTATION_REQUEST_SORT_KEY]
    QUOTATION_REQUEST_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[QUOTATION_REQUEST_SORT_KEY]
    QUOTATION_REQUEST_SORT_KEY_PRIORITY: _ClassVar[QUOTATION_REQUEST_SORT_KEY]
QUOTATION_REQUEST_ITEM_SORT_KEY_ID_UNSPECIFIED: QUOTATION_REQUEST_ITEM_SORT_KEY
QUOTATION_REQUEST_ITEM_SORT_KEY_CREATED_AT: QUOTATION_REQUEST_ITEM_SORT_KEY
QUOTATION_REQUEST_ITEM_SORT_KEY_MODIFIED_AT: QUOTATION_REQUEST_ITEM_SORT_KEY
QUOTATION_REQUEST_ITEM_SORT_KEY_APPROVED_ON: QUOTATION_REQUEST_ITEM_SORT_KEY
QUOTATION_REQUEST_ITEM_SORT_KEY_APPROVED_BY: QUOTATION_REQUEST_ITEM_SORT_KEY
QUOTATION_REQUEST_ITEM_SORT_KEY_APPROVER_ROLE_ID: QUOTATION_REQUEST_ITEM_SORT_KEY
QUOTATION_REQUEST_ITEM_SORT_KEY_NAME: QUOTATION_REQUEST_ITEM_SORT_KEY
QUOTATION_REQUEST_ITEM_SORT_KEY_BASELINE_PRICE: QUOTATION_REQUEST_ITEM_SORT_KEY
QUOTATION_REQUEST_ITEM_SORT_KEY_QUANTITY: QUOTATION_REQUEST_ITEM_SORT_KEY
QUOTATION_REQUEST_ITEM_SORT_KEY_DELIVERY_DATE: QUOTATION_REQUEST_ITEM_SORT_KEY
QUOTATION_REQUEST_ITEM_STATUS_ANY_UNSPECIFIED: QUOTATION_REQUEST_ITEM_STATUS
QUOTATION_REQUEST_ITEM_STATUS_APPROVED: QUOTATION_REQUEST_ITEM_STATUS
QUOTATION_REQUEST_ITEM_STATUS_UNAPPROVED: QUOTATION_REQUEST_ITEM_STATUS
QUOTATION_REQUEST_SORT_KEY_ID_UNSPECIFIED: QUOTATION_REQUEST_SORT_KEY
QUOTATION_REQUEST_SORT_KEY_CREATED_AT: QUOTATION_REQUEST_SORT_KEY
QUOTATION_REQUEST_SORT_KEY_MODIFIED_AT: QUOTATION_REQUEST_SORT_KEY
QUOTATION_REQUEST_SORT_KEY_APPROVED_ON: QUOTATION_REQUEST_SORT_KEY
QUOTATION_REQUEST_SORT_KEY_APPROVED_BY: QUOTATION_REQUEST_SORT_KEY
QUOTATION_REQUEST_SORT_KEY_APPROVER_ROLE_ID: QUOTATION_REQUEST_SORT_KEY
QUOTATION_REQUEST_SORT_KEY_COMPLETED_ON: QUOTATION_REQUEST_SORT_KEY
QUOTATION_REQUEST_SORT_KEY_REFERENCE_ID: QUOTATION_REQUEST_SORT_KEY
QUOTATION_REQUEST_SORT_KEY_FINAL_REF_NUMBER: QUOTATION_REQUEST_SORT_KEY
QUOTATION_REQUEST_SORT_KEY_PRIORITY: QUOTATION_REQUEST_SORT_KEY

class QuotationsRequestsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "purchase_enquiry_id", "last_date", "currency_id", "renewal_period", "priority", "description", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_ENQUIRY_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_DATE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    RENEWAL_PERIOD_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    purchase_enquiry_id: int
    last_date: str
    currency_id: int
    renewal_period: int
    priority: str
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., purchase_enquiry_id: _Optional[int] = ..., last_date: _Optional[str] = ..., currency_id: _Optional[int] = ..., renewal_period: _Optional[int] = ..., priority: _Optional[str] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class QuotationsRequestsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "last_date", "currency_id", "renewal_period", "priority", "description", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_DATE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    RENEWAL_PERIOD_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    last_date: str
    currency_id: int
    renewal_period: int
    priority: str
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., last_date: _Optional[str] = ..., currency_id: _Optional[int] = ..., renewal_period: _Optional[int] = ..., priority: _Optional[str] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class QuotationsRequestsServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ...) -> None: ...

class QuotationRequestAncillaryParameters(_message.Message):
    __slots__ = ("purchase_enquiry_uuid", "currency_uuid")
    PURCHASE_ENQUIRY_UUID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_UUID_FIELD_NUMBER: _ClassVar[int]
    purchase_enquiry_uuid: str
    currency_uuid: str
    def __init__(self, purchase_enquiry_uuid: _Optional[str] = ..., currency_uuid: _Optional[str] = ...) -> None: ...

class QuotationRequest(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "purchase_enquiry_id", "last_date", "currency_id", "renewal_period", "priority", "description", "list", "form_data", "total_value")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_ENQUIRY_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_DATE_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    RENEWAL_PERIOD_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    completed_on: int
    vault_folder_id: int
    reference_id: str
    final_ref_number: str
    purchase_enquiry_id: int
    last_date: str
    currency_id: int
    renewal_period: int
    priority: str
    description: str
    list: _containers.RepeatedCompositeFieldContainer[QuotationRequestItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatum]
    total_value: float
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., purchase_enquiry_id: _Optional[int] = ..., last_date: _Optional[str] = ..., currency_id: _Optional[int] = ..., renewal_period: _Optional[int] = ..., priority: _Optional[str] = ..., description: _Optional[str] = ..., list: _Optional[_Iterable[_Union[QuotationRequestItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatum, _Mapping]]] = ..., total_value: _Optional[float] = ...) -> None: ...

class QuotationsRequestsServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "vault_folder_id", "quotation_request_id", "name", "hsn_sac_code", "baseline_price", "quantity", "uom_id", "delivery_date", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    QUOTATION_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    HSN_SAC_CODE_FIELD_NUMBER: _ClassVar[int]
    BASELINE_PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    vault_folder_id: int
    quotation_request_id: int
    name: str
    hsn_sac_code: str
    baseline_price: int
    quantity: int
    uom_id: int
    delivery_date: str
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., quotation_request_id: _Optional[int] = ..., name: _Optional[str] = ..., hsn_sac_code: _Optional[str] = ..., baseline_price: _Optional[int] = ..., quantity: _Optional[int] = ..., uom_id: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ...) -> None: ...

class QuotationsRequestsServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "vault_folder_id", "name", "hsn_sac_code", "baseline_price", "quantity", "uom_id", "delivery_date", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    HSN_SAC_CODE_FIELD_NUMBER: _ClassVar[int]
    BASELINE_PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    vault_folder_id: int
    name: str
    hsn_sac_code: str
    baseline_price: int
    quantity: int
    uom_id: int
    delivery_date: str
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., hsn_sac_code: _Optional[str] = ..., baseline_price: _Optional[int] = ..., quantity: _Optional[int] = ..., uom_id: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ...) -> None: ...

class QuotationRequestItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "vault_folder_id", "quotation_request_id", "name", "hsn_sac_code", "baseline_price", "quantity", "uom_id", "delivery_date", "specifications")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    QUOTATION_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    HSN_SAC_CODE_FIELD_NUMBER: _ClassVar[int]
    BASELINE_PRICE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    vault_folder_id: int
    quotation_request_id: int
    name: str
    hsn_sac_code: str
    baseline_price: int
    quantity: int
    uom_id: int
    delivery_date: str
    specifications: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., quotation_request_id: _Optional[int] = ..., name: _Optional[str] = ..., hsn_sac_code: _Optional[str] = ..., baseline_price: _Optional[int] = ..., quantity: _Optional[int] = ..., uom_id: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ...) -> None: ...

class QuotationsRequestsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[QuotationRequest]
    def __init__(self, list: _Optional[_Iterable[_Union[QuotationRequest, _Mapping]]] = ...) -> None: ...

class QuotationsRequestsItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[QuotationRequestItem]
    def __init__(self, list: _Optional[_Iterable[_Union[QuotationRequestItem, _Mapping]]] = ...) -> None: ...

class QuotationRequestItemHistoryRequest(_message.Message):
    __slots__ = ("quotation_request_id", "name")
    QUOTATION_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    quotation_request_id: int
    name: str
    def __init__(self, quotation_request_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class QuotationRequestItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "quotation_request_id", "uom_id", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "search_key")
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
    QUOTATION_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: QUOTATION_REQUEST_ITEM_SORT_KEY
    entity_uuid: str
    status: QUOTATION_REQUEST_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    quotation_request_id: int
    uom_id: int
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[QUOTATION_REQUEST_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[QUOTATION_REQUEST_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., quotation_request_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., search_key: _Optional[str] = ...) -> None: ...

class QuotationsRequestsServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[QuotationRequestItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[QuotationRequestItem, _Mapping]]] = ...) -> None: ...

class QuotationsRequestsServicePaginationReq(_message.Message):
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
    sort_key: QUOTATION_REQUEST_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[QUOTATION_REQUEST_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class QuotationsRequestsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[QuotationRequest]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[QuotationRequest, _Mapping]]] = ...) -> None: ...

class QuotationsRequestsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "purchase_enquiry_id", "currency_id", "form_data")
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
    PURCHASE_ENQUIRY_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: QUOTATION_REQUEST_SORT_KEY
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
    purchase_enquiry_id: int
    currency_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[QUOTATION_REQUEST_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., purchase_enquiry_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class QuotationsRequestsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "purchase_enquiry_id", "currency_id", "form_data")
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
    PURCHASE_ENQUIRY_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
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
    purchase_enquiry_id: int
    currency_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., purchase_enquiry_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class QuotationsRequestsServiceSearchAllReq(_message.Message):
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
    sort_key: QUOTATION_REQUEST_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[QUOTATION_REQUEST_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ...) -> None: ...
