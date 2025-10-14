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

class SALES_ENQUIRY_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALES_ENQUIRY_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[SALES_ENQUIRY_ITEM_SORT_KEY]
    SALES_ENQUIRY_ITEM_SORT_KEY_CREATED_AT: _ClassVar[SALES_ENQUIRY_ITEM_SORT_KEY]
    SALES_ENQUIRY_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[SALES_ENQUIRY_ITEM_SORT_KEY]
    SALES_ENQUIRY_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[SALES_ENQUIRY_ITEM_SORT_KEY]
    SALES_ENQUIRY_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[SALES_ENQUIRY_ITEM_SORT_KEY]
    SALES_ENQUIRY_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[SALES_ENQUIRY_ITEM_SORT_KEY]
    SALES_ENQUIRY_ITEM_SORT_KEY_NAME: _ClassVar[SALES_ENQUIRY_ITEM_SORT_KEY]
    SALES_ENQUIRY_ITEM_SORT_KEY_INTERNAL_QUANTITY: _ClassVar[SALES_ENQUIRY_ITEM_SORT_KEY]
    SALES_ENQUIRY_ITEM_SORT_KEY_UNIT_PRICE: _ClassVar[SALES_ENQUIRY_ITEM_SORT_KEY]
    SALES_ENQUIRY_ITEM_SORT_KEY_DISCOUNT: _ClassVar[SALES_ENQUIRY_ITEM_SORT_KEY]
    SALES_ENQUIRY_ITEM_SORT_KEY_DELIVERY_DATE: _ClassVar[SALES_ENQUIRY_ITEM_SORT_KEY]

class SALES_ENQUIRY_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALES_ENQUIRY_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[SALES_ENQUIRY_ITEM_STATUS]
    SALES_ENQUIRY_ITEM_STATUS_APPROVED: _ClassVar[SALES_ENQUIRY_ITEM_STATUS]
    SALES_ENQUIRY_ITEM_STATUS_UNAPPROVED: _ClassVar[SALES_ENQUIRY_ITEM_STATUS]

class SALES_ENQUIRY_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALES_ENQUIRY_SORT_KEY_ID_UNSPECIFIED: _ClassVar[SALES_ENQUIRY_SORT_KEY]
    SALES_ENQUIRY_SORT_KEY_CREATED_AT: _ClassVar[SALES_ENQUIRY_SORT_KEY]
    SALES_ENQUIRY_SORT_KEY_MODIFIED_AT: _ClassVar[SALES_ENQUIRY_SORT_KEY]
    SALES_ENQUIRY_SORT_KEY_APPROVED_ON: _ClassVar[SALES_ENQUIRY_SORT_KEY]
    SALES_ENQUIRY_SORT_KEY_APPROVED_BY: _ClassVar[SALES_ENQUIRY_SORT_KEY]
    SALES_ENQUIRY_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[SALES_ENQUIRY_SORT_KEY]
    SALES_ENQUIRY_SORT_KEY_COMPLETED_ON: _ClassVar[SALES_ENQUIRY_SORT_KEY]
    SALES_ENQUIRY_SORT_KEY_REFERENCE_ID: _ClassVar[SALES_ENQUIRY_SORT_KEY]
    SALES_ENQUIRY_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[SALES_ENQUIRY_SORT_KEY]
    SALES_ENQUIRY_SORT_KEY_CONSIGNEE_CLIENT_ID: _ClassVar[SALES_ENQUIRY_SORT_KEY]
    SALES_ENQUIRY_SORT_KEY_BUYER_CLIENT_ID: _ClassVar[SALES_ENQUIRY_SORT_KEY]
    SALES_ENQUIRY_SORT_KEY_PRIORITY: _ClassVar[SALES_ENQUIRY_SORT_KEY]
    SALES_ENQUIRY_SORT_KEY_AMENDMENT_COUNT: _ClassVar[SALES_ENQUIRY_SORT_KEY]
SALES_ENQUIRY_ITEM_SORT_KEY_ID_UNSPECIFIED: SALES_ENQUIRY_ITEM_SORT_KEY
SALES_ENQUIRY_ITEM_SORT_KEY_CREATED_AT: SALES_ENQUIRY_ITEM_SORT_KEY
SALES_ENQUIRY_ITEM_SORT_KEY_MODIFIED_AT: SALES_ENQUIRY_ITEM_SORT_KEY
SALES_ENQUIRY_ITEM_SORT_KEY_APPROVED_ON: SALES_ENQUIRY_ITEM_SORT_KEY
SALES_ENQUIRY_ITEM_SORT_KEY_APPROVED_BY: SALES_ENQUIRY_ITEM_SORT_KEY
SALES_ENQUIRY_ITEM_SORT_KEY_APPROVER_ROLE_ID: SALES_ENQUIRY_ITEM_SORT_KEY
SALES_ENQUIRY_ITEM_SORT_KEY_NAME: SALES_ENQUIRY_ITEM_SORT_KEY
SALES_ENQUIRY_ITEM_SORT_KEY_INTERNAL_QUANTITY: SALES_ENQUIRY_ITEM_SORT_KEY
SALES_ENQUIRY_ITEM_SORT_KEY_UNIT_PRICE: SALES_ENQUIRY_ITEM_SORT_KEY
SALES_ENQUIRY_ITEM_SORT_KEY_DISCOUNT: SALES_ENQUIRY_ITEM_SORT_KEY
SALES_ENQUIRY_ITEM_SORT_KEY_DELIVERY_DATE: SALES_ENQUIRY_ITEM_SORT_KEY
SALES_ENQUIRY_ITEM_STATUS_ANY_UNSPECIFIED: SALES_ENQUIRY_ITEM_STATUS
SALES_ENQUIRY_ITEM_STATUS_APPROVED: SALES_ENQUIRY_ITEM_STATUS
SALES_ENQUIRY_ITEM_STATUS_UNAPPROVED: SALES_ENQUIRY_ITEM_STATUS
SALES_ENQUIRY_SORT_KEY_ID_UNSPECIFIED: SALES_ENQUIRY_SORT_KEY
SALES_ENQUIRY_SORT_KEY_CREATED_AT: SALES_ENQUIRY_SORT_KEY
SALES_ENQUIRY_SORT_KEY_MODIFIED_AT: SALES_ENQUIRY_SORT_KEY
SALES_ENQUIRY_SORT_KEY_APPROVED_ON: SALES_ENQUIRY_SORT_KEY
SALES_ENQUIRY_SORT_KEY_APPROVED_BY: SALES_ENQUIRY_SORT_KEY
SALES_ENQUIRY_SORT_KEY_APPROVER_ROLE_ID: SALES_ENQUIRY_SORT_KEY
SALES_ENQUIRY_SORT_KEY_COMPLETED_ON: SALES_ENQUIRY_SORT_KEY
SALES_ENQUIRY_SORT_KEY_REFERENCE_ID: SALES_ENQUIRY_SORT_KEY
SALES_ENQUIRY_SORT_KEY_FINAL_REF_NUMBER: SALES_ENQUIRY_SORT_KEY
SALES_ENQUIRY_SORT_KEY_CONSIGNEE_CLIENT_ID: SALES_ENQUIRY_SORT_KEY
SALES_ENQUIRY_SORT_KEY_BUYER_CLIENT_ID: SALES_ENQUIRY_SORT_KEY
SALES_ENQUIRY_SORT_KEY_PRIORITY: SALES_ENQUIRY_SORT_KEY
SALES_ENQUIRY_SORT_KEY_AMENDMENT_COUNT: SALES_ENQUIRY_SORT_KEY

class SalesEnquiriesServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "consignee_client_id", "buyer_client_id", "priority", "currency_id", "description", "miscellaneous_cost", "overall_discount", "round_off", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MISCELLANEOUS_COST_FIELD_NUMBER: _ClassVar[int]
    OVERALL_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    consignee_client_id: int
    buyer_client_id: int
    priority: str
    currency_id: int
    description: str
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., priority: _Optional[str] = ..., currency_id: _Optional[int] = ..., description: _Optional[str] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class SalesEnquiriesServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "consignee_client_id", "buyer_client_id", "priority", "currency_id", "description", "miscellaneous_cost", "overall_discount", "round_off", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MISCELLANEOUS_COST_FIELD_NUMBER: _ClassVar[int]
    OVERALL_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    consignee_client_id: int
    buyer_client_id: int
    priority: str
    currency_id: int
    description: str
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., priority: _Optional[str] = ..., currency_id: _Optional[int] = ..., description: _Optional[str] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class SalesEnquiryAncillaryParameters(_message.Message):
    __slots__ = ("consignee_client_uuid", "buyer_client_uuid", "currency_uuid")
    CONSIGNEE_CLIENT_UUID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_UUID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_UUID_FIELD_NUMBER: _ClassVar[int]
    consignee_client_uuid: str
    buyer_client_uuid: str
    currency_uuid: str
    def __init__(self, consignee_client_uuid: _Optional[str] = ..., buyer_client_uuid: _Optional[str] = ..., currency_uuid: _Optional[str] = ...) -> None: ...

class SalesEnquiry(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "consignee_client_id", "buyer_client_id", "priority", "currency_id", "description", "miscellaneous_cost", "overall_discount", "round_off", "amendment_count", "list", "form_data", "total_price")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MISCELLANEOUS_COST_FIELD_NUMBER: _ClassVar[int]
    OVERALL_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_COUNT_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PRICE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    completed_on: int
    vault_folder_id: int
    reference_id: str
    final_ref_number: str
    consignee_client_id: int
    buyer_client_id: int
    priority: str
    currency_id: int
    description: str
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    amendment_count: int
    list: _containers.RepeatedCompositeFieldContainer[SalesEnquiryItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatum]
    total_price: float
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., priority: _Optional[str] = ..., currency_id: _Optional[int] = ..., description: _Optional[str] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., amendment_count: _Optional[int] = ..., list: _Optional[_Iterable[_Union[SalesEnquiryItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatum, _Mapping]]] = ..., total_price: _Optional[float] = ...) -> None: ...

class SalesEnquiriesServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "sales_enquiry_id", "name", "internal_quantity", "uom_id", "unit_price", "discount", "tax_group_id", "round_off", "delivery_date", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_ENQUIRY_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    sales_enquiry_id: int
    name: str
    internal_quantity: int
    uom_id: int
    unit_price: int
    discount: int
    tax_group_id: int
    round_off: int
    delivery_date: str
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., sales_enquiry_id: _Optional[int] = ..., name: _Optional[str] = ..., internal_quantity: _Optional[int] = ..., uom_id: _Optional[int] = ..., unit_price: _Optional[int] = ..., discount: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., round_off: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ...) -> None: ...

class SalesEnquiriesServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "name", "internal_quantity", "uom_id", "unit_price", "discount", "tax_group_id", "round_off", "delivery_date", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    name: str
    internal_quantity: int
    uom_id: int
    unit_price: int
    discount: int
    tax_group_id: int
    round_off: int
    delivery_date: str
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., name: _Optional[str] = ..., internal_quantity: _Optional[int] = ..., uom_id: _Optional[int] = ..., unit_price: _Optional[int] = ..., discount: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., round_off: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ...) -> None: ...

class SalesEnquiryItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "sales_enquiry_id", "name", "internal_quantity", "uom_id", "unit_price", "discount", "tax_group_id", "round_off", "delivery_date", "specifications", "discounted_unit_price")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_ENQUIRY_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    DISCOUNTED_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    sales_enquiry_id: int
    name: str
    internal_quantity: int
    uom_id: int
    unit_price: int
    discount: int
    tax_group_id: int
    round_off: int
    delivery_date: str
    specifications: str
    discounted_unit_price: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., sales_enquiry_id: _Optional[int] = ..., name: _Optional[str] = ..., internal_quantity: _Optional[int] = ..., uom_id: _Optional[int] = ..., unit_price: _Optional[int] = ..., discount: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., round_off: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ..., discounted_unit_price: _Optional[int] = ...) -> None: ...

class SalesEnquiriesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalesEnquiry]
    def __init__(self, list: _Optional[_Iterable[_Union[SalesEnquiry, _Mapping]]] = ...) -> None: ...

class SalesEnquiriesItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalesEnquiryItem]
    def __init__(self, list: _Optional[_Iterable[_Union[SalesEnquiryItem, _Mapping]]] = ...) -> None: ...

class SalesEnquiryItemHistoryRequest(_message.Message):
    __slots__ = ("sales_enquiry_id", "name")
    SALES_ENQUIRY_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    sales_enquiry_id: int
    name: str
    def __init__(self, sales_enquiry_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class SalesEnquiryItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "sales_enquiry_id", "uom_id", "tax_group_id", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "search_key")
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
    SALES_ENQUIRY_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: SALES_ENQUIRY_ITEM_SORT_KEY
    entity_uuid: str
    status: SALES_ENQUIRY_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    sales_enquiry_id: int
    uom_id: int
    tax_group_id: int
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALES_ENQUIRY_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[SALES_ENQUIRY_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., sales_enquiry_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., search_key: _Optional[str] = ...) -> None: ...

class SalesEnquiriesServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[SalesEnquiryItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[SalesEnquiryItem, _Mapping]]] = ...) -> None: ...

class SalesEnquiriesServicePaginationReq(_message.Message):
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
    sort_key: SALES_ENQUIRY_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALES_ENQUIRY_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class SalesEnquiriesServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[SalesEnquiry]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[SalesEnquiry, _Mapping]]] = ...) -> None: ...

class SalesEnquiriesServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "consignee_client_id", "buyer_client_id", "priority", "currency_id", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "form_data")
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
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: SALES_ENQUIRY_SORT_KEY
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
    consignee_client_id: int
    buyer_client_id: int
    priority: str
    currency_id: int
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALES_ENQUIRY_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., priority: _Optional[str] = ..., currency_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class SalesEnquiriesServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "consignee_client_id", "buyer_client_id", "priority", "currency_id", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "form_data")
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
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    PRIORITY_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
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
    consignee_client_id: int
    buyer_client_id: int
    priority: str
    currency_id: int
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., priority: _Optional[str] = ..., currency_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class SalesEnquiriesServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "consignee_client_id", "buyer_client_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: SALES_ENQUIRY_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    consignee_client_id: int
    buyer_client_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALES_ENQUIRY_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ...) -> None: ...

class SalesEnquiriesServiceContactCreateRequest(_message.Message):
    __slots__ = ("user_comment", "sales_enquiry_id", "associate_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_ENQUIRY_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    sales_enquiry_id: int
    associate_id: int
    def __init__(self, user_comment: _Optional[str] = ..., sales_enquiry_id: _Optional[int] = ..., associate_id: _Optional[int] = ...) -> None: ...

class SalesEnquiryContact(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "sales_enquiry_id", "associate_id", "associate_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_ENQUIRY_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    sales_enquiry_id: int
    associate_id: int
    associate_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., sales_enquiry_id: _Optional[int] = ..., associate_id: _Optional[int] = ..., associate_uuid: _Optional[str] = ...) -> None: ...

class SalesEnquiryContactsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalesEnquiryContact]
    def __init__(self, list: _Optional[_Iterable[_Union[SalesEnquiryContact, _Mapping]]] = ...) -> None: ...
