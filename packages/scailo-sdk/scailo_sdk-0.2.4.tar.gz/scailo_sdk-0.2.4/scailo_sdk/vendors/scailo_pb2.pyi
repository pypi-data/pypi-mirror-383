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

class VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE_ANY_UNSPECIFIED: _ClassVar[VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE]
    VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE_PERCENTAGE: _ClassVar[VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE]
    VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE_ABSOLUTE: _ClassVar[VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE]

class VENDOR_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_SORT_KEY_ID_UNSPECIFIED: _ClassVar[VENDOR_SORT_KEY]
    VENDOR_SORT_KEY_CREATED_AT: _ClassVar[VENDOR_SORT_KEY]
    VENDOR_SORT_KEY_MODIFIED_AT: _ClassVar[VENDOR_SORT_KEY]
    VENDOR_SORT_KEY_APPROVED_ON: _ClassVar[VENDOR_SORT_KEY]
    VENDOR_SORT_KEY_APPROVED_BY: _ClassVar[VENDOR_SORT_KEY]
    VENDOR_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[VENDOR_SORT_KEY]
    VENDOR_SORT_KEY_NAME: _ClassVar[VENDOR_SORT_KEY]
    VENDOR_SORT_KEY_CODE: _ClassVar[VENDOR_SORT_KEY]
    VENDOR_SORT_KEY_EMAIL: _ClassVar[VENDOR_SORT_KEY]
    VENDOR_SORT_KEY_PHONE: _ClassVar[VENDOR_SORT_KEY]

class VENDOR_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[VENDOR_ITEM_SORT_KEY]
    VENDOR_ITEM_SORT_KEY_CREATED_AT: _ClassVar[VENDOR_ITEM_SORT_KEY]
    VENDOR_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[VENDOR_ITEM_SORT_KEY]
    VENDOR_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[VENDOR_ITEM_SORT_KEY]
    VENDOR_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[VENDOR_ITEM_SORT_KEY]
    VENDOR_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[VENDOR_ITEM_SORT_KEY]
    VENDOR_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[VENDOR_ITEM_SORT_KEY]
    VENDOR_ITEM_SORT_KEY_VENDOR_FAMILY_CODE: _ClassVar[VENDOR_ITEM_SORT_KEY]
    VENDOR_ITEM_SORT_KEY_UOM_ID: _ClassVar[VENDOR_ITEM_SORT_KEY]
    VENDOR_ITEM_SORT_KEY_TAX_GROUP_ID: _ClassVar[VENDOR_ITEM_SORT_KEY]
    VENDOR_ITEM_SORT_KEY_PRICE: _ClassVar[VENDOR_ITEM_SORT_KEY]
    VENDOR_ITEM_SORT_KEY_MIN_ORDER_QTY: _ClassVar[VENDOR_ITEM_SORT_KEY]
    VENDOR_ITEM_SORT_KEY_MAX_ORDER_QTY: _ClassVar[VENDOR_ITEM_SORT_KEY]
    VENDOR_ITEM_SORT_KEY_STEP_INTERVAL: _ClassVar[VENDOR_ITEM_SORT_KEY]

class VENDOR_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[VENDOR_ITEM_STATUS]
    VENDOR_ITEM_STATUS_APPROVED: _ClassVar[VENDOR_ITEM_STATUS]
    VENDOR_ITEM_STATUS_UNAPPROVED: _ClassVar[VENDOR_ITEM_STATUS]

class VENDOR_USER_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_USER_STATUS_ANY_UNSPECIFIED: _ClassVar[VENDOR_USER_STATUS]
    VENDOR_USER_STATUS_APPROVED: _ClassVar[VENDOR_USER_STATUS]
    VENDOR_USER_STATUS_UNAPPROVED: _ClassVar[VENDOR_USER_STATUS]
VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE_ANY_UNSPECIFIED: VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE
VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE_PERCENTAGE: VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE
VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE_ABSOLUTE: VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE
VENDOR_SORT_KEY_ID_UNSPECIFIED: VENDOR_SORT_KEY
VENDOR_SORT_KEY_CREATED_AT: VENDOR_SORT_KEY
VENDOR_SORT_KEY_MODIFIED_AT: VENDOR_SORT_KEY
VENDOR_SORT_KEY_APPROVED_ON: VENDOR_SORT_KEY
VENDOR_SORT_KEY_APPROVED_BY: VENDOR_SORT_KEY
VENDOR_SORT_KEY_APPROVER_ROLE_ID: VENDOR_SORT_KEY
VENDOR_SORT_KEY_NAME: VENDOR_SORT_KEY
VENDOR_SORT_KEY_CODE: VENDOR_SORT_KEY
VENDOR_SORT_KEY_EMAIL: VENDOR_SORT_KEY
VENDOR_SORT_KEY_PHONE: VENDOR_SORT_KEY
VENDOR_ITEM_SORT_KEY_ID_UNSPECIFIED: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_SORT_KEY_CREATED_AT: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_SORT_KEY_MODIFIED_AT: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_SORT_KEY_APPROVED_ON: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_SORT_KEY_APPROVED_BY: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_SORT_KEY_APPROVER_ROLE_ID: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_SORT_KEY_FAMILY_ID: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_SORT_KEY_VENDOR_FAMILY_CODE: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_SORT_KEY_UOM_ID: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_SORT_KEY_TAX_GROUP_ID: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_SORT_KEY_PRICE: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_SORT_KEY_MIN_ORDER_QTY: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_SORT_KEY_MAX_ORDER_QTY: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_SORT_KEY_STEP_INTERVAL: VENDOR_ITEM_SORT_KEY
VENDOR_ITEM_STATUS_ANY_UNSPECIFIED: VENDOR_ITEM_STATUS
VENDOR_ITEM_STATUS_APPROVED: VENDOR_ITEM_STATUS
VENDOR_ITEM_STATUS_UNAPPROVED: VENDOR_ITEM_STATUS
VENDOR_USER_STATUS_ANY_UNSPECIFIED: VENDOR_USER_STATUS
VENDOR_USER_STATUS_APPROVED: VENDOR_USER_STATUS
VENDOR_USER_STATUS_UNAPPROVED: VENDOR_USER_STATUS

class VendorsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "name", "code", "email", "phone", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    name: str
    code: str
    email: str
    phone: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class VendorsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "name", "code", "email", "phone", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    name: str
    code: str
    email: str
    phone: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class Vendor(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "vault_folder_id", "name", "code", "email", "phone", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    vault_folder_id: int
    name: str
    code: str
    email: str
    phone: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class VendorsServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "vendor_id", "family_id", "vendor_family_code", "uom_id", "tax_group_id", "price", "price_deviation_rel_lower_limit_type", "price_deviation_rel_lower_limit_value", "price_deviation_rel_upper_limit_type", "price_deviation_rel_upper_limit_value", "min_order_qty", "max_order_qty", "step_interval")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    PRICE_DEVIATION_REL_LOWER_LIMIT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRICE_DEVIATION_REL_LOWER_LIMIT_VALUE_FIELD_NUMBER: _ClassVar[int]
    PRICE_DEVIATION_REL_UPPER_LIMIT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRICE_DEVIATION_REL_UPPER_LIMIT_VALUE_FIELD_NUMBER: _ClassVar[int]
    MIN_ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    MAX_ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    STEP_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    vendor_id: int
    family_id: int
    vendor_family_code: str
    uom_id: int
    tax_group_id: int
    price: int
    price_deviation_rel_lower_limit_type: VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE
    price_deviation_rel_lower_limit_value: int
    price_deviation_rel_upper_limit_type: VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE
    price_deviation_rel_upper_limit_value: int
    min_order_qty: int
    max_order_qty: int
    step_interval: int
    def __init__(self, user_comment: _Optional[str] = ..., vendor_id: _Optional[int] = ..., family_id: _Optional[int] = ..., vendor_family_code: _Optional[str] = ..., uom_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., price: _Optional[int] = ..., price_deviation_rel_lower_limit_type: _Optional[_Union[VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE, str]] = ..., price_deviation_rel_lower_limit_value: _Optional[int] = ..., price_deviation_rel_upper_limit_type: _Optional[_Union[VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE, str]] = ..., price_deviation_rel_upper_limit_value: _Optional[int] = ..., min_order_qty: _Optional[int] = ..., max_order_qty: _Optional[int] = ..., step_interval: _Optional[int] = ...) -> None: ...

class VendorsServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "vendor_family_code", "uom_id", "tax_group_id", "price", "price_deviation_rel_lower_limit_type", "price_deviation_rel_lower_limit_value", "price_deviation_rel_upper_limit_type", "price_deviation_rel_upper_limit_value", "min_order_qty", "max_order_qty", "step_interval")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    PRICE_DEVIATION_REL_LOWER_LIMIT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRICE_DEVIATION_REL_LOWER_LIMIT_VALUE_FIELD_NUMBER: _ClassVar[int]
    PRICE_DEVIATION_REL_UPPER_LIMIT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRICE_DEVIATION_REL_UPPER_LIMIT_VALUE_FIELD_NUMBER: _ClassVar[int]
    MIN_ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    MAX_ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    STEP_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    vendor_family_code: str
    uom_id: int
    tax_group_id: int
    price: int
    price_deviation_rel_lower_limit_type: VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE
    price_deviation_rel_lower_limit_value: int
    price_deviation_rel_upper_limit_type: VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE
    price_deviation_rel_upper_limit_value: int
    min_order_qty: int
    max_order_qty: int
    step_interval: int
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., vendor_family_code: _Optional[str] = ..., uom_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., price: _Optional[int] = ..., price_deviation_rel_lower_limit_type: _Optional[_Union[VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE, str]] = ..., price_deviation_rel_lower_limit_value: _Optional[int] = ..., price_deviation_rel_upper_limit_type: _Optional[_Union[VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE, str]] = ..., price_deviation_rel_upper_limit_value: _Optional[int] = ..., min_order_qty: _Optional[int] = ..., max_order_qty: _Optional[int] = ..., step_interval: _Optional[int] = ...) -> None: ...

class VendorItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "vendor_id", "family_id", "vendor_family_code", "uom_id", "tax_group_id", "price", "price_deviation_rel_lower_limit_type", "price_deviation_rel_lower_limit_value", "price_deviation_rel_upper_limit_type", "price_deviation_rel_upper_limit_value", "min_order_qty", "max_order_qty", "step_interval")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    PRICE_DEVIATION_REL_LOWER_LIMIT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRICE_DEVIATION_REL_LOWER_LIMIT_VALUE_FIELD_NUMBER: _ClassVar[int]
    PRICE_DEVIATION_REL_UPPER_LIMIT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRICE_DEVIATION_REL_UPPER_LIMIT_VALUE_FIELD_NUMBER: _ClassVar[int]
    MIN_ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    MAX_ORDER_QTY_FIELD_NUMBER: _ClassVar[int]
    STEP_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    vendor_id: int
    family_id: int
    vendor_family_code: str
    uom_id: int
    tax_group_id: int
    price: int
    price_deviation_rel_lower_limit_type: VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE
    price_deviation_rel_lower_limit_value: int
    price_deviation_rel_upper_limit_type: VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE
    price_deviation_rel_upper_limit_value: int
    min_order_qty: int
    max_order_qty: int
    step_interval: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., vendor_id: _Optional[int] = ..., family_id: _Optional[int] = ..., vendor_family_code: _Optional[str] = ..., uom_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., price: _Optional[int] = ..., price_deviation_rel_lower_limit_type: _Optional[_Union[VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE, str]] = ..., price_deviation_rel_lower_limit_value: _Optional[int] = ..., price_deviation_rel_upper_limit_type: _Optional[_Union[VENDOR_ITEM_PRICE_DEVIATION_LIMIT_TYPE, str]] = ..., price_deviation_rel_upper_limit_value: _Optional[int] = ..., min_order_qty: _Optional[int] = ..., max_order_qty: _Optional[int] = ..., step_interval: _Optional[int] = ...) -> None: ...

class VendorsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[Vendor]
    def __init__(self, list: _Optional[_Iterable[_Union[Vendor, _Mapping]]] = ...) -> None: ...

class VendorItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VendorItem]
    def __init__(self, list: _Optional[_Iterable[_Union[VendorItem, _Mapping]]] = ...) -> None: ...

class VendorItemHistoryRequest(_message.Message):
    __slots__ = ("vendor_id", "family_id", "uom_id")
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    vendor_id: int
    family_id: int
    uom_id: int
    def __init__(self, vendor_id: _Optional[int] = ..., family_id: _Optional[int] = ..., uom_id: _Optional[int] = ...) -> None: ...

class VendorsServicePaginationReq(_message.Message):
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
    sort_key: VENDOR_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VENDOR_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class VendorsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[Vendor]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[Vendor, _Mapping]]] = ...) -> None: ...

class VendorsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "name", "code", "email", "phone", "family_id", "form_data")
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
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: VENDOR_SORT_KEY
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
    name: str
    code: str
    email: str
    phone: str
    family_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VENDOR_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., family_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class VendorsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "name", "code", "email", "phone", "family_id", "form_data")
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
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
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
    name: str
    code: str
    email: str
    phone: str
    family_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., family_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class VendorsServiceSearchAllReq(_message.Message):
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
    sort_key: VENDOR_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VENDOR_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ...) -> None: ...

class VendorItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "vendor_id", "family_id", "vendor_family_code", "uom_id", "tax_group_id", "search_key")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_FAMILY_CODE_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: VENDOR_ITEM_SORT_KEY
    entity_uuid: str
    status: VENDOR_ITEM_STATUS
    vendor_id: int
    family_id: int
    vendor_family_code: str
    uom_id: int
    tax_group_id: int
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VENDOR_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[VENDOR_ITEM_STATUS, str]] = ..., vendor_id: _Optional[int] = ..., family_id: _Optional[int] = ..., vendor_family_code: _Optional[str] = ..., uom_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., search_key: _Optional[str] = ...) -> None: ...

class VendorsServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[VendorItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[VendorItem, _Mapping]]] = ...) -> None: ...

class VendorItemRequired(_message.Message):
    __slots__ = ("item", "required_qty")
    ITEM_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_QTY_FIELD_NUMBER: _ClassVar[int]
    item: VendorItem
    required_qty: int
    def __init__(self, item: _Optional[_Union[VendorItem, _Mapping]] = ..., required_qty: _Optional[int] = ...) -> None: ...

class VendorsServicePaginatedRequiredItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[VendorItemRequired]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[VendorItemRequired, _Mapping]]] = ...) -> None: ...

class VendorsServiceUserCreateRequest(_message.Message):
    __slots__ = ("user_comment", "vendor_id", "user_id", "associate_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    vendor_id: int
    user_id: int
    associate_id: int
    def __init__(self, user_comment: _Optional[str] = ..., vendor_id: _Optional[int] = ..., user_id: _Optional[int] = ..., associate_id: _Optional[int] = ...) -> None: ...

class VendorUser(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "vendor_id", "user_id", "associate_id")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    vendor_id: int
    user_id: int
    associate_id: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., vendor_id: _Optional[int] = ..., user_id: _Optional[int] = ..., associate_id: _Optional[int] = ...) -> None: ...

class VendorUsersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VendorUser]
    def __init__(self, list: _Optional[_Iterable[_Union[VendorUser, _Mapping]]] = ...) -> None: ...

class VendorUsersSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "entity_uuid", "status", "vendor_id", "user_id", "associate_id", "search_key")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    entity_uuid: str
    status: VENDOR_USER_STATUS
    vendor_id: int
    user_id: int
    associate_id: int
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[VENDOR_USER_STATUS, str]] = ..., vendor_id: _Optional[int] = ..., user_id: _Optional[int] = ..., associate_id: _Optional[int] = ..., search_key: _Optional[str] = ...) -> None: ...

class VendorsServicePaginatedUsersResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[VendorUser]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[VendorUser, _Mapping]]] = ...) -> None: ...
