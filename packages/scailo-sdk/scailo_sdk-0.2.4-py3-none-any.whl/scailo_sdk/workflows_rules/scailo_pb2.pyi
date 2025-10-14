from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class WORKFLOW_RULE_SERVICE_NAME(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WORKFLOW_RULE_SERVICE_NAME_ANY_UNSPECIFIED: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_ABSENCES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_ACTIONS_CODES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_ACTIVITIES_GROUPS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_ACTIVITIES_STATUSES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_ACTIVITIES_TAGS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_ACTIVITIES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_ANNOUNCEMENTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_ASSET_INDENTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_ASSOCIATES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_ATTENDANCES_AMENDMENTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_ATTENDANCES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_BANK_ACCOUNTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_CLIENTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_COMPONENTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_CREDIT_NOTES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_CURRENCIES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_DEBIT_NOTES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_DEPARTMENTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_EQUATIONS_FAMILIES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_EQUATIONS_REPLACEABLES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_EQUATIONS_SALES_BUNDLES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_EQUATIONS_WORK_ORDERS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_EQUIPMENTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_EXPENSES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_FAMILIES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_FEEDSTOCKS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_GOALS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_GOODS_DISPATCHES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_GOODS_RECEIPTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_HOLIDAYS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_INFRASTRUCTURES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_INVENTORY: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_INWARD_JOBS_FREE_ISSUE_MATERIALS_RETURNS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_INWARD_JOBS_FREE_ISSUE_MATERIALS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_INWARD_JOBS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_LEAVES_ADJUSTMENTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_LEAVES_REQUESTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_MEETINGS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_MERCHANDISES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_NOTES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_ON_DUTIES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_OUTWARD_JOBS_FREE_ISSUE_MATERIALS_RETURNS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_OUTWARD_JOBS_FREE_ISSUE_MATERIALS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_OUTWARD_JOBS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_OVERTIMES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_PRODUCTION_INDENTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_PRODUCTION_PLANS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_PRODUCTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_PROJECTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_PURCHASES_ENQUIRIES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_PURCHASES_INDENTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_PURCHASES_ORDERS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_SUPPLY_OFFERS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_PURCHASES_PAYMENTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_PURCHASES_RETURNS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_QC_GROUPS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_QC_SAMPLES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_QUOTATIONS_REQUESTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_QUOTATIONS_RESPONSES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_REPLACEABLE_INDENTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_ROLES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_SALARIES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_SALES_ENQUIRIES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_SALES_INVOICES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_PROFORMA_INVOICES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_SALES_ORDERS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_SALES_QUOTATIONS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_SALES_RECEIPTS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_SALES_RETURNS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_STOCK_AUDITS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_STOCK_ISSUANCES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_STOCK_RETURNS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_USERS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_VENDOR_INVOICES: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_VENDORS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_VISITATIONS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]
    WORKFLOW_RULE_SERVICE_NAME_WORK_ORDERS: _ClassVar[WORKFLOW_RULE_SERVICE_NAME]

class WORKFLOW_RULE_MOMENT(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WORKFLOW_RULE_MOMENT_ANY_UNSPECIFIED: _ClassVar[WORKFLOW_RULE_MOMENT]
    WORKFLOW_RULE_MOMENT_BEGIN: _ClassVar[WORKFLOW_RULE_MOMENT]
    WORKFLOW_RULE_MOMENT_END: _ClassVar[WORKFLOW_RULE_MOMENT]

class WORKFLOW_RULE_EXECUTE_ON(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WORKFLOW_RULE_EXECUTE_ON_ANY_UNSPECIFIED: _ClassVar[WORKFLOW_RULE_EXECUTE_ON]
    WORKFLOW_RULE_EXECUTE_ON_SUCCESS: _ClassVar[WORKFLOW_RULE_EXECUTE_ON]
    WORKFLOW_RULE_EXECUTE_ON_FAILURE: _ClassVar[WORKFLOW_RULE_EXECUTE_ON]

class WORKFLOW_RULE_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WORKFLOW_RULE_SORT_KEY_ID_UNSPECIFIED: _ClassVar[WORKFLOW_RULE_SORT_KEY]
    WORKFLOW_RULE_SORT_KEY_CREATED_AT: _ClassVar[WORKFLOW_RULE_SORT_KEY]
    WORKFLOW_RULE_SORT_KEY_MODIFIED_AT: _ClassVar[WORKFLOW_RULE_SORT_KEY]
    WORKFLOW_RULE_SORT_KEY_APPROVED_ON: _ClassVar[WORKFLOW_RULE_SORT_KEY]
    WORKFLOW_RULE_SORT_KEY_APPROVED_BY: _ClassVar[WORKFLOW_RULE_SORT_KEY]
    WORKFLOW_RULE_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[WORKFLOW_RULE_SORT_KEY]
    WORKFLOW_RULE_SORT_KEY_COMPLETED_ON: _ClassVar[WORKFLOW_RULE_SORT_KEY]
    WORKFLOW_RULE_SORT_KEY_NAME: _ClassVar[WORKFLOW_RULE_SORT_KEY]
    WORKFLOW_RULE_SORT_KEY_SERVICE_NAME: _ClassVar[WORKFLOW_RULE_SORT_KEY]
WORKFLOW_RULE_SERVICE_NAME_ANY_UNSPECIFIED: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_ABSENCES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_ACTIONS_CODES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_ACTIVITIES_GROUPS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_ACTIVITIES_STATUSES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_ACTIVITIES_TAGS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_ACTIVITIES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_ANNOUNCEMENTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_ASSET_INDENTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_ASSOCIATES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_ATTENDANCES_AMENDMENTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_ATTENDANCES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_BANK_ACCOUNTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_CLIENTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_COMPONENTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_CREDIT_NOTES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_CURRENCIES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_DEBIT_NOTES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_DEPARTMENTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_EQUATIONS_FAMILIES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_EQUATIONS_REPLACEABLES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_EQUATIONS_SALES_BUNDLES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_EQUATIONS_WORK_ORDERS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_EQUIPMENTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_EXPENSES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_FAMILIES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_FEEDSTOCKS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_GOALS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_GOODS_DISPATCHES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_GOODS_RECEIPTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_HOLIDAYS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_INFRASTRUCTURES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_INVENTORY: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_INWARD_JOBS_FREE_ISSUE_MATERIALS_RETURNS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_INWARD_JOBS_FREE_ISSUE_MATERIALS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_INWARD_JOBS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_LEAVES_ADJUSTMENTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_LEAVES_REQUESTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_MEETINGS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_MERCHANDISES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_NOTES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_ON_DUTIES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_OUTWARD_JOBS_FREE_ISSUE_MATERIALS_RETURNS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_OUTWARD_JOBS_FREE_ISSUE_MATERIALS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_OUTWARD_JOBS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_OVERTIMES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_PRODUCTION_INDENTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_PRODUCTION_PLANS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_PRODUCTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_PROJECTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_PURCHASES_ENQUIRIES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_PURCHASES_INDENTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_PURCHASES_ORDERS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_SUPPLY_OFFERS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_PURCHASES_PAYMENTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_PURCHASES_RETURNS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_QC_GROUPS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_QC_SAMPLES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_QUOTATIONS_REQUESTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_QUOTATIONS_RESPONSES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_REPLACEABLE_INDENTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_ROLES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_SALARIES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_SALES_ENQUIRIES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_SALES_INVOICES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_PROFORMA_INVOICES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_SALES_ORDERS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_SALES_QUOTATIONS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_SALES_RECEIPTS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_SALES_RETURNS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_STOCK_AUDITS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_STOCK_ISSUANCES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_STOCK_RETURNS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_USERS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_VENDOR_INVOICES: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_VENDORS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_VISITATIONS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_SERVICE_NAME_WORK_ORDERS: WORKFLOW_RULE_SERVICE_NAME
WORKFLOW_RULE_MOMENT_ANY_UNSPECIFIED: WORKFLOW_RULE_MOMENT
WORKFLOW_RULE_MOMENT_BEGIN: WORKFLOW_RULE_MOMENT
WORKFLOW_RULE_MOMENT_END: WORKFLOW_RULE_MOMENT
WORKFLOW_RULE_EXECUTE_ON_ANY_UNSPECIFIED: WORKFLOW_RULE_EXECUTE_ON
WORKFLOW_RULE_EXECUTE_ON_SUCCESS: WORKFLOW_RULE_EXECUTE_ON
WORKFLOW_RULE_EXECUTE_ON_FAILURE: WORKFLOW_RULE_EXECUTE_ON
WORKFLOW_RULE_SORT_KEY_ID_UNSPECIFIED: WORKFLOW_RULE_SORT_KEY
WORKFLOW_RULE_SORT_KEY_CREATED_AT: WORKFLOW_RULE_SORT_KEY
WORKFLOW_RULE_SORT_KEY_MODIFIED_AT: WORKFLOW_RULE_SORT_KEY
WORKFLOW_RULE_SORT_KEY_APPROVED_ON: WORKFLOW_RULE_SORT_KEY
WORKFLOW_RULE_SORT_KEY_APPROVED_BY: WORKFLOW_RULE_SORT_KEY
WORKFLOW_RULE_SORT_KEY_APPROVER_ROLE_ID: WORKFLOW_RULE_SORT_KEY
WORKFLOW_RULE_SORT_KEY_COMPLETED_ON: WORKFLOW_RULE_SORT_KEY
WORKFLOW_RULE_SORT_KEY_NAME: WORKFLOW_RULE_SORT_KEY
WORKFLOW_RULE_SORT_KEY_SERVICE_NAME: WORKFLOW_RULE_SORT_KEY

class WorkflowsRulesServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "name", "notify_user_id", "description", "service_name", "record_status", "moment", "execute_on", "user_payload")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    RECORD_STATUS_FIELD_NUMBER: _ClassVar[int]
    MOMENT_FIELD_NUMBER: _ClassVar[int]
    EXECUTE_ON_FIELD_NUMBER: _ClassVar[int]
    USER_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    name: str
    notify_user_id: int
    description: str
    service_name: WORKFLOW_RULE_SERVICE_NAME
    record_status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    moment: WORKFLOW_RULE_MOMENT
    execute_on: WORKFLOW_RULE_EXECUTE_ON
    user_payload: bytes
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., notify_user_id: _Optional[int] = ..., description: _Optional[str] = ..., service_name: _Optional[_Union[WORKFLOW_RULE_SERVICE_NAME, str]] = ..., record_status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., moment: _Optional[_Union[WORKFLOW_RULE_MOMENT, str]] = ..., execute_on: _Optional[_Union[WORKFLOW_RULE_EXECUTE_ON, str]] = ..., user_payload: _Optional[bytes] = ...) -> None: ...

class WorkflowsRulesServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "name", "notify_user_id", "description", "service_name", "record_status", "moment", "execute_on", "user_payload")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    RECORD_STATUS_FIELD_NUMBER: _ClassVar[int]
    MOMENT_FIELD_NUMBER: _ClassVar[int]
    EXECUTE_ON_FIELD_NUMBER: _ClassVar[int]
    USER_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    name: str
    notify_user_id: int
    description: str
    service_name: WORKFLOW_RULE_SERVICE_NAME
    record_status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    moment: WORKFLOW_RULE_MOMENT
    execute_on: WORKFLOW_RULE_EXECUTE_ON
    user_payload: bytes
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., notify_user_id: _Optional[int] = ..., description: _Optional[str] = ..., service_name: _Optional[_Union[WORKFLOW_RULE_SERVICE_NAME, str]] = ..., record_status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., moment: _Optional[_Union[WORKFLOW_RULE_MOMENT, str]] = ..., execute_on: _Optional[_Union[WORKFLOW_RULE_EXECUTE_ON, str]] = ..., user_payload: _Optional[bytes] = ...) -> None: ...

class WorkflowRule(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "name", "code", "notify_user_id", "description", "service_name", "record_status", "moment", "execute_on", "user_payload")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    RECORD_STATUS_FIELD_NUMBER: _ClassVar[int]
    MOMENT_FIELD_NUMBER: _ClassVar[int]
    EXECUTE_ON_FIELD_NUMBER: _ClassVar[int]
    USER_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    completed_on: int
    vault_folder_id: int
    name: str
    code: str
    notify_user_id: int
    description: str
    service_name: WORKFLOW_RULE_SERVICE_NAME
    record_status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    moment: WORKFLOW_RULE_MOMENT
    execute_on: WORKFLOW_RULE_EXECUTE_ON
    user_payload: bytes
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., notify_user_id: _Optional[int] = ..., description: _Optional[str] = ..., service_name: _Optional[_Union[WORKFLOW_RULE_SERVICE_NAME, str]] = ..., record_status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., moment: _Optional[_Union[WORKFLOW_RULE_MOMENT, str]] = ..., execute_on: _Optional[_Union[WORKFLOW_RULE_EXECUTE_ON, str]] = ..., user_payload: _Optional[bytes] = ...) -> None: ...

class WorkflowsRulesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[WorkflowRule]
    def __init__(self, list: _Optional[_Iterable[_Union[WorkflowRule, _Mapping]]] = ...) -> None: ...

class WorkflowsRulesServicePaginationReq(_message.Message):
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
    sort_key: WORKFLOW_RULE_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[WORKFLOW_RULE_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class WorkflowsRulesServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[WorkflowRule]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[WorkflowRule, _Mapping]]] = ...) -> None: ...

class WorkflowsRulesServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "name", "code", "notify_user_id", "service_name", "record_status", "moment", "execute_on")
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
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    RECORD_STATUS_FIELD_NUMBER: _ClassVar[int]
    MOMENT_FIELD_NUMBER: _ClassVar[int]
    EXECUTE_ON_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: WORKFLOW_RULE_SORT_KEY
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
    name: str
    code: str
    notify_user_id: int
    service_name: WORKFLOW_RULE_SERVICE_NAME
    record_status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    moment: WORKFLOW_RULE_MOMENT
    execute_on: WORKFLOW_RULE_EXECUTE_ON
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[WORKFLOW_RULE_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., notify_user_id: _Optional[int] = ..., service_name: _Optional[_Union[WORKFLOW_RULE_SERVICE_NAME, str]] = ..., record_status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., moment: _Optional[_Union[WORKFLOW_RULE_MOMENT, str]] = ..., execute_on: _Optional[_Union[WORKFLOW_RULE_EXECUTE_ON, str]] = ...) -> None: ...

class WorkflowsRulesServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "name", "code", "notify_user_id", "service_name", "record_status", "moment", "execute_on")
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
    NAME_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    RECORD_STATUS_FIELD_NUMBER: _ClassVar[int]
    MOMENT_FIELD_NUMBER: _ClassVar[int]
    EXECUTE_ON_FIELD_NUMBER: _ClassVar[int]
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
    name: str
    code: str
    notify_user_id: int
    service_name: WORKFLOW_RULE_SERVICE_NAME
    record_status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    moment: WORKFLOW_RULE_MOMENT
    execute_on: WORKFLOW_RULE_EXECUTE_ON
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., name: _Optional[str] = ..., code: _Optional[str] = ..., notify_user_id: _Optional[int] = ..., service_name: _Optional[_Union[WORKFLOW_RULE_SERVICE_NAME, str]] = ..., record_status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., moment: _Optional[_Union[WORKFLOW_RULE_MOMENT, str]] = ..., execute_on: _Optional[_Union[WORKFLOW_RULE_EXECUTE_ON, str]] = ...) -> None: ...

class WorkflowsRulesServiceSearchAllReq(_message.Message):
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
    sort_key: WORKFLOW_RULE_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[WORKFLOW_RULE_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ...) -> None: ...

class WorkflowEvent(_message.Message):
    __slots__ = ("event_id", "rule_code", "service_name", "transaction_status", "transaction_payload", "user_payload", "username")
    EVENT_ID_FIELD_NUMBER: _ClassVar[int]
    RULE_CODE_FIELD_NUMBER: _ClassVar[int]
    SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_STATUS_FIELD_NUMBER: _ClassVar[int]
    TRANSACTION_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    USER_PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    event_id: int
    rule_code: str
    service_name: WORKFLOW_RULE_SERVICE_NAME
    transaction_status: WORKFLOW_RULE_EXECUTE_ON
    transaction_payload: bytes
    user_payload: bytes
    username: str
    def __init__(self, event_id: _Optional[int] = ..., rule_code: _Optional[str] = ..., service_name: _Optional[_Union[WORKFLOW_RULE_SERVICE_NAME, str]] = ..., transaction_status: _Optional[_Union[WORKFLOW_RULE_EXECUTE_ON, str]] = ..., transaction_payload: _Optional[bytes] = ..., user_payload: _Optional[bytes] = ..., username: _Optional[str] = ...) -> None: ...
