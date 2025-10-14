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

class SUPPLY_OFFER_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SUPPLY_OFFER_SORT_KEY_ID_UNSPECIFIED: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_CREATED_AT: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_MODIFIED_AT: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_APPROVED_ON: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_APPROVED_BY: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_COMPLETED_ON: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_REFERENCE_ID: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_CONSIGNEE_LOCATION_ID: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_BUYER_LOCATION_ID: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_VENDOR_ID: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_CURRENCY_ID: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_PROJECT_ID: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_PAYMENT_ADVANCE: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_AMENDMENT_COUNT: _ClassVar[SUPPLY_OFFER_SORT_KEY]
    SUPPLY_OFFER_SORT_KEY_TOTAL_VALUE: _ClassVar[SUPPLY_OFFER_SORT_KEY]

class SUPPLY_OFFER_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SUPPLY_OFFER_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]
    SUPPLY_OFFER_ITEM_SORT_KEY_CREATED_AT: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]
    SUPPLY_OFFER_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]
    SUPPLY_OFFER_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]
    SUPPLY_OFFER_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]
    SUPPLY_OFFER_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]
    SUPPLY_OFFER_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]
    SUPPLY_OFFER_ITEM_SORT_KEY_INTERNAL_QUANTITY: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]
    SUPPLY_OFFER_ITEM_SORT_KEY_VENDOR_UOM_ID: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]
    SUPPLY_OFFER_ITEM_SORT_KEY_VENDOR_QUANTITY: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]
    SUPPLY_OFFER_ITEM_SORT_KEY_VENDOR_UNIT_PRICE: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]
    SUPPLY_OFFER_ITEM_SORT_KEY_TAX_GROUP_ID: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]
    SUPPLY_OFFER_ITEM_SORT_KEY_DISCOUNT: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]
    SUPPLY_OFFER_ITEM_SORT_KEY_DELIVERY_DATE: _ClassVar[SUPPLY_OFFER_ITEM_SORT_KEY]

class SUPPLY_OFFER_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SUPPLY_OFFER_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[SUPPLY_OFFER_ITEM_STATUS]
    SUPPLY_OFFER_ITEM_STATUS_APPROVED: _ClassVar[SUPPLY_OFFER_ITEM_STATUS]
    SUPPLY_OFFER_ITEM_STATUS_UNAPPROVED: _ClassVar[SUPPLY_OFFER_ITEM_STATUS]
SUPPLY_OFFER_SORT_KEY_ID_UNSPECIFIED: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_CREATED_AT: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_MODIFIED_AT: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_APPROVED_ON: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_APPROVED_BY: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_APPROVER_ROLE_ID: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_COMPLETED_ON: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_REFERENCE_ID: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_FINAL_REF_NUMBER: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_CONSIGNEE_LOCATION_ID: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_BUYER_LOCATION_ID: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_VENDOR_ID: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_CURRENCY_ID: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_PROJECT_ID: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_PAYMENT_ADVANCE: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_AMENDMENT_COUNT: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_SORT_KEY_TOTAL_VALUE: SUPPLY_OFFER_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_ID_UNSPECIFIED: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_CREATED_AT: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_MODIFIED_AT: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_APPROVED_ON: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_APPROVED_BY: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_APPROVER_ROLE_ID: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_FAMILY_ID: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_INTERNAL_QUANTITY: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_VENDOR_UOM_ID: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_VENDOR_QUANTITY: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_VENDOR_UNIT_PRICE: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_TAX_GROUP_ID: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_DISCOUNT: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_SORT_KEY_DELIVERY_DATE: SUPPLY_OFFER_ITEM_SORT_KEY
SUPPLY_OFFER_ITEM_STATUS_ANY_UNSPECIFIED: SUPPLY_OFFER_ITEM_STATUS
SUPPLY_OFFER_ITEM_STATUS_APPROVED: SUPPLY_OFFER_ITEM_STATUS
SUPPLY_OFFER_ITEM_STATUS_UNAPPROVED: SUPPLY_OFFER_ITEM_STATUS

class SupplyOffersServiceCreateRequest(_message.Message):
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

class SupplyOffersServiceUpdateRequest(_message.Message):
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

class SupplyOffersServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ...) -> None: ...

class SupplyOfferAncillaryParameters(_message.Message):
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

class SupplyOffer(_message.Message):
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
    list: _containers.RepeatedCompositeFieldContainer[SupplyOfferItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., buyer_location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ..., miscellaneous_cost: _Optional[int] = ..., overall_discount: _Optional[int] = ..., round_off: _Optional[int] = ..., payment_advance: _Optional[int] = ..., payment_cycle_in_days: _Optional[int] = ..., amendment_count: _Optional[int] = ..., total_value: _Optional[float] = ..., list: _Optional[_Iterable[_Union[SupplyOfferItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class SupplyOffersServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "supply_offer_id", "family_id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "vendor_unit_price", "tax_group_id", "discount", "delivery_date", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SUPPLY_OFFER_ID_FIELD_NUMBER: _ClassVar[int]
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
    supply_offer_id: int
    family_id: int
    internal_quantity: int
    vendor_uom_id: int
    vendor_quantity: int
    vendor_unit_price: int
    tax_group_id: int
    discount: int
    delivery_date: str
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., supply_offer_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., vendor_unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., discount: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ...) -> None: ...

class SupplyOffersServiceItemUpdateRequest(_message.Message):
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

class SupplyOfferItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "supply_offer_id", "family_id", "internal_quantity", "vendor_uom_id", "vendor_quantity", "vendor_unit_price", "tax_group_id", "discount", "delivery_date", "specifications", "discounted_vendor_unit_price", "supply_offer_uuid", "family_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SUPPLY_OFFER_ID_FIELD_NUMBER: _ClassVar[int]
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
    SUPPLY_OFFER_UUID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    supply_offer_id: int
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
    supply_offer_uuid: str
    family_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., supply_offer_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., vendor_quantity: _Optional[int] = ..., vendor_unit_price: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., discount: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ..., discounted_vendor_unit_price: _Optional[int] = ..., supply_offer_uuid: _Optional[str] = ..., family_uuid: _Optional[str] = ...) -> None: ...

class SupplyOffersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SupplyOffer]
    def __init__(self, list: _Optional[_Iterable[_Union[SupplyOffer, _Mapping]]] = ...) -> None: ...

class SupplyOfferItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SupplyOfferItem]
    def __init__(self, list: _Optional[_Iterable[_Union[SupplyOfferItem, _Mapping]]] = ...) -> None: ...

class SupplyOfferItemHistoryRequest(_message.Message):
    __slots__ = ("supply_offer_id", "family_id")
    SUPPLY_OFFER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    supply_offer_id: int
    family_id: int
    def __init__(self, supply_offer_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class SupplyOfferItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("supply_offer_id", "family_id", "vendor_uom_id")
    SUPPLY_OFFER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    supply_offer_id: int
    family_id: int
    vendor_uom_id: int
    def __init__(self, supply_offer_id: _Optional[int] = ..., family_id: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ...) -> None: ...

class SupplyOffersServicePaginationReq(_message.Message):
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
    sort_key: SUPPLY_OFFER_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SUPPLY_OFFER_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class SupplyOffersServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[SupplyOffer]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[SupplyOffer, _Mapping]]] = ...) -> None: ...

class SupplyOffersServiceFilterReq(_message.Message):
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
    sort_key: SUPPLY_OFFER_SORT_KEY
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
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SUPPLY_OFFER_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., buyer_location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ..., family_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., total_value_min: _Optional[int] = ..., total_value_max: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class SupplyOffersServiceCountReq(_message.Message):
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

class SupplyOffersServiceSearchAllReq(_message.Message):
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
    sort_key: SUPPLY_OFFER_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    consignee_location_id: int
    buyer_location_id: int
    vendor_id: int
    currency_id: int
    project_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SUPPLY_OFFER_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., buyer_location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., project_id: _Optional[int] = ...) -> None: ...

class SupplyOfferItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "supply_offer_id", "family_id", "vendor_uom_id", "tax_group_id", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "search_key", "vendor_id")
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
    SUPPLY_OFFER_ID_FIELD_NUMBER: _ClassVar[int]
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
    sort_key: SUPPLY_OFFER_ITEM_SORT_KEY
    entity_uuid: str
    status: SUPPLY_OFFER_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    supply_offer_id: int
    family_id: int
    vendor_uom_id: int
    tax_group_id: int
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    search_key: str
    vendor_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SUPPLY_OFFER_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[SUPPLY_OFFER_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., supply_offer_id: _Optional[int] = ..., family_id: _Optional[int] = ..., vendor_uom_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., search_key: _Optional[str] = ..., vendor_id: _Optional[int] = ...) -> None: ...

class SupplyOffersServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[SupplyOfferItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[SupplyOfferItem, _Mapping]]] = ...) -> None: ...
