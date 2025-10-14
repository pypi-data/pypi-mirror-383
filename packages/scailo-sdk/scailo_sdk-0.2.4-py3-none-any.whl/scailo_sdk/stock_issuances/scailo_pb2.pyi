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

class STOCK_ISSUANCE_REF_FROM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STOCK_ISSUANCE_REF_FROM_ANY_UNSPECIFIED: _ClassVar[STOCK_ISSUANCE_REF_FROM]
    STOCK_ISSUANCE_REF_FROM_PRODUCTION_INDENT: _ClassVar[STOCK_ISSUANCE_REF_FROM]
    STOCK_ISSUANCE_REF_FROM_ASSET_INDENT: _ClassVar[STOCK_ISSUANCE_REF_FROM]
    STOCK_ISSUANCE_REF_FROM_REPLACEABLE_INDENT: _ClassVar[STOCK_ISSUANCE_REF_FROM]

class STOCK_ISSUANCE_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STOCK_ISSUANCE_SORT_KEY_ID_UNSPECIFIED: _ClassVar[STOCK_ISSUANCE_SORT_KEY]
    STOCK_ISSUANCE_SORT_KEY_CREATED_AT: _ClassVar[STOCK_ISSUANCE_SORT_KEY]
    STOCK_ISSUANCE_SORT_KEY_MODIFIED_AT: _ClassVar[STOCK_ISSUANCE_SORT_KEY]
    STOCK_ISSUANCE_SORT_KEY_APPROVED_ON: _ClassVar[STOCK_ISSUANCE_SORT_KEY]
    STOCK_ISSUANCE_SORT_KEY_APPROVED_BY: _ClassVar[STOCK_ISSUANCE_SORT_KEY]
    STOCK_ISSUANCE_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[STOCK_ISSUANCE_SORT_KEY]
    STOCK_ISSUANCE_SORT_KEY_COMPLETED_ON: _ClassVar[STOCK_ISSUANCE_SORT_KEY]
    STOCK_ISSUANCE_SORT_KEY_REFERENCE_ID: _ClassVar[STOCK_ISSUANCE_SORT_KEY]
    STOCK_ISSUANCE_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[STOCK_ISSUANCE_SORT_KEY]

class STOCK_ISSUANCE_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STOCK_ISSUANCE_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[STOCK_ISSUANCE_ITEM_SORT_KEY]
    STOCK_ISSUANCE_ITEM_SORT_KEY_CREATED_AT: _ClassVar[STOCK_ISSUANCE_ITEM_SORT_KEY]
    STOCK_ISSUANCE_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[STOCK_ISSUANCE_ITEM_SORT_KEY]
    STOCK_ISSUANCE_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[STOCK_ISSUANCE_ITEM_SORT_KEY]
    STOCK_ISSUANCE_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[STOCK_ISSUANCE_ITEM_SORT_KEY]
    STOCK_ISSUANCE_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[STOCK_ISSUANCE_ITEM_SORT_KEY]
    STOCK_ISSUANCE_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[STOCK_ISSUANCE_ITEM_SORT_KEY]
    STOCK_ISSUANCE_ITEM_SORT_KEY_INTERNAL_QUANTITY: _ClassVar[STOCK_ISSUANCE_ITEM_SORT_KEY]

class STOCK_ISSUANCE_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STOCK_ISSUANCE_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[STOCK_ISSUANCE_ITEM_STATUS]
    STOCK_ISSUANCE_ITEM_STATUS_APPROVED: _ClassVar[STOCK_ISSUANCE_ITEM_STATUS]
    STOCK_ISSUANCE_ITEM_STATUS_UNAPPROVED: _ClassVar[STOCK_ISSUANCE_ITEM_STATUS]
STOCK_ISSUANCE_REF_FROM_ANY_UNSPECIFIED: STOCK_ISSUANCE_REF_FROM
STOCK_ISSUANCE_REF_FROM_PRODUCTION_INDENT: STOCK_ISSUANCE_REF_FROM
STOCK_ISSUANCE_REF_FROM_ASSET_INDENT: STOCK_ISSUANCE_REF_FROM
STOCK_ISSUANCE_REF_FROM_REPLACEABLE_INDENT: STOCK_ISSUANCE_REF_FROM
STOCK_ISSUANCE_SORT_KEY_ID_UNSPECIFIED: STOCK_ISSUANCE_SORT_KEY
STOCK_ISSUANCE_SORT_KEY_CREATED_AT: STOCK_ISSUANCE_SORT_KEY
STOCK_ISSUANCE_SORT_KEY_MODIFIED_AT: STOCK_ISSUANCE_SORT_KEY
STOCK_ISSUANCE_SORT_KEY_APPROVED_ON: STOCK_ISSUANCE_SORT_KEY
STOCK_ISSUANCE_SORT_KEY_APPROVED_BY: STOCK_ISSUANCE_SORT_KEY
STOCK_ISSUANCE_SORT_KEY_APPROVER_ROLE_ID: STOCK_ISSUANCE_SORT_KEY
STOCK_ISSUANCE_SORT_KEY_COMPLETED_ON: STOCK_ISSUANCE_SORT_KEY
STOCK_ISSUANCE_SORT_KEY_REFERENCE_ID: STOCK_ISSUANCE_SORT_KEY
STOCK_ISSUANCE_SORT_KEY_FINAL_REF_NUMBER: STOCK_ISSUANCE_SORT_KEY
STOCK_ISSUANCE_ITEM_SORT_KEY_ID_UNSPECIFIED: STOCK_ISSUANCE_ITEM_SORT_KEY
STOCK_ISSUANCE_ITEM_SORT_KEY_CREATED_AT: STOCK_ISSUANCE_ITEM_SORT_KEY
STOCK_ISSUANCE_ITEM_SORT_KEY_MODIFIED_AT: STOCK_ISSUANCE_ITEM_SORT_KEY
STOCK_ISSUANCE_ITEM_SORT_KEY_APPROVED_ON: STOCK_ISSUANCE_ITEM_SORT_KEY
STOCK_ISSUANCE_ITEM_SORT_KEY_APPROVED_BY: STOCK_ISSUANCE_ITEM_SORT_KEY
STOCK_ISSUANCE_ITEM_SORT_KEY_APPROVER_ROLE_ID: STOCK_ISSUANCE_ITEM_SORT_KEY
STOCK_ISSUANCE_ITEM_SORT_KEY_FAMILY_ID: STOCK_ISSUANCE_ITEM_SORT_KEY
STOCK_ISSUANCE_ITEM_SORT_KEY_INTERNAL_QUANTITY: STOCK_ISSUANCE_ITEM_SORT_KEY
STOCK_ISSUANCE_ITEM_STATUS_ANY_UNSPECIFIED: STOCK_ISSUANCE_ITEM_STATUS
STOCK_ISSUANCE_ITEM_STATUS_APPROVED: STOCK_ISSUANCE_ITEM_STATUS
STOCK_ISSUANCE_ITEM_STATUS_UNAPPROVED: STOCK_ISSUANCE_ITEM_STATUS

class StockIssuancesServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "ref_from", "ref_id", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    ref_from: STOCK_ISSUANCE_REF_FROM
    ref_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., ref_from: _Optional[_Union[STOCK_ISSUANCE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class StockIssuancesServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class StockIssuancesServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid", "split_into_unit_quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    SPLIT_INTO_UNIT_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    split_into_unit_quantity: bool
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ..., split_into_unit_quantity: _Optional[bool] = ...) -> None: ...

class StockIssuance(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "ref_from", "ref_id", "location_id", "list", "form_data")
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
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
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
    ref_from: STOCK_ISSUANCE_REF_FROM
    ref_id: int
    location_id: int
    list: _containers.RepeatedCompositeFieldContainer[StockIssuanceItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[STOCK_ISSUANCE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., location_id: _Optional[int] = ..., list: _Optional[_Iterable[_Union[StockIssuanceItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class StockIssuancesServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "stock_issuance_id", "family_id", "internal_quantity", "item_hash")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    STOCK_ISSUANCE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    stock_issuance_id: int
    family_id: int
    internal_quantity: int
    item_hash: str
    def __init__(self, user_comment: _Optional[str] = ..., stock_issuance_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., item_hash: _Optional[str] = ...) -> None: ...

class StockIssuancesServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "internal_quantity", "item_hash")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    internal_quantity: int
    item_hash: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., item_hash: _Optional[str] = ...) -> None: ...

class StockIssuanceItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "stock_issuance_id", "family_id", "internal_quantity", "item_hash")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    STOCK_ISSUANCE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    stock_issuance_id: int
    family_id: int
    internal_quantity: int
    item_hash: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., stock_issuance_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., item_hash: _Optional[str] = ...) -> None: ...

class StockIssuancesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[StockIssuance]
    def __init__(self, list: _Optional[_Iterable[_Union[StockIssuance, _Mapping]]] = ...) -> None: ...

class StockIssuancesItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[StockIssuanceItem]
    def __init__(self, list: _Optional[_Iterable[_Union[StockIssuanceItem, _Mapping]]] = ...) -> None: ...

class StockIssuanceItemHistoryRequest(_message.Message):
    __slots__ = ("stock_issuance_id", "family_id")
    STOCK_ISSUANCE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    stock_issuance_id: int
    family_id: int
    def __init__(self, stock_issuance_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class StockIssuanceItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("stock_issuance_id", "family_id")
    STOCK_ISSUANCE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    stock_issuance_id: int
    family_id: int
    def __init__(self, stock_issuance_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class StockIssuancesServiceAlreadyAddedQuantityForSourceRequest(_message.Message):
    __slots__ = ("ref_from", "ref_id", "family_id")
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ref_from: STOCK_ISSUANCE_REF_FROM
    ref_id: int
    family_id: int
    def __init__(self, ref_from: _Optional[_Union[STOCK_ISSUANCE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class StockIssuancesServicePaginationReq(_message.Message):
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
    sort_key: STOCK_ISSUANCE_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[STOCK_ISSUANCE_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class StockIssuancesServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[StockIssuance]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[StockIssuance, _Mapping]]] = ...) -> None: ...

class StockIssuancesServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "location_id", "family_id", "form_data")
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
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: STOCK_ISSUANCE_SORT_KEY
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
    ref_from: STOCK_ISSUANCE_REF_FROM
    ref_id: int
    location_id: int
    family_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[STOCK_ISSUANCE_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[STOCK_ISSUANCE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., location_id: _Optional[int] = ..., family_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class StockIssuancesServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "location_id", "family_id", "form_data")
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
    LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
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
    completed_on_start: int
    completed_on_end: int
    reference_id: str
    final_ref_number: str
    ref_from: STOCK_ISSUANCE_REF_FROM
    ref_id: int
    location_id: int
    family_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[_Union[STOCK_ISSUANCE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., location_id: _Optional[int] = ..., family_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class StockIssuancesServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "ref_from", "ref_id")
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
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: STOCK_ISSUANCE_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    ref_from: STOCK_ISSUANCE_REF_FROM
    ref_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[STOCK_ISSUANCE_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., ref_from: _Optional[_Union[STOCK_ISSUANCE_REF_FROM, str]] = ..., ref_id: _Optional[int] = ...) -> None: ...

class StockIssuanceItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "stock_issuance_id", "family_id", "item_hash", "search_key")
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
    STOCK_ISSUANCE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: STOCK_ISSUANCE_ITEM_SORT_KEY
    entity_uuid: str
    status: STOCK_ISSUANCE_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    stock_issuance_id: int
    family_id: int
    item_hash: str
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[STOCK_ISSUANCE_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[STOCK_ISSUANCE_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., stock_issuance_id: _Optional[int] = ..., family_id: _Optional[int] = ..., item_hash: _Optional[str] = ..., search_key: _Optional[str] = ...) -> None: ...

class StockIssuancesServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[StockIssuanceItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[StockIssuanceItem, _Mapping]]] = ...) -> None: ...
