from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ASSOCIATE_ORG_REF_FROM(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ASSOCIATE_ORG_REF_FROM_ANY_UNSPECIFIED: _ClassVar[ASSOCIATE_ORG_REF_FROM]
    ASSOCIATE_ORG_REF_FROM_EMPTY: _ClassVar[ASSOCIATE_ORG_REF_FROM]
    ASSOCIATE_ORG_REF_FROM_CLIENT: _ClassVar[ASSOCIATE_ORG_REF_FROM]
    ASSOCIATE_ORG_REF_FROM_VENDOR: _ClassVar[ASSOCIATE_ORG_REF_FROM]

class ASSOCIATE_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ASSOCIATE_SORT_KEY_ID_UNSPECIFIED: _ClassVar[ASSOCIATE_SORT_KEY]
    ASSOCIATE_SORT_KEY_CREATED_AT: _ClassVar[ASSOCIATE_SORT_KEY]
    ASSOCIATE_SORT_KEY_MODIFIED_AT: _ClassVar[ASSOCIATE_SORT_KEY]
    ASSOCIATE_SORT_KEY_FIRST_NAME: _ClassVar[ASSOCIATE_SORT_KEY]
    ASSOCIATE_SORT_KEY_MIDDLE_NAME: _ClassVar[ASSOCIATE_SORT_KEY]
    ASSOCIATE_SORT_KEY_LAST_NAME: _ClassVar[ASSOCIATE_SORT_KEY]
    ASSOCIATE_SORT_KEY_ORG_NAME: _ClassVar[ASSOCIATE_SORT_KEY]
    ASSOCIATE_SORT_KEY_JOB_TITLE: _ClassVar[ASSOCIATE_SORT_KEY]
ASSOCIATE_ORG_REF_FROM_ANY_UNSPECIFIED: ASSOCIATE_ORG_REF_FROM
ASSOCIATE_ORG_REF_FROM_EMPTY: ASSOCIATE_ORG_REF_FROM
ASSOCIATE_ORG_REF_FROM_CLIENT: ASSOCIATE_ORG_REF_FROM
ASSOCIATE_ORG_REF_FROM_VENDOR: ASSOCIATE_ORG_REF_FROM
ASSOCIATE_SORT_KEY_ID_UNSPECIFIED: ASSOCIATE_SORT_KEY
ASSOCIATE_SORT_KEY_CREATED_AT: ASSOCIATE_SORT_KEY
ASSOCIATE_SORT_KEY_MODIFIED_AT: ASSOCIATE_SORT_KEY
ASSOCIATE_SORT_KEY_FIRST_NAME: ASSOCIATE_SORT_KEY
ASSOCIATE_SORT_KEY_MIDDLE_NAME: ASSOCIATE_SORT_KEY
ASSOCIATE_SORT_KEY_LAST_NAME: ASSOCIATE_SORT_KEY
ASSOCIATE_SORT_KEY_ORG_NAME: ASSOCIATE_SORT_KEY
ASSOCIATE_SORT_KEY_JOB_TITLE: ASSOCIATE_SORT_KEY

class Associate(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "vault_folder_id", "first_name", "middle_name", "last_name", "org_ref_from", "org_ref_id", "org_name", "job_title", "department", "work_phone", "work_email", "personal_phone", "personal_email", "birthday", "anniversary", "description")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    ORG_REF_FROM_FIELD_NUMBER: _ClassVar[int]
    ORG_REF_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_TITLE_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_FIELD_NUMBER: _ClassVar[int]
    WORK_PHONE_FIELD_NUMBER: _ClassVar[int]
    WORK_EMAIL_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_PHONE_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_EMAIL_FIELD_NUMBER: _ClassVar[int]
    BIRTHDAY_FIELD_NUMBER: _ClassVar[int]
    ANNIVERSARY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    vault_folder_id: int
    first_name: str
    middle_name: str
    last_name: str
    org_ref_from: ASSOCIATE_ORG_REF_FROM
    org_ref_id: int
    org_name: str
    job_title: str
    department: str
    work_phone: str
    work_email: str
    personal_phone: str
    personal_email: str
    birthday: str
    anniversary: str
    description: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., vault_folder_id: _Optional[int] = ..., first_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., last_name: _Optional[str] = ..., org_ref_from: _Optional[_Union[ASSOCIATE_ORG_REF_FROM, str]] = ..., org_ref_id: _Optional[int] = ..., org_name: _Optional[str] = ..., job_title: _Optional[str] = ..., department: _Optional[str] = ..., work_phone: _Optional[str] = ..., work_email: _Optional[str] = ..., personal_phone: _Optional[str] = ..., personal_email: _Optional[str] = ..., birthday: _Optional[str] = ..., anniversary: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class AssociatesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[Associate]
    def __init__(self, list: _Optional[_Iterable[_Union[Associate, _Mapping]]] = ...) -> None: ...

class AssociatePaginationResp(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[Associate]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[Associate, _Mapping]]] = ...) -> None: ...

class AssociatesServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "first_name", "middle_name", "last_name", "org_ref_from", "org_ref_id", "org_name", "job_title", "department", "work_phone", "work_email", "personal_phone", "personal_email", "birthday", "anniversary", "description")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    ORG_REF_FROM_FIELD_NUMBER: _ClassVar[int]
    ORG_REF_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_TITLE_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_FIELD_NUMBER: _ClassVar[int]
    WORK_PHONE_FIELD_NUMBER: _ClassVar[int]
    WORK_EMAIL_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_PHONE_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_EMAIL_FIELD_NUMBER: _ClassVar[int]
    BIRTHDAY_FIELD_NUMBER: _ClassVar[int]
    ANNIVERSARY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    first_name: str
    middle_name: str
    last_name: str
    org_ref_from: ASSOCIATE_ORG_REF_FROM
    org_ref_id: int
    org_name: str
    job_title: str
    department: str
    work_phone: str
    work_email: str
    personal_phone: str
    personal_email: str
    birthday: str
    anniversary: str
    description: str
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., first_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., last_name: _Optional[str] = ..., org_ref_from: _Optional[_Union[ASSOCIATE_ORG_REF_FROM, str]] = ..., org_ref_id: _Optional[int] = ..., org_name: _Optional[str] = ..., job_title: _Optional[str] = ..., department: _Optional[str] = ..., work_phone: _Optional[str] = ..., work_email: _Optional[str] = ..., personal_phone: _Optional[str] = ..., personal_email: _Optional[str] = ..., birthday: _Optional[str] = ..., anniversary: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class AssociatesServiceImportRequest(_message.Message):
    __slots__ = ("user_comment", "list")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    list: _containers.RepeatedCompositeFieldContainer[AssociatesServiceCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., list: _Optional[_Iterable[_Union[AssociatesServiceCreateRequest, _Mapping]]] = ...) -> None: ...

class AssociatesServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "vault_folder_id", "first_name", "middle_name", "last_name", "org_ref_from", "org_ref_id", "org_name", "job_title", "department", "work_phone", "work_email", "personal_phone", "personal_email", "birthday", "anniversary", "description")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    ORG_REF_FROM_FIELD_NUMBER: _ClassVar[int]
    ORG_REF_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_TITLE_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_FIELD_NUMBER: _ClassVar[int]
    WORK_PHONE_FIELD_NUMBER: _ClassVar[int]
    WORK_EMAIL_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_PHONE_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_EMAIL_FIELD_NUMBER: _ClassVar[int]
    BIRTHDAY_FIELD_NUMBER: _ClassVar[int]
    ANNIVERSARY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    vault_folder_id: int
    first_name: str
    middle_name: str
    last_name: str
    org_ref_from: ASSOCIATE_ORG_REF_FROM
    org_ref_id: int
    org_name: str
    job_title: str
    department: str
    work_phone: str
    work_email: str
    personal_phone: str
    personal_email: str
    birthday: str
    anniversary: str
    description: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., first_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., last_name: _Optional[str] = ..., org_ref_from: _Optional[_Union[ASSOCIATE_ORG_REF_FROM, str]] = ..., org_ref_id: _Optional[int] = ..., org_name: _Optional[str] = ..., job_title: _Optional[str] = ..., department: _Optional[str] = ..., work_phone: _Optional[str] = ..., work_email: _Optional[str] = ..., personal_phone: _Optional[str] = ..., personal_email: _Optional[str] = ..., birthday: _Optional[str] = ..., anniversary: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...

class AssociatesServicePaginationReq(_message.Message):
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
    sort_key: ASSOCIATE_SORT_KEY
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ASSOCIATE_SORT_KEY, str]] = ...) -> None: ...

class AssociatesServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "first_name", "middle_name", "last_name", "org_ref_from", "org_ref_id", "org_name", "job_title", "department", "work_phone", "work_email", "personal_phone", "personal_email", "vendor_id", "client_id")
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
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    ORG_REF_FROM_FIELD_NUMBER: _ClassVar[int]
    ORG_REF_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_TITLE_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_FIELD_NUMBER: _ClassVar[int]
    WORK_PHONE_FIELD_NUMBER: _ClassVar[int]
    WORK_EMAIL_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_PHONE_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_EMAIL_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: ASSOCIATE_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    first_name: str
    middle_name: str
    last_name: str
    org_ref_from: ASSOCIATE_ORG_REF_FROM
    org_ref_id: int
    org_name: str
    job_title: str
    department: str
    work_phone: str
    work_email: str
    personal_phone: str
    personal_email: str
    vendor_id: int
    client_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ASSOCIATE_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., first_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., last_name: _Optional[str] = ..., org_ref_from: _Optional[_Union[ASSOCIATE_ORG_REF_FROM, str]] = ..., org_ref_id: _Optional[int] = ..., org_name: _Optional[str] = ..., job_title: _Optional[str] = ..., department: _Optional[str] = ..., work_phone: _Optional[str] = ..., work_email: _Optional[str] = ..., personal_phone: _Optional[str] = ..., personal_email: _Optional[str] = ..., vendor_id: _Optional[int] = ..., client_id: _Optional[int] = ...) -> None: ...

class AssociatesServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "first_name", "middle_name", "last_name", "org_ref_from", "org_ref_id", "org_name", "job_title", "department", "work_phone", "work_email", "personal_phone", "personal_email", "vendor_id", "client_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    MIDDLE_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    ORG_REF_FROM_FIELD_NUMBER: _ClassVar[int]
    ORG_REF_ID_FIELD_NUMBER: _ClassVar[int]
    ORG_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_TITLE_FIELD_NUMBER: _ClassVar[int]
    DEPARTMENT_FIELD_NUMBER: _ClassVar[int]
    WORK_PHONE_FIELD_NUMBER: _ClassVar[int]
    WORK_EMAIL_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_PHONE_FIELD_NUMBER: _ClassVar[int]
    PERSONAL_EMAIL_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    first_name: str
    middle_name: str
    last_name: str
    org_ref_from: ASSOCIATE_ORG_REF_FROM
    org_ref_id: int
    org_name: str
    job_title: str
    department: str
    work_phone: str
    work_email: str
    personal_phone: str
    personal_email: str
    vendor_id: int
    client_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., first_name: _Optional[str] = ..., middle_name: _Optional[str] = ..., last_name: _Optional[str] = ..., org_ref_from: _Optional[_Union[ASSOCIATE_ORG_REF_FROM, str]] = ..., org_ref_id: _Optional[int] = ..., org_name: _Optional[str] = ..., job_title: _Optional[str] = ..., department: _Optional[str] = ..., work_phone: _Optional[str] = ..., work_email: _Optional[str] = ..., personal_phone: _Optional[str] = ..., personal_email: _Optional[str] = ..., vendor_id: _Optional[int] = ..., client_id: _Optional[int] = ...) -> None: ...

class AssociatesServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "search_key", "org_ref_from", "org_ref_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    ORG_REF_FROM_FIELD_NUMBER: _ClassVar[int]
    ORG_REF_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: ASSOCIATE_SORT_KEY
    entity_uuid: str
    search_key: str
    org_ref_from: ASSOCIATE_ORG_REF_FROM
    org_ref_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[ASSOCIATE_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., search_key: _Optional[str] = ..., org_ref_from: _Optional[_Union[ASSOCIATE_ORG_REF_FROM, str]] = ..., org_ref_id: _Optional[int] = ...) -> None: ...
