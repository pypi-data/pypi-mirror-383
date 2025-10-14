from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ACTIVITY_LIFECYCLE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTIVITY_LIFECYCLE_ANY_UNSPECIFIED: _ClassVar[ACTIVITY_LIFECYCLE]
    ACTIVITY_LIFECYCLE_OPEN: _ClassVar[ACTIVITY_LIFECYCLE]
    ACTIVITY_LIFECYCLE_COMPLETED: _ClassVar[ACTIVITY_LIFECYCLE]
    ACTIVITY_LIFECYCLE_CANCELLED: _ClassVar[ACTIVITY_LIFECYCLE]

class ACTIVITY_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTIVITY_SORT_KEY_ID_UNSPECIFIED: _ClassVar[ACTIVITY_SORT_KEY]
    ACTIVITY_SORT_KEY_CREATED_AT: _ClassVar[ACTIVITY_SORT_KEY]
    ACTIVITY_SORT_KEY_MODIFIED_AT: _ClassVar[ACTIVITY_SORT_KEY]
    ACTIVITY_SORT_KEY_COMPLETED_ON: _ClassVar[ACTIVITY_SORT_KEY]
    ACTIVITY_SORT_KEY_TITLE: _ClassVar[ACTIVITY_SORT_KEY]
    ACTIVITY_SORT_KEY_STARTS_AT: _ClassVar[ACTIVITY_SORT_KEY]
    ACTIVITY_SORT_KEY_DUE_BY: _ClassVar[ACTIVITY_SORT_KEY]

class ACTIVITY_ACTION_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTIVITY_ACTION_SORT_KEY_ID_UNSPECIFIED: _ClassVar[ACTIVITY_ACTION_SORT_KEY]
    ACTIVITY_ACTION_SORT_KEY_CREATED_AT: _ClassVar[ACTIVITY_ACTION_SORT_KEY]
    ACTIVITY_ACTION_SORT_KEY_MODIFIED_AT: _ClassVar[ACTIVITY_ACTION_SORT_KEY]
    ACTIVITY_ACTION_SORT_KEY_TITLE: _ClassVar[ACTIVITY_ACTION_SORT_KEY]
    ACTIVITY_ACTION_SORT_KEY_ACTION_CODE_ID: _ClassVar[ACTIVITY_ACTION_SORT_KEY]
    ACTIVITY_ACTION_SORT_KEY_POINTS: _ClassVar[ACTIVITY_ACTION_SORT_KEY]

class ACTIVITY_TIMER_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTIVITY_TIMER_SORT_KEY_ID_UNSPECIFIED: _ClassVar[ACTIVITY_TIMER_SORT_KEY]
    ACTIVITY_TIMER_SORT_KEY_CREATED_AT: _ClassVar[ACTIVITY_TIMER_SORT_KEY]
    ACTIVITY_TIMER_SORT_KEY_MODIFIED_AT: _ClassVar[ACTIVITY_TIMER_SORT_KEY]
    ACTIVITY_TIMER_SORT_KEY_ACTIVITY_ID: _ClassVar[ACTIVITY_TIMER_SORT_KEY]
    ACTIVITY_TIMER_SORT_KEY_ACTIVITY_ACTION_ID: _ClassVar[ACTIVITY_TIMER_SORT_KEY]
    ACTIVITY_TIMER_SORT_KEY_EMPLOYEE_ID: _ClassVar[ACTIVITY_TIMER_SORT_KEY]
    ACTIVITY_TIMER_SORT_KEY_START_AT: _ClassVar[ACTIVITY_TIMER_SORT_KEY]
    ACTIVITY_TIMER_SORT_KEY_END_AT: _ClassVar[ACTIVITY_TIMER_SORT_KEY]
    ACTIVITY_TIMER_SORT_KEY_COMPLETION_PERCENTAGE: _ClassVar[ACTIVITY_TIMER_SORT_KEY]
ACTIVITY_LIFECYCLE_ANY_UNSPECIFIED: ACTIVITY_LIFECYCLE
ACTIVITY_LIFECYCLE_OPEN: ACTIVITY_LIFECYCLE
ACTIVITY_LIFECYCLE_COMPLETED: ACTIVITY_LIFECYCLE
ACTIVITY_LIFECYCLE_CANCELLED: ACTIVITY_LIFECYCLE
ACTIVITY_SORT_KEY_ID_UNSPECIFIED: ACTIVITY_SORT_KEY
ACTIVITY_SORT_KEY_CREATED_AT: ACTIVITY_SORT_KEY
ACTIVITY_SORT_KEY_MODIFIED_AT: ACTIVITY_SORT_KEY
ACTIVITY_SORT_KEY_COMPLETED_ON: ACTIVITY_SORT_KEY
ACTIVITY_SORT_KEY_TITLE: ACTIVITY_SORT_KEY
ACTIVITY_SORT_KEY_STARTS_AT: ACTIVITY_SORT_KEY
ACTIVITY_SORT_KEY_DUE_BY: ACTIVITY_SORT_KEY
ACTIVITY_ACTION_SORT_KEY_ID_UNSPECIFIED: ACTIVITY_ACTION_SORT_KEY
ACTIVITY_ACTION_SORT_KEY_CREATED_AT: ACTIVITY_ACTION_SORT_KEY
ACTIVITY_ACTION_SORT_KEY_MODIFIED_AT: ACTIVITY_ACTION_SORT_KEY
ACTIVITY_ACTION_SORT_KEY_TITLE: ACTIVITY_ACTION_SORT_KEY
ACTIVITY_ACTION_SORT_KEY_ACTION_CODE_ID: ACTIVITY_ACTION_SORT_KEY
ACTIVITY_ACTION_SORT_KEY_POINTS: ACTIVITY_ACTION_SORT_KEY
ACTIVITY_TIMER_SORT_KEY_ID_UNSPECIFIED: ACTIVITY_TIMER_SORT_KEY
ACTIVITY_TIMER_SORT_KEY_CREATED_AT: ACTIVITY_TIMER_SORT_KEY
ACTIVITY_TIMER_SORT_KEY_MODIFIED_AT: ACTIVITY_TIMER_SORT_KEY
ACTIVITY_TIMER_SORT_KEY_ACTIVITY_ID: ACTIVITY_TIMER_SORT_KEY
ACTIVITY_TIMER_SORT_KEY_ACTIVITY_ACTION_ID: ACTIVITY_TIMER_SORT_KEY
ACTIVITY_TIMER_SORT_KEY_EMPLOYEE_ID: ACTIVITY_TIMER_SORT_KEY
ACTIVITY_TIMER_SORT_KEY_START_AT: ACTIVITY_TIMER_SORT_KEY
ACTIVITY_TIMER_SORT_KEY_END_AT: ACTIVITY_TIMER_SORT_KEY
ACTIVITY_TIMER_SORT_KEY_COMPLETION_PERCENTAGE: ACTIVITY_TIMER_SORT_KEY

class LogbookLogActivityLC(_message.Message):
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
    operation: ACTIVITY_LIFECYCLE
    username: str
    name: str
    user_id: int
    app_comment: str
    user_comment: str
    def __init__(self, id: _Optional[int] = ..., is_active: _Optional[bool] = ..., timestamp: _Optional[int] = ..., ref_uuid: _Optional[str] = ..., operation: _Optional[_Union[ACTIVITY_LIFECYCLE, str]] = ..., username: _Optional[str] = ..., name: _Optional[str] = ..., user_id: _Optional[int] = ..., app_comment: _Optional[str] = ..., user_comment: _Optional[str] = ...) -> None: ...

class ActivitiesServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "activity_group_id", "activity_status_id", "title", "starts_at", "due_by", "description", "assign_self_as_owner", "assign_self_as_supervisor")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_STATUS_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_FIELD_NUMBER: _ClassVar[int]
    DUE_BY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ASSIGN_SELF_AS_OWNER_FIELD_NUMBER: _ClassVar[int]
    ASSIGN_SELF_AS_SUPERVISOR_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    activity_group_id: int
    activity_status_id: int
    title: str
    starts_at: int
    due_by: int
    description: str
    assign_self_as_owner: bool
    assign_self_as_supervisor: bool
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., activity_group_id: _Optional[int] = ..., activity_status_id: _Optional[int] = ..., title: _Optional[str] = ..., starts_at: _Optional[int] = ..., due_by: _Optional[int] = ..., description: _Optional[str] = ..., assign_self_as_owner: _Optional[bool] = ..., assign_self_as_supervisor: _Optional[bool] = ...) -> None: ...

class ActivitiesServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "activity_group_id", "activity_status_id", "title", "starts_at", "due_by", "description")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_STATUS_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_FIELD_NUMBER: _ClassVar[int]
    DUE_BY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    activity_group_id: int
    activity_status_id: int
    title: str
    starts_at: int
    due_by: int
    description: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., activity_group_id: _Optional[int] = ..., activity_status_id: _Optional[int] = ..., title: _Optional[str] = ..., starts_at: _Optional[int] = ..., due_by: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class Activity(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "status", "logs", "completed_on", "vault_folder_id", "activity_group_id", "activity_status_id", "title", "starts_at", "due_by", "description", "internal_ref")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_STATUS_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_FIELD_NUMBER: _ClassVar[int]
    DUE_BY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_REF_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    status: ACTIVITY_LIFECYCLE
    logs: _containers.RepeatedCompositeFieldContainer[LogbookLogActivityLC]
    completed_on: int
    vault_folder_id: int
    activity_group_id: int
    activity_status_id: int
    title: str
    starts_at: int
    due_by: int
    description: str
    internal_ref: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., status: _Optional[_Union[ACTIVITY_LIFECYCLE, str]] = ..., logs: _Optional[_Iterable[_Union[LogbookLogActivityLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., activity_group_id: _Optional[int] = ..., activity_status_id: _Optional[int] = ..., title: _Optional[str] = ..., starts_at: _Optional[int] = ..., due_by: _Optional[int] = ..., description: _Optional[str] = ..., internal_ref: _Optional[str] = ...) -> None: ...

class ActivitiesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[Activity]
    def __init__(self, list: _Optional[_Iterable[_Union[Activity, _Mapping]]] = ...) -> None: ...

class ActivityStatistics(_message.Message):
    __slots__ = ("total_duration", "total_completion_percentage", "total_points")
    TOTAL_DURATION_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COMPLETION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_POINTS_FIELD_NUMBER: _ClassVar[int]
    total_duration: int
    total_completion_percentage: int
    total_points: int
    def __init__(self, total_duration: _Optional[int] = ..., total_completion_percentage: _Optional[int] = ..., total_points: _Optional[int] = ...) -> None: ...

class ActivitiesServicePaginationReq(_message.Message):
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
    sort_key: ACTIVITY_SORT_KEY
    status: ACTIVITY_LIFECYCLE
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ACTIVITY_SORT_KEY, str]] = ..., status: _Optional[_Union[ACTIVITY_LIFECYCLE, str]] = ...) -> None: ...

class ActivitiesServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[Activity]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[Activity, _Mapping]]] = ...) -> None: ...

class ActivitiesServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "completed_on_start", "completed_on_end", "internal_ref", "title", "starts_at_start", "starts_at_end", "due_by_start", "due_by_end", "activity_group_id", "activity_status_id", "project_id", "owner_employee_id", "supervisor_employee_id", "goal_id", "action_code_id", "activity_tag_id")
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
    STARTS_AT_START_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_END_FIELD_NUMBER: _ClassVar[int]
    DUE_BY_START_FIELD_NUMBER: _ClassVar[int]
    DUE_BY_END_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_STATUS_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    GOAL_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_CODE_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TAG_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: ACTIVITY_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: ACTIVITY_LIFECYCLE
    completed_on_start: int
    completed_on_end: int
    internal_ref: str
    title: str
    starts_at_start: int
    starts_at_end: int
    due_by_start: int
    due_by_end: int
    activity_group_id: int
    activity_status_id: int
    project_id: int
    owner_employee_id: int
    supervisor_employee_id: int
    goal_id: int
    action_code_id: int
    activity_tag_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ACTIVITY_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[ACTIVITY_LIFECYCLE, str]] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., internal_ref: _Optional[str] = ..., title: _Optional[str] = ..., starts_at_start: _Optional[int] = ..., starts_at_end: _Optional[int] = ..., due_by_start: _Optional[int] = ..., due_by_end: _Optional[int] = ..., activity_group_id: _Optional[int] = ..., activity_status_id: _Optional[int] = ..., project_id: _Optional[int] = ..., owner_employee_id: _Optional[int] = ..., supervisor_employee_id: _Optional[int] = ..., goal_id: _Optional[int] = ..., action_code_id: _Optional[int] = ..., activity_tag_id: _Optional[int] = ...) -> None: ...

class ActivitiesServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "completed_on_start", "completed_on_end", "internal_ref", "title", "starts_at_start", "starts_at_end", "due_by_start", "due_by_end", "activity_group_id", "activity_status_id", "project_id", "owner_employee_id", "supervisor_employee_id", "goal_id", "action_code_id", "activity_tag_id")
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
    STARTS_AT_START_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_END_FIELD_NUMBER: _ClassVar[int]
    DUE_BY_START_FIELD_NUMBER: _ClassVar[int]
    DUE_BY_END_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_STATUS_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    GOAL_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_CODE_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TAG_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    status: ACTIVITY_LIFECYCLE
    completed_on_start: int
    completed_on_end: int
    internal_ref: str
    title: str
    starts_at_start: int
    starts_at_end: int
    due_by_start: int
    due_by_end: int
    activity_group_id: int
    activity_status_id: int
    project_id: int
    owner_employee_id: int
    supervisor_employee_id: int
    goal_id: int
    action_code_id: int
    activity_tag_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[ACTIVITY_LIFECYCLE, str]] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., internal_ref: _Optional[str] = ..., title: _Optional[str] = ..., starts_at_start: _Optional[int] = ..., starts_at_end: _Optional[int] = ..., due_by_start: _Optional[int] = ..., due_by_end: _Optional[int] = ..., activity_group_id: _Optional[int] = ..., activity_status_id: _Optional[int] = ..., project_id: _Optional[int] = ..., owner_employee_id: _Optional[int] = ..., supervisor_employee_id: _Optional[int] = ..., goal_id: _Optional[int] = ..., action_code_id: _Optional[int] = ..., activity_tag_id: _Optional[int] = ...) -> None: ...

class ActivitiesServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "activity_group_id", "activity_status_id", "project_id", "owner_employee_id", "supervisor_employee_id", "goal_id", "action_code_id", "activity_tag_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_STATUS_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    SUPERVISOR_EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    GOAL_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_CODE_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TAG_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: ACTIVITY_SORT_KEY
    entity_uuid: str
    status: ACTIVITY_LIFECYCLE
    search_key: str
    activity_group_id: int
    activity_status_id: int
    project_id: int
    owner_employee_id: int
    supervisor_employee_id: int
    goal_id: int
    action_code_id: int
    activity_tag_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ACTIVITY_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[ACTIVITY_LIFECYCLE, str]] = ..., search_key: _Optional[str] = ..., activity_group_id: _Optional[int] = ..., activity_status_id: _Optional[int] = ..., project_id: _Optional[int] = ..., owner_employee_id: _Optional[int] = ..., supervisor_employee_id: _Optional[int] = ..., goal_id: _Optional[int] = ..., action_code_id: _Optional[int] = ..., activity_tag_id: _Optional[int] = ...) -> None: ...

class ActivitiesServiceActionCreateRequest(_message.Message):
    __slots__ = ("user_comment", "employee_id", "activity_id", "title", "content", "action_code_id", "points")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ACTION_CODE_ID_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    employee_id: int
    activity_id: int
    title: str
    content: str
    action_code_id: int
    points: int
    def __init__(self, user_comment: _Optional[str] = ..., employee_id: _Optional[int] = ..., activity_id: _Optional[int] = ..., title: _Optional[str] = ..., content: _Optional[str] = ..., action_code_id: _Optional[int] = ..., points: _Optional[int] = ...) -> None: ...

class ActivitiesServiceActionUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "employee_id", "title", "content", "action_code_id", "points")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ACTION_CODE_ID_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    employee_id: int
    title: str
    content: str
    action_code_id: int
    points: int
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., employee_id: _Optional[int] = ..., title: _Optional[str] = ..., content: _Optional[str] = ..., action_code_id: _Optional[int] = ..., points: _Optional[int] = ...) -> None: ...

class ActivityAction(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "employee_id", "activity_id", "title", "content", "action_code_id", "points", "statistics")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    ACTION_CODE_ID_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    STATISTICS_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    employee_id: int
    activity_id: int
    title: str
    content: str
    action_code_id: int
    points: int
    statistics: ActivityActionStatistics
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., employee_id: _Optional[int] = ..., activity_id: _Optional[int] = ..., title: _Optional[str] = ..., content: _Optional[str] = ..., action_code_id: _Optional[int] = ..., points: _Optional[int] = ..., statistics: _Optional[_Union[ActivityActionStatistics, _Mapping]] = ...) -> None: ...

class ActivityActionStatistics(_message.Message):
    __slots__ = ("total_duration", "total_completion_percentage")
    TOTAL_DURATION_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COMPLETION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    total_duration: int
    total_completion_percentage: int
    def __init__(self, total_duration: _Optional[int] = ..., total_completion_percentage: _Optional[int] = ...) -> None: ...

class ActivityActionsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ActivityAction]
    def __init__(self, list: _Optional[_Iterable[_Union[ActivityAction, _Mapping]]] = ...) -> None: ...

class ActivityActionHistoryRequest(_message.Message):
    __slots__ = ("activity_id", "action_code_id")
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_CODE_ID_FIELD_NUMBER: _ClassVar[int]
    activity_id: int
    action_code_id: int
    def __init__(self, activity_id: _Optional[int] = ..., action_code_id: _Optional[int] = ...) -> None: ...

class ActivityActionsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "employee_id", "activity_id", "action_code_id", "search_key")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_CODE_ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: ACTIVITY_ACTION_SORT_KEY
    entity_uuid: str
    employee_id: int
    activity_id: int
    action_code_id: int
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ACTIVITY_ACTION_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., employee_id: _Optional[int] = ..., activity_id: _Optional[int] = ..., action_code_id: _Optional[int] = ..., search_key: _Optional[str] = ...) -> None: ...

class ActivitiesServicePaginatedActionsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[ActivityAction]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[ActivityAction, _Mapping]]] = ...) -> None: ...

class ActivitiesServiceActionWithTimerCreateRequest(_message.Message):
    __slots__ = ("user_comment", "activity_id", "goal_id", "employee_id", "points", "start_at", "end_at", "completion_percentage", "action_code_id", "title", "content")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    GOAL_ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    START_AT_FIELD_NUMBER: _ClassVar[int]
    END_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    ACTION_CODE_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    activity_id: int
    goal_id: int
    employee_id: int
    points: int
    start_at: int
    end_at: int
    completion_percentage: int
    action_code_id: int
    title: str
    content: str
    def __init__(self, user_comment: _Optional[str] = ..., activity_id: _Optional[int] = ..., goal_id: _Optional[int] = ..., employee_id: _Optional[int] = ..., points: _Optional[int] = ..., start_at: _Optional[int] = ..., end_at: _Optional[int] = ..., completion_percentage: _Optional[int] = ..., action_code_id: _Optional[int] = ..., title: _Optional[str] = ..., content: _Optional[str] = ...) -> None: ...

class ActivitiesServiceActivityTagAssociationCreateRequest(_message.Message):
    __slots__ = ("user_comment", "activity_id", "activity_tag_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TAG_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    activity_id: int
    activity_tag_id: int
    def __init__(self, user_comment: _Optional[str] = ..., activity_id: _Optional[int] = ..., activity_tag_id: _Optional[int] = ...) -> None: ...

class ActivityTagAssociation(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "activity_id", "activity_tag_id")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_TAG_ID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    activity_id: int
    activity_tag_id: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., activity_id: _Optional[int] = ..., activity_tag_id: _Optional[int] = ...) -> None: ...

class ActivityTagAssociationsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ActivityTagAssociation]
    def __init__(self, list: _Optional[_Iterable[_Union[ActivityTagAssociation, _Mapping]]] = ...) -> None: ...

class ActivitiesServiceOwnerCreateRequest(_message.Message):
    __slots__ = ("user_comment", "activity_id", "employee_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    activity_id: int
    employee_id: int
    def __init__(self, user_comment: _Optional[str] = ..., activity_id: _Optional[int] = ..., employee_id: _Optional[int] = ...) -> None: ...

class ActivityOwner(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "activity_id", "employee_id")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    activity_id: int
    employee_id: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., activity_id: _Optional[int] = ..., employee_id: _Optional[int] = ...) -> None: ...

class ActivityOwnersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ActivityOwner]
    def __init__(self, list: _Optional[_Iterable[_Union[ActivityOwner, _Mapping]]] = ...) -> None: ...

class ActivitiesServiceImportOwnersRequest(_message.Message):
    __slots__ = ("user_comment", "activity_id", "resource_id", "delete_existing")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    DELETE_EXISTING_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    activity_id: int
    resource_id: int
    delete_existing: bool
    def __init__(self, user_comment: _Optional[str] = ..., activity_id: _Optional[int] = ..., resource_id: _Optional[int] = ..., delete_existing: _Optional[bool] = ...) -> None: ...

class ActivitiesServiceSupervisorCreateRequest(_message.Message):
    __slots__ = ("user_comment", "activity_id", "employee_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    activity_id: int
    employee_id: int
    def __init__(self, user_comment: _Optional[str] = ..., activity_id: _Optional[int] = ..., employee_id: _Optional[int] = ...) -> None: ...

class ActivitySupervisor(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "activity_id", "employee_id")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    activity_id: int
    employee_id: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., activity_id: _Optional[int] = ..., employee_id: _Optional[int] = ...) -> None: ...

class ActivitySupervisorsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ActivitySupervisor]
    def __init__(self, list: _Optional[_Iterable[_Union[ActivitySupervisor, _Mapping]]] = ...) -> None: ...

class ActivitiesServiceTimerCreateRequest(_message.Message):
    __slots__ = ("user_comment", "activity_action_id", "goal_id", "employee_id", "start_at", "end_at", "completion_percentage", "description")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    GOAL_ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    START_AT_FIELD_NUMBER: _ClassVar[int]
    END_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    activity_action_id: int
    goal_id: int
    employee_id: int
    start_at: int
    end_at: int
    completion_percentage: int
    description: str
    def __init__(self, user_comment: _Optional[str] = ..., activity_action_id: _Optional[int] = ..., goal_id: _Optional[int] = ..., employee_id: _Optional[int] = ..., start_at: _Optional[int] = ..., end_at: _Optional[int] = ..., completion_percentage: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class ActivitiesServiceTimerEndRequest(_message.Message):
    __slots__ = ("user_comment", "id", "goal_id", "end_at", "completion_percentage", "description")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    GOAL_ID_FIELD_NUMBER: _ClassVar[int]
    END_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    goal_id: int
    end_at: int
    completion_percentage: int
    description: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., goal_id: _Optional[int] = ..., end_at: _Optional[int] = ..., completion_percentage: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class ActivityTimer(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "user_comment", "activity_id", "activity_action_id", "goal_id", "employee_id", "start_at", "end_at", "completion_percentage", "description")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    GOAL_ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    START_AT_FIELD_NUMBER: _ClassVar[int]
    END_AT_FIELD_NUMBER: _ClassVar[int]
    COMPLETION_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    user_comment: str
    activity_id: int
    activity_action_id: int
    goal_id: int
    employee_id: int
    start_at: int
    end_at: int
    completion_percentage: int
    description: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., user_comment: _Optional[str] = ..., activity_id: _Optional[int] = ..., activity_action_id: _Optional[int] = ..., goal_id: _Optional[int] = ..., employee_id: _Optional[int] = ..., start_at: _Optional[int] = ..., end_at: _Optional[int] = ..., completion_percentage: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class ActivityTimersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ActivityTimer]
    def __init__(self, list: _Optional[_Iterable[_Union[ActivityTimer, _Mapping]]] = ...) -> None: ...

class ActivityTimersSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "activity_id", "activity_action_id", "goal_id", "employee_id", "starts_at_start", "starts_at_end", "ends_at_start", "ends_at_end", "search_key")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVITY_ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    GOAL_ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_START_FIELD_NUMBER: _ClassVar[int]
    STARTS_AT_END_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_START_FIELD_NUMBER: _ClassVar[int]
    ENDS_AT_END_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: ACTIVITY_TIMER_SORT_KEY
    entity_uuid: str
    activity_id: int
    activity_action_id: int
    goal_id: int
    employee_id: int
    starts_at_start: int
    starts_at_end: int
    ends_at_start: int
    ends_at_end: int
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ACTIVITY_TIMER_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., activity_id: _Optional[int] = ..., activity_action_id: _Optional[int] = ..., goal_id: _Optional[int] = ..., employee_id: _Optional[int] = ..., starts_at_start: _Optional[int] = ..., starts_at_end: _Optional[int] = ..., ends_at_start: _Optional[int] = ..., ends_at_end: _Optional[int] = ..., search_key: _Optional[str] = ...) -> None: ...

class ActivitiesServicePaginatedTimersResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[ActivityTimer]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[ActivityTimer, _Mapping]]] = ...) -> None: ...
