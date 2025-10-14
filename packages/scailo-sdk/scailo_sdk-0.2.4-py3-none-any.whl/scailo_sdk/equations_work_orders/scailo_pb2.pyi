from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from magic_links import scailo_pb2 as _scailo_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EQUATION_WORK_ORDER_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EQUATION_WORK_ORDER_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[EQUATION_WORK_ORDER_ITEM_SORT_KEY]
    EQUATION_WORK_ORDER_ITEM_SORT_KEY_CREATED_AT: _ClassVar[EQUATION_WORK_ORDER_ITEM_SORT_KEY]
    EQUATION_WORK_ORDER_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[EQUATION_WORK_ORDER_ITEM_SORT_KEY]
    EQUATION_WORK_ORDER_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[EQUATION_WORK_ORDER_ITEM_SORT_KEY]
    EQUATION_WORK_ORDER_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[EQUATION_WORK_ORDER_ITEM_SORT_KEY]
    EQUATION_WORK_ORDER_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[EQUATION_WORK_ORDER_ITEM_SORT_KEY]
    EQUATION_WORK_ORDER_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[EQUATION_WORK_ORDER_ITEM_SORT_KEY]
    EQUATION_WORK_ORDER_ITEM_SORT_KEY_QUANTITY: _ClassVar[EQUATION_WORK_ORDER_ITEM_SORT_KEY]
    EQUATION_WORK_ORDER_ITEM_SORT_KEY_UNIT_PRICE: _ClassVar[EQUATION_WORK_ORDER_ITEM_SORT_KEY]

class EQUATION_WORK_ORDER_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EQUATION_WORK_ORDER_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[EQUATION_WORK_ORDER_ITEM_STATUS]
    EQUATION_WORK_ORDER_ITEM_STATUS_APPROVED: _ClassVar[EQUATION_WORK_ORDER_ITEM_STATUS]
    EQUATION_WORK_ORDER_ITEM_STATUS_UNAPPROVED: _ClassVar[EQUATION_WORK_ORDER_ITEM_STATUS]

class EQUATION_WORK_ORDER_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EQUATION_WORK_ORDER_SORT_KEY_ID_UNSPECIFIED: _ClassVar[EQUATION_WORK_ORDER_SORT_KEY]
    EQUATION_WORK_ORDER_SORT_KEY_CREATED_AT: _ClassVar[EQUATION_WORK_ORDER_SORT_KEY]
    EQUATION_WORK_ORDER_SORT_KEY_MODIFIED_AT: _ClassVar[EQUATION_WORK_ORDER_SORT_KEY]
    EQUATION_WORK_ORDER_SORT_KEY_APPROVED_ON: _ClassVar[EQUATION_WORK_ORDER_SORT_KEY]
    EQUATION_WORK_ORDER_SORT_KEY_APPROVED_BY: _ClassVar[EQUATION_WORK_ORDER_SORT_KEY]
    EQUATION_WORK_ORDER_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[EQUATION_WORK_ORDER_SORT_KEY]
    EQUATION_WORK_ORDER_SORT_KEY_COMPLETED_ON: _ClassVar[EQUATION_WORK_ORDER_SORT_KEY]
    EQUATION_WORK_ORDER_SORT_KEY_NAME: _ClassVar[EQUATION_WORK_ORDER_SORT_KEY]
    EQUATION_WORK_ORDER_SORT_KEY_WORK_ORDER_ID: _ClassVar[EQUATION_WORK_ORDER_SORT_KEY]
    EQUATION_WORK_ORDER_SORT_KEY_AMENDMENT_COUNT: _ClassVar[EQUATION_WORK_ORDER_SORT_KEY]
EQUATION_WORK_ORDER_ITEM_SORT_KEY_ID_UNSPECIFIED: EQUATION_WORK_ORDER_ITEM_SORT_KEY
EQUATION_WORK_ORDER_ITEM_SORT_KEY_CREATED_AT: EQUATION_WORK_ORDER_ITEM_SORT_KEY
EQUATION_WORK_ORDER_ITEM_SORT_KEY_MODIFIED_AT: EQUATION_WORK_ORDER_ITEM_SORT_KEY
EQUATION_WORK_ORDER_ITEM_SORT_KEY_APPROVED_ON: EQUATION_WORK_ORDER_ITEM_SORT_KEY
EQUATION_WORK_ORDER_ITEM_SORT_KEY_APPROVED_BY: EQUATION_WORK_ORDER_ITEM_SORT_KEY
EQUATION_WORK_ORDER_ITEM_SORT_KEY_APPROVER_ROLE_ID: EQUATION_WORK_ORDER_ITEM_SORT_KEY
EQUATION_WORK_ORDER_ITEM_SORT_KEY_FAMILY_ID: EQUATION_WORK_ORDER_ITEM_SORT_KEY
EQUATION_WORK_ORDER_ITEM_SORT_KEY_QUANTITY: EQUATION_WORK_ORDER_ITEM_SORT_KEY
EQUATION_WORK_ORDER_ITEM_SORT_KEY_UNIT_PRICE: EQUATION_WORK_ORDER_ITEM_SORT_KEY
EQUATION_WORK_ORDER_ITEM_STATUS_ANY_UNSPECIFIED: EQUATION_WORK_ORDER_ITEM_STATUS
EQUATION_WORK_ORDER_ITEM_STATUS_APPROVED: EQUATION_WORK_ORDER_ITEM_STATUS
EQUATION_WORK_ORDER_ITEM_STATUS_UNAPPROVED: EQUATION_WORK_ORDER_ITEM_STATUS
EQUATION_WORK_ORDER_SORT_KEY_ID_UNSPECIFIED: EQUATION_WORK_ORDER_SORT_KEY
EQUATION_WORK_ORDER_SORT_KEY_CREATED_AT: EQUATION_WORK_ORDER_SORT_KEY
EQUATION_WORK_ORDER_SORT_KEY_MODIFIED_AT: EQUATION_WORK_ORDER_SORT_KEY
EQUATION_WORK_ORDER_SORT_KEY_APPROVED_ON: EQUATION_WORK_ORDER_SORT_KEY
EQUATION_WORK_ORDER_SORT_KEY_APPROVED_BY: EQUATION_WORK_ORDER_SORT_KEY
EQUATION_WORK_ORDER_SORT_KEY_APPROVER_ROLE_ID: EQUATION_WORK_ORDER_SORT_KEY
EQUATION_WORK_ORDER_SORT_KEY_COMPLETED_ON: EQUATION_WORK_ORDER_SORT_KEY
EQUATION_WORK_ORDER_SORT_KEY_NAME: EQUATION_WORK_ORDER_SORT_KEY
EQUATION_WORK_ORDER_SORT_KEY_WORK_ORDER_ID: EQUATION_WORK_ORDER_SORT_KEY
EQUATION_WORK_ORDER_SORT_KEY_AMENDMENT_COUNT: EQUATION_WORK_ORDER_SORT_KEY

class EquationsWorkOrdersServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "name", "work_order_id", "description")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    WORK_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    name: str
    work_order_id: int
    description: str
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., work_order_id: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class EquationsWorkOrdersServiceUpdateRequest(_message.Message):
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

class EquationWorkOrder(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "name", "work_order_id", "description", "list", "total_price", "amendment_count")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    WORK_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    TOTAL_PRICE_FIELD_NUMBER: _ClassVar[int]
    AMENDMENT_COUNT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    completed_on: int
    vault_folder_id: int
    name: str
    work_order_id: int
    description: str
    list: _containers.RepeatedCompositeFieldContainer[EquationWorkOrderItem]
    total_price: float
    amendment_count: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., work_order_id: _Optional[int] = ..., description: _Optional[str] = ..., list: _Optional[_Iterable[_Union[EquationWorkOrderItem, _Mapping]]] = ..., total_price: _Optional[float] = ..., amendment_count: _Optional[int] = ...) -> None: ...

class EquationsWorkOrdersServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "equation_id", "family_id", "quantity", "unit_price", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    EQUATION_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    equation_id: int
    family_id: int
    quantity: int
    unit_price: int
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., equation_id: _Optional[int] = ..., family_id: _Optional[int] = ..., quantity: _Optional[int] = ..., unit_price: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class EquationsWorkOrdersServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "quantity", "unit_price", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    quantity: int
    unit_price: int
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., quantity: _Optional[int] = ..., unit_price: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class EquationWorkOrderItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "equation_id", "family_id", "quantity", "unit_price", "specifications")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    EQUATION_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    UNIT_PRICE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    equation_id: int
    family_id: int
    quantity: int
    unit_price: int
    specifications: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., equation_id: _Optional[int] = ..., family_id: _Optional[int] = ..., quantity: _Optional[int] = ..., unit_price: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class EquationsWorkOrdersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[EquationWorkOrder]
    def __init__(self, list: _Optional[_Iterable[_Union[EquationWorkOrder, _Mapping]]] = ...) -> None: ...

class EquationsWorkOrdersItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[EquationWorkOrderItem]
    def __init__(self, list: _Optional[_Iterable[_Union[EquationWorkOrderItem, _Mapping]]] = ...) -> None: ...

class EquationWorkOrderItemHistoryRequest(_message.Message):
    __slots__ = ("equation_id", "family_id")
    EQUATION_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    equation_id: int
    family_id: int
    def __init__(self, equation_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class EquationWorkOrderItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "equation_id", "family_id", "search_key")
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
    EQUATION_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: EQUATION_WORK_ORDER_ITEM_SORT_KEY
    entity_uuid: str
    status: EQUATION_WORK_ORDER_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    equation_id: int
    family_id: int
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[EQUATION_WORK_ORDER_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[EQUATION_WORK_ORDER_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., equation_id: _Optional[int] = ..., family_id: _Optional[int] = ..., search_key: _Optional[str] = ...) -> None: ...

class EquationsWorkOrdersServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[EquationWorkOrderItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[EquationWorkOrderItem, _Mapping]]] = ...) -> None: ...

class EquationsWorkOrdersServicePaginationReq(_message.Message):
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
    sort_key: EQUATION_WORK_ORDER_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[EQUATION_WORK_ORDER_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class EquationsWorkOrdersServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[EquationWorkOrder]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[EquationWorkOrder, _Mapping]]] = ...) -> None: ...

class EquationsWorkOrdersServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "name", "work_order_id", "constituent_family_id")
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
    NAME_FIELD_NUMBER: _ClassVar[int]
    WORK_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    CONSTITUENT_FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: EQUATION_WORK_ORDER_SORT_KEY
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
    name: str
    work_order_id: int
    constituent_family_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[EQUATION_WORK_ORDER_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., name: _Optional[str] = ..., work_order_id: _Optional[int] = ..., constituent_family_id: _Optional[int] = ...) -> None: ...

class EquationsWorkOrdersServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "name", "work_order_id", "constituent_family_id")
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
    NAME_FIELD_NUMBER: _ClassVar[int]
    WORK_ORDER_ID_FIELD_NUMBER: _ClassVar[int]
    CONSTITUENT_FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
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
    name: str
    work_order_id: int
    constituent_family_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., name: _Optional[str] = ..., work_order_id: _Optional[int] = ..., constituent_family_id: _Optional[int] = ...) -> None: ...

class EquationsWorkOrdersServiceSearchAllReq(_message.Message):
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
    sort_key: EQUATION_WORK_ORDER_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[EQUATION_WORK_ORDER_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ...) -> None: ...
