from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CLIENT_STREAM_LIFECYCLE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLIENT_STREAM_LIFECYCLE_ANY_UNSPECIFIED: _ClassVar[CLIENT_STREAM_LIFECYCLE]
    CLIENT_STREAM_LIFECYCLE_OPEN: _ClassVar[CLIENT_STREAM_LIFECYCLE]
    CLIENT_STREAM_LIFECYCLE_COMPLETED: _ClassVar[CLIENT_STREAM_LIFECYCLE]
    CLIENT_STREAM_LIFECYCLE_CANCELLED: _ClassVar[CLIENT_STREAM_LIFECYCLE]

class CLIENT_STREAM_REF_FROM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLIENT_STREAM_REF_FROM_ANY_UNSPECIFIED: _ClassVar[CLIENT_STREAM_REF_FROM]
    CLIENT_STREAM_REF_FROM_SALES_ORDER: _ClassVar[CLIENT_STREAM_REF_FROM]
    CLIENT_STREAM_REF_FROM_GOODS_DISPATCH: _ClassVar[CLIENT_STREAM_REF_FROM]
    CLIENT_STREAM_REF_FROM_SALES_INVOICE: _ClassVar[CLIENT_STREAM_REF_FROM]
    CLIENT_STREAM_REF_FROM_SALES_RETURN: _ClassVar[CLIENT_STREAM_REF_FROM]
    CLIENT_STREAM_REF_FROM_CREDIT_NOTE: _ClassVar[CLIENT_STREAM_REF_FROM]
    CLIENT_STREAM_REF_FROM_SALES_RECEIPT: _ClassVar[CLIENT_STREAM_REF_FROM]
    CLIENT_STREAM_REF_FROM_SALES_QUOTATION: _ClassVar[CLIENT_STREAM_REF_FROM]
    CLIENT_STREAM_REF_FROM_SALES_ENQUIRY: _ClassVar[CLIENT_STREAM_REF_FROM]
    CLIENT_STREAM_REF_FROM_WORK_ORDER: _ClassVar[CLIENT_STREAM_REF_FROM]

class CLIENT_STREAM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLIENT_STREAM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[CLIENT_STREAM_SORT_KEY]
    CLIENT_STREAM_SORT_KEY_CREATED_AT: _ClassVar[CLIENT_STREAM_SORT_KEY]
    CLIENT_STREAM_SORT_KEY_MODIFIED_AT: _ClassVar[CLIENT_STREAM_SORT_KEY]
    CLIENT_STREAM_SORT_KEY_COMPLETED_ON: _ClassVar[CLIENT_STREAM_SORT_KEY]
    CLIENT_STREAM_SORT_KEY_TITLE: _ClassVar[CLIENT_STREAM_SORT_KEY]

class CLIENT_STREAM_MESSAGE_TYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLIENT_STREAM_MESSAGE_TYPE_ANY_UNSPECIFIED: _ClassVar[CLIENT_STREAM_MESSAGE_TYPE]
    CLIENT_STREAM_MESSAGE_TYPE_USER: _ClassVar[CLIENT_STREAM_MESSAGE_TYPE]
    CLIENT_STREAM_MESSAGE_TYPE_SYSTEM: _ClassVar[CLIENT_STREAM_MESSAGE_TYPE]

class CLIENT_STREAM_MESSAGE_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLIENT_STREAM_MESSAGE_SORT_KEY_ID_UNSPECIFIED: _ClassVar[CLIENT_STREAM_MESSAGE_SORT_KEY]
    CLIENT_STREAM_MESSAGE_SORT_KEY_CREATED_AT: _ClassVar[CLIENT_STREAM_MESSAGE_SORT_KEY]
    CLIENT_STREAM_MESSAGE_SORT_KEY_MODIFIED_AT: _ClassVar[CLIENT_STREAM_MESSAGE_SORT_KEY]
CLIENT_STREAM_LIFECYCLE_ANY_UNSPECIFIED: CLIENT_STREAM_LIFECYCLE
CLIENT_STREAM_LIFECYCLE_OPEN: CLIENT_STREAM_LIFECYCLE
CLIENT_STREAM_LIFECYCLE_COMPLETED: CLIENT_STREAM_LIFECYCLE
CLIENT_STREAM_LIFECYCLE_CANCELLED: CLIENT_STREAM_LIFECYCLE
CLIENT_STREAM_REF_FROM_ANY_UNSPECIFIED: CLIENT_STREAM_REF_FROM
CLIENT_STREAM_REF_FROM_SALES_ORDER: CLIENT_STREAM_REF_FROM
CLIENT_STREAM_REF_FROM_GOODS_DISPATCH: CLIENT_STREAM_REF_FROM
CLIENT_STREAM_REF_FROM_SALES_INVOICE: CLIENT_STREAM_REF_FROM
CLIENT_STREAM_REF_FROM_SALES_RETURN: CLIENT_STREAM_REF_FROM
CLIENT_STREAM_REF_FROM_CREDIT_NOTE: CLIENT_STREAM_REF_FROM
CLIENT_STREAM_REF_FROM_SALES_RECEIPT: CLIENT_STREAM_REF_FROM
CLIENT_STREAM_REF_FROM_SALES_QUOTATION: CLIENT_STREAM_REF_FROM
CLIENT_STREAM_REF_FROM_SALES_ENQUIRY: CLIENT_STREAM_REF_FROM
CLIENT_STREAM_REF_FROM_WORK_ORDER: CLIENT_STREAM_REF_FROM
CLIENT_STREAM_SORT_KEY_ID_UNSPECIFIED: CLIENT_STREAM_SORT_KEY
CLIENT_STREAM_SORT_KEY_CREATED_AT: CLIENT_STREAM_SORT_KEY
CLIENT_STREAM_SORT_KEY_MODIFIED_AT: CLIENT_STREAM_SORT_KEY
CLIENT_STREAM_SORT_KEY_COMPLETED_ON: CLIENT_STREAM_SORT_KEY
CLIENT_STREAM_SORT_KEY_TITLE: CLIENT_STREAM_SORT_KEY
CLIENT_STREAM_MESSAGE_TYPE_ANY_UNSPECIFIED: CLIENT_STREAM_MESSAGE_TYPE
CLIENT_STREAM_MESSAGE_TYPE_USER: CLIENT_STREAM_MESSAGE_TYPE
CLIENT_STREAM_MESSAGE_TYPE_SYSTEM: CLIENT_STREAM_MESSAGE_TYPE
CLIENT_STREAM_MESSAGE_SORT_KEY_ID_UNSPECIFIED: CLIENT_STREAM_MESSAGE_SORT_KEY
CLIENT_STREAM_MESSAGE_SORT_KEY_CREATED_AT: CLIENT_STREAM_MESSAGE_SORT_KEY
CLIENT_STREAM_MESSAGE_SORT_KEY_MODIFIED_AT: CLIENT_STREAM_MESSAGE_SORT_KEY

class LogbookLogClientStreamLC(_message.Message):
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
    operation: CLIENT_STREAM_LIFECYCLE
    username: str
    name: str
    user_id: int
    app_comment: str
    user_comment: str
    def __init__(self, id: _Optional[int] = ..., is_active: _Optional[bool] = ..., timestamp: _Optional[int] = ..., ref_uuid: _Optional[str] = ..., operation: _Optional[_Union[CLIENT_STREAM_LIFECYCLE, str]] = ..., username: _Optional[str] = ..., name: _Optional[str] = ..., user_id: _Optional[int] = ..., app_comment: _Optional[str] = ..., user_comment: _Optional[str] = ...) -> None: ...

class ClientStreamsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "title", "client_id", "ref_from", "ref_id", "assign_self_as_internal_subscriber", "assign_self_as_client_subscriber")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    ASSIGN_SELF_AS_INTERNAL_SUBSCRIBER_FIELD_NUMBER: _ClassVar[int]
    ASSIGN_SELF_AS_CLIENT_SUBSCRIBER_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    title: str
    client_id: int
    ref_from: CLIENT_STREAM_REF_FROM
    ref_id: int
    assign_self_as_internal_subscriber: bool
    assign_self_as_client_subscriber: bool
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., title: _Optional[str] = ..., client_id: _Optional[int] = ..., ref_from: _Optional[_Union[CLIENT_STREAM_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., assign_self_as_internal_subscriber: _Optional[bool] = ..., assign_self_as_client_subscriber: _Optional[bool] = ...) -> None: ...

class ClientStreamsServiceUpdateRequest(_message.Message):
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

class ClientStream(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "status", "logs", "completed_on", "vault_folder_id", "vault_folder_uuid", "title", "client_id", "ref_from", "ref_id", "ref_uuid", "internal_ref", "unread_count", "message_count", "last_message_by")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_UUID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_REF_FIELD_NUMBER: _ClassVar[int]
    UNREAD_COUNT_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_COUNT_FIELD_NUMBER: _ClassVar[int]
    LAST_MESSAGE_BY_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    status: CLIENT_STREAM_LIFECYCLE
    logs: _containers.RepeatedCompositeFieldContainer[LogbookLogClientStreamLC]
    completed_on: int
    vault_folder_id: int
    vault_folder_uuid: str
    title: str
    client_id: int
    ref_from: CLIENT_STREAM_REF_FROM
    ref_id: int
    ref_uuid: str
    internal_ref: str
    unread_count: int
    message_count: int
    last_message_by: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., status: _Optional[_Union[CLIENT_STREAM_LIFECYCLE, str]] = ..., logs: _Optional[_Iterable[_Union[LogbookLogClientStreamLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., vault_folder_uuid: _Optional[str] = ..., title: _Optional[str] = ..., client_id: _Optional[int] = ..., ref_from: _Optional[_Union[CLIENT_STREAM_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., ref_uuid: _Optional[str] = ..., internal_ref: _Optional[str] = ..., unread_count: _Optional[int] = ..., message_count: _Optional[int] = ..., last_message_by: _Optional[str] = ...) -> None: ...

class ClientStreamsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ClientStream]
    def __init__(self, list: _Optional[_Iterable[_Union[ClientStream, _Mapping]]] = ...) -> None: ...

class ClientStreamsServicePaginationReq(_message.Message):
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
    sort_key: CLIENT_STREAM_SORT_KEY
    status: CLIENT_STREAM_LIFECYCLE
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[CLIENT_STREAM_SORT_KEY, str]] = ..., status: _Optional[_Union[CLIENT_STREAM_LIFECYCLE, str]] = ...) -> None: ...

class ClientStreamsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[ClientStream]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[ClientStream, _Mapping]]] = ...) -> None: ...

class ClientStreamsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "completed_on_start", "completed_on_end", "internal_ref", "title", "client_id", "ref_from", "ref_id", "internal_subscriber_user_id", "client_subscriber_user_id")
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
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_SUBSCRIBER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SUBSCRIBER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: CLIENT_STREAM_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: CLIENT_STREAM_LIFECYCLE
    completed_on_start: int
    completed_on_end: int
    internal_ref: str
    title: str
    client_id: int
    ref_from: CLIENT_STREAM_REF_FROM
    ref_id: int
    internal_subscriber_user_id: int
    client_subscriber_user_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[CLIENT_STREAM_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[CLIENT_STREAM_LIFECYCLE, str]] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., internal_ref: _Optional[str] = ..., title: _Optional[str] = ..., client_id: _Optional[int] = ..., ref_from: _Optional[_Union[CLIENT_STREAM_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., internal_subscriber_user_id: _Optional[int] = ..., client_subscriber_user_id: _Optional[int] = ...) -> None: ...

class ClientStreamsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "completed_on_start", "completed_on_end", "internal_ref", "title", "client_id", "ref_from", "ref_id", "internal_subscriber_user_id", "client_subscriber_user_id")
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
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_SUBSCRIBER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SUBSCRIBER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: CLIENT_STREAM_LIFECYCLE
    completed_on_start: int
    completed_on_end: int
    internal_ref: str
    title: str
    client_id: int
    ref_from: CLIENT_STREAM_REF_FROM
    ref_id: int
    internal_subscriber_user_id: int
    client_subscriber_user_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[CLIENT_STREAM_LIFECYCLE, str]] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., internal_ref: _Optional[str] = ..., title: _Optional[str] = ..., client_id: _Optional[int] = ..., ref_from: _Optional[_Union[CLIENT_STREAM_REF_FROM, str]] = ..., ref_id: _Optional[int] = ..., internal_subscriber_user_id: _Optional[int] = ..., client_subscriber_user_id: _Optional[int] = ...) -> None: ...

class ClientStreamsServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "client_id", "internal_subscriber_user_id", "client_subscriber_user_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_SUBSCRIBER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SUBSCRIBER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: CLIENT_STREAM_SORT_KEY
    entity_uuid: str
    status: CLIENT_STREAM_LIFECYCLE
    search_key: str
    client_id: int
    internal_subscriber_user_id: int
    client_subscriber_user_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[CLIENT_STREAM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[CLIENT_STREAM_LIFECYCLE, str]] = ..., search_key: _Optional[str] = ..., client_id: _Optional[int] = ..., internal_subscriber_user_id: _Optional[int] = ..., client_subscriber_user_id: _Optional[int] = ...) -> None: ...

class ClientStreamsServiceMessageCreateRequest(_message.Message):
    __slots__ = ("message_type", "client_stream_uuid", "response_to_message_uuid", "content")
    MESSAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CLIENT_STREAM_UUID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TO_MESSAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    message_type: CLIENT_STREAM_MESSAGE_TYPE
    client_stream_uuid: str
    response_to_message_uuid: str
    content: str
    def __init__(self, message_type: _Optional[_Union[CLIENT_STREAM_MESSAGE_TYPE, str]] = ..., client_stream_uuid: _Optional[str] = ..., response_to_message_uuid: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class ClientStreamMessage(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "message_type", "client_stream_id", "response_to_message_uuid", "content", "internal_ref", "is_read")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CLIENT_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TO_MESSAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_REF_FIELD_NUMBER: _ClassVar[int]
    IS_READ_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    message_type: CLIENT_STREAM_MESSAGE_TYPE
    client_stream_id: int
    response_to_message_uuid: str
    content: str
    internal_ref: str
    is_read: bool
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., message_type: _Optional[_Union[CLIENT_STREAM_MESSAGE_TYPE, str]] = ..., client_stream_id: _Optional[int] = ..., response_to_message_uuid: _Optional[str] = ..., content: _Optional[str] = ..., internal_ref: _Optional[str] = ..., is_read: _Optional[bool] = ...) -> None: ...

class ClientStreamMessagesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ClientStreamMessage]
    def __init__(self, list: _Optional[_Iterable[_Union[ClientStreamMessage, _Mapping]]] = ...) -> None: ...

class ClientStreamMessagesSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "message_type", "client_stream_id", "response_to_message_uuid", "search_key")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CLIENT_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_TO_MESSAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: CLIENT_STREAM_MESSAGE_SORT_KEY
    entity_uuid: str
    message_type: CLIENT_STREAM_MESSAGE_TYPE
    client_stream_id: int
    response_to_message_uuid: str
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[CLIENT_STREAM_MESSAGE_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., message_type: _Optional[_Union[CLIENT_STREAM_MESSAGE_TYPE, str]] = ..., client_stream_id: _Optional[int] = ..., response_to_message_uuid: _Optional[str] = ..., search_key: _Optional[str] = ...) -> None: ...

class ClientStreamsServicePaginatedMessagesResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[ClientStreamMessage]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[ClientStreamMessage, _Mapping]]] = ...) -> None: ...

class ClientStreamMessageReceipt(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "client_stream_message_uuid", "user_id", "is_read", "read_at")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CLIENT_STREAM_MESSAGE_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    IS_READ_FIELD_NUMBER: _ClassVar[int]
    READ_AT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    client_stream_message_uuid: str
    user_id: int
    is_read: bool
    read_at: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., client_stream_message_uuid: _Optional[str] = ..., user_id: _Optional[int] = ..., is_read: _Optional[bool] = ..., read_at: _Optional[int] = ...) -> None: ...

class ClientStreamMessageReceiptsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ClientStreamMessageReceipt]
    def __init__(self, list: _Optional[_Iterable[_Union[ClientStreamMessageReceipt, _Mapping]]] = ...) -> None: ...

class ClientStreamsServiceInternalSubscriberCreateRequest(_message.Message):
    __slots__ = ("user_comment", "client_stream_id", "user_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    CLIENT_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    client_stream_id: int
    user_id: int
    def __init__(self, user_comment: _Optional[str] = ..., client_stream_id: _Optional[int] = ..., user_id: _Optional[int] = ...) -> None: ...

class ClientStreamInternalSubscriber(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "client_stream_id", "user_id", "user_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    CLIENT_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    client_stream_id: int
    user_id: int
    user_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., client_stream_id: _Optional[int] = ..., user_id: _Optional[int] = ..., user_uuid: _Optional[str] = ...) -> None: ...

class ClientStreamInternalSubscribersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ClientStreamInternalSubscriber]
    def __init__(self, list: _Optional[_Iterable[_Union[ClientStreamInternalSubscriber, _Mapping]]] = ...) -> None: ...

class ClientStreamsServiceImportInternalSubscribersRequest(_message.Message):
    __slots__ = ("user_comment", "client_stream_id", "resource_id", "delete_existing")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    CLIENT_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    DELETE_EXISTING_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    client_stream_id: int
    resource_id: int
    delete_existing: bool
    def __init__(self, user_comment: _Optional[str] = ..., client_stream_id: _Optional[int] = ..., resource_id: _Optional[int] = ..., delete_existing: _Optional[bool] = ...) -> None: ...

class ClientStreamsServiceClientSubscriberCreateRequest(_message.Message):
    __slots__ = ("user_comment", "client_stream_id", "user_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    CLIENT_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    client_stream_id: int
    user_id: int
    def __init__(self, user_comment: _Optional[str] = ..., client_stream_id: _Optional[int] = ..., user_id: _Optional[int] = ...) -> None: ...

class ClientStreamClientSubscriber(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "client_stream_id", "user_id", "user_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    CLIENT_STREAM_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USER_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    client_stream_id: int
    user_id: int
    user_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., client_stream_id: _Optional[int] = ..., user_id: _Optional[int] = ..., user_uuid: _Optional[str] = ...) -> None: ...

class ClientStreamClientSubscribersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ClientStreamClientSubscriber]
    def __init__(self, list: _Optional[_Iterable[_Union[ClientStreamClientSubscriber, _Mapping]]] = ...) -> None: ...
