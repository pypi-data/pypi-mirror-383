from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from families import scailo_pb2 as _scailo_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GENERIC_INVENTORY_REF_FROM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GENERIC_INVENTORY_REF_FROM_ANY_UNSPECIFIED: _ClassVar[GENERIC_INVENTORY_REF_FROM]
    GENERIC_INVENTORY_REF_FROM_INITIAL_STOCK: _ClassVar[GENERIC_INVENTORY_REF_FROM]
    GENERIC_INVENTORY_REF_FROM_GOODS_RECEIPT: _ClassVar[GENERIC_INVENTORY_REF_FROM]
    GENERIC_INVENTORY_REF_FROM_INWARD_JOB_FREE_ISSUE_MATERIAL: _ClassVar[GENERIC_INVENTORY_REF_FROM]
    GENERIC_INVENTORY_REF_FROM_OUTWARD_JOB_FREE_ISSUE_MATERIAL: _ClassVar[GENERIC_INVENTORY_REF_FROM]
    GENERIC_INVENTORY_REF_FROM_PRODUCTION_PLAN: _ClassVar[GENERIC_INVENTORY_REF_FROM]

class INVENTORY_NODE_ORIGIN_TYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVENTORY_NODE_ORIGIN_TYPE_ANY_UNSPECIFIED: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_SALES_ORDER: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_SALES_RETURN: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_PRODUCTION_PLAN: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_WORK_ORDER_EQUATION: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_MIN_STOCK: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_GOODS_DISPATCH: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_STOCK_ISSUANCE: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_FAMILY_EQUATION: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_WORK_IN_PROGRESS: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_NET_INDENTED: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_NET_ORDERED: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_QC: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_REJECTED: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_RETURNABLE: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_REWORK: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_SCRAP: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
    INVENTORY_NODE_ORIGIN_TYPE_STORE: _ClassVar[INVENTORY_NODE_ORIGIN_TYPE]
GENERIC_INVENTORY_REF_FROM_ANY_UNSPECIFIED: GENERIC_INVENTORY_REF_FROM
GENERIC_INVENTORY_REF_FROM_INITIAL_STOCK: GENERIC_INVENTORY_REF_FROM
GENERIC_INVENTORY_REF_FROM_GOODS_RECEIPT: GENERIC_INVENTORY_REF_FROM
GENERIC_INVENTORY_REF_FROM_INWARD_JOB_FREE_ISSUE_MATERIAL: GENERIC_INVENTORY_REF_FROM
GENERIC_INVENTORY_REF_FROM_OUTWARD_JOB_FREE_ISSUE_MATERIAL: GENERIC_INVENTORY_REF_FROM
GENERIC_INVENTORY_REF_FROM_PRODUCTION_PLAN: GENERIC_INVENTORY_REF_FROM
INVENTORY_NODE_ORIGIN_TYPE_ANY_UNSPECIFIED: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_SALES_ORDER: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_SALES_RETURN: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_PRODUCTION_PLAN: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_WORK_ORDER_EQUATION: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_MIN_STOCK: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_GOODS_DISPATCH: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_STOCK_ISSUANCE: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_FAMILY_EQUATION: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_WORK_IN_PROGRESS: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_NET_INDENTED: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_NET_ORDERED: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_QC: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_REJECTED: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_RETURNABLE: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_REWORK: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_SCRAP: INVENTORY_NODE_ORIGIN_TYPE
INVENTORY_NODE_ORIGIN_TYPE_STORE: INVENTORY_NODE_ORIGIN_TYPE

class GenericInventory(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "status", "store_intake_at", "consumed_or_rejected_at", "rework_start_at", "rework_end_at", "returned_or_scrapped_at", "discarded_at", "vault_folder_id", "parent_ref_id", "ref_from", "ref_id", "family_id", "code", "internal_item_code", "hash", "quantity", "quantity_remaining", "secondary_uom_id", "secondary_quantity", "shelf_life_timestamp", "warranty_timestamp", "store_id", "storage_id", "is_qc_report_public", "location_id", "remaining_dimensions", "description", "short_url")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
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
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    status: _scailo_pb2.INVENTORY_LIFECYCLE
    store_intake_at: int
    consumed_or_rejected_at: int
    rework_start_at: int
    rework_end_at: int
    returned_or_scrapped_at: int
    discarded_at: int
    vault_folder_id: int
    parent_ref_id: int
    ref_from: GENERIC_INVENTORY_REF_FROM
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
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.INVENTORY_LIFECYCLE, str]] = ..., store_intake_at: _Optional[int] = ..., consumed_or_rejected_at: _Optional[int] = ..., rework_start_at: _Optional[int] = ..., rework_end_at: _Optional[int] = ..., returned_or_scrapped_at: _Optional[int] = ..., discarded_at: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., parent_ref_id: _Optional[int] = ..., ref_from: _Optional[_Union[GENERIC_INVENTORY_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., family_id: _Optional[int] = ..., code: _Optional[str] = ..., internal_item_code: _Optional[str] = ..., hash: _Optional[str] = ..., quantity: _Optional[int] = ..., quantity_remaining: _Optional[int] = ..., secondary_uom_id: _Optional[int] = ..., secondary_quantity: _Optional[int] = ..., shelf_life_timestamp: _Optional[int] = ..., warranty_timestamp: _Optional[int] = ..., store_id: _Optional[int] = ..., storage_id: _Optional[int] = ..., is_qc_report_public: _Optional[bool] = ..., location_id: _Optional[int] = ..., remaining_dimensions: _Optional[str] = ..., description: _Optional[str] = ..., short_url: _Optional[str] = ...) -> None: ...

class GenericInventoryList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[GenericInventory]
    def __init__(self, list: _Optional[_Iterable[_Union[GenericInventory, _Mapping]]] = ...) -> None: ...

class InventoryCodeMap(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "purpose", "family_type", "family_id", "code", "hash", "short_url")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    SHORT_URL_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    purpose: str
    family_type: _scailo_pb2_1.FAMILY_TYPE
    family_id: int
    code: str
    hash: str
    short_url: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., purpose: _Optional[str] = ..., family_type: _Optional[_Union[_scailo_pb2_1.FAMILY_TYPE, str]] = ..., family_id: _Optional[int] = ..., code: _Optional[str] = ..., hash: _Optional[str] = ..., short_url: _Optional[str] = ...) -> None: ...

class IssuableInventorySearchReq(_message.Message):
    __slots__ = ("status", "search_key", "family_id", "location_id")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    status: _scailo_pb2.INVENTORY_LIFECYCLE
    search_key: str
    family_id: int
    location_id: int
    def __init__(self, status: _Optional[_Union[_scailo_pb2.INVENTORY_LIFECYCLE, str]] = ..., search_key: _Optional[str] = ..., family_id: _Optional[int] = ..., location_id: _Optional[int] = ...) -> None: ...

class InventoryHashSearchReq(_message.Message):
    __slots__ = ("hash",)
    HASH_FIELD_NUMBER: _ClassVar[int]
    hash: str
    def __init__(self, hash: _Optional[str] = ...) -> None: ...

class InventoryServiceFamilyQuantityReq(_message.Message):
    __slots__ = ("status", "family_id")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    status: _scailo_pb2.INVENTORY_LIFECYCLE
    family_id: int
    def __init__(self, status: _Optional[_Union[_scailo_pb2.INVENTORY_LIFECYCLE, str]] = ..., family_id: _Optional[int] = ...) -> None: ...

class ReturnableInventorySearchReq(_message.Message):
    __slots__ = ("ref_id", "search_key", "family_id", "location_id")
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    ref_id: int
    search_key: str
    family_id: int
    location_id: int
    def __init__(self, ref_id: _Optional[int] = ..., search_key: _Optional[str] = ..., family_id: _Optional[int] = ..., location_id: _Optional[int] = ...) -> None: ...

class SearchReturnableInventoryReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "search_key", "family_id", "quantity_remaining_min", "quantity_remaining_max", "secondary_uom_id", "shelf_life_timestamp_start", "shelf_life_timestamp_end", "warranty_timestamp_start", "warranty_timestamp_end", "is_qc_report_public", "location_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_REMAINING_MIN_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_REMAINING_MAX_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    SHELF_LIFE_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    SHELF_LIFE_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    WARRANTY_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    WARRANTY_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    IS_QC_REPORT_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: _scailo_pb2.INVENTORY_SORT_KEY
    entity_uuid: str
    search_key: str
    family_id: int
    quantity_remaining_min: int
    quantity_remaining_max: int
    secondary_uom_id: int
    shelf_life_timestamp_start: int
    shelf_life_timestamp_end: int
    warranty_timestamp_start: int
    warranty_timestamp_end: int
    is_qc_report_public: _scailo_pb2.BOOL_FILTER
    location_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[_scailo_pb2.INVENTORY_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., search_key: _Optional[str] = ..., family_id: _Optional[int] = ..., quantity_remaining_min: _Optional[int] = ..., quantity_remaining_max: _Optional[int] = ..., secondary_uom_id: _Optional[int] = ..., shelf_life_timestamp_start: _Optional[int] = ..., shelf_life_timestamp_end: _Optional[int] = ..., warranty_timestamp_start: _Optional[int] = ..., warranty_timestamp_end: _Optional[int] = ..., is_qc_report_public: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., location_id: _Optional[int] = ...) -> None: ...

class SearchReturnableInventoryForIdentifierUUID(_message.Message):
    __slots__ = ("uuid", "filter")
    UUID_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    filter: SearchReturnableInventoryReq
    def __init__(self, uuid: _Optional[str] = ..., filter: _Optional[_Union[SearchReturnableInventoryReq, _Mapping]] = ...) -> None: ...

class FilterReturnableInventoryReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "family_id", "code", "internal_item_code", "hash", "quantity_remaining_min", "quantity_remaining_max", "secondary_uom_id", "shelf_life_timestamp_start", "shelf_life_timestamp_end", "warranty_timestamp_start", "warranty_timestamp_end", "is_qc_report_public", "location_id")
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
    IS_QC_REPORT_PUBLIC_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
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
    is_qc_report_public: _scailo_pb2.BOOL_FILTER
    location_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[_scailo_pb2.INVENTORY_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., family_id: _Optional[int] = ..., code: _Optional[str] = ..., internal_item_code: _Optional[str] = ..., hash: _Optional[str] = ..., quantity_remaining_min: _Optional[int] = ..., quantity_remaining_max: _Optional[int] = ..., secondary_uom_id: _Optional[int] = ..., shelf_life_timestamp_start: _Optional[int] = ..., shelf_life_timestamp_end: _Optional[int] = ..., warranty_timestamp_start: _Optional[int] = ..., warranty_timestamp_end: _Optional[int] = ..., is_qc_report_public: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., location_id: _Optional[int] = ...) -> None: ...

class FilterReturnableInventoryForIdentifierUUID(_message.Message):
    __slots__ = ("uuid", "filter")
    UUID_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    filter: FilterReturnableInventoryReq
    def __init__(self, uuid: _Optional[str] = ..., filter: _Optional[_Union[FilterReturnableInventoryReq, _Mapping]] = ...) -> None: ...

class ConsolidatedInventoryStatistics(_message.Message):
    __slots__ = ("family_id", "base_demand_count", "work_in_progress_count", "indented_count", "ordered_count", "qc_count", "rejected_count", "returnable_count", "rework_count", "scrap_count", "store_count", "required_count")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    BASE_DEMAND_COUNT_FIELD_NUMBER: _ClassVar[int]
    WORK_IN_PROGRESS_COUNT_FIELD_NUMBER: _ClassVar[int]
    INDENTED_COUNT_FIELD_NUMBER: _ClassVar[int]
    ORDERED_COUNT_FIELD_NUMBER: _ClassVar[int]
    QC_COUNT_FIELD_NUMBER: _ClassVar[int]
    REJECTED_COUNT_FIELD_NUMBER: _ClassVar[int]
    RETURNABLE_COUNT_FIELD_NUMBER: _ClassVar[int]
    REWORK_COUNT_FIELD_NUMBER: _ClassVar[int]
    SCRAP_COUNT_FIELD_NUMBER: _ClassVar[int]
    STORE_COUNT_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_COUNT_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    base_demand_count: int
    work_in_progress_count: int
    indented_count: int
    ordered_count: int
    qc_count: int
    rejected_count: int
    returnable_count: int
    rework_count: int
    scrap_count: int
    store_count: int
    required_count: int
    def __init__(self, family_id: _Optional[int] = ..., base_demand_count: _Optional[int] = ..., work_in_progress_count: _Optional[int] = ..., indented_count: _Optional[int] = ..., ordered_count: _Optional[int] = ..., qc_count: _Optional[int] = ..., rejected_count: _Optional[int] = ..., returnable_count: _Optional[int] = ..., rework_count: _Optional[int] = ..., scrap_count: _Optional[int] = ..., store_count: _Optional[int] = ..., required_count: _Optional[int] = ...) -> None: ...

class AbridgedProductionPlanItem(_message.Message):
    __slots__ = ("production_plan_id", "family_id", "quantity")
    PRODUCTION_PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    production_plan_id: int
    family_id: int
    quantity: int
    def __init__(self, production_plan_id: _Optional[int] = ..., family_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class AbridgedInventoryItem(_message.Message):
    __slots__ = ("family_id", "hash", "quantity")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    HASH_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    hash: str
    quantity: int
    def __init__(self, family_id: _Optional[int] = ..., hash: _Optional[str] = ..., quantity: _Optional[int] = ...) -> None: ...

class AbridgedPurchaseIndentItem(_message.Message):
    __slots__ = ("purchase_indent_id", "family_id", "quantity")
    PURCHASE_INDENT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    purchase_indent_id: int
    family_id: int
    quantity: int
    def __init__(self, purchase_indent_id: _Optional[int] = ..., family_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class AbridgedPurchaseOrderItem(_message.Message):
    __slots__ = ("purchase_order_id", "family_id", "quantity")
    PURCHASE_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    purchase_order_id: int
    family_id: int
    quantity: int
    def __init__(self, purchase_order_id: _Optional[int] = ..., family_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class AbridgedGoodsReceiptItem(_message.Message):
    __slots__ = ("goods_receipt_id", "family_id", "quantity")
    GOODS_RECEIPT_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    goods_receipt_id: int
    family_id: int
    quantity: int
    def __init__(self, goods_receipt_id: _Optional[int] = ..., family_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class AbridgedPurchaseReturnItem(_message.Message):
    __slots__ = ("purchase_return_id", "family_id", "quantity")
    PURCHASE_RETURN_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    purchase_return_id: int
    family_id: int
    quantity: int
    def __init__(self, purchase_return_id: _Optional[int] = ..., family_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class InventoryWorkInProgressStatistics(_message.Message):
    __slots__ = ("production_plans", "inventory_items")
    PRODUCTION_PLANS_FIELD_NUMBER: _ClassVar[int]
    INVENTORY_ITEMS_FIELD_NUMBER: _ClassVar[int]
    production_plans: _containers.RepeatedCompositeFieldContainer[AbridgedProductionPlanItem]
    inventory_items: _containers.RepeatedCompositeFieldContainer[AbridgedInventoryItem]
    def __init__(self, production_plans: _Optional[_Iterable[_Union[AbridgedProductionPlanItem, _Mapping]]] = ..., inventory_items: _Optional[_Iterable[_Union[AbridgedInventoryItem, _Mapping]]] = ...) -> None: ...

class InventoryIndentedStatistics(_message.Message):
    __slots__ = ("purchase_indents", "purchase_orders")
    PURCHASE_INDENTS_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_ORDERS_FIELD_NUMBER: _ClassVar[int]
    purchase_indents: _containers.RepeatedCompositeFieldContainer[AbridgedPurchaseIndentItem]
    purchase_orders: _containers.RepeatedCompositeFieldContainer[AbridgedPurchaseOrderItem]
    def __init__(self, purchase_indents: _Optional[_Iterable[_Union[AbridgedPurchaseIndentItem, _Mapping]]] = ..., purchase_orders: _Optional[_Iterable[_Union[AbridgedPurchaseOrderItem, _Mapping]]] = ...) -> None: ...

class InventoryOrderedStatistics(_message.Message):
    __slots__ = ("purchase_orders", "goods_receipts", "purchase_returns")
    PURCHASE_ORDERS_FIELD_NUMBER: _ClassVar[int]
    GOODS_RECEIPTS_FIELD_NUMBER: _ClassVar[int]
    PURCHASE_RETURNS_FIELD_NUMBER: _ClassVar[int]
    purchase_orders: _containers.RepeatedCompositeFieldContainer[AbridgedPurchaseOrderItem]
    goods_receipts: _containers.RepeatedCompositeFieldContainer[AbridgedGoodsReceiptItem]
    purchase_returns: _containers.RepeatedCompositeFieldContainer[AbridgedPurchaseReturnItem]
    def __init__(self, purchase_orders: _Optional[_Iterable[_Union[AbridgedPurchaseOrderItem, _Mapping]]] = ..., goods_receipts: _Optional[_Iterable[_Union[AbridgedGoodsReceiptItem, _Mapping]]] = ..., purchase_returns: _Optional[_Iterable[_Union[AbridgedPurchaseReturnItem, _Mapping]]] = ...) -> None: ...

class InventoryDetailedDemand(_message.Message):
    __slots__ = ("id", "uuid", "family_id", "base_demand_quantity", "adjusted_demand_quantity", "required_quantity", "demand_map", "is_active", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    BASE_DEMAND_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    ADJUSTED_DEMAND_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DEMAND_MAP_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    uuid: str
    family_id: int
    base_demand_quantity: int
    adjusted_demand_quantity: int
    required_quantity: int
    demand_map: InventoryDemandMap
    is_active: bool
    created_at: int
    def __init__(self, id: _Optional[int] = ..., uuid: _Optional[str] = ..., family_id: _Optional[int] = ..., base_demand_quantity: _Optional[int] = ..., adjusted_demand_quantity: _Optional[int] = ..., required_quantity: _Optional[int] = ..., demand_map: _Optional[_Union[InventoryDemandMap, _Mapping]] = ..., is_active: _Optional[bool] = ..., created_at: _Optional[int] = ...) -> None: ...

class InventoryDemandMap(_message.Message):
    __slots__ = ("family_id", "base_demand_list", "adjusted_demand_list", "base_demand_quantity", "adjusted_demand_quantity", "required_quantity", "is_evaluated")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    BASE_DEMAND_LIST_FIELD_NUMBER: _ClassVar[int]
    ADJUSTED_DEMAND_LIST_FIELD_NUMBER: _ClassVar[int]
    BASE_DEMAND_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    ADJUSTED_DEMAND_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    IS_EVALUATED_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    base_demand_list: _containers.RepeatedCompositeFieldContainer[InventoryDemand]
    adjusted_demand_list: _containers.RepeatedCompositeFieldContainer[InventoryDemand]
    base_demand_quantity: int
    adjusted_demand_quantity: int
    required_quantity: int
    is_evaluated: bool
    def __init__(self, family_id: _Optional[int] = ..., base_demand_list: _Optional[_Iterable[_Union[InventoryDemand, _Mapping]]] = ..., adjusted_demand_list: _Optional[_Iterable[_Union[InventoryDemand, _Mapping]]] = ..., base_demand_quantity: _Optional[int] = ..., adjusted_demand_quantity: _Optional[int] = ..., required_quantity: _Optional[int] = ..., is_evaluated: _Optional[bool] = ...) -> None: ...

class InventoryDemand(_message.Message):
    __slots__ = ("origin_type", "origin_id", "quantity", "multiplier", "total", "is_positive_quantity")
    ORIGIN_TYPE_FIELD_NUMBER: _ClassVar[int]
    ORIGIN_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    IS_POSITIVE_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    origin_type: INVENTORY_NODE_ORIGIN_TYPE
    origin_id: int
    quantity: int
    multiplier: int
    total: int
    is_positive_quantity: bool
    def __init__(self, origin_type: _Optional[_Union[INVENTORY_NODE_ORIGIN_TYPE, str]] = ..., origin_id: _Optional[int] = ..., quantity: _Optional[int] = ..., multiplier: _Optional[int] = ..., total: _Optional[int] = ..., is_positive_quantity: _Optional[bool] = ...) -> None: ...
