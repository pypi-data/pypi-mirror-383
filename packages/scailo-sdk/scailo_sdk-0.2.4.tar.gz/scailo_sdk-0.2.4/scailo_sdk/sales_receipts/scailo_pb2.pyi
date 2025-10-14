from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from magic_links import scailo_pb2 as _scailo_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SALE_RECEIPT_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALE_RECEIPT_SORT_KEY_ID_UNSPECIFIED: _ClassVar[SALE_RECEIPT_SORT_KEY]
    SALE_RECEIPT_SORT_KEY_CREATED_AT: _ClassVar[SALE_RECEIPT_SORT_KEY]
    SALE_RECEIPT_SORT_KEY_MODIFIED_AT: _ClassVar[SALE_RECEIPT_SORT_KEY]
    SALE_RECEIPT_SORT_KEY_APPROVED_ON: _ClassVar[SALE_RECEIPT_SORT_KEY]
    SALE_RECEIPT_SORT_KEY_APPROVED_BY: _ClassVar[SALE_RECEIPT_SORT_KEY]
    SALE_RECEIPT_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[SALE_RECEIPT_SORT_KEY]
    SALE_RECEIPT_SORT_KEY_COMPLETED_ON: _ClassVar[SALE_RECEIPT_SORT_KEY]
    SALE_RECEIPT_SORT_KEY_REFERENCE_ID: _ClassVar[SALE_RECEIPT_SORT_KEY]
    SALE_RECEIPT_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[SALE_RECEIPT_SORT_KEY]
    SALE_RECEIPT_SORT_KEY_PAYMENT_TIMESTAMP: _ClassVar[SALE_RECEIPT_SORT_KEY]
SALE_RECEIPT_SORT_KEY_ID_UNSPECIFIED: SALE_RECEIPT_SORT_KEY
SALE_RECEIPT_SORT_KEY_CREATED_AT: SALE_RECEIPT_SORT_KEY
SALE_RECEIPT_SORT_KEY_MODIFIED_AT: SALE_RECEIPT_SORT_KEY
SALE_RECEIPT_SORT_KEY_APPROVED_ON: SALE_RECEIPT_SORT_KEY
SALE_RECEIPT_SORT_KEY_APPROVED_BY: SALE_RECEIPT_SORT_KEY
SALE_RECEIPT_SORT_KEY_APPROVER_ROLE_ID: SALE_RECEIPT_SORT_KEY
SALE_RECEIPT_SORT_KEY_COMPLETED_ON: SALE_RECEIPT_SORT_KEY
SALE_RECEIPT_SORT_KEY_REFERENCE_ID: SALE_RECEIPT_SORT_KEY
SALE_RECEIPT_SORT_KEY_FINAL_REF_NUMBER: SALE_RECEIPT_SORT_KEY
SALE_RECEIPT_SORT_KEY_PAYMENT_TIMESTAMP: SALE_RECEIPT_SORT_KEY

class SalesReceiptsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "ref_from", "ref_id", "bank_account_id", "currency_id", "transaction_type", "amount_base", "amount_net", "payment_timestamp", "description")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_BASE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_NET_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    ref_from: str
    ref_id: int
    bank_account_id: int
    currency_id: int
    transaction_type: str
    amount_base: int
    amount_net: int
    payment_timestamp: int
    description: str
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., bank_account_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., transaction_type: _Optional[str] = ..., amount_base: _Optional[int] = ..., amount_net: _Optional[int] = ..., payment_timestamp: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class SalesReceiptsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "bank_account_id", "currency_id", "transaction_type", "amount_base", "amount_net", "payment_timestamp", "description")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_BASE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_NET_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    bank_account_id: int
    currency_id: int
    transaction_type: str
    amount_base: int
    amount_net: int
    payment_timestamp: int
    description: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., bank_account_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., transaction_type: _Optional[str] = ..., amount_base: _Optional[int] = ..., amount_net: _Optional[int] = ..., payment_timestamp: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class SaleReceiptAncillaryParameters(_message.Message):
    __slots__ = ("ref_uuid", "client_uuid", "bank_account_uuid", "currency_uuid")
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_UUID_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_UUID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_UUID_FIELD_NUMBER: _ClassVar[int]
    ref_uuid: str
    client_uuid: str
    bank_account_uuid: str
    currency_uuid: str
    def __init__(self, ref_uuid: _Optional[str] = ..., client_uuid: _Optional[str] = ..., bank_account_uuid: _Optional[str] = ..., currency_uuid: _Optional[str] = ...) -> None: ...

class SaleReceipt(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "ref_from", "ref_id", "client_id", "bank_account_id", "currency_id", "transaction_type", "amount_base", "amount_net", "payment_timestamp", "description")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_BASE_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_NET_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    completed_on: int
    vault_folder_id: int
    reference_id: str
    final_ref_number: str
    ref_from: str
    ref_id: int
    client_id: int
    bank_account_id: int
    currency_id: int
    transaction_type: str
    amount_base: int
    amount_net: int
    payment_timestamp: int
    description: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., client_id: _Optional[int] = ..., bank_account_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., transaction_type: _Optional[str] = ..., amount_base: _Optional[int] = ..., amount_net: _Optional[int] = ..., payment_timestamp: _Optional[int] = ..., description: _Optional[str] = ...) -> None: ...

class SalesReceiptsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SaleReceipt]
    def __init__(self, list: _Optional[_Iterable[_Union[SaleReceipt, _Mapping]]] = ...) -> None: ...

class SalesReceiptsServicePaginationReq(_message.Message):
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
    sort_key: SALE_RECEIPT_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALE_RECEIPT_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class SalesReceiptsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[SaleReceipt]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[SaleReceipt, _Mapping]]] = ...) -> None: ...

class SalesReceiptsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "client_id", "bank_account_id", "currency_id", "transaction_type", "payment_timestamp_start", "payment_timestamp_end")
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
    COMPLETED_ON_START_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_END_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: SALE_RECEIPT_SORT_KEY
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
    completed_on_start: int
    completed_on_end: int
    reference_id: str
    final_ref_number: str
    ref_from: str
    ref_id: int
    client_id: int
    bank_account_id: int
    currency_id: int
    transaction_type: str
    payment_timestamp_start: int
    payment_timestamp_end: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALE_RECEIPT_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., client_id: _Optional[int] = ..., bank_account_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., transaction_type: _Optional[str] = ..., payment_timestamp_start: _Optional[int] = ..., payment_timestamp_end: _Optional[int] = ...) -> None: ...

class SalesReceiptsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "ref_from", "ref_id", "client_id", "bank_account_id", "currency_id", "transaction_type", "payment_timestamp_start", "payment_timestamp_end")
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
    COMPLETED_ON_START_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_END_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_TIMESTAMP_START_FIELD_NUMBER: _ClassVar[int]
    PAYMENT_TIMESTAMP_END_FIELD_NUMBER: _ClassVar[int]
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
    completed_on_start: int
    completed_on_end: int
    reference_id: str
    final_ref_number: str
    ref_from: str
    ref_id: int
    client_id: int
    bank_account_id: int
    currency_id: int
    transaction_type: str
    payment_timestamp_start: int
    payment_timestamp_end: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., client_id: _Optional[int] = ..., bank_account_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., transaction_type: _Optional[str] = ..., payment_timestamp_start: _Optional[int] = ..., payment_timestamp_end: _Optional[int] = ...) -> None: ...

class SalesReceiptsServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "consignee_client_id", "buyer_client_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    BUYER_CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: SALE_RECEIPT_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    consignee_client_id: int
    buyer_client_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALE_RECEIPT_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., consignee_client_id: _Optional[int] = ..., buyer_client_id: _Optional[int] = ...) -> None: ...
