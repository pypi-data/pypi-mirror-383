from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from forms_fields_data import scailo_pb2 as _scailo_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SALARY_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SALARY_SORT_KEY_ID_UNSPECIFIED: _ClassVar[SALARY_SORT_KEY]
    SALARY_SORT_KEY_CREATED_AT: _ClassVar[SALARY_SORT_KEY]
    SALARY_SORT_KEY_MODIFIED_AT: _ClassVar[SALARY_SORT_KEY]
    SALARY_SORT_KEY_APPROVED_ON: _ClassVar[SALARY_SORT_KEY]
    SALARY_SORT_KEY_APPROVED_BY: _ClassVar[SALARY_SORT_KEY]
    SALARY_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[SALARY_SORT_KEY]
    SALARY_SORT_KEY_COMPLETED_ON: _ClassVar[SALARY_SORT_KEY]
    SALARY_SORT_KEY_REFERENCE_ID: _ClassVar[SALARY_SORT_KEY]
    SALARY_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[SALARY_SORT_KEY]
    SALARY_SORT_KEY_EMPLOYEE_ID: _ClassVar[SALARY_SORT_KEY]
    SALARY_SORT_KEY_BANK_ACCOUNT_ID: _ClassVar[SALARY_SORT_KEY]
    SALARY_SORT_KEY_CURRENCY_ID: _ClassVar[SALARY_SORT_KEY]
    SALARY_SORT_KEY_PAYROLL_GROUP_ID: _ClassVar[SALARY_SORT_KEY]
    SALARY_SORT_KEY_TAX_GROUP_ID: _ClassVar[SALARY_SORT_KEY]
SALARY_SORT_KEY_ID_UNSPECIFIED: SALARY_SORT_KEY
SALARY_SORT_KEY_CREATED_AT: SALARY_SORT_KEY
SALARY_SORT_KEY_MODIFIED_AT: SALARY_SORT_KEY
SALARY_SORT_KEY_APPROVED_ON: SALARY_SORT_KEY
SALARY_SORT_KEY_APPROVED_BY: SALARY_SORT_KEY
SALARY_SORT_KEY_APPROVER_ROLE_ID: SALARY_SORT_KEY
SALARY_SORT_KEY_COMPLETED_ON: SALARY_SORT_KEY
SALARY_SORT_KEY_REFERENCE_ID: SALARY_SORT_KEY
SALARY_SORT_KEY_FINAL_REF_NUMBER: SALARY_SORT_KEY
SALARY_SORT_KEY_EMPLOYEE_ID: SALARY_SORT_KEY
SALARY_SORT_KEY_BANK_ACCOUNT_ID: SALARY_SORT_KEY
SALARY_SORT_KEY_CURRENCY_ID: SALARY_SORT_KEY
SALARY_SORT_KEY_PAYROLL_GROUP_ID: SALARY_SORT_KEY
SALARY_SORT_KEY_TAX_GROUP_ID: SALARY_SORT_KEY

class SalariesServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "employee_id", "from_date", "to_date", "bank_account_id", "currency_id", "basic_pay_amount", "basic_pay_uom_id", "applicable_attendance_records_count", "applicable_attendance_uom_id", "cf_from_attendance_uom_id_to_basic_pay_uom_id_numerator", "cf_from_attendance_uom_id_to_basic_pay_uom_id_denominator", "payroll_group_id", "tax_group_id", "description", "round_off", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_DATE_FIELD_NUMBER: _ClassVar[int]
    TO_DATE_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICABLE_ATTENDANCE_RECORDS_COUNT_FIELD_NUMBER: _ClassVar[int]
    APPLICABLE_ATTENDANCE_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    CF_FROM_ATTENDANCE_UOM_ID_TO_BASIC_PAY_UOM_ID_NUMERATOR_FIELD_NUMBER: _ClassVar[int]
    CF_FROM_ATTENDANCE_UOM_ID_TO_BASIC_PAY_UOM_ID_DENOMINATOR_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    employee_id: int
    from_date: str
    to_date: str
    bank_account_id: int
    currency_id: int
    basic_pay_amount: int
    basic_pay_uom_id: int
    applicable_attendance_records_count: int
    applicable_attendance_uom_id: int
    cf_from_attendance_uom_id_to_basic_pay_uom_id_numerator: int
    cf_from_attendance_uom_id_to_basic_pay_uom_id_denominator: int
    payroll_group_id: int
    tax_group_id: int
    description: str
    round_off: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., employee_id: _Optional[int] = ..., from_date: _Optional[str] = ..., to_date: _Optional[str] = ..., bank_account_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., basic_pay_amount: _Optional[int] = ..., basic_pay_uom_id: _Optional[int] = ..., applicable_attendance_records_count: _Optional[int] = ..., applicable_attendance_uom_id: _Optional[int] = ..., cf_from_attendance_uom_id_to_basic_pay_uom_id_numerator: _Optional[int] = ..., cf_from_attendance_uom_id_to_basic_pay_uom_id_denominator: _Optional[int] = ..., payroll_group_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., description: _Optional[str] = ..., round_off: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class SalariesServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "from_date", "to_date", "bank_account_id", "currency_id", "basic_pay_amount", "basic_pay_uom_id", "applicable_attendance_records_count", "applicable_attendance_uom_id", "cf_from_attendance_uom_id_to_basic_pay_uom_id_numerator", "cf_from_attendance_uom_id_to_basic_pay_uom_id_denominator", "payroll_group_id", "tax_group_id", "description", "round_off", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_DATE_FIELD_NUMBER: _ClassVar[int]
    TO_DATE_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICABLE_ATTENDANCE_RECORDS_COUNT_FIELD_NUMBER: _ClassVar[int]
    APPLICABLE_ATTENDANCE_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    CF_FROM_ATTENDANCE_UOM_ID_TO_BASIC_PAY_UOM_ID_NUMERATOR_FIELD_NUMBER: _ClassVar[int]
    CF_FROM_ATTENDANCE_UOM_ID_TO_BASIC_PAY_UOM_ID_DENOMINATOR_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    from_date: str
    to_date: str
    bank_account_id: int
    currency_id: int
    basic_pay_amount: int
    basic_pay_uom_id: int
    applicable_attendance_records_count: int
    applicable_attendance_uom_id: int
    cf_from_attendance_uom_id_to_basic_pay_uom_id_numerator: int
    cf_from_attendance_uom_id_to_basic_pay_uom_id_denominator: int
    payroll_group_id: int
    tax_group_id: int
    description: str
    round_off: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., from_date: _Optional[str] = ..., to_date: _Optional[str] = ..., bank_account_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., basic_pay_amount: _Optional[int] = ..., basic_pay_uom_id: _Optional[int] = ..., applicable_attendance_records_count: _Optional[int] = ..., applicable_attendance_uom_id: _Optional[int] = ..., cf_from_attendance_uom_id_to_basic_pay_uom_id_numerator: _Optional[int] = ..., cf_from_attendance_uom_id_to_basic_pay_uom_id_denominator: _Optional[int] = ..., payroll_group_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., description: _Optional[str] = ..., round_off: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class SalariesServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ...) -> None: ...

class Salary(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "employee_id", "from_date", "to_date", "bank_account_id", "currency_id", "basic_pay_amount", "basic_pay_uom_id", "applicable_attendance_records_count", "applicable_attendance_uom_id", "cf_from_attendance_uom_id_to_basic_pay_uom_id_numerator", "cf_from_attendance_uom_id_to_basic_pay_uom_id_denominator", "payroll_group_id", "tax_group_id", "description", "round_off", "addition_items_list", "deduction_items_list", "reimbursement_items_list", "form_data", "total_amount")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    FROM_DATE_FIELD_NUMBER: _ClassVar[int]
    TO_DATE_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    BASIC_PAY_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    APPLICABLE_ATTENDANCE_RECORDS_COUNT_FIELD_NUMBER: _ClassVar[int]
    APPLICABLE_ATTENDANCE_UOM_ID_FIELD_NUMBER: _ClassVar[int]
    CF_FROM_ATTENDANCE_UOM_ID_TO_BASIC_PAY_UOM_ID_NUMERATOR_FIELD_NUMBER: _ClassVar[int]
    CF_FROM_ATTENDANCE_UOM_ID_TO_BASIC_PAY_UOM_ID_DENOMINATOR_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ROUND_OFF_FIELD_NUMBER: _ClassVar[int]
    ADDITION_ITEMS_LIST_FIELD_NUMBER: _ClassVar[int]
    DEDUCTION_ITEMS_LIST_FIELD_NUMBER: _ClassVar[int]
    REIMBURSEMENT_ITEMS_LIST_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    TOTAL_AMOUNT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    completed_on: int
    vault_folder_id: int
    reference_id: str
    final_ref_number: str
    employee_id: int
    from_date: str
    to_date: str
    bank_account_id: int
    currency_id: int
    basic_pay_amount: int
    basic_pay_uom_id: int
    applicable_attendance_records_count: int
    applicable_attendance_uom_id: int
    cf_from_attendance_uom_id_to_basic_pay_uom_id_numerator: int
    cf_from_attendance_uom_id_to_basic_pay_uom_id_denominator: int
    payroll_group_id: int
    tax_group_id: int
    description: str
    round_off: int
    addition_items_list: _containers.RepeatedCompositeFieldContainer[SalaryAdditionItem]
    deduction_items_list: _containers.RepeatedCompositeFieldContainer[SalaryDeductionItem]
    reimbursement_items_list: _containers.RepeatedCompositeFieldContainer[SalaryReimbursementItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatum]
    total_amount: float
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., employee_id: _Optional[int] = ..., from_date: _Optional[str] = ..., to_date: _Optional[str] = ..., bank_account_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., basic_pay_amount: _Optional[int] = ..., basic_pay_uom_id: _Optional[int] = ..., applicable_attendance_records_count: _Optional[int] = ..., applicable_attendance_uom_id: _Optional[int] = ..., cf_from_attendance_uom_id_to_basic_pay_uom_id_numerator: _Optional[int] = ..., cf_from_attendance_uom_id_to_basic_pay_uom_id_denominator: _Optional[int] = ..., payroll_group_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., description: _Optional[str] = ..., round_off: _Optional[int] = ..., addition_items_list: _Optional[_Iterable[_Union[SalaryAdditionItem, _Mapping]]] = ..., deduction_items_list: _Optional[_Iterable[_Union[SalaryDeductionItem, _Mapping]]] = ..., reimbursement_items_list: _Optional[_Iterable[_Union[SalaryReimbursementItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatum, _Mapping]]] = ..., total_amount: _Optional[float] = ...) -> None: ...

class SalariesList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[Salary]
    def __init__(self, list: _Optional[_Iterable[_Union[Salary, _Mapping]]] = ...) -> None: ...

class SalariesServiceAdditionItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "salary_id", "ref_from", "ref_id", "quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALARY_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    salary_id: int
    ref_from: str
    ref_id: int
    quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., salary_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class SalariesServiceAdditionItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class SalaryAdditionItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "salary_id", "ref_from", "ref_id", "quantity")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALARY_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    salary_id: int
    ref_from: str
    ref_id: int
    quantity: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., salary_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class SalariesAdditionItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalaryAdditionItem]
    def __init__(self, list: _Optional[_Iterable[_Union[SalaryAdditionItem, _Mapping]]] = ...) -> None: ...

class SalaryAdditionItemHistoryRequest(_message.Message):
    __slots__ = ("salary_id", "ref_from", "ref_id")
    SALARY_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    salary_id: int
    ref_from: str
    ref_id: int
    def __init__(self, salary_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ...) -> None: ...

class SalaryAdditionItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("salary_id", "ref_from")
    SALARY_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    salary_id: int
    ref_from: str
    def __init__(self, salary_id: _Optional[int] = ..., ref_from: _Optional[str] = ...) -> None: ...

class SalariesServiceDeductionItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "salary_id", "ref_from", "ref_id", "quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALARY_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    salary_id: int
    ref_from: str
    ref_id: int
    quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., salary_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class SalariesServiceDeductionItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "quantity")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    quantity: int
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class SalaryDeductionItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "salary_id", "ref_from", "ref_id", "quantity")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALARY_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    salary_id: int
    ref_from: str
    ref_id: int
    quantity: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., salary_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class SalariesDeductionItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalaryDeductionItem]
    def __init__(self, list: _Optional[_Iterable[_Union[SalaryDeductionItem, _Mapping]]] = ...) -> None: ...

class SalaryDeductionItemHistoryRequest(_message.Message):
    __slots__ = ("salary_id", "ref_from", "ref_id")
    SALARY_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    salary_id: int
    ref_from: str
    ref_id: int
    def __init__(self, salary_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ...) -> None: ...

class SalaryDeductionItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("salary_id", "ref_from")
    SALARY_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    salary_id: int
    ref_from: str
    def __init__(self, salary_id: _Optional[int] = ..., ref_from: _Optional[str] = ...) -> None: ...

class SalariesServiceReimbursementItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "salary_id", "ref_from", "ref_id", "amount")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALARY_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    salary_id: int
    ref_from: str
    ref_id: int
    amount: int
    def __init__(self, user_comment: _Optional[str] = ..., salary_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., amount: _Optional[int] = ...) -> None: ...

class SalariesServiceReimbursementItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "amount")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    amount: int
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., amount: _Optional[int] = ...) -> None: ...

class SalaryReimbursementItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "salary_id", "ref_from", "ref_id", "amount")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    SALARY_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    salary_id: int
    ref_from: str
    ref_id: int
    amount: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., salary_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ..., amount: _Optional[int] = ...) -> None: ...

class SalariesReimbursementItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[SalaryReimbursementItem]
    def __init__(self, list: _Optional[_Iterable[_Union[SalaryReimbursementItem, _Mapping]]] = ...) -> None: ...

class SalaryReimbursementItemHistoryRequest(_message.Message):
    __slots__ = ("salary_id", "ref_from", "ref_id")
    SALARY_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    salary_id: int
    ref_from: str
    ref_id: int
    def __init__(self, salary_id: _Optional[int] = ..., ref_from: _Optional[str] = ..., ref_id: _Optional[int] = ...) -> None: ...

class SalaryReimbursementItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("salary_id", "ref_from")
    SALARY_ID_FIELD_NUMBER: _ClassVar[int]
    REF_FROM_FIELD_NUMBER: _ClassVar[int]
    salary_id: int
    ref_from: str
    def __init__(self, salary_id: _Optional[int] = ..., ref_from: _Optional[str] = ...) -> None: ...

class SalariesServicePaginationReq(_message.Message):
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
    sort_key: SALARY_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALARY_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class SalariesServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[Salary]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[Salary, _Mapping]]] = ...) -> None: ...

class SalariesServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "employee_id", "bank_account_id", "currency_id", "payroll_group_id", "tax_group_id", "form_data")
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
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: SALARY_SORT_KEY
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
    employee_id: int
    bank_account_id: int
    currency_id: int
    payroll_group_id: int
    tax_group_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALARY_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., employee_id: _Optional[int] = ..., bank_account_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., payroll_group_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class SalariesServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "reference_id", "final_ref_number", "employee_id", "bank_account_id", "currency_id", "payroll_group_id", "tax_group_id", "form_data")
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
    EMPLOYEE_ID_FIELD_NUMBER: _ClassVar[int]
    BANK_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_ID_FIELD_NUMBER: _ClassVar[int]
    PAYROLL_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
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
    employee_id: int
    bank_account_id: int
    currency_id: int
    payroll_group_id: int
    tax_group_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., employee_id: _Optional[int] = ..., bank_account_id: _Optional[int] = ..., currency_id: _Optional[int] = ..., payroll_group_id: _Optional[int] = ..., tax_group_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class SalariesServiceSearchAllReq(_message.Message):
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
    sort_key: SALARY_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[SALARY_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ...) -> None: ...
