from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from forms_fields_data import scailo_pb2 as _scailo_pb2_1
from magic_links import scailo_pb2 as _scailo_pb2_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class USER_TYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    USER_TYPE_ANY_UNSPECIFIED: _ClassVar[USER_TYPE]
    USER_TYPE_EMPLOYEE: _ClassVar[USER_TYPE]
    USER_TYPE_CLIENT: _ClassVar[USER_TYPE]
    USER_TYPE_VENDOR: _ClassVar[USER_TYPE]

class USER_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    USER_SORT_KEY_ID_UNSPECIFIED: _ClassVar[USER_SORT_KEY]
    USER_SORT_KEY_CREATED_AT: _ClassVar[USER_SORT_KEY]
    USER_SORT_KEY_MODIFIED_AT: _ClassVar[USER_SORT_KEY]
    USER_SORT_KEY_APPROVED_ON: _ClassVar[USER_SORT_KEY]
    USER_SORT_KEY_APPROVED_BY: _ClassVar[USER_SORT_KEY]
    USER_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[USER_SORT_KEY]
    USER_SORT_KEY_USERNAME: _ClassVar[USER_SORT_KEY]
    USER_SORT_KEY_NAME: _ClassVar[USER_SORT_KEY]
    USER_SORT_KEY_CODE: _ClassVar[USER_SORT_KEY]
    USER_SORT_KEY_EMAIL: _ClassVar[USER_SORT_KEY]
    USER_SORT_KEY_PHONE: _ClassVar[USER_SORT_KEY]
USER_TYPE_ANY_UNSPECIFIED: USER_TYPE
USER_TYPE_EMPLOYEE: USER_TYPE
USER_TYPE_CLIENT: USER_TYPE
USER_TYPE_VENDOR: USER_TYPE
USER_SORT_KEY_ID_UNSPECIFIED: USER_SORT_KEY
USER_SORT_KEY_CREATED_AT: USER_SORT_KEY
USER_SORT_KEY_MODIFIED_AT: USER_SORT_KEY
USER_SORT_KEY_APPROVED_ON: USER_SORT_KEY
USER_SORT_KEY_APPROVED_BY: USER_SORT_KEY
USER_SORT_KEY_APPROVER_ROLE_ID: USER_SORT_KEY
USER_SORT_KEY_USERNAME: USER_SORT_KEY
USER_SORT_KEY_NAME: USER_SORT_KEY
USER_SORT_KEY_CODE: USER_SORT_KEY
USER_SORT_KEY_EMAIL: USER_SORT_KEY
USER_SORT_KEY_PHONE: USER_SORT_KEY

class UsersServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "user_type", "vault_folder_id", "username", "code", "name", "plain_text_password", "role_id", "mobile_role_id", "email", "work_email", "phone", "birthday", "joining_date", "address", "city", "state", "country", "pin_code", "blood_group", "shift_group_id", "attendance_uom_id", "department_id", "payroll_group_id", "payroll_tax_group_id", "payroll_currency_id", "basic_pay_amount", "basic_pay_uom_id", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    USER_TYPE_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PLAIN_TEXT_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    MOBILE_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    WORK_EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    BIRTHDAY_FIELD_NUMBER: _ClassVar[int]
    JOINING_DATE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    PIN_CODE_FIELD_NUMBER: _ClassVar[int]
    BLOOD_GROUP_FIELD_NUMBER: _ClassVar[int]
    SHIFT_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    user_type: USER_TYPE
    vault_folder_id: int
    username: str
    code: str
    name: str
    plain_text_password: str
    role_id: int
    mobile_role_id: int
    email: str
    work_email: str
    phone: str
    birthday: str
    joining_date: str
    address: str
    city: str
    state: str
    country: str
    pin_code: str
    blood_group: str
    shift_group_id: int
    attendance_uom_id: int
    department_id: int
    payroll_group_id: int
    payroll_tax_group_id: int
    payroll_currency_id: int
    basic_pay_amount: int
    basic_pay_uom_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., user_type: _Optional[_Union[USER_TYPE, str]] = ..., vault_folder_id: _Optional[int] = ..., username: _Optional[str] = ..., code: _Optional[str] = ..., name: _Optional[str] = ..., plain_text_password: _Optional[str] = ..., role_id: _Optional[int] = ..., mobile_role_id: _Optional[int] = ..., email: _Optional[str] = ..., work_email: _Optional[str] = ..., phone: _Optional[str] = ..., birthday: _Optional[str] = ..., joining_date: _Optional[str] = ..., address: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., country: _Optional[str] = ..., pin_code: _Optional[str] = ..., blood_group: _Optional[str] = ..., shift_group_id: _Optional[int] = ..., attendance_uom_id: _Optional[int] = ..., department_id: _Optional[int] = ..., payroll_group_id: _Optional[int] = ..., payroll_tax_group_id: _Optional[int] = ..., payroll_currency_id: _Optional[int] = ..., basic_pay_amount: _Optional[int] = ..., basic_pay_uom_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class UsersServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "code", "name", "role_id", "mobile_role_id", "email", "work_email", "phone", "birthday", "joining_date", "address", "city", "state", "country", "pin_code", "blood_group", "shift_group_id", "attendance_uom_id", "department_id", "payroll_group_id", "payroll_tax_group_id", "payroll_currency_id", "basic_pay_amount", "basic_pay_uom_id", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    MOBILE_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    WORK_EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    BIRTHDAY_FIELD_NUMBER: _ClassVar[int]
    JOINING_DATE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    PIN_CODE_FIELD_NUMBER: _ClassVar[int]
    BLOOD_GROUP_FIELD_NUMBER: _ClassVar[int]
    SHIFT_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    code: str
    name: str
    role_id: int
    mobile_role_id: int
    email: str
    work_email: str
    phone: str
    birthday: str
    joining_date: str
    address: str
    city: str
    state: str
    country: str
    pin_code: str
    blood_group: str
    shift_group_id: int
    attendance_uom_id: int
    department_id: int
    payroll_group_id: int
    payroll_tax_group_id: int
    payroll_currency_id: int
    basic_pay_amount: int
    basic_pay_uom_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., code: _Optional[str] = ..., name: _Optional[str] = ..., role_id: _Optional[int] = ..., mobile_role_id: _Optional[int] = ..., email: _Optional[str] = ..., work_email: _Optional[str] = ..., phone: _Optional[str] = ..., birthday: _Optional[str] = ..., joining_date: _Optional[str] = ..., address: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., country: _Optional[str] = ..., pin_code: _Optional[str] = ..., blood_group: _Optional[str] = ..., shift_group_id: _Optional[int] = ..., attendance_uom_id: _Optional[int] = ..., department_id: _Optional[int] = ..., payroll_group_id: _Optional[int] = ..., payroll_tax_group_id: _Optional[int] = ..., payroll_currency_id: _Optional[int] = ..., basic_pay_amount: _Optional[int] = ..., basic_pay_uom_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class User(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "user_type", "vault_folder_id", "username", "code", "name", "role_id", "mobile_role_id", "email", "work_email", "phone", "birthday", "joining_date", "address", "city", "state", "country", "pin_code", "blood_group", "shift_group_id", "attendance_uom_id", "department_id", "payroll_group_id", "payroll_tax_group_id", "payroll_currency_id", "basic_pay_amount", "basic_pay_uom_id", "mfa_status", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    USER_TYPE_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    MOBILE_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    WORK_EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    BIRTHDAY_FIELD_NUMBER: _ClassVar[int]
    JOINING_DATE_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    PIN_CODE_FIELD_NUMBER: _ClassVar[int]
    BLOOD_GROUP_FIELD_NUMBER: _ClassVar[int]
    SHIFT_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    MFA_STATUS_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    user_type: USER_TYPE
    vault_folder_id: int
    username: str
    code: str
    name: str
    role_id: int
    mobile_role_id: int
    email: str
    work_email: str
    phone: str
    birthday: str
    joining_date: str
    address: str
    city: str
    state: str
    country: str
    pin_code: str
    blood_group: str
    shift_group_id: int
    attendance_uom_id: int
    department_id: int
    payroll_group_id: int
    payroll_tax_group_id: int
    payroll_currency_id: int
    basic_pay_amount: int
    basic_pay_uom_id: int
    mfa_status: bool
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., user_type: _Optional[_Union[USER_TYPE, str]] = ..., vault_folder_id: _Optional[int] = ..., username: _Optional[str] = ..., code: _Optional[str] = ..., name: _Optional[str] = ..., role_id: _Optional[int] = ..., mobile_role_id: _Optional[int] = ..., email: _Optional[str] = ..., work_email: _Optional[str] = ..., phone: _Optional[str] = ..., birthday: _Optional[str] = ..., joining_date: _Optional[str] = ..., address: _Optional[str] = ..., city: _Optional[str] = ..., state: _Optional[str] = ..., country: _Optional[str] = ..., pin_code: _Optional[str] = ..., blood_group: _Optional[str] = ..., shift_group_id: _Optional[int] = ..., attendance_uom_id: _Optional[int] = ..., department_id: _Optional[int] = ..., payroll_group_id: _Optional[int] = ..., payroll_tax_group_id: _Optional[int] = ..., payroll_currency_id: _Optional[int] = ..., basic_pay_amount: _Optional[int] = ..., basic_pay_uom_id: _Optional[int] = ..., mfa_status: _Optional[bool] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class UserPrimaryInfo(_message.Message):
    __slots__ = ("user_type", "username", "name", "password", "role_id", "mobile_role_id", "mfa_status", "mfa_secret", "blood_group")
    USER_TYPE_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    MOBILE_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    MFA_STATUS_FIELD_NUMBER: _ClassVar[int]
    MFA_SECRET_FIELD_NUMBER: _ClassVar[int]
    BLOOD_GROUP_FIELD_NUMBER: _ClassVar[int]
    user_type: USER_TYPE
    username: str
    name: str
    password: bytes
    role_id: int
    mobile_role_id: int
    mfa_status: bool
    mfa_secret: bytes
    blood_group: str
    def __init__(self, user_type: _Optional[_Union[USER_TYPE, str]] = ..., username: _Optional[str] = ..., name: _Optional[str] = ..., password: _Optional[bytes] = ..., role_id: _Optional[int] = ..., mobile_role_id: _Optional[int] = ..., mfa_status: _Optional[bool] = ..., mfa_secret: _Optional[bytes] = ..., blood_group: _Optional[str] = ...) -> None: ...

class UsersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[User]
    def __init__(self, list: _Optional[_Iterable[_Union[User, _Mapping]]] = ...) -> None: ...

class UsersServicePaginationReq(_message.Message):
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
    sort_key: USER_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[USER_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class UsersServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[User]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[User, _Mapping]]] = ...) -> None: ...

class UsersServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "user_type", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "username", "name", "code", "email", "phone", "role_id", "shift_group_id", "attendance_uom_id", "department_id", "payroll_group_id", "payroll_tax_group_id", "payroll_currency_id", "basic_pay_uom_id", "work_email", "vendor_id", "client_id", "form_data")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    USER_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_START_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_END_FIELD_NUMBER: _ClassVar[int]
    APPROVED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVER_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    SHIFT_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    WORK_EMAIL_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: USER_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    user_type: USER_TYPE
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    username: str
    name: str
    code: str
    email: str
    phone: str
    role_id: int
    shift_group_id: int
    attendance_uom_id: int
    department_id: int
    payroll_group_id: int
    payroll_tax_group_id: int
    payroll_currency_id: int
    basic_pay_uom_id: int
    work_email: str
    vendor_id: int
    client_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[USER_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., user_type: _Optional[_Union[USER_TYPE, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., username: _Optional[str] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., role_id: _Optional[int] = ..., shift_group_id: _Optional[int] = ..., attendance_uom_id: _Optional[int] = ..., department_id: _Optional[int] = ..., payroll_group_id: _Optional[int] = ..., payroll_tax_group_id: _Optional[int] = ..., payroll_currency_id: _Optional[int] = ..., basic_pay_uom_id: _Optional[int] = ..., work_email: _Optional[str] = ..., vendor_id: _Optional[int] = ..., client_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class UsersServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "user_type", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "username", "name", "code", "email", "phone", "role_id", "shift_group_id", "attendance_uom_id", "department_id", "payroll_group_id", "payroll_tax_group_id", "payroll_currency_id", "basic_pay_uom_id", "work_email", "vendor_id", "client_id", "form_data")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    USER_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_START_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_END_FIELD_NUMBER: _ClassVar[int]
    APPROVED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVER_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    SHIFT_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    ATTENDANCE_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    WORK_EMAIL_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    user_type: USER_TYPE
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    username: str
    name: str
    code: str
    email: str
    phone: str
    role_id: int
    shift_group_id: int
    attendance_uom_id: int
    department_id: int
    payroll_group_id: int
    payroll_tax_group_id: int
    payroll_currency_id: int
    basic_pay_uom_id: int
    work_email: str
    vendor_id: int
    client_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., user_type: _Optional[_Union[USER_TYPE, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., username: _Optional[str] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., email: _Optional[str] = ..., phone: _Optional[str] = ..., role_id: _Optional[int] = ..., shift_group_id: _Optional[int] = ..., attendance_uom_id: _Optional[int] = ..., department_id: _Optional[int] = ..., payroll_group_id: _Optional[int] = ..., payroll_tax_group_id: _Optional[int] = ..., payroll_currency_id: _Optional[int] = ..., basic_pay_uom_id: _Optional[int] = ..., work_email: _Optional[str] = ..., vendor_id: _Optional[int] = ..., client_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class UsersServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "user_type", "status", "search_key", "vendor_id", "client_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: USER_SORT_KEY
    entity_uuid: str
    user_type: USER_TYPE
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    vendor_id: int
    client_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[USER_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., user_type: _Optional[_Union[USER_TYPE, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., vendor_id: _Optional[int] = ..., client_id: _Optional[int] = ...) -> None: ...

class UsersServiceRegisterMobileDeviceRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_id", "device_os", "device_token")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_OS_FIELD_NUMBER: _ClassVar[int]
    DEVICE_TOKEN_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_id: int
    device_os: str
    device_token: str
    def __init__(self, entity_uuid: _Optional[str] = ..., user_id: _Optional[int] = ..., device_os: _Optional[str] = ..., device_token: _Optional[str] = ...) -> None: ...
