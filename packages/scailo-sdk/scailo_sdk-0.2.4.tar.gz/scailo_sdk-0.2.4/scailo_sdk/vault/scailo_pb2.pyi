from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from roles import scailo_pb2 as _scailo_pb2_1
from vault_commons import scailo_pb2 as _scailo_pb2_1_1
from vault_files import scailo_pb2 as _scailo_pb2_1_1_1
from vault_folders import scailo_pb2 as _scailo_pb2_1_1_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VaultResourcesList(_message.Message):
    __slots__ = ("files", "folders")
    FILES_FIELD_NUMBER: _ClassVar[int]
    FOLDERS_FIELD_NUMBER: _ClassVar[int]
    files: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1_1.VaultFile]
    folders: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1_1_1.VaultFolder]
    def __init__(self, files: _Optional[_Iterable[_Union[_scailo_pb2_1_1_1.VaultFile, _Mapping]]] = ..., folders: _Optional[_Iterable[_Union[_scailo_pb2_1_1_1_1.VaultFolder, _Mapping]]] = ...) -> None: ...

class GiXRelayHeader(_message.Message):
    __slots__ = ("name", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: str
    def __init__(self, name: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class GiXRelayReqWithoutBody(_message.Message):
    __slots__ = ("uuid", "relay_content_type_header", "relay_accept_header", "relay_headers", "url")
    UUID_FIELD_NUMBER: _ClassVar[int]
    RELAY_CONTENT_TYPE_HEADER_FIELD_NUMBER: _ClassVar[int]
    RELAY_ACCEPT_HEADER_FIELD_NUMBER: _ClassVar[int]
    RELAY_HEADERS_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    relay_content_type_header: str
    relay_accept_header: str
    relay_headers: _containers.RepeatedCompositeFieldContainer[GiXRelayHeader]
    url: str
    def __init__(self, uuid: _Optional[str] = ..., relay_content_type_header: _Optional[str] = ..., relay_accept_header: _Optional[str] = ..., relay_headers: _Optional[_Iterable[_Union[GiXRelayHeader, _Mapping]]] = ..., url: _Optional[str] = ...) -> None: ...

class GiXRelayReqWithBody(_message.Message):
    __slots__ = ("uuid", "relay_content_type_header", "relay_accept_header", "relay_headers", "url", "body")
    UUID_FIELD_NUMBER: _ClassVar[int]
    RELAY_CONTENT_TYPE_HEADER_FIELD_NUMBER: _ClassVar[int]
    RELAY_ACCEPT_HEADER_FIELD_NUMBER: _ClassVar[int]
    RELAY_HEADERS_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    relay_content_type_header: str
    relay_accept_header: str
    relay_headers: _containers.RepeatedCompositeFieldContainer[GiXRelayHeader]
    url: str
    body: bytes
    def __init__(self, uuid: _Optional[str] = ..., relay_content_type_header: _Optional[str] = ..., relay_accept_header: _Optional[str] = ..., relay_headers: _Optional[_Iterable[_Union[GiXRelayHeader, _Mapping]]] = ..., url: _Optional[str] = ..., body: _Optional[bytes] = ...) -> None: ...

class GiXRelayResponse(_message.Message):
    __slots__ = ("uuid", "body")
    UUID_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    body: bytes
    def __init__(self, uuid: _Optional[str] = ..., body: _Optional[bytes] = ...) -> None: ...
