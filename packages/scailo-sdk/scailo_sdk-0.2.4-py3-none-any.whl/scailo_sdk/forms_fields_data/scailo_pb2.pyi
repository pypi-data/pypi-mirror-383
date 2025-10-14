from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from forms_fields import scailo_pb2 as _scailo_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FORM_FIELD_FILTER_OPERATOR(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FORM_FIELD_FILTER_OPERATOR_SIMILARITY_UNSPECIFIED: _ClassVar[FORM_FIELD_FILTER_OPERATOR]
    FORM_FIELD_FILTER_OPERATOR_EQUALITY: _ClassVar[FORM_FIELD_FILTER_OPERATOR]
    FORM_FIELD_FILTER_OPERATOR_LESS_THAN: _ClassVar[FORM_FIELD_FILTER_OPERATOR]
    FORM_FIELD_FILTER_OPERATOR_LESS_THAN_OR_EQUAL: _ClassVar[FORM_FIELD_FILTER_OPERATOR]
    FORM_FIELD_FILTER_OPERATOR_GREATER_THAN: _ClassVar[FORM_FIELD_FILTER_OPERATOR]
    FORM_FIELD_FILTER_OPERATOR_GREATER_THAN_OR_EQUAL: _ClassVar[FORM_FIELD_FILTER_OPERATOR]
FORM_FIELD_FILTER_OPERATOR_SIMILARITY_UNSPECIFIED: FORM_FIELD_FILTER_OPERATOR
FORM_FIELD_FILTER_OPERATOR_EQUALITY: FORM_FIELD_FILTER_OPERATOR
FORM_FIELD_FILTER_OPERATOR_LESS_THAN: FORM_FIELD_FILTER_OPERATOR
FORM_FIELD_FILTER_OPERATOR_LESS_THAN_OR_EQUAL: FORM_FIELD_FILTER_OPERATOR
FORM_FIELD_FILTER_OPERATOR_GREATER_THAN: FORM_FIELD_FILTER_OPERATOR
FORM_FIELD_FILTER_OPERATOR_GREATER_THAN_OR_EQUAL: FORM_FIELD_FILTER_OPERATOR

class FormFieldDatum(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "form_field_id", "form_field", "ref_uuid", "value", "selected_values", "need_approval")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    FORM_FIELD_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_FIELD_FIELD_NUMBER: _ClassVar[int]
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    SELECTED_VALUES_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    form_field_id: int
    form_field: _scailo_pb2_1.FormField
    ref_uuid: str
    value: str
    selected_values: _containers.RepeatedScalarFieldContainer[str]
    need_approval: bool
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., form_field_id: _Optional[int] = ..., form_field: _Optional[_Union[_scailo_pb2_1.FormField, _Mapping]] = ..., ref_uuid: _Optional[str] = ..., value: _Optional[str] = ..., selected_values: _Optional[_Iterable[str]] = ..., need_approval: _Optional[bool] = ...) -> None: ...

class FormFieldDatumCreateRequest(_message.Message):
    __slots__ = ("form_field_id", "value", "selected_values")
    FORM_FIELD_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    SELECTED_VALUES_FIELD_NUMBER: _ClassVar[int]
    form_field_id: int
    value: str
    selected_values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, form_field_id: _Optional[int] = ..., value: _Optional[str] = ..., selected_values: _Optional[_Iterable[str]] = ...) -> None: ...

class FormFieldDatumList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[FormFieldDatum]
    def __init__(self, list: _Optional[_Iterable[_Union[FormFieldDatum, _Mapping]]] = ...) -> None: ...

class FormFieldDatumHistoryRequest(_message.Message):
    __slots__ = ("form_field_id", "ref_uuid")
    FORM_FIELD_ID_FIELD_NUMBER: _ClassVar[int]
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    form_field_id: int
    ref_uuid: str
    def __init__(self, form_field_id: _Optional[int] = ..., ref_uuid: _Optional[str] = ...) -> None: ...

class FormFieldDatumFilterRequest(_message.Message):
    __slots__ = ("form_field_id", "value", "operator")
    FORM_FIELD_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    OPERATOR_FIELD_NUMBER: _ClassVar[int]
    form_field_id: int
    value: str
    operator: FORM_FIELD_FILTER_OPERATOR
    def __init__(self, form_field_id: _Optional[int] = ..., value: _Optional[str] = ..., operator: _Optional[_Union[FORM_FIELD_FILTER_OPERATOR, str]] = ...) -> None: ...
