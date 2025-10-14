from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from forms_fields_data import scailo_pb2 as _scailo_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MEETING_LIFECYCLE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEETING_LIFECYCLE_ANY_UNSPECIFIED: _ClassVar[MEETING_LIFECYCLE]
    MEETING_LIFECYCLE_OPEN: _ClassVar[MEETING_LIFECYCLE]
    MEETING_LIFECYCLE_COMPLETED: _ClassVar[MEETING_LIFECYCLE]
    MEETING_LIFECYCLE_CANCELLED: _ClassVar[MEETING_LIFECYCLE]

class MEETING_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEETING_SORT_KEY_ID_UNSPECIFIED: _ClassVar[MEETING_SORT_KEY]
    MEETING_SORT_KEY_CREATED_AT: _ClassVar[MEETING_SORT_KEY]
    MEETING_SORT_KEY_MODIFIED_AT: _ClassVar[MEETING_SORT_KEY]
    MEETING_SORT_KEY_COMPLETED_ON: _ClassVar[MEETING_SORT_KEY]
    MEETING_SORT_KEY_TITLE: _ClassVar[MEETING_SORT_KEY]
    MEETING_SORT_KEY_STARTS_AT: _ClassVar[MEETING_SORT_KEY]
    MEETING_SORT_KEY_ENDS_AT: _ClassVar[MEETING_SORT_KEY]

class MEETING_RSVP(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEETING_RSVP_ANY_UNSPECIFIED: _ClassVar[MEETING_RSVP]
    MEETING_RSVP_NONE: _ClassVar[MEETING_RSVP]
    MEETING_RSVP_YES: _ClassVar[MEETING_RSVP]
    MEETING_RSVP_NO: _ClassVar[MEETING_RSVP]
    MEETING_RSVP_MAYBE: _ClassVar[MEETING_RSVP]

class MEETING_ACTIONABLE_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MEETING_ACTIONABLE_SORT_KEY_ID_UNSPECIFIED: _ClassVar[MEETING_ACTIONABLE_SORT_KEY]
    MEETING_ACTIONABLE_SORT_KEY_CREATED_AT: _ClassVar[MEETING_ACTIONABLE_SORT_KEY]
    MEETING_ACTIONABLE_SORT_KEY_MODIFIED_AT: _ClassVar[MEETING_ACTIONABLE_SORT_KEY]
    MEETING_ACTIONABLE_SORT_KEY_TITLE: _ClassVar[MEETING_ACTIONABLE_SORT_KEY]
    MEETING_ACTIONABLE_SORT_KEY_ACTIVITY_TAG_ID: _ClassVar[MEETING_ACTIONABLE_SORT_KEY]
MEETING_LIFECYCLE_ANY_UNSPECIFIED: MEETING_LIFECYCLE
MEETING_LIFECYCLE_OPEN: MEETING_LIFECYCLE
MEETING_LIFECYCLE_COMPLETED: MEETING_LIFECYCLE
MEETING_LIFECYCLE_CANCELLED: MEETING_LIFECYCLE
MEETING_SORT_KEY_ID_UNSPECIFIED: MEETING_SORT_KEY
MEETING_SORT_KEY_CREATED_AT: MEETING_SORT_KEY
MEETING_SORT_KEY_MODIFIED_AT: MEETING_SORT_KEY
MEETING_SORT_KEY_COMPLETED_ON: MEETING_SORT_KEY
MEETING_SORT_KEY_TITLE: MEETING_SORT_KEY
MEETING_SORT_KEY_STARTS_AT: MEETING_SORT_KEY
MEETING_SORT_KEY_ENDS_AT: MEETING_SORT_KEY
MEETING_RSVP_ANY_UNSPECIFIED: MEETING_RSVP
MEETING_RSVP_NONE: MEETING_RSVP
MEETING_RSVP_YES: MEETING_RSVP
MEETING_RSVP_NO: MEETING_RSVP
MEETING_RSVP_MAYBE: MEETING_RSVP
MEETING_ACTIONABLE_SORT_KEY_ID_UNSPECIFIED: MEETING_ACTIONABLE_SORT_KEY
MEETING_ACTIONABLE_SORT_KEY_CREATED_AT: MEETING_ACTIONABLE_SORT_KEY
MEETING_ACTIONABLE_SORT_KEY_MODIFIED_AT: MEETING_ACTIONABLE_SORT_KEY
MEETING_ACTIONABLE_SORT_KEY_TITLE: MEETING_ACTIONABLE_SORT_KEY
MEETING_ACTIONABLE_SORT_KEY_ACTIVITY_TAG_ID: MEETING_ACTIONABLE_SORT_KEY

class LogbookLogMeetingLC(_message.Message):
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
    operation: MEETING_LIFECYCLE
    username: str
    name: str
    user_id: int
    app_comment: str
    user_comment: str
    def __init__(self, id: _Optional[int] = ..., is_active: _Optional[bool] = ..., timestamp: _Optional[int] = ..., ref_uuid: _Optional[str] = ..., operation: _Optional[_Union[MEETING_LIFECYCLE, str]] = ..., username: _Optional[str] = ..., name: _Optional[str] = ..., user_id: _Optional[int] = ..., app_comment: _Optional[str] = ..., user_comment: _Optional[str] = ...) -> None: ...

class MeetingsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "project_id", "title", "starts_at", "ends_at", "description", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    project_id: int
    title: str
    starts_at: int
    ends_at: int
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., project_id: _Optional[int] = ..., title: _Optional[str] = ..., starts_at: _Optional[int] = ..., ends_at: _Optional[int] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class MeetingsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "project_id", "title", "starts_at", "ends_at", "description", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    project_id: int
    title: str
    starts_at: int
    ends_at: int
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., project_id: _Optional[int] = ..., title: _Optional[str] = ..., starts_at: _Optional[int] = ..., ends_at: _Optional[int] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class Meeting(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "status", "logs", "completed_on", "vault_folder_id", "project_id", "title", "starts_at", "ends_at", "description", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    status: MEETING_LIFECYCLE
    logs: _containers.RepeatedCompositeFieldContainer[LogbookLogMeetingLC]
    completed_on: int
    vault_folder_id: int
    project_id: int
    title: str
    starts_at: int
    ends_at: int
    description: str
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., status: _Optional[_Union[MEETING_LIFECYCLE, str]] = ..., logs: _Optional[_Iterable[_Union[LogbookLogMeetingLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., project_id: _Optional[int] = ..., title: _Optional[str] = ..., starts_at: _Optional[int] = ..., ends_at: _Optional[int] = ..., description: _Optional[str] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class MeetingsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[Meeting]
    def __init__(self, list: _Optional[_Iterable[_Union[Meeting, _Mapping]]] = ...) -> None: ...

class MeetingsServicePaginationReq(_message.Message):
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
    sort_key: MEETING_SORT_KEY
    status: MEETING_LIFECYCLE
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[MEETING_SORT_KEY, str]] = ..., status: _Optional[_Union[MEETING_LIFECYCLE, str]] = ...) -> None: ...

class MeetingsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[Meeting]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[Meeting, _Mapping]]] = ...) -> None: ...

class MeetingsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "completed_on_start", "completed_on_end", "title", "starts_at_start", "starts_at_end", "ends_at_start", "ends_at_end", "project_id", "employee_id", "associate_id", "activity_tag_id", "form_data")
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
    TITLE_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_START_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_END_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_START_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_END_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TAG_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: MEETING_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: MEETING_LIFECYCLE
    completed_on_start: int
    completed_on_end: int
    title: str
    starts_at_start: int
    starts_at_end: int
    ends_at_start: int
    ends_at_end: int
    project_id: int
    employee_id: int
    associate_id: int
    activity_tag_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[MEETING_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[MEETING_LIFECYCLE, str]] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., title: _Optional[str] = ..., starts_at_start: _Optional[int] = ..., starts_at_end: _Optional[int] = ..., ends_at_start: _Optional[int] = ..., ends_at_end: _Optional[int] = ..., project_id: _Optional[int] = ..., employee_id: _Optional[int] = ..., associate_id: _Optional[int] = ..., activity_tag_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class MeetingsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "completed_on_start", "completed_on_end", "title", "starts_at_start", "starts_at_end", "ends_at_start", "ends_at_end", "project_id", "employee_id", "associate_id", "activity_tag_id", "form_data")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_START_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_END_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_START_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_END_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_START_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_END_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TAG_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: MEETING_LIFECYCLE
    completed_on_start: int
    completed_on_end: int
    title: str
    starts_at_start: int
    starts_at_end: int
    ends_at_start: int
    ends_at_end: int
    project_id: int
    employee_id: int
    associate_id: int
    activity_tag_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[MEETING_LIFECYCLE, str]] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., title: _Optional[str] = ..., starts_at_start: _Optional[int] = ..., starts_at_end: _Optional[int] = ..., ends_at_start: _Optional[int] = ..., ends_at_end: _Optional[int] = ..., project_id: _Optional[int] = ..., employee_id: _Optional[int] = ..., associate_id: _Optional[int] = ..., activity_tag_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class MeetingsServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "employee_id", "associate_id", "activity_tag_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TAG_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: MEETING_SORT_KEY
    entity_uuid: str
    status: MEETING_LIFECYCLE
    search_key: str
    employee_id: int
    associate_id: int
    activity_tag_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[MEETING_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[MEETING_LIFECYCLE, str]] = ..., search_key: _Optional[str] = ..., employee_id: _Optional[int] = ..., associate_id: _Optional[int] = ..., activity_tag_id: _Optional[int] = ...) -> None: ...

class MeetingsServiceActionableCreateRequest(_message.Message):
    __slots__ = ("user_comment", "meeting_id", "title", "content", "activity_tag_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEETING_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TAG_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    meeting_id: int
    title: str
    content: str
    activity_tag_id: int
    def __init__(self, user_comment: _Optional[str] = ..., meeting_id: _Optional[int] = ..., title: _Optional[str] = ..., content: _Optional[str] = ..., activity_tag_id: _Optional[int] = ...) -> None: ...

class MeetingsServiceActionableUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "title", "content", "activity_tag_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TAG_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    title: str
    content: str
    activity_tag_id: int
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., title: _Optional[str] = ..., content: _Optional[str] = ..., activity_tag_id: _Optional[int] = ...) -> None: ...

class MeetingActionable(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "meeting_id", "title", "content", "activity_tag_id")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEETING_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TAG_ID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    meeting_id: int
    title: str
    content: str
    activity_tag_id: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., meeting_id: _Optional[int] = ..., title: _Optional[str] = ..., content: _Optional[str] = ..., activity_tag_id: _Optional[int] = ...) -> None: ...

class MeetingActionablesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[MeetingActionable]
    def __init__(self, list: _Optional[_Iterable[_Union[MeetingActionable, _Mapping]]] = ...) -> None: ...

class MeetingActionableHistoryRequest(_message.Message):
    __slots__ = ("meeting_id", "title")
    MEETING_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    meeting_id: int
    title: str
    def __init__(self, meeting_id: _Optional[int] = ..., title: _Optional[str] = ...) -> None: ...

class MeetingActionablesSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "meeting_id", "activity_tag_id", "search_key")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    MEETING_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TAG_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: MEETING_ACTIONABLE_SORT_KEY
    entity_uuid: str
    meeting_id: int
    activity_tag_id: int
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[MEETING_ACTIONABLE_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., meeting_id: _Optional[int] = ..., activity_tag_id: _Optional[int] = ..., search_key: _Optional[str] = ...) -> None: ...

class MeetingsServicePaginatedActionablesResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[MeetingActionable]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[MeetingActionable, _Mapping]]] = ...) -> None: ...

class MeetingsServiceEmployeeCreateRequest(_message.Message):
    __slots__ = ("user_comment", "meeting_id", "employee_id", "rsvp")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEETING_ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    RSVP_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    meeting_id: int
    employee_id: int
    rsvp: MEETING_RSVP
    def __init__(self, user_comment: _Optional[str] = ..., meeting_id: _Optional[int] = ..., employee_id: _Optional[int] = ..., rsvp: _Optional[_Union[MEETING_RSVP, str]] = ...) -> None: ...

class MeetingEmployee(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "meeting_id", "employee_id", "rsvp")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEETING_ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    RSVP_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    meeting_id: int
    employee_id: int
    rsvp: MEETING_RSVP
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., meeting_id: _Optional[int] = ..., employee_id: _Optional[int] = ..., rsvp: _Optional[_Union[MEETING_RSVP, str]] = ...) -> None: ...

class MeetingEmployeesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[MeetingEmployee]
    def __init__(self, list: _Optional[_Iterable[_Union[MeetingEmployee, _Mapping]]] = ...) -> None: ...

class MeetingsServiceAssociateCreateRequest(_message.Message):
    __slots__ = ("user_comment", "meeting_id", "associate_id", "rsvp")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEETING_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    RSVP_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    meeting_id: int
    associate_id: int
    rsvp: MEETING_RSVP
    def __init__(self, user_comment: _Optional[str] = ..., meeting_id: _Optional[int] = ..., associate_id: _Optional[int] = ..., rsvp: _Optional[_Union[MEETING_RSVP, str]] = ...) -> None: ...

class MeetingAssociate(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "meeting_id", "associate_id", "rsvp")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEETING_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    RSVP_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    meeting_id: int
    associate_id: int
    rsvp: MEETING_RSVP
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., meeting_id: _Optional[int] = ..., associate_id: _Optional[int] = ..., rsvp: _Optional[_Union[MEETING_RSVP, str]] = ...) -> None: ...

class MeetingAssociatesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[MeetingAssociate]
    def __init__(self, list: _Optional[_Iterable[_Union[MeetingAssociate, _Mapping]]] = ...) -> None: ...

class MeetingsServiceImportEmployeesRequest(_message.Message):
    __slots__ = ("user_comment", "meeting_id", "resource_id", "delete_existing")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    MEETING_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    DELETE_EXISTING_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    meeting_id: int
    resource_id: int
    delete_existing: bool
    def __init__(self, user_comment: _Optional[str] = ..., meeting_id: _Optional[int] = ..., resource_id: _Optional[int] = ..., delete_existing: _Optional[bool] = ...) -> None: ...

class MeetingsServiceSetRSVPRequest(_message.Message):
    __slots__ = ("user_comment", "uuid", "rsvp")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    RSVP_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    rsvp: MEETING_RSVP
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ..., rsvp: _Optional[_Union[MEETING_RSVP, str]] = ...) -> None: ...
