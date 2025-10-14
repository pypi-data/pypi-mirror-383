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

class VENDOR_INVOICE_REF_FROM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_INVOICE_REF_FROM_ANY_UNSPECIFIED: _ClassVar[VENDOR_INVOICE_REF_FROM]
    VENDOR_INVOICE_REF_FROM_PURCHASE_ORDER: _ClassVar[VENDOR_INVOICE_REF_FROM]

class VENDOR_INVOICE_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_INVOICE_SORT_KEY_ID_UNSPECIFIED: _ClassVar[VENDOR_INVOICE_SORT_KEY]
    VENDOR_INVOICE_SORT_KEY_CREATED_AT: _ClassVar[VENDOR_INVOICE_SORT_KEY]
    VENDOR_INVOICE_SORT_KEY_MODIFIED_AT: _ClassVar[VENDOR_INVOICE_SORT_KEY]
    VENDOR_INVOICE_SORT_KEY_APPROVED_ON: _ClassVar[VENDOR_INVOICE_SORT_KEY]
    VENDOR_INVOICE_SORT_KEY_APPROVED_BY: _ClassVar[VENDOR_INVOICE_SORT_KEY]
    VENDOR_INVOICE_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[VENDOR_INVOICE_SORT_KEY]
    VENDOR_INVOICE_SORT_KEY_COMPLETED_ON: _ClassVar[VENDOR_INVOICE_SORT_KEY]
    VENDOR_INVOICE_SORT_KEY_REFERENCE_ID: _ClassVar[VENDOR_INVOICE_SORT_KEY]
    VENDOR_INVOICE_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[VENDOR_INVOICE_SORT_KEY]
    VENDOR_INVOICE_SORT_KEY_TOTAL_VALUE: _ClassVar[VENDOR_INVOICE_SORT_KEY]

class VENDOR_INVOICE_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_INVOICE_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[VENDOR_INVOICE_ITEM_SORT_KEY]
    VENDOR_INVOICE_ITEM_SORT_KEY_CREATED_AT: _ClassVar[VENDOR_INVOICE_ITEM_SORT_KEY]
    VENDOR_INVOICE_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[VENDOR_INVOICE_ITEM_SORT_KEY]
    VENDOR_INVOICE_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[VENDOR_INVOICE_ITEM_SORT_KEY]
    VENDOR_INVOICE_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[VENDOR_INVOICE_ITEM_SORT_KEY]
    VENDOR_INVOICE_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[VENDOR_INVOICE_ITEM_SORT_KEY]
    VENDOR_INVOICE_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[VENDOR_INVOICE_ITEM_SORT_KEY]
    VENDOR_INVOICE_ITEM_SORT_KEY_INTERNAL_QUANTITY: _ClassVar[VENDOR_INVOICE_ITEM_SORT_KEY]
    VENDOR_INVOICE_ITEM_SORT_KEY_VENDOR_UOM_ID: _ClassVar[VENDOR_INVOICE_ITEM_SORT_KEY]
    VENDOR_INVOICE_ITEM_SORT_KEY_VENDOR_QUANTITY: _ClassVar[VENDOR_INVOICE_ITEM_SORT_KEY]
    VENDOR_INVOICE_ITEM_SORT_KEY_VENDOR_UNIT_PRICE: _ClassVar[VENDOR_INVOICE_ITEM_SORT_KEY]
    VENDOR_INVOICE_ITEM_SORT_KEY_TAX_GROUP_ID: _ClassVar[VENDOR_INVOICE_ITEM_SORT_KEY]

class VENDOR_INVOICE_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_INVOICE_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[VENDOR_INVOICE_ITEM_STATUS]
    VENDOR_INVOICE_ITEM_STATUS_APPROVED: _ClassVar[VENDOR_INVOICE_ITEM_STATUS]
    VENDOR_INVOICE_ITEM_STATUS_UNAPPROVED: _ClassVar[VENDOR_INVOICE_ITEM_STATUS]
VENDOR_INVOICE_REF_FROM_ANY_UNSPECIFIED: VENDOR_INVOICE_REF_FROM
VENDOR_INVOICE_REF_FROM_PURCHASE_ORDER: VENDOR_INVOICE_REF_FROM
VENDOR_INVOICE_SORT_KEY_ID_UNSPECIFIED: VENDOR_INVOICE_SORT_KEY
VENDOR_INVOICE_SORT_KEY_CREATED_AT: VENDOR_INVOICE_SORT_KEY
VENDOR_INVOICE_SORT_KEY_MODIFIED_AT: VENDOR_INVOICE_SORT_KEY
VENDOR_INVOICE_SORT_KEY_APPROVED_ON: VENDOR_INVOICE_SORT_KEY
VENDOR_INVOICE_SORT_KEY_APPROVED_BY: VENDOR_INVOICE_SORT_KEY
VENDOR_INVOICE_SORT_KEY_APPROVER_ROLE_ID: VENDOR_INVOICE_SORT_KEY
VENDOR_INVOICE_SORT_KEY_COMPLETED_ON: VENDOR_INVOICE_SORT_KEY
VENDOR_INVOICE_SORT_KEY_REFERENCE_ID: VENDOR_INVOICE_SORT_KEY
VENDOR_INVOICE_SORT_KEY_FINAL_REF_NUMBER: VENDOR_INVOICE_SORT_KEY
VENDOR_INVOICE_SORT_KEY_TOTAL_VALUE: VENDOR_INVOICE_SORT_KEY
VENDOR_INVOICE_ITEM_SORT_KEY_ID_UNSPECIFIED: VENDOR_INVOICE_ITEM_SORT_KEY
VENDOR_INVOICE_ITEM_SORT_KEY_CREATED_AT: VENDOR_INVOICE_ITEM_SORT_KEY
VENDOR_INVOICE_ITEM_SORT_KEY_MODIFIED_AT: VENDOR_INVOICE_ITEM_SORT_KEY
VENDOR_INVOICE_ITEM_SORT_KEY_APPROVED_ON: VENDOR_INVOICE_ITEM_SORT_KEY
VENDOR_INVOICE_ITEM_SORT_KEY_APPROVED_BY: VENDOR_INVOICE_ITEM_SORT_KEY
VENDOR_INVOICE_ITEM_SORT_KEY_APPROVER_ROLE_ID: VENDOR_INVOICE_ITEM_SORT_KEY
VENDOR_INVOICE_ITEM_SORT_KEY_FAMILY_ID: VENDOR_INVOICE_ITEM_SORT_KEY
VENDOR_INVOICE_ITEM_SORT_KEY_INTERNAL_QUANTITY: VENDOR_INVOICE_ITEM_SORT_KEY
VENDOR_INVOICE_ITEM_SORT_KEY_VENDOR_UOM_ID: VENDOR_INVOICE_ITEM_SORT_KEY
VENDOR_INVOICE_ITEM_SORT_KEY_VENDOR_QUANTITY: VENDOR_INVOICE_ITEM_SORT_KEY
VENDOR_INVOICE_ITEM_SORT_KEY_VENDOR_UNIT_PRICE: VENDOR_INVOICE_ITEM_SORT_KEY
VENDOR_INVOICE_ITEM_SORT_KEY_TAX_GROUP_ID: VENDOR_INVOICE_ITEM_SORT_KEY
VENDOR_INVOICE_ITEM_STATUS_ANY_UNSPECIFIED: VENDOR_INVOICE_ITEM_STATUS
VENDOR_INVOICE_ITEM_STATUS_APPROVED: VENDOR_INVOICE_ITEM_STATUS
VENDOR_INVOICE_ITEM_STATUS_UNAPPROVED: VENDOR_INVOICE_ITEM_STATUS

class VendorInvoicesServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "ref_from", "ref_id", "currency_id", "vendor_bill_no", "vendor_bill_date", "miscellaneous_cost", "overall_discount", "round_off", "cumulative_excess_tax_group_id", "cumulative_excess_tax_amount", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_NO_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_DATE_FIELD_NUMBER: _ClassVar[int]
    MISCELLANEOUS_COST_FIELD_NUMBER: _ClassVar[int]
    OVERALL_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    CUMULATIVE_EXCESS_TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    CUMULATIVE_EXCESS_TAX_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    ref_from: VENDOR_INVOICE_REF_FROM
    ref_id: int
    currency_id: int
    vendor_bill_no: str
    vendor_bill_date: str
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    cumulative_excess_tax_group_id: int
    cumulative_excess_tax_amount: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., ref_from: _Optional[_Union[VENDOR_INVOICE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., vendor_bill_no: _Optional[str] = ..., vendor_bill_date: _Optional[str] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., cumulative_excess_tax_group_id: _Optional[int] = ..., cumulative_excess_tax_amount: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class VendorInvoicesServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "currency_id", "vendor_bill_no", "vendor_bill_date", "miscellaneous_cost", "overall_discount", "round_off", "cumulative_excess_tax_group_id", "cumulative_excess_tax_amount", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_NO_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_DATE_FIELD_NUMBER: _ClassVar[int]
    MISCELLANEOUS_COST_FIELD_NUMBER: _ClassVar[int]
    OVERALL_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    CUMULATIVE_EXCESS_TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    CUMULATIVE_EXCESS_TAX_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    currency_id: int
    vendor_bill_no: str
    vendor_bill_date: str
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    cumulative_excess_tax_group_id: int
    cumulative_excess_tax_amount: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., currency_id: _Optional[int] = ..., vendor_bill_no: _Optional[str] = ..., vendor_bill_date: _Optional[str] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., cumulative_excess_tax_group_id: _Optional[int] = ..., cumulative_excess_tax_amount: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class VendorInvoicesServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid", "include_services")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_SERVICES_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    include_services: bool
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ..., include_services: _Optional[bool] = ...) -> None: ...

class VendorInvoiceAncillaryParameters(_message.Message):
    __slots__ = ("ref_uuid", "currency_uuid")
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_UUID_FIELD_NUMBER: _ClassVar[int]
    ref_uuid: str
    currency_uuid: str
    def __init__(self, ref_uuid: _Optional[str] = ..., currency_uuid: _Optional[str] = ...) -> None: ...

class VendorInvoice(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "ref_from", "ref_id", "currency_id", "vendor_bill_no", "vendor_bill_date", "miscellaneous_cost", "overall_discount", "round_off", "cumulative_excess_tax_group_id", "cumulative_excess_tax_amount", "total_value", "list", "form_data")
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
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_NO_FIELD_NUMBER: _ClassVar[int]
    VENDOR_BILL_DATE_FIELD_NUMBER: _ClassVar[int]
    MISCELLANEOUS_COST_FIELD_NUMBER: _ClassVar[int]
    OVERALL_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    CUMULATIVE_EXCESS_TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    CUMULATIVE_EXCESS_TAX_AMOUNT_FIELD_NUMBER: _ClassVar[int]
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
    ref_from: VENDOR_INVOICE_REF_FROM
    ref_id: int
    currency_id: int
    vendor_bill_no: str
    vendor_bill_date: str
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    cumulative_excess_tax_group_id: int
    cumulative_excess_tax_amount: int
    total_value: float
    list: _containers.RepeatedCompositeFieldContainer[VendorInvoiceItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[VENDOR_INVOICE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., vendor_bill_no: _Optional[str] = ..., vendor_bill_date: _Optional[str] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., cumulative_excess_tax_group_id: _Optional[int] = ..., cumulative_excess_tax_amount: _Optional[int] = ..., total_value: _Optional[float] = ..., list: _Optional[_Iterable[_Union[VendorInvoiceItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class VendorInvoicesServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "vendor_invoice_id", "family_id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "vendor_unit_price", "tax_group_id", "round_off", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    vendor_invoice_id: int
    family_id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    vendor_unit_price: int
    tax_group_id: int
    round_off: int
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., vendor_invoice_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., vendor_unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., round_off: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class VendorInvoicesServiceMultipleItemsSingleton(_message.Message):
    __slots__ = ("family_id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "vendor_unit_price", "tax_group_id", "round_off", "specifications")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    vendor_unit_price: int
    tax_group_id: int
    round_off: int
    specifications: str
    def __init__(self, family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., vendor_unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., round_off: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class VendorInvoicesServiceMultipleItemsCreateRequest(_message.Message):
    __slots__ = ("user_comment", "vendor_invoice_id", "list")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    vendor_invoice_id: int
    list: _containers.RepeatedCompositeFieldContainer[VendorInvoicesServiceMultipleItemsSingleton]
    def __init__(self, user_comment: _Optional[str] = ..., vendor_invoice_id: _Optional[int] = ..., list: _Optional[_Iterable[_Union[VendorInvoicesServiceMultipleItemsSingleton, _Mapping]]] = ...) -> None: ...

class VendorInvoicesServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "vendor_unit_price", "tax_group_id", "round_off", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    vendor_unit_price: int
    tax_group_id: int
    round_off: int
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., vendor_unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., round_off: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class VendorInvoiceItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "vendor_invoice_id", "family_id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "vendor_unit_price", "tax_group_id", "round_off", "specifications", "vendor_invoice_uuid", "family_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    VENDOR_INVOICE_UUID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    vendor_invoice_id: int
    family_id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    vendor_unit_price: int
    tax_group_id: int
    round_off: int
    specifications: str
    vendor_invoice_uuid: str
    family_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., vendor_invoice_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., vendor_unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., round_off: _Optional[int] = ..., specifications: _Optional[str] = ..., vendor_invoice_uuid: _Optional[str] = ..., family_uuid: _Optional[str] = ...) -> None: ...

class VendorInvoicesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VendorInvoice]
    def __init__(self, list: _Optional[_Iterable[_Union[VendorInvoice, _Mapping]]] = ...) -> None: ...

class VendorInvoiceItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VendorInvoiceItem]
    def __init__(self, list: _Optional[_Iterable[_Union[VendorInvoiceItem, _Mapping]]] = ...) -> None: ...

class VendorInvoiceItemHistoryRequest(_message.Message):
    __slots__ = ("vendor_invoice_id", "family_id")
    VENDOR_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    vendor_invoice_id: int
    family_id: int
    def __init__(self, vendor_invoice_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class VendorInvoiceItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("vendor_invoice_id", "family_id")
    VENDOR_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    vendor_invoice_id: int
    family_id: int
    def __init__(self, vendor_invoice_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class VendorInvoicesServiceAlreadyAddedQuantityForSourceRequest(_message.Message):
    __slots__ = ("ref_from", "ref_id", "family_id")
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ref_from: VENDOR_INVOICE_REF_FROM
    ref_id: int
    family_id: int
    def __init__(self, ref_from: _Optional[_Union[VENDOR_INVOICE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class VendorInvoicesServicePaginationReq(_message.Message):
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
    sort_key: VENDOR_INVOICE_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VENDOR_INVOICE_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class VendorInvoicesServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[VendorInvoice]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[VendorInvoice, _Mapping]]] = ...) -> None: ...

class VendorInvoicesServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "vendor_bill_no", "vendor_bill_date_start", "vendor_bill_date_end", "vendor_bill_date_exact", "currency_id", "vendor_id", "project_id", "family_id", "total_value_min", "total_value_max", "form_data")
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
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_MIN_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_MAX_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: VENDOR_INVOICE_SORT_KEY
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
    ref_from: VENDOR_INVOICE_REF_FROM
    ref_id: int
    vendor_bill_no: str
    vendor_bill_date_start: str
    vendor_bill_date_end: str
    vendor_bill_date_exact: str
    currency_id: int
    vendor_id: int
    project_id: int
    family_id: int
    total_value_min: int
    total_value_max: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VENDOR_INVOICE_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[VENDOR_INVOICE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., vendor_bill_no: _Optional[str] = ..., vendor_bill_date_start: _Optional[str] = ..., vendor_bill_date_end: _Optional[str] = ..., vendor_bill_date_exact: _Optional[str] = ..., currency_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., project_id: _Optional[int] = ..., family_id: _Optional[int] = ..., total_value_min: _Optional[int] = ..., total_value_max: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class VendorInvoicesServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "vendor_bill_no", "vendor_bill_date_start", "vendor_bill_date_end", "vendor_bill_date_exact", "currency_id", "vendor_id", "project_id", "family_id", "total_value_min", "total_value_max", "form_data")
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
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
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
    ref_from: VENDOR_INVOICE_REF_FROM
    ref_id: int
    vendor_bill_no: str
    vendor_bill_date_start: str
    vendor_bill_date_end: str
    vendor_bill_date_exact: str
    currency_id: int
    vendor_id: int
    project_id: int
    family_id: int
    total_value_min: int
    total_value_max: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[VENDOR_INVOICE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., vendor_bill_no: _Optional[str] = ..., vendor_bill_date_start: _Optional[str] = ..., vendor_bill_date_end: _Optional[str] = ..., vendor_bill_date_exact: _Optional[str] = ..., currency_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., project_id: _Optional[int] = ..., family_id: _Optional[int] = ..., total_value_min: _Optional[int] = ..., total_value_max: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class VendorInvoicesServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "ref_from", "ref_id", "vendor_id")
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
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: VENDOR_INVOICE_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    ref_from: VENDOR_INVOICE_REF_FROM
    ref_id: int
    vendor_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VENDOR_INVOICE_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., ref_from: _Optional[_Union[VENDOR_INVOICE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., vendor_id: _Optional[int] = ...) -> None: ...

class VendorInvoicesServiceReferenceCreateRequest(_message.Message):
    __slots__ = ("user_comment", "vendor_invoice_id", "goods_receipt_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    GOODS_RECEIPT_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    vendor_invoice_id: int
    goods_receipt_id: int
    def __init__(self, user_comment: _Optional[str] = ..., vendor_invoice_id: _Optional[int] = ..., goods_receipt_id: _Optional[int] = ...) -> None: ...

class VendorInvoiceReference(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "vendor_invoice_id", "goods_receipt_id")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    GOODS_RECEIPT_ID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    vendor_invoice_id: int
    goods_receipt_id: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., vendor_invoice_id: _Optional[int] = ..., goods_receipt_id: _Optional[int] = ...) -> None: ...

class VendorInvoiceReferencesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VendorInvoiceReference]
    def __init__(self, list: _Optional[_Iterable[_Union[VendorInvoiceReference, _Mapping]]] = ...) -> None: ...

class VendorInvoiceItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "vendor_invoice_id", "family_id", "vendor_uom_id", "tax_group_id", "search_key", "vendor_id")
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
    VENDOR_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: VENDOR_INVOICE_ITEM_SORT_KEY
    entity_uuid: str
    status: VENDOR_INVOICE_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    vendor_invoice_id: int
    family_id: int
    vendor_uom_id: int
    tax_group_id: int
    search_key: str
    vendor_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VENDOR_INVOICE_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[VENDOR_INVOICE_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., vendor_invoice_id: _Optional[int] = ..., family_id: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., search_key: _Optional[str] = ..., vendor_id: _Optional[int] = ...) -> None: ...

class VendorInvoicesServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[VendorInvoiceItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[VendorInvoiceItem, _Mapping]]] = ...) -> None: ...

class VendorInvoiceReceiptStatistics(_message.Message):
    __slots__ = ("family_id", "invoiced_quantity", "receipt_quantity")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INVOICED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    RECEIPT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    invoiced_quantity: int
    receipt_quantity: int
    def __init__(self, family_id: _Optional[int] = ..., invoiced_quantity: _Optional[int] = ..., receipt_quantity: _Optional[int] = ...) -> None: ...

class VendorInvoiceReceiptStatisticsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VendorInvoiceReceiptStatistics]
    def __init__(self, list: _Optional[_Iterable[_Union[VendorInvoiceReceiptStatistics, _Mapping]]] = ...) -> None: ...
