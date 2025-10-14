from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VAULT_REF_FOR(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VAULT_REF_FOR_ANY_UNSPECIFIED: _ClassVar[VAULT_REF_FOR]
    VAULT_REF_FOR_FILE: _ClassVar[VAULT_REF_FOR]
    VAULT_REF_FOR_FOLDER: _ClassVar[VAULT_REF_FOR]

class VAULT_PERMISSION_CODE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VAULT_PERMISSION_CODE_VIEW_UNSPECIFIED: _ClassVar[VAULT_PERMISSION_CODE]
    VAULT_PERMISSION_CODE_META: _ClassVar[VAULT_PERMISSION_CODE]
    VAULT_PERMISSION_CODE_DOWNLOAD: _ClassVar[VAULT_PERMISSION_CODE]
    VAULT_PERMISSION_CODE_ADD: _ClassVar[VAULT_PERMISSION_CODE]
    VAULT_PERMISSION_CODE_DELETE: _ClassVar[VAULT_PERMISSION_CODE]
    VAULT_PERMISSION_CODE_EXECUTE: _ClassVar[VAULT_PERMISSION_CODE]
    VAULT_PERMISSION_CODE_ALL: _ClassVar[VAULT_PERMISSION_CODE]

class VAULT_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VAULT_SORT_KEY_ID_UNSPECIFIED: _ClassVar[VAULT_SORT_KEY]
    VAULT_SORT_KEY_CREATED_AT: _ClassVar[VAULT_SORT_KEY]
    VAULT_SORT_KEY_MODIFIED_AT: _ClassVar[VAULT_SORT_KEY]
    VAULT_SORT_KEY_NAME: _ClassVar[VAULT_SORT_KEY]

class VAULT_ACCESS_LOG_OPERATION(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VAULT_ACCESS_LOG_OPERATION_ANY_UNSPECIFIED: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_CREATE: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_MOVE: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_RENAME: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_DELETE: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_DOWNLOAD: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_UPLOAD: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_UNZIP: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_PERSISTENT: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_PERMISSIONS: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
    VAULT_ACCESS_LOG_OPERATION_EXECUTE: _ClassVar[VAULT_ACCESS_LOG_OPERATION]
VAULT_REF_FOR_ANY_UNSPECIFIED: VAULT_REF_FOR
VAULT_REF_FOR_FILE: VAULT_REF_FOR
VAULT_REF_FOR_FOLDER: VAULT_REF_FOR
VAULT_PERMISSION_CODE_VIEW_UNSPECIFIED: VAULT_PERMISSION_CODE
VAULT_PERMISSION_CODE_META: VAULT_PERMISSION_CODE
VAULT_PERMISSION_CODE_DOWNLOAD: VAULT_PERMISSION_CODE
VAULT_PERMISSION_CODE_ADD: VAULT_PERMISSION_CODE
VAULT_PERMISSION_CODE_DELETE: VAULT_PERMISSION_CODE
VAULT_PERMISSION_CODE_EXECUTE: VAULT_PERMISSION_CODE
VAULT_PERMISSION_CODE_ALL: VAULT_PERMISSION_CODE
VAULT_SORT_KEY_ID_UNSPECIFIED: VAULT_SORT_KEY
VAULT_SORT_KEY_CREATED_AT: VAULT_SORT_KEY
VAULT_SORT_KEY_MODIFIED_AT: VAULT_SORT_KEY
VAULT_SORT_KEY_NAME: VAULT_SORT_KEY
VAULT_ACCESS_LOG_OPERATION_ANY_UNSPECIFIED: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_CREATE: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_MOVE: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_RENAME: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_DELETE: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_DOWNLOAD: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_UPLOAD: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_UNZIP: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_PERSISTENT: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_PERMISSIONS: VAULT_ACCESS_LOG_OPERATION
VAULT_ACCESS_LOG_OPERATION_EXECUTE: VAULT_ACCESS_LOG_OPERATION

class VaultPermission(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "ref_for", "ref_id", "role_id", "permission_code")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    REF_FOR_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_CODE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    ref_for: VAULT_REF_FOR
    ref_id: int
    role_id: int
    permission_code: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., ref_for: _Optional[_Union[VAULT_REF_FOR, str]] = ..., ref_id: _Optional[int] = ..., role_id: _Optional[int] = ..., permission_code: _Optional[int] = ...) -> None: ...

class VaultPermissionAddRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "ref_uuid", "role_id", "permission_code")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_CODE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    ref_uuid: str
    role_id: int
    permission_code: int
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., ref_uuid: _Optional[str] = ..., role_id: _Optional[int] = ..., permission_code: _Optional[int] = ...) -> None: ...

class VaultPermissionModifyRequest(_message.Message):
    __slots__ = ("uuid", "user_comment", "permission_code")
    UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_CODE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    user_comment: str
    permission_code: int
    def __init__(self, uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., permission_code: _Optional[int] = ...) -> None: ...

class GixResources(_message.Message):
    __slots__ = ("html_entry", "logos", "external_apis")
    HTML_ENTRY_FIELD_NUMBER: _ClassVar[int]
    LOGOS_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_APIS_FIELD_NUMBER: _ClassVar[int]
    html_entry: str
    logos: _containers.RepeatedScalarFieldContainer[str]
    external_apis: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, html_entry: _Optional[str] = ..., logos: _Optional[_Iterable[str]] = ..., external_apis: _Optional[_Iterable[str]] = ...) -> None: ...

class GiXManifest(_message.Message):
    __slots__ = ("manifest_version", "app_version", "app_name", "app_unique_identifier", "min_genesis_version", "max_genesis_version", "resources")
    MANIFEST_VERSION_FIELD_NUMBER: _ClassVar[int]
    APP_VERSION_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    APP_UNIQUE_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    MIN_GENESIS_VERSION_FIELD_NUMBER: _ClassVar[int]
    MAX_GENESIS_VERSION_FIELD_NUMBER: _ClassVar[int]
    RESOURCES_FIELD_NUMBER: _ClassVar[int]
    manifest_version: str
    app_version: str
    app_name: str
    app_unique_identifier: str
    min_genesis_version: str
    max_genesis_version: str
    resources: GixResources
    def __init__(self, manifest_version: _Optional[str] = ..., app_version: _Optional[str] = ..., app_name: _Optional[str] = ..., app_unique_identifier: _Optional[str] = ..., min_genesis_version: _Optional[str] = ..., max_genesis_version: _Optional[str] = ..., resources: _Optional[_Union[GixResources, _Mapping]] = ...) -> None: ...

class GiXAppRun(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "vault_file_id", "vault_file_version_id", "app_unique_identifier", "extracted_path", "ip_addr", "manifest", "run_by", "app_version", "app_name", "app_endpoint")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    APP_UNIQUE_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    EXTRACTED_PATH_FIELD_NUMBER: _ClassVar[int]
    IP_ADDR_FIELD_NUMBER: _ClassVar[int]
    MANIFEST_FIELD_NUMBER: _ClassVar[int]
    RUN_BY_FIELD_NUMBER: _ClassVar[int]
    APP_VERSION_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    APP_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    vault_file_id: int
    vault_file_version_id: int
    app_unique_identifier: str
    extracted_path: str
    ip_addr: str
    manifest: GiXManifest
    run_by: str
    app_version: str
    app_name: str
    app_endpoint: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., vault_file_id: _Optional[int] = ..., vault_file_version_id: _Optional[int] = ..., app_unique_identifier: _Optional[str] = ..., extracted_path: _Optional[str] = ..., ip_addr: _Optional[str] = ..., manifest: _Optional[_Union[GiXManifest, _Mapping]] = ..., run_by: _Optional[str] = ..., app_version: _Optional[str] = ..., app_name: _Optional[str] = ..., app_endpoint: _Optional[str] = ...) -> None: ...

class GiXAppRunsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[GiXAppRun]
    def __init__(self, list: _Optional[_Iterable[_Union[GiXAppRun, _Mapping]]] = ...) -> None: ...

class GiXAppRunCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "vault_file_uuid", "vault_file_version_uuid", "run_by")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_UUID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_VERSION_UUID_FIELD_NUMBER: _ClassVar[int]
    RUN_BY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    vault_file_uuid: str
    vault_file_version_uuid: str
    run_by: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., vault_file_uuid: _Optional[str] = ..., vault_file_version_uuid: _Optional[str] = ..., run_by: _Optional[str] = ...) -> None: ...

class GiXAppRunFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "vault_file_uuid", "vault_file_version_uuid", "run_by")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_UUID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_VERSION_UUID_FIELD_NUMBER: _ClassVar[int]
    RUN_BY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    vault_file_uuid: str
    vault_file_version_uuid: str
    run_by: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., vault_file_uuid: _Optional[str] = ..., vault_file_version_uuid: _Optional[str] = ..., run_by: _Optional[str] = ...) -> None: ...

class VaultSearchReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "ref_for", "folder_uuid", "search_key")
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
    REF_FOR_FIELD_NUMBER: _ClassVar[int]
    FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: VAULT_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    ref_for: VAULT_REF_FOR
    folder_uuid: str
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VAULT_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., ref_for: _Optional[_Union[VAULT_REF_FOR, str]] = ..., folder_uuid: _Optional[str] = ..., search_key: _Optional[str] = ...) -> None: ...

class VaultSearchResponse(_message.Message):
    __slots__ = ("name", "type", "element_id", "element_uuid", "path", "parent_folder_uuid")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_UUID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    PARENT_FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: VAULT_REF_FOR
    element_id: int
    element_uuid: str
    path: str
    parent_folder_uuid: str
    def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[VAULT_REF_FOR, str]] = ..., element_id: _Optional[int] = ..., element_uuid: _Optional[str] = ..., path: _Optional[str] = ..., parent_folder_uuid: _Optional[str] = ...) -> None: ...

class VaultSearchResponsesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VaultSearchResponse]
    def __init__(self, list: _Optional[_Iterable[_Union[VaultSearchResponse, _Mapping]]] = ...) -> None: ...

class VaultDuplicateCheckReq(_message.Message):
    __slots__ = ("name", "folder_uuid")
    NAME_FIELD_NUMBER: _ClassVar[int]
    FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    name: str
    folder_uuid: str
    def __init__(self, name: _Optional[str] = ..., folder_uuid: _Optional[str] = ...) -> None: ...

class VaultAccessLog(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "ref_for", "ref_id", "username", "ip_addr", "operation", "comment")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    REF_FOR_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    IP_ADDR_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    ref_for: VAULT_REF_FOR
    ref_id: int
    username: str
    ip_addr: str
    operation: VAULT_ACCESS_LOG_OPERATION
    comment: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., ref_for: _Optional[_Union[VAULT_REF_FOR, str]] = ..., ref_id: _Optional[int] = ..., username: _Optional[str] = ..., ip_addr: _Optional[str] = ..., operation: _Optional[_Union[VAULT_ACCESS_LOG_OPERATION, str]] = ..., comment: _Optional[str] = ...) -> None: ...

class VaultAccessLogCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "ref_for", "ref_id", "username", "ip_addr", "operation", "comment")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    REF_FOR_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    IP_ADDR_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    ref_for: VAULT_REF_FOR
    ref_id: int
    username: str
    ip_addr: str
    operation: VAULT_ACCESS_LOG_OPERATION
    comment: str
    def __init__(self, entity_uuid: _Optional[str] = ..., ref_for: _Optional[_Union[VAULT_REF_FOR, str]] = ..., ref_id: _Optional[int] = ..., username: _Optional[str] = ..., ip_addr: _Optional[str] = ..., operation: _Optional[_Union[VAULT_ACCESS_LOG_OPERATION, str]] = ..., comment: _Optional[str] = ...) -> None: ...

class VaultAccessLogsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VaultAccessLog]
    def __init__(self, list: _Optional[_Iterable[_Union[VaultAccessLog, _Mapping]]] = ...) -> None: ...
