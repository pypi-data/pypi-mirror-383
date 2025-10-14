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

class GOODS_RECEIPT_REF_FROM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GOODS_RECEIPT_REF_FROM_ANY_UNSPECIFIED: _ClassVar[GOODS_RECEIPT_REF_FROM]
    GOODS_RECEIPT_REF_FROM_PURCHASE_ORDER: _ClassVar[GOODS_RECEIPT_REF_FROM]

class GOODS_RECEIPT_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GOODS_RECEIPT_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[GOODS_RECEIPT_ITEM_SORT_KEY]
    GOODS_RECEIPT_ITEM_SORT_KEY_CREATED_AT: _ClassVar[GOODS_RECEIPT_ITEM_SORT_KEY]
    GOODS_RECEIPT_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[GOODS_RECEIPT_ITEM_SORT_KEY]
    GOODS_RECEIPT_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[GOODS_RECEIPT_ITEM_SORT_KEY]
    GOODS_RECEIPT_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[GOODS_RECEIPT_ITEM_SORT_KEY]
    GOODS_RECEIPT_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[GOODS_RECEIPT_ITEM_SORT_KEY]
    GOODS_RECEIPT_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[GOODS_RECEIPT_ITEM_SORT_KEY]
    GOODS_RECEIPT_ITEM_SORT_KEY_INTERNAL_QUANTITY: _ClassVar[GOODS_RECEIPT_ITEM_SORT_KEY]
    GOODS_RECEIPT_ITEM_SORT_KEY_VENDOR_UOM_ID: _ClassVar[GOODS_RECEIPT_ITEM_SORT_KEY]
    GOODS_RECEIPT_ITEM_SORT_KEY_VENDOR_QUANTITY: _ClassVar[GOODS_RECEIPT_ITEM_SORT_KEY]

class GOODS_RECEIPT_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GOODS_RECEIPT_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[GOODS_RECEIPT_ITEM_STATUS]
    GOODS_RECEIPT_ITEM_STATUS_APPROVED: _ClassVar[GOODS_RECEIPT_ITEM_STATUS]
    GOODS_RECEIPT_ITEM_STATUS_UNAPPROVED: _ClassVar[GOODS_RECEIPT_ITEM_STATUS]

class GOODS_RECEIPT_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GOODS_RECEIPT_SORT_KEY_ID_UNSPECIFIED: _ClassVar[GOODS_RECEIPT_SORT_KEY]
    GOODS_RECEIPT_SORT_KEY_CREATED_AT: _ClassVar[GOODS_RECEIPT_SORT_KEY]
    GOODS_RECEIPT_SORT_KEY_MODIFIED_AT: _ClassVar[GOODS_RECEIPT_SORT_KEY]
    GOODS_RECEIPT_SORT_KEY_APPROVED_ON: _ClassVar[GOODS_RECEIPT_SORT_KEY]
    GOODS_RECEIPT_SORT_KEY_APPROVED_BY: _ClassVar[GOODS_RECEIPT_SORT_KEY]
    GOODS_RECEIPT_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[GOODS_RECEIPT_SORT_KEY]
    GOODS_RECEIPT_SORT_KEY_COMPLETED_ON: _ClassVar[GOODS_RECEIPT_SORT_KEY]
    GOODS_RECEIPT_SORT_KEY_REFERENCE_ID: _ClassVar[GOODS_RECEIPT_SORT_KEY]
    GOODS_RECEIPT_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[GOODS_RECEIPT_SORT_KEY]
    GOODS_RECEIPT_SORT_KEY_VENDOR_BILL_NO: _ClassVar[GOODS_RECEIPT_SORT_KEY]
    GOODS_RECEIPT_SORT_KEY_VENDOR_BILL_DATE: _ClassVar[GOODS_RECEIPT_SORT_KEY]

class GOODS_RECEIPT_BILLING_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GOODS_RECEIPT_BILLING_STATUS_ANY_UNSPECIFIED: _ClassVar[GOODS_RECEIPT_BILLING_STATUS]
    GOODS_RECEIPT_BILLING_STATUS_BILLED: _ClassVar[GOODS_RECEIPT_BILLING_STATUS]
    GOODS_RECEIPT_BILLING_STATUS_UNBILLED: _ClassVar[GOODS_RECEIPT_BILLING_STATUS]
GOODS_RECEIPT_REF_FROM_ANY_UNSPECIFIED: GOODS_RECEIPT_REF_FROM
GOODS_RECEIPT_REF_FROM_PURCHASE_ORDER: GOODS_RECEIPT_REF_FROM
GOODS_RECEIPT_ITEM_SORT_KEY_ID_UNSPECIFIED: GOODS_RECEIPT_ITEM_SORT_KEY
GOODS_RECEIPT_ITEM_SORT_KEY_CREATED_AT: GOODS_RECEIPT_ITEM_SORT_KEY
GOODS_RECEIPT_ITEM_SORT_KEY_MODIFIED_AT: GOODS_RECEIPT_ITEM_SORT_KEY
GOODS_RECEIPT_ITEM_SORT_KEY_APPROVED_ON: GOODS_RECEIPT_ITEM_SORT_KEY
GOODS_RECEIPT_ITEM_SORT_KEY_APPROVED_BY: GOODS_RECEIPT_ITEM_SORT_KEY
GOODS_RECEIPT_ITEM_SORT_KEY_APPROVER_ROLE_ID: GOODS_RECEIPT_ITEM_SORT_KEY
GOODS_RECEIPT_ITEM_SORT_KEY_FAMILY_ID: GOODS_RECEIPT_ITEM_SORT_KEY
GOODS_RECEIPT_ITEM_SORT_KEY_INTERNAL_QUANTITY: GOODS_RECEIPT_ITEM_SORT_KEY
GOODS_RECEIPT_ITEM_SORT_KEY_VENDOR_UOM_ID: GOODS_RECEIPT_ITEM_SORT_KEY
GOODS_RECEIPT_ITEM_SORT_KEY_VENDOR_QUANTITY: GOODS_RECEIPT_ITEM_SORT_KEY
GOODS_RECEIPT_ITEM_STATUS_ANY_UNSPECIFIED: GOODS_RECEIPT_ITEM_STATUS
GOODS_RECEIPT_ITEM_STATUS_APPROVED: GOODS_RECEIPT_ITEM_STATUS
GOODS_RECEIPT_ITEM_STATUS_UNAPPROVED: GOODS_RECEIPT_ITEM_STATUS
GOODS_RECEIPT_SORT_KEY_ID_UNSPECIFIED: GOODS_RECEIPT_SORT_KEY
GOODS_RECEIPT_SORT_KEY_CREATED_AT: GOODS_RECEIPT_SORT_KEY
GOODS_RECEIPT_SORT_KEY_MODIFIED_AT: GOODS_RECEIPT_SORT_KEY
GOODS_RECEIPT_SORT_KEY_APPROVED_ON: GOODS_RECEIPT_SORT_KEY
GOODS_RECEIPT_SORT_KEY_APPROVED_BY: GOODS_RECEIPT_SORT_KEY
GOODS_RECEIPT_SORT_KEY_APPROVER_ROLE_ID: GOODS_RECEIPT_SORT_KEY
GOODS_RECEIPT_SORT_KEY_COMPLETED_ON: GOODS_RECEIPT_SORT_KEY
GOODS_RECEIPT_SORT_KEY_REFERENCE_ID: GOODS_RECEIPT_SORT_KEY
GOODS_RECEIPT_SORT_KEY_FINAL_REF_NUMBER: GOODS_RECEIPT_SORT_KEY
GOODS_RECEIPT_SORT_KEY_VENDOR_BILL_NO: GOODS_RECEIPT_SORT_KEY
GOODS_RECEIPT_SORT_KEY_VENDOR_BILL_DATE: GOODS_RECEIPT_SORT_KEY
GOODS_RECEIPT_BILLING_STATUS_ANY_UNSPECIFIED: GOODS_RECEIPT_BILLING_STATUS
GOODS_RECEIPT_BILLING_STATUS_BILLED: GOODS_RECEIPT_BILLING_STATUS
GOODS_RECEIPT_BILLING_STATUS_UNBILLED: GOODS_RECEIPT_BILLING_STATUS

class GoodsReceiptsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "ref_from", "ref_id", "vendor_bill_no", "vendor_bill_date", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_NO_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_DATE_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    ref_from: GOODS_RECEIPT_REF_FROM
    ref_id: int
    vendor_bill_no: str
    vendor_bill_date: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., ref_from: _Optional[_Union[GOODS_RECEIPT_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., vendor_bill_no: _Optional[str] = ..., vendor_bill_date: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class GoodsReceiptsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "vendor_bill_no", "vendor_bill_date", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_NO_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_DATE_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    vendor_bill_no: str
    vendor_bill_date: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., vendor_bill_no: _Optional[str] = ..., vendor_bill_date: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class GoodsReceiptsServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ...) -> None: ...

class GoodsReceiptAncillaryParameters(_message.Message):
    __slots__ = ("ref_uuid",)
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    ref_uuid: str
    def __init__(self, ref_uuid: _Optional[str] = ...) -> None: ...

class GoodsReceipt(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "ref_from", "ref_id", "vendor_bill_no", "vendor_bill_date", "list", "form_data")
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
    VENDOR_BILL_NO_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_DATE_FIELD_NUMBER: _ClassVar[int]
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
    ref_from: GOODS_RECEIPT_REF_FROM
    ref_id: int
    vendor_bill_no: str
    vendor_bill_date: str
    list: _containers.RepeatedCompositeFieldContainer[GoodsReceiptItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[GOODS_RECEIPT_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., vendor_bill_no: _Optional[str] = ..., vendor_bill_date: _Optional[str] = ..., list: _Optional[_Iterable[_Union[GoodsReceiptItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class GoodsReceiptsServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "goods_receipt_id", "family_id", "internal_quantity", "vendor_uom_id", "vendor_quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    GOODS_RECEIPT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    goods_receipt_id: int
    family_id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., goods_receipt_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ...) -> None: ...

class GoodsReceiptsServiceMultipleItemsSingleton(_message.Message):
    __slots__ = ("family_id", "internal_quantity", "vendor_uom_id", "vendor_quantity")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    def __init__(self, family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ...) -> None: ...

class GoodsReceiptsServiceMultipleItemsCreateRequest(_message.Message):
    __slots__ = ("user_comment", "goods_receipt_id", "list")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    GOODS_RECEIPT_ID_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    goods_receipt_id: int
    list: _containers.RepeatedCompositeFieldContainer[GoodsReceiptsServiceMultipleItemsSingleton]
    def __init__(self, user_comment: _Optional[str] = ..., goods_receipt_id: _Optional[int] = ..., list: _Optional[_Iterable[_Union[GoodsReceiptsServiceMultipleItemsSingleton, _Mapping]]] = ...) -> None: ...

class GoodsReceiptsServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "internal_quantity", "vendor_uom_id", "vendor_quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ...) -> None: ...

class GoodsReceiptItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "goods_receipt_id", "family_id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "goods_receipt_uuid", "family_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    GOODS_RECEIPT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    GOODS_RECEIPT_UUID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    goods_receipt_id: int
    family_id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    goods_receipt_uuid: str
    family_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., goods_receipt_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., goods_receipt_uuid: _Optional[str] = ..., family_uuid: _Optional[str] = ...) -> None: ...

class GoodsReceiptsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[GoodsReceipt]
    def __init__(self, list: _Optional[_Iterable[_Union[GoodsReceipt, _Mapping]]] = ...) -> None: ...

class GoodsReceiptsItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[GoodsReceiptItem]
    def __init__(self, list: _Optional[_Iterable[_Union[GoodsReceiptItem, _Mapping]]] = ...) -> None: ...

class GoodsReceiptItemHistoryRequest(_message.Message):
    __slots__ = ("goods_receipt_id", "family_id")
    GOODS_RECEIPT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    goods_receipt_id: int
    family_id: int
    def __init__(self, goods_receipt_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class GoodsReceiptItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("goods_receipt_id", "family_id")
    GOODS_RECEIPT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    goods_receipt_id: int
    family_id: int
    def __init__(self, goods_receipt_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class GoodsReceiptItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "goods_receipt_id", "family_id", "vendor_uom_id", "search_key", "vendor_id")
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
    GOODS_RECEIPT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: GOODS_RECEIPT_ITEM_SORT_KEY
    entity_uuid: str
    status: GOODS_RECEIPT_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    goods_receipt_id: int
    family_id: int
    vendor_uom_id: int
    search_key: str
    vendor_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[GOODS_RECEIPT_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[GOODS_RECEIPT_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., goods_receipt_id: _Optional[int] = ..., family_id: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., search_key: _Optional[str] = ..., vendor_id: _Optional[int] = ...) -> None: ...

class GoodsReceiptsServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[GoodsReceiptItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[GoodsReceiptItem, _Mapping]]] = ...) -> None: ...

class GoodsReceiptsServiceAlreadyAddedQuantityForSourceRequest(_message.Message):
    __slots__ = ("ref_from", "ref_id", "family_id")
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ref_from: GOODS_RECEIPT_REF_FROM
    ref_id: int
    family_id: int
    def __init__(self, ref_from: _Optional[_Union[GOODS_RECEIPT_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class GoodsReceiptsServicePaginationReq(_message.Message):
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
    sort_key: GOODS_RECEIPT_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[GOODS_RECEIPT_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class GoodsReceiptsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[GoodsReceipt]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[GoodsReceipt, _Mapping]]] = ...) -> None: ...

class GoodsReceiptsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "vendor_bill_no", "vendor_bill_date_start", "vendor_bill_date_end", "vendor_bill_date_exact", "vendor_id", "project_id", "family_id", "billing_status", "form_data")
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
    VENDOR_BILL_NO_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_DATE_START_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_DATE_END_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_STATUS_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: GOODS_RECEIPT_SORT_KEY
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
    ref_from: GOODS_RECEIPT_REF_FROM
    ref_id: int
    vendor_bill_no: str
    vendor_bill_date_start: str
    vendor_bill_date_end: str
    vendor_bill_date_exact: str
    vendor_id: int
    project_id: int
    family_id: int
    billing_status: GOODS_RECEIPT_BILLING_STATUS
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[GOODS_RECEIPT_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[GOODS_RECEIPT_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., vendor_bill_no: _Optional[str] = ..., vendor_bill_date_start: _Optional[str] = ..., vendor_bill_date_end: _Optional[str] = ..., vendor_bill_date_exact: _Optional[str] = ..., vendor_id: _Optional[int] = ..., project_id: _Optional[int] = ..., family_id: _Optional[int] = ..., billing_status: _Optional[_Union[GOODS_RECEIPT_BILLING_STATUS, str]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class GoodsReceiptsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "vendor_bill_no", "vendor_bill_date_start", "vendor_bill_date_end", "vendor_bill_date_exact", "vendor_id", "project_id", "family_id", "billing_status", "form_data")
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
    VENDOR_BILL_NO_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_DATE_START_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_DATE_END_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    BILLING_STATUS_FIELD_NUMBER: _ClassVar[int]
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
    ref_from: GOODS_RECEIPT_REF_FROM
    ref_id: int
    vendor_bill_no: str
    vendor_bill_date_start: str
    vendor_bill_date_end: str
    vendor_bill_date_exact: str
    vendor_id: int
    project_id: int
    family_id: int
    billing_status: GOODS_RECEIPT_BILLING_STATUS
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[GOODS_RECEIPT_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., vendor_bill_no: _Optional[str] = ..., vendor_bill_date_start: _Optional[str] = ..., vendor_bill_date_end: _Optional[str] = ..., vendor_bill_date_exact: _Optional[str] = ..., vendor_id: _Optional[int] = ..., project_id: _Optional[int] = ..., family_id: _Optional[int] = ..., billing_status: _Optional[_Union[GOODS_RECEIPT_BILLING_STATUS, str]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class GoodsReceiptsServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "ref_from", "ref_id", "billing_status", "vendor_id")
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
    BILLING_STATUS_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: GOODS_RECEIPT_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    ref_from: GOODS_RECEIPT_REF_FROM
    ref_id: int
    billing_status: GOODS_RECEIPT_BILLING_STATUS
    vendor_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[GOODS_RECEIPT_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., ref_from: _Optional[_Union[GOODS_RECEIPT_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., billing_status: _Optional[_Union[GOODS_RECEIPT_BILLING_STATUS, str]] = ..., vendor_id: _Optional[int] = ...) -> None: ...
