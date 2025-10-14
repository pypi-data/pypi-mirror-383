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

class SALES_ORDER_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALES_ORDER_SORT_KEY_ID_UNSPECIFIED: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_CREATED_AT: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_MODIFIED_AT: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_APPROVED_ON: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_APPROVED_BY: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_COMPLETED_ON: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_REFERENCE_ID: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_CONSIGNEE_CLIENT_ID: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_BUYER_CLIENT_ID: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_LOCATION_ID: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_CURRENCY_ID: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_PROJECT_ID: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_PAYMENT_ADVANCE: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_AMENDMENT_COUNT: _ClassVar[SALES_ORDER_SORT_KEY]
    SALES_ORDER_SORT_KEY_TOTAL_VALUE: _ClassVar[SALES_ORDER_SORT_KEY]

class SALES_ORDER_REFERENCE_CONTEXT(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALES_ORDER_REFERENCE_CONTEXT_ANY_UNSPECIFIED: _ClassVar[SALES_ORDER_REFERENCE_CONTEXT]
    SALES_ORDER_REFERENCE_CONTEXT_BILLING: _ClassVar[SALES_ORDER_REFERENCE_CONTEXT]

class SALES_ORDER_REFERENCE_REF_FROM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALES_ORDER_REFERENCE_REF_FROM_ANY_UNSPECIFIED: _ClassVar[SALES_ORDER_REFERENCE_REF_FROM]
    SALES_ORDER_REFERENCE_REF_FROM_INWARD_JOB: _ClassVar[SALES_ORDER_REFERENCE_REF_FROM]
    SALES_ORDER_REFERENCE_REF_FROM_SALES_ENQUIRY: _ClassVar[SALES_ORDER_REFERENCE_REF_FROM]
    SALES_ORDER_REFERENCE_REF_FROM_SALES_QUOTATION: _ClassVar[SALES_ORDER_REFERENCE_REF_FROM]

class SALES_ORDER_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALES_ORDER_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_CREATED_AT: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_INTERNAL_QUANTITY: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_CLIENT_UOM_ID: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_CLIENT_QUANTITY: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_CLIENT_FAMILY_CODE: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_UNIT_PRICE: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_TAX_GROUP_ID: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_DISCOUNT: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]
    SALES_ORDER_ITEM_SORT_KEY_DELIVERY_DATE: _ClassVar[SALES_ORDER_ITEM_SORT_KEY]

class SALES_ORDER_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALES_ORDER_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[SALES_ORDER_ITEM_STATUS]
    SALES_ORDER_ITEM_STATUS_APPROVED: _ClassVar[SALES_ORDER_ITEM_STATUS]
    SALES_ORDER_ITEM_STATUS_UNAPPROVED: _ClassVar[SALES_ORDER_ITEM_STATUS]
SALES_ORDER_SORT_KEY_ID_UNSPECIFIED: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_CREATED_AT: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_MODIFIED_AT: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_APPROVED_ON: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_APPROVED_BY: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_APPROVER_ROLE_ID: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_COMPLETED_ON: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_REFERENCE_ID: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_FINAL_REF_NUMBER: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_CONSIGNEE_CLIENT_ID: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_BUYER_CLIENT_ID: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_LOCATION_ID: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_CURRENCY_ID: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_PROJECT_ID: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_PAYMENT_ADVANCE: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_AMENDMENT_COUNT: SALES_ORDER_SORT_KEY
SALES_ORDER_SORT_KEY_TOTAL_VALUE: SALES_ORDER_SORT_KEY
SALES_ORDER_REFERENCE_CONTEXT_ANY_UNSPECIFIED: SALES_ORDER_REFERENCE_CONTEXT
SALES_ORDER_REFERENCE_CONTEXT_BILLING: SALES_ORDER_REFERENCE_CONTEXT
SALES_ORDER_REFERENCE_REF_FROM_ANY_UNSPECIFIED: SALES_ORDER_REFERENCE_REF_FROM
SALES_ORDER_REFERENCE_REF_FROM_INWARD_JOB: SALES_ORDER_REFERENCE_REF_FROM
SALES_ORDER_REFERENCE_REF_FROM_SALES_ENQUIRY: SALES_ORDER_REFERENCE_REF_FROM
SALES_ORDER_REFERENCE_REF_FROM_SALES_QUOTATION: SALES_ORDER_REFERENCE_REF_FROM
SALES_ORDER_ITEM_SORT_KEY_ID_UNSPECIFIED: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_CREATED_AT: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_MODIFIED_AT: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_APPROVED_ON: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_APPROVED_BY: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_APPROVER_ROLE_ID: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_FAMILY_ID: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_INTERNAL_QUANTITY: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_CLIENT_UOM_ID: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_CLIENT_QUANTITY: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_CLIENT_FAMILY_CODE: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_UNIT_PRICE: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_TAX_GROUP_ID: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_DISCOUNT: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_SORT_KEY_DELIVERY_DATE: SALES_ORDER_ITEM_SORT_KEY
SALES_ORDER_ITEM_STATUS_ANY_UNSPECIFIED: SALES_ORDER_ITEM_STATUS
SALES_ORDER_ITEM_STATUS_APPROVED: SALES_ORDER_ITEM_STATUS
SALES_ORDER_ITEM_STATUS_UNAPPROVED: SALES_ORDER_ITEM_STATUS

class SalesOrdersServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "consignee_client_id", "buyer_client_id", "location_id", "currency_id", "project_id", "miscellaneous_cost", "overall_discount", "round_off", "payment_advance", "payment_cycle_in_days", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
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
    consignee_client_id: int
    buyer_client_id: int
    location_id: int
    currency_id: int
    project_id: int
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    payment_advance: int
    payment_cycle_in_days: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., location_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., payment_advance: _Optional[int] = ..., payment_cycle_in_days: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class SalesOrdersServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "consignee_client_id", "buyer_client_id", "currency_id", "project_id", "miscellaneous_cost", "overall_discount", "round_off", "payment_advance", "payment_cycle_in_days", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
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
    consignee_client_id: int
    buyer_client_id: int
    currency_id: int
    project_id: int
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    payment_advance: int
    payment_cycle_in_days: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., payment_advance: _Optional[int] = ..., payment_cycle_in_days: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class SalesOrdersServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ...) -> None: ...

class SalesOrderAncillaryParameters(_message.Message):
    __slots__ = ("consignee_client_uuid", "buyer_client_uuid", "location_uuid", "currency_uuid")
    CONSIGNEE_CLIENT_UUID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_UUID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_UUID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_UUID_FIELD_NUMBER: _ClassVar[int]
    consignee_client_uuid: str
    buyer_client_uuid: str
    location_uuid: str
    currency_uuid: str
    def __init__(self, consignee_client_uuid: _Optional[str] = ..., buyer_client_uuid: _Optional[str] = ..., location_uuid: _Optional[str] = ..., currency_uuid: _Optional[str] = ...) -> None: ...

class SalesOrder(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "consignee_client_id", "buyer_client_id", "location_id", "currency_id", "project_id", "miscellaneous_cost", "overall_discount", "round_off", "payment_advance", "payment_cycle_in_days", "amendment_count", "total_value", "list", "form_data")
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
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
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
    consignee_client_id: int
    buyer_client_id: int
    location_id: int
    currency_id: int
    project_id: int
    miscellaneous_cost: int
    overall_discount: int
    round_off: int
    payment_advance: int
    payment_cycle_in_days: int
    amendment_count: int
    total_value: float
    list: _containers.RepeatedCompositeFieldContainer[SalesOrderItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., location_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., payment_advance: _Optional[int] = ..., payment_cycle_in_days: _Optional[int] = ..., amendment_count: _Optional[int] = ..., total_value: _Optional[float] = ..., list: _Optional[_Iterable[_Union[SalesOrderItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class SalesOrdersServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "sales_order_id", "family_id", "internal_quantity", "client_uom_id", "client_quantity", "client_family_code", "unit_price", "tax_group_id", "discount", "delivery_date", "specifications", "is_invoiceable")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    IS_INVOICEABLE_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    sales_order_id: int
    family_id: int
    internal_quantity: int
    client_uom_id: int
    client_quantity: int
    client_family_code: str
    unit_price: int
    tax_group_id: int
    discount: int
    delivery_date: str
    specifications: str
    is_invoiceable: bool
    def __init__(self, user_comment: _Optional[str] = ..., sales_order_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., client_uom_id: _Optional[int] = ..., client_quantity: _Optional[int] = ..., client_family_code: _Optional[str] = ..., unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., discount: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ..., is_invoiceable: _Optional[bool] = ...) -> None: ...

class SalesOrdersServiceMultipleItemsSingleton(_message.Message):
    __slots__ = ("family_id", "internal_quantity", "client_uom_id", "client_quantity", "client_family_code", "unit_price", "tax_group_id", "discount", "delivery_date", "specifications", "is_invoiceable")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    IS_INVOICEABLE_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    internal_quantity: int
    client_uom_id: int
    client_quantity: int
    client_family_code: str
    unit_price: int
    tax_group_id: int
    discount: int
    delivery_date: str
    specifications: str
    is_invoiceable: bool
    def __init__(self, family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., client_uom_id: _Optional[int] = ..., client_quantity: _Optional[int] = ..., client_family_code: _Optional[str] = ..., unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., discount: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ..., is_invoiceable: _Optional[bool] = ...) -> None: ...

class SalesOrdersServiceMultipleItemsCreateRequest(_message.Message):
    __slots__ = ("user_comment", "sales_order_id", "list")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    sales_order_id: int
    list: _containers.RepeatedCompositeFieldContainer[SalesOrdersServiceMultipleItemsSingleton]
    def __init__(self, user_comment: _Optional[str] = ..., sales_order_id: _Optional[int] = ..., list: _Optional[_Iterable[_Union[SalesOrdersServiceMultipleItemsSingleton, _Mapping]]] = ...) -> None: ...

class SalesOrdersServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "internal_quantity", "client_uom_id", "client_quantity", "client_family_code", "unit_price", "tax_group_id", "discount", "delivery_date", "specifications", "is_invoiceable")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    IS_INVOICEABLE_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    internal_quantity: int
    client_uom_id: int
    client_quantity: int
    client_family_code: str
    unit_price: int
    tax_group_id: int
    discount: int
    delivery_date: str
    specifications: str
    is_invoiceable: bool
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., client_uom_id: _Optional[int] = ..., client_quantity: _Optional[int] = ..., client_family_code: _Optional[str] = ..., unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., discount: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ..., is_invoiceable: _Optional[bool] = ...) -> None: ...

class SalesOrderItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "sales_order_id", "bundled_with_id", "family_id", "internal_quantity", "client_uom_id", "client_quantity", "client_family_code", "unit_price", "tax_group_id", "discount", "delivery_date", "specifications", "is_invoiceable", "discounted_unit_price")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    BUNDLED_WITH_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DISCOUNT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    IS_INVOICEABLE_FIELD_NUMBER: _ClassVar[int]
    DISCOUNTED_UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    sales_order_id: int
    bundled_with_id: int
    family_id: int
    internal_quantity: int
    client_uom_id: int
    client_quantity: int
    client_family_code: str
    unit_price: int
    tax_group_id: int
    discount: int
    delivery_date: str
    specifications: str
    is_invoiceable: bool
    discounted_unit_price: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., sales_order_id: _Optional[int] = ..., bundled_with_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., client_uom_id: _Optional[int] = ..., client_quantity: _Optional[int] = ..., client_family_code: _Optional[str] = ..., unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., discount: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ..., is_invoiceable: _Optional[bool] = ..., discounted_unit_price: _Optional[int] = ...) -> None: ...

class SalesOrdersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalesOrder]
    def __init__(self, list: _Optional[_Iterable[_Union[SalesOrder, _Mapping]]] = ...) -> None: ...

class SalesOrderItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalesOrderItem]
    def __init__(self, list: _Optional[_Iterable[_Union[SalesOrderItem, _Mapping]]] = ...) -> None: ...

class SalesOrderItemHistoryRequest(_message.Message):
    __slots__ = ("sales_order_id", "family_id")
    SALES_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    sales_order_id: int
    family_id: int
    def __init__(self, sales_order_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class SalesOrderItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("sales_order_id", "family_id", "client_uom_id")
    SALES_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    sales_order_id: int
    family_id: int
    client_uom_id: int
    def __init__(self, sales_order_id: _Optional[int] = ..., family_id: _Optional[int] = ..., client_uom_id: _Optional[int] = ...) -> None: ...

class SalesOrdersServicePaginationReq(_message.Message):
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
    sort_key: SALES_ORDER_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALES_ORDER_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class SalesOrdersServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[SalesOrder]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[SalesOrder, _Mapping]]] = ...) -> None: ...

class SalesOrdersServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "consignee_client_id", "buyer_client_id", "location_id", "currency_id", "project_id", "family_id", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "total_value_min", "total_value_max", "form_data")
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
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
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
    sort_key: SALES_ORDER_SORT_KEY
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
    location_id: int
    currency_id: int
    project_id: int
    family_id: int
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    total_value_min: int
    total_value_max: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALES_ORDER_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., location_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ..., family_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., total_value_min: _Optional[int] = ..., total_value_max: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class SalesOrdersServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "consignee_client_id", "buyer_client_id", "location_id", "currency_id", "project_id", "family_id", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "total_value_min", "total_value_max", "form_data")
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
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
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
    consignee_client_id: int
    buyer_client_id: int
    location_id: int
    currency_id: int
    project_id: int
    family_id: int
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    total_value_min: int
    total_value_max: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., location_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ..., family_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., total_value_min: _Optional[int] = ..., total_value_max: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class SalesOrdersServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "consignee_client_id", "buyer_client_id", "location_id", "currency_id", "project_id")
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
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: SALES_ORDER_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    consignee_client_id: int
    buyer_client_id: int
    location_id: int
    currency_id: int
    project_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALES_ORDER_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ..., location_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ...) -> None: ...

class SalesOrdersServiceReferenceCreateRequest(_message.Message):
    __slots__ = ("user_comment", "sales_order_id", "context", "ref_from", "ref_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    sales_order_id: int
    context: SALES_ORDER_REFERENCE_CONTEXT
    ref_from: SALES_ORDER_REFERENCE_REF_FROM
    ref_id: int
    def __init__(self, user_comment: _Optional[str] = ..., sales_order_id: _Optional[int] = ..., context: _Optional[_Union[SALES_ORDER_REFERENCE_CONTEXT, str]] = ..., ref_from: _Optional[_Union[SALES_ORDER_REFERENCE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ...) -> None: ...

class SalesOrderReference(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "sales_order_id", "context", "ref_from", "ref_id")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    sales_order_id: int
    context: SALES_ORDER_REFERENCE_CONTEXT
    ref_from: SALES_ORDER_REFERENCE_REF_FROM
    ref_id: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., sales_order_id: _Optional[int] = ..., context: _Optional[_Union[SALES_ORDER_REFERENCE_CONTEXT, str]] = ..., ref_from: _Optional[_Union[SALES_ORDER_REFERENCE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ...) -> None: ...

class SalesOrderReferencesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalesOrderReference]
    def __init__(self, list: _Optional[_Iterable[_Union[SalesOrderReference, _Mapping]]] = ...) -> None: ...

class SalesOrderItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "sales_order_id", "bundled_with_id", "family_id", "client_uom_id", "client_family_code", "tax_group_id", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "search_key")
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
    SALES_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    BUNDLED_WITH_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: SALES_ORDER_ITEM_SORT_KEY
    entity_uuid: str
    status: SALES_ORDER_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    sales_order_id: int
    bundled_with_id: int
    family_id: int
    client_uom_id: int
    client_family_code: str
    tax_group_id: int
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALES_ORDER_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[SALES_ORDER_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., sales_order_id: _Optional[int] = ..., bundled_with_id: _Optional[int] = ..., family_id: _Optional[int] = ..., client_uom_id: _Optional[int] = ..., client_family_code: _Optional[str] = ..., tax_group_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., search_key: _Optional[str] = ...) -> None: ...

class SalesOrdersServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[SalesOrderItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[SalesOrderItem, _Mapping]]] = ...) -> None: ...

class SalesOrdersServiceContactCreateRequest(_message.Message):
    __slots__ = ("user_comment", "sales_order_id", "associate_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    sales_order_id: int
    associate_id: int
    def __init__(self, user_comment: _Optional[str] = ..., sales_order_id: _Optional[int] = ..., associate_id: _Optional[int] = ...) -> None: ...

class SalesOrderContact(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "sales_order_id", "associate_id", "associate_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALES_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    sales_order_id: int
    associate_id: int
    associate_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., sales_order_id: _Optional[int] = ..., associate_id: _Optional[int] = ..., associate_uuid: _Optional[str] = ...) -> None: ...

class SalesOrderContactsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalesOrderContact]
    def __init__(self, list: _Optional[_Iterable[_Union[SalesOrderContact, _Mapping]]] = ...) -> None: ...

class SalesOrderInventoryStatistics(_message.Message):
    __slots__ = ("ordered", "dispatched", "returned")
    ORDERED_FIELD_NUMBER: _ClassVar[int]
    DISPATCHED_FIELD_NUMBER: _ClassVar[int]
    RETURNED_FIELD_NUMBER: _ClassVar[int]
    ordered: int
    dispatched: int
    returned: int
    def __init__(self, ordered: _Optional[int] = ..., dispatched: _Optional[int] = ..., returned: _Optional[int] = ...) -> None: ...

class SalesOrderBillingStatistics(_message.Message):
    __slots__ = ("ordered", "invoiced", "credited")
    ORDERED_FIELD_NUMBER: _ClassVar[int]
    INVOICED_FIELD_NUMBER: _ClassVar[int]
    CREDITED_FIELD_NUMBER: _ClassVar[int]
    ordered: int
    invoiced: int
    credited: int
    def __init__(self, ordered: _Optional[int] = ..., invoiced: _Optional[int] = ..., credited: _Optional[int] = ...) -> None: ...

class SalesOrderInventoryMatch(_message.Message):
    __slots__ = ("family_id", "client_uom_id", "ordered_primary", "ordered_secondary", "dispatched_primary", "dispatched_secondary", "invoiced_primary", "invoiced_secondary", "returned_primary", "returned_secondary", "credited_primary", "credited_secondary")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    ORDERED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    ORDERED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    DISPATCHED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    DISPATCHED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    INVOICED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    INVOICED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    RETURNED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    RETURNED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    CREDITED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    CREDITED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    client_uom_id: int
    ordered_primary: int
    ordered_secondary: int
    dispatched_primary: int
    dispatched_secondary: int
    invoiced_primary: int
    invoiced_secondary: int
    returned_primary: int
    returned_secondary: int
    credited_primary: int
    credited_secondary: int
    def __init__(self, family_id: _Optional[int] = ..., client_uom_id: _Optional[int] = ..., ordered_primary: _Optional[int] = ..., ordered_secondary: _Optional[int] = ..., dispatched_primary: _Optional[int] = ..., dispatched_secondary: _Optional[int] = ..., invoiced_primary: _Optional[int] = ..., invoiced_secondary: _Optional[int] = ..., returned_primary: _Optional[int] = ..., returned_secondary: _Optional[int] = ..., credited_primary: _Optional[int] = ..., credited_secondary: _Optional[int] = ...) -> None: ...

class SalesOrderInventoryMatchList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalesOrderInventoryMatch]
    def __init__(self, list: _Optional[_Iterable[_Union[SalesOrderInventoryMatch, _Mapping]]] = ...) -> None: ...

class SalesOrderPriceMatch(_message.Message):
    __slots__ = ("family_id", "client_uom_id", "ordered_primary", "ordered_secondary", "ordered_total_value", "invoiced_primary", "invoiced_secondary", "invoiced_total_value", "credited_primary", "credited_secondary", "credited_total_value")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    ORDERED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    ORDERED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    ORDERED_TOTAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    INVOICED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    INVOICED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    INVOICED_TOTAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    CREDITED_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    CREDITED_SECONDARY_FIELD_NUMBER: _ClassVar[int]
    CREDITED_TOTAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    client_uom_id: int
    ordered_primary: int
    ordered_secondary: int
    ordered_total_value: int
    invoiced_primary: int
    invoiced_secondary: int
    invoiced_total_value: int
    credited_primary: int
    credited_secondary: int
    credited_total_value: int
    def __init__(self, family_id: _Optional[int] = ..., client_uom_id: _Optional[int] = ..., ordered_primary: _Optional[int] = ..., ordered_secondary: _Optional[int] = ..., ordered_total_value: _Optional[int] = ..., invoiced_primary: _Optional[int] = ..., invoiced_secondary: _Optional[int] = ..., invoiced_total_value: _Optional[int] = ..., credited_primary: _Optional[int] = ..., credited_secondary: _Optional[int] = ..., credited_total_value: _Optional[int] = ...) -> None: ...

class SalesOrderPriceMatchList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalesOrderPriceMatch]
    def __init__(self, list: _Optional[_Iterable[_Union[SalesOrderPriceMatch, _Mapping]]] = ...) -> None: ...
