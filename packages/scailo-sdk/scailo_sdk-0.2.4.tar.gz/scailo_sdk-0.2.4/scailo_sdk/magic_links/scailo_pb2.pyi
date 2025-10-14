from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MAGIC_LINK_RESOURCE_TYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MAGIC_LINK_RESOURCE_TYPE_ANY_UNSPECIFIED: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_VENDOR: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_PURCHASE_ENQUIRY: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_QUOTATION_REQUEST: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_QUOTATION_RESPONSE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_PURCHASE_ORDER: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_GOODS_RECEIPT: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_VENDOR_INVOICE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_DEBIT_NOTE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_PURCHASE_RETURN: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_PURCHASE_PAYMENT: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_SUPPLY_OFFER: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_SALES_ENQUIRY: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_SALES_QUOTATION: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_SALES_ORDER: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_GOODS_DISPATCH: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_PROFORMA_INVOICE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_SALES_INVOICE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_CREDIT_NOTE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_SALES_RETURN: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_SALES_RECEIPT: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_INWARD_JOB: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_INWARD_JOB_FREE_ISSUE_MATERIAL: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_INWARD_JOB_FREE_ISSUE_MATERIAL_RETURN: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_OUTWARD_JOB: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_OUTWARD_JOB_FREE_ISSUE_MATERIAL: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_OUTWARD_JOB_FREE_ISSUE_MATERIAL_RETURN: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_EQUATION_FAMILY: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_EQUATION_SALES_BUNDLE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_EQUATION_WORK_ORDER: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_EQUATION_REPLACEABLE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_WORK_ORDER: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_PRODUCTION_PLAN: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_REPLACEABLE_INDENT: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_PURCHASE_INDENT: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_PRODUCTION_INDENT: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_ASSET_INDENT: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_STOCK_ISSUANCE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_STOCK_RETURN: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_STOCK_AUDIT: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_QC_SAMPLE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_COMPONENT: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_PRODUCT: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_FEEDSTOCK: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_MERCHANDISE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_EQUIPMENT: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_INFRASTRUCTURE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_ATTENDANCE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_ABSENCE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_ON_DUTY: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_VISITATION: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_EXPENSE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]
    MAGIC_LINK_RESOURCE_TYPE_USER_SIGNATURE: _ClassVar[MAGIC_LINK_RESOURCE_TYPE]

class MAGIC_LINK_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MAGIC_LINK_SORT_KEY_ID_UNSPECIFIED: _ClassVar[MAGIC_LINK_SORT_KEY]
    MAGIC_LINK_SORT_KEY_CREATED_AT: _ClassVar[MAGIC_LINK_SORT_KEY]
    MAGIC_LINK_SORT_KEY_MODIFIED_AT: _ClassVar[MAGIC_LINK_SORT_KEY]
    MAGIC_LINK_SORT_KEY_EXPIRES_AT: _ClassVar[MAGIC_LINK_SORT_KEY]
MAGIC_LINK_RESOURCE_TYPE_ANY_UNSPECIFIED: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_VENDOR: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_PURCHASE_ENQUIRY: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_QUOTATION_REQUEST: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_QUOTATION_RESPONSE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_PURCHASE_ORDER: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_GOODS_RECEIPT: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_VENDOR_INVOICE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_DEBIT_NOTE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_PURCHASE_RETURN: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_PURCHASE_PAYMENT: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_SUPPLY_OFFER: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_SALES_ENQUIRY: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_SALES_QUOTATION: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_SALES_ORDER: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_GOODS_DISPATCH: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_PROFORMA_INVOICE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_SALES_INVOICE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_CREDIT_NOTE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_SALES_RETURN: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_SALES_RECEIPT: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_INWARD_JOB: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_INWARD_JOB_FREE_ISSUE_MATERIAL: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_INWARD_JOB_FREE_ISSUE_MATERIAL_RETURN: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_OUTWARD_JOB: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_OUTWARD_JOB_FREE_ISSUE_MATERIAL: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_OUTWARD_JOB_FREE_ISSUE_MATERIAL_RETURN: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_EQUATION_FAMILY: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_EQUATION_SALES_BUNDLE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_EQUATION_WORK_ORDER: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_EQUATION_REPLACEABLE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_WORK_ORDER: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_PRODUCTION_PLAN: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_REPLACEABLE_INDENT: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_PURCHASE_INDENT: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_PRODUCTION_INDENT: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_ASSET_INDENT: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_STOCK_ISSUANCE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_STOCK_RETURN: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_STOCK_AUDIT: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_QC_SAMPLE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_COMPONENT: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_PRODUCT: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_FEEDSTOCK: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_MERCHANDISE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_EQUIPMENT: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_INFRASTRUCTURE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_ATTENDANCE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_ABSENCE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_ON_DUTY: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_VISITATION: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_EXPENSE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_RESOURCE_TYPE_USER_SIGNATURE: MAGIC_LINK_RESOURCE_TYPE
MAGIC_LINK_SORT_KEY_ID_UNSPECIFIED: MAGIC_LINK_SORT_KEY
MAGIC_LINK_SORT_KEY_CREATED_AT: MAGIC_LINK_SORT_KEY
MAGIC_LINK_SORT_KEY_MODIFIED_AT: MAGIC_LINK_SORT_KEY
MAGIC_LINK_SORT_KEY_EXPIRES_AT: MAGIC_LINK_SORT_KEY

class MagicLink(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "resource_uuid", "resource_type", "expires_at", "description", "code", "url")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_UUID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    resource_uuid: str
    resource_type: MAGIC_LINK_RESOURCE_TYPE
    expires_at: int
    description: str
    code: str
    url: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., resource_uuid: _Optional[str] = ..., resource_type: _Optional[_Union[MAGIC_LINK_RESOURCE_TYPE, str]] = ..., expires_at: _Optional[int] = ..., description: _Optional[str] = ..., code: _Optional[str] = ..., url: _Optional[str] = ...) -> None: ...

class MagicLinksList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[MagicLink]
    def __init__(self, list: _Optional[_Iterable[_Union[MagicLink, _Mapping]]] = ...) -> None: ...

class MagicLinkPaginationResp(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[MagicLink]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[MagicLink, _Mapping]]] = ...) -> None: ...

class MagicLinksServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "resource_uuid", "resource_type", "expires_at", "description")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_UUID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    resource_uuid: str
    resource_type: MAGIC_LINK_RESOURCE_TYPE
    expires_at: int
    description: str
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., resource_uuid: _Optional[str] = ..., resource_type: _Optional[_Union[MAGIC_LINK_RESOURCE_TYPE, str]] = ..., expires_at: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class MagicLinksServiceCreateRequestForSpecificResource(_message.Message):
    __slots__ = ("user_comment", "resource_uuid", "expires_at", "description")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_UUID_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    resource_uuid: str
    expires_at: int
    description: str
    def __init__(self, user_comment: _Optional[str] = ..., resource_uuid: _Optional[str] = ..., expires_at: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class MagicLinksServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "expires_at", "description")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    expires_at: int
    description: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., expires_at: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class MagicLinksServicePaginationReq(_message.Message):
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
    sort_key: MAGIC_LINK_SORT_KEY
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[MAGIC_LINK_SORT_KEY, str]] = ...) -> None: ...

class MagicLinksServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "resource_type", "resource_uuid", "expires_at_start", "expires_at_end")
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
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_UUID_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_START_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_END_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: MAGIC_LINK_SORT_KEY
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    resource_type: MAGIC_LINK_RESOURCE_TYPE
    resource_uuid: str
    expires_at_start: int
    expires_at_end: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[MAGIC_LINK_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., resource_type: _Optional[_Union[MAGIC_LINK_RESOURCE_TYPE, str]] = ..., resource_uuid: _Optional[str] = ..., expires_at_start: _Optional[int] = ..., expires_at_end: _Optional[int] = ...) -> None: ...

class MagicLinksServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "resource_type", "resource_uuid", "expires_at_start", "expires_at_end")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    MODIFICATION_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_UUID_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_START_FIELD_NUMBER: _ClassVar[int]
    EXPIRES_AT_END_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    creation_timestamp_start: int
    creation_timestamp_end: int
    modification_timestamp_start: int
    modification_timestamp_end: int
    entity_uuid: str
    resource_type: MAGIC_LINK_RESOURCE_TYPE
    resource_uuid: str
    expires_at_start: int
    expires_at_end: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., resource_type: _Optional[_Union[MAGIC_LINK_RESOURCE_TYPE, str]] = ..., resource_uuid: _Optional[str] = ..., expires_at_start: _Optional[int] = ..., expires_at_end: _Optional[int] = ...) -> None: ...

class MagicLinksServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "search_key", "resource_type")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: MAGIC_LINK_SORT_KEY
    entity_uuid: str
    search_key: str
    resource_type: MAGIC_LINK_RESOURCE_TYPE
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[MAGIC_LINK_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., search_key: _Optional[str] = ..., resource_type: _Optional[_Union[MAGIC_LINK_RESOURCE_TYPE, str]] = ...) -> None: ...

class MagicLinkServiceSearchByCodeReq(_message.Message):
    __slots__ = ("code", "ip_address", "user_agent")
    CODE_FIELD_NUMBER: _ClassVar[int]
    IP_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    code: str
    ip_address: str
    user_agent: str
    def __init__(self, code: _Optional[str] = ..., ip_address: _Optional[str] = ..., user_agent: _Optional[str] = ...) -> None: ...

class MagicLinkAccessLog(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "magic_link_uuid", "ip_addr", "user_agent")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    MAGIC_LINK_UUID_FIELD_NUMBER: _ClassVar[int]
    IP_ADDR_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    magic_link_uuid: str
    ip_addr: str
    user_agent: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., magic_link_uuid: _Optional[str] = ..., ip_addr: _Optional[str] = ..., user_agent: _Optional[str] = ...) -> None: ...

class MagicLinkAccessLogsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[MagicLinkAccessLog]
    def __init__(self, list: _Optional[_Iterable[_Union[MagicLinkAccessLog, _Mapping]]] = ...) -> None: ...
