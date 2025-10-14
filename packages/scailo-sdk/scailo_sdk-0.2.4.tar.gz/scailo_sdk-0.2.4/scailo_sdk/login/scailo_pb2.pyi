from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UserLoginRequest(_message.Message):
    __slots__ = ("username", "plain_text_password", "otp", "expires_in")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PLAIN_TEXT_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    OTP_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_IN_FIELD_NUMBER: _ClassVar[int]
    username: str
    plain_text_password: str
    otp: str
    expires_in: int
    def __init__(self, username: _Optional[str] = ..., plain_text_password: _Optional[str] = ..., otp: _Optional[str] = ..., expires_in: _Optional[int] = ...) -> None: ...

class UserLoginResponse(_message.Message):
    __slots__ = ("username", "auth_token", "expires_at")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    username: str
    auth_token: str
    expires_at: int
    def __init__(self, username: _Optional[str] = ..., auth_token: _Optional[str] = ..., expires_at: _Optional[int] = ...) -> None: ...

class AuthTokenValidityRequest(_message.Message):
    __slots__ = ("auth_token",)
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    auth_token: str
    def __init__(self, auth_token: _Optional[str] = ...) -> None: ...

class LogoutRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LogoutResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UserLoginHistory(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "url_scheme", "username", "ip_addr", "expires_at")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    URL_SCHEME_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    IP_ADDR_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    url_scheme: str
    username: str
    ip_addr: str
    expires_at: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., url_scheme: _Optional[str] = ..., username: _Optional[str] = ..., ip_addr: _Optional[str] = ..., expires_at: _Optional[int] = ...) -> None: ...

class UserLoginHistoryList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[UserLoginHistory]
    def __init__(self, list: _Optional[_Iterable[_Union[UserLoginHistory, _Mapping]]] = ...) -> None: ...

class VendorUserLoginResponse(_message.Message):
    __slots__ = ("username", "auth_token", "expires_at", "vendor_id", "vendor_uuid")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UUID_FIELD_NUMBER: _ClassVar[int]
    username: str
    auth_token: str
    expires_at: int
    vendor_id: int
    vendor_uuid: str
    def __init__(self, username: _Optional[str] = ..., auth_token: _Optional[str] = ..., expires_at: _Optional[int] = ..., vendor_id: _Optional[int] = ..., vendor_uuid: _Optional[str] = ...) -> None: ...

class ClientUserLoginResponse(_message.Message):
    __slots__ = ("username", "auth_token", "expires_at", "client_id", "client_uuid")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UUID_FIELD_NUMBER: _ClassVar[int]
    username: str
    auth_token: str
    expires_at: int
    client_id: int
    client_uuid: str
    def __init__(self, username: _Optional[str] = ..., auth_token: _Optional[str] = ..., expires_at: _Optional[int] = ..., client_id: _Optional[int] = ..., client_uuid: _Optional[str] = ...) -> None: ...
