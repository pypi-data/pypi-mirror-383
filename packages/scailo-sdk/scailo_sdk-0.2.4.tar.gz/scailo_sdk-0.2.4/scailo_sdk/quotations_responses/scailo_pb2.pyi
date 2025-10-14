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

class QUOTATION_RESPONSE_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUOTATION_RESPONSE_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[QUOTATION_RESPONSE_ITEM_SORT_KEY]
    QUOTATION_RESPONSE_ITEM_SORT_KEY_CREATED_AT: _ClassVar[QUOTATION_RESPONSE_ITEM_SORT_KEY]
    QUOTATION_RESPONSE_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[QUOTATION_RESPONSE_ITEM_SORT_KEY]
    QUOTATION_RESPONSE_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[QUOTATION_RESPONSE_ITEM_SORT_KEY]
    QUOTATION_RESPONSE_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[QUOTATION_RESPONSE_ITEM_SORT_KEY]
    QUOTATION_RESPONSE_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[QUOTATION_RESPONSE_ITEM_SORT_KEY]
    QUOTATION_RESPONSE_ITEM_SORT_KEY_NAME: _ClassVar[QUOTATION_RESPONSE_ITEM_SORT_KEY]
    QUOTATION_RESPONSE_ITEM_SORT_KEY_INTERNAL_QUANTITY: _ClassVar[QUOTATION_RESPONSE_ITEM_SORT_KEY]
    QUOTATION_RESPONSE_ITEM_SORT_KEY_VENDOR_QUANTITY: _ClassVar[QUOTATION_RESPONSE_ITEM_SORT_KEY]
    QUOTATION_RESPONSE_ITEM_SORT_KEY_VENDOR_UNIT_PRICE: _ClassVar[QUOTATION_RESPONSE_ITEM_SORT_KEY]
    QUOTATION_RESPONSE_ITEM_SORT_KEY_DELIVERY_TIME: _ClassVar[QUOTATION_RESPONSE_ITEM_SORT_KEY]

class QUOTATION_RESPONSE_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUOTATION_RESPONSE_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[QUOTATION_RESPONSE_ITEM_STATUS]
    QUOTATION_RESPONSE_ITEM_STATUS_APPROVED: _ClassVar[QUOTATION_RESPONSE_ITEM_STATUS]
    QUOTATION_RESPONSE_ITEM_STATUS_UNAPPROVED: _ClassVar[QUOTATION_RESPONSE_ITEM_STATUS]

class QUOTATION_RESPONSE_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QUOTATION_RESPONSE_SORT_KEY_ID_UNSPECIFIED: _ClassVar[QUOTATION_RESPONSE_SORT_KEY]
    QUOTATION_RESPONSE_SORT_KEY_CREATED_AT: _ClassVar[QUOTATION_RESPONSE_SORT_KEY]
    QUOTATION_RESPONSE_SORT_KEY_MODIFIED_AT: _ClassVar[QUOTATION_RESPONSE_SORT_KEY]
    QUOTATION_RESPONSE_SORT_KEY_APPROVED_ON: _ClassVar[QUOTATION_RESPONSE_SORT_KEY]
    QUOTATION_RESPONSE_SORT_KEY_APPROVED_BY: _ClassVar[QUOTATION_RESPONSE_SORT_KEY]
    QUOTATION_RESPONSE_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[QUOTATION_RESPONSE_SORT_KEY]
    QUOTATION_RESPONSE_SORT_KEY_COMPLETED_ON: _ClassVar[QUOTATION_RESPONSE_SORT_KEY]
    QUOTATION_RESPONSE_SORT_KEY_REFERENCE_ID: _ClassVar[QUOTATION_RESPONSE_SORT_KEY]
    QUOTATION_RESPONSE_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[QUOTATION_RESPONSE_SORT_KEY]
QUOTATION_RESPONSE_ITEM_SORT_KEY_ID_UNSPECIFIED: QUOTATION_RESPONSE_ITEM_SORT_KEY
QUOTATION_RESPONSE_ITEM_SORT_KEY_CREATED_AT: QUOTATION_RESPONSE_ITEM_SORT_KEY
QUOTATION_RESPONSE_ITEM_SORT_KEY_MODIFIED_AT: QUOTATION_RESPONSE_ITEM_SORT_KEY
QUOTATION_RESPONSE_ITEM_SORT_KEY_APPROVED_ON: QUOTATION_RESPONSE_ITEM_SORT_KEY
QUOTATION_RESPONSE_ITEM_SORT_KEY_APPROVED_BY: QUOTATION_RESPONSE_ITEM_SORT_KEY
QUOTATION_RESPONSE_ITEM_SORT_KEY_APPROVER_ROLE_ID: QUOTATION_RESPONSE_ITEM_SORT_KEY
QUOTATION_RESPONSE_ITEM_SORT_KEY_NAME: QUOTATION_RESPONSE_ITEM_SORT_KEY
QUOTATION_RESPONSE_ITEM_SORT_KEY_INTERNAL_QUANTITY: QUOTATION_RESPONSE_ITEM_SORT_KEY
QUOTATION_RESPONSE_ITEM_SORT_KEY_VENDOR_QUANTITY: QUOTATION_RESPONSE_ITEM_SORT_KEY
QUOTATION_RESPONSE_ITEM_SORT_KEY_VENDOR_UNIT_PRICE: QUOTATION_RESPONSE_ITEM_SORT_KEY
QUOTATION_RESPONSE_ITEM_SORT_KEY_DELIVERY_TIME: QUOTATION_RESPONSE_ITEM_SORT_KEY
QUOTATION_RESPONSE_ITEM_STATUS_ANY_UNSPECIFIED: QUOTATION_RESPONSE_ITEM_STATUS
QUOTATION_RESPONSE_ITEM_STATUS_APPROVED: QUOTATION_RESPONSE_ITEM_STATUS
QUOTATION_RESPONSE_ITEM_STATUS_UNAPPROVED: QUOTATION_RESPONSE_ITEM_STATUS
QUOTATION_RESPONSE_SORT_KEY_ID_UNSPECIFIED: QUOTATION_RESPONSE_SORT_KEY
QUOTATION_RESPONSE_SORT_KEY_CREATED_AT: QUOTATION_RESPONSE_SORT_KEY
QUOTATION_RESPONSE_SORT_KEY_MODIFIED_AT: QUOTATION_RESPONSE_SORT_KEY
QUOTATION_RESPONSE_SORT_KEY_APPROVED_ON: QUOTATION_RESPONSE_SORT_KEY
QUOTATION_RESPONSE_SORT_KEY_APPROVED_BY: QUOTATION_RESPONSE_SORT_KEY
QUOTATION_RESPONSE_SORT_KEY_APPROVER_ROLE_ID: QUOTATION_RESPONSE_SORT_KEY
QUOTATION_RESPONSE_SORT_KEY_COMPLETED_ON: QUOTATION_RESPONSE_SORT_KEY
QUOTATION_RESPONSE_SORT_KEY_REFERENCE_ID: QUOTATION_RESPONSE_SORT_KEY
QUOTATION_RESPONSE_SORT_KEY_FINAL_REF_NUMBER: QUOTATION_RESPONSE_SORT_KEY

class QuotationsResponsesServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "quotation_request_id", "ref_from", "ref_id", "currency_id", "description", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    QUOTATION_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    quotation_request_id: int
    ref_from: str
    ref_id: int
    currency_id: int
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., quotation_request_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class QuotationsResponsesServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "currency_id", "description", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    currency_id: int
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., currency_id: _Optional[int] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class QuotationResponseAncillaryParameters(_message.Message):
    __slots__ = ("quotation_request_uuid", "currency_uuid")
    QUOTATION_REQUEST_UUID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_UUID_FIELD_NUMBER: _ClassVar[int]
    quotation_request_uuid: str
    currency_uuid: str
    def __init__(self, quotation_request_uuid: _Optional[str] = ..., currency_uuid: _Optional[str] = ...) -> None: ...

class QuotationResponse(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "quotation_request_id", "ref_from", "ref_id", "currency_id", "description", "list", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    QUOTATION_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
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
    quotation_request_id: int
    ref_from: str
    ref_id: int
    currency_id: int
    description: str
    list: _containers.RepeatedCompositeFieldContainer[QuotationResponseItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., quotation_request_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., description: _Optional[str] = ..., list: _Optional[_Iterable[_Union[QuotationResponseItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class QuotationsResponsesServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "vault_folder_id", "quotation_response_id", "quotation_request_item_id", "name", "hsn_sac_code", "uom_id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "vendor_unit_price", "tax_group_id", "delivery_time_in_days", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    QUOTATION_RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    QUOTATION_REQUEST_ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    HSN_SAC_CODE_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_TIME_IN_DAYS_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    vault_folder_id: int
    quotation_response_id: int
    quotation_request_item_id: int
    name: str
    hsn_sac_code: str
    uom_id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    vendor_unit_price: int
    tax_group_id: int
    delivery_time_in_days: int
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., quotation_response_id: _Optional[int] = ..., quotation_request_item_id: _Optional[int] = ..., name: _Optional[str] = ..., hsn_sac_code: _Optional[str] = ..., uom_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., vendor_unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., delivery_time_in_days: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class QuotationsResponsesServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "vault_folder_id", "name", "hsn_sac_code", "uom_id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "vendor_unit_price", "tax_group_id", "delivery_time_in_days", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    HSN_SAC_CODE_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_TIME_IN_DAYS_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    vault_folder_id: int
    name: str
    hsn_sac_code: str
    uom_id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    vendor_unit_price: int
    tax_group_id: int
    delivery_time_in_days: int
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., hsn_sac_code: _Optional[str] = ..., uom_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., vendor_unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., delivery_time_in_days: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class QuotationResponseItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "vault_folder_id", "quotation_response_id", "quotation_request_item_id", "name", "hsn_sac_code", "uom_id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "vendor_unit_price", "tax_group_id", "delivery_time_in_days", "specifications")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    QUOTATION_RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    QUOTATION_REQUEST_ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    HSN_SAC_CODE_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_TIME_IN_DAYS_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    vault_folder_id: int
    quotation_response_id: int
    quotation_request_item_id: int
    name: str
    hsn_sac_code: str
    uom_id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    vendor_unit_price: int
    tax_group_id: int
    delivery_time_in_days: int
    specifications: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., quotation_response_id: _Optional[int] = ..., quotation_request_item_id: _Optional[int] = ..., name: _Optional[str] = ..., hsn_sac_code: _Optional[str] = ..., uom_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., vendor_unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., delivery_time_in_days: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class QuotationsResponsesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[QuotationResponse]
    def __init__(self, list: _Optional[_Iterable[_Union[QuotationResponse, _Mapping]]] = ...) -> None: ...

class QuotationsResponsesItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[QuotationResponseItem]
    def __init__(self, list: _Optional[_Iterable[_Union[QuotationResponseItem, _Mapping]]] = ...) -> None: ...

class QuotationResponseItemHistoryRequest(_message.Message):
    __slots__ = ("quotation_response_id", "name")
    QUOTATION_RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    quotation_response_id: int
    name: str
    def __init__(self, quotation_response_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class QuotationResponseItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "quotation_response_id", "quotation_request_item_id", "uom_id", "vendor_uom_id", "tax_group_id", "search_key")
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
    QUOTATION_RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    QUOTATION_REQUEST_ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: QUOTATION_RESPONSE_ITEM_SORT_KEY
    entity_uuid: str
    status: QUOTATION_RESPONSE_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    quotation_response_id: int
    quotation_request_item_id: int
    uom_id: int
    vendor_uom_id: int
    tax_group_id: int
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[QUOTATION_RESPONSE_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[QUOTATION_RESPONSE_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., quotation_response_id: _Optional[int] = ..., quotation_request_item_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., search_key: _Optional[str] = ...) -> None: ...

class QuotationsResponsesServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[QuotationResponseItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[QuotationResponseItem, _Mapping]]] = ...) -> None: ...

class QuotationsResponsesServicePaginationReq(_message.Message):
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
    sort_key: QUOTATION_RESPONSE_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[QUOTATION_RESPONSE_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class QuotationsResponsesServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[QuotationResponse]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[QuotationResponse, _Mapping]]] = ...) -> None: ...

class QuotationsResponsesServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "quotation_request_id", "currency_id", "vendor_id", "form_data")
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
    QUOTATION_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: QUOTATION_RESPONSE_SORT_KEY
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
    quotation_request_id: int
    currency_id: int
    vendor_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[QUOTATION_RESPONSE_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., quotation_request_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class QuotationsResponsesServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "quotation_request_id", "currency_id", "vendor_id", "form_data")
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
    QUOTATION_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
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
    quotation_request_id: int
    currency_id: int
    vendor_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., quotation_request_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class QuotationsResponsesServiceSearchAllReq(_message.Message):
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
    sort_key: QUOTATION_RESPONSE_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[QUOTATION_RESPONSE_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ...) -> None: ...

class QuotationsResponsesServiceItemsFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "quotation_response_id", "quotation_request_item_id", "name", "hsn_sac_code", "uom_id", "vendor_uom_id", "tax_group_id")
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
    APPROVED_ON_START_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_END_FIELD_NUMBER: _ClassVar[int]
    APPROVED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVER_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    QUOTATION_RESPONSE_ID_FIELD_NUMBER: _ClassVar[int]
    QUOTATION_REQUEST_ITEM_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    HSN_SAC_CODE_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: QUOTATION_RESPONSE_ITEM_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    quotation_response_id: int
    quotation_request_item_id: int
    name: str
    hsn_sac_code: str
    uom_id: int
    vendor_uom_id: int
    tax_group_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[QUOTATION_RESPONSE_ITEM_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., quotation_response_id: _Optional[int] = ..., quotation_request_item_id: _Optional[int] = ..., name: _Optional[str] = ..., hsn_sac_code: _Optional[str] = ..., uom_id: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ...) -> None: ...
