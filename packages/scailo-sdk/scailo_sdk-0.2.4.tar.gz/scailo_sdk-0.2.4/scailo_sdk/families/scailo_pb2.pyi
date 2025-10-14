from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from forms_fields_data import scailo_pb2 as _scailo_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FAMILY_TYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FAMILY_TYPE_ANY_UNSPECIFIED: _ClassVar[FAMILY_TYPE]
    FAMILY_TYPE_COMPONENT: _ClassVar[FAMILY_TYPE]
    FAMILY_TYPE_EQUIPMENT: _ClassVar[FAMILY_TYPE]
    FAMILY_TYPE_FEEDSTOCK: _ClassVar[FAMILY_TYPE]
    FAMILY_TYPE_INFRASTRUCTURE: _ClassVar[FAMILY_TYPE]
    FAMILY_TYPE_MERCHANDISE: _ClassVar[FAMILY_TYPE]
    FAMILY_TYPE_PRODUCT: _ClassVar[FAMILY_TYPE]
    FAMILY_TYPE_SERVICE: _ClassVar[FAMILY_TYPE]

class CONSUMPTION_SEQUENCE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONSUMPTION_SEQUENCE_ANY_UNSPECIFIED: _ClassVar[CONSUMPTION_SEQUENCE]
    CONSUMPTION_SEQUENCE_FIFO_INTAKE: _ClassVar[CONSUMPTION_SEQUENCE]
    CONSUMPTION_SEQUENCE_FIFO_SHELF_LIFE: _ClassVar[CONSUMPTION_SEQUENCE]
    CONSUMPTION_SEQUENCE_FIFO_WARRANTY: _ClassVar[CONSUMPTION_SEQUENCE]
    CONSUMPTION_SEQUENCE_LIFO_INTAKE: _ClassVar[CONSUMPTION_SEQUENCE]
    CONSUMPTION_SEQUENCE_LIFO_SHELF_LIFE: _ClassVar[CONSUMPTION_SEQUENCE]
    CONSUMPTION_SEQUENCE_LIFO_WARRANTY: _ClassVar[CONSUMPTION_SEQUENCE]

class FAMILY_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FAMILY_SORT_KEY_ID_UNSPECIFIED: _ClassVar[FAMILY_SORT_KEY]
    FAMILY_SORT_KEY_CREATED_AT: _ClassVar[FAMILY_SORT_KEY]
    FAMILY_SORT_KEY_MODIFIED_AT: _ClassVar[FAMILY_SORT_KEY]
    FAMILY_SORT_KEY_APPROVED_ON: _ClassVar[FAMILY_SORT_KEY]
    FAMILY_SORT_KEY_APPROVED_BY: _ClassVar[FAMILY_SORT_KEY]
    FAMILY_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[FAMILY_SORT_KEY]
    FAMILY_SORT_KEY_NAME: _ClassVar[FAMILY_SORT_KEY]
    FAMILY_SORT_KEY_CODE: _ClassVar[FAMILY_SORT_KEY]
    FAMILY_SORT_KEY_UNIT_QUANTITY: _ClassVar[FAMILY_SORT_KEY]
    FAMILY_SORT_KEY_PRICE: _ClassVar[FAMILY_SORT_KEY]
    FAMILY_SORT_KEY_AMENDMENT_COUNT: _ClassVar[FAMILY_SORT_KEY]
FAMILY_TYPE_ANY_UNSPECIFIED: FAMILY_TYPE
FAMILY_TYPE_COMPONENT: FAMILY_TYPE
FAMILY_TYPE_EQUIPMENT: FAMILY_TYPE
FAMILY_TYPE_FEEDSTOCK: FAMILY_TYPE
FAMILY_TYPE_INFRASTRUCTURE: FAMILY_TYPE
FAMILY_TYPE_MERCHANDISE: FAMILY_TYPE
FAMILY_TYPE_PRODUCT: FAMILY_TYPE
FAMILY_TYPE_SERVICE: FAMILY_TYPE
CONSUMPTION_SEQUENCE_ANY_UNSPECIFIED: CONSUMPTION_SEQUENCE
CONSUMPTION_SEQUENCE_FIFO_INTAKE: CONSUMPTION_SEQUENCE
CONSUMPTION_SEQUENCE_FIFO_SHELF_LIFE: CONSUMPTION_SEQUENCE
CONSUMPTION_SEQUENCE_FIFO_WARRANTY: CONSUMPTION_SEQUENCE
CONSUMPTION_SEQUENCE_LIFO_INTAKE: CONSUMPTION_SEQUENCE
CONSUMPTION_SEQUENCE_LIFO_SHELF_LIFE: CONSUMPTION_SEQUENCE
CONSUMPTION_SEQUENCE_LIFO_WARRANTY: CONSUMPTION_SEQUENCE
FAMILY_SORT_KEY_ID_UNSPECIFIED: FAMILY_SORT_KEY
FAMILY_SORT_KEY_CREATED_AT: FAMILY_SORT_KEY
FAMILY_SORT_KEY_MODIFIED_AT: FAMILY_SORT_KEY
FAMILY_SORT_KEY_APPROVED_ON: FAMILY_SORT_KEY
FAMILY_SORT_KEY_APPROVED_BY: FAMILY_SORT_KEY
FAMILY_SORT_KEY_APPROVER_ROLE_ID: FAMILY_SORT_KEY
FAMILY_SORT_KEY_NAME: FAMILY_SORT_KEY
FAMILY_SORT_KEY_CODE: FAMILY_SORT_KEY
FAMILY_SORT_KEY_UNIT_QUANTITY: FAMILY_SORT_KEY
FAMILY_SORT_KEY_PRICE: FAMILY_SORT_KEY
FAMILY_SORT_KEY_AMENDMENT_COUNT: FAMILY_SORT_KEY

class FamilyTypesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedScalarFieldContainer[FAMILY_TYPE]
    def __init__(self, list: _Optional[_Iterable[_Union[FAMILY_TYPE, str]]] = ...) -> None: ...

class FamiliesServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "name", "print_name", "code", "description", "family_type", "hsn_sac_code", "uom_id", "unit_quantity", "parent_id", "is_leaf", "ledger_id", "tax_group_id", "price", "min_stock_to_maintain", "consumption_sequence", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRINT_NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    HSN_SAC_CODE_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    UNIT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    IS_LEAF_FIELD_NUMBER: _ClassVar[int]
    LEDGER_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    MIN_STOCK_TO_MAINTAIN_FIELD_NUMBER: _ClassVar[int]
    CONSUMPTION_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    name: str
    print_name: str
    code: str
    description: str
    family_type: FAMILY_TYPE
    hsn_sac_code: str
    uom_id: int
    unit_quantity: int
    parent_id: int
    is_leaf: bool
    ledger_id: int
    tax_group_id: int
    price: int
    min_stock_to_maintain: int
    consumption_sequence: CONSUMPTION_SEQUENCE
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., print_name: _Optional[str] = ..., code: _Optional[str] = ..., description: _Optional[str] = ..., family_type: _Optional[_Union[FAMILY_TYPE, str]] = ..., hsn_sac_code: _Optional[str] = ..., uom_id: _Optional[int] = ..., unit_quantity: _Optional[int] = ..., parent_id: _Optional[int] = ..., is_leaf: _Optional[bool] = ..., ledger_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., price: _Optional[int] = ..., min_stock_to_maintain: _Optional[int] = ..., consumption_sequence: _Optional[_Union[CONSUMPTION_SEQUENCE, str]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class FamiliesServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "name", "print_name", "code", "description", "family_type", "hsn_sac_code", "uom_id", "unit_quantity", "parent_id", "is_leaf", "ledger_id", "tax_group_id", "price", "min_stock_to_maintain", "consumption_sequence", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRINT_NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    HSN_SAC_CODE_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    UNIT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    IS_LEAF_FIELD_NUMBER: _ClassVar[int]
    LEDGER_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    MIN_STOCK_TO_MAINTAIN_FIELD_NUMBER: _ClassVar[int]
    CONSUMPTION_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    name: str
    print_name: str
    code: str
    description: str
    family_type: FAMILY_TYPE
    hsn_sac_code: str
    uom_id: int
    unit_quantity: int
    parent_id: int
    is_leaf: bool
    ledger_id: int
    tax_group_id: int
    price: int
    min_stock_to_maintain: int
    consumption_sequence: CONSUMPTION_SEQUENCE
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., print_name: _Optional[str] = ..., code: _Optional[str] = ..., description: _Optional[str] = ..., family_type: _Optional[_Union[FAMILY_TYPE, str]] = ..., hsn_sac_code: _Optional[str] = ..., uom_id: _Optional[int] = ..., unit_quantity: _Optional[int] = ..., parent_id: _Optional[int] = ..., is_leaf: _Optional[bool] = ..., ledger_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., price: _Optional[int] = ..., min_stock_to_maintain: _Optional[int] = ..., consumption_sequence: _Optional[_Union[CONSUMPTION_SEQUENCE, str]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class Family(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "vault_folder_id", "name", "print_name", "code", "description", "family_type", "hsn_sac_code", "uom_id", "unit_quantity", "parent_id", "is_leaf", "ledger_id", "tax_group_id", "price", "min_stock_to_maintain", "consumption_sequence", "amendment_count", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PRINT_NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    HSN_SAC_CODE_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    UNIT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    IS_LEAF_FIELD_NUMBER: _ClassVar[int]
    LEDGER_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    MIN_STOCK_TO_MAINTAIN_FIELD_NUMBER: _ClassVar[int]
    CONSUMPTION_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_COUNT_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    vault_folder_id: int
    name: str
    print_name: str
    code: str
    description: str
    family_type: FAMILY_TYPE
    hsn_sac_code: str
    uom_id: int
    unit_quantity: int
    parent_id: int
    is_leaf: bool
    ledger_id: int
    tax_group_id: int
    price: int
    min_stock_to_maintain: int
    consumption_sequence: CONSUMPTION_SEQUENCE
    amendment_count: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., print_name: _Optional[str] = ..., code: _Optional[str] = ..., description: _Optional[str] = ..., family_type: _Optional[_Union[FAMILY_TYPE, str]] = ..., hsn_sac_code: _Optional[str] = ..., uom_id: _Optional[int] = ..., unit_quantity: _Optional[int] = ..., parent_id: _Optional[int] = ..., is_leaf: _Optional[bool] = ..., ledger_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., price: _Optional[int] = ..., min_stock_to_maintain: _Optional[int] = ..., consumption_sequence: _Optional[_Union[CONSUMPTION_SEQUENCE, str]] = ..., amendment_count: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class FamiliesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[Family]
    def __init__(self, list: _Optional[_Iterable[_Union[Family, _Mapping]]] = ...) -> None: ...

class FamiliesServicePaginationReq(_message.Message):
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
    sort_key: FAMILY_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[FAMILY_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class FamiliesServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[Family]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[Family, _Mapping]]] = ...) -> None: ...

class FamiliesServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "multi_status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "name", "code", "family_type", "multi_family_type", "hsn_sac_code", "uom_id", "unit_quantity", "parent_id", "is_leaf", "ledger_id", "qc_group_id", "tax_group_id", "consumption_sequence", "parent_storage_id", "label_id", "form_data")
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
    MULTI_STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_START_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_END_FIELD_NUMBER: _ClassVar[int]
    APPROVED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVER_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    MULTI_FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    HSN_SAC_CODE_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    UNIT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    IS_LEAF_FIELD_NUMBER: _ClassVar[int]
    LEDGER_ID_FIELD_NUMBER: _ClassVar[int]
    QC_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    CONSUMPTION_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    PARENT_STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: FAMILY_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    multi_status: _containers.RepeatedScalarFieldContainer[_scailo_pb2.STANDARD_LIFECYCLE_STATUS]
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    name: str
    code: str
    family_type: FAMILY_TYPE
    multi_family_type: _containers.RepeatedScalarFieldContainer[FAMILY_TYPE]
    hsn_sac_code: str
    uom_id: int
    unit_quantity: int
    parent_id: int
    is_leaf: _scailo_pb2.BOOL_FILTER
    ledger_id: int
    qc_group_id: int
    tax_group_id: int
    consumption_sequence: CONSUMPTION_SEQUENCE
    parent_storage_id: int
    label_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[FAMILY_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., multi_status: _Optional[_Iterable[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., family_type: _Optional[_Union[FAMILY_TYPE, str]] = ..., multi_family_type: _Optional[_Iterable[_Union[FAMILY_TYPE, str]]] = ..., hsn_sac_code: _Optional[str] = ..., uom_id: _Optional[int] = ..., unit_quantity: _Optional[int] = ..., parent_id: _Optional[int] = ..., is_leaf: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., ledger_id: _Optional[int] = ..., qc_group_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., consumption_sequence: _Optional[_Union[CONSUMPTION_SEQUENCE, str]] = ..., parent_storage_id: _Optional[int] = ..., label_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class FamiliesServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "multi_status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "name", "code", "family_type", "multi_family_type", "hsn_sac_code", "uom_id", "unit_quantity", "parent_id", "is_leaf", "ledger_id", "qc_group_id", "tax_group_id", "consumption_sequence", "parent_storage_id", "label_id", "form_data")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MULTI_STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_START_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_END_FIELD_NUMBER: _ClassVar[int]
    APPROVED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVER_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    MULTI_FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    HSN_SAC_CODE_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    UNIT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    IS_LEAF_FIELD_NUMBER: _ClassVar[int]
    LEDGER_ID_FIELD_NUMBER: _ClassVar[int]
    QC_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    CONSUMPTION_SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    PARENT_STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    multi_status: _containers.RepeatedScalarFieldContainer[_scailo_pb2.STANDARD_LIFECYCLE_STATUS]
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    name: str
    code: str
    family_type: FAMILY_TYPE
    multi_family_type: _containers.RepeatedScalarFieldContainer[FAMILY_TYPE]
    hsn_sac_code: str
    uom_id: int
    unit_quantity: int
    parent_id: int
    is_leaf: _scailo_pb2.BOOL_FILTER
    ledger_id: int
    qc_group_id: int
    tax_group_id: int
    consumption_sequence: CONSUMPTION_SEQUENCE
    parent_storage_id: int
    label_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., multi_status: _Optional[_Iterable[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., family_type: _Optional[_Union[FAMILY_TYPE, str]] = ..., multi_family_type: _Optional[_Iterable[_Union[FAMILY_TYPE, str]]] = ..., hsn_sac_code: _Optional[str] = ..., uom_id: _Optional[int] = ..., unit_quantity: _Optional[int] = ..., parent_id: _Optional[int] = ..., is_leaf: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., ledger_id: _Optional[int] = ..., qc_group_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., consumption_sequence: _Optional[_Union[CONSUMPTION_SEQUENCE, str]] = ..., parent_storage_id: _Optional[int] = ..., label_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class FamiliesServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "multi_status", "search_key", "family_type", "multi_family_type", "parent_id", "is_leaf")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MULTI_STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    MULTI_FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    IS_LEAF_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: FAMILY_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    multi_status: _containers.RepeatedScalarFieldContainer[_scailo_pb2.STANDARD_LIFECYCLE_STATUS]
    search_key: str
    family_type: FAMILY_TYPE
    multi_family_type: _containers.RepeatedScalarFieldContainer[FAMILY_TYPE]
    parent_id: int
    is_leaf: _scailo_pb2.BOOL_FILTER
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[FAMILY_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., multi_status: _Optional[_Iterable[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]]] = ..., search_key: _Optional[str] = ..., family_type: _Optional[_Union[FAMILY_TYPE, str]] = ..., multi_family_type: _Optional[_Iterable[_Union[FAMILY_TYPE, str]]] = ..., parent_id: _Optional[int] = ..., is_leaf: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ...) -> None: ...

class FilterFamiliesReqForIdentifier(_message.Message):
    __slots__ = ("uuid", "filter")
    UUID_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    filter: FamiliesServiceFilterReq
    def __init__(self, uuid: _Optional[str] = ..., filter: _Optional[_Union[FamiliesServiceFilterReq, _Mapping]] = ...) -> None: ...

class FamiliesServiceLabelCreateRequest(_message.Message):
    __slots__ = ("user_comment", "family_id", "label_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    family_id: int
    label_id: int
    def __init__(self, user_comment: _Optional[str] = ..., family_id: _Optional[int] = ..., label_id: _Optional[int] = ...) -> None: ...

class FamilyLabel(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "family_id", "label_id")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_ID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    family_id: int
    label_id: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., family_id: _Optional[int] = ..., label_id: _Optional[int] = ...) -> None: ...

class FamilyLabelsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[FamilyLabel]
    def __init__(self, list: _Optional[_Iterable[_Union[FamilyLabel, _Mapping]]] = ...) -> None: ...

class FamiliesServiceStorageCreateRequest(_message.Message):
    __slots__ = ("user_comment", "family_id", "storage_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    family_id: int
    storage_id: int
    def __init__(self, user_comment: _Optional[str] = ..., family_id: _Optional[int] = ..., storage_id: _Optional[int] = ...) -> None: ...

class FamilyStorage(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "family_id", "storage_id")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    family_id: int
    storage_id: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., family_id: _Optional[int] = ..., storage_id: _Optional[int] = ...) -> None: ...

class FamilyStoragesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[FamilyStorage]
    def __init__(self, list: _Optional[_Iterable[_Union[FamilyStorage, _Mapping]]] = ...) -> None: ...

class FamiliesServiceUnitConversionPresenceRequest(_message.Message):
    __slots__ = ("family_id", "uom_id")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    uom_id: int
    def __init__(self, family_id: _Optional[int] = ..., uom_id: _Optional[int] = ...) -> None: ...

class FamiliesServiceUnitConversionCreateRequest(_message.Message):
    __slots__ = ("user_comment", "family_id", "uom_id", "factor", "divisor")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    FACTOR_FIELD_NUMBER: _ClassVar[int]
    DIVISOR_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    family_id: int
    uom_id: int
    factor: int
    divisor: int
    def __init__(self, user_comment: _Optional[str] = ..., family_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., factor: _Optional[int] = ..., divisor: _Optional[int] = ...) -> None: ...

class FamilyUnitConversion(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "family_id", "uom_id", "factor", "divisor")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    FACTOR_FIELD_NUMBER: _ClassVar[int]
    DIVISOR_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    family_id: int
    uom_id: int
    factor: int
    divisor: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., family_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., factor: _Optional[int] = ..., divisor: _Optional[int] = ...) -> None: ...

class FamilyUnitConversionsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[FamilyUnitConversion]
    def __init__(self, list: _Optional[_Iterable[_Union[FamilyUnitConversion, _Mapping]]] = ...) -> None: ...

class FamiliesServiceQCGroupCreateRequest(_message.Message):
    __slots__ = ("user_comment", "family_id", "qc_group_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QC_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    family_id: int
    qc_group_id: int
    def __init__(self, user_comment: _Optional[str] = ..., family_id: _Optional[int] = ..., qc_group_id: _Optional[int] = ...) -> None: ...

class FamilyQCGroup(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "family_id", "qc_group_id")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QC_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    family_id: int
    qc_group_id: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., family_id: _Optional[int] = ..., qc_group_id: _Optional[int] = ...) -> None: ...

class FamilyQCGroupsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[FamilyQCGroup]
    def __init__(self, list: _Optional[_Iterable[_Union[FamilyQCGroup, _Mapping]]] = ...) -> None: ...

class FamiliesServiceUpdatePriceRequest(_message.Message):
    __slots__ = ("user_comment", "uuid", "price")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    price: int
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ..., price: _Optional[int] = ...) -> None: ...

class FamiliesServiceUpdateMinStockToMaintainRequest(_message.Message):
    __slots__ = ("user_comment", "uuid", "min_stock_to_maintain")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    MIN_STOCK_TO_MAINTAIN_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    min_stock_to_maintain: int
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ..., min_stock_to_maintain: _Optional[int] = ...) -> None: ...
