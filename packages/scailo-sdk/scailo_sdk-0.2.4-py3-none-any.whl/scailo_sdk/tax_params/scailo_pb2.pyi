from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TAX_PARAM_VALUE_TYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TAX_PARAM_VALUE_TYPE_ANY_UNSPECIFIED: _ClassVar[TAX_PARAM_VALUE_TYPE]
    TAX_PARAM_VALUE_TYPE_PERCENTAGE: _ClassVar[TAX_PARAM_VALUE_TYPE]
    TAX_PARAM_VALUE_TYPE_FIXED: _ClassVar[TAX_PARAM_VALUE_TYPE]

class TAX_PARAM_CATEGORY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TAX_PARAM_CATEGORY_ANY_UNSPECIFIED: _ClassVar[TAX_PARAM_CATEGORY]
    TAX_PARAM_CATEGORY_GENERAL: _ClassVar[TAX_PARAM_CATEGORY]
    TAX_PARAM_CATEGORY_PAYROLL: _ClassVar[TAX_PARAM_CATEGORY]

class TAX_PARAM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TAX_PARAM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[TAX_PARAM_SORT_KEY]
    TAX_PARAM_SORT_KEY_CREATED_AT: _ClassVar[TAX_PARAM_SORT_KEY]
    TAX_PARAM_SORT_KEY_MODIFIED_AT: _ClassVar[TAX_PARAM_SORT_KEY]
    TAX_PARAM_SORT_KEY_APPROVED_ON: _ClassVar[TAX_PARAM_SORT_KEY]
    TAX_PARAM_SORT_KEY_APPROVED_BY: _ClassVar[TAX_PARAM_SORT_KEY]
    TAX_PARAM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[TAX_PARAM_SORT_KEY]
    TAX_PARAM_SORT_KEY_NAME: _ClassVar[TAX_PARAM_SORT_KEY]
    TAX_PARAM_SORT_KEY_TAX_RATE_PERCENTAGE: _ClassVar[TAX_PARAM_SORT_KEY]
    TAX_PARAM_SORT_KEY_CODE: _ClassVar[TAX_PARAM_SORT_KEY]
TAX_PARAM_VALUE_TYPE_ANY_UNSPECIFIED: TAX_PARAM_VALUE_TYPE
TAX_PARAM_VALUE_TYPE_PERCENTAGE: TAX_PARAM_VALUE_TYPE
TAX_PARAM_VALUE_TYPE_FIXED: TAX_PARAM_VALUE_TYPE
TAX_PARAM_CATEGORY_ANY_UNSPECIFIED: TAX_PARAM_CATEGORY
TAX_PARAM_CATEGORY_GENERAL: TAX_PARAM_CATEGORY
TAX_PARAM_CATEGORY_PAYROLL: TAX_PARAM_CATEGORY
TAX_PARAM_SORT_KEY_ID_UNSPECIFIED: TAX_PARAM_SORT_KEY
TAX_PARAM_SORT_KEY_CREATED_AT: TAX_PARAM_SORT_KEY
TAX_PARAM_SORT_KEY_MODIFIED_AT: TAX_PARAM_SORT_KEY
TAX_PARAM_SORT_KEY_APPROVED_ON: TAX_PARAM_SORT_KEY
TAX_PARAM_SORT_KEY_APPROVED_BY: TAX_PARAM_SORT_KEY
TAX_PARAM_SORT_KEY_APPROVER_ROLE_ID: TAX_PARAM_SORT_KEY
TAX_PARAM_SORT_KEY_NAME: TAX_PARAM_SORT_KEY
TAX_PARAM_SORT_KEY_TAX_RATE_PERCENTAGE: TAX_PARAM_SORT_KEY
TAX_PARAM_SORT_KEY_CODE: TAX_PARAM_SORT_KEY

class TaxParamsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "name", "code", "value_type", "tax_fixed_amount", "tax_rate_percentage", "divisor", "input_credit_percentage", "min_amount", "max_amount", "category", "description")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TAX_FIXED_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TAX_RATE_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    DIVISOR_FIELD_NUMBER: _ClassVar[int]
    INPUT_CREDIT_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    MIN_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    MAX_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    name: str
    code: str
    value_type: TAX_PARAM_VALUE_TYPE
    tax_fixed_amount: int
    tax_rate_percentage: int
    divisor: int
    input_credit_percentage: int
    min_amount: int
    max_amount: int
    category: TAX_PARAM_CATEGORY
    description: str
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., value_type: _Optional[_Union[TAX_PARAM_VALUE_TYPE, str]] = ..., tax_fixed_amount: _Optional[int] = ..., tax_rate_percentage: _Optional[int] = ..., divisor: _Optional[int] = ..., input_credit_percentage: _Optional[int] = ..., min_amount: _Optional[int] = ..., max_amount: _Optional[int] = ..., category: _Optional[_Union[TAX_PARAM_CATEGORY, str]] = ..., description: _Optional[str] = ...) -> None: ...

class TaxParamsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "name", "code", "description")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    name: str
    code: str
    description: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class TaxParam(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "name", "code", "value_type", "tax_fixed_amount", "tax_rate_percentage", "divisor", "input_credit_percentage", "min_amount", "max_amount", "category", "description")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TAX_FIXED_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    TAX_RATE_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    DIVISOR_FIELD_NUMBER: _ClassVar[int]
    INPUT_CREDIT_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    MIN_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    MAX_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    name: str
    code: str
    value_type: TAX_PARAM_VALUE_TYPE
    tax_fixed_amount: int
    tax_rate_percentage: int
    divisor: int
    input_credit_percentage: int
    min_amount: int
    max_amount: int
    category: TAX_PARAM_CATEGORY
    description: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., value_type: _Optional[_Union[TAX_PARAM_VALUE_TYPE, str]] = ..., tax_fixed_amount: _Optional[int] = ..., tax_rate_percentage: _Optional[int] = ..., divisor: _Optional[int] = ..., input_credit_percentage: _Optional[int] = ..., min_amount: _Optional[int] = ..., max_amount: _Optional[int] = ..., category: _Optional[_Union[TAX_PARAM_CATEGORY, str]] = ..., description: _Optional[str] = ...) -> None: ...

class TaxParamsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[TaxParam]
    def __init__(self, list: _Optional[_Iterable[_Union[TaxParam, _Mapping]]] = ...) -> None: ...

class TaxParamsServicePaginationReq(_message.Message):
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
    sort_key: TAX_PARAM_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[TAX_PARAM_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class TaxParamsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[TaxParam]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[TaxParam, _Mapping]]] = ...) -> None: ...

class TaxParamsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "name", "code", "value_type", "category")
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
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: TAX_PARAM_SORT_KEY
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
    name: str
    code: str
    value_type: TAX_PARAM_VALUE_TYPE
    category: TAX_PARAM_CATEGORY
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[TAX_PARAM_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., value_type: _Optional[_Union[TAX_PARAM_VALUE_TYPE, str]] = ..., category: _Optional[_Union[TAX_PARAM_CATEGORY, str]] = ...) -> None: ...

class TaxParamsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "name", "code", "value_type", "category")
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
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
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
    name: str
    code: str
    value_type: TAX_PARAM_VALUE_TYPE
    category: TAX_PARAM_CATEGORY
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., value_type: _Optional[_Union[TAX_PARAM_VALUE_TYPE, str]] = ..., category: _Optional[_Union[TAX_PARAM_CATEGORY, str]] = ...) -> None: ...

class TaxParamsServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "value_type", "category")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: TAX_PARAM_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    value_type: TAX_PARAM_VALUE_TYPE
    category: TAX_PARAM_CATEGORY
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[TAX_PARAM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., value_type: _Optional[_Union[TAX_PARAM_VALUE_TYPE, str]] = ..., category: _Optional[_Union[TAX_PARAM_CATEGORY, str]] = ...) -> None: ...
