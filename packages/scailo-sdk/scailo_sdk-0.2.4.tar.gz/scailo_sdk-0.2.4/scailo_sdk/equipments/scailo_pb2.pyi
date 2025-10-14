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

class EQUIPMENT_REF_FROM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EQUIPMENT_REF_FROM_ANY_UNSPECIFIED: _ClassVar[EQUIPMENT_REF_FROM]
    EQUIPMENT_REF_FROM_INITIAL_STOCK: _ClassVar[EQUIPMENT_REF_FROM]
    EQUIPMENT_REF_FROM_GOODS_RECEIPT: _ClassVar[EQUIPMENT_REF_FROM]
    EQUIPMENT_REF_FROM_INWARD_JOB_FREE_ISSUE_MATERIAL: _ClassVar[EQUIPMENT_REF_FROM]
EQUIPMENT_REF_FROM_ANY_UNSPECIFIED: EQUIPMENT_REF_FROM
EQUIPMENT_REF_FROM_INITIAL_STOCK: EQUIPMENT_REF_FROM
EQUIPMENT_REF_FROM_GOODS_RECEIPT: EQUIPMENT_REF_FROM
EQUIPMENT_REF_FROM_INWARD_JOB_FREE_ISSUE_MATERIAL: EQUIPMENT_REF_FROM

class EquipmentsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "ref_from", "ref_id", "family_id", "internal_item_code", "quantity", "secondary_uom_id", "secondary_quantity", "shelf_life_timestamp", "warranty_timestamp", "location_id", "description", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_ITEM_CODE_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SHELF_LIFE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WARRANTY_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    ref_from: EQUIPMENT_REF_FROM
    ref_id: int
    family_id: int
    internal_item_code: str
    quantity: int
    secondary_uom_id: int
    secondary_quantity: int
    shelf_life_timestamp: int
    warranty_timestamp: int
    location_id: int
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., ref_from: _Optional[_Union[EQUIPMENT_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_item_code: _Optional[str] = ..., quantity: _Optional[int] = ..., secondary_uom_id: _Optional[int] = ..., secondary_quantity: _Optional[int] = ..., shelf_life_timestamp: _Optional[int] = ..., warranty_timestamp: _Optional[int] = ..., location_id: _Optional[int] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class EquipmentsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "internal_item_code", "secondary_uom_id", "secondary_quantity", "shelf_life_timestamp", "warranty_timestamp", "storage_id", "is_qc_report_public", "remaining_dimensions", "description", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_ITEM_CODE_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SHELF_LIFE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WARRANTY_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    IS_QC_REPORT_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    REMAINING_DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    internal_item_code: str
    secondary_uom_id: int
    secondary_quantity: int
    shelf_life_timestamp: int
    warranty_timestamp: int
    storage_id: int
    is_qc_report_public: bool
    remaining_dimensions: str
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., internal_item_code: _Optional[str] = ..., secondary_uom_id: _Optional[int] = ..., secondary_quantity: _Optional[int] = ..., shelf_life_timestamp: _Optional[int] = ..., warranty_timestamp: _Optional[int] = ..., storage_id: _Optional[int] = ..., is_qc_report_public: _Optional[bool] = ..., remaining_dimensions: _Optional[str] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class EquipmentsServiceSendToStoreRequest(_message.Message):
    __slots__ = ("user_comment", "id", "shelf_life_timestamp", "warranty_timestamp", "store_id", "storage_id", "is_qc_report_public", "remaining_dimensions", "description")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    SHELF_LIFE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WARRANTY_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STORE_ID_FIELD_NUMBER: _ClassVar[int]
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    IS_QC_REPORT_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    REMAINING_DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    shelf_life_timestamp: int
    warranty_timestamp: int
    store_id: int
    storage_id: int
    is_qc_report_public: bool
    remaining_dimensions: str
    description: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., shelf_life_timestamp: _Optional[int] = ..., warranty_timestamp: _Optional[int] = ..., store_id: _Optional[int] = ..., storage_id: _Optional[int] = ..., is_qc_report_public: _Optional[bool] = ..., remaining_dimensions: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class Equipment(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "status", "logs", "store_intake_at", "consumed_or_rejected_at", "rework_start_at", "rework_end_at", "returned_or_scrapped_at", "discarded_at", "vault_folder_id", "parent_ref_id", "ref_from", "ref_id", "family_id", "code", "internal_item_code", "hash", "quantity", "quantity_remaining", "secondary_uom_id", "secondary_quantity", "shelf_life_timestamp", "warranty_timestamp", "store_id", "storage_id", "is_qc_report_public", "location_id", "remaining_dimensions", "description", "short_url", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    STORE_INTAKE_AT_FIELD_NUMBER: _ClassVar[int]
    CONSUMED_OR_REJECTED_AT_FIELD_NUMBER: _ClassVar[int]
    REWORK_START_AT_FIELD_NUMBER: _ClassVar[int]
    REWORK_END_AT_FIELD_NUMBER: _ClassVar[int]
    RETURNED_OR_SCRAPPED_AT_FIELD_NUMBER: _ClassVar[int]
    DISCARDED_AT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_REF_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_ITEM_CODE_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_REMAINING_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SHELF_LIFE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    WARRANTY_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    STORE_ID_FIELD_NUMBER: _ClassVar[int]
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    IS_QC_REPORT_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    REMAINING_DIMENSIONS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SHORT_URL_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    status: _scailo_pb2.INVENTORY_LIFECYCLE
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogInventoryLC]
    store_intake_at: int
    consumed_or_rejected_at: int
    rework_start_at: int
    rework_end_at: int
    returned_or_scrapped_at: int
    discarded_at: int
    vault_folder_id: int
    parent_ref_id: int
    ref_from: EQUIPMENT_REF_FROM
    ref_id: int
    family_id: int
    code: str
    internal_item_code: str
    hash: str
    quantity: int
    quantity_remaining: int
    secondary_uom_id: int
    secondary_quantity: int
    shelf_life_timestamp: int
    warranty_timestamp: int
    store_id: int
    storage_id: int
    is_qc_report_public: bool
    location_id: int
    remaining_dimensions: str
    description: str
    short_url: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.INVENTORY_LIFECYCLE, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogInventoryLC, _Mapping]]] = ..., store_intake_at: _Optional[int] = ..., consumed_or_rejected_at: _Optional[int] = ..., rework_start_at: _Optional[int] = ..., rework_end_at: _Optional[int] = ..., returned_or_scrapped_at: _Optional[int] = ..., discarded_at: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., parent_ref_id: _Optional[int] = ..., ref_from: _Optional[_Union[EQUIPMENT_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., family_id: _Optional[int] = ..., code: _Optional[str] = ..., internal_item_code: _Optional[str] = ..., hash: _Optional[str] = ..., quantity: _Optional[int] = ..., quantity_remaining: _Optional[int] = ..., secondary_uom_id: _Optional[int] = ..., secondary_quantity: _Optional[int] = ..., shelf_life_timestamp: _Optional[int] = ..., warranty_timestamp: _Optional[int] = ..., store_id: _Optional[int] = ..., storage_id: _Optional[int] = ..., is_qc_report_public: _Optional[bool] = ..., location_id: _Optional[int] = ..., remaining_dimensions: _Optional[str] = ..., description: _Optional[str] = ..., short_url: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class EquipmentsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[Equipment]
    def __init__(self, list: _Optional[_Iterable[_Union[Equipment, _Mapping]]] = ...) -> None: ...

class EquipmentsServicePaginationReq(_message.Message):
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
    sort_key: _scailo_pb2.INVENTORY_SORT_KEY
    status: _scailo_pb2.INVENTORY_LIFECYCLE
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[_scailo_pb2.INVENTORY_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.INVENTORY_LIFECYCLE, str]] = ...) -> None: ...

class EquipmentsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[Equipment]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[Equipment, _Mapping]]] = ...) -> None: ...

class EquipmentsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "store_intake_at_start", "store_intake_at_end", "discarded_at_start", "discarded_at_end", "parent_ref_id", "ref_from", "ref_id", "family_id", "code", "internal_item_code", "hash", "quantity_remaining_min", "quantity_remaining_max", "secondary_uom_id", "shelf_life_timestamp_start", "shelf_life_timestamp_end", "warranty_timestamp_start", "warranty_timestamp_end", "store_id", "storage_id", "is_qc_report_public", "location_id", "vendor_id", "form_data")
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
    STORE_INTAKE_AT_START_FIELD_NUMBER: _ClassVar[int]
    STORE_INTAKE_AT_END_FIELD_NUMBER: _ClassVar[int]
    DISCARDED_AT_START_FIELD_NUMBER: _ClassVar[int]
    DISCARDED_AT_END_FIELD_NUMBER: _ClassVar[int]
    PARENT_REF_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_ITEM_CODE_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_REMAINING_MIN_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_REMAINING_MAX_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    SHELF_LIFE_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    SHELF_LIFE_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    WARRANTY_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    WARRANTY_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    STORE_ID_FIELD_NUMBER: _ClassVar[int]
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    IS_QC_REPORT_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: _scailo_pb2.INVENTORY_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: _scailo_pb2.INVENTORY_LIFECYCLE
    store_intake_at_start: int
    store_intake_at_end: int
    discarded_at_start: int
    discarded_at_end: int
    parent_ref_id: int
    ref_from: EQUIPMENT_REF_FROM
    ref_id: int
    family_id: int
    code: str
    internal_item_code: str
    hash: str
    quantity_remaining_min: int
    quantity_remaining_max: int
    secondary_uom_id: int
    shelf_life_timestamp_start: int
    shelf_life_timestamp_end: int
    warranty_timestamp_start: int
    warranty_timestamp_end: int
    store_id: int
    storage_id: int
    is_qc_report_public: _scailo_pb2.BOOL_FILTER
    location_id: int
    vendor_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[_scailo_pb2.INVENTORY_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.INVENTORY_LIFECYCLE, str]] = ..., store_intake_at_start: _Optional[int] = ..., store_intake_at_end: _Optional[int] = ..., discarded_at_start: _Optional[int] = ..., discarded_at_end: _Optional[int] = ..., parent_ref_id: _Optional[int] = ..., ref_from: _Optional[_Union[EQUIPMENT_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., family_id: _Optional[int] = ..., code: _Optional[str] = ..., internal_item_code: _Optional[str] = ..., hash: _Optional[str] = ..., quantity_remaining_min: _Optional[int] = ..., quantity_remaining_max: _Optional[int] = ..., secondary_uom_id: _Optional[int] = ..., shelf_life_timestamp_start: _Optional[int] = ..., shelf_life_timestamp_end: _Optional[int] = ..., warranty_timestamp_start: _Optional[int] = ..., warranty_timestamp_end: _Optional[int] = ..., store_id: _Optional[int] = ..., storage_id: _Optional[int] = ..., is_qc_report_public: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class EquipmentsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "store_intake_at_start", "store_intake_at_end", "discarded_at_start", "discarded_at_end", "parent_ref_id", "ref_from", "ref_id", "family_id", "code", "internal_item_code", "hash", "quantity_remaining_min", "quantity_remaining_max", "secondary_uom_id", "shelf_life_timestamp_start", "shelf_life_timestamp_end", "warranty_timestamp_start", "warranty_timestamp_end", "store_id", "storage_id", "is_qc_report_public", "location_id", "vendor_id", "form_data")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STORE_INTAKE_AT_START_FIELD_NUMBER: _ClassVar[int]
    STORE_INTAKE_AT_END_FIELD_NUMBER: _ClassVar[int]
    DISCARDED_AT_START_FIELD_NUMBER: _ClassVar[int]
    DISCARDED_AT_END_FIELD_NUMBER: _ClassVar[int]
    PARENT_REF_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_ITEM_CODE_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_REMAINING_MIN_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_REMAINING_MAX_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    SHELF_LIFE_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    SHELF_LIFE_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    WARRANTY_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    WARRANTY_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    STORE_ID_FIELD_NUMBER: _ClassVar[int]
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    IS_QC_REPORT_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: _scailo_pb2.INVENTORY_LIFECYCLE
    store_intake_at_start: int
    store_intake_at_end: int
    discarded_at_start: int
    discarded_at_end: int
    parent_ref_id: int
    ref_from: EQUIPMENT_REF_FROM
    ref_id: int
    family_id: int
    code: str
    internal_item_code: str
    hash: str
    quantity_remaining_min: int
    quantity_remaining_max: int
    secondary_uom_id: int
    shelf_life_timestamp_start: int
    shelf_life_timestamp_end: int
    warranty_timestamp_start: int
    warranty_timestamp_end: int
    store_id: int
    storage_id: int
    is_qc_report_public: _scailo_pb2.BOOL_FILTER
    location_id: int
    vendor_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.INVENTORY_LIFECYCLE, str]] = ..., store_intake_at_start: _Optional[int] = ..., store_intake_at_end: _Optional[int] = ..., discarded_at_start: _Optional[int] = ..., discarded_at_end: _Optional[int] = ..., parent_ref_id: _Optional[int] = ..., ref_from: _Optional[_Union[EQUIPMENT_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., family_id: _Optional[int] = ..., code: _Optional[str] = ..., internal_item_code: _Optional[str] = ..., hash: _Optional[str] = ..., quantity_remaining_min: _Optional[int] = ..., quantity_remaining_max: _Optional[int] = ..., secondary_uom_id: _Optional[int] = ..., shelf_life_timestamp_start: _Optional[int] = ..., shelf_life_timestamp_end: _Optional[int] = ..., warranty_timestamp_start: _Optional[int] = ..., warranty_timestamp_end: _Optional[int] = ..., store_id: _Optional[int] = ..., storage_id: _Optional[int] = ..., is_qc_report_public: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class EquipmentsServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "parent_ref_id", "ref_from", "ref_id", "family_id", "secondary_uom_id", "store_id", "storage_id", "is_qc_report_public", "location_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    PARENT_REF_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    STORE_ID_FIELD_NUMBER: _ClassVar[int]
    STORAGE_ID_FIELD_NUMBER: _ClassVar[int]
    IS_QC_REPORT_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: _scailo_pb2.INVENTORY_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.INVENTORY_LIFECYCLE
    search_key: str
    parent_ref_id: int
    ref_from: EQUIPMENT_REF_FROM
    ref_id: int
    family_id: int
    secondary_uom_id: int
    store_id: int
    storage_id: int
    is_qc_report_public: _scailo_pb2.BOOL_FILTER
    location_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[_scailo_pb2.INVENTORY_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.INVENTORY_LIFECYCLE, str]] = ..., search_key: _Optional[str] = ..., parent_ref_id: _Optional[int] = ..., ref_from: _Optional[_Union[EQUIPMENT_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., family_id: _Optional[int] = ..., secondary_uom_id: _Optional[int] = ..., store_id: _Optional[int] = ..., storage_id: _Optional[int] = ..., is_qc_report_public: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., location_id: _Optional[int] = ...) -> None: ...
