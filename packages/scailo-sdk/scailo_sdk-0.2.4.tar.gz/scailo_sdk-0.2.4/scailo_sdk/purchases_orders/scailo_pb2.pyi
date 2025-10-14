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

class PURCHASE_ORDER_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PURCHASE_ORDER_SORT_KEY_ID_UNSPECIFIED: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_CREATED_AT: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_MODIFIED_AT: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_APPROVED_ON: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_APPROVED_BY: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_COMPLETED_ON: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_REFERENCE_ID: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_CONSIGNEE_LOCATION_ID: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_BUYER_LOCATION_ID: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_VENDOR_ID: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_CURRENCY_ID: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_PROJECT_ID: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_PAYMENT_ADVANCE: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_AMENDMENT_COUNT: _ClassVar[PURCHASE_ORDER_SORT_KEY]
    PURCHASE_ORDER_SORT_KEY_TOTAL_VALUE: _ClassVar[PURCHASE_ORDER_SORT_KEY]

class PURCHASE_ORDER_REFERENCE_CONTEXT(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PURCHASE_ORDER_REFERENCE_CONTEXT_ANY_UNSPECIFIED: _ClassVar[PURCHASE_ORDER_REFERENCE_CONTEXT]
    PURCHASE_ORDER_REFERENCE_CONTEXT_BUYING: _ClassVar[PURCHASE_ORDER_REFERENCE_CONTEXT]
    PURCHASE_ORDER_REFERENCE_CONTEXT_BILLING: _ClassVar[PURCHASE_ORDER_REFERENCE_CONTEXT]

class PURCHASE_ORDER_REFERENCE_REF_FROM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PURCHASE_ORDER_REFERENCE_REF_FROM_ANY_UNSPECIFIED: _ClassVar[PURCHASE_ORDER_REFERENCE_REF_FROM]
    PURCHASE_ORDER_REFERENCE_REF_FROM_PURCHASE_INDENT: _ClassVar[PURCHASE_ORDER_REFERENCE_REF_FROM]
    PURCHASE_ORDER_REFERENCE_REF_FROM_OUTWARD_JOB: _ClassVar[PURCHASE_ORDER_REFERENCE_REF_FROM]
    PURCHASE_ORDER_REFERENCE_REF_FROM_QUOTATION_RESPONSE: _ClassVar[PURCHASE_ORDER_REFERENCE_REF_FROM]
    PURCHASE_ORDER_REFERENCE_REF_FROM_SALES_ORDER: _ClassVar[PURCHASE_ORDER_REFERENCE_REF_FROM]
    PURCHASE_ORDER_REFERENCE_REF_FROM_WORK_ORDER: _ClassVar[PURCHASE_ORDER_REFERENCE_REF_FROM]
    PURCHASE_ORDER_REFERENCE_REF_FROM_PURCHASE_ORDER: _ClassVar[PURCHASE_ORDER_REFERENCE_REF_FROM]
    PURCHASE_ORDER_REFERENCE_REF_FROM_SALES_INVOICE: _ClassVar[PURCHASE_ORDER_REFERENCE_REF_FROM]

class PURCHASE_ORDER_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PURCHASE_ORDER_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]
    PURCHASE_ORDER_ITEM_SORT_KEY_CREATED_AT: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]
    PURCHASE_ORDER_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]
    PURCHASE_ORDER_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]
    PURCHASE_ORDER_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]
    PURCHASE_ORDER_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]
    PURCHASE_ORDER_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]
    PURCHASE_ORDER_ITEM_SORT_KEY_INTERNAL_QUANTITY: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]
    PURCHASE_ORDER_ITEM_SORT_KEY_VENDOR_UOM_ID: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]
    PURCHASE_ORDER_ITEM_SORT_KEY_VENDOR_QUANTITY: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]
    PURCHASE_ORDER_ITEM_SORT_KEY_VENDOR_UNIT_PRICE: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]
    PURCHASE_ORDER_ITEM_SORT_KEY_TAX_GROUP_ID: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]
    PURCHASE_ORDER_ITEM_SORT_KEY_DISCOUNT: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]
    PURCHASE_ORDER_ITEM_SORT_KEY_DELIVERY_DATE: _ClassVar[PURCHASE_ORDER_ITEM_SORT_KEY]

class PURCHASE_ORDER_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PURCHASE_ORDER_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[PURCHASE_ORDER_ITEM_STATUS]
    PURCHASE_ORDER_ITEM_STATUS_APPROVED: _ClassVar[PURCHASE_ORDER_ITEM_STATUS]
    PURCHASE_ORDER_ITEM_STATUS_UNAPPROVED: _ClassVar[PURCHASE_ORDER_ITEM_STATUS]
PURCHASE_ORDER_SORT_KEY_ID_UNSPECIFIED: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_CREATED_AT: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_MODIFIED_AT: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_APPROVED_ON: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_APPROVED_BY: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_APPROVER_ROLE_ID: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_COMPLETED_ON: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_REFERENCE_ID: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_FINAL_REF_NUMBER: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_CONSIGNEE_LOCATION_ID: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_BUYER_LOCATION_ID: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_VENDOR_ID: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_CURRENCY_ID: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_PROJECT_ID: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_PAYMENT_ADVANCE: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_AMENDMENT_COUNT: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_SORT_KEY_TOTAL_VALUE: PURCHASE_ORDER_SORT_KEY
PURCHASE_ORDER_REFERENCE_CONTEXT_ANY_UNSPECIFIED: PURCHASE_ORDER_REFERENCE_CONTEXT
PURCHASE_ORDER_REFERENCE_CONTEXT_BUYING: PURCHASE_ORDER_REFERENCE_CONTEXT
PURCHASE_ORDER_REFERENCE_CONTEXT_BILLING: PURCHASE_ORDER_REFERENCE_CONTEXT
PURCHASE_ORDER_REFERENCE_REF_FROM_ANY_UNSPECIFIED: PURCHASE_ORDER_REFERENCE_REF_FROM
PURCHASE_ORDER_REFERENCE_REF_FROM_PURCHASE_INDENT: PURCHASE_ORDER_REFERENCE_REF_FROM
PURCHASE_ORDER_REFERENCE_REF_FROM_OUTWARD_JOB: PURCHASE_ORDER_REFERENCE_REF_FROM
PURCHASE_ORDER_REFERENCE_REF_FROM_QUOTATION_RESPONSE: PURCHASE_ORDER_REFERENCE_REF_FROM
PURCHASE_ORDER_REFERENCE_REF_FROM_SALES_ORDER: PURCHASE_ORDER_REFERENCE_REF_FROM
PURCHASE_ORDER_REFERENCE_REF_FROM_WORK_ORDER: PURCHASE_ORDER_REFERENCE_REF_FROM
PURCHASE_ORDER_REFERENCE_REF_FROM_PURCHASE_ORDER: PURCHASE_ORDER_REFERENCE_REF_FROM
PURCHASE_ORDER_REFERENCE_REF_FROM_SALES_INVOICE: PURCHASE_ORDER_REFERENCE_REF_FROM
PURCHASE_ORDER_ITEM_SORT_KEY_ID_UNSPECIFIED: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_SORT_KEY_CREATED_AT: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_SORT_KEY_MODIFIED_AT: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_SORT_KEY_APPROVED_ON: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_SORT_KEY_APPROVED_BY: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_SORT_KEY_APPROVER_ROLE_ID: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_SORT_KEY_FAMILY_ID: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_SORT_KEY_INTERNAL_QUANTITY: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_SORT_KEY_VENDOR_UOM_ID: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_SORT_KEY_VENDOR_QUANTITY: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_SORT_KEY_VENDOR_UNIT_PRICE: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_SORT_KEY_TAX_GROUP_ID: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_SORT_KEY_DISCOUNT: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_SORT_KEY_DELIVERY_DATE: PURCHASE_ORDER_ITEM_SORT_KEY
PURCHASE_ORDER_ITEM_STATUS_ANY_UNSPECIFIED: PURCHASE_ORDER_ITEM_STATUS
PURCHASE_ORDER_ITEM_STATUS_APPROVED: PURCHASE_ORDER_ITEM_STATUS
PURCHASE_ORDER_ITEM_STATUS_UNAPPROVED: PURCHASE_ORDER_ITEM_STATUS

class PurchasesOrdersServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "consignee_location_id", "buyer_location_id", "vendor_id", "currency_id", "project_id", "miscellaneous_cost", "overall_discount", "round_off", "payment_advance", "payment_cycle_in_days", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    MISCELLANEOUS_COST_FIELD_NUMBER: _ClassVar[int]
    OVERALL_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_ADVANCE_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_CYCLE_IN_DAYS_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    consignee_location_id: int
    buyer_location_id: int
    vendor_id: int
    currency_id: int
    project_id: int
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    payment_advance: int
    payment_cycle_in_days: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., buyer_location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., payment_advance: _Optional[int] = ..., payment_cycle_in_days: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class PurchasesOrdersServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "consignee_location_id", "buyer_location_id", "currency_id", "project_id", "miscellaneous_cost", "overall_discount", "round_off", "payment_advance", "payment_cycle_in_days", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    MISCELLANEOUS_COST_FIELD_NUMBER: _ClassVar[int]
    OVERALL_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_ADVANCE_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_CYCLE_IN_DAYS_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    consignee_location_id: int
    buyer_location_id: int
    currency_id: int
    project_id: int
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    payment_advance: int
    payment_cycle_in_days: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., buyer_location_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., payment_advance: _Optional[int] = ..., payment_cycle_in_days: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class PurchasesOrdersServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid", "consolidate_referenced_items")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    CONSOLIDATE_REFERENCED_ITEMS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    consolidate_referenced_items: bool
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ..., consolidate_referenced_items: _Optional[bool] = ...) -> None: ...

class PurchaseOrderAncillaryParameters(_message.Message):
    __slots__ = ("consignee_location_uuid", "buyer_location_uuid", "vendor_uuid", "currency_uuid")
    CONSIGNEE_LOCATION_UUID_FIELD_NUMBER: _ClassVar[int]
    BUYER_LOCATION_UUID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UUID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_UUID_FIELD_NUMBER: _ClassVar[int]
    consignee_location_uuid: str
    buyer_location_uuid: str
    vendor_uuid: str
    currency_uuid: str
    def __init__(self, consignee_location_uuid: _Optional[str] = ..., buyer_location_uuid: _Optional[str] = ..., vendor_uuid: _Optional[str] = ..., currency_uuid: _Optional[str] = ...) -> None: ...

class PurchaseOrder(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "consignee_location_id", "buyer_location_id", "vendor_id", "currency_id", "project_id", "miscellaneous_cost", "overall_discount", "round_off", "payment_advance", "payment_cycle_in_days", "amendment_count", "total_value", "list", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    MISCELLANEOUS_COST_FIELD_NUMBER: _ClassVar[int]
    OVERALL_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_ADVANCE_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_CYCLE_IN_DAYS_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_FIELD_NUMBER: _ClassVar[int]
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
    consignee_location_id: int
    buyer_location_id: int
    vendor_id: int
    currency_id: int
    project_id: int
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    payment_advance: int
    payment_cycle_in_days: int
    amendment_count: int
    total_value: float
    list: _containers.RepeatedCompositeFieldContainer[PurchaseOrderItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., buyer_location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., payment_advance: _Optional[int] = ..., payment_cycle_in_days: _Optional[int] = ..., amendment_count: _Optional[int] = ..., total_value: _Optional[float] = ..., list: _Optional[_Iterable[_Union[PurchaseOrderItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class PurchasesOrdersServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "purchase_order_id", "family_id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "vendor_unit_price", "tax_group_id", "discount", "delivery_date", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    purchase_order_id: int
    family_id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    vendor_unit_price: int
    tax_group_id: int
    discount: int
    delivery_date: str
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., purchase_order_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., vendor_unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., discount: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ...) -> None: ...

class PurchasesOrdersServiceMultipleItemsSingleton(_message.Message):
    __slots__ = ("family_id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "vendor_unit_price", "tax_group_id", "discount", "delivery_date", "specifications")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    vendor_unit_price: int
    tax_group_id: int
    discount: int
    delivery_date: str
    specifications: str
    def __init__(self, family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., vendor_unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., discount: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ...) -> None: ...

class PurchasesOrdersServiceMultipleItemsCreateRequest(_message.Message):
    __slots__ = ("user_comment", "purchase_order_id", "list")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    purchase_order_id: int
    list: _containers.RepeatedCompositeFieldContainer[PurchasesOrdersServiceMultipleItemsSingleton]
    def __init__(self, user_comment: _Optional[str] = ..., purchase_order_id: _Optional[int] = ..., list: _Optional[_Iterable[_Union[PurchasesOrdersServiceMultipleItemsSingleton, _Mapping]]] = ...) -> None: ...

class PurchasesOrdersServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "vendor_unit_price", "tax_group_id", "discount", "delivery_date", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    vendor_unit_price: int
    tax_group_id: int
    discount: int
    delivery_date: str
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., vendor_unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., discount: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ...) -> None: ...

class PurchaseOrderItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "purchase_order_id", "family_id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "vendor_unit_price", "tax_group_id", "discount", "delivery_date", "specifications", "discounted_vendor_unit_price", "purchase_order_uuid", "family_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    DISCOUNTED_VENDOR_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_ORDER_UUID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    purchase_order_id: int
    family_id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    vendor_unit_price: int
    tax_group_id: int
    discount: int
    delivery_date: str
    specifications: str
    discounted_vendor_unit_price: int
    purchase_order_uuid: str
    family_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., purchase_order_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., vendor_unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., discount: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ..., discounted_vendor_unit_price: _Optional[int] = ..., purchase_order_uuid: _Optional[str] = ..., family_uuid: _Optional[str] = ...) -> None: ...

class PurchasesOrdersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[PurchaseOrder]
    def __init__(self, list: _Optional[_Iterable[_Union[PurchaseOrder, _Mapping]]] = ...) -> None: ...

class PurchaseOrderItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[PurchaseOrderItem]
    def __init__(self, list: _Optional[_Iterable[_Union[PurchaseOrderItem, _Mapping]]] = ...) -> None: ...

class PurchaseOrderItemHistoryRequest(_message.Message):
    __slots__ = ("purchase_order_id", "family_id")
    PURCHASE_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    purchase_order_id: int
    family_id: int
    def __init__(self, purchase_order_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class PurchaseOrderItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("purchase_order_id", "family_id", "vendor_uom_id")
    PURCHASE_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    purchase_order_id: int
    family_id: int
    vendor_uom_id: int
    def __init__(self, purchase_order_id: _Optional[int] = ..., family_id: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ...) -> None: ...

class PurchasesOrdersServicePaginationReq(_message.Message):
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
    sort_key: PURCHASE_ORDER_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[PURCHASE_ORDER_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class PurchasesOrdersServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[PurchaseOrder]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[PurchaseOrder, _Mapping]]] = ...) -> None: ...

class PurchasesOrdersServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "consignee_location_id", "buyer_location_id", "vendor_id", "currency_id", "project_id", "family_id", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "total_value_min", "total_value_max", "form_data")
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
    CONSIGNEE_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_MIN_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_MAX_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: PURCHASE_ORDER_SORT_KEY
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
    consignee_location_id: int
    buyer_location_id: int
    vendor_id: int
    currency_id: int
    project_id: int
    family_id: int
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    total_value_min: int
    total_value_max: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[PURCHASE_ORDER_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., buyer_location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ..., family_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., total_value_min: _Optional[int] = ..., total_value_max: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class PurchasesOrdersServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "consignee_location_id", "buyer_location_id", "vendor_id", "currency_id", "project_id", "family_id", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "total_value_min", "total_value_max", "form_data")
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
    CONSIGNEE_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_MIN_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_MAX_FIELD_NUMBER: _ClassVar[int]
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
    consignee_location_id: int
    buyer_location_id: int
    vendor_id: int
    currency_id: int
    project_id: int
    family_id: int
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    total_value_min: int
    total_value_max: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., buyer_location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ..., family_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., total_value_min: _Optional[int] = ..., total_value_max: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class PurchasesOrdersServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "consignee_location_id", "buyer_location_id", "vendor_id", "currency_id", "project_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: PURCHASE_ORDER_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    consignee_location_id: int
    buyer_location_id: int
    vendor_id: int
    currency_id: int
    project_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[PURCHASE_ORDER_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., buyer_location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ...) -> None: ...

class PurchasesOrdersServiceReferenceCreateRequest(_message.Message):
    __slots__ = ("user_comment", "purchase_order_id", "context", "ref_from", "ref_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    purchase_order_id: int
    context: PURCHASE_ORDER_REFERENCE_CONTEXT
    ref_from: PURCHASE_ORDER_REFERENCE_REF_FROM
    ref_id: int
    def __init__(self, user_comment: _Optional[str] = ..., purchase_order_id: _Optional[int] = ..., context: _Optional[_Union[PURCHASE_ORDER_REFERENCE_CONTEXT, str]] = ..., ref_from: _Optional[_Union[PURCHASE_ORDER_REFERENCE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ...) -> None: ...

class PurchaseOrderReference(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "purchase_order_id", "context", "ref_from", "ref_id")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    purchase_order_id: int
    context: PURCHASE_ORDER_REFERENCE_CONTEXT
    ref_from: PURCHASE_ORDER_REFERENCE_REF_FROM
    ref_id: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., purchase_order_id: _Optional[int] = ..., context: _Optional[_Union[PURCHASE_ORDER_REFERENCE_CONTEXT, str]] = ..., ref_from: _Optional[_Union[PURCHASE_ORDER_REFERENCE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ...) -> None: ...

class PurchaseOrderReferencesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[PurchaseOrderReference]
    def __init__(self, list: _Optional[_Iterable[_Union[PurchaseOrderReference, _Mapping]]] = ...) -> None: ...

class PurchaseOrderItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "purchase_order_id", "family_id", "vendor_uom_id", "tax_group_id", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "search_key", "vendor_id")
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
    PURCHASE_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: PURCHASE_ORDER_ITEM_SORT_KEY
    entity_uuid: str
    status: PURCHASE_ORDER_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    purchase_order_id: int
    family_id: int
    vendor_uom_id: int
    tax_group_id: int
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    search_key: str
    vendor_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[PURCHASE_ORDER_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[PURCHASE_ORDER_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., purchase_order_id: _Optional[int] = ..., family_id: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., search_key: _Optional[str] = ..., vendor_id: _Optional[int] = ...) -> None: ...

class PurchasesOrdersServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[PurchaseOrderItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[PurchaseOrderItem, _Mapping]]] = ...) -> None: ...

class PurchasesOrdersServiceContactCreateRequest(_message.Message):
    __slots__ = ("user_comment", "purchase_order_id", "associate_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    purchase_order_id: int
    associate_id: int
    def __init__(self, user_comment: _Optional[str] = ..., purchase_order_id: _Optional[int] = ..., associate_id: _Optional[int] = ...) -> None: ...

class PurchaseOrderContact(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "purchase_order_id", "associate_id", "associate_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    purchase_order_id: int
    associate_id: int
    associate_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., purchase_order_id: _Optional[int] = ..., associate_id: _Optional[int] = ..., associate_uuid: _Optional[str] = ...) -> None: ...

class PurchaseOrderContactsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[PurchaseOrderContact]
    def __init__(self, list: _Optional[_Iterable[_Union[PurchaseOrderContact, _Mapping]]] = ...) -> None: ...

class PurchaseOrderInventoryStatistics(_message.Message):
    __slots__ = ("ordered", "received", "returned")
    ORDERED_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_FIELD_NUMBER: _ClassVar[int]
    RETURNED_FIELD_NUMBER: _ClassVar[int]
    ordered: int
    received: int
    returned: int
    def __init__(self, ordered: _Optional[int] = ..., received: _Optional[int] = ..., returned: _Optional[int] = ...) -> None: ...

class PurchaseOrderBillingStatistics(_message.Message):
    __slots__ = ("ordered", "billed", "debited")
    ORDERED_FIELD_NUMBER: _ClassVar[int]
    BILLED_FIELD_NUMBER: _ClassVar[int]
    DEBITED_FIELD_NUMBER: _ClassVar[int]
    ordered: int
    billed: int
    debited: int
    def __init__(self, ordered: _Optional[int] = ..., billed: _Optional[int] = ..., debited: _Optional[int] = ...) -> None: ...

class PurchaseOrderInventoryMatch(_message.Message):
    __slots__ = ("family_id", "vendor_uom_id", "ordered_primary", "ordered_secondary", "received_primary", "received_secondary", "invoiced_primary", "invoiced_secondary", "returned_primary", "returned_secondary", "debited_primary", "debited_secondary")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    ORDERED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    ORDERED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    INVOICED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    INVOICED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    RETURNED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    RETURNED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    DEBITED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    DEBITED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    vendor_uom_id: int
    ordered_primary: int
    ordered_secondary: int
    received_primary: int
    received_secondary: int
    invoiced_primary: int
    invoiced_secondary: int
    returned_primary: int
    returned_secondary: int
    debited_primary: int
    debited_secondary: int
    def __init__(self, family_id: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., ordered_primary: _Optional[int] = ..., ordered_secondary: _Optional[int] = ..., received_primary: _Optional[int] = ..., received_secondary: _Optional[int] = ..., invoiced_primary: _Optional[int] = ..., invoiced_secondary: _Optional[int] = ..., returned_primary: _Optional[int] = ..., returned_secondary: _Optional[int] = ..., debited_primary: _Optional[int] = ..., debited_secondary: _Optional[int] = ...) -> None: ...

class PurchaseOrderInventoryMatchList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[PurchaseOrderInventoryMatch]
    def __init__(self, list: _Optional[_Iterable[_Union[PurchaseOrderInventoryMatch, _Mapping]]] = ...) -> None: ...

class PurchaseOrderPriceMatch(_message.Message):
    __slots__ = ("family_id", "vendor_uom_id", "ordered_primary", "ordered_secondary", "ordered_total_value", "invoiced_primary", "invoiced_secondary", "invoiced_total_value", "debited_primary", "debited_secondary", "debited_total_value")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    ORDERED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    ORDERED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    ORDERED_TOTAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    INVOICED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    INVOICED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    INVOICED_TOTAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    DEBITED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    DEBITED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    DEBITED_TOTAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    vendor_uom_id: int
    ordered_primary: int
    ordered_secondary: int
    ordered_total_value: int
    invoiced_primary: int
    invoiced_secondary: int
    invoiced_total_value: int
    debited_primary: int
    debited_secondary: int
    debited_total_value: int
    def __init__(self, family_id: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., ordered_primary: _Optional[int] = ..., ordered_secondary: _Optional[int] = ..., ordered_total_value: _Optional[int] = ..., invoiced_primary: _Optional[int] = ..., invoiced_secondary: _Optional[int] = ..., invoiced_total_value: _Optional[int] = ..., debited_primary: _Optional[int] = ..., debited_secondary: _Optional[int] = ..., debited_total_value: _Optional[int] = ...) -> None: ...

class PurchaseOrderPriceMatchList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[PurchaseOrderPriceMatch]
    def __init__(self, list: _Optional[_Iterable[_Union[PurchaseOrderPriceMatch, _Mapping]]] = ...) -> None: ...
