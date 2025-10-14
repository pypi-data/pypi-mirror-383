from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from families import scailo_pb2 as _scailo_pb2_1
from inventory import scailo_pb2 as _scailo_pb2_1_1
from magic_links import scailo_pb2 as _scailo_pb2_1_1_1
from qc_groups import scailo_pb2 as _scailo_pb2_1_1_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class QC_SAMPLE_LIFECYCLE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QC_SAMPLE_LIFECYCLE_ANY_UNSPECIFIED: _ClassVar[QC_SAMPLE_LIFECYCLE]
    QC_SAMPLE_LIFECYCLE_OPEN: _ClassVar[QC_SAMPLE_LIFECYCLE]
    QC_SAMPLE_LIFECYCLE_FINISHED: _ClassVar[QC_SAMPLE_LIFECYCLE]
    QC_SAMPLE_LIFECYCLE_ACCEPTED: _ClassVar[QC_SAMPLE_LIFECYCLE]
    QC_SAMPLE_LIFECYCLE_ACCEPTED_WITH_DEVIATION: _ClassVar[QC_SAMPLE_LIFECYCLE]
    QC_SAMPLE_LIFECYCLE_REJECTED: _ClassVar[QC_SAMPLE_LIFECYCLE]
    QC_SAMPLE_LIFECYCLE_CANCELLED: _ClassVar[QC_SAMPLE_LIFECYCLE]

class QC_SAMPLE_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QC_SAMPLE_SORT_KEY_ID_UNSPECIFIED: _ClassVar[QC_SAMPLE_SORT_KEY]
    QC_SAMPLE_SORT_KEY_CREATED_AT: _ClassVar[QC_SAMPLE_SORT_KEY]
    QC_SAMPLE_SORT_KEY_MODIFIED_AT: _ClassVar[QC_SAMPLE_SORT_KEY]
    QC_SAMPLE_SORT_KEY_APPROVED_ON: _ClassVar[QC_SAMPLE_SORT_KEY]
    QC_SAMPLE_SORT_KEY_APPROVED_BY: _ClassVar[QC_SAMPLE_SORT_KEY]
    QC_SAMPLE_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[QC_SAMPLE_SORT_KEY]
    QC_SAMPLE_SORT_KEY_FINISHED_ON: _ClassVar[QC_SAMPLE_SORT_KEY]
    QC_SAMPLE_SORT_KEY_QC_GROUP_ID: _ClassVar[QC_SAMPLE_SORT_KEY]
    QC_SAMPLE_SORT_KEY_NAME: _ClassVar[QC_SAMPLE_SORT_KEY]

class QC_SAMPLE_PARAMETER_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    QC_SAMPLE_PARAMETER_SORT_KEY_ID_UNSPECIFIED: _ClassVar[QC_SAMPLE_PARAMETER_SORT_KEY]
    QC_SAMPLE_PARAMETER_SORT_KEY_CREATED_AT: _ClassVar[QC_SAMPLE_PARAMETER_SORT_KEY]
    QC_SAMPLE_PARAMETER_SORT_KEY_MODIFIED_AT: _ClassVar[QC_SAMPLE_PARAMETER_SORT_KEY]
    QC_SAMPLE_PARAMETER_SORT_KEY_CHECKED_BY: _ClassVar[QC_SAMPLE_PARAMETER_SORT_KEY]
    QC_SAMPLE_PARAMETER_SORT_KEY_CHECKED_AT: _ClassVar[QC_SAMPLE_PARAMETER_SORT_KEY]
    QC_SAMPLE_PARAMETER_SORT_KEY_QC_SAMPLE_ID: _ClassVar[QC_SAMPLE_PARAMETER_SORT_KEY]
    QC_SAMPLE_PARAMETER_SORT_KEY_QC_PARAM_ID: _ClassVar[QC_SAMPLE_PARAMETER_SORT_KEY]
    QC_SAMPLE_PARAMETER_SORT_KEY_UOM_ID: _ClassVar[QC_SAMPLE_PARAMETER_SORT_KEY]
QC_SAMPLE_LIFECYCLE_ANY_UNSPECIFIED: QC_SAMPLE_LIFECYCLE
QC_SAMPLE_LIFECYCLE_OPEN: QC_SAMPLE_LIFECYCLE
QC_SAMPLE_LIFECYCLE_FINISHED: QC_SAMPLE_LIFECYCLE
QC_SAMPLE_LIFECYCLE_ACCEPTED: QC_SAMPLE_LIFECYCLE
QC_SAMPLE_LIFECYCLE_ACCEPTED_WITH_DEVIATION: QC_SAMPLE_LIFECYCLE
QC_SAMPLE_LIFECYCLE_REJECTED: QC_SAMPLE_LIFECYCLE
QC_SAMPLE_LIFECYCLE_CANCELLED: QC_SAMPLE_LIFECYCLE
QC_SAMPLE_SORT_KEY_ID_UNSPECIFIED: QC_SAMPLE_SORT_KEY
QC_SAMPLE_SORT_KEY_CREATED_AT: QC_SAMPLE_SORT_KEY
QC_SAMPLE_SORT_KEY_MODIFIED_AT: QC_SAMPLE_SORT_KEY
QC_SAMPLE_SORT_KEY_APPROVED_ON: QC_SAMPLE_SORT_KEY
QC_SAMPLE_SORT_KEY_APPROVED_BY: QC_SAMPLE_SORT_KEY
QC_SAMPLE_SORT_KEY_APPROVER_ROLE_ID: QC_SAMPLE_SORT_KEY
QC_SAMPLE_SORT_KEY_FINISHED_ON: QC_SAMPLE_SORT_KEY
QC_SAMPLE_SORT_KEY_QC_GROUP_ID: QC_SAMPLE_SORT_KEY
QC_SAMPLE_SORT_KEY_NAME: QC_SAMPLE_SORT_KEY
QC_SAMPLE_PARAMETER_SORT_KEY_ID_UNSPECIFIED: QC_SAMPLE_PARAMETER_SORT_KEY
QC_SAMPLE_PARAMETER_SORT_KEY_CREATED_AT: QC_SAMPLE_PARAMETER_SORT_KEY
QC_SAMPLE_PARAMETER_SORT_KEY_MODIFIED_AT: QC_SAMPLE_PARAMETER_SORT_KEY
QC_SAMPLE_PARAMETER_SORT_KEY_CHECKED_BY: QC_SAMPLE_PARAMETER_SORT_KEY
QC_SAMPLE_PARAMETER_SORT_KEY_CHECKED_AT: QC_SAMPLE_PARAMETER_SORT_KEY
QC_SAMPLE_PARAMETER_SORT_KEY_QC_SAMPLE_ID: QC_SAMPLE_PARAMETER_SORT_KEY
QC_SAMPLE_PARAMETER_SORT_KEY_QC_PARAM_ID: QC_SAMPLE_PARAMETER_SORT_KEY
QC_SAMPLE_PARAMETER_SORT_KEY_UOM_ID: QC_SAMPLE_PARAMETER_SORT_KEY

class LogbookLogQCSampleLC(_message.Message):
    __slots__ = ("id", "is_active", "timestamp", "ref_uuid", "operation", "username", "name", "user_id", "app_comment", "user_comment")
    ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    APP_COMMENT_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    id: int
    is_active: bool
    timestamp: int
    ref_uuid: str
    operation: QC_SAMPLE_LIFECYCLE
    username: str
    name: str
    user_id: int
    app_comment: str
    user_comment: str
    def __init__(self, id: _Optional[int] = ..., is_active: _Optional[bool] = ..., timestamp: _Optional[int] = ..., ref_uuid: _Optional[str] = ..., operation: _Optional[_Union[QC_SAMPLE_LIFECYCLE, str]] = ..., username: _Optional[str] = ..., name: _Optional[str] = ..., user_id: _Optional[int] = ..., app_comment: _Optional[str] = ..., user_comment: _Optional[str] = ...) -> None: ...

class QCSamplesServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "family_id", "inventory_item_uuid", "qc_group_id", "location_id", "name_prefix", "description", "sample_count")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INVENTORY_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    QC_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_PREFIX_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_COUNT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    family_id: int
    inventory_item_uuid: str
    qc_group_id: int
    location_id: int
    name_prefix: str
    description: str
    sample_count: int
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., family_id: _Optional[int] = ..., inventory_item_uuid: _Optional[str] = ..., qc_group_id: _Optional[int] = ..., location_id: _Optional[int] = ..., name_prefix: _Optional[str] = ..., description: _Optional[str] = ..., sample_count: _Optional[int] = ...) -> None: ...

class QCSamplesServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "name", "description")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    name: str
    description: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class QCSampleAncillaryParameters(_message.Message):
    __slots__ = ("family_uuid", "inventory_item_uuid", "qc_group_uuid", "location_uuid")
    FAMILY_UUID_FIELD_NUMBER: _ClassVar[int]
    INVENTORY_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    QC_GROUP_UUID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_UUID_FIELD_NUMBER: _ClassVar[int]
    family_uuid: str
    inventory_item_uuid: str
    qc_group_uuid: str
    location_uuid: str
    def __init__(self, family_uuid: _Optional[str] = ..., inventory_item_uuid: _Optional[str] = ..., qc_group_uuid: _Optional[str] = ..., location_uuid: _Optional[str] = ...) -> None: ...

class QCSample(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "finished_on", "vault_folder_id", "family_type", "family_id", "inventory_item_uuid", "qc_group_id", "location_id", "name", "description")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    FINISHED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INVENTORY_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    QC_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: QC_SAMPLE_LIFECYCLE
    logs: _containers.RepeatedCompositeFieldContainer[LogbookLogQCSampleLC]
    finished_on: int
    vault_folder_id: int
    family_type: _scailo_pb2_1.FAMILY_TYPE
    family_id: int
    inventory_item_uuid: str
    qc_group_id: int
    location_id: int
    name: str
    description: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[QC_SAMPLE_LIFECYCLE, str]] = ..., logs: _Optional[_Iterable[_Union[LogbookLogQCSampleLC, _Mapping]]] = ..., finished_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., family_type: _Optional[_Union[_scailo_pb2_1.FAMILY_TYPE, str]] = ..., family_id: _Optional[int] = ..., inventory_item_uuid: _Optional[str] = ..., qc_group_id: _Optional[int] = ..., location_id: _Optional[int] = ..., name: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class QCSampleWithMetadata(_message.Message):
    __slots__ = ("qc_sample", "family", "qc_group", "inventory_item")
    QC_SAMPLE_FIELD_NUMBER: _ClassVar[int]
    FAMILY_FIELD_NUMBER: _ClassVar[int]
    QC_GROUP_FIELD_NUMBER: _ClassVar[int]
    INVENTORY_ITEM_FIELD_NUMBER: _ClassVar[int]
    qc_sample: QCSample
    family: _scailo_pb2_1.Family
    qc_group: _scailo_pb2_1_1_1_1.QCGroup
    inventory_item: _scailo_pb2_1_1.GenericInventory
    def __init__(self, qc_sample: _Optional[_Union[QCSample, _Mapping]] = ..., family: _Optional[_Union[_scailo_pb2_1.Family, _Mapping]] = ..., qc_group: _Optional[_Union[_scailo_pb2_1_1_1_1.QCGroup, _Mapping]] = ..., inventory_item: _Optional[_Union[_scailo_pb2_1_1.GenericInventory, _Mapping]] = ...) -> None: ...

class QCSamplesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[QCSample]
    def __init__(self, list: _Optional[_Iterable[_Union[QCSample, _Mapping]]] = ...) -> None: ...

class QCSamplesWithMetadataList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[QCSampleWithMetadata]
    def __init__(self, list: _Optional[_Iterable[_Union[QCSampleWithMetadata, _Mapping]]] = ...) -> None: ...

class QCSamplesServicePaginationReq(_message.Message):
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
    sort_key: QC_SAMPLE_SORT_KEY
    status: QC_SAMPLE_LIFECYCLE
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[QC_SAMPLE_SORT_KEY, str]] = ..., status: _Optional[_Union[QC_SAMPLE_LIFECYCLE, str]] = ...) -> None: ...

class QCSamplesServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[QCSample]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[QCSample, _Mapping]]] = ...) -> None: ...

class QCSamplesServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "finished_on_start", "finished_on_end", "family_type", "family_id", "qc_group_id", "inventory_item_uuid", "location_id", "production_plan_id", "goods_receipt_id", "inward_job_free_issue_material_id", "vendor_id", "buyer_client_id")
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
    FINISHED_ON_START_FIELD_NUMBER: _ClassVar[int]
    FINISHED_ON_END_FIELD_NUMBER: _ClassVar[int]
    FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QC_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    INVENTORY_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    GOODS_RECEIPT_ID_FIELD_NUMBER: _ClassVar[int]
    INWARD_JOB_FREE_ISSUE_MATERIAL_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: QC_SAMPLE_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: QC_SAMPLE_LIFECYCLE
    finished_on_start: int
    finished_on_end: int
    family_type: _scailo_pb2_1.FAMILY_TYPE
    family_id: int
    qc_group_id: int
    inventory_item_uuid: str
    location_id: int
    production_plan_id: int
    goods_receipt_id: int
    inward_job_free_issue_material_id: int
    vendor_id: int
    buyer_client_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[QC_SAMPLE_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[QC_SAMPLE_LIFECYCLE, str]] = ..., finished_on_start: _Optional[int] = ..., finished_on_end: _Optional[int] = ..., family_type: _Optional[_Union[_scailo_pb2_1.FAMILY_TYPE, str]] = ..., family_id: _Optional[int] = ..., qc_group_id: _Optional[int] = ..., inventory_item_uuid: _Optional[str] = ..., location_id: _Optional[int] = ..., production_plan_id: _Optional[int] = ..., goods_receipt_id: _Optional[int] = ..., inward_job_free_issue_material_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ...) -> None: ...

class QCSamplesServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "finished_on_start", "finished_on_end", "family_type", "family_id", "qc_group_id", "inventory_item_uuid", "location_id", "production_plan_id", "goods_receipt_id", "inward_job_free_issue_material_id", "vendor_id", "buyer_client_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    FINISHED_ON_START_FIELD_NUMBER: _ClassVar[int]
    FINISHED_ON_END_FIELD_NUMBER: _ClassVar[int]
    FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QC_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    INVENTORY_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    GOODS_RECEIPT_ID_FIELD_NUMBER: _ClassVar[int]
    INWARD_JOB_FREE_ISSUE_MATERIAL_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: QC_SAMPLE_LIFECYCLE
    finished_on_start: int
    finished_on_end: int
    family_type: _scailo_pb2_1.FAMILY_TYPE
    family_id: int
    qc_group_id: int
    inventory_item_uuid: str
    location_id: int
    production_plan_id: int
    goods_receipt_id: int
    inward_job_free_issue_material_id: int
    vendor_id: int
    buyer_client_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[QC_SAMPLE_LIFECYCLE, str]] = ..., finished_on_start: _Optional[int] = ..., finished_on_end: _Optional[int] = ..., family_type: _Optional[_Union[_scailo_pb2_1.FAMILY_TYPE, str]] = ..., family_id: _Optional[int] = ..., qc_group_id: _Optional[int] = ..., inventory_item_uuid: _Optional[str] = ..., location_id: _Optional[int] = ..., production_plan_id: _Optional[int] = ..., goods_receipt_id: _Optional[int] = ..., inward_job_free_issue_material_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ...) -> None: ...

class QCSamplesServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "family_type", "family_id", "qc_group_id", "inventory_item_uuid")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    FAMILY_TYPE_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QC_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    INVENTORY_ITEM_UUID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: QC_SAMPLE_SORT_KEY
    entity_uuid: str
    status: QC_SAMPLE_LIFECYCLE
    search_key: str
    family_type: _scailo_pb2_1.FAMILY_TYPE
    family_id: int
    qc_group_id: int
    inventory_item_uuid: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[QC_SAMPLE_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[QC_SAMPLE_LIFECYCLE, str]] = ..., search_key: _Optional[str] = ..., family_type: _Optional[_Union[_scailo_pb2_1.FAMILY_TYPE, str]] = ..., family_id: _Optional[int] = ..., qc_group_id: _Optional[int] = ..., inventory_item_uuid: _Optional[str] = ...) -> None: ...

class QCSamplesServiceParameterUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "number_observed_value", "text_observed_value", "description")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OBSERVED_VALUE_FIELD_NUMBER: _ClassVar[int]
    TEXT_OBSERVED_VALUE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    number_observed_value: int
    text_observed_value: str
    description: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., number_observed_value: _Optional[int] = ..., text_observed_value: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class QCSampleParameter(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "checked_by", "checked_at", "qc_sample_id", "qc_param_id", "uom_id", "number_observed_value", "text_observed_value", "is_internal", "acceptable_value_type", "number_acceptable_value", "number_relative_lower_bound", "number_relative_upper_bound", "text_acceptable_values", "text_acceptable_values_with_deviation", "text_unacceptable_values", "description")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    CHECKED_BY_FIELD_NUMBER: _ClassVar[int]
    CHECKED_AT_FIELD_NUMBER: _ClassVar[int]
    QC_SAMPLE_ID_FIELD_NUMBER: _ClassVar[int]
    QC_PARAM_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OBSERVED_VALUE_FIELD_NUMBER: _ClassVar[int]
    TEXT_OBSERVED_VALUE_FIELD_NUMBER: _ClassVar[int]
    IS_INTERNAL_FIELD_NUMBER: _ClassVar[int]
    ACCEPTABLE_VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_ACCEPTABLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_RELATIVE_LOWER_BOUND_FIELD_NUMBER: _ClassVar[int]
    NUMBER_RELATIVE_UPPER_BOUND_FIELD_NUMBER: _ClassVar[int]
    TEXT_ACCEPTABLE_VALUES_FIELD_NUMBER: _ClassVar[int]
    TEXT_ACCEPTABLE_VALUES_WITH_DEVIATION_FIELD_NUMBER: _ClassVar[int]
    TEXT_UNACCEPTABLE_VALUES_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    checked_by: str
    checked_at: int
    qc_sample_id: int
    qc_param_id: int
    uom_id: int
    number_observed_value: int
    text_observed_value: str
    is_internal: bool
    acceptable_value_type: _scailo_pb2_1_1_1_1.QC_GROUP_ITEM_ACCEPTABLE_VALUE_TYPE
    number_acceptable_value: int
    number_relative_lower_bound: int
    number_relative_upper_bound: int
    text_acceptable_values: _containers.RepeatedScalarFieldContainer[str]
    text_acceptable_values_with_deviation: _containers.RepeatedScalarFieldContainer[str]
    text_unacceptable_values: _containers.RepeatedScalarFieldContainer[str]
    description: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., checked_by: _Optional[str] = ..., checked_at: _Optional[int] = ..., qc_sample_id: _Optional[int] = ..., qc_param_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., number_observed_value: _Optional[int] = ..., text_observed_value: _Optional[str] = ..., is_internal: _Optional[bool] = ..., acceptable_value_type: _Optional[_Union[_scailo_pb2_1_1_1_1.QC_GROUP_ITEM_ACCEPTABLE_VALUE_TYPE, str]] = ..., number_acceptable_value: _Optional[int] = ..., number_relative_lower_bound: _Optional[int] = ..., number_relative_upper_bound: _Optional[int] = ..., text_acceptable_values: _Optional[_Iterable[str]] = ..., text_acceptable_values_with_deviation: _Optional[_Iterable[str]] = ..., text_unacceptable_values: _Optional[_Iterable[str]] = ..., description: _Optional[str] = ...) -> None: ...

class QCSampleParametersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[QCSampleParameter]
    def __init__(self, list: _Optional[_Iterable[_Union[QCSampleParameter, _Mapping]]] = ...) -> None: ...

class QCSampleParameterHistoryRequest(_message.Message):
    __slots__ = ("qc_sample_parameter_id",)
    QC_SAMPLE_PARAMETER_ID_FIELD_NUMBER: _ClassVar[int]
    qc_sample_parameter_id: int
    def __init__(self, qc_sample_parameter_id: _Optional[int] = ...) -> None: ...

class QCSampleParameterHistory(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "checked_by", "checked_at", "qc_sample_parameter_id", "number_observed_value", "text_observed_value", "description")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    CHECKED_BY_FIELD_NUMBER: _ClassVar[int]
    CHECKED_AT_FIELD_NUMBER: _ClassVar[int]
    QC_SAMPLE_PARAMETER_ID_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OBSERVED_VALUE_FIELD_NUMBER: _ClassVar[int]
    TEXT_OBSERVED_VALUE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    checked_by: str
    checked_at: int
    qc_sample_parameter_id: int
    number_observed_value: int
    text_observed_value: str
    description: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., checked_by: _Optional[str] = ..., checked_at: _Optional[int] = ..., qc_sample_parameter_id: _Optional[int] = ..., number_observed_value: _Optional[int] = ..., text_observed_value: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class QCSampleParameterHistoryList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[QCSampleParameterHistory]
    def __init__(self, list: _Optional[_Iterable[_Union[QCSampleParameterHistory, _Mapping]]] = ...) -> None: ...

class QCSampleParametersSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "checked_by", "checked_at_start", "checked_at_end", "qc_sample_id", "qc_param_id", "uom_id", "number_observed_value_start", "number_observed_value_end", "text_observed_value", "search_key", "production_plan_id", "goods_receipt_id", "inward_job_free_issue_material_id", "vendor_id", "family_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    CHECKED_BY_FIELD_NUMBER: _ClassVar[int]
    CHECKED_AT_START_FIELD_NUMBER: _ClassVar[int]
    CHECKED_AT_END_FIELD_NUMBER: _ClassVar[int]
    QC_SAMPLE_ID_FIELD_NUMBER: _ClassVar[int]
    QC_PARAM_ID_FIELD_NUMBER: _ClassVar[int]
    UOM_ID_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OBSERVED_VALUE_START_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OBSERVED_VALUE_END_FIELD_NUMBER: _ClassVar[int]
    TEXT_OBSERVED_VALUE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    PRODUCTION_PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    GOODS_RECEIPT_ID_FIELD_NUMBER: _ClassVar[int]
    INWARD_JOB_FREE_ISSUE_MATERIAL_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: QC_SAMPLE_PARAMETER_SORT_KEY
    entity_uuid: str
    checked_by: str
    checked_at_start: int
    checked_at_end: int
    qc_sample_id: int
    qc_param_id: int
    uom_id: int
    number_observed_value_start: int
    number_observed_value_end: int
    text_observed_value: str
    search_key: str
    production_plan_id: int
    goods_receipt_id: int
    inward_job_free_issue_material_id: int
    vendor_id: int
    family_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[QC_SAMPLE_PARAMETER_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., checked_by: _Optional[str] = ..., checked_at_start: _Optional[int] = ..., checked_at_end: _Optional[int] = ..., qc_sample_id: _Optional[int] = ..., qc_param_id: _Optional[int] = ..., uom_id: _Optional[int] = ..., number_observed_value_start: _Optional[int] = ..., number_observed_value_end: _Optional[int] = ..., text_observed_value: _Optional[str] = ..., search_key: _Optional[str] = ..., production_plan_id: _Optional[int] = ..., goods_receipt_id: _Optional[int] = ..., inward_job_free_issue_material_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class QCSamplesServicePaginatedParametersResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[QCSampleParameter]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[QCSampleParameter, _Mapping]]] = ...) -> None: ...

class QCSamplesCountStatistics(_message.Message):
    __slots__ = ("open", "finished", "accepted", "accepted_with_deviation", "rejected", "cancelled")
    OPEN_FIELD_NUMBER: _ClassVar[int]
    FINISHED_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_WITH_DEVIATION_FIELD_NUMBER: _ClassVar[int]
    REJECTED_FIELD_NUMBER: _ClassVar[int]
    CANCELLED_FIELD_NUMBER: _ClassVar[int]
    open: int
    finished: int
    accepted: int
    accepted_with_deviation: int
    rejected: int
    cancelled: int
    def __init__(self, open: _Optional[int] = ..., finished: _Optional[int] = ..., accepted: _Optional[int] = ..., accepted_with_deviation: _Optional[int] = ..., rejected: _Optional[int] = ..., cancelled: _Optional[int] = ...) -> None: ...
