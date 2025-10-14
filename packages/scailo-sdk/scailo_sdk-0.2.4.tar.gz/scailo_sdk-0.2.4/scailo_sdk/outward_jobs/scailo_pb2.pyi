from base import scailo_pb2 as _scailo_pb2
from buf.validate import validate_pb2 as _validate_pb2
from families import scailo_pb2 as _scailo_pb2_1
from forms_fields_data import scailo_pb2 as _scailo_pb2_1_1
from magic_links import scailo_pb2 as _scailo_pb2_1_1_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OUTWARD_JOB_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OUTWARD_JOB_SORT_KEY_ID_UNSPECIFIED: _ClassVar[OUTWARD_JOB_SORT_KEY]
    OUTWARD_JOB_SORT_KEY_CREATED_AT: _ClassVar[OUTWARD_JOB_SORT_KEY]
    OUTWARD_JOB_SORT_KEY_MODIFIED_AT: _ClassVar[OUTWARD_JOB_SORT_KEY]
    OUTWARD_JOB_SORT_KEY_APPROVED_ON: _ClassVar[OUTWARD_JOB_SORT_KEY]
    OUTWARD_JOB_SORT_KEY_APPROVED_BY: _ClassVar[OUTWARD_JOB_SORT_KEY]
    OUTWARD_JOB_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[OUTWARD_JOB_SORT_KEY]
    OUTWARD_JOB_SORT_KEY_COMPLETED_ON: _ClassVar[OUTWARD_JOB_SORT_KEY]
    OUTWARD_JOB_SORT_KEY_REFERENCE_ID: _ClassVar[OUTWARD_JOB_SORT_KEY]
    OUTWARD_JOB_SORT_KEY_FINAL_REF_NUMBER: _ClassVar[OUTWARD_JOB_SORT_KEY]
    OUTWARD_JOB_SORT_KEY_CONSIGNEE_LOCATION_ID: _ClassVar[OUTWARD_JOB_SORT_KEY]
    OUTWARD_JOB_SORT_KEY_VENDOR_ID: _ClassVar[OUTWARD_JOB_SORT_KEY]
    OUTWARD_JOB_SORT_KEY_PROJECT_ID: _ClassVar[OUTWARD_JOB_SORT_KEY]

class OUTWARD_JOB_INWARD_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OUTWARD_JOB_INWARD_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[OUTWARD_JOB_INWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_INWARD_ITEM_SORT_KEY_CREATED_AT: _ClassVar[OUTWARD_JOB_INWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_INWARD_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[OUTWARD_JOB_INWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_INWARD_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[OUTWARD_JOB_INWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_INWARD_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[OUTWARD_JOB_INWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_INWARD_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[OUTWARD_JOB_INWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_INWARD_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[OUTWARD_JOB_INWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_INWARD_ITEM_SORT_KEY_INTERNAL_QUANTITY: _ClassVar[OUTWARD_JOB_INWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_INWARD_ITEM_SORT_KEY_DELIVERY_DATE: _ClassVar[OUTWARD_JOB_INWARD_ITEM_SORT_KEY]

class OUTWARD_JOB_INWARD_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OUTWARD_JOB_INWARD_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[OUTWARD_JOB_INWARD_ITEM_STATUS]
    OUTWARD_JOB_INWARD_ITEM_STATUS_APPROVED: _ClassVar[OUTWARD_JOB_INWARD_ITEM_STATUS]
    OUTWARD_JOB_INWARD_ITEM_STATUS_UNAPPROVED: _ClassVar[OUTWARD_JOB_INWARD_ITEM_STATUS]

class OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_ID_UNSPECIFIED: _ClassVar[OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_CREATED_AT: _ClassVar[OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_MODIFIED_AT: _ClassVar[OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_APPROVED_ON: _ClassVar[OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_APPROVED_BY: _ClassVar[OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_APPROVER_ROLE_ID: _ClassVar[OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_FAMILY_ID: _ClassVar[OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY]
    OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_INTERNAL_QUANTITY: _ClassVar[OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY]

class OUTWARD_JOB_OUTWARD_ITEM_STATUS(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    OUTWARD_JOB_OUTWARD_ITEM_STATUS_ANY_UNSPECIFIED: _ClassVar[OUTWARD_JOB_OUTWARD_ITEM_STATUS]
    OUTWARD_JOB_OUTWARD_ITEM_STATUS_APPROVED: _ClassVar[OUTWARD_JOB_OUTWARD_ITEM_STATUS]
    OUTWARD_JOB_OUTWARD_ITEM_STATUS_UNAPPROVED: _ClassVar[OUTWARD_JOB_OUTWARD_ITEM_STATUS]
OUTWARD_JOB_SORT_KEY_ID_UNSPECIFIED: OUTWARD_JOB_SORT_KEY
OUTWARD_JOB_SORT_KEY_CREATED_AT: OUTWARD_JOB_SORT_KEY
OUTWARD_JOB_SORT_KEY_MODIFIED_AT: OUTWARD_JOB_SORT_KEY
OUTWARD_JOB_SORT_KEY_APPROVED_ON: OUTWARD_JOB_SORT_KEY
OUTWARD_JOB_SORT_KEY_APPROVED_BY: OUTWARD_JOB_SORT_KEY
OUTWARD_JOB_SORT_KEY_APPROVER_ROLE_ID: OUTWARD_JOB_SORT_KEY
OUTWARD_JOB_SORT_KEY_COMPLETED_ON: OUTWARD_JOB_SORT_KEY
OUTWARD_JOB_SORT_KEY_REFERENCE_ID: OUTWARD_JOB_SORT_KEY
OUTWARD_JOB_SORT_KEY_FINAL_REF_NUMBER: OUTWARD_JOB_SORT_KEY
OUTWARD_JOB_SORT_KEY_CONSIGNEE_LOCATION_ID: OUTWARD_JOB_SORT_KEY
OUTWARD_JOB_SORT_KEY_VENDOR_ID: OUTWARD_JOB_SORT_KEY
OUTWARD_JOB_SORT_KEY_PROJECT_ID: OUTWARD_JOB_SORT_KEY
OUTWARD_JOB_INWARD_ITEM_SORT_KEY_ID_UNSPECIFIED: OUTWARD_JOB_INWARD_ITEM_SORT_KEY
OUTWARD_JOB_INWARD_ITEM_SORT_KEY_CREATED_AT: OUTWARD_JOB_INWARD_ITEM_SORT_KEY
OUTWARD_JOB_INWARD_ITEM_SORT_KEY_MODIFIED_AT: OUTWARD_JOB_INWARD_ITEM_SORT_KEY
OUTWARD_JOB_INWARD_ITEM_SORT_KEY_APPROVED_ON: OUTWARD_JOB_INWARD_ITEM_SORT_KEY
OUTWARD_JOB_INWARD_ITEM_SORT_KEY_APPROVED_BY: OUTWARD_JOB_INWARD_ITEM_SORT_KEY
OUTWARD_JOB_INWARD_ITEM_SORT_KEY_APPROVER_ROLE_ID: OUTWARD_JOB_INWARD_ITEM_SORT_KEY
OUTWARD_JOB_INWARD_ITEM_SORT_KEY_FAMILY_ID: OUTWARD_JOB_INWARD_ITEM_SORT_KEY
OUTWARD_JOB_INWARD_ITEM_SORT_KEY_INTERNAL_QUANTITY: OUTWARD_JOB_INWARD_ITEM_SORT_KEY
OUTWARD_JOB_INWARD_ITEM_SORT_KEY_DELIVERY_DATE: OUTWARD_JOB_INWARD_ITEM_SORT_KEY
OUTWARD_JOB_INWARD_ITEM_STATUS_ANY_UNSPECIFIED: OUTWARD_JOB_INWARD_ITEM_STATUS
OUTWARD_JOB_INWARD_ITEM_STATUS_APPROVED: OUTWARD_JOB_INWARD_ITEM_STATUS
OUTWARD_JOB_INWARD_ITEM_STATUS_UNAPPROVED: OUTWARD_JOB_INWARD_ITEM_STATUS
OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_ID_UNSPECIFIED: OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY
OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_CREATED_AT: OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY
OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_MODIFIED_AT: OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY
OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_APPROVED_ON: OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY
OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_APPROVED_BY: OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY
OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_APPROVER_ROLE_ID: OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY
OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_FAMILY_ID: OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY
OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY_INTERNAL_QUANTITY: OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY
OUTWARD_JOB_OUTWARD_ITEM_STATUS_ANY_UNSPECIFIED: OUTWARD_JOB_OUTWARD_ITEM_STATUS
OUTWARD_JOB_OUTWARD_ITEM_STATUS_APPROVED: OUTWARD_JOB_OUTWARD_ITEM_STATUS
OUTWARD_JOB_OUTWARD_ITEM_STATUS_UNAPPROVED: OUTWARD_JOB_OUTWARD_ITEM_STATUS

class OutwardJobsServiceCreateRequest(_message.Message):
    __slots__ = ("entity_uuid", "user_comment", "vault_folder_id", "reference_id", "consignee_location_id", "vendor_id", "project_id", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    user_comment: str
    vault_folder_id: int
    reference_id: str
    consignee_location_id: int
    vendor_id: int
    project_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, entity_uuid: _Optional[str] = ..., user_comment: _Optional[str] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., project_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class OutwardJobsServiceUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "notify_users", "vault_folder_id", "reference_id", "project_id", "form_data")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NOTIFY_USERS_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    notify_users: bool
    vault_folder_id: int
    reference_id: str
    project_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumCreateRequest]
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., notify_users: _Optional[bool] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., project_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumCreateRequest, _Mapping]]] = ...) -> None: ...

class OutwardJobsServiceAutofillRequest(_message.Message):
    __slots__ = ("user_comment", "uuid")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    UUID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    uuid: str
    def __init__(self, user_comment: _Optional[str] = ..., uuid: _Optional[str] = ...) -> None: ...

class OutwardJobAncillaryParameters(_message.Message):
    __slots__ = ("consignee_location_uuid", "vendor_uuid")
    CONSIGNEE_LOCATION_UUID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_UUID_FIELD_NUMBER: _ClassVar[int]
    consignee_location_uuid: str
    vendor_uuid: str
    def __init__(self, consignee_location_uuid: _Optional[str] = ..., vendor_uuid: _Optional[str] = ...) -> None: ...

class OutwardJob(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "status", "logs", "completed_on", "vault_folder_id", "reference_id", "final_ref_number", "consignee_location_id", "vendor_id", "project_id", "inward_items_list", "outward_items_list", "form_data")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ON_FIELD_NUMBER: _ClassVar[int]
    VAULT_FOLDER_ID_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    INWARD_ITEMS_LIST_FIELD_NUMBER: _ClassVar[int]
    OUTWARD_ITEMS_LIST_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    logs: _containers.RepeatedCompositeFieldContainer[_scailo_pb2.LogbookLogConciseSLC]
    completed_on: int
    vault_folder_id: int
    reference_id: str
    final_ref_number: str
    consignee_location_id: int
    vendor_id: int
    project_id: int
    inward_items_list: _containers.RepeatedCompositeFieldContainer[OutwardJobInwardItem]
    outward_items_list: _containers.RepeatedCompositeFieldContainer[OutwardJobOutwardItem]
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatum]
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., logs: _Optional[_Iterable[_Union[_scailo_pb2.LogbookLogConciseSLC, _Mapping]]] = ..., completed_on: _Optional[int] = ..., vault_folder_id: _Optional[int] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., project_id: _Optional[int] = ..., inward_items_list: _Optional[_Iterable[_Union[OutwardJobInwardItem, _Mapping]]] = ..., outward_items_list: _Optional[_Iterable[_Union[OutwardJobOutwardItem, _Mapping]]] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatum, _Mapping]]] = ...) -> None: ...

class OutwardJobsServiceInwardItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "outward_job_id", "family_id", "internal_quantity", "delivery_date", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    outward_job_id: int
    family_id: int
    internal_quantity: int
    delivery_date: str
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., outward_job_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ...) -> None: ...

class OutwardJobsServiceMultipleInwardItemsSingleton(_message.Message):
    __slots__ = ("family_id", "internal_quantity", "delivery_date", "specifications")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    internal_quantity: int
    delivery_date: str
    specifications: str
    def __init__(self, family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ...) -> None: ...

class OutwardJobsServiceMultipleInwardItemsCreateRequest(_message.Message):
    __slots__ = ("user_comment", "outward_job_id", "list")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    outward_job_id: int
    list: _containers.RepeatedCompositeFieldContainer[OutwardJobsServiceMultipleInwardItemsSingleton]
    def __init__(self, user_comment: _Optional[str] = ..., outward_job_id: _Optional[int] = ..., list: _Optional[_Iterable[_Union[OutwardJobsServiceMultipleInwardItemsSingleton, _Mapping]]] = ...) -> None: ...

class OutwardJobsServiceInwardItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "internal_quantity", "delivery_date", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    internal_quantity: int
    delivery_date: str
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ...) -> None: ...

class OutwardJobInwardItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "outward_job_id", "family_id", "internal_quantity", "delivery_date", "specifications", "outward_job_uuid", "family_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    OUTWARD_JOB_UUID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    outward_job_id: int
    family_id: int
    internal_quantity: int
    delivery_date: str
    specifications: str
    outward_job_uuid: str
    family_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., outward_job_id: _Optional[int] = ..., family_id: _Optional[int] = ..., internal_quantity: _Optional[int] = ..., delivery_date: _Optional[str] = ..., specifications: _Optional[str] = ..., outward_job_uuid: _Optional[str] = ..., family_uuid: _Optional[str] = ...) -> None: ...

class OutwardJobsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[OutwardJob]
    def __init__(self, list: _Optional[_Iterable[_Union[OutwardJob, _Mapping]]] = ...) -> None: ...

class OutwardJobsInwardItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[OutwardJobInwardItem]
    def __init__(self, list: _Optional[_Iterable[_Union[OutwardJobInwardItem, _Mapping]]] = ...) -> None: ...

class OutwardJobInwardItemHistoryRequest(_message.Message):
    __slots__ = ("outward_job_id", "family_id")
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    outward_job_id: int
    family_id: int
    def __init__(self, outward_job_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class OutwardJobInwardItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("outward_job_id", "family_id")
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    outward_job_id: int
    family_id: int
    def __init__(self, outward_job_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class OutwardJobsServicePaginationReq(_message.Message):
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
    sort_key: OUTWARD_JOB_SORT_KEY
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[OUTWARD_JOB_SORT_KEY, str]] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ...) -> None: ...

class OutwardJobsServicePaginationResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[OutwardJob]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[OutwardJob, _Mapping]]] = ...) -> None: ...

class OutwardJobsServiceFilterReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "reference_id", "final_ref_number", "consignee_location_id", "vendor_id", "project_id", "inward_family_id", "form_data")
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
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    INWARD_FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    FORM_DATA_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: OUTWARD_JOB_SORT_KEY
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
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    reference_id: str
    final_ref_number: str
    consignee_location_id: int
    vendor_id: int
    project_id: int
    inward_family_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[OUTWARD_JOB_SORT_KEY, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., project_id: _Optional[int] = ..., inward_family_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class OutwardJobsServiceCountReq(_message.Message):
    __slots__ = ("is_active", "creation_timestamp_start", "creation_timestamp_end", "modification_timestamp_start", "modification_timestamp_end", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "completed_on_start", "completed_on_end", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "reference_id", "final_ref_number", "consignee_location_id", "vendor_id", "project_id", "inward_family_id", "form_data")
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
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
    REFERENCE_ID_FIELD_NUMBER: _ClassVar[int]
    FINAL_REF_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    INWARD_FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
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
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    reference_id: str
    final_ref_number: str
    consignee_location_id: int
    vendor_id: int
    project_id: int
    inward_family_id: int
    form_data: _containers.RepeatedCompositeFieldContainer[_scailo_pb2_1_1.FormFieldDatumFilterRequest]
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., creation_timestamp_start: _Optional[int] = ..., creation_timestamp_end: _Optional[int] = ..., modification_timestamp_start: _Optional[int] = ..., modification_timestamp_end: _Optional[int] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., completed_on_start: _Optional[int] = ..., completed_on_end: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., reference_id: _Optional[str] = ..., final_ref_number: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., project_id: _Optional[int] = ..., inward_family_id: _Optional[int] = ..., form_data: _Optional[_Iterable[_Union[_scailo_pb2_1_1.FormFieldDatumFilterRequest, _Mapping]]] = ...) -> None: ...

class OutwardJobsServiceSearchAllReq(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "search_key", "consignee_location_id", "vendor_id", "project_id")
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    SORT_ORDER_FIELD_NUMBER: _ClassVar[int]
    SORT_KEY_FIELD_NUMBER: _ClassVar[int]
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    CONSIGNEE_LOCATION_ID_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: OUTWARD_JOB_SORT_KEY
    entity_uuid: str
    status: _scailo_pb2.STANDARD_LIFECYCLE_STATUS
    search_key: str
    consignee_location_id: int
    vendor_id: int
    project_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[OUTWARD_JOB_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[_scailo_pb2.STANDARD_LIFECYCLE_STATUS, str]] = ..., search_key: _Optional[str] = ..., consignee_location_id: _Optional[int] = ..., vendor_id: _Optional[int] = ..., project_id: _Optional[int] = ...) -> None: ...

class OutwardJobInwardItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "outward_job_id", "family_id", "delivery_date_exact", "delivery_date_start", "delivery_date_end", "search_key", "vendor_id")
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
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_EXACT_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_START_FIELD_NUMBER: _ClassVar[int]
    DELIVERY_DATE_END_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: OUTWARD_JOB_INWARD_ITEM_SORT_KEY
    entity_uuid: str
    status: OUTWARD_JOB_INWARD_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    outward_job_id: int
    family_id: int
    delivery_date_exact: str
    delivery_date_start: str
    delivery_date_end: str
    search_key: str
    vendor_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[OUTWARD_JOB_INWARD_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[OUTWARD_JOB_INWARD_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., outward_job_id: _Optional[int] = ..., family_id: _Optional[int] = ..., delivery_date_exact: _Optional[str] = ..., delivery_date_start: _Optional[str] = ..., delivery_date_end: _Optional[str] = ..., search_key: _Optional[str] = ..., vendor_id: _Optional[int] = ...) -> None: ...

class OutwardJobsServicePaginatedInwardItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[OutwardJobInwardItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[OutwardJobInwardItem, _Mapping]]] = ...) -> None: ...

class OutwardJobsServiceOutwardItemCreateRequest(_message.Message):
    __slots__ = ("user_comment", "outward_job_id", "family_id", "item_hash", "internal_quantity", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    outward_job_id: int
    family_id: int
    item_hash: str
    internal_quantity: int
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., outward_job_id: _Optional[int] = ..., family_id: _Optional[int] = ..., item_hash: _Optional[str] = ..., internal_quantity: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class OutwardJobsServiceMultipleOutwardItemsSingleton(_message.Message):
    __slots__ = ("family_id", "item_hash", "internal_quantity", "specifications")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    item_hash: str
    internal_quantity: int
    specifications: str
    def __init__(self, family_id: _Optional[int] = ..., item_hash: _Optional[str] = ..., internal_quantity: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class OutwardJobsServiceMultipleOutwardItemsCreateRequest(_message.Message):
    __slots__ = ("user_comment", "outward_job_id", "list")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    LIST_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    outward_job_id: int
    list: _containers.RepeatedCompositeFieldContainer[OutwardJobsServiceMultipleOutwardItemsSingleton]
    def __init__(self, user_comment: _Optional[str] = ..., outward_job_id: _Optional[int] = ..., list: _Optional[_Iterable[_Union[OutwardJobsServiceMultipleOutwardItemsSingleton, _Mapping]]] = ...) -> None: ...

class OutwardJobsServiceOutwardItemUpdateRequest(_message.Message):
    __slots__ = ("user_comment", "id", "item_hash", "internal_quantity", "specifications")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    id: int
    item_hash: str
    internal_quantity: int
    specifications: str
    def __init__(self, user_comment: _Optional[str] = ..., id: _Optional[int] = ..., item_hash: _Optional[str] = ..., internal_quantity: _Optional[int] = ..., specifications: _Optional[str] = ...) -> None: ...

class OutwardJobOutwardItem(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "outward_job_id", "family_id", "item_hash", "internal_quantity", "specifications", "outward_job_uuid", "family_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    SPECIFICATIONS_FIELD_NUMBER: _ClassVar[int]
    OUTWARD_JOB_UUID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    outward_job_id: int
    family_id: int
    item_hash: str
    internal_quantity: int
    specifications: str
    outward_job_uuid: str
    family_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., outward_job_id: _Optional[int] = ..., family_id: _Optional[int] = ..., item_hash: _Optional[str] = ..., internal_quantity: _Optional[int] = ..., specifications: _Optional[str] = ..., outward_job_uuid: _Optional[str] = ..., family_uuid: _Optional[str] = ...) -> None: ...

class OutwardJobsOutwardItemsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[OutwardJobOutwardItem]
    def __init__(self, list: _Optional[_Iterable[_Union[OutwardJobOutwardItem, _Mapping]]] = ...) -> None: ...

class OutwardJobOutwardItemHistoryRequest(_message.Message):
    __slots__ = ("outward_job_id", "family_id")
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    outward_job_id: int
    family_id: int
    def __init__(self, outward_job_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class OutwardJobOutwardItemProspectiveInfoRequest(_message.Message):
    __slots__ = ("outward_job_id", "family_id")
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    outward_job_id: int
    family_id: int
    def __init__(self, outward_job_id: _Optional[int] = ..., family_id: _Optional[int] = ...) -> None: ...

class OutwardJobOutwardItemsSearchRequest(_message.Message):
    __slots__ = ("is_active", "count", "offset", "sort_order", "sort_key", "entity_uuid", "status", "approved_on_start", "approved_on_end", "approved_by_user_id", "approver_role_id", "outward_job_id", "family_id", "item_hash", "search_key", "vendor_id")
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
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    ITEM_HASH_FIELD_NUMBER: _ClassVar[int]
    SEARCH_KEY_FIELD_NUMBER: _ClassVar[int]
    VENDOR_ID_FIELD_NUMBER: _ClassVar[int]
    is_active: _scailo_pb2.BOOL_FILTER
    count: int
    offset: int
    sort_order: _scailo_pb2.SORT_ORDER
    sort_key: OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY
    entity_uuid: str
    status: OUTWARD_JOB_OUTWARD_ITEM_STATUS
    approved_on_start: int
    approved_on_end: int
    approved_by_user_id: int
    approver_role_id: int
    outward_job_id: int
    family_id: int
    item_hash: str
    search_key: str
    vendor_id: int
    def __init__(self, is_active: _Optional[_Union[_scailo_pb2.BOOL_FILTER, str]] = ..., count: _Optional[int] = ..., offset: _Optional[int] = ..., sort_order: _Optional[_Union[_scailo_pb2.SORT_ORDER, str]] = ..., sort_key: _Optional[_Union[OUTWARD_JOB_OUTWARD_ITEM_SORT_KEY, str]] = ..., entity_uuid: _Optional[str] = ..., status: _Optional[_Union[OUTWARD_JOB_OUTWARD_ITEM_STATUS, str]] = ..., approved_on_start: _Optional[int] = ..., approved_on_end: _Optional[int] = ..., approved_by_user_id: _Optional[int] = ..., approver_role_id: _Optional[int] = ..., outward_job_id: _Optional[int] = ..., family_id: _Optional[int] = ..., item_hash: _Optional[str] = ..., search_key: _Optional[str] = ..., vendor_id: _Optional[int] = ...) -> None: ...

class OutwardJobsServicePaginatedOutwardItemsResponse(_message.Message):
    __slots__ = ("count", "offset", "total", "payload")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_FIELD_NUMBER: _ClassVar[int]
    count: int
    offset: int
    total: int
    payload: _containers.RepeatedCompositeFieldContainer[OutwardJobOutwardItem]
    def __init__(self, count: _Optional[int] = ..., offset: _Optional[int] = ..., total: _Optional[int] = ..., payload: _Optional[_Iterable[_Union[OutwardJobOutwardItem, _Mapping]]] = ...) -> None: ...

class OutwardJobsServiceContactCreateRequest(_message.Message):
    __slots__ = ("user_comment", "outward_job_id", "associate_id")
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    user_comment: str
    outward_job_id: int
    associate_id: int
    def __init__(self, user_comment: _Optional[str] = ..., outward_job_id: _Optional[int] = ..., associate_id: _Optional[int] = ...) -> None: ...

class OutwardJobContact(_message.Message):
    __slots__ = ("entity_uuid", "metadata", "approval_metadata", "need_approval", "user_comment", "outward_job_id", "associate_id", "associate_uuid")
    ENTITY_UUID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    APPROVAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    NEED_APPROVAL_FIELD_NUMBER: _ClassVar[int]
    USER_COMMENT_FIELD_NUMBER: _ClassVar[int]
    OUTWARD_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_ID_FIELD_NUMBER: _ClassVar[int]
    ASSOCIATE_UUID_FIELD_NUMBER: _ClassVar[int]
    entity_uuid: str
    metadata: _scailo_pb2.EmployeeMetadata
    approval_metadata: _scailo_pb2.ApprovalMetadata
    need_approval: bool
    user_comment: str
    outward_job_id: int
    associate_id: int
    associate_uuid: str
    def __init__(self, entity_uuid: _Optional[str] = ..., metadata: _Optional[_Union[_scailo_pb2.EmployeeMetadata, _Mapping]] = ..., approval_metadata: _Optional[_Union[_scailo_pb2.ApprovalMetadata, _Mapping]] = ..., need_approval: _Optional[bool] = ..., user_comment: _Optional[str] = ..., outward_job_id: _Optional[int] = ..., associate_id: _Optional[int] = ..., associate_uuid: _Optional[str] = ...) -> None: ...

class OutwardJobContactsList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[OutwardJobContact]
    def __init__(self, list: _Optional[_Iterable[_Union[OutwardJobContact, _Mapping]]] = ...) -> None: ...

class OutwardJobInwardInventoryMatch(_message.Message):
    __slots__ = ("family_id", "job_qty_primary", "ordered_qty_primary", "received_qty_primary", "returned_qty_primary")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_QTY_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    ORDERED_QTY_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    RECEIVED_QTY_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    RETURNED_QTY_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    job_qty_primary: int
    ordered_qty_primary: int
    received_qty_primary: int
    returned_qty_primary: int
    def __init__(self, family_id: _Optional[int] = ..., job_qty_primary: _Optional[int] = ..., ordered_qty_primary: _Optional[int] = ..., received_qty_primary: _Optional[int] = ..., returned_qty_primary: _Optional[int] = ...) -> None: ...

class OutwardJobInwardInventoryMatchList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[OutwardJobInwardInventoryMatch]
    def __init__(self, list: _Optional[_Iterable[_Union[OutwardJobInwardInventoryMatch, _Mapping]]] = ...) -> None: ...

class OutwardJobOutwardInventoryMatch(_message.Message):
    __slots__ = ("family_id", "job_qty_primary", "issued_qty_primary", "returned_qty_primary")
    FAMILY_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_QTY_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    ISSUED_QTY_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    RETURNED_QTY_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    family_id: int
    job_qty_primary: int
    issued_qty_primary: int
    returned_qty_primary: int
    def __init__(self, family_id: _Optional[int] = ..., job_qty_primary: _Optional[int] = ..., issued_qty_primary: _Optional[int] = ..., returned_qty_primary: _Optional[int] = ...) -> None: ...

class OutwardJobOutwardInventoryMatchList(_message.Message):
    __slots__ = ("list",)
    LIST_FIELD_NUMBER: _ClassVar[int]
    list: _containers.RepeatedCompositeFieldContainer[OutwardJobOutwardInventoryMatch]
    def __init__(self, list: _Optional[_Iterable[_Union[OutwardJobOutwardInventoryMatch, _Mapping]]] = ...) -> None: ...
