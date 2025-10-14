from buf.validate import validate_pb2 as _validate_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SORT_ORDER(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ASCENDING_UNSPECIFIED: _ClassVar[SORT_ORDER]
    DESCENDING: _ClassVar[SORT_ORDER]

class STANDARD_LIFECYCLE_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ANY_UNSPECIFIED: _ClassVar[STANDARD_LIFECYCLE_STATUS]
    PREVERIFY: _ClassVar[STANDARD_LIFECYCLE_STATUS]
    DRAFT: _ClassVar[STANDARD_LIFECYCLE_STATUS]
    VERIFIED: _ClassVar[STANDARD_LIFECYCLE_STATUS]
    STANDING: _ClassVar[STANDARD_LIFECYCLE_STATUS]
    REVISION: _ClassVar[STANDARD_LIFECYCLE_STATUS]
    HALTED: _ClassVar[STANDARD_LIFECYCLE_STATUS]
    COMPLETED: _ClassVar[STANDARD_LIFECYCLE_STATUS]
    DISCARDED: _ClassVar[STANDARD_LIFECYCLE_STATUS]

class FORM_TYPE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FORM_TYPE_ANY_UNSPECIFIED: _ClassVar[FORM_TYPE]
    FORM_TYPE_FAMILY_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_SALES_ENQUIRY_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_PURCHASE_ENQUIRY_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_PROJECT_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_SALES_ORDER_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_SALES_QUOTATION_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_CLIENT_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_USER_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_PURCHASE_ORDER_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_SUPPLY_OFFER_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_PURCHASE_INDENT_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_SALES_INVOICE_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_PROFORMA_INVOICE_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_GOODS_DISPATCH_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_VENDOR_INVOICE_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_GOODS_RECEIPT_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_WORK_ORDER_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_VENDOR_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_STOCK_ISSUANCE_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_STOCK_AUDIT_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_STOCK_RETURN_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_EXPENSE_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_LOCATION_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_BANK_ACCOUNT_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_QC_GROUP_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_QUOTATION_REQUEST_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_QUOTATION_RESPONSE_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_PRODUCTION_PLAN_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_PRODUCTION_INDENT_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_REPLACEABLE_INDENT_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_ASSET_INDENT_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_PURCHASE_RETURN_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_SALES_RETURN_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_DEBIT_NOTE_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_CREDIT_NOTE_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_INWARD_JOB_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_INWARD_JOB_FREE_ISSUE_MATERIAL_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_INWARD_JOB_FREE_ISSUE_MATERIAL_RETURN_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_OUTWARD_JOB_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_OUTWARD_JOB_FREE_ISSUE_MATERIAL_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_OUTWARD_JOB_FREE_ISSUE_MATERIAL_RETURN_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_LEAVE_REQUEST_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_OVERTIME_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_ATTENDANCE_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_ABSENCE_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_ONDUTY_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_ATTENDANCE_AMENDMENT_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_VISITATION_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_SALARY_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_SKILL_PARAM_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_SKILL_GROUP_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_GOAL_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_MEETING_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_PRODUCT_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_COMPONENT_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_FEEDSTOCK_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_MERCHANDISE_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_EQUIPMENT_FORM: _ClassVar[FORM_TYPE]
    FORM_TYPE_INFRASTRUCTURE_FORM: _ClassVar[FORM_TYPE]

class FORM_FIELD_ELEMENT(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FORM_FIELD_ELEMENT_ANY_UNSPECIFIED: _ClassVar[FORM_FIELD_ELEMENT]
    FORM_FIELD_ELEMENT_INPUT: _ClassVar[FORM_FIELD_ELEMENT]
    FORM_FIELD_ELEMENT_RADIO: _ClassVar[FORM_FIELD_ELEMENT]
    FORM_FIELD_ELEMENT_CHECKBOX: _ClassVar[FORM_FIELD_ELEMENT]
    FORM_FIELD_ELEMENT_SELECT: _ClassVar[FORM_FIELD_ELEMENT]
    FORM_FIELD_ELEMENT_TEXTAREA: _ClassVar[FORM_FIELD_ELEMENT]
    FORM_FIELD_ELEMENT_DATE: _ClassVar[FORM_FIELD_ELEMENT]
    FORM_FIELD_ELEMENT_EMAIL: _ClassVar[FORM_FIELD_ELEMENT]
    FORM_FIELD_ELEMENT_PHONE: _ClassVar[FORM_FIELD_ELEMENT]
    FORM_FIELD_ELEMENT_NUMBER: _ClassVar[FORM_FIELD_ELEMENT]

class LOGBOOK_OPERATION(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CREATE_UNSPECIFIED: _ClassVar[LOGBOOK_OPERATION]
    UPDATE: _ClassVar[LOGBOOK_OPERATION]
    ARCHIVE: _ClassVar[LOGBOOK_OPERATION]
    RESTORE: _ClassVar[LOGBOOK_OPERATION]

class BOOL_FILTER(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BOOL_FILTER_ANY_UNSPECIFIED: _ClassVar[BOOL_FILTER]
    BOOL_FILTER_TRUE: _ClassVar[BOOL_FILTER]
    BOOL_FILTER_FALSE: _ClassVar[BOOL_FILTER]

class INVENTORY_LIFECYCLE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVENTORY_LIFECYCLE_ANY_UNSPECIFIED: _ClassVar[INVENTORY_LIFECYCLE]
    INVENTORY_LIFECYCLE_QC: _ClassVar[INVENTORY_LIFECYCLE]
    INVENTORY_LIFECYCLE_STORE: _ClassVar[INVENTORY_LIFECYCLE]
    INVENTORY_LIFECYCLE_REWORK: _ClassVar[INVENTORY_LIFECYCLE]
    INVENTORY_LIFECYCLE_CONSUMED: _ClassVar[INVENTORY_LIFECYCLE]
    INVENTORY_LIFECYCLE_REJECTED: _ClassVar[INVENTORY_LIFECYCLE]
    INVENTORY_LIFECYCLE_SCRAP: _ClassVar[INVENTORY_LIFECYCLE]
    INVENTORY_LIFECYCLE_RETURNABLE: _ClassVar[INVENTORY_LIFECYCLE]
    INVENTORY_LIFECYCLE_DISCARDED: _ClassVar[INVENTORY_LIFECYCLE]
    INVENTORY_LIFECYCLE_ISSUED: _ClassVar[INVENTORY_LIFECYCLE]

class INVENTORY_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVENTORY_SORT_KEY_ID_UNSPECIFIED: _ClassVar[INVENTORY_SORT_KEY]
    INVENTORY_SORT_KEY_CREATED_AT: _ClassVar[INVENTORY_SORT_KEY]
    INVENTORY_SORT_KEY_MODIFIED_AT: _ClassVar[INVENTORY_SORT_KEY]
    INVENTORY_SORT_KEY_STORE_INTAKE_AT: _ClassVar[INVENTORY_SORT_KEY]
    INVENTORY_SORT_KEY_DISCARDED_AT: _ClassVar[INVENTORY_SORT_KEY]
    INVENTORY_SORT_KEY_SHELF_TIMESTAMP: _ClassVar[INVENTORY_SORT_KEY]
    INVENTORY_SORT_KEY_WARRANTY_TIMESTAMP: _ClassVar[INVENTORY_SORT_KEY]
    INVENTORY_SORT_KEY_FAMILY_ID: _ClassVar[INVENTORY_SORT_KEY]
    INVENTORY_SORT_KEY_INTERNAL_ITEM_CODE: _ClassVar[INVENTORY_SORT_KEY]
    INVENTORY_SORT_KEY_PRIMARY_QUANTITY: _ClassVar[INVENTORY_SORT_KEY]
    INVENTORY_SORT_KEY_PRIMARY_QUANTITY_REMAINING: _ClassVar[INVENTORY_SORT_KEY]
    INVENTORY_SORT_KEY_SECONDARY_QUANTITY: _ClassVar[INVENTORY_SORT_KEY]
    INVENTORY_SORT_KEY_STORE_ID: _ClassVar[INVENTORY_SORT_KEY]
    INVENTORY_SORT_KEY_STORAGE_ID: _ClassVar[INVENTORY_SORT_KEY]

class INVENTORY_INTERACTION_CATEGORY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVENTORY_INTERACTION_CATEGORY_ANY_UNSPECIFIED: _ClassVar[INVENTORY_INTERACTION_CATEGORY]
    INVENTORY_INTERACTION_CATEGORY_ISSUED: _ClassVar[INVENTORY_INTERACTION_CATEGORY]
    INVENTORY_INTERACTION_CATEGORY_RETURNED: _ClassVar[INVENTORY_INTERACTION_CATEGORY]
    INVENTORY_INTERACTION_CATEGORY_ADJUSTED: _ClassVar[INVENTORY_INTERACTION_CATEGORY]

class INVENTORY_ISSUED_PURPOSE(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVENTORY_ISSUED_PURPOSE_ANY_UNSPECIFIED: _ClassVar[INVENTORY_ISSUED_PURPOSE]
    INVENTORY_ISSUED_PURPOSE_STOCK_ISSUANCE: _ClassVar[INVENTORY_ISSUED_PURPOSE]
    INVENTORY_ISSUED_PURPOSE_STOCK_AUDIT: _ClassVar[INVENTORY_ISSUED_PURPOSE]
    INVENTORY_ISSUED_PURPOSE_STOCK_SPLIT: _ClassVar[INVENTORY_ISSUED_PURPOSE]
    INVENTORY_ISSUED_PURPOSE_STOCK_RETURN: _ClassVar[INVENTORY_ISSUED_PURPOSE]
    INVENTORY_ISSUED_PURPOSE_GOODS_DISPATCH: _ClassVar[INVENTORY_ISSUED_PURPOSE]
    INVENTORY_ISSUED_PURPOSE_INTAKE: _ClassVar[INVENTORY_ISSUED_PURPOSE]
    INVENTORY_ISSUED_PURPOSE_INITIAL_STOCK: _ClassVar[INVENTORY_ISSUED_PURPOSE]
    INVENTORY_ISSUED_PURPOSE_SALES_RETURN: _ClassVar[INVENTORY_ISSUED_PURPOSE]
    INVENTORY_ISSUED_PURPOSE_PURCHASE_RETURN: _ClassVar[INVENTORY_ISSUED_PURPOSE]
    INVENTORY_ISSUED_PURPOSE_OUTWARD_JOB_FREE_ISSUE_MATERIAL: _ClassVar[INVENTORY_ISSUED_PURPOSE]
    INVENTORY_ISSUED_PURPOSE_OUTWARD_JOB_FREE_ISSUE_MATERIAL_RETURN: _ClassVar[INVENTORY_ISSUED_PURPOSE]
    INVENTORY_ISSUED_PURPOSE_INWARD_JOB_FREE_ISSUE_MATERIAL_RETURN: _ClassVar[INVENTORY_ISSUED_PURPOSE]

class AMENDMENT_LOG_REF_FOR(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AMENDMENT_LOG_REF_FOR_ANY_UNSPECIFIED: _ClassVar[AMENDMENT_LOG_REF_FOR]
    AMENDMENT_LOG_REF_FOR_FAMILY: _ClassVar[AMENDMENT_LOG_REF_FOR]
    AMENDMENT_LOG_REF_FOR_PURCHASE_ORDER: _ClassVar[AMENDMENT_LOG_REF_FOR]
    AMENDMENT_LOG_REF_FOR_SUPPLY_OFFER: _ClassVar[AMENDMENT_LOG_REF_FOR]
    AMENDMENT_LOG_REF_FOR_SALES_ORDER: _ClassVar[AMENDMENT_LOG_REF_FOR]
    AMENDMENT_LOG_REF_FOR_SALES_ENQUIRY: _ClassVar[AMENDMENT_LOG_REF_FOR]
    AMENDMENT_LOG_REF_FOR_SALES_QUOTATION: _ClassVar[AMENDMENT_LOG_REF_FOR]
    AMENDMENT_LOG_REF_FOR_SALES_INVOICE: _ClassVar[AMENDMENT_LOG_REF_FOR]
    AMENDMENT_LOG_REF_FOR_PROFORMA_INVOICE: _ClassVar[AMENDMENT_LOG_REF_FOR]
    AMENDMENT_LOG_REF_FOR_WORK_ORDER: _ClassVar[AMENDMENT_LOG_REF_FOR]
    AMENDMENT_LOG_REF_FOR_EQUATION_WORK_ORDER: _ClassVar[AMENDMENT_LOG_REF_FOR]
ASCENDING_UNSPECIFIED: SORT_ORDER
DESCENDING: SORT_ORDER
ANY_UNSPECIFIED: STANDARD_LIFECYCLE_STATUS
PREVERIFY: STANDARD_LIFECYCLE_STATUS
DRAFT: STANDARD_LIFECYCLE_STATUS
VERIFIED: STANDARD_LIFECYCLE_STATUS
STANDING: STANDARD_LIFECYCLE_STATUS
REVISION: STANDARD_LIFECYCLE_STATUS
HALTED: STANDARD_LIFECYCLE_STATUS
COMPLETED: STANDARD_LIFECYCLE_STATUS
DISCARDED: STANDARD_LIFECYCLE_STATUS
FORM_TYPE_ANY_UNSPECIFIED: FORM_TYPE
FORM_TYPE_FAMILY_FORM: FORM_TYPE
FORM_TYPE_SALES_ENQUIRY_FORM: FORM_TYPE
FORM_TYPE_PURCHASE_ENQUIRY_FORM: FORM_TYPE
FORM_TYPE_PROJECT_FORM: FORM_TYPE
FORM_TYPE_SALES_ORDER_FORM: FORM_TYPE
FORM_TYPE_SALES_QUOTATION_FORM: FORM_TYPE
FORM_TYPE_CLIENT_FORM: FORM_TYPE
FORM_TYPE_USER_FORM: FORM_TYPE
FORM_TYPE_PURCHASE_ORDER_FORM: FORM_TYPE
FORM_TYPE_SUPPLY_OFFER_FORM: FORM_TYPE
FORM_TYPE_PURCHASE_INDENT_FORM: FORM_TYPE
FORM_TYPE_SALES_INVOICE_FORM: FORM_TYPE
FORM_TYPE_PROFORMA_INVOICE_FORM: FORM_TYPE
FORM_TYPE_GOODS_DISPATCH_FORM: FORM_TYPE
FORM_TYPE_VENDOR_INVOICE_FORM: FORM_TYPE
FORM_TYPE_GOODS_RECEIPT_FORM: FORM_TYPE
FORM_TYPE_WORK_ORDER_FORM: FORM_TYPE
FORM_TYPE_VENDOR_FORM: FORM_TYPE
FORM_TYPE_STOCK_ISSUANCE_FORM: FORM_TYPE
FORM_TYPE_STOCK_AUDIT_FORM: FORM_TYPE
FORM_TYPE_STOCK_RETURN_FORM: FORM_TYPE
FORM_TYPE_EXPENSE_FORM: FORM_TYPE
FORM_TYPE_LOCATION_FORM: FORM_TYPE
FORM_TYPE_BANK_ACCOUNT_FORM: FORM_TYPE
FORM_TYPE_QC_GROUP_FORM: FORM_TYPE
FORM_TYPE_QUOTATION_REQUEST_FORM: FORM_TYPE
FORM_TYPE_QUOTATION_RESPONSE_FORM: FORM_TYPE
FORM_TYPE_PRODUCTION_PLAN_FORM: FORM_TYPE
FORM_TYPE_PRODUCTION_INDENT_FORM: FORM_TYPE
FORM_TYPE_REPLACEABLE_INDENT_FORM: FORM_TYPE
FORM_TYPE_ASSET_INDENT_FORM: FORM_TYPE
FORM_TYPE_PURCHASE_RETURN_FORM: FORM_TYPE
FORM_TYPE_SALES_RETURN_FORM: FORM_TYPE
FORM_TYPE_DEBIT_NOTE_FORM: FORM_TYPE
FORM_TYPE_CREDIT_NOTE_FORM: FORM_TYPE
FORM_TYPE_INWARD_JOB_FORM: FORM_TYPE
FORM_TYPE_INWARD_JOB_FREE_ISSUE_MATERIAL_FORM: FORM_TYPE
FORM_TYPE_INWARD_JOB_FREE_ISSUE_MATERIAL_RETURN_FORM: FORM_TYPE
FORM_TYPE_OUTWARD_JOB_FORM: FORM_TYPE
FORM_TYPE_OUTWARD_JOB_FREE_ISSUE_MATERIAL_FORM: FORM_TYPE
FORM_TYPE_OUTWARD_JOB_FREE_ISSUE_MATERIAL_RETURN_FORM: FORM_TYPE
FORM_TYPE_LEAVE_REQUEST_FORM: FORM_TYPE
FORM_TYPE_OVERTIME_FORM: FORM_TYPE
FORM_TYPE_ATTENDANCE_FORM: FORM_TYPE
FORM_TYPE_ABSENCE_FORM: FORM_TYPE
FORM_TYPE_ONDUTY_FORM: FORM_TYPE
FORM_TYPE_ATTENDANCE_AMENDMENT_FORM: FORM_TYPE
FORM_TYPE_VISITATION_FORM: FORM_TYPE
FORM_TYPE_SALARY_FORM: FORM_TYPE
FORM_TYPE_SKILL_PARAM_FORM: FORM_TYPE
FORM_TYPE_SKILL_GROUP_FORM: FORM_TYPE
FORM_TYPE_GOAL_FORM: FORM_TYPE
FORM_TYPE_MEETING_FORM: FORM_TYPE
FORM_TYPE_PRODUCT_FORM: FORM_TYPE
FORM_TYPE_COMPONENT_FORM: FORM_TYPE
FORM_TYPE_FEEDSTOCK_FORM: FORM_TYPE
FORM_TYPE_MERCHANDISE_FORM: FORM_TYPE
FORM_TYPE_EQUIPMENT_FORM: FORM_TYPE
FORM_TYPE_INFRASTRUCTURE_FORM: FORM_TYPE
FORM_FIELD_ELEMENT_ANY_UNSPECIFIED: FORM_FIELD_ELEMENT
FORM_FIELD_ELEMENT_INPUT: FORM_FIELD_ELEMENT
FORM_FIELD_ELEMENT_RADIO: FORM_FIELD_ELEMENT
FORM_FIELD_ELEMENT_CHECKBOX: FORM_FIELD_ELEMENT
FORM_FIELD_ELEMENT_SELECT: FORM_FIELD_ELEMENT
FORM_FIELD_ELEMENT_TEXTAREA: FORM_FIELD_ELEMENT
FORM_FIELD_ELEMENT_DATE: FORM_FIELD_ELEMENT
FORM_FIELD_ELEMENT_EMAIL: FORM_FIELD_ELEMENT
FORM_FIELD_ELEMENT_PHONE: FORM_FIELD_ELEMENT
FORM_FIELD_ELEMENT_NUMBER: FORM_FIELD_ELEMENT
CREATE_UNSPECIFIED: LOGBOOK_OPERATION
UPDATE: LOGBOOK_OPERATION
ARCHIVE: LOGBOOK_OPERATION
RESTORE: LOGBOOK_OPERATION
BOOL_FILTER_ANY_UNSPECIFIED: BOOL_FILTER
BOOL_FILTER_TRUE: BOOL_FILTER
BOOL_FILTER_FALSE: BOOL_FILTER
INVENTORY_LIFECYCLE_ANY_UNSPECIFIED: INVENTORY_LIFECYCLE
INVENTORY_LIFECYCLE_QC: INVENTORY_LIFECYCLE
INVENTORY_LIFECYCLE_STORE: INVENTORY_LIFECYCLE
INVENTORY_LIFECYCLE_REWORK: INVENTORY_LIFECYCLE
INVENTORY_LIFECYCLE_CONSUMED: INVENTORY_LIFECYCLE
INVENTORY_LIFECYCLE_REJECTED: INVENTORY_LIFECYCLE
INVENTORY_LIFECYCLE_SCRAP: INVENTORY_LIFECYCLE
INVENTORY_LIFECYCLE_RETURNABLE: INVENTORY_LIFECYCLE
INVENTORY_LIFECYCLE_DISCARDED: INVENTORY_LIFECYCLE
INVENTORY_LIFECYCLE_ISSUED: INVENTORY_LIFECYCLE
INVENTORY_SORT_KEY_ID_UNSPECIFIED: INVENTORY_SORT_KEY
INVENTORY_SORT_KEY_CREATED_AT: INVENTORY_SORT_KEY
INVENTORY_SORT_KEY_MODIFIED_AT: INVENTORY_SORT_KEY
INVENTORY_SORT_KEY_STORE_INTAKE_AT: INVENTORY_SORT_KEY
INVENTORY_SORT_KEY_DISCARDED_AT: INVENTORY_SORT_KEY
INVENTORY_SORT_KEY_SHELF_TIMESTAMP: INVENTORY_SORT_KEY
INVENTORY_SORT_KEY_WARRANTY_TIMESTAMP: INVENTORY_SORT_KEY
INVENTORY_SORT_KEY_FAMILY_ID: INVENTORY_SORT_KEY
INVENTORY_SORT_KEY_INTERNAL_ITEM_CODE: INVENTORY_SORT_KEY
INVENTORY_SORT_KEY_PRIMARY_QUANTITY: INVENTORY_SORT_KEY
INVENTORY_SORT_KEY_PRIMARY_QUANTITY_REMAINING: INVENTORY_SORT_KEY
INVENTORY_SORT_KEY_SECONDARY_QUANTITY: INVENTORY_SORT_KEY
INVENTORY_SORT_KEY_STORE_ID: INVENTORY_SORT_KEY
INVENTORY_SORT_KEY_STORAGE_ID: INVENTORY_SORT_KEY
INVENTORY_INTERACTION_CATEGORY_ANY_UNSPECIFIED: INVENTORY_INTERACTION_CATEGORY
INVENTORY_INTERACTION_CATEGORY_ISSUED: INVENTORY_INTERACTION_CATEGORY
INVENTORY_INTERACTION_CATEGORY_RETURNED: INVENTORY_INTERACTION_CATEGORY
INVENTORY_INTERACTION_CATEGORY_ADJUSTED: INVENTORY_INTERACTION_CATEGORY
INVENTORY_ISSUED_PURPOSE_ANY_UNSPECIFIED: INVENTORY_ISSUED_PURPOSE
INVENTORY_ISSUED_PURPOSE_STOCK_ISSUANCE: INVENTORY_ISSUED_PURPOSE
INVENTORY_ISSUED_PURPOSE_STOCK_AUDIT: INVENTORY_ISSUED_PURPOSE
INVENTORY_ISSUED_PURPOSE_STOCK_SPLIT: INVENTORY_ISSUED_PURPOSE
INVENTORY_ISSUED_PURPOSE_STOCK_RETURN: INVENTORY_ISSUED_PURPOSE
INVENTORY_ISSUED_PURPOSE_GOODS_DISPATCH: INVENTORY_ISSUED_PURPOSE
INVENTORY_ISSUED_PURPOSE_INTAKE: INVENTORY_ISSUED_PURPOSE
INVENTORY_ISSUED_PURPOSE_INITIAL_STOCK: INVENTORY_ISSUED_PURPOSE
INVENTORY_ISSUED_PURPOSE_SALES_RETURN: INVENTORY_ISSUED_PURPOSE
INVENTORY_ISSUED_PURPOSE_PURCHASE_RETURN: INVENTORY_ISSUED_PURPOSE
INVENTORY_ISSUED_PURPOSE_OUTWARD_JOB_FREE_ISSUE_MATERIAL: INVENTORY_ISSUED_PURPOSE
INVENTORY_ISSUED_PURPOSE_OUTWARD_JOB_FREE_ISSUE_MATERIAL_RETURN: INVENTORY_ISSUED_PURPOSE
INVENTORY_ISSUED_PURPOSE_INWARD_JOB_FREE_ISSUE_MATERIAL_RETURN: INVENTORY_ISSUED_PURPOSE
AMENDMENT_LOG_REF_FOR_ANY_UNSPECIFIED: AMENDMENT_LOG_REF_FOR
AMENDMENT_LOG_REF_FOR_FAMILY: AMENDMENT_LOG_REF_FOR
AMENDMENT_LOG_REF_FOR_PURCHASE_ORDER: AMENDMENT_LOG_REF_FOR
AMENDMENT_LOG_REF_FOR_SUPPLY_OFFER: AMENDMENT_LOG_REF_FOR
AMENDMENT_LOG_REF_FOR_SALES_ORDER: AMENDMENT_LOG_REF_FOR
AMENDMENT_LOG_REF_FOR_SALES_ENQUIRY: AMENDMENT_LOG_REF_FOR
AMENDMENT_LOG_REF_FOR_SALES_QUOTATION: AMENDMENT_LOG_REF_FOR
AMENDMENT_LOG_REF_FOR_SALES_INVOICE: AMENDMENT_LOG_REF_FOR
AMENDMENT_LOG_REF_FOR_PROFORMA_INVOICE: AMENDMENT_LOG_REF_FOR
AMENDMENT_LOG_REF_FOR_WORK_ORDER: AMENDMENT_LOG_REF_FOR
AMENDMENT_LOG_REF_FOR_EQUATION_WORK_ORDER: AMENDMENT_LOG_REF_FOR

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class BooleanResponse(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bool
    def __init__(self, value: _Optional[bool] = ...) -> None: ...

class BytesResponse(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: bytes
    def __init__(self, value: _Optional[bytes] = ...) -> None: ...

class StringResponse(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    def __init__(self, value: _Optional[str] = ...) -> None: ...

class PriceResponse(_message.Message):
    __slots__ = ("value",)
    VALUE_FIELD_NUMBER: _ClassVar[int]
    value: int
    def __init__(self, value: _Optional[int] = ...) -> None: ...

class ImageResponse(_message.Message):
    __slots__ = ("image", "mime_type", "timestamp")
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    image: bytes
    mime_type: str
    timestamp: int
    def __init__(self, image: _Optional[bytes] = ..., mime_type: _Optional[str] = ..., timestamp: _Optional[int] = ...) -> None: ...

class Base64String(_message.Message):
    __slots__ = ("image",)
    IMAGE_FIELD_NUMBER: _ClassVar[int]
    image: str
    def __init__(self, image: _Optional[str] = ...) -> None: ...

class MonthAndDayFilter(_message.Message):
    __slots__ = ("month", "day")
    MONTH_FIELD_NUMBER: _ClassVar[int]
    DAY_FIELD_NUMBER: _ClassVar[int]
    month: int
    day: int
    def __init__(self, month: _Optional[int] = ..., day: _Optional[int] = ...) -> None: ...

class GPSCoordinatesResponse(_message.Message):
    __slots__ = ("latitude", "longitude")
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    latitude: float
    longitude: float
    def __init__(self, latitude: _Optional[float] = ..., longitude: _Optional[float] = ...) -> None: ...

class CountInSLCStatusRequest(_message.Message):
    __slots__ = ("is_active", "status")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    is_active: BOOL_FILTER
    status: STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[BOOL_FILTER, str]] = ..., status: _Optional[_Union[STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class CountResponse(_message.Message):
    __slots__ = ("count",)
    COUNT_FIELD_NUMBER: _ClassVar[int]
    count: int
    def __init__(self, count: _Optional[int] = ...) -> None: ...

class SumResponse(_message.Message):
    __slots__ = ("sum",)
    SUM_FIELD_NUMBER: _ClassVar[int]
    sum: float
    def __init__(self, sum: _Optional[float] = ...) -> None: ...

class QuantityResponse(_message.Message):
    __slots__ = ("quantity",)
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    quantity: int
    def __init__(self, quantity: _Optional[int] = ...) -> None: ...

class DualQuantitiesResponse(_message.Message):
    __slots__ = ("primary_quantity", "secondary_quantity")
    PRIMARY_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    primary_quantity: int
    secondary_quantity: int
    def __init__(self, primary_quantity: _Optional[int] = ..., secondary_quantity: _Optional[int] = ...) -> None: ...

class EmployeeMetadata(_message.Message):
    __slots__ = ("id", "uuid", "added_by", "is_active", "created_at", "modified_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    ADDED_BY_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    uuid: str
    added_by: str
    is_active: bool
    created_at: int
    modified_at: int
    def __init__(self, id: _Optional[int] = ..., uuid: _Optional[str] = ..., added_by: _Optional[str] = ..., is_active: _Optional[bool] = ..., created_at: _Optional[int] = ..., modified_at: _Optional[int] = ...) -> None: ...

class ApprovalMetadata(_message.Message):
    __slots__ = ("approved_on", "approved_by_user_id", "approver_role_id")
    APPROVED_ON_FIELD_NUMBER: _ClassVar[int]
    APPROVED_BY_USER_ID_FIELD_NUMBER: _ClassVar[int]
    APPROVER_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    approved_on: int
    approved_by_user_id: int
    approver_role_id: int
    def __init__(self, approved_on: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ...) -> None: ...

class ActiveStatus(_message.Message):
    __slots__ = ("is_active",)
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    is_active: BOOL_FILTER
    def __init__(self, is_active: _Optional[_Union[BOOL_FILTER, str]] = ...) -> None: ...

class UpdatePasswordReq(_message.Message):
    __slots__ = ("user_comment", "id", "plain_text_password")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PLAIN_TEXT_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    plain_text_password: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., plain_text_password: _Optional[str] = ...) -> None: ...

class UpdateOwnPasswordReq(_message.Message):
    __slots__ = ("user_comment", "old_plain_text_password", "plain_text_password")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    OLD_PLAIN_TEXT_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    PLAIN_TEXT_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    old_plain_text_password: str
    plain_text_password: str
    def __init__(self, user_comment: _Optional[str] = ..., old_plain_text_password: _Optional[str] = ..., plain_text_password: _Optional[str] = ...) -> None: ...

class UploadPictureReq(_message.Message):
    __slots__ = ("user_comment", "id", "img", "mime_type")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    IMG_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    img: str
    mime_type: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., img: _Optional[str] = ..., mime_type: _Optional[str] = ...) -> None: ...

class SimpleSearchReq(_message.Message):
    __slots__ = ("search_key",)
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    search_key: str
    def __init__(self, search_key: _Optional[str] = ...) -> None: ...

class RepeatWithDeliveryDate(_message.Message):
    __slots__ = ("uuid", "user_comment", "reference_id", "delivery_date")
    UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    user_comment: str
    reference_id: str
    delivery_date: str
    def __init__(self, uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., reference_id: _Optional[str] = ..., delivery_date: _Optional[str] = ...) -> None: ...

class Identifier(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class IdentifierResponse(_message.Message):
    __slots__ = ("id", "uuid")
    ID_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    id: int
    uuid: str
    def __init__(self, id: _Optional[int] = ..., uuid: _Optional[str] = ...) -> None: ...

class IdentifierZeroable(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class IdentifiersList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, list: _Optional[_Iterable[int]] = ...) -> None: ...

class StringsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, list: _Optional[_Iterable[str]] = ...) -> None: ...

class IdentifierWithUserComment(_message.Message):
    __slots__ = ("id", "user_comment")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    id: int
    user_comment: str
    def __init__(self, id: _Optional[int] = ..., user_comment: _Optional[str] = ...) -> None: ...

class IdentifierWithEmailAttributes(_message.Message):
    __slots__ = ("id", "subject", "recipients", "body")
    ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    RECIPIENTS_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    id: int
    subject: str
    recipients: _containers.RepeatedScalarFieldContainer[str]
    body: str
    def __init__(self, id: _Optional[int] = ..., subject: _Optional[str] = ..., recipients: _Optional[_Iterable[str]] = ..., body: _Optional[str] = ...) -> None: ...

class IdentifierWithSearchKey(_message.Message):
    __slots__ = ("id", "search_key")
    ID_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    id: int
    search_key: str
    def __init__(self, id: _Optional[int] = ..., search_key: _Optional[str] = ...) -> None: ...

class IdentifierWithFile(_message.Message):
    __slots__ = ("id", "file_content")
    ID_FIELD_NUMBER: _ClassVar[int]
    FILE_CONTENT_FIELD_NUMBER: _ClassVar[int]
    id: int
    file_content: bytes
    def __init__(self, id: _Optional[int] = ..., file_content: _Optional[bytes] = ...) -> None: ...

class IdentifierUUIDWithFile(_message.Message):
    __slots__ = ("uuid", "file_content")
    UUID_FIELD_NUMBER: _ClassVar[int]
    FILE_CONTENT_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    file_content: bytes
    def __init__(self, uuid: _Optional[str] = ..., file_content: _Optional[bytes] = ...) -> None: ...

class IdentifierUUID(_message.Message):
    __slots__ = ("uuid",)
    UUID_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    def __init__(self, uuid: _Optional[str] = ...) -> None: ...

class IdentifierUUIDWithUserComment(_message.Message):
    __slots__ = ("uuid", "user_comment")
    UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    user_comment: str
    def __init__(self, uuid: _Optional[str] = ..., user_comment: _Optional[str] = ...) -> None: ...

class IdentifierUUIDsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[IdentifierUUID]
    def __init__(self, list: _Optional[_Iterable[_Union[IdentifierUUID, _Mapping]]] = ...) -> None: ...

class LogbookLogConciseSLC(_message.Message):
    __slots__ = ("id", "is_active", "timestamp", "ref_uuid", "operation", "username", "name", "user_id", "app_comment", "user_comment")
    ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    APP_COMMENT_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    id: int
    is_active: bool
    timestamp: int
    ref_uuid: str
    operation: STANDARD_LIFECYCLE_STATUS
    username: str
    name: str
    user_id: int
    app_comment: str
    user_comment: str
    def __init__(self, id: _Optional[int] = ..., is_active: _Optional[bool] = ..., timestamp: _Optional[int] = ..., ref_uuid: _Optional[str] = ..., operation: _Optional[_Union[STANDARD_LIFECYCLE_STATUS, str]] = ..., username: _Optional[str] = ..., name: _Optional[str] = ..., user_id: _Optional[int] = ..., app_comment: _Optional[str] = ..., user_comment: _Optional[str] = ...) -> None: ...

class LogbookLogConciseSLCCreateRequest(_message.Message):
    __slots__ = ("timestamp", "ref_uuid", "operation", "username", "app_comment", "user_comment")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    APP_COMMENT_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    ref_uuid: str
    operation: STANDARD_LIFECYCLE_STATUS
    username: str
    app_comment: str
    user_comment: str
    def __init__(self, timestamp: _Optional[int] = ..., ref_uuid: _Optional[str] = ..., operation: _Optional[_Union[STANDARD_LIFECYCLE_STATUS, str]] = ..., username: _Optional[str] = ..., app_comment: _Optional[str] = ..., user_comment: _Optional[str] = ...) -> None: ...

class LogbookLogConciseGenericCreateRequest(_message.Message):
    __slots__ = ("timestamp", "ref_uuid", "operation", "username", "app_comment", "user_comment")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    APP_COMMENT_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    ref_uuid: str
    operation: str
    username: str
    app_comment: str
    user_comment: str
    def __init__(self, timestamp: _Optional[int] = ..., ref_uuid: _Optional[str] = ..., operation: _Optional[str] = ..., username: _Optional[str] = ..., app_comment: _Optional[str] = ..., user_comment: _Optional[str] = ...) -> None: ...

class LogbookLogComplete(_message.Message):
    __slots__ = ("metadata", "ref_uuid", "operation", "username", "app_comment", "user_comment", "previous_data")
    METADATA_FIELD_NUMBER: _ClassVar[int]
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    APP_COMMENT_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_DATA_FIELD_NUMBER: _ClassVar[int]
    metadata: EmployeeMetadata
    ref_uuid: str
    operation: LOGBOOK_OPERATION
    username: str
    app_comment: str
    user_comment: str
    previous_data: bytes
    def __init__(self, metadata: _Optional[_Union[EmployeeMetadata, _Mapping]] = ..., ref_uuid: _Optional[str] = ..., operation: _Optional[_Union[LOGBOOK_OPERATION, str]] = ..., username: _Optional[str] = ..., app_comment: _Optional[str] = ..., user_comment: _Optional[str] = ..., previous_data: _Optional[bytes] = ...) -> None: ...

class ReorderItemsRequest(_message.Message):
    __slots__ = ("id", "sequence")
    ID_FIELD_NUMBER: _ClassVar[int]
    SEQUENCE_FIELD_NUMBER: _ClassVar[int]
    id: int
    sequence: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, id: _Optional[int] = ..., sequence: _Optional[_Iterable[int]] = ...) -> None: ...

class CloneRequest(_message.Message):
    __slots__ = ("source_id", "target_id", "delete_existing", "user_comment")
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    DELETE_EXISTING_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    source_id: int
    target_id: int
    delete_existing: bool
    user_comment: str
    def __init__(self, source_id: _Optional[int] = ..., target_id: _Optional[int] = ..., delete_existing: _Optional[bool] = ..., user_comment: _Optional[str] = ...) -> None: ...

class StandardFile(_message.Message):
    __slots__ = ("name", "mime_type", "content")
    NAME_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    name: str
    mime_type: str
    content: bytes
    def __init__(self, name: _Optional[str] = ..., mime_type: _Optional[str] = ..., content: _Optional[bytes] = ...) -> None: ...

class LogbookLogInventoryLC(_message.Message):
    __slots__ = ("id", "is_active", "timestamp", "ref_uuid", "operation", "username", "name", "user_id", "app_comment", "user_comment")
    ID_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    REF_UUID_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    APP_COMMENT_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    id: int
    is_active: bool
    timestamp: int
    ref_uuid: str
    operation: INVENTORY_LIFECYCLE
    username: str
    name: str
    user_id: int
    app_comment: str
    user_comment: str
    def __init__(self, id: _Optional[int] = ..., is_active: _Optional[bool] = ..., timestamp: _Optional[int] = ..., ref_uuid: _Optional[str] = ..., operation: _Optional[_Union[INVENTORY_LIFECYCLE, str]] = ..., username: _Optional[str] = ..., name: _Optional[str] = ..., user_id: _Optional[int] = ..., app_comment: _Optional[str] = ..., user_comment: _Optional[str] = ...) -> None: ...

class InventoryPartitionRequest(_message.Message):
    __slots__ = ("id", "user_comment", "partition_quantity", "partition_secondary_quantity")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    PARTITION_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PARTITION_SECONDARY_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    id: int
    user_comment: str
    partition_quantity: int
    partition_secondary_quantity: int
    def __init__(self, id: _Optional[int] = ..., user_comment: _Optional[str] = ..., partition_quantity: _Optional[int] = ..., partition_secondary_quantity: _Optional[int] = ...) -> None: ...

class InventoryInteraction(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "category", "inventory_ref_uuid", "issued_inventory_hash", "issued_ref_purpose", "issued_ref_id", "internal_quantity")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    INVENTORY_REF_UUID_FIELD_NUMBER: _ClassVar[int]
    ISSUED_INVENTORY_HASH_FIELD_NUMBER: _ClassVar[int]
    ISSUED_REF_PURPOSE_FIELD_NUMBER: _ClassVar[int]
    ISSUED_REF_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: EmployeeMetadata
    category: INVENTORY_INTERACTION_CATEGORY
    inventory_ref_uuid: str
    issued_inventory_hash: str
    issued_ref_purpose: INVENTORY_ISSUED_PURPOSE
    issued_ref_id: int
    internal_quantity: int
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[EmployeeMetadata, _Mapping]] = ..., category: _Optional[_Union[INVENTORY_INTERACTION_CATEGORY, str]] = ..., inventory_ref_uuid: _Optional[str] = ..., issued_inventory_hash: _Optional[str] = ..., issued_ref_purpose: _Optional[_Union[INVENTORY_ISSUED_PURPOSE, str]] = ..., issued_ref_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ...) -> None: ...

class InventoryInteractionsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[InventoryInteraction]
    def __init__(self, list: _Optional[_Iterable[_Union[InventoryInteraction, _Mapping]]] = ...) -> None: ...

class AmendmentLog(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "ref_for", "ref_id", "comment")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    REF_FOR_FIELD_NUMBER: _ClassVar[int]
    REF_ID_FIELD_NUMBER: _ClassVar[int]
    COMMENT_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: EmployeeMetadata
    ref_for: AMENDMENT_LOG_REF_FOR
    ref_id: int
    comment: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[EmployeeMetadata, _Mapping]] = ..., ref_for: _Optional[_Union[AMENDMENT_LOG_REF_FOR, str]] = ..., ref_id: _Optional[int] = ..., comment: _Optional[str] = ...) -> None: ...

class AmendmentLogsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[AmendmentLog]
    def __init__(self, list: _Optional[_Iterable[_Union[AmendmentLog, _Mapping]]] = ...) -> None: ...
