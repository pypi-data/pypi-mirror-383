from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VENDOR_STREAM_LIFECYCLE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_STREAM_LIFECYCLE_ANY_UNSPECIFIED: _ClassVar[VENDOR_STREAM_LIFECYCLE]
    VENDOR_STREAM_LIFECYCLE_OPEN: _ClassVar[VENDOR_STREAM_LIFECYCLE]
    VENDOR_STREAM_LIFECYCLE_COMPLETED: _ClassVar[VENDOR_STREAM_LIFECYCLE]
    VENDOR_STREAM_LIFECYCLE_CANCELLED: _ClassVar[VENDOR_STREAM_LIFECYCLE]

class VENDOR_STREAM_REF_FROM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_STREAM_REF_FROM_ANY_UNSPECIFIED: _ClassVar[VENDOR_STREAM_REF_FROM]
    VENDOR_STREAM_REF_FROM_PURCHASE_ORDER: _ClassVar[VENDOR_STREAM_REF_FROM]
    VENDOR_STREAM_REF_FROM_GOODS_RECEIPT: _ClassVar[VENDOR_STREAM_REF_FROM]
    VENDOR_STREAM_REF_FROM_VENDOR_INVOICE: _ClassVar[VENDOR_STREAM_REF_FROM]
    VENDOR_STREAM_REF_FROM_PURCHASE_RETURN: _ClassVar[VENDOR_STREAM_REF_FROM]
    VENDOR_STREAM_REF_FROM_DEBIT_NOTE: _ClassVar[VENDOR_STREAM_REF_FROM]
    VENDOR_STREAM_REF_FROM_PURCHASE_PAYMENT: _ClassVar[VENDOR_STREAM_REF_FROM]
    VENDOR_STREAM_REF_FROM_SUPPLY_OFFER: _ClassVar[VENDOR_STREAM_REF_FROM]

class VENDOR_STREAM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_STREAM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[VENDOR_STREAM_SORT_KEY]
    VENDOR_STREAM_SORT_KEY_CREATED_AT: _ClassVar[VENDOR_STREAM_SORT_KEY]
    VENDOR_STREAM_SORT_KEY_MODIFIED_AT: _ClassVar[VENDOR_STREAM_SORT_KEY]
    VENDOR_STREAM_SORT_KEY_COMPLETED_ON: _ClassVar[VENDOR_STREAM_SORT_KEY]
    VENDOR_STREAM_SORT_KEY_TITLE: _ClassVar[VENDOR_STREAM_SORT_KEY]

class VENDOR_STREAM_MESSAGE_TYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_STREAM_MESSAGE_TYPE_ANY_UNSPECIFIED: _ClassVar[VENDOR_STREAM_MESSAGE_TYPE]
    VENDOR_STREAM_MESSAGE_TYPE_USER: _ClassVar[VENDOR_STREAM_MESSAGE_TYPE]
    VENDOR_STREAM_MESSAGE_TYPE_SYSTEM: _ClassVar[VENDOR_STREAM_MESSAGE_TYPE]

class VENDOR_STREAM_MESSAGE_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VENDOR_STREAM_MESSAGE_SORT_KEY_ID_UNSPECIFIED: _ClassVar[VENDOR_STREAM_MESSAGE_SORT_KEY]
    VENDOR_STREAM_MESSAGE_SORT_KEY_CREATED_AT: _ClassVar[VENDOR_STREAM_MESSAGE_SORT_KEY]
    VENDOR_STREAM_MESSAGE_SORT_KEY_MODIFIED_AT: _ClassVar[VENDOR_STREAM_MESSAGE_SORT_KEY]
VENDOR_STREAM_LIFECYCLE_ANY_UNSPECIFIED: VENDOR_STREAM_LIFECYCLE
VENDOR_STREAM_LIFECYCLE_OPEN: VENDOR_STREAM_LIFECYCLE
VENDOR_STREAM_LIFECYCLE_COMPLETED: VENDOR_STREAM_LIFECYCLE
VENDOR_STREAM_LIFECYCLE_CANCELLED: VENDOR_STREAM_LIFECYCLE
VENDOR_STREAM_REF_FROM_ANY_UNSPECIFIED: VENDOR_STREAM_REF_FROM
VENDOR_STREAM_REF_FROM_PURCHASE_ORDER: VENDOR_STREAM_REF_FROM
VENDOR_STREAM_REF_FROM_GOODS_RECEIPT: VENDOR_STREAM_REF_FROM
VENDOR_STREAM_REF_FROM_VENDOR_INVOICE: VENDOR_STREAM_REF_FROM
VENDOR_STREAM_REF_FROM_PURCHASE_RETURN: VENDOR_STREAM_REF_FROM
VENDOR_STREAM_REF_FROM_DEBIT_NOTE: VENDOR_STREAM_REF_FROM
VENDOR_STREAM_REF_FROM_PURCHASE_PAYMENT: VENDOR_STREAM_REF_FROM
VENDOR_STREAM_REF_FROM_SUPPLY_OFFER: VENDOR_STREAM_REF_FROM
VENDOR_STREAM_SORT_KEY_ID_UNSPECIFIED: VENDOR_STREAM_SORT_KEY
VENDOR_STREAM_SORT_KEY_CREATED_AT: VENDOR_STREAM_SORT_KEY
VENDOR_STREAM_SORT_KEY_MODIFIED_AT: VENDOR_STREAM_SORT_KEY
VENDOR_STREAM_SORT_KEY_COMPLETED_ON: VENDOR_STREAM_SORT_KEY
VENDOR_STREAM_SORT_KEY_TITLE: VENDOR_STREAM_SORT_KEY
VENDOR_STREAM_MESSAGE_TYPE_ANY_UNSPECIFIED: VENDOR_STREAM_MESSAGE_TYPE
VENDOR_STREAM_MESSAGE_TYPE_USER: VENDOR_STREAM_MESSAGE_TYPE
VENDOR_STREAM_MESSAGE_TYPE_SYSTEM: VENDOR_STREAM_MESSAGE_TYPE
VENDOR_STREAM_MESSAGE_SORT_KEY_ID_UNSPECIFIED: VENDOR_STREAM_MESSAGE_SORT_KEY
VENDOR_STREAM_MESSAGE_SORT_KEY_CREATED_AT: VENDOR_STREAM_MESSAGE_SORT_KEY
VENDOR_STREAM_MESSAGE_SORT_KEY_MODIFIED_AT: VENDOR_STREAM_MESSAGE_SORT_KEY

class LogbookLogVendorStreamLC(_message.Message):
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
    operation: VENDOR_STREAM_LIFECYCLE
    username: str
    name: str
    user_id: int
    app_comment: str
    user_comment: str
    def __init__(self, id: _Optional[int] = ..., is_active: _Optional[bool] = ..., timestamp: _Optional[int] = ..., ref_uuid: _Optional[str] = ..., operation: _Optional[_Union[VENDOR_STREAM_LIFECYCLE, str]] = ..., username: _Optional[str] = ..., name: _Optional[str] = ..., user_id: _Optional[int] = ..., app_comment: _Optional[str] = ..., user_comment: _Optional[str] = ...) -> None: ...

class VendorStreamsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "title", "vendor_id", "ref_from", "ref_id", "assign_self_as_internal_subscriber", "assign_self_as_vendor_subscriber")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGN_SELF_AS_INTERNAL_SUBSCRIBER_FIELD_NUMBER: _ClassVar[int]
    ASSIGN_SELF_AS_VENDOR_SUBSCRIBER_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    title: str
    vendor_id: int
    ref_from: VENDOR_STREAM_REF_FROM
    ref_id: int
    assign_self_as_internal_subscriber: bool
    assign_self_as_vendor_subscriber: bool
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., title: _Optional[str] = ..., vendor_id: _Optional[int] = ..., ref_from: _Optional[_Union[VENDOR_STREAM_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., assign_self_as_internal_subscriber: _Optional[bool] = ..., assign_self_as_vendor_subscriber: _Optional[bool] = ...) -> None: ...

class VendorStreamsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "title")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    title: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., title: _Optional[str] = ...) -> None: ...

class VendorStream(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "status", "logs", "completed_on", "vault_folder_id", "vault_folder_uuid", "title", "vendor_id", "ref_from", "ref_id", "ref_uuid", "internal_ref", "unread_count", "message_count", "last_message_by")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_REF_FIELD_NUMBER: _ClassVar[int]
    UNREAD_COUNT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    LAST_MESSAGE_BY_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    status: VENDOR_STREAM_LIFECYCLE
    logs: _containers.RepeatedCompositeFieldContainer[LogbookLogVendorStreamLC]
    completed_on: int
    vault_folder_id: int
    vault_folder_uuid: str
    title: str
    vendor_id: int
    ref_from: VENDOR_STREAM_REF_FROM
    ref_id: int
    ref_uuid: str
    internal_ref: str
    unread_count: int
    message_count: int
    last_message_by: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., status: _Optional[_Union[VENDOR_STREAM_LIFECYCLE, str]] = ..., logs: _Optional[_Iterable[_Union[LogbookLogVendorStreamLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., vault_folder_uuid: _Optional[str] = ..., title: _Optional[str] = ..., vendor_id: _Optional[int] = ..., ref_from: _Optional[_Union[VENDOR_STREAM_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., ref_uuid: _Optional[str] = ..., internal_ref: _Optional[str] = ..., unread_count: _Optional[int] = ..., message_count: _Optional[int] = ..., last_message_by: _Optional[str] = ...) -> None: ...

class VendorStreamsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VendorStream]
    def __init__(self, list: _Optional[_Iterable[_Union[VendorStream, _Mapping]]] = ...) -> None: ...

class VendorStreamsServicePaginationReq(_message.Message):
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
    sort_key: VENDOR_STREAM_SORT_KEY
    status: VENDOR_STREAM_LIFECYCLE
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VENDOR_STREAM_SORT_KEY, str]] = ..., status: _Optional[_Union[VENDOR_STREAM_LIFECYCLE, str]] = ...) -> None: ...

class VendorStreamsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[VendorStream]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[VendorStream, _Mapping]]] = ...) -> None: ...

class VendorStreamsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "completed_on_start", "completed_on_end", "internal_ref", "title", "vendor_id", "ref_from", "ref_id", "internal_subscriber_user_id", "vendor_subscriber_user_id")
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
    COMPLETED_ON_START_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_END_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_REF_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_SUBSCRIBER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_SUBSCRIBER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: VENDOR_STREAM_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: VENDOR_STREAM_LIFECYCLE
    completed_on_start: int
    completed_on_end: int
    internal_ref: str
    title: str
    vendor_id: int
    ref_from: VENDOR_STREAM_REF_FROM
    ref_id: int
    internal_subscriber_user_id: int
    vendor_subscriber_user_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VENDOR_STREAM_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[VENDOR_STREAM_LIFECYCLE, str]] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., internal_ref: _Optional[str] = ..., title: _Optional[str] = ..., vendor_id: _Optional[int] = ..., ref_from: _Optional[_Union[VENDOR_STREAM_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., internal_subscriber_user_id: _Optional[int] = ..., vendor_subscriber_user_id: _Optional[int] = ...) -> None: ...

class VendorStreamsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "completed_on_start", "completed_on_end", "internal_ref", "title", "vendor_id", "ref_from", "ref_id", "internal_subscriber_user_id", "vendor_subscriber_user_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_START_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_END_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_REF_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_SUBSCRIBER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_SUBSCRIBER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: VENDOR_STREAM_LIFECYCLE
    completed_on_start: int
    completed_on_end: int
    internal_ref: str
    title: str
    vendor_id: int
    ref_from: VENDOR_STREAM_REF_FROM
    ref_id: int
    internal_subscriber_user_id: int
    vendor_subscriber_user_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[VENDOR_STREAM_LIFECYCLE, str]] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., internal_ref: _Optional[str] = ..., title: _Optional[str] = ..., vendor_id: _Optional[int] = ..., ref_from: _Optional[_Union[VENDOR_STREAM_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., internal_subscriber_user_id: _Optional[int] = ..., vendor_subscriber_user_id: _Optional[int] = ...) -> None: ...

class VendorStreamsServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "vendor_id", "internal_subscriber_user_id", "vendor_subscriber_user_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_SUBSCRIBER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_SUBSCRIBER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: VENDOR_STREAM_SORT_KEY
    entity_uuid: str
    status: VENDOR_STREAM_LIFECYCLE
    search_key: str
    vendor_id: int
    internal_subscriber_user_id: int
    vendor_subscriber_user_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VENDOR_STREAM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[VENDOR_STREAM_LIFECYCLE, str]] = ..., search_key: _Optional[str] = ..., vendor_id: _Optional[int] = ..., internal_subscriber_user_id: _Optional[int] = ..., vendor_subscriber_user_id: _Optional[int] = ...) -> None: ...

class VendorStreamsServiceMessageCreateRequest(_message.Message):
    __slots__ = ("message_type", "vendor_stream_uuid", "response_to_message_uuid", "content")
    MESSAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    VENDOR_STREAM_UUID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TO_MESSAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    message_type: VENDOR_STREAM_MESSAGE_TYPE
    vendor_stream_uuid: str
    response_to_message_uuid: str
    content: str
    def __init__(self, message_type: _Optional[_Union[VENDOR_STREAM_MESSAGE_TYPE, str]] = ..., vendor_stream_uuid: _Optional[str] = ..., response_to_message_uuid: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class VendorStreamMessage(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "message_type", "vendor_stream_id", "response_to_message_uuid", "content", "internal_ref", "is_read")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    VENDOR_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TO_MESSAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_REF_FIELD_NUMBER: _ClassVar[int]
    IS_READ_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    message_type: VENDOR_STREAM_MESSAGE_TYPE
    vendor_stream_id: int
    response_to_message_uuid: str
    content: str
    internal_ref: str
    is_read: bool
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., message_type: _Optional[_Union[VENDOR_STREAM_MESSAGE_TYPE, str]] = ..., vendor_stream_id: _Optional[int] = ..., response_to_message_uuid: _Optional[str] = ..., content: _Optional[str] = ..., internal_ref: _Optional[str] = ..., is_read: _Optional[bool] = ...) -> None: ...

class VendorStreamMessagesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VendorStreamMessage]
    def __init__(self, list: _Optional[_Iterable[_Union[VendorStreamMessage, _Mapping]]] = ...) -> None: ...

class VendorStreamMessagesSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "message_type", "vendor_stream_id", "response_to_message_uuid", "search_key")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    VENDOR_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TO_MESSAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: VENDOR_STREAM_MESSAGE_SORT_KEY
    entity_uuid: str
    message_type: VENDOR_STREAM_MESSAGE_TYPE
    vendor_stream_id: int
    response_to_message_uuid: str
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[VENDOR_STREAM_MESSAGE_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., message_type: _Optional[_Union[VENDOR_STREAM_MESSAGE_TYPE, str]] = ..., vendor_stream_id: _Optional[int] = ..., response_to_message_uuid: _Optional[str] = ..., search_key: _Optional[str] = ...) -> None: ...

class VendorStreamsServicePaginatedMessagesResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[VendorStreamMessage]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[VendorStreamMessage, _Mapping]]] = ...) -> None: ...

class VendorStreamMessageReceipt(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "vendor_stream_message_uuid", "user_id", "is_read", "read_at")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    VENDOR_STREAM_MESSAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_READ_FIELD_NUMBER: _ClassVar[int]
    READ_AT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    vendor_stream_message_uuid: str
    user_id: int
    is_read: bool
    read_at: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., vendor_stream_message_uuid: _Optional[str] = ..., user_id: _Optional[int] = ..., is_read: _Optional[bool] = ..., read_at: _Optional[int] = ...) -> None: ...

class VendorStreamMessageReceiptsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VendorStreamMessageReceipt]
    def __init__(self, list: _Optional[_Iterable[_Union[VendorStreamMessageReceipt, _Mapping]]] = ...) -> None: ...

class VendorStreamsServiceInternalSubscriberCreateRequest(_message.Message):
    __slots__ = ("user_comment", "vendor_stream_id", "user_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    vendor_stream_id: int
    user_id: int
    def __init__(self, user_comment: _Optional[str] = ..., vendor_stream_id: _Optional[int] = ..., user_id: _Optional[int] = ...) -> None: ...

class VendorStreamInternalSubscriber(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "vendor_stream_id", "user_id", "user_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    vendor_stream_id: int
    user_id: int
    user_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., vendor_stream_id: _Optional[int] = ..., user_id: _Optional[int] = ..., user_uuid: _Optional[str] = ...) -> None: ...

class VendorStreamInternalSubscribersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VendorStreamInternalSubscriber]
    def __init__(self, list: _Optional[_Iterable[_Union[VendorStreamInternalSubscriber, _Mapping]]] = ...) -> None: ...

class VendorStreamsServiceImportInternalSubscribersRequest(_message.Message):
    __slots__ = ("user_comment", "vendor_stream_id", "resource_id", "delete_existing")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    DELETE_EXISTING_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    vendor_stream_id: int
    resource_id: int
    delete_existing: bool
    def __init__(self, user_comment: _Optional[str] = ..., vendor_stream_id: _Optional[int] = ..., resource_id: _Optional[int] = ..., delete_existing: _Optional[bool] = ...) -> None: ...

class VendorStreamsServiceVendorSubscriberCreateRequest(_message.Message):
    __slots__ = ("user_comment", "vendor_stream_id", "user_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    vendor_stream_id: int
    user_id: int
    def __init__(self, user_comment: _Optional[str] = ..., vendor_stream_id: _Optional[int] = ..., user_id: _Optional[int] = ...) -> None: ...

class VendorStreamVendorSubscriber(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "vendor_stream_id", "user_id", "user_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VENDOR_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    vendor_stream_id: int
    user_id: int
    user_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., vendor_stream_id: _Optional[int] = ..., user_id: _Optional[int] = ..., user_uuid: _Optional[str] = ...) -> None: ...

class VendorStreamVendorSubscribersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[VendorStreamVendorSubscriber]
    def __init__(self, list: _Optional[_Iterable[_Union[VendorStreamVendorSubscriber, _Mapping]]] = ...) -> None: ...
