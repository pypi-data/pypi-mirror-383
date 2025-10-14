from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FORM_FIELD_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FORM_FIELD_SORT_KEY_ID_UNSPECIFIED: _ClassVar[FORM_FIELD_SORT_KEY]
    FORM_FIELD_SORT_KEY_CREATED_AT: _ClassVar[FORM_FIELD_SORT_KEY]
    FORM_FIELD_SORT_KEY_MODIFIED_AT: _ClassVar[FORM_FIELD_SORT_KEY]
    FORM_FIELD_SORT_KEY_NAME: _ClassVar[FORM_FIELD_SORT_KEY]
    FORM_FIELD_SORT_KEY_CODE: _ClassVar[FORM_FIELD_SORT_KEY]
    FORM_FIELD_SORT_KEY_SECTION_ID_AND_RECORD_ID: _ClassVar[FORM_FIELD_SORT_KEY]
FORM_FIELD_SORT_KEY_ID_UNSPECIFIED: FORM_FIELD_SORT_KEY
FORM_FIELD_SORT_KEY_CREATED_AT: FORM_FIELD_SORT_KEY
FORM_FIELD_SORT_KEY_MODIFIED_AT: FORM_FIELD_SORT_KEY
FORM_FIELD_SORT_KEY_NAME: FORM_FIELD_SORT_KEY
FORM_FIELD_SORT_KEY_CODE: FORM_FIELD_SORT_KEY
FORM_FIELD_SORT_KEY_SECTION_ID_AND_RECORD_ID: FORM_FIELD_SORT_KEY

class FormField(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "name", "code", "type", "section_id", "width", "element", "placeholder", "regex", "defined_values", "printable", "highlightable")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SECTION_ID_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_FIELD_NUMBER: _ClassVar[int]
    PLACEHOLDER_FIELD_NUMBER: _ClassVar[int]
    REGEX_FIELD_NUMBER: _ClassVar[int]
    DEFINED_VALUES_FIELD_NUMBER: _ClassVar[int]
    PRINTABLE_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHTABLE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    name: str
    code: str
    type: _scailo_pb2.FORM_TYPE
    section_id: int
    width: str
    element: _scailo_pb2.FORM_FIELD_ELEMENT
    placeholder: str
    regex: str
    defined_values: _containers.RepeatedScalarFieldContainer[str]
    printable: bool
    highlightable: bool
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., type: _Optional[_Union[_scailo_pb2.FORM_TYPE, str]] = ..., section_id: _Optional[int] = ..., width: _Optional[str] = ..., element: _Optional[_Union[_scailo_pb2.FORM_FIELD_ELEMENT, str]] = ..., placeholder: _Optional[str] = ..., regex: _Optional[str] = ..., defined_values: _Optional[_Iterable[str]] = ..., printable: _Optional[bool] = ..., highlightable: _Optional[bool] = ...) -> None: ...

class FormsFieldsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[FormField]
    def __init__(self, list: _Optional[_Iterable[_Union[FormField, _Mapping]]] = ...) -> None: ...

class FormFieldPaginationResp(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[FormField]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[FormField, _Mapping]]] = ...) -> None: ...

class FormsFieldsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "name", "code", "type", "section_id", "width", "element", "placeholder", "regex", "defined_values", "printable", "highlightable")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SECTION_ID_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_FIELD_NUMBER: _ClassVar[int]
    PLACEHOLDER_FIELD_NUMBER: _ClassVar[int]
    REGEX_FIELD_NUMBER: _ClassVar[int]
    DEFINED_VALUES_FIELD_NUMBER: _ClassVar[int]
    PRINTABLE_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHTABLE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    name: str
    code: str
    type: _scailo_pb2.FORM_TYPE
    section_id: int
    width: str
    element: _scailo_pb2.FORM_FIELD_ELEMENT
    placeholder: str
    regex: str
    defined_values: _containers.RepeatedScalarFieldContainer[str]
    printable: bool
    highlightable: bool
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., type: _Optional[_Union[_scailo_pb2.FORM_TYPE, str]] = ..., section_id: _Optional[int] = ..., width: _Optional[str] = ..., element: _Optional[_Union[_scailo_pb2.FORM_FIELD_ELEMENT, str]] = ..., placeholder: _Optional[str] = ..., regex: _Optional[str] = ..., defined_values: _Optional[_Iterable[str]] = ..., printable: _Optional[bool] = ..., highlightable: _Optional[bool] = ...) -> None: ...

class FormsFieldsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "name", "code", "section_id", "width", "placeholder", "regex", "defined_values", "printable", "highlightable")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    SECTION_ID_FIELD_NUMBER: _ClassVar[int]
    WIDTH_FIELD_NUMBER: _ClassVar[int]
    PLACEHOLDER_FIELD_NUMBER: _ClassVar[int]
    REGEX_FIELD_NUMBER: _ClassVar[int]
    DEFINED_VALUES_FIELD_NUMBER: _ClassVar[int]
    PRINTABLE_FIELD_NUMBER: _ClassVar[int]
    HIGHLIGHTABLE_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    name: str
    code: str
    section_id: int
    width: str
    placeholder: str
    regex: str
    defined_values: _containers.RepeatedScalarFieldContainer[str]
    printable: bool
    highlightable: bool
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., section_id: _Optional[int] = ..., width: _Optional[str] = ..., placeholder: _Optional[str] = ..., regex: _Optional[str] = ..., defined_values: _Optional[_Iterable[str]] = ..., printable: _Optional[bool] = ..., highlightable: _Optional[bool] = ...) -> None: ...

class FormsFieldsServicePaginationReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: FORM_FIELD_SORT_KEY
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[FORM_FIELD_SORT_KEY, str]] = ...) -> None: ...

class FormsFieldsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "name", "type", "section_id", "code")
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
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SECTION_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: FORM_FIELD_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    name: str
    type: _scailo_pb2.FORM_TYPE
    section_id: int
    code: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[FORM_FIELD_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[_Union[_scailo_pb2.FORM_TYPE, str]] = ..., section_id: _Optional[int] = ..., code: _Optional[str] = ...) -> None: ...

class FormsFieldsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "name", "type", "section_id", "code")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SECTION_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    name: str
    type: _scailo_pb2.FORM_TYPE
    section_id: int
    code: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[_Union[_scailo_pb2.FORM_TYPE, str]] = ..., section_id: _Optional[int] = ..., code: _Optional[str] = ...) -> None: ...

class FormsFieldsServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "search_key", "type", "section_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SECTION_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: FORM_FIELD_SORT_KEY
    entity_uuid: str
    search_key: str
    type: _scailo_pb2.FORM_TYPE
    section_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[FORM_FIELD_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., search_key: _Optional[str] = ..., type: _Optional[_Union[_scailo_pb2.FORM_TYPE, str]] = ..., section_id: _Optional[int] = ...) -> None: ...
