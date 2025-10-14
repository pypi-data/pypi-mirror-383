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

from scailo_sdk import base, meetings

class MeetingsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: meetings.scailo_pb2.MeetingsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def create(
        self, req: meetings.scailo_pb2.MeetingsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_create(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_update(
        self, req: meetings.scailo_pb2.MeetingsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Update, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/Update"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def update(
        self, req: meetings.scailo_pb2.MeetingsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_update(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_cancel(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Cancel, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/Cancel"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def cancel(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_cancel(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.MeetingsService/Complete"
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
        url = self.base_url + "/Scailo.MeetingsService/Repeat"
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
        url = self.base_url + "/Scailo.MeetingsService/CommentAdd"
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

    def call_send_email(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call SendEmail, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/SendEmail"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def send_email(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_send_email(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_request_rsvp(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RequestRSVP, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/RequestRSVP"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def request_rsvp(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_request_rsvp(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_send_actionables(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call SendActionables, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/SendActionables"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def send_actionables(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_send_actionables(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_actionable(
        self, req: meetings.scailo_pb2.MeetingsServiceActionableCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddActionable, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/AddActionable"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_actionable(
        self, req: meetings.scailo_pb2.MeetingsServiceActionableCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_actionable(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_actionable(
        self, req: meetings.scailo_pb2.MeetingsServiceActionableUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyActionable, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ModifyActionable"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_actionable(
        self, req: meetings.scailo_pb2.MeetingsServiceActionableUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_actionable(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_actionable(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteActionable, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/DeleteActionable"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_actionable(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_actionable(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_actionables(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderActionables, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ReorderActionables"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_actionables(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_actionables(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_actionable_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingActionable]:
        """Low-level method to call ViewActionableByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewActionableByID"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingActionable,extra_headers, timeout_seconds)


    def view_actionable_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingActionable:
        response = self.call_view_actionable_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_actionables(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingActionablesList]:
        """Low-level method to call ViewActionables, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewActionables"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingActionablesList,extra_headers, timeout_seconds)


    def view_actionables(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingActionablesList:
        response = self.call_view_actionables(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_actionable_history(
        self, req: meetings.scailo_pb2.MeetingActionableHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingActionablesList]:
        """Low-level method to call ViewActionableHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewActionableHistory"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingActionablesList,extra_headers, timeout_seconds)


    def view_actionable_history(
        self, req: meetings.scailo_pb2.MeetingActionableHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingActionablesList:
        response = self.call_view_actionable_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_actionables(
        self, req: meetings.scailo_pb2.MeetingActionablesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse]:
        """Low-level method to call ViewPaginatedActionables, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewPaginatedActionables"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse,extra_headers, timeout_seconds)


    def view_paginated_actionables(
        self, req: meetings.scailo_pb2.MeetingActionablesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse:
        response = self.call_view_paginated_actionables(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_actionables_with_pagination(
        self, req: meetings.scailo_pb2.MeetingActionablesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse]:
        """Low-level method to call SearchActionablesWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/SearchActionablesWithPagination"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse,extra_headers, timeout_seconds)


    def search_actionables_with_pagination(
        self, req: meetings.scailo_pb2.MeetingActionablesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse:
        response = self.call_search_actionables_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_employee(
        self, req: meetings.scailo_pb2.MeetingsServiceEmployeeCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddEmployee, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/AddEmployee"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_employee(
        self, req: meetings.scailo_pb2.MeetingsServiceEmployeeCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_employee(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_employee(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteEmployee, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/DeleteEmployee"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_employee(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_employee(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_employee_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingEmployee]:
        """Low-level method to call ViewEmployeeByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewEmployeeByID"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingEmployee,extra_headers, timeout_seconds)


    def view_employee_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingEmployee:
        response = self.call_view_employee_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_employees(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingEmployeesList]:
        """Low-level method to call ViewEmployees, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewEmployees"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingEmployeesList,extra_headers, timeout_seconds)


    def view_employees(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingEmployeesList:
        response = self.call_view_employees(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_set_employee_rsvp(
        self, req: meetings.scailo_pb2.MeetingsServiceSetRSVPRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call SetEmployeeRSVP, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/SetEmployeeRSVP"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def set_employee_rsvp(
        self, req: meetings.scailo_pb2.MeetingsServiceSetRSVPRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_set_employee_rsvp(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_import_from_team(
        self, req: meetings.scailo_pb2.MeetingsServiceImportEmployeesRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportFromTeam, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ImportFromTeam"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def import_from_team(
        self, req: meetings.scailo_pb2.MeetingsServiceImportEmployeesRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_import_from_team(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_import_from_department(
        self, req: meetings.scailo_pb2.MeetingsServiceImportEmployeesRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportFromDepartment, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ImportFromDepartment"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def import_from_department(
        self, req: meetings.scailo_pb2.MeetingsServiceImportEmployeesRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_import_from_department(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_associate(
        self, req: meetings.scailo_pb2.MeetingsServiceAssociateCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddAssociate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/AddAssociate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_associate(
        self, req: meetings.scailo_pb2.MeetingsServiceAssociateCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_associate(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_associate(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteAssociate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/DeleteAssociate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_associate(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_associate(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_associate_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingAssociate]:
        """Low-level method to call ViewAssociateByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewAssociateByID"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingAssociate,extra_headers, timeout_seconds)


    def view_associate_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingAssociate:
        response = self.call_view_associate_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_associates(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingAssociatesList]:
        """Low-level method to call ViewAssociates, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewAssociates"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingAssociatesList,extra_headers, timeout_seconds)


    def view_associates(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingAssociatesList:
        response = self.call_view_associates(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_set_associate_rsvp(
        self, req: meetings.scailo_pb2.MeetingsServiceSetRSVPRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call SetAssociateRSVP, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/SetAssociateRSVP"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def set_associate_rsvp(
        self, req: meetings.scailo_pb2.MeetingsServiceSetRSVPRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_set_associate_rsvp(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.Meeting]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewByID"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.Meeting,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.Meeting:
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
    ) -> UnaryOutput[meetings.scailo_pb2.Meeting]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewByUUID"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.Meeting,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.Meeting:
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
    ) -> UnaryOutput[meetings.scailo_pb2.Meeting]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.Meeting,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.Meeting:
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
    ) -> UnaryOutput[meetings.scailo_pb2.Meeting]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.Meeting,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.Meeting:
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
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsList:
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
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewAll"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsList:
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
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: meetings.scailo_pb2.MeetingsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: meetings.scailo_pb2.MeetingsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsServicePaginationResponse:
        response = self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_all(
        self, req: meetings.scailo_pb2.MeetingsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/SearchAll"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsList,extra_headers, timeout_seconds)


    def search_all(
        self, req: meetings.scailo_pb2.MeetingsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: meetings.scailo_pb2.MeetingsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/Filter"
        return self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsList,extra_headers, timeout_seconds)


    def filter(
        self, req: meetings.scailo_pb2.MeetingsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsList:
        response = self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_count(
        self, req: meetings.scailo_pb2.MeetingsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: meetings.scailo_pb2.MeetingsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = self.call_count(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncMeetingsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: meetings.scailo_pb2.MeetingsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def create(
        self, req: meetings.scailo_pb2.MeetingsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_create(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_update(
        self, req: meetings.scailo_pb2.MeetingsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Update, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/Update"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def update(
        self, req: meetings.scailo_pb2.MeetingsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_update(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_cancel(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Cancel, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/Cancel"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def cancel(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_cancel(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.MeetingsService/Complete"
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
        url = self.base_url + "/Scailo.MeetingsService/Repeat"
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
        url = self.base_url + "/Scailo.MeetingsService/CommentAdd"
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

    async def call_send_email(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call SendEmail, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/SendEmail"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def send_email(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_send_email(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_request_rsvp(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RequestRSVP, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/RequestRSVP"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def request_rsvp(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_request_rsvp(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_send_actionables(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call SendActionables, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/SendActionables"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def send_actionables(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_send_actionables(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_actionable(
        self, req: meetings.scailo_pb2.MeetingsServiceActionableCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddActionable, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/AddActionable"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_actionable(
        self, req: meetings.scailo_pb2.MeetingsServiceActionableCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_actionable(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_actionable(
        self, req: meetings.scailo_pb2.MeetingsServiceActionableUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyActionable, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ModifyActionable"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_actionable(
        self, req: meetings.scailo_pb2.MeetingsServiceActionableUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_actionable(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_actionable(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteActionable, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/DeleteActionable"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_actionable(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_actionable(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_actionables(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderActionables, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ReorderActionables"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_actionables(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_actionables(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_actionable_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingActionable]:
        """Low-level method to call ViewActionableByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewActionableByID"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingActionable,extra_headers, timeout_seconds)

    async def view_actionable_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingActionable:
        response = await self.call_view_actionable_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_actionables(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingActionablesList]:
        """Low-level method to call ViewActionables, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewActionables"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingActionablesList,extra_headers, timeout_seconds)

    async def view_actionables(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingActionablesList:
        response = await self.call_view_actionables(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_actionable_history(
        self, req: meetings.scailo_pb2.MeetingActionableHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingActionablesList]:
        """Low-level method to call ViewActionableHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewActionableHistory"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingActionablesList,extra_headers, timeout_seconds)

    async def view_actionable_history(
        self, req: meetings.scailo_pb2.MeetingActionableHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingActionablesList:
        response = await self.call_view_actionable_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_actionables(
        self, req: meetings.scailo_pb2.MeetingActionablesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse]:
        """Low-level method to call ViewPaginatedActionables, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewPaginatedActionables"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse,extra_headers, timeout_seconds)

    async def view_paginated_actionables(
        self, req: meetings.scailo_pb2.MeetingActionablesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse:
        response = await self.call_view_paginated_actionables(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_actionables_with_pagination(
        self, req: meetings.scailo_pb2.MeetingActionablesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse]:
        """Low-level method to call SearchActionablesWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/SearchActionablesWithPagination"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse,extra_headers, timeout_seconds)

    async def search_actionables_with_pagination(
        self, req: meetings.scailo_pb2.MeetingActionablesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse:
        response = await self.call_search_actionables_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_employee(
        self, req: meetings.scailo_pb2.MeetingsServiceEmployeeCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddEmployee, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/AddEmployee"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_employee(
        self, req: meetings.scailo_pb2.MeetingsServiceEmployeeCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_employee(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_employee(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteEmployee, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/DeleteEmployee"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_employee(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_employee(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_employee_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingEmployee]:
        """Low-level method to call ViewEmployeeByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewEmployeeByID"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingEmployee,extra_headers, timeout_seconds)

    async def view_employee_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingEmployee:
        response = await self.call_view_employee_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_employees(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingEmployeesList]:
        """Low-level method to call ViewEmployees, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewEmployees"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingEmployeesList,extra_headers, timeout_seconds)

    async def view_employees(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingEmployeesList:
        response = await self.call_view_employees(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_set_employee_rsvp(
        self, req: meetings.scailo_pb2.MeetingsServiceSetRSVPRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call SetEmployeeRSVP, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/SetEmployeeRSVP"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def set_employee_rsvp(
        self, req: meetings.scailo_pb2.MeetingsServiceSetRSVPRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_set_employee_rsvp(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_import_from_team(
        self, req: meetings.scailo_pb2.MeetingsServiceImportEmployeesRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportFromTeam, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ImportFromTeam"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def import_from_team(
        self, req: meetings.scailo_pb2.MeetingsServiceImportEmployeesRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_import_from_team(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_import_from_department(
        self, req: meetings.scailo_pb2.MeetingsServiceImportEmployeesRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportFromDepartment, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ImportFromDepartment"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def import_from_department(
        self, req: meetings.scailo_pb2.MeetingsServiceImportEmployeesRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_import_from_department(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_associate(
        self, req: meetings.scailo_pb2.MeetingsServiceAssociateCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddAssociate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/AddAssociate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_associate(
        self, req: meetings.scailo_pb2.MeetingsServiceAssociateCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_associate(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_associate(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteAssociate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/DeleteAssociate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_associate(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_associate(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_associate_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingAssociate]:
        """Low-level method to call ViewAssociateByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewAssociateByID"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingAssociate,extra_headers, timeout_seconds)

    async def view_associate_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingAssociate:
        response = await self.call_view_associate_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_associates(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingAssociatesList]:
        """Low-level method to call ViewAssociates, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewAssociates"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingAssociatesList,extra_headers, timeout_seconds)

    async def view_associates(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingAssociatesList:
        response = await self.call_view_associates(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_set_associate_rsvp(
        self, req: meetings.scailo_pb2.MeetingsServiceSetRSVPRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call SetAssociateRSVP, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/SetAssociateRSVP"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def set_associate_rsvp(
        self, req: meetings.scailo_pb2.MeetingsServiceSetRSVPRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_set_associate_rsvp(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.Meeting]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewByID"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.Meeting,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.Meeting:
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
    ) -> UnaryOutput[meetings.scailo_pb2.Meeting]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.Meeting,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.Meeting:
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
    ) -> UnaryOutput[meetings.scailo_pb2.Meeting]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.Meeting,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.Meeting:
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
    ) -> UnaryOutput[meetings.scailo_pb2.Meeting]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.Meeting,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.Meeting:
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
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsList:
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
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewAll"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsList:
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
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: meetings.scailo_pb2.MeetingsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: meetings.scailo_pb2.MeetingsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsServicePaginationResponse:
        response = await self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_all(
        self, req: meetings.scailo_pb2.MeetingsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/SearchAll"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: meetings.scailo_pb2.MeetingsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: meetings.scailo_pb2.MeetingsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[meetings.scailo_pb2.MeetingsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/Filter"
        return await self._connect_client.call_unary(url, req, meetings.scailo_pb2.MeetingsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: meetings.scailo_pb2.MeetingsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> meetings.scailo_pb2.MeetingsList:
        response = await self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_count(
        self, req: meetings.scailo_pb2.MeetingsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.MeetingsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: meetings.scailo_pb2.MeetingsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = await self.call_count(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class MeetingsServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def update(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def cancel(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def complete(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def repeat(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def comment_add(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_email(self, req: ClientRequest[base.scailo_pb2.IdentifierWithEmailAttributes]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def request_rsvp(self, req: ClientRequest[base.scailo_pb2.IdentifierWithEmailAttributes]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_actionables(self, req: ClientRequest[base.scailo_pb2.IdentifierWithEmailAttributes]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_actionable(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServiceActionableCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_actionable(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServiceActionableUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_actionable(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_actionables(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_actionable_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[meetings.scailo_pb2.MeetingActionable]:
        ...
    def view_actionables(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[meetings.scailo_pb2.MeetingActionablesList]:
        ...
    def view_actionable_history(self, req: ClientRequest[meetings.scailo_pb2.MeetingActionableHistoryRequest]) -> ServerResponse[meetings.scailo_pb2.MeetingActionablesList]:
        ...
    def view_paginated_actionables(self, req: ClientRequest[meetings.scailo_pb2.MeetingActionablesSearchRequest]) -> ServerResponse[meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse]:
        ...
    def search_actionables_with_pagination(self, req: ClientRequest[meetings.scailo_pb2.MeetingActionablesSearchRequest]) -> ServerResponse[meetings.scailo_pb2.MeetingsServicePaginatedActionablesResponse]:
        ...
    def add_employee(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServiceEmployeeCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_employee(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_employee_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[meetings.scailo_pb2.MeetingEmployee]:
        ...
    def view_employees(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[meetings.scailo_pb2.MeetingEmployeesList]:
        ...
    def set_employee_rsvp(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServiceSetRSVPRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def import_from_team(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServiceImportEmployeesRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def import_from_department(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServiceImportEmployeesRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_associate(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServiceAssociateCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_associate(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_associate_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[meetings.scailo_pb2.MeetingAssociate]:
        ...
    def view_associates(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[meetings.scailo_pb2.MeetingAssociatesList]:
        ...
    def set_associate_rsvp(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServiceSetRSVPRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[meetings.scailo_pb2.Meeting]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[meetings.scailo_pb2.Meeting]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[meetings.scailo_pb2.Meeting]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[meetings.scailo_pb2.Meeting]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[meetings.scailo_pb2.MeetingsList]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[meetings.scailo_pb2.MeetingsList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[meetings.scailo_pb2.MeetingsList]:
        ...
    def view_with_pagination(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServicePaginationReq]) -> ServerResponse[meetings.scailo_pb2.MeetingsServicePaginationResponse]:
        ...
    def search_all(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServiceSearchAllReq]) -> ServerResponse[meetings.scailo_pb2.MeetingsList]:
        ...
    def filter(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServiceFilterReq]) -> ServerResponse[meetings.scailo_pb2.MeetingsList]:
        ...
    def count(self, req: ClientRequest[meetings.scailo_pb2.MeetingsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...

MEETINGS_SERVICE_PATH_PREFIX = "/Scailo.MeetingsService"

def wsgi_meetings_service(implementation: MeetingsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.MeetingsService/Create", implementation.create, meetings.scailo_pb2.MeetingsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/Update", implementation.update, meetings.scailo_pb2.MeetingsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/Cancel", implementation.cancel, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.MeetingsService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.MeetingsService/Repeat", implementation.repeat, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.MeetingsService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.MeetingsService/SendEmail", implementation.send_email, base.scailo_pb2.IdentifierWithEmailAttributes)
    app.register_unary_rpc("/Scailo.MeetingsService/RequestRSVP", implementation.request_rsvp, base.scailo_pb2.IdentifierWithEmailAttributes)
    app.register_unary_rpc("/Scailo.MeetingsService/SendActionables", implementation.send_actionables, base.scailo_pb2.IdentifierWithEmailAttributes)
    app.register_unary_rpc("/Scailo.MeetingsService/AddActionable", implementation.add_actionable, meetings.scailo_pb2.MeetingsServiceActionableCreateRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/ModifyActionable", implementation.modify_actionable, meetings.scailo_pb2.MeetingsServiceActionableUpdateRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/DeleteActionable", implementation.delete_actionable, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.MeetingsService/ReorderActionables", implementation.reorder_actionables, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewActionableByID", implementation.view_actionable_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewActionables", implementation.view_actionables, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewActionableHistory", implementation.view_actionable_history, meetings.scailo_pb2.MeetingActionableHistoryRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewPaginatedActionables", implementation.view_paginated_actionables, meetings.scailo_pb2.MeetingActionablesSearchRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/SearchActionablesWithPagination", implementation.search_actionables_with_pagination, meetings.scailo_pb2.MeetingActionablesSearchRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/AddEmployee", implementation.add_employee, meetings.scailo_pb2.MeetingsServiceEmployeeCreateRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/DeleteEmployee", implementation.delete_employee, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewEmployeeByID", implementation.view_employee_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewEmployees", implementation.view_employees, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.MeetingsService/SetEmployeeRSVP", implementation.set_employee_rsvp, meetings.scailo_pb2.MeetingsServiceSetRSVPRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/ImportFromTeam", implementation.import_from_team, meetings.scailo_pb2.MeetingsServiceImportEmployeesRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/ImportFromDepartment", implementation.import_from_department, meetings.scailo_pb2.MeetingsServiceImportEmployeesRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/AddAssociate", implementation.add_associate, meetings.scailo_pb2.MeetingsServiceAssociateCreateRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/DeleteAssociate", implementation.delete_associate, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewAssociateByID", implementation.view_associate_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewAssociates", implementation.view_associates, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.MeetingsService/SetAssociateRSVP", implementation.set_associate_rsvp, meetings.scailo_pb2.MeetingsServiceSetRSVPRequest)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.MeetingsService/ViewWithPagination", implementation.view_with_pagination, meetings.scailo_pb2.MeetingsServicePaginationReq)
    app.register_unary_rpc("/Scailo.MeetingsService/SearchAll", implementation.search_all, meetings.scailo_pb2.MeetingsServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.MeetingsService/Filter", implementation.filter, meetings.scailo_pb2.MeetingsServiceFilterReq)
    app.register_unary_rpc("/Scailo.MeetingsService/Count", implementation.count, meetings.scailo_pb2.MeetingsServiceCountReq)
    return app
