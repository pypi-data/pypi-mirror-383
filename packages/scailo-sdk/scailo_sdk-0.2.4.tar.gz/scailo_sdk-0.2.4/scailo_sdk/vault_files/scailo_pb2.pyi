from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from vault_commons import scailo_pb2 as _scailo_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VaultFileInitiateFileRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "name", "type", "folder_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    name: str
    type: str
    folder_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., folder_uuid: _Optional[str] = ...) -> None: ...

class VaultFileInitiateFileResponse(_message.Message):
    __slots__ = ("uuid", "chunk_size")
    UUID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_SIZE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    chunk_size: int
    def __init__(self, uuid: _Optional[str] = ..., chunk_size: _Optional[int] = ...) -> None: ...

class VaultFileRenameFileRequest(_message.Message):
    __slots__ = ("uuid", "name")
    UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    name: str
    def __init__(self, uuid: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class VaultFileMoveFileRequest(_message.Message):
    __slots__ = ("uuid", "destination_folder_uuid")
    UUID_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    destination_folder_uuid: str
    def __init__(self, uuid: _Optional[str] = ..., destination_folder_uuid: _Optional[str] = ...) -> None: ...

class VaultFile(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "completed_at", "name", "type", "is_persistent", "folder_id", "path_tree", "size", "permissions", "folder_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_PERSISTENT_FIELD_NUMBER: _ClassVar[int]
    FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_TREE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    completed_at: int
    name: str
    type: str
    is_persistent: bool
    folder_id: int
    path_tree: str
    size: int
    permissions: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.VaultPermission]
    folder_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., completed_at: _Optional[int] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., is_persistent: _Optional[bool] = ..., folder_id: _Optional[int] = ..., path_tree: _Optional[str] = ..., size: _Optional[int] = ..., permissions: _Optional[_Iterable[_Union[_scailo_pb2_1.VaultPermission, _Mapping]]] = ..., folder_uuid: _Optional[str] = ...) -> None: ...

class VaultFilesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VaultFile]
    def __init__(self, list: _Optional[_Iterable[_Union[VaultFile, _Mapping]]] = ...) -> None: ...

class VaultFileVersion(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "completed_at", "vault_file_id", "name", "type", "size")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_AT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    completed_at: int
    vault_file_id: int
    name: str
    type: str
    size: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., completed_at: _Optional[int] = ..., vault_file_id: _Optional[int] = ..., name: _Optional[str] = ..., type: _Optional[str] = ..., size: _Optional[int] = ...) -> None: ...

class VaultFileVersionsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VaultFileVersion]
    def __init__(self, list: _Optional[_Iterable[_Union[VaultFileVersion, _Mapping]]] = ...) -> None: ...

class VaultFileAddChunkRequest(_message.Message):
    __slots__ = ("uuid", "sequence_id", "chunk")
    UUID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    sequence_id: int
    chunk: bytes
    def __init__(self, uuid: _Optional[str] = ..., sequence_id: _Optional[int] = ..., chunk: _Optional[bytes] = ...) -> None: ...

class VaultFileVersionChunk(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "vault_file_version_id", "sequence_id", "chunk", "checksum")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    VAULT_FILE_VERSION_ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_ID_FIELD_NUMBER: _ClassVar[int]
    CHUNK_FIELD_NUMBER: _ClassVar[int]
    CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    vault_file_version_id: int
    sequence_id: int
    chunk: bytes
    checksum: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., vault_file_version_id: _Optional[int] = ..., sequence_id: _Optional[int] = ..., chunk: _Optional[bytes] = ..., checksum: _Optional[str] = ...) -> None: ...

class VaultFileUnzipRequest(_message.Message):
    __slots__ = ("uuid", "delete_after_unzip")
    UUID_FIELD_NUMBER: _ClassVar[int]
    DELETE_AFTER_UNZIP_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    delete_after_unzip: bool
    def __init__(self, uuid: _Optional[str] = ..., delete_after_unzip: _Optional[bool] = ...) -> None: ...
