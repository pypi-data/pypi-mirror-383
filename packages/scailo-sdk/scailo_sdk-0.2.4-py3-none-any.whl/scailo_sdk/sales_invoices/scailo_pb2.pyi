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

class SALES_INVOICE_REF_FROM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALES_INVOICE_REF_FROM_ANY_UNSPECIFIED: _ClassVar[SALES_INVOICE_REF_FROM]
    SALES_INVOICE_REF_FROM_SALES_ORDER: _ClassVar[SALES_INVOICE_REF_FROM]

class SALES_INVOICE_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALES_INVOICE_SORT_KEY_ID_UNSPECIFIED: _ClassVar[SALES_INVOICE_SORT_KEY]
    SALES_INVOICE_SORT_KEY_CREATED_AT: _ClassVar[SALES_INVOICE_SORT_KEY]
    SALES_INVOICE_SORT_KEY_MODIFIED_AT: _ClassVar[SALES_INVOICE_SORT_KEY]
    SALES_INVOICE_SORT_KEY_APPROVED_ON: _ClassVar[SALES_INVOICE_SORT_KEY]
    SALES_INVOICE_SORT_KEY_APPROVED_BY: _ClassVar[SALES_INVOICE_SORT_KEY]
    SALES_INVOICE_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[SALES_INVOICE_SORT_KEY]
    SALES_INVOICE_SORT_KEY_COMPLETED_ON: _ClassVar[SALES_INVOICE_SORT_KEY]
    SALES_INVOICE_SORT_KEY_REFERENCE_ID: _ClassVar[SALES_INVOICE_SORT_KEY]
    SALES_INVOICE_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[SALES_INVOICE_SORT_KEY]
    SALES_INVOICE_SORT_KEY_AMENDMENT_COUNT: _ClassVar[SALES_INVOICE_SORT_KEY]
    SALES_INVOICE_SORT_KEY_TOTAL_VALUE: _ClassVar[SALES_INVOICE_SORT_KEY]

class SALES_INVOICE_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALES_INVOICE_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[SALES_INVOICE_ITEM_SORT_KEY]
    SALES_INVOICE_ITEM_SORT_KEY_CREATED_AT: _ClassVar[SALES_INVOICE_ITEM_SORT_KEY]
    SALES_INVOICE_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[SALES_INVOICE_ITEM_SORT_KEY]
    SALES_INVOICE_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[SALES_INVOICE_ITEM_SORT_KEY]
    SALES_INVOICE_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[SALES_INVOICE_ITEM_SORT_KEY]
    SALES_INVOICE_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[SALES_INVOICE_ITEM_SORT_KEY]
    SALES_INVOICE_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[SALES_INVOICE_ITEM_SORT_KEY]
    SALES_INVOICE_ITEM_SORT_KEY_INTERNAL_QUANTITY: _ClassVar[SALES_INVOICE_ITEM_SORT_KEY]
    SALES_INVOICE_ITEM_SORT_KEY_CLIENT_UOM_ID: _ClassVar[SALES_INVOICE_ITEM_SORT_KEY]
    SALES_INVOICE_ITEM_SORT_KEY_CLIENT_QUANTITY: _ClassVar[SALES_INVOICE_ITEM_SORT_KEY]
    SALES_INVOICE_ITEM_SORT_KEY_CLIENT_FAMILY_CODE: _ClassVar[SALES_INVOICE_ITEM_SORT_KEY]
    SALES_INVOICE_ITEM_SORT_KEY_UNIT_PRICE: _ClassVar[SALES_INVOICE_ITEM_SORT_KEY]
    SALES_INVOICE_ITEM_SORT_KEY_TAX_GROUP_ID: _ClassVar[SALES_INVOICE_ITEM_SORT_KEY]

class SALES_INVOICE_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALES_INVOICE_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[SALES_INVOICE_ITEM_STATUS]
    SALES_INVOICE_ITEM_STATUS_APPROVED: _ClassVar[SALES_INVOICE_ITEM_STATUS]
    SALES_INVOICE_ITEM_STATUS_UNAPPROVED: _ClassVar[SALES_INVOICE_ITEM_STATUS]
SALES_INVOICE_REF_FROM_ANY_UNSPECIFIED: SALES_INVOICE_REF_FROM
SALES_INVOICE_REF_FROM_SALES_ORDER: SALES_INVOICE_REF_FROM
SALES_INVOICE_SORT_KEY_ID_UNSPECIFIED: SALES_INVOICE_SORT_KEY
SALES_INVOICE_SORT_KEY_CREATED_AT: SALES_INVOICE_SORT_KEY
SALES_INVOICE_SORT_KEY_MODIFIED_AT: SALES_INVOICE_SORT_KEY
SALES_INVOICE_SORT_KEY_APPROVED_ON: SALES_INVOICE_SORT_KEY
SALES_INVOICE_SORT_KEY_APPROVED_BY: SALES_INVOICE_SORT_KEY
SALES_INVOICE_SORT_KEY_APPROVER_ROLE_ID: SALES_INVOICE_SORT_KEY
SALES_INVOICE_SORT_KEY_COMPLETED_ON: SALES_INVOICE_SORT_KEY
SALES_INVOICE_SORT_KEY_REFERENCE_ID: SALES_INVOICE_SORT_KEY
SALES_INVOICE_SORT_KEY_FINAL_REF_NUMBER: SALES_INVOICE_SORT_KEY
SALES_INVOICE_SORT_KEY_AMENDMENT_COUNT: SALES_INVOICE_SORT_KEY
SALES_INVOICE_SORT_KEY_TOTAL_VALUE: SALES_INVOICE_SORT_KEY
SALES_INVOICE_ITEM_SORT_KEY_ID_UNSPECIFIED: SALES_INVOICE_ITEM_SORT_KEY
SALES_INVOICE_ITEM_SORT_KEY_CREATED_AT: SALES_INVOICE_ITEM_SORT_KEY
SALES_INVOICE_ITEM_SORT_KEY_MODIFIED_AT: SALES_INVOICE_ITEM_SORT_KEY
SALES_INVOICE_ITEM_SORT_KEY_APPROVED_ON: SALES_INVOICE_ITEM_SORT_KEY
SALES_INVOICE_ITEM_SORT_KEY_APPROVED_BY: SALES_INVOICE_ITEM_SORT_KEY
SALES_INVOICE_ITEM_SORT_KEY_APPROVER_ROLE_ID: SALES_INVOICE_ITEM_SORT_KEY
SALES_INVOICE_ITEM_SORT_KEY_FAMILY_ID: SALES_INVOICE_ITEM_SORT_KEY
SALES_INVOICE_ITEM_SORT_KEY_INTERNAL_QUANTITY: SALES_INVOICE_ITEM_SORT_KEY
SALES_INVOICE_ITEM_SORT_KEY_CLIENT_UOM_ID: SALES_INVOICE_ITEM_SORT_KEY
SALES_INVOICE_ITEM_SORT_KEY_CLIENT_QUANTITY: SALES_INVOICE_ITEM_SORT_KEY
SALES_INVOICE_ITEM_SORT_KEY_CLIENT_FAMILY_CODE: SALES_INVOICE_ITEM_SORT_KEY
SALES_INVOICE_ITEM_SORT_KEY_UNIT_PRICE: SALES_INVOICE_ITEM_SORT_KEY
SALES_INVOICE_ITEM_SORT_KEY_TAX_GROUP_ID: SALES_INVOICE_ITEM_SORT_KEY
SALES_INVOICE_ITEM_STATUS_ANY_UNSPECIFIED: SALES_INVOICE_ITEM_STATUS
SALES_INVOICE_ITEM_STATUS_APPROVED: SALES_INVOICE_ITEM_STATUS
SALES_INVOICE_ITEM_STATUS_UNAPPROVED: SALES_INVOICE_ITEM_STATUS

class SalesInvoicesServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "ref_from", "ref_id", "currency_id", "bank_account_id", "miscellaneous_cost", "overall_discount", "round_off", "cumulative_excess_tax_group_id", "cumulative_excess_tax_amount", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
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
    ref_from: SALES_INVOICE_REF_FROM
    ref_id: int
    currency_id: int
    bank_account_id: int
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    cumulative_excess_tax_group_id: int
    cumulative_excess_tax_amount: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., ref_from: _Optional[_Union[SALES_INVOICE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., bank_account_id: _Optional[int] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., cumulative_excess_tax_group_id: _Optional[int] = ..., cumulative_excess_tax_amount: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class SalesInvoicesServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "currency_id", "bank_account_id", "miscellaneous_cost", "overall_discount", "round_off", "cumulative_excess_tax_group_id", "cumulative_excess_tax_amount", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
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
    bank_account_id: int
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    cumulative_excess_tax_group_id: int
    cumulative_excess_tax_amount: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., currency_id: _Optional[int] = ..., bank_account_id: _Optional[int] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., cumulative_excess_tax_group_id: _Optional[int] = ..., cumulative_excess_tax_amount: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class SalesInvoicesServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid", "include_services")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_SERVICES_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    include_services: bool
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ..., include_services: _Optional[bool] = ...) -> None: ...

class SalesInvoiceAncillaryParameters(_message.Message):
    __slots__ = ("ref_uuid", "currency_uuid")
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_UUID_FIELD_NUMBER: _ClassVar[int]
    ref_uuid: str
    currency_uuid: str
    def __init__(self, ref_uuid: _Optional[str] = ..., currency_uuid: _Optional[str] = ...) -> None: ...

class SalesInvoice(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "ref_from", "ref_id", "currency_id", "bank_account_id", "miscellaneous_cost", "overall_discount", "round_off", "cumulative_excess_tax_group_id", "cumulative_excess_tax_amount", "total_value", "amendment_count", "list", "form_data")
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
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    MISCELLANEOUS_COST_FIELD_NUMBER: _ClassVar[int]
    OVERALL_DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    CUMULATIVE_EXCESS_TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    CUMULATIVE_EXCESS_TAX_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_FIELD_NUMBER: _ClassVar[int]
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
    ref_from: SALES_INVOICE_REF_FROM
    ref_id: int
    currency_id: int
    bank_account_id: int
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    cumulative_excess_tax_group_id: int
    cumulative_excess_tax_amount: int
    total_value: float
    amendment_count: int
    list: _containers.RepeatedCompositeFieldContainer[SalesInvoiceItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[SALES_INVOICE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., bank_account_id: _Optional[int] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., cumulative_excess_tax_group_id: _Optional[int] = ..., cumulative_excess_tax_amount: _Optional[int] = ..., total_value: _Optional[float] = ..., amendment_count: _Optional[int] = ..., list: _Optional[_Iterable[_Union[SalesInvoiceItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class SalesInvoicesServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "sales_invoice_id", "family_id", "internal_quantity", "client_uom_id", "client_quantity", "client_family_code", "unit_price", "tax_group_id", "round_off", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    sales_invoice_id: int
    family_id: int
    internal_quantity: int
    client_uom_id: int
    client_quantity: int
    client_family_code: str
    unit_price: int
    tax_group_id: int
    round_off: int
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., sales_invoice_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., client_uom_id: _Optional[int] = ..., client_quantity: _Optional[int] = ..., client_family_code: _Optional[str] = ..., unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., round_off: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class SalesInvoicesServiceMultipleItemsSingleton(_message.Message):
    __slots__ = ("family_id", "internal_quantity", "client_uom_id", "client_quantity", "client_family_code", "unit_price", "tax_group_id", "round_off", "specifications")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    internal_quantity: int
    client_uom_id: int
    client_quantity: int
    client_family_code: str
    unit_price: int
    tax_group_id: int
    round_off: int
    specifications: str
    def __init__(self, family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., client_uom_id: _Optional[int] = ..., client_quantity: _Optional[int] = ..., client_family_code: _Optional[str] = ..., unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., round_off: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class SalesInvoicesServiceMultipleItemsCreateRequest(_message.Message):
    __slots__ = ("user_comment", "sales_invoice_id", "list")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    sales_invoice_id: int
    list: _containers.RepeatedCompositeFieldContainer[SalesInvoicesServiceMultipleItemsSingleton]
    def __init__(self, user_comment: _Optional[str] = ..., sales_invoice_id: _Optional[int] = ..., list: _Optional[_Iterable[_Union[SalesInvoicesServiceMultipleItemsSingleton, _Mapping]]] = ...) -> None: ...

class SalesInvoicesServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "internal_quantity", "client_uom_id", "client_quantity", "client_family_code", "unit_price", "tax_group_id", "round_off", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    internal_quantity: int
    client_uom_id: int
    client_quantity: int
    client_family_code: str
    unit_price: int
    tax_group_id: int
    round_off: int
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., client_uom_id: _Optional[int] = ..., client_quantity: _Optional[int] = ..., client_family_code: _Optional[str] = ..., unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., round_off: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class SalesInvoiceItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "sales_invoice_id", "family_id", "internal_quantity", "client_uom_id", "client_quantity", "client_family_code", "unit_price", "tax_group_id", "round_off", "specifications")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    sales_invoice_id: int
    family_id: int
    internal_quantity: int
    client_uom_id: int
    client_quantity: int
    client_family_code: str
    unit_price: int
    tax_group_id: int
    round_off: int
    specifications: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., sales_invoice_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., client_uom_id: _Optional[int] = ..., client_quantity: _Optional[int] = ..., client_family_code: _Optional[str] = ..., unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., round_off: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class SalesInvoicesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalesInvoice]
    def __init__(self, list: _Optional[_Iterable[_Union[SalesInvoice, _Mapping]]] = ...) -> None: ...

class SalesInvoiceItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalesInvoiceItem]
    def __init__(self, list: _Optional[_Iterable[_Union[SalesInvoiceItem, _Mapping]]] = ...) -> None: ...

class SalesInvoiceItemHistoryRequest(_message.Message):
    __slots__ = ("sales_invoice_id", "family_id")
    SALES_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    sales_invoice_id: int
    family_id: int
    def __init__(self, sales_invoice_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class SalesInvoiceItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("sales_invoice_id", "family_id")
    SALES_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    sales_invoice_id: int
    family_id: int
    def __init__(self, sales_invoice_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class SalesInvoicesServiceAlreadyAddedQuantityForSourceRequest(_message.Message):
    __slots__ = ("ref_from", "ref_id", "family_id")
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ref_from: SALES_INVOICE_REF_FROM
    ref_id: int
    family_id: int
    def __init__(self, ref_from: _Optional[_Union[SALES_INVOICE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class SalesInvoicesServicePaginationReq(_message.Message):
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
    sort_key: SALES_INVOICE_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALES_INVOICE_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class SalesInvoicesServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[SalesInvoice]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[SalesInvoice, _Mapping]]] = ...) -> None: ...

class SalesInvoicesServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "currency_id", "bank_account_id", "family_id", "consignee_client_id", "buyer_client_id", "project_id", "total_value_min", "total_value_max", "form_data")
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
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_MIN_FIELD_NUMBER: _ClassVar[int]
    TOTAL_VALUE_MAX_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: SALES_INVOICE_SORT_KEY
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
    ref_from: SALES_INVOICE_REF_FROM
    ref_id: int
    currency_id: int
    bank_account_id: int
    family_id: int
    consignee_client_id: int
    buyer_client_id: int
    project_id: int
    total_value_min: int
    total_value_max: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALES_INVOICE_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[SALES_INVOICE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., bank_account_id: _Optional[int] = ..., family_id: _Optional[int] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., project_id: _Optional[int] = ..., total_value_min: _Optional[int] = ..., total_value_max: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class SalesInvoicesServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "currency_id", "bank_account_id", "family_id", "consignee_client_id", "buyer_client_id", "project_id", "total_value_min", "total_value_max", "form_data")
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
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
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
    ref_from: SALES_INVOICE_REF_FROM
    ref_id: int
    currency_id: int
    bank_account_id: int
    family_id: int
    consignee_client_id: int
    buyer_client_id: int
    project_id: int
    total_value_min: int
    total_value_max: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[SALES_INVOICE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., bank_account_id: _Optional[int] = ..., family_id: _Optional[int] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., project_id: _Optional[int] = ..., total_value_min: _Optional[int] = ..., total_value_max: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class SalesInvoicesServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "ref_from", "ref_id", "consignee_client_id", "buyer_client_id")
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
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: SALES_INVOICE_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    ref_from: SALES_INVOICE_REF_FROM
    ref_id: int
    consignee_client_id: int
    buyer_client_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALES_INVOICE_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., ref_from: _Optional[_Union[SALES_INVOICE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ...) -> None: ...

class SalesInvoicesServiceReferenceCreateRequest(_message.Message):
    __slots__ = ("user_comment", "sales_invoice_id", "goods_dispatch_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    GOODS_DISPATCH_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    sales_invoice_id: int
    goods_dispatch_id: int
    def __init__(self, user_comment: _Optional[str] = ..., sales_invoice_id: _Optional[int] = ..., goods_dispatch_id: _Optional[int] = ...) -> None: ...

class SalesInvoiceReference(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "sales_invoice_id", "goods_dispatch_id")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    GOODS_DISPATCH_ID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    sales_invoice_id: int
    goods_dispatch_id: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., sales_invoice_id: _Optional[int] = ..., goods_dispatch_id: _Optional[int] = ...) -> None: ...

class SalesInvoiceReferencesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalesInvoiceReference]
    def __init__(self, list: _Optional[_Iterable[_Union[SalesInvoiceReference, _Mapping]]] = ...) -> None: ...

class SalesInvoiceItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "sales_invoice_id", "family_id", "client_uom_id", "client_family_code", "tax_group_id", "search_key")
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
    SALES_INVOICE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: SALES_INVOICE_ITEM_SORT_KEY
    entity_uuid: str
    status: SALES_INVOICE_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    sales_invoice_id: int
    family_id: int
    client_uom_id: int
    client_family_code: str
    tax_group_id: int
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALES_INVOICE_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[SALES_INVOICE_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., sales_invoice_id: _Optional[int] = ..., family_id: _Optional[int] = ..., client_uom_id: _Optional[int] = ..., client_family_code: _Optional[str] = ..., tax_group_id: _Optional[int] = ..., search_key: _Optional[str] = ...) -> None: ...

class SalesInvoicesServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[SalesInvoiceItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[SalesInvoiceItem, _Mapping]]] = ...) -> None: ...

class SalesInvoiceDispatchedStatistics(_message.Message):
    __slots__ = ("family_id", "invoiced_quantity", "dispatched_quantity")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INVOICED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DISPATCHED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    invoiced_quantity: int
    dispatched_quantity: int
    def __init__(self, family_id: _Optional[int] = ..., invoiced_quantity: _Optional[int] = ..., dispatched_quantity: _Optional[int] = ...) -> None: ...

class SalesInvoiceDispatchedStatisticsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalesInvoiceDispatchedStatistics]
    def __init__(self, list: _Optional[_Iterable[_Union[SalesInvoiceDispatchedStatistics, _Mapping]]] = ...) -> None: ...
