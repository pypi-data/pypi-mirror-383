from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ROLE_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_SORT_KEY_ID_UNSPECIFIED: _ClassVar[ROLE_SORT_KEY]
    ROLE_SORT_KEY_CREATED_AT: _ClassVar[ROLE_SORT_KEY]
    ROLE_SORT_KEY_MODIFIED_AT: _ClassVar[ROLE_SORT_KEY]
    ROLE_SORT_KEY_APPROVED_ON: _ClassVar[ROLE_SORT_KEY]
    ROLE_SORT_KEY_APPROVED_BY: _ClassVar[ROLE_SORT_KEY]
    ROLE_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[ROLE_SORT_KEY]
    ROLE_SORT_KEY_COMPLETED_ON: _ClassVar[ROLE_SORT_KEY]
    ROLE_SORT_KEY_NAME: _ClassVar[ROLE_SORT_KEY]
    ROLE_SORT_KEY_CODE: _ClassVar[ROLE_SORT_KEY]
ROLE_SORT_KEY_ID_UNSPECIFIED: ROLE_SORT_KEY
ROLE_SORT_KEY_CREATED_AT: ROLE_SORT_KEY
ROLE_SORT_KEY_MODIFIED_AT: ROLE_SORT_KEY
ROLE_SORT_KEY_APPROVED_ON: ROLE_SORT_KEY
ROLE_SORT_KEY_APPROVED_BY: ROLE_SORT_KEY
ROLE_SORT_KEY_APPROVER_ROLE_ID: ROLE_SORT_KEY
ROLE_SORT_KEY_COMPLETED_ON: ROLE_SORT_KEY
ROLE_SORT_KEY_NAME: ROLE_SORT_KEY
ROLE_SORT_KEY_CODE: ROLE_SORT_KEY

class RolesServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "name", "code", "description", "vault_access", "vault_root_folder_interactions", "http_access", "https_access", "access_list")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VAULT_ACCESS_FIELD_NUMBER: _ClassVar[int]
    VAULT_ROOT_FOLDER_INTERACTIONS_FIELD_NUMBER: _ClassVar[int]
    HTTP_ACCESS_FIELD_NUMBER: _ClassVar[int]
    HTTPS_ACCESS_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LIST_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    name: str
    code: str
    description: str
    vault_access: bool
    vault_root_folder_interactions: bool
    http_access: bool
    https_access: bool
    access_list: _containers.RepeatedCompositeFieldContainer[RolesServiceAccessCreateAndUpdateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., description: _Optional[str] = ..., vault_access: _Optional[bool] = ..., vault_root_folder_interactions: _Optional[bool] = ..., http_access: _Optional[bool] = ..., https_access: _Optional[bool] = ..., access_list: _Optional[_Iterable[_Union[RolesServiceAccessCreateAndUpdateRequest, _Mapping]]] = ...) -> None: ...

class RolesServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "name", "code", "description", "vault_access", "vault_root_folder_interactions", "http_access", "https_access", "access_list")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VAULT_ACCESS_FIELD_NUMBER: _ClassVar[int]
    VAULT_ROOT_FOLDER_INTERACTIONS_FIELD_NUMBER: _ClassVar[int]
    HTTP_ACCESS_FIELD_NUMBER: _ClassVar[int]
    HTTPS_ACCESS_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LIST_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    name: str
    code: str
    description: str
    vault_access: bool
    vault_root_folder_interactions: bool
    http_access: bool
    https_access: bool
    access_list: _containers.RepeatedCompositeFieldContainer[RolesServiceAccessCreateAndUpdateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., description: _Optional[str] = ..., vault_access: _Optional[bool] = ..., vault_root_folder_interactions: _Optional[bool] = ..., http_access: _Optional[bool] = ..., https_access: _Optional[bool] = ..., access_list: _Optional[_Iterable[_Union[RolesServiceAccessCreateAndUpdateRequest, _Mapping]]] = ...) -> None: ...

class Role(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "name", "code", "description", "vault_access", "vault_root_folder_interactions", "http_access", "https_access", "access_list")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    VAULT_ACCESS_FIELD_NUMBER: _ClassVar[int]
    VAULT_ROOT_FOLDER_INTERACTIONS_FIELD_NUMBER: _ClassVar[int]
    HTTP_ACCESS_FIELD_NUMBER: _ClassVar[int]
    HTTPS_ACCESS_FIELD_NUMBER: _ClassVar[int]
    ACCESS_LIST_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    completed_on: int
    name: str
    code: str
    description: str
    vault_access: bool
    vault_root_folder_interactions: bool
    http_access: bool
    https_access: bool
    access_list: _containers.RepeatedCompositeFieldContainer[RoleAccess]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., description: _Optional[str] = ..., vault_access: _Optional[bool] = ..., vault_root_folder_interactions: _Optional[bool] = ..., http_access: _Optional[bool] = ..., https_access: _Optional[bool] = ..., access_list: _Optional[_Iterable[_Union[RoleAccess, _Mapping]]] = ...) -> None: ...

class RolesServiceAccessCreateAndUpdateRequest(_message.Message):
    __slots__ = ("menu_uid", "is_accessible")
    MENU_UID_FIELD_NUMBER: _ClassVar[int]
    IS_ACCESSIBLE_FIELD_NUMBER: _ClassVar[int]
    menu_uid: str
    is_accessible: bool
    def __init__(self, menu_uid: _Optional[str] = ..., is_accessible: _Optional[bool] = ...) -> None: ...

class RolesServiceAccessDefinition(_message.Message):
    __slots__ = ("menu_uid", "menu_name", "menu_description")
    MENU_UID_FIELD_NUMBER: _ClassVar[int]
    MENU_NAME_FIELD_NUMBER: _ClassVar[int]
    MENU_DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    menu_uid: str
    menu_name: str
    menu_description: str
    def __init__(self, menu_uid: _Optional[str] = ..., menu_name: _Optional[str] = ..., menu_description: _Optional[str] = ...) -> None: ...

class RoleAccess(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "role_id", "menu_uid", "is_accessible")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    MENU_UID_FIELD_NUMBER: _ClassVar[int]
    IS_ACCESSIBLE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    role_id: int
    menu_uid: str
    is_accessible: bool
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., role_id: _Optional[int] = ..., menu_uid: _Optional[str] = ..., is_accessible: _Optional[bool] = ...) -> None: ...

class RolesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[Role]
    def __init__(self, list: _Optional[_Iterable[_Union[Role, _Mapping]]] = ...) -> None: ...

class RolesServicePaginationReq(_message.Message):
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
    sort_key: ROLE_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ROLE_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class RolesServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[Role]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[Role, _Mapping]]] = ...) -> None: ...

class RolesServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "name", "code")
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
    CODE_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: ROLE_SORT_KEY
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
    code: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ROLE_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ...) -> None: ...

class RolesServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "name", "code")
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
    CODE_FIELD_NUMBER: _ClassVar[int]
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
    code: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ...) -> None: ...

class RolesServiceSearchAllReq(_message.Message):
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
    sort_key: ROLE_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ROLE_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ...) -> None: ...
