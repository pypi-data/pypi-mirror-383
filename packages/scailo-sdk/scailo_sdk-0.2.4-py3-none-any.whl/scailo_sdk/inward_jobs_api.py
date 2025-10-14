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

from scailo_sdk import base, families, inward_jobs, magic_links

class InwardJobsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def create(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Draft"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DraftUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft_update(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.InwardJobsService/SendForVerification"
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
        url = self.base_url + "/Scailo.InwardJobsService/Verify"
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
        url = self.base_url + "/Scailo.InwardJobsService/Approve"
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
        url = self.base_url + "/Scailo.InwardJobsService/SendForRevision"
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
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/RevisionUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def revision_update(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.InwardJobsService/Halt"
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
        url = self.base_url + "/Scailo.InwardJobsService/Discard"
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
        url = self.base_url + "/Scailo.InwardJobsService/Restore"
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
        url = self.base_url + "/Scailo.InwardJobsService/Complete"
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
        self, req: base.scailo_pb2.RepeatWithDeliveryDate,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Repeat, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Repeat"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def repeat(
        self, req: base.scailo_pb2.RepeatWithDeliveryDate,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_repeat(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reopen(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Reopen, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Reopen"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reopen(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reopen(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.InwardJobsService/CommentAdd"
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
        url = self.base_url + "/Scailo.InwardJobsService/SendEmail"
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

    def call_autofill(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Autofill"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def autofill(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_autofill(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_create_magic_link(
        self, req: magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[magic_links.scailo_pb2.MagicLink]:
        """Low-level method to call CreateMagicLink, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/CreateMagicLink"
        return self._connect_client.call_unary(url, req, magic_links.scailo_pb2.MagicLink,extra_headers, timeout_seconds)


    def create_magic_link(
        self, req: magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> magic_links.scailo_pb2.MagicLink:
        response = self.call_create_magic_link(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_is_completable(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call IsCompletable, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/IsCompletable"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)


    def is_completable(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = self.call_is_completable(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_is_ordered(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call IsOrdered, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/IsOrdered"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)


    def is_ordered(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = self.call_is_ordered(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_is_received(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call IsReceived, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/IsReceived"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)


    def is_received(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = self.call_is_received(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_multiple_inward_job_inward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceMultipleInwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddMultipleInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/AddMultipleInwardJobInwardItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_multiple_inward_job_inward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceMultipleInwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_multiple_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_inward_job_inward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceInwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/AddInwardJobInwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_inward_job_inward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceInwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_inward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_inward_job_inward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceInwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyInwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ModifyInwardJobInwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_inward_job_inward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceInwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_inward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_inward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveInwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ApproveInwardJobInwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_inward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_inward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_inward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteInwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DeleteInwardJobInwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_inward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_inward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_inward_job_inward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ReorderInwardJobInwardItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_inward_job_inward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_inward_job_inward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobInwardItem]:
        """Low-level method to call ViewInwardJobInwardItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardJobInwardItemByID"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobInwardItem,extra_headers, timeout_seconds)


    def view_inward_job_inward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobInwardItem:
        response = self.call_view_inward_job_inward_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_approved_inward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsInwardItemsList]:
        """Low-level method to call ViewApprovedInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewApprovedInwardJobInwardItems"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsInwardItemsList,extra_headers, timeout_seconds)


    def view_approved_inward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsInwardItemsList:
        response = self.call_view_approved_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_unapproved_inward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsInwardItemsList]:
        """Low-level method to call ViewUnapprovedInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewUnapprovedInwardJobInwardItems"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsInwardItemsList,extra_headers, timeout_seconds)


    def view_unapproved_inward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsInwardItemsList:
        response = self.call_view_unapproved_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_inward_job_inward_item_history(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsInwardItemsList]:
        """Low-level method to call ViewInwardJobInwardItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardJobInwardItemHistory"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsInwardItemsList,extra_headers, timeout_seconds)


    def view_inward_job_inward_item_history(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsInwardItemsList:
        response = self.call_view_inward_job_inward_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_approved_inward_job_inward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewPaginatedApprovedInwardJobInwardItems"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_approved_inward_job_inward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse:
        response = self.call_view_paginated_approved_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_unapproved_inward_job_inward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewPaginatedUnapprovedInwardJobInwardItems"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_unapproved_inward_job_inward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse:
        response = self.call_view_paginated_unapproved_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_inward_items_with_pagination(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse]:
        """Low-level method to call SearchInwardItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/SearchInwardItemsWithPagination"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse,extra_headers, timeout_seconds)


    def search_inward_items_with_pagination(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse:
        response = self.call_search_inward_items_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_download_inward_items_csv_template(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadInwardItemsCSVTemplate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DownloadInwardItemsCSVTemplate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_inward_items_csv_template(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_inward_items_csv_template(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_upload_inward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/UploadInwardJobInwardItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def upload_inward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_upload_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_multiple_inward_job_outward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceMultipleOutwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddMultipleInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/AddMultipleInwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_multiple_inward_job_outward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceMultipleOutwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_multiple_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_inward_job_outward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/AddInwardJobOutwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_inward_job_outward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_inward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_inward_job_outward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyInwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ModifyInwardJobOutwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_inward_job_outward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_inward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_inward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveInwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ApproveInwardJobOutwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_inward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_inward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_inward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteInwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DeleteInwardJobOutwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_inward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_inward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_inward_job_outward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ReorderInwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_inward_job_outward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_inward_job_outward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobOutwardItem]:
        """Low-level method to call ViewInwardJobOutwardItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardJobOutwardItemByID"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobOutwardItem,extra_headers, timeout_seconds)


    def view_inward_job_outward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobOutwardItem:
        response = self.call_view_inward_job_outward_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_approved_inward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsOutwardItemsList]:
        """Low-level method to call ViewApprovedInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewApprovedInwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsOutwardItemsList,extra_headers, timeout_seconds)


    def view_approved_inward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsOutwardItemsList:
        response = self.call_view_approved_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_unapproved_inward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsOutwardItemsList]:
        """Low-level method to call ViewUnapprovedInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewUnapprovedInwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsOutwardItemsList,extra_headers, timeout_seconds)


    def view_unapproved_inward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsOutwardItemsList:
        response = self.call_view_unapproved_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_inward_job_outward_item_history(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsOutwardItemsList]:
        """Low-level method to call ViewInwardJobOutwardItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardJobOutwardItemHistory"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsOutwardItemsList,extra_headers, timeout_seconds)


    def view_inward_job_outward_item_history(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsOutwardItemsList:
        response = self.call_view_inward_job_outward_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_approved_inward_job_outward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewPaginatedApprovedInwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_approved_inward_job_outward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse:
        response = self.call_view_paginated_approved_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_unapproved_inward_job_outward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewPaginatedUnapprovedInwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_unapproved_inward_job_outward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse:
        response = self.call_view_paginated_unapproved_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_outward_items_with_pagination(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse]:
        """Low-level method to call SearchOutwardItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/SearchOutwardItemsWithPagination"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse,extra_headers, timeout_seconds)


    def search_outward_items_with_pagination(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse:
        response = self.call_search_outward_items_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_download_outward_items_csv_template(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadOutwardItemsCSVTemplate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DownloadOutwardItemsCSVTemplate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_outward_items_csv_template(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_outward_items_csv_template(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_upload_inward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/UploadInwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def upload_inward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_upload_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_inward_job_contact(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceContactCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInwardJobContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/AddInwardJobContact"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_inward_job_contact(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceContactCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_inward_job_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_inward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveInwardJobContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ApproveInwardJobContact"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_inward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_inward_job_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_inward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteInwardJobContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DeleteInwardJobContact"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_inward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_inward_job_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_inward_job_contact_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobContact]:
        """Low-level method to call ViewInwardJobContactByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardJobContactByID"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobContact,extra_headers, timeout_seconds)


    def view_inward_job_contact_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobContact:
        response = self.call_view_inward_job_contact_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_inward_job_contacts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobContactsList]:
        """Low-level method to call ViewInwardJobContacts, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardJobContacts"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobContactsList,extra_headers, timeout_seconds)


    def view_inward_job_contacts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobContactsList:
        response = self.call_view_inward_job_contacts(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJob]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewByID"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJob,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJob:
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
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJob]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewByUUID"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJob,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJob:
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
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJob]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJob,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJob:
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
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJob]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJob,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJob:
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
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsList:
        response = self.call_view_from_i_ds(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewAncillaryParametersByUUID"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobAncillaryParameters,extra_headers, timeout_seconds)


    def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobAncillaryParameters:
        response = self.call_view_ancillary_parameters_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewAll"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsList:
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
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: inward_jobs.scailo_pb2.InwardJobsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: inward_jobs.scailo_pb2.InwardJobsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginationResponse:
        response = self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_associated_sales_order_i_ds(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call ViewAssociatedSalesOrderIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewAssociatedSalesOrderIDs"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def view_associated_sales_order_i_ds(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_view_associated_sales_order_i_ds(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_inward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobInwardInventoryMatchList]:
        """Low-level method to call ViewInwardInventoryMatch, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardInventoryMatch"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobInwardInventoryMatchList,extra_headers, timeout_seconds)


    def view_inward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobInwardInventoryMatchList:
        response = self.call_view_inward_inventory_match(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_prospective_inward_families(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call ViewProspectiveInwardFamilies, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewProspectiveInwardFamilies"
        return self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)


    def view_prospective_inward_families(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = self.call_view_prospective_inward_families(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter_prospective_inward_families(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call FilterProspectiveInwardFamilies, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/FilterProspectiveInwardFamilies"
        return self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)


    def filter_prospective_inward_families(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = self.call_filter_prospective_inward_families(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_prospective_inward_job_inward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServiceInwardItemCreateRequest]:
        """Low-level method to call ViewProspectiveInwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewProspectiveInwardJobInwardItem"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServiceInwardItemCreateRequest,extra_headers, timeout_seconds)


    def view_prospective_inward_job_inward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServiceInwardItemCreateRequest:
        response = self.call_view_prospective_inward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobOutwardInventoryMatchList]:
        """Low-level method to call ViewOutwardInventoryMatch, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewOutwardInventoryMatch"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobOutwardInventoryMatchList,extra_headers, timeout_seconds)


    def view_outward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobOutwardInventoryMatchList:
        response = self.call_view_outward_inventory_match(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_prospective_outward_families(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call ViewProspectiveOutwardFamilies, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewProspectiveOutwardFamilies"
        return self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)


    def view_prospective_outward_families(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = self.call_view_prospective_outward_families(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter_prospective_outward_families(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call FilterProspectiveOutwardFamilies, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/FilterProspectiveOutwardFamilies"
        return self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)


    def filter_prospective_outward_families(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = self.call_filter_prospective_outward_families(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_prospective_inward_job_outward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemCreateRequest]:
        """Low-level method to call ViewProspectiveInwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewProspectiveInwardJobOutwardItem"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemCreateRequest,extra_headers, timeout_seconds)


    def view_prospective_inward_job_outward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemCreateRequest:
        response = self.call_view_prospective_inward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_is_downloadable(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call IsDownloadable, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/IsDownloadable"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)


    def is_downloadable(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = self.call_is_downloadable(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_download_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DownloadByUUID"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_all(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/SearchAll"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsList,extra_headers, timeout_seconds)


    def search_all(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Filter"
        return self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsList,extra_headers, timeout_seconds)


    def filter(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsList:
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
        url = self.base_url + "/Scailo.InwardJobsService/CountInStatus"
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
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncInwardJobsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def create(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Draft"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DraftUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft_update(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.InwardJobsService/SendForVerification"
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
        url = self.base_url + "/Scailo.InwardJobsService/Verify"
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
        url = self.base_url + "/Scailo.InwardJobsService/Approve"
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
        url = self.base_url + "/Scailo.InwardJobsService/SendForRevision"
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
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/RevisionUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def revision_update(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.InwardJobsService/Halt"
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
        url = self.base_url + "/Scailo.InwardJobsService/Discard"
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
        url = self.base_url + "/Scailo.InwardJobsService/Restore"
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
        url = self.base_url + "/Scailo.InwardJobsService/Complete"
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
        self, req: base.scailo_pb2.RepeatWithDeliveryDate,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Repeat, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Repeat"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def repeat(
        self, req: base.scailo_pb2.RepeatWithDeliveryDate,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_repeat(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reopen(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Reopen, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Reopen"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reopen(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reopen(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.InwardJobsService/CommentAdd"
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
        url = self.base_url + "/Scailo.InwardJobsService/SendEmail"
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

    async def call_autofill(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Autofill"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def autofill(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_autofill(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_create_magic_link(
        self, req: magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[magic_links.scailo_pb2.MagicLink]:
        """Low-level method to call CreateMagicLink, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/CreateMagicLink"
        return await self._connect_client.call_unary(url, req, magic_links.scailo_pb2.MagicLink,extra_headers, timeout_seconds)

    async def create_magic_link(
        self, req: magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> magic_links.scailo_pb2.MagicLink:
        response = await self.call_create_magic_link(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_is_completable(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call IsCompletable, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/IsCompletable"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)

    async def is_completable(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = await self.call_is_completable(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_is_ordered(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call IsOrdered, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/IsOrdered"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)

    async def is_ordered(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = await self.call_is_ordered(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_is_received(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call IsReceived, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/IsReceived"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)

    async def is_received(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = await self.call_is_received(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_multiple_inward_job_inward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceMultipleInwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddMultipleInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/AddMultipleInwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_multiple_inward_job_inward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceMultipleInwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_multiple_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_inward_job_inward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceInwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/AddInwardJobInwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_inward_job_inward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceInwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_inward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_inward_job_inward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceInwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyInwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ModifyInwardJobInwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_inward_job_inward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceInwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_inward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_inward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveInwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ApproveInwardJobInwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_inward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_inward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_inward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteInwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DeleteInwardJobInwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_inward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_inward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_inward_job_inward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ReorderInwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_inward_job_inward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_inward_job_inward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobInwardItem]:
        """Low-level method to call ViewInwardJobInwardItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardJobInwardItemByID"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobInwardItem,extra_headers, timeout_seconds)

    async def view_inward_job_inward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobInwardItem:
        response = await self.call_view_inward_job_inward_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_approved_inward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsInwardItemsList]:
        """Low-level method to call ViewApprovedInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewApprovedInwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsInwardItemsList,extra_headers, timeout_seconds)

    async def view_approved_inward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsInwardItemsList:
        response = await self.call_view_approved_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_unapproved_inward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsInwardItemsList]:
        """Low-level method to call ViewUnapprovedInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewUnapprovedInwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsInwardItemsList,extra_headers, timeout_seconds)

    async def view_unapproved_inward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsInwardItemsList:
        response = await self.call_view_unapproved_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_inward_job_inward_item_history(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsInwardItemsList]:
        """Low-level method to call ViewInwardJobInwardItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardJobInwardItemHistory"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsInwardItemsList,extra_headers, timeout_seconds)

    async def view_inward_job_inward_item_history(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsInwardItemsList:
        response = await self.call_view_inward_job_inward_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_approved_inward_job_inward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewPaginatedApprovedInwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_approved_inward_job_inward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse:
        response = await self.call_view_paginated_approved_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_unapproved_inward_job_inward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewPaginatedUnapprovedInwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_unapproved_inward_job_inward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse:
        response = await self.call_view_paginated_unapproved_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_inward_items_with_pagination(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse]:
        """Low-level method to call SearchInwardItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/SearchInwardItemsWithPagination"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse,extra_headers, timeout_seconds)

    async def search_inward_items_with_pagination(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse:
        response = await self.call_search_inward_items_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_download_inward_items_csv_template(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadInwardItemsCSVTemplate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DownloadInwardItemsCSVTemplate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_inward_items_csv_template(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_inward_items_csv_template(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_upload_inward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadInwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/UploadInwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def upload_inward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_upload_inward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_multiple_inward_job_outward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceMultipleOutwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddMultipleInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/AddMultipleInwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_multiple_inward_job_outward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceMultipleOutwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_multiple_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_inward_job_outward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/AddInwardJobOutwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_inward_job_outward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_inward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_inward_job_outward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyInwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ModifyInwardJobOutwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_inward_job_outward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_inward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_inward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveInwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ApproveInwardJobOutwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_inward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_inward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_inward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteInwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DeleteInwardJobOutwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_inward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_inward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_inward_job_outward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ReorderInwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_inward_job_outward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_inward_job_outward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobOutwardItem]:
        """Low-level method to call ViewInwardJobOutwardItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardJobOutwardItemByID"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobOutwardItem,extra_headers, timeout_seconds)

    async def view_inward_job_outward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobOutwardItem:
        response = await self.call_view_inward_job_outward_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_approved_inward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsOutwardItemsList]:
        """Low-level method to call ViewApprovedInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewApprovedInwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsOutwardItemsList,extra_headers, timeout_seconds)

    async def view_approved_inward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsOutwardItemsList:
        response = await self.call_view_approved_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_unapproved_inward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsOutwardItemsList]:
        """Low-level method to call ViewUnapprovedInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewUnapprovedInwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsOutwardItemsList,extra_headers, timeout_seconds)

    async def view_unapproved_inward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsOutwardItemsList:
        response = await self.call_view_unapproved_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_inward_job_outward_item_history(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsOutwardItemsList]:
        """Low-level method to call ViewInwardJobOutwardItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardJobOutwardItemHistory"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsOutwardItemsList,extra_headers, timeout_seconds)

    async def view_inward_job_outward_item_history(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsOutwardItemsList:
        response = await self.call_view_inward_job_outward_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_approved_inward_job_outward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewPaginatedApprovedInwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_approved_inward_job_outward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse:
        response = await self.call_view_paginated_approved_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_unapproved_inward_job_outward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewPaginatedUnapprovedInwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_unapproved_inward_job_outward_items(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse:
        response = await self.call_view_paginated_unapproved_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_outward_items_with_pagination(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse]:
        """Low-level method to call SearchOutwardItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/SearchOutwardItemsWithPagination"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse,extra_headers, timeout_seconds)

    async def search_outward_items_with_pagination(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse:
        response = await self.call_search_outward_items_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_download_outward_items_csv_template(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadOutwardItemsCSVTemplate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DownloadOutwardItemsCSVTemplate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_outward_items_csv_template(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_outward_items_csv_template(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_upload_inward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadInwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/UploadInwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def upload_inward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_upload_inward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_inward_job_contact(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceContactCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInwardJobContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/AddInwardJobContact"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_inward_job_contact(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceContactCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_inward_job_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_inward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveInwardJobContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ApproveInwardJobContact"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_inward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_inward_job_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_inward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteInwardJobContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DeleteInwardJobContact"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_inward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_inward_job_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_inward_job_contact_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobContact]:
        """Low-level method to call ViewInwardJobContactByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardJobContactByID"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobContact,extra_headers, timeout_seconds)

    async def view_inward_job_contact_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobContact:
        response = await self.call_view_inward_job_contact_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_inward_job_contacts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobContactsList]:
        """Low-level method to call ViewInwardJobContacts, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardJobContacts"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobContactsList,extra_headers, timeout_seconds)

    async def view_inward_job_contacts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobContactsList:
        response = await self.call_view_inward_job_contacts(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJob]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewByID"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJob,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJob:
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
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJob]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJob,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJob:
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
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJob]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJob,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJob:
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
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJob]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJob,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJob:
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
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsList:
        response = await self.call_view_from_i_ds(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewAncillaryParametersByUUID"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobAncillaryParameters,extra_headers, timeout_seconds)

    async def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobAncillaryParameters:
        response = await self.call_view_ancillary_parameters_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewAll"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsList:
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
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: inward_jobs.scailo_pb2.InwardJobsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: inward_jobs.scailo_pb2.InwardJobsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServicePaginationResponse:
        response = await self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_associated_sales_order_i_ds(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call ViewAssociatedSalesOrderIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewAssociatedSalesOrderIDs"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def view_associated_sales_order_i_ds(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_view_associated_sales_order_i_ds(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_inward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobInwardInventoryMatchList]:
        """Low-level method to call ViewInwardInventoryMatch, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewInwardInventoryMatch"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobInwardInventoryMatchList,extra_headers, timeout_seconds)

    async def view_inward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobInwardInventoryMatchList:
        response = await self.call_view_inward_inventory_match(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_prospective_inward_families(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call ViewProspectiveInwardFamilies, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewProspectiveInwardFamilies"
        return await self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)

    async def view_prospective_inward_families(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = await self.call_view_prospective_inward_families(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter_prospective_inward_families(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call FilterProspectiveInwardFamilies, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/FilterProspectiveInwardFamilies"
        return await self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)

    async def filter_prospective_inward_families(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = await self.call_filter_prospective_inward_families(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_prospective_inward_job_inward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServiceInwardItemCreateRequest]:
        """Low-level method to call ViewProspectiveInwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewProspectiveInwardJobInwardItem"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServiceInwardItemCreateRequest,extra_headers, timeout_seconds)

    async def view_prospective_inward_job_inward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobInwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServiceInwardItemCreateRequest:
        response = await self.call_view_prospective_inward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobOutwardInventoryMatchList]:
        """Low-level method to call ViewOutwardInventoryMatch, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewOutwardInventoryMatch"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobOutwardInventoryMatchList,extra_headers, timeout_seconds)

    async def view_outward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobOutwardInventoryMatchList:
        response = await self.call_view_outward_inventory_match(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_prospective_outward_families(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call ViewProspectiveOutwardFamilies, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewProspectiveOutwardFamilies"
        return await self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)

    async def view_prospective_outward_families(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = await self.call_view_prospective_outward_families(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter_prospective_outward_families(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call FilterProspectiveOutwardFamilies, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/FilterProspectiveOutwardFamilies"
        return await self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)

    async def filter_prospective_outward_families(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = await self.call_filter_prospective_outward_families(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_prospective_inward_job_outward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemCreateRequest]:
        """Low-level method to call ViewProspectiveInwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/ViewProspectiveInwardJobOutwardItem"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemCreateRequest,extra_headers, timeout_seconds)

    async def view_prospective_inward_job_outward_item(
        self, req: inward_jobs.scailo_pb2.InwardJobOutwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemCreateRequest:
        response = await self.call_view_prospective_inward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_is_downloadable(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call IsDownloadable, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/IsDownloadable"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)

    async def is_downloadable(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = await self.call_is_downloadable(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_download_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DownloadByUUID"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_all(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/SearchAll"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs.scailo_pb2.InwardJobsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Filter"
        return await self._connect_client.call_unary(url, req, inward_jobs.scailo_pb2.InwardJobsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs.scailo_pb2.InwardJobsList:
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
        url = self.base_url + "/Scailo.InwardJobsService/CountInStatus"
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
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: inward_jobs.scailo_pb2.InwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
class InwardJobsServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft_update(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_verification(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def verify(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_revision(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def revision_update(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def halt(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def discard(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def restore(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def complete(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def repeat(self, req: ClientRequest[base.scailo_pb2.RepeatWithDeliveryDate]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reopen(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def comment_add(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_email(self, req: ClientRequest[base.scailo_pb2.IdentifierWithEmailAttributes]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def autofill(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceAutofillRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def create_magic_link(self, req: ClientRequest[magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource]) -> ServerResponse[magic_links.scailo_pb2.MagicLink]:
        ...
    def is_completable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def is_ordered(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def is_received(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def add_multiple_inward_job_inward_items(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceMultipleInwardItemsCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_inward_job_inward_item(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceInwardItemCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_inward_job_inward_item(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceInwardItemUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_inward_job_inward_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_inward_job_inward_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_inward_job_inward_items(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_inward_job_inward_item_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobInwardItem]:
        ...
    def view_approved_inward_job_inward_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsInwardItemsList]:
        ...
    def view_unapproved_inward_job_inward_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsInwardItemsList]:
        ...
    def view_inward_job_inward_item_history(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobInwardItemHistoryRequest]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsInwardItemsList]:
        ...
    def view_paginated_approved_inward_job_inward_items(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse]:
        ...
    def view_paginated_unapproved_inward_job_inward_items(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse]:
        ...
    def search_inward_items_with_pagination(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsServicePaginatedInwardItemsResponse]:
        ...
    def download_inward_items_csv_template(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def upload_inward_job_inward_items(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithFile]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def add_multiple_inward_job_outward_items(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceMultipleOutwardItemsCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_inward_job_outward_item(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_inward_job_outward_item(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_inward_job_outward_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_inward_job_outward_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_inward_job_outward_items(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_inward_job_outward_item_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobOutwardItem]:
        ...
    def view_approved_inward_job_outward_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsOutwardItemsList]:
        ...
    def view_unapproved_inward_job_outward_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsOutwardItemsList]:
        ...
    def view_inward_job_outward_item_history(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobOutwardItemHistoryRequest]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsOutwardItemsList]:
        ...
    def view_paginated_approved_inward_job_outward_items(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse]:
        ...
    def view_paginated_unapproved_inward_job_outward_items(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse]:
        ...
    def search_outward_items_with_pagination(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsServicePaginatedOutwardItemsResponse]:
        ...
    def download_outward_items_csv_template(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def upload_inward_job_outward_items(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithFile]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def add_inward_job_contact(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceContactCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_inward_job_contact(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_inward_job_contact(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_inward_job_contact_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobContact]:
        ...
    def view_inward_job_contacts(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobContactsList]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJob]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJob]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJob]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJob]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsList]:
        ...
    def view_ancillary_parameters_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobAncillaryParameters]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsList]:
        ...
    def view_with_pagination(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServicePaginationReq]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsServicePaginationResponse]:
        ...
    def view_associated_sales_order_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def view_inward_inventory_match(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobInwardInventoryMatchList]:
        ...
    def view_prospective_inward_families(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def filter_prospective_inward_families(self, req: ClientRequest[families.scailo_pb2.FilterFamiliesReqForIdentifier]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def view_prospective_inward_job_inward_item(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobInwardItemProspectiveInfoRequest]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsServiceInwardItemCreateRequest]:
        ...
    def view_outward_inventory_match(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobOutwardInventoryMatchList]:
        ...
    def view_prospective_outward_families(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def filter_prospective_outward_families(self, req: ClientRequest[families.scailo_pb2.FilterFamiliesReqForIdentifier]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def view_prospective_inward_job_outward_item(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobOutwardItemProspectiveInfoRequest]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemCreateRequest]:
        ...
    def is_downloadable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def download_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def search_all(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceSearchAllReq]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsList]:
        ...
    def filter(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceFilterReq]) -> ServerResponse[inward_jobs.scailo_pb2.InwardJobsList]:
        ...
    def count_in_status(self, req: ClientRequest[base.scailo_pb2.CountInSLCStatusRequest]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def count(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[inward_jobs.scailo_pb2.InwardJobsServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

INWARD_JOBS_SERVICE_PATH_PREFIX = "/Scailo.InwardJobsService"

def wsgi_inward_jobs_service(implementation: InwardJobsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.InwardJobsService/Create", implementation.create, inward_jobs.scailo_pb2.InwardJobsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/Draft", implementation.draft, inward_jobs.scailo_pb2.InwardJobsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/DraftUpdate", implementation.draft_update, inward_jobs.scailo_pb2.InwardJobsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/SendForVerification", implementation.send_for_verification, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/Verify", implementation.verify, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/Approve", implementation.approve, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/SendForRevision", implementation.send_for_revision, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/RevisionUpdate", implementation.revision_update, inward_jobs.scailo_pb2.InwardJobsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/Halt", implementation.halt, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/Discard", implementation.discard, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/Restore", implementation.restore, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/Repeat", implementation.repeat, base.scailo_pb2.RepeatWithDeliveryDate)
    app.register_unary_rpc("/Scailo.InwardJobsService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/SendEmail", implementation.send_email, base.scailo_pb2.IdentifierWithEmailAttributes)
    app.register_unary_rpc("/Scailo.InwardJobsService/Autofill", implementation.autofill, inward_jobs.scailo_pb2.InwardJobsServiceAutofillRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/CreateMagicLink", implementation.create_magic_link, magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource)
    app.register_unary_rpc("/Scailo.InwardJobsService/IsCompletable", implementation.is_completable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/IsOrdered", implementation.is_ordered, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/IsReceived", implementation.is_received, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/AddMultipleInwardJobInwardItems", implementation.add_multiple_inward_job_inward_items, inward_jobs.scailo_pb2.InwardJobsServiceMultipleInwardItemsCreateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/AddInwardJobInwardItem", implementation.add_inward_job_inward_item, inward_jobs.scailo_pb2.InwardJobsServiceInwardItemCreateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/ModifyInwardJobInwardItem", implementation.modify_inward_job_inward_item, inward_jobs.scailo_pb2.InwardJobsServiceInwardItemUpdateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/ApproveInwardJobInwardItem", implementation.approve_inward_job_inward_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/DeleteInwardJobInwardItem", implementation.delete_inward_job_inward_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/ReorderInwardJobInwardItems", implementation.reorder_inward_job_inward_items, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewInwardJobInwardItemByID", implementation.view_inward_job_inward_item_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewApprovedInwardJobInwardItems", implementation.view_approved_inward_job_inward_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewUnapprovedInwardJobInwardItems", implementation.view_unapproved_inward_job_inward_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewInwardJobInwardItemHistory", implementation.view_inward_job_inward_item_history, inward_jobs.scailo_pb2.InwardJobInwardItemHistoryRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewPaginatedApprovedInwardJobInwardItems", implementation.view_paginated_approved_inward_job_inward_items, inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewPaginatedUnapprovedInwardJobInwardItems", implementation.view_paginated_unapproved_inward_job_inward_items, inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/SearchInwardItemsWithPagination", implementation.search_inward_items_with_pagination, inward_jobs.scailo_pb2.InwardJobInwardItemsSearchRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/DownloadInwardItemsCSVTemplate", implementation.download_inward_items_csv_template, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/UploadInwardJobInwardItems", implementation.upload_inward_job_inward_items, base.scailo_pb2.IdentifierUUIDWithFile)
    app.register_unary_rpc("/Scailo.InwardJobsService/AddMultipleInwardJobOutwardItems", implementation.add_multiple_inward_job_outward_items, inward_jobs.scailo_pb2.InwardJobsServiceMultipleOutwardItemsCreateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/AddInwardJobOutwardItem", implementation.add_inward_job_outward_item, inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemCreateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/ModifyInwardJobOutwardItem", implementation.modify_inward_job_outward_item, inward_jobs.scailo_pb2.InwardJobsServiceOutwardItemUpdateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/ApproveInwardJobOutwardItem", implementation.approve_inward_job_outward_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/DeleteInwardJobOutwardItem", implementation.delete_inward_job_outward_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/ReorderInwardJobOutwardItems", implementation.reorder_inward_job_outward_items, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewInwardJobOutwardItemByID", implementation.view_inward_job_outward_item_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewApprovedInwardJobOutwardItems", implementation.view_approved_inward_job_outward_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewUnapprovedInwardJobOutwardItems", implementation.view_unapproved_inward_job_outward_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewInwardJobOutwardItemHistory", implementation.view_inward_job_outward_item_history, inward_jobs.scailo_pb2.InwardJobOutwardItemHistoryRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewPaginatedApprovedInwardJobOutwardItems", implementation.view_paginated_approved_inward_job_outward_items, inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewPaginatedUnapprovedInwardJobOutwardItems", implementation.view_paginated_unapproved_inward_job_outward_items, inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/SearchOutwardItemsWithPagination", implementation.search_outward_items_with_pagination, inward_jobs.scailo_pb2.InwardJobOutwardItemsSearchRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/DownloadOutwardItemsCSVTemplate", implementation.download_outward_items_csv_template, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/UploadInwardJobOutwardItems", implementation.upload_inward_job_outward_items, base.scailo_pb2.IdentifierUUIDWithFile)
    app.register_unary_rpc("/Scailo.InwardJobsService/AddInwardJobContact", implementation.add_inward_job_contact, inward_jobs.scailo_pb2.InwardJobsServiceContactCreateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/ApproveInwardJobContact", implementation.approve_inward_job_contact, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/DeleteInwardJobContact", implementation.delete_inward_job_contact, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewInwardJobContactByID", implementation.view_inward_job_contact_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewInwardJobContacts", implementation.view_inward_job_contacts, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewAncillaryParametersByUUID", implementation.view_ancillary_parameters_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewWithPagination", implementation.view_with_pagination, inward_jobs.scailo_pb2.InwardJobsServicePaginationReq)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewAssociatedSalesOrderIDs", implementation.view_associated_sales_order_i_ds, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewInwardInventoryMatch", implementation.view_inward_inventory_match, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewProspectiveInwardFamilies", implementation.view_prospective_inward_families, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.InwardJobsService/FilterProspectiveInwardFamilies", implementation.filter_prospective_inward_families, families.scailo_pb2.FilterFamiliesReqForIdentifier)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewProspectiveInwardJobInwardItem", implementation.view_prospective_inward_job_inward_item, inward_jobs.scailo_pb2.InwardJobInwardItemProspectiveInfoRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewOutwardInventoryMatch", implementation.view_outward_inventory_match, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewProspectiveOutwardFamilies", implementation.view_prospective_outward_families, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.InwardJobsService/FilterProspectiveOutwardFamilies", implementation.filter_prospective_outward_families, families.scailo_pb2.FilterFamiliesReqForIdentifier)
    app.register_unary_rpc("/Scailo.InwardJobsService/ViewProspectiveInwardJobOutwardItem", implementation.view_prospective_inward_job_outward_item, inward_jobs.scailo_pb2.InwardJobOutwardItemProspectiveInfoRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/IsDownloadable", implementation.is_downloadable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/DownloadByUUID", implementation.download_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsService/SearchAll", implementation.search_all, inward_jobs.scailo_pb2.InwardJobsServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.InwardJobsService/Filter", implementation.filter, inward_jobs.scailo_pb2.InwardJobsServiceFilterReq)
    app.register_unary_rpc("/Scailo.InwardJobsService/CountInStatus", implementation.count_in_status, base.scailo_pb2.CountInSLCStatusRequest)
    app.register_unary_rpc("/Scailo.InwardJobsService/Count", implementation.count, inward_jobs.scailo_pb2.InwardJobsServiceCountReq)
    app.register_unary_rpc("/Scailo.InwardJobsService/DownloadAsCSV", implementation.download_as_csv, inward_jobs.scailo_pb2.InwardJobsServiceFilterReq)
    return app
