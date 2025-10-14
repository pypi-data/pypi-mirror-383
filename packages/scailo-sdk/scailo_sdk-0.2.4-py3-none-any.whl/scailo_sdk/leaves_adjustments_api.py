# Generated Connect client code

from __future__ import annotations
from collections.abc import AsyncIterator
from collections.abc import Iterator
from collections.abc import Iterable
import aiohttp
import urllib3
import typing
import sys

from connectrpc.client_async import AsyncConnectClient
from connectrpc.client_sync import ConnectClient
from connectrpc.client_protocol import ConnectProtocol
from connectrpc.client_connect import ConnectProtocolError
from connectrpc.headers import HeaderInput
from connectrpc.server import ClientRequest
from connectrpc.server import ClientStream
from connectrpc.server import ServerResponse
from connectrpc.server import ServerStream
from connectrpc.server_sync import ConnectWSGI
from connectrpc.streams import StreamInput
from connectrpc.streams import AsyncStreamOutput
from connectrpc.streams import StreamOutput
from connectrpc.unary import UnaryOutput
from connectrpc.unary import ClientStreamingOutput

if typing.TYPE_CHECKING:
    # wsgiref.types was added in Python 3.11.
    if sys.version_info >= (3, 11):
        from wsgiref.types import WSGIApplication
    else:
        from _typeshed.wsgi import WSGIApplication

from scailo_sdk import base, leaves_adjustments

class LeavesAdjustmentsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def create(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_create(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_draft(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Draft"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_draft(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_draft_update(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/DraftUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft_update(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_draft_update(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_send_for_verification(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call SendForVerification, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/SendForVerification"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def send_for_verification(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_send_for_verification(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_verify(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Verify, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Verify"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def verify(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_verify(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Approve, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Approve"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_send_for_revision(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call SendForRevision, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/SendForRevision"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def send_for_revision(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_send_for_revision(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_revision_update(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/RevisionUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def revision_update(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_revision_update(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_halt(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Halt, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Halt"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def halt(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_halt(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_discard(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Discard, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Discard"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def discard(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_discard(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_restore(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Restore, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Restore"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def restore(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_restore(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_complete(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Complete, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Complete"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def complete(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_complete(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_repeat(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Repeat, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Repeat"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def repeat(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_repeat(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_comment_add(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call CommentAdd, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/CommentAdd"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def comment_add(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_comment_add(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_leave_adjustment_record(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceRecordCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddLeaveAdjustmentRecord, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/AddLeaveAdjustmentRecord"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_leave_adjustment_record(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceRecordCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_leave_adjustment_record(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_leave_adjustment_record(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceRecordUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyLeaveAdjustmentRecord, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ModifyLeaveAdjustmentRecord"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_leave_adjustment_record(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceRecordUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_leave_adjustment_record(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_leave_adjustment_record(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveLeaveAdjustmentRecord, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ApproveLeaveAdjustmentRecord"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_leave_adjustment_record(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_leave_adjustment_record(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_leave_adjustment_record(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteLeaveAdjustmentRecord, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/DeleteLeaveAdjustmentRecord"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_leave_adjustment_record(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_leave_adjustment_record(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_leave_adjustment_records(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderLeaveAdjustmentRecords, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ReorderLeaveAdjustmentRecords"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_leave_adjustment_records(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_leave_adjustment_records(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_leave_adjustment_record_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeaveAdjustmentRecord]:
        """Low-level method to call ViewLeaveAdjustmentRecordByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewLeaveAdjustmentRecordByID"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeaveAdjustmentRecord,extra_headers, timeout_seconds)


    def view_leave_adjustment_record_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeaveAdjustmentRecord:
        response = self.call_view_leave_adjustment_record_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_approved_leave_adjustment_records(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList]:
        """Low-level method to call ViewApprovedLeaveAdjustmentRecords, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewApprovedLeaveAdjustmentRecords"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList,extra_headers, timeout_seconds)


    def view_approved_leave_adjustment_records(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList:
        response = self.call_view_approved_leave_adjustment_records(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_unapproved_leave_adjustment_records(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList]:
        """Low-level method to call ViewUnapprovedLeaveAdjustmentRecords, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewUnapprovedLeaveAdjustmentRecords"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList,extra_headers, timeout_seconds)


    def view_unapproved_leave_adjustment_records(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList:
        response = self.call_view_unapproved_leave_adjustment_records(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_leave_adjustment_record_history(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList]:
        """Low-level method to call ViewLeaveAdjustmentRecordHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewLeaveAdjustmentRecordHistory"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList,extra_headers, timeout_seconds)


    def view_leave_adjustment_record_history(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList:
        response = self.call_view_leave_adjustment_record_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_approved_leave_adjustment_records(
        self, req: leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse]:
        """Low-level method to call ViewPaginatedApprovedLeaveAdjustmentRecords, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewPaginatedApprovedLeaveAdjustmentRecords"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse,extra_headers, timeout_seconds)


    def view_paginated_approved_leave_adjustment_records(
        self, req: leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse:
        response = self.call_view_paginated_approved_leave_adjustment_records(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_unapproved_leave_adjustment_records(
        self, req: leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedLeaveAdjustmentRecords, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewPaginatedUnapprovedLeaveAdjustmentRecords"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse,extra_headers, timeout_seconds)


    def view_paginated_unapproved_leave_adjustment_records(
        self, req: leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse:
        response = self.call_view_paginated_unapproved_leave_adjustment_records(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_records_with_pagination(
        self, req: leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse]:
        """Low-level method to call SearchRecordsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/SearchRecordsWithPagination"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse,extra_headers, timeout_seconds)


    def search_records_with_pagination(
        self, req: leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse:
        response = self.call_search_records_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeaveAdjustment]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewByID"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeaveAdjustment,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeaveAdjustment:
        response = self.call_view_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeaveAdjustment]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewByUUID"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeaveAdjustment,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeaveAdjustment:
        response = self.call_view_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeaveAdjustment]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeaveAdjustment,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeaveAdjustment:
        response = self.call_view_essential_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeaveAdjustment]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeaveAdjustment,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeaveAdjustment:
        response = self.call_view_essential_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsList:
        response = self.call_view_from_i_ds(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewAll"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsList:
        response = self.call_view_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginationResponse:
        response = self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_all(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/SearchAll"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsList,extra_headers, timeout_seconds)


    def search_all(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Filter"
        return self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsList,extra_headers, timeout_seconds)


    def filter(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsList:
        response = self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_count_in_status(
        self, req: base.scailo_pb2.CountInSLCStatusRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call CountInStatus, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/CountInStatus"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count_in_status(
        self, req: base.scailo_pb2.CountInSLCStatusRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = self.call_count_in_status(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_count(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = self.call_count(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_download_as_csv(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncLeavesAdjustmentsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def create(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_create(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_draft(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Draft"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_draft(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_draft_update(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/DraftUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft_update(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_draft_update(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_send_for_verification(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call SendForVerification, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/SendForVerification"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def send_for_verification(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_send_for_verification(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_verify(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Verify, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Verify"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def verify(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_verify(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Approve, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Approve"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_send_for_revision(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call SendForRevision, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/SendForRevision"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def send_for_revision(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_send_for_revision(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_revision_update(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/RevisionUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def revision_update(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_revision_update(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_halt(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Halt, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Halt"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def halt(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_halt(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_discard(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Discard, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Discard"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def discard(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_discard(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_restore(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Restore, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Restore"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def restore(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_restore(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_complete(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Complete, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Complete"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def complete(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_complete(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_repeat(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Repeat, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Repeat"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def repeat(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_repeat(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_comment_add(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call CommentAdd, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/CommentAdd"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def comment_add(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_comment_add(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_leave_adjustment_record(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceRecordCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddLeaveAdjustmentRecord, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/AddLeaveAdjustmentRecord"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_leave_adjustment_record(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceRecordCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_leave_adjustment_record(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_leave_adjustment_record(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceRecordUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyLeaveAdjustmentRecord, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ModifyLeaveAdjustmentRecord"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_leave_adjustment_record(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceRecordUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_leave_adjustment_record(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_leave_adjustment_record(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveLeaveAdjustmentRecord, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ApproveLeaveAdjustmentRecord"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_leave_adjustment_record(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_leave_adjustment_record(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_leave_adjustment_record(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteLeaveAdjustmentRecord, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/DeleteLeaveAdjustmentRecord"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_leave_adjustment_record(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_leave_adjustment_record(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_leave_adjustment_records(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderLeaveAdjustmentRecords, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ReorderLeaveAdjustmentRecords"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_leave_adjustment_records(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_leave_adjustment_records(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_leave_adjustment_record_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeaveAdjustmentRecord]:
        """Low-level method to call ViewLeaveAdjustmentRecordByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewLeaveAdjustmentRecordByID"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeaveAdjustmentRecord,extra_headers, timeout_seconds)

    async def view_leave_adjustment_record_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeaveAdjustmentRecord:
        response = await self.call_view_leave_adjustment_record_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_approved_leave_adjustment_records(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList]:
        """Low-level method to call ViewApprovedLeaveAdjustmentRecords, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewApprovedLeaveAdjustmentRecords"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList,extra_headers, timeout_seconds)

    async def view_approved_leave_adjustment_records(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList:
        response = await self.call_view_approved_leave_adjustment_records(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_unapproved_leave_adjustment_records(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList]:
        """Low-level method to call ViewUnapprovedLeaveAdjustmentRecords, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewUnapprovedLeaveAdjustmentRecords"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList,extra_headers, timeout_seconds)

    async def view_unapproved_leave_adjustment_records(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList:
        response = await self.call_view_unapproved_leave_adjustment_records(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_leave_adjustment_record_history(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList]:
        """Low-level method to call ViewLeaveAdjustmentRecordHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewLeaveAdjustmentRecordHistory"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList,extra_headers, timeout_seconds)

    async def view_leave_adjustment_record_history(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList:
        response = await self.call_view_leave_adjustment_record_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_approved_leave_adjustment_records(
        self, req: leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse]:
        """Low-level method to call ViewPaginatedApprovedLeaveAdjustmentRecords, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewPaginatedApprovedLeaveAdjustmentRecords"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse,extra_headers, timeout_seconds)

    async def view_paginated_approved_leave_adjustment_records(
        self, req: leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse:
        response = await self.call_view_paginated_approved_leave_adjustment_records(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_unapproved_leave_adjustment_records(
        self, req: leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedLeaveAdjustmentRecords, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewPaginatedUnapprovedLeaveAdjustmentRecords"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse,extra_headers, timeout_seconds)

    async def view_paginated_unapproved_leave_adjustment_records(
        self, req: leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse:
        response = await self.call_view_paginated_unapproved_leave_adjustment_records(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_records_with_pagination(
        self, req: leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse]:
        """Low-level method to call SearchRecordsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/SearchRecordsWithPagination"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse,extra_headers, timeout_seconds)

    async def search_records_with_pagination(
        self, req: leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse:
        response = await self.call_search_records_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeaveAdjustment]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewByID"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeaveAdjustment,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeaveAdjustment:
        response = await self.call_view_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeaveAdjustment]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeaveAdjustment,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeaveAdjustment:
        response = await self.call_view_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeaveAdjustment]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeaveAdjustment,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeaveAdjustment:
        response = await self.call_view_essential_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeaveAdjustment]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeaveAdjustment,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeaveAdjustment:
        response = await self.call_view_essential_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsList:
        response = await self.call_view_from_i_ds(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewAll"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsList:
        response = await self.call_view_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginationResponse:
        response = await self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_all(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/SearchAll"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Filter"
        return await self._connect_client.call_unary(url, req, leaves_adjustments.scailo_pb2.LeavesAdjustmentsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_adjustments.scailo_pb2.LeavesAdjustmentsList:
        response = await self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_count_in_status(
        self, req: base.scailo_pb2.CountInSLCStatusRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call CountInStatus, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/CountInStatus"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count_in_status(
        self, req: base.scailo_pb2.CountInSLCStatusRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = await self.call_count_in_status(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_count(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = await self.call_count(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_download_as_csv(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesAdjustmentsService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class LeavesAdjustmentsServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft_update(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_verification(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def verify(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_revision(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def revision_update(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def halt(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def discard(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def restore(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def complete(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def repeat(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def comment_add(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_leave_adjustment_record(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceRecordCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_leave_adjustment_record(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceRecordUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_leave_adjustment_record(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_leave_adjustment_record(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_leave_adjustment_records(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_leave_adjustment_record_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeaveAdjustmentRecord]:
        ...
    def view_approved_leave_adjustment_records(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList]:
        ...
    def view_unapproved_leave_adjustment_records(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList]:
        ...
    def view_leave_adjustment_record_history(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsHistoryRequest]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsList]:
        ...
    def view_paginated_approved_leave_adjustment_records(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse]:
        ...
    def view_paginated_unapproved_leave_adjustment_records(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse]:
        ...
    def search_records_with_pagination(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginatedRecordsResponse]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeaveAdjustment]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeaveAdjustment]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeaveAdjustment]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeaveAdjustment]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        ...
    def view_with_pagination(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginationReq]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginationResponse]:
        ...
    def search_all(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceSearchAllReq]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        ...
    def filter(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceFilterReq]) -> ServerResponse[leaves_adjustments.scailo_pb2.LeavesAdjustmentsList]:
        ...
    def count_in_status(self, req: ClientRequest[base.scailo_pb2.CountInSLCStatusRequest]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def count(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

LEAVES_ADJUSTMENTS_SERVICE_PATH_PREFIX = "/Scailo.LeavesAdjustmentsService"

def wsgi_leaves_adjustments_service(implementation: LeavesAdjustmentsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/Create", implementation.create, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/Draft", implementation.draft, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/DraftUpdate", implementation.draft_update, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/SendForVerification", implementation.send_for_verification, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/Verify", implementation.verify, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/Approve", implementation.approve, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/SendForRevision", implementation.send_for_revision, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/RevisionUpdate", implementation.revision_update, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/Halt", implementation.halt, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/Discard", implementation.discard, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/Restore", implementation.restore, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/Repeat", implementation.repeat, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/AddLeaveAdjustmentRecord", implementation.add_leave_adjustment_record, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceRecordCreateRequest)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ModifyLeaveAdjustmentRecord", implementation.modify_leave_adjustment_record, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceRecordUpdateRequest)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ApproveLeaveAdjustmentRecord", implementation.approve_leave_adjustment_record, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/DeleteLeaveAdjustmentRecord", implementation.delete_leave_adjustment_record, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ReorderLeaveAdjustmentRecords", implementation.reorder_leave_adjustment_records, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewLeaveAdjustmentRecordByID", implementation.view_leave_adjustment_record_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewApprovedLeaveAdjustmentRecords", implementation.view_approved_leave_adjustment_records, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewUnapprovedLeaveAdjustmentRecords", implementation.view_unapproved_leave_adjustment_records, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewLeaveAdjustmentRecordHistory", implementation.view_leave_adjustment_record_history, leaves_adjustments.scailo_pb2.LeavesAdjustmentsRecordsHistoryRequest)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewPaginatedApprovedLeaveAdjustmentRecords", implementation.view_paginated_approved_leave_adjustment_records, leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewPaginatedUnapprovedLeaveAdjustmentRecords", implementation.view_paginated_unapproved_leave_adjustment_records, leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/SearchRecordsWithPagination", implementation.search_records_with_pagination, leaves_adjustments.scailo_pb2.LeaveAdjustmentRecordsSearchRequest)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/ViewWithPagination", implementation.view_with_pagination, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServicePaginationReq)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/SearchAll", implementation.search_all, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/Filter", implementation.filter, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceFilterReq)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/CountInStatus", implementation.count_in_status, base.scailo_pb2.CountInSLCStatusRequest)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/Count", implementation.count, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceCountReq)
    app.register_unary_rpc("/Scailo.LeavesAdjustmentsService/DownloadAsCSV", implementation.download_as_csv, leaves_adjustments.scailo_pb2.LeavesAdjustmentsServiceFilterReq)
    return app
