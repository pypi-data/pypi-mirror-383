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

class EXPENSE_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EXPENSE_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[EXPENSE_ITEM_SORT_KEY]
    EXPENSE_ITEM_SORT_KEY_CREATED_AT: _ClassVar[EXPENSE_ITEM_SORT_KEY]
    EXPENSE_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[EXPENSE_ITEM_SORT_KEY]
    EXPENSE_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[EXPENSE_ITEM_SORT_KEY]
    EXPENSE_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[EXPENSE_ITEM_SORT_KEY]
    EXPENSE_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[EXPENSE_ITEM_SORT_KEY]
    EXPENSE_ITEM_SORT_KEY_LEDGER_ID: _ClassVar[EXPENSE_ITEM_SORT_KEY]
    EXPENSE_ITEM_SORT_KEY_TAX_GROUP_ID: _ClassVar[EXPENSE_ITEM_SORT_KEY]
    EXPENSE_ITEM_SORT_KEY_AMOUNT: _ClassVar[EXPENSE_ITEM_SORT_KEY]
    EXPENSE_ITEM_SORT_KEY_DATE_OF_EXPENSE: _ClassVar[EXPENSE_ITEM_SORT_KEY]

class EXPENSE_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EXPENSE_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[EXPENSE_ITEM_STATUS]
    EXPENSE_ITEM_STATUS_APPROVED: _ClassVar[EXPENSE_ITEM_STATUS]
    EXPENSE_ITEM_STATUS_UNAPPROVED: _ClassVar[EXPENSE_ITEM_STATUS]

class EXPENSE_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    EXPENSE_SORT_KEY_ID_UNSPECIFIED: _ClassVar[EXPENSE_SORT_KEY]
    EXPENSE_SORT_KEY_CREATED_AT: _ClassVar[EXPENSE_SORT_KEY]
    EXPENSE_SORT_KEY_MODIFIED_AT: _ClassVar[EXPENSE_SORT_KEY]
    EXPENSE_SORT_KEY_APPROVED_ON: _ClassVar[EXPENSE_SORT_KEY]
    EXPENSE_SORT_KEY_APPROVED_BY: _ClassVar[EXPENSE_SORT_KEY]
    EXPENSE_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[EXPENSE_SORT_KEY]
    EXPENSE_SORT_KEY_COMPLETED_ON: _ClassVar[EXPENSE_SORT_KEY]
    EXPENSE_SORT_KEY_REFERENCE_ID: _ClassVar[EXPENSE_SORT_KEY]
    EXPENSE_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[EXPENSE_SORT_KEY]
    EXPENSE_SORT_KEY_CURRENCY_ID: _ClassVar[EXPENSE_SORT_KEY]
    EXPENSE_SORT_KEY_PAID_BY_USER_ID: _ClassVar[EXPENSE_SORT_KEY]
EXPENSE_ITEM_SORT_KEY_ID_UNSPECIFIED: EXPENSE_ITEM_SORT_KEY
EXPENSE_ITEM_SORT_KEY_CREATED_AT: EXPENSE_ITEM_SORT_KEY
EXPENSE_ITEM_SORT_KEY_MODIFIED_AT: EXPENSE_ITEM_SORT_KEY
EXPENSE_ITEM_SORT_KEY_APPROVED_ON: EXPENSE_ITEM_SORT_KEY
EXPENSE_ITEM_SORT_KEY_APPROVED_BY: EXPENSE_ITEM_SORT_KEY
EXPENSE_ITEM_SORT_KEY_APPROVER_ROLE_ID: EXPENSE_ITEM_SORT_KEY
EXPENSE_ITEM_SORT_KEY_LEDGER_ID: EXPENSE_ITEM_SORT_KEY
EXPENSE_ITEM_SORT_KEY_TAX_GROUP_ID: EXPENSE_ITEM_SORT_KEY
EXPENSE_ITEM_SORT_KEY_AMOUNT: EXPENSE_ITEM_SORT_KEY
EXPENSE_ITEM_SORT_KEY_DATE_OF_EXPENSE: EXPENSE_ITEM_SORT_KEY
EXPENSE_ITEM_STATUS_ANY_UNSPECIFIED: EXPENSE_ITEM_STATUS
EXPENSE_ITEM_STATUS_APPROVED: EXPENSE_ITEM_STATUS
EXPENSE_ITEM_STATUS_UNAPPROVED: EXPENSE_ITEM_STATUS
EXPENSE_SORT_KEY_ID_UNSPECIFIED: EXPENSE_SORT_KEY
EXPENSE_SORT_KEY_CREATED_AT: EXPENSE_SORT_KEY
EXPENSE_SORT_KEY_MODIFIED_AT: EXPENSE_SORT_KEY
EXPENSE_SORT_KEY_APPROVED_ON: EXPENSE_SORT_KEY
EXPENSE_SORT_KEY_APPROVED_BY: EXPENSE_SORT_KEY
EXPENSE_SORT_KEY_APPROVER_ROLE_ID: EXPENSE_SORT_KEY
EXPENSE_SORT_KEY_COMPLETED_ON: EXPENSE_SORT_KEY
EXPENSE_SORT_KEY_REFERENCE_ID: EXPENSE_SORT_KEY
EXPENSE_SORT_KEY_FINAL_REF_NUMBER: EXPENSE_SORT_KEY
EXPENSE_SORT_KEY_CURRENCY_ID: EXPENSE_SORT_KEY
EXPENSE_SORT_KEY_PAID_BY_USER_ID: EXPENSE_SORT_KEY

class ExpensesServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "project_id", "vault_folder_id", "reference_id", "ref_from", "ref_id", "currency_id", "paid_by_user_id", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PAID_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    project_id: int
    vault_folder_id: int
    reference_id: str
    ref_from: str
    ref_id: int
    currency_id: int
    paid_by_user_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., project_id: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., paid_by_user_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class ExpensesServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "project_id", "vault_folder_id", "reference_id", "ref_from", "ref_id", "currency_id", "paid_by_user_id", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PAID_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    project_id: int
    vault_folder_id: int
    reference_id: str
    ref_from: str
    ref_id: int
    currency_id: int
    paid_by_user_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., project_id: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., paid_by_user_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class Expense(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "project_id", "vault_folder_id", "reference_id", "final_ref_number", "ref_from", "ref_id", "currency_id", "paid_by_user_id", "list", "form_data", "total_amount")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PAID_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    completed_on: int
    project_id: int
    vault_folder_id: int
    reference_id: str
    final_ref_number: str
    ref_from: str
    ref_id: int
    currency_id: int
    paid_by_user_id: int
    list: _containers.RepeatedCompositeFieldContainer[ExpenseItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatum]
    total_amount: float
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., project_id: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., paid_by_user_id: _Optional[int] = ..., list: _Optional[_Iterable[_Union[ExpenseItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatum, _Mapping]]] = ..., total_amount: _Optional[float] = ...) -> None: ...

class ExpensesServiceItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "expense_id", "name", "bill_no", "description", "ledger_id", "tax_group_id", "amount", "date_of_expense")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    EXPENSE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BILL_NO_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LEDGER_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    DATE_OF_EXPENSE_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    expense_id: int
    name: str
    bill_no: str
    description: str
    ledger_id: int
    tax_group_id: int
    amount: int
    date_of_expense: str
    def __init__(self, user_comment: _Optional[str] = ..., expense_id: _Optional[int] = ..., name: _Optional[str] = ..., bill_no: _Optional[str] = ..., description: _Optional[str] = ..., ledger_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., amount: _Optional[int] = ..., date_of_expense: _Optional[str] = ...) -> None: ...

class ExpensesServiceItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "name", "bill_no", "description", "ledger_id", "tax_group_id", "amount", "date_of_expense")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BILL_NO_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LEDGER_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    DATE_OF_EXPENSE_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    name: str
    bill_no: str
    description: str
    ledger_id: int
    tax_group_id: int
    amount: int
    date_of_expense: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., name: _Optional[str] = ..., bill_no: _Optional[str] = ..., description: _Optional[str] = ..., ledger_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., amount: _Optional[int] = ..., date_of_expense: _Optional[str] = ...) -> None: ...

class ExpenseItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "expense_id", "name", "bill_no", "description", "ledger_id", "tax_group_id", "amount", "date_of_expense")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    EXPENSE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BILL_NO_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    LEDGER_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    DATE_OF_EXPENSE_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    expense_id: int
    name: str
    bill_no: str
    description: str
    ledger_id: int
    tax_group_id: int
    amount: int
    date_of_expense: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., expense_id: _Optional[int] = ..., name: _Optional[str] = ..., bill_no: _Optional[str] = ..., description: _Optional[str] = ..., ledger_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., amount: _Optional[int] = ..., date_of_expense: _Optional[str] = ...) -> None: ...

class ExpensesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[Expense]
    def __init__(self, list: _Optional[_Iterable[_Union[Expense, _Mapping]]] = ...) -> None: ...

class ExpensesItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[ExpenseItem]
    def __init__(self, list: _Optional[_Iterable[_Union[ExpenseItem, _Mapping]]] = ...) -> None: ...

class ExpenseItemHistoryRequest(_message.Message):
    __slots__ = ("expense_id", "name")
    EXPENSE_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    expense_id: int
    name: str
    def __init__(self, expense_id: _Optional[int] = ..., name: _Optional[str] = ...) -> None: ...

class ExpenseItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "expense_id", "ledger_id", "tax_group_id", "date_of_expense", "search_key")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_START_FIELD_NUMBER: _ClassVar[int]
    APPROVED_ON_END_FIELD_NUMBER: _ClassVar[int]
    APPROVED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVER_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    EXPENSE_ID_FIELD_NUMBER: _ClassVar[int]
    LEDGER_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_OF_EXPENSE_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: EXPENSE_ITEM_SORT_KEY
    entity_uuid: str
    status: EXPENSE_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    expense_id: int
    ledger_id: int
    tax_group_id: int
    date_of_expense: str
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[EXPENSE_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[EXPENSE_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., expense_id: _Optional[int] = ..., ledger_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., date_of_expense: _Optional[str] = ..., search_key: _Optional[str] = ...) -> None: ...

class ExpensesServicePaginatedItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[ExpenseItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[ExpenseItem, _Mapping]]] = ...) -> None: ...

class ExpensesServicePaginationReq(_message.Message):
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
    sort_key: EXPENSE_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[EXPENSE_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class ExpensesServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[Expense]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[Expense, _Mapping]]] = ...) -> None: ...

class ExpensesServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "currency_id", "paid_by_user_id", "project_id", "form_data")
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
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PAID_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: EXPENSE_SORT_KEY
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
    currency_id: int
    paid_by_user_id: int
    project_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[EXPENSE_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., currency_id: _Optional[int] = ..., paid_by_user_id: _Optional[int] = ..., project_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class ExpensesServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "currency_id", "paid_by_user_id", "project_id", "form_data")
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
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PAID_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
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
    currency_id: int
    paid_by_user_id: int
    project_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., currency_id: _Optional[int] = ..., paid_by_user_id: _Optional[int] = ..., project_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class ExpensesServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: EXPENSE_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[EXPENSE_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ...) -> None: ...
