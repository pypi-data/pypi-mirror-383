from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from vault_commons import scailo_pb2 as _scailo_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VaultFolderAddRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "name", "parent_folder_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    name: str
    parent_folder_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., name: _Optional[str] = ..., parent_folder_uuid: _Optional[str] = ...) -> None: ...

class VaultFolderMoveFolderRequest(_message.Message):
    __slots__ = ("source_folder_uuid", "destination_folder_uuid")
    SOURCE_FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    source_folder_uuid: str
    destination_folder_uuid: str
    def __init__(self, source_folder_uuid: _Optional[str] = ..., destination_folder_uuid: _Optional[str] = ...) -> None: ...

class VaultFolderRenameFolderRequest(_message.Message):
    __slots__ = ("uuid", "name")
    UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    name: str
    def __init__(self, uuid: _Optional[str] = ..., name: _Optional[str] = ...) -> None: ...

class VaultParentFolder(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "name", "parent_folder_id", "path_tree", "permissions", "parent_folder_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_TREE_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    PARENT_FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    name: str
    parent_folder_id: int
    path_tree: str
    permissions: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.VaultPermission]
    parent_folder_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., name: _Optional[str] = ..., parent_folder_id: _Optional[int] = ..., path_tree: _Optional[str] = ..., permissions: _Optional[_Iterable[_Union[_scailo_pb2_1.VaultPermission, _Mapping]]] = ..., parent_folder_uuid: _Optional[str] = ...) -> None: ...

class VaultFolder(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "name", "parent_folder_id", "path_tree", "permissions", "parent_folders", "parent_folder_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_TREE_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    PARENT_FOLDERS_FIELD_NUMBER: _ClassVar[int]
    PARENT_FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    name: str
    parent_folder_id: int
    path_tree: str
    permissions: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.VaultPermission]
    parent_folders: _containers.RepeatedCompositeFieldContainer[VaultParentFolder]
    parent_folder_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., name: _Optional[str] = ..., parent_folder_id: _Optional[int] = ..., path_tree: _Optional[str] = ..., permissions: _Optional[_Iterable[_Union[_scailo_pb2_1.VaultPermission, _Mapping]]] = ..., parent_folders: _Optional[_Iterable[_Union[VaultParentFolder, _Mapping]]] = ..., parent_folder_uuid: _Optional[str] = ...) -> None: ...

class VaultFoldersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VaultFolder]
    def __init__(self, list: _Optional[_Iterable[_Union[VaultFolder, _Mapping]]] = ...) -> None: ...

class VaultFolderDownload(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "folder_id", "zip_file_path", "is_zipped", "requested_by", "download_started_at", "download_ended_at", "downloaded_by", "error")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    ZIP_FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    IS_ZIPPED_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_BY_FIELD_NUMBER: _ClassVar[int]
    DOWNLOAD_STARTED_AT_FIELD_NUMBER: _ClassVar[int]
    DOWNLOAD_ENDED_AT_FIELD_NUMBER: _ClassVar[int]
    DOWNLOADED_BY_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    folder_id: int
    zip_file_path: str
    is_zipped: bool
    requested_by: str
    download_started_at: int
    download_ended_at: int
    downloaded_by: str
    error: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., folder_id: _Optional[int] = ..., zip_file_path: _Optional[str] = ..., is_zipped: _Optional[bool] = ..., requested_by: _Optional[str] = ..., download_started_at: _Optional[int] = ..., download_ended_at: _Optional[int] = ..., downloaded_by: _Optional[str] = ..., error: _Optional[str] = ...) -> None: ...
