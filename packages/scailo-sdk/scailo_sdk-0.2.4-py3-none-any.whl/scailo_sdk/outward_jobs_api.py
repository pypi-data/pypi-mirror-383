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

from scailo_sdk import base, families, magic_links, outward_jobs

class OutwardJobsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def create(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/Draft"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/DraftUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft_update(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsService/SendForVerification"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Verify"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Approve"
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
        url = self.base_url + "/Scailo.OutwardJobsService/SendForRevision"
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/RevisionUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def revision_update(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsService/Halt"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Discard"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Restore"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Complete"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Repeat"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Reopen"
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
        url = self.base_url + "/Scailo.OutwardJobsService/CommentAdd"
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
        url = self.base_url + "/Scailo.OutwardJobsService/SendEmail"
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/Autofill"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def autofill(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsService/CreateMagicLink"
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
        url = self.base_url + "/Scailo.OutwardJobsService/IsCompletable"
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
        url = self.base_url + "/Scailo.OutwardJobsService/IsOrdered"
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

    def call_is_dispatched(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call IsDispatched, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/IsDispatched"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)


    def is_dispatched(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = self.call_is_dispatched(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_multiple_outward_job_inward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceMultipleInwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddMultipleOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/AddMultipleOutwardJobInwardItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_multiple_outward_job_inward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceMultipleInwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_multiple_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_outward_job_inward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddOutwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/AddOutwardJobInwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_outward_job_inward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_outward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_outward_job_inward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyOutwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ModifyOutwardJobInwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_outward_job_inward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_outward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_outward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveOutwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ApproveOutwardJobInwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_outward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_outward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_outward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteOutwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/DeleteOutwardJobInwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_outward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_outward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_outward_job_inward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ReorderOutwardJobInwardItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_outward_job_inward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_job_inward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobInwardItem]:
        """Low-level method to call ViewOutwardJobInwardItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardJobInwardItemByID"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobInwardItem,extra_headers, timeout_seconds)


    def view_outward_job_inward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobInwardItem:
        response = self.call_view_outward_job_inward_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_approved_outward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsInwardItemsList]:
        """Low-level method to call ViewApprovedOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewApprovedOutwardJobInwardItems"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsInwardItemsList,extra_headers, timeout_seconds)


    def view_approved_outward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsInwardItemsList:
        response = self.call_view_approved_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_unapproved_outward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsInwardItemsList]:
        """Low-level method to call ViewUnapprovedOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewUnapprovedOutwardJobInwardItems"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsInwardItemsList,extra_headers, timeout_seconds)


    def view_unapproved_outward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsInwardItemsList:
        response = self.call_view_unapproved_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_job_inward_item_history(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsInwardItemsList]:
        """Low-level method to call ViewOutwardJobInwardItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardJobInwardItemHistory"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsInwardItemsList,extra_headers, timeout_seconds)


    def view_outward_job_inward_item_history(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsInwardItemsList:
        response = self.call_view_outward_job_inward_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_approved_outward_job_inward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewPaginatedApprovedOutwardJobInwardItems"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_approved_outward_job_inward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse:
        response = self.call_view_paginated_approved_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_unapproved_outward_job_inward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewPaginatedUnapprovedOutwardJobInwardItems"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_unapproved_outward_job_inward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse:
        response = self.call_view_paginated_unapproved_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_inward_items_with_pagination(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse]:
        """Low-level method to call SearchInwardItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/SearchInwardItemsWithPagination"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse,extra_headers, timeout_seconds)


    def search_inward_items_with_pagination(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse:
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
        url = self.base_url + "/Scailo.OutwardJobsService/DownloadInwardItemsCSVTemplate"
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

    def call_upload_outward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/UploadOutwardJobInwardItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def upload_outward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_upload_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_multiple_outward_job_outward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceMultipleOutwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddMultipleOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/AddMultipleOutwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_multiple_outward_job_outward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceMultipleOutwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_multiple_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_outward_job_outward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddOutwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/AddOutwardJobOutwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_outward_job_outward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_outward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_outward_job_outward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyOutwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ModifyOutwardJobOutwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_outward_job_outward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_outward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_outward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveOutwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ApproveOutwardJobOutwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_outward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_outward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_outward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteOutwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/DeleteOutwardJobOutwardItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_outward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_outward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_outward_job_outward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ReorderOutwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_outward_job_outward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_job_outward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobOutwardItem]:
        """Low-level method to call ViewOutwardJobOutwardItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardJobOutwardItemByID"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobOutwardItem,extra_headers, timeout_seconds)


    def view_outward_job_outward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobOutwardItem:
        response = self.call_view_outward_job_outward_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_approved_outward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList]:
        """Low-level method to call ViewApprovedOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewApprovedOutwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList,extra_headers, timeout_seconds)


    def view_approved_outward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList:
        response = self.call_view_approved_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_unapproved_outward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList]:
        """Low-level method to call ViewUnapprovedOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewUnapprovedOutwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList,extra_headers, timeout_seconds)


    def view_unapproved_outward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList:
        response = self.call_view_unapproved_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_job_outward_item_history(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList]:
        """Low-level method to call ViewOutwardJobOutwardItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardJobOutwardItemHistory"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList,extra_headers, timeout_seconds)


    def view_outward_job_outward_item_history(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList:
        response = self.call_view_outward_job_outward_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_approved_outward_job_outward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewPaginatedApprovedOutwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_approved_outward_job_outward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse:
        response = self.call_view_paginated_approved_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_unapproved_outward_job_outward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewPaginatedUnapprovedOutwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_unapproved_outward_job_outward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse:
        response = self.call_view_paginated_unapproved_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_outward_items_with_pagination(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse]:
        """Low-level method to call SearchOutwardItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/SearchOutwardItemsWithPagination"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse,extra_headers, timeout_seconds)


    def search_outward_items_with_pagination(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse:
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
        url = self.base_url + "/Scailo.OutwardJobsService/DownloadOutwardItemsCSVTemplate"
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

    def call_upload_outward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/UploadOutwardJobOutwardItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def upload_outward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_upload_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_outward_job_contact(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceContactCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddOutwardJobContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/AddOutwardJobContact"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_outward_job_contact(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceContactCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_outward_job_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_outward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveOutwardJobContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ApproveOutwardJobContact"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_outward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_outward_job_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_outward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteOutwardJobContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/DeleteOutwardJobContact"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_outward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_outward_job_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_job_contact_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobContact]:
        """Low-level method to call ViewOutwardJobContactByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardJobContactByID"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobContact,extra_headers, timeout_seconds)


    def view_outward_job_contact_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobContact:
        response = self.call_view_outward_job_contact_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_job_contacts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobContactsList]:
        """Low-level method to call ViewOutwardJobContacts, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardJobContacts"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobContactsList,extra_headers, timeout_seconds)


    def view_outward_job_contacts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobContactsList:
        response = self.call_view_outward_job_contacts(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJob]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewByID"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJob,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJob:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJob]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewByUUID"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJob,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJob:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJob]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJob,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJob:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJob]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJob,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJob:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsList:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewAncillaryParametersByUUID"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobAncillaryParameters,extra_headers, timeout_seconds)


    def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobAncillaryParameters:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewAll"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsList:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginationResponse:
        response = self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_associated_purchase_order_i_ds(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call ViewAssociatedPurchaseOrderIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewAssociatedPurchaseOrderIDs"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def view_associated_purchase_order_i_ds(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_view_associated_purchase_order_i_ds(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.OutwardJobsService/ViewProspectiveInwardFamilies"
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
        url = self.base_url + "/Scailo.OutwardJobsService/FilterProspectiveInwardFamilies"
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

    def call_view_prospective_outward_job_inward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemCreateRequest]:
        """Low-level method to call ViewProspectiveOutwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewProspectiveOutwardJobInwardItem"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemCreateRequest,extra_headers, timeout_seconds)


    def view_prospective_outward_job_inward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemCreateRequest:
        response = self.call_view_prospective_outward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_inward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobInwardInventoryMatchList]:
        """Low-level method to call ViewInwardInventoryMatch, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewInwardInventoryMatch"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobInwardInventoryMatchList,extra_headers, timeout_seconds)


    def view_inward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobInwardInventoryMatchList:
        response = self.call_view_inward_inventory_match(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.OutwardJobsService/ViewProspectiveOutwardFamilies"
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
        url = self.base_url + "/Scailo.OutwardJobsService/FilterProspectiveOutwardFamilies"
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

    def call_view_prospective_outward_job_outward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemCreateRequest]:
        """Low-level method to call ViewProspectiveOutwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewProspectiveOutwardJobOutwardItem"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemCreateRequest,extra_headers, timeout_seconds)


    def view_prospective_outward_job_outward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemCreateRequest:
        response = self.call_view_prospective_outward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobOutwardInventoryMatchList]:
        """Low-level method to call ViewOutwardInventoryMatch, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardInventoryMatch"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobOutwardInventoryMatchList,extra_headers, timeout_seconds)


    def view_outward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobOutwardInventoryMatchList:
        response = self.call_view_outward_inventory_match(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.OutwardJobsService/IsDownloadable"
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
        url = self.base_url + "/Scailo.OutwardJobsService/DownloadByUUID"
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/SearchAll"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsList,extra_headers, timeout_seconds)


    def search_all(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/Filter"
        return self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsList,extra_headers, timeout_seconds)


    def filter(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsList:
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
        url = self.base_url + "/Scailo.OutwardJobsService/CountInStatus"
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncOutwardJobsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def create(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/Draft"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/DraftUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft_update(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsService/SendForVerification"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Verify"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Approve"
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
        url = self.base_url + "/Scailo.OutwardJobsService/SendForRevision"
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/RevisionUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def revision_update(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsService/Halt"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Discard"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Restore"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Complete"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Repeat"
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
        url = self.base_url + "/Scailo.OutwardJobsService/Reopen"
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
        url = self.base_url + "/Scailo.OutwardJobsService/CommentAdd"
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
        url = self.base_url + "/Scailo.OutwardJobsService/SendEmail"
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/Autofill"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def autofill(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsService/CreateMagicLink"
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
        url = self.base_url + "/Scailo.OutwardJobsService/IsCompletable"
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
        url = self.base_url + "/Scailo.OutwardJobsService/IsOrdered"
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

    async def call_is_dispatched(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call IsDispatched, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/IsDispatched"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)

    async def is_dispatched(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = await self.call_is_dispatched(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_multiple_outward_job_inward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceMultipleInwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddMultipleOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/AddMultipleOutwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_multiple_outward_job_inward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceMultipleInwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_multiple_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_outward_job_inward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddOutwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/AddOutwardJobInwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_outward_job_inward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_outward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_outward_job_inward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyOutwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ModifyOutwardJobInwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_outward_job_inward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_outward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_outward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveOutwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ApproveOutwardJobInwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_outward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_outward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_outward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteOutwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/DeleteOutwardJobInwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_outward_job_inward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_outward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_outward_job_inward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ReorderOutwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_outward_job_inward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_job_inward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobInwardItem]:
        """Low-level method to call ViewOutwardJobInwardItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardJobInwardItemByID"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobInwardItem,extra_headers, timeout_seconds)

    async def view_outward_job_inward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobInwardItem:
        response = await self.call_view_outward_job_inward_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_approved_outward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsInwardItemsList]:
        """Low-level method to call ViewApprovedOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewApprovedOutwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsInwardItemsList,extra_headers, timeout_seconds)

    async def view_approved_outward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsInwardItemsList:
        response = await self.call_view_approved_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_unapproved_outward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsInwardItemsList]:
        """Low-level method to call ViewUnapprovedOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewUnapprovedOutwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsInwardItemsList,extra_headers, timeout_seconds)

    async def view_unapproved_outward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsInwardItemsList:
        response = await self.call_view_unapproved_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_job_inward_item_history(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsInwardItemsList]:
        """Low-level method to call ViewOutwardJobInwardItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardJobInwardItemHistory"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsInwardItemsList,extra_headers, timeout_seconds)

    async def view_outward_job_inward_item_history(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsInwardItemsList:
        response = await self.call_view_outward_job_inward_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_approved_outward_job_inward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewPaginatedApprovedOutwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_approved_outward_job_inward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse:
        response = await self.call_view_paginated_approved_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_unapproved_outward_job_inward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewPaginatedUnapprovedOutwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_unapproved_outward_job_inward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse:
        response = await self.call_view_paginated_unapproved_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_inward_items_with_pagination(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse]:
        """Low-level method to call SearchInwardItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/SearchInwardItemsWithPagination"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse,extra_headers, timeout_seconds)

    async def search_inward_items_with_pagination(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse:
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
        url = self.base_url + "/Scailo.OutwardJobsService/DownloadInwardItemsCSVTemplate"
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

    async def call_upload_outward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadOutwardJobInwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/UploadOutwardJobInwardItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def upload_outward_job_inward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_upload_outward_job_inward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_multiple_outward_job_outward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceMultipleOutwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddMultipleOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/AddMultipleOutwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_multiple_outward_job_outward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceMultipleOutwardItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_multiple_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_outward_job_outward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddOutwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/AddOutwardJobOutwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_outward_job_outward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_outward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_outward_job_outward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyOutwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ModifyOutwardJobOutwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_outward_job_outward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_outward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_outward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveOutwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ApproveOutwardJobOutwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_outward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_outward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_outward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteOutwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/DeleteOutwardJobOutwardItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_outward_job_outward_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_outward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_outward_job_outward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ReorderOutwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_outward_job_outward_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_job_outward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobOutwardItem]:
        """Low-level method to call ViewOutwardJobOutwardItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardJobOutwardItemByID"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobOutwardItem,extra_headers, timeout_seconds)

    async def view_outward_job_outward_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobOutwardItem:
        response = await self.call_view_outward_job_outward_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_approved_outward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList]:
        """Low-level method to call ViewApprovedOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewApprovedOutwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList,extra_headers, timeout_seconds)

    async def view_approved_outward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList:
        response = await self.call_view_approved_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_unapproved_outward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList]:
        """Low-level method to call ViewUnapprovedOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewUnapprovedOutwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList,extra_headers, timeout_seconds)

    async def view_unapproved_outward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList:
        response = await self.call_view_unapproved_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_job_outward_item_history(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList]:
        """Low-level method to call ViewOutwardJobOutwardItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardJobOutwardItemHistory"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList,extra_headers, timeout_seconds)

    async def view_outward_job_outward_item_history(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList:
        response = await self.call_view_outward_job_outward_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_approved_outward_job_outward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewPaginatedApprovedOutwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_approved_outward_job_outward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse:
        response = await self.call_view_paginated_approved_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_unapproved_outward_job_outward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewPaginatedUnapprovedOutwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_unapproved_outward_job_outward_items(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse:
        response = await self.call_view_paginated_unapproved_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_outward_items_with_pagination(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse]:
        """Low-level method to call SearchOutwardItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/SearchOutwardItemsWithPagination"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse,extra_headers, timeout_seconds)

    async def search_outward_items_with_pagination(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse:
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
        url = self.base_url + "/Scailo.OutwardJobsService/DownloadOutwardItemsCSVTemplate"
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

    async def call_upload_outward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadOutwardJobOutwardItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/UploadOutwardJobOutwardItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def upload_outward_job_outward_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_upload_outward_job_outward_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_outward_job_contact(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceContactCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddOutwardJobContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/AddOutwardJobContact"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_outward_job_contact(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceContactCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_outward_job_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_outward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveOutwardJobContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ApproveOutwardJobContact"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_outward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_outward_job_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_outward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteOutwardJobContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/DeleteOutwardJobContact"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_outward_job_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_outward_job_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_job_contact_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobContact]:
        """Low-level method to call ViewOutwardJobContactByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardJobContactByID"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobContact,extra_headers, timeout_seconds)

    async def view_outward_job_contact_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobContact:
        response = await self.call_view_outward_job_contact_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_job_contacts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobContactsList]:
        """Low-level method to call ViewOutwardJobContacts, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardJobContacts"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobContactsList,extra_headers, timeout_seconds)

    async def view_outward_job_contacts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobContactsList:
        response = await self.call_view_outward_job_contacts(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJob]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewByID"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJob,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJob:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJob]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJob,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJob:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJob]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJob,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJob:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJob]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJob,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJob:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsList:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewAncillaryParametersByUUID"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobAncillaryParameters,extra_headers, timeout_seconds)

    async def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobAncillaryParameters:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewAll"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsList:
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
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServicePaginationResponse:
        response = await self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_associated_purchase_order_i_ds(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call ViewAssociatedPurchaseOrderIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewAssociatedPurchaseOrderIDs"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def view_associated_purchase_order_i_ds(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_view_associated_purchase_order_i_ds(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.OutwardJobsService/ViewProspectiveInwardFamilies"
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
        url = self.base_url + "/Scailo.OutwardJobsService/FilterProspectiveInwardFamilies"
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

    async def call_view_prospective_outward_job_inward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemCreateRequest]:
        """Low-level method to call ViewProspectiveOutwardJobInwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewProspectiveOutwardJobInwardItem"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemCreateRequest,extra_headers, timeout_seconds)

    async def view_prospective_outward_job_inward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobInwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemCreateRequest:
        response = await self.call_view_prospective_outward_job_inward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_inward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobInwardInventoryMatchList]:
        """Low-level method to call ViewInwardInventoryMatch, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewInwardInventoryMatch"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobInwardInventoryMatchList,extra_headers, timeout_seconds)

    async def view_inward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobInwardInventoryMatchList:
        response = await self.call_view_inward_inventory_match(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.OutwardJobsService/ViewProspectiveOutwardFamilies"
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
        url = self.base_url + "/Scailo.OutwardJobsService/FilterProspectiveOutwardFamilies"
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

    async def call_view_prospective_outward_job_outward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemCreateRequest]:
        """Low-level method to call ViewProspectiveOutwardJobOutwardItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewProspectiveOutwardJobOutwardItem"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemCreateRequest,extra_headers, timeout_seconds)

    async def view_prospective_outward_job_outward_item(
        self, req: outward_jobs.scailo_pb2.OutwardJobOutwardItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemCreateRequest:
        response = await self.call_view_prospective_outward_job_outward_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobOutwardInventoryMatchList]:
        """Low-level method to call ViewOutwardInventoryMatch, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/ViewOutwardInventoryMatch"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobOutwardInventoryMatchList,extra_headers, timeout_seconds)

    async def view_outward_inventory_match(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobOutwardInventoryMatchList:
        response = await self.call_view_outward_inventory_match(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.OutwardJobsService/IsDownloadable"
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
        url = self.base_url + "/Scailo.OutwardJobsService/DownloadByUUID"
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/SearchAll"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs.scailo_pb2.OutwardJobsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/Filter"
        return await self._connect_client.call_unary(url, req, outward_jobs.scailo_pb2.OutwardJobsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs.scailo_pb2.OutwardJobsList:
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
        url = self.base_url + "/Scailo.OutwardJobsService/CountInStatus"
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: outward_jobs.scailo_pb2.OutwardJobsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
class OutwardJobsServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft_update(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_verification(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def verify(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_revision(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def revision_update(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
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
    def autofill(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceAutofillRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def create_magic_link(self, req: ClientRequest[magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource]) -> ServerResponse[magic_links.scailo_pb2.MagicLink]:
        ...
    def is_completable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def is_ordered(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def is_dispatched(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def add_multiple_outward_job_inward_items(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceMultipleInwardItemsCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_outward_job_inward_item(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_outward_job_inward_item(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_outward_job_inward_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_outward_job_inward_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_outward_job_inward_items(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_outward_job_inward_item_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobInwardItem]:
        ...
    def view_approved_outward_job_inward_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsInwardItemsList]:
        ...
    def view_unapproved_outward_job_inward_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsInwardItemsList]:
        ...
    def view_outward_job_inward_item_history(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobInwardItemHistoryRequest]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsInwardItemsList]:
        ...
    def view_paginated_approved_outward_job_inward_items(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse]:
        ...
    def view_paginated_unapproved_outward_job_inward_items(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse]:
        ...
    def search_inward_items_with_pagination(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedInwardItemsResponse]:
        ...
    def download_inward_items_csv_template(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def upload_outward_job_inward_items(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithFile]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def add_multiple_outward_job_outward_items(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceMultipleOutwardItemsCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_outward_job_outward_item(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_outward_job_outward_item(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_outward_job_outward_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_outward_job_outward_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_outward_job_outward_items(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_outward_job_outward_item_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobOutwardItem]:
        ...
    def view_approved_outward_job_outward_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList]:
        ...
    def view_unapproved_outward_job_outward_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList]:
        ...
    def view_outward_job_outward_item_history(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobOutwardItemHistoryRequest]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsOutwardItemsList]:
        ...
    def view_paginated_approved_outward_job_outward_items(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse]:
        ...
    def view_paginated_unapproved_outward_job_outward_items(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse]:
        ...
    def search_outward_items_with_pagination(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsServicePaginatedOutwardItemsResponse]:
        ...
    def download_outward_items_csv_template(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def upload_outward_job_outward_items(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithFile]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def add_outward_job_contact(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceContactCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_outward_job_contact(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_outward_job_contact(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_outward_job_contact_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobContact]:
        ...
    def view_outward_job_contacts(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobContactsList]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJob]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJob]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJob]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJob]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsList]:
        ...
    def view_ancillary_parameters_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobAncillaryParameters]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsList]:
        ...
    def view_with_pagination(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServicePaginationReq]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsServicePaginationResponse]:
        ...
    def view_associated_purchase_order_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def view_prospective_inward_families(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def filter_prospective_inward_families(self, req: ClientRequest[families.scailo_pb2.FilterFamiliesReqForIdentifier]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def view_prospective_outward_job_inward_item(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobInwardItemProspectiveInfoRequest]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemCreateRequest]:
        ...
    def view_inward_inventory_match(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobInwardInventoryMatchList]:
        ...
    def view_prospective_outward_families(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def filter_prospective_outward_families(self, req: ClientRequest[families.scailo_pb2.FilterFamiliesReqForIdentifier]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def view_prospective_outward_job_outward_item(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobOutwardItemProspectiveInfoRequest]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemCreateRequest]:
        ...
    def view_outward_inventory_match(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobOutwardInventoryMatchList]:
        ...
    def is_downloadable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def download_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def search_all(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceSearchAllReq]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsList]:
        ...
    def filter(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceFilterReq]) -> ServerResponse[outward_jobs.scailo_pb2.OutwardJobsList]:
        ...
    def count_in_status(self, req: ClientRequest[base.scailo_pb2.CountInSLCStatusRequest]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def count(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[outward_jobs.scailo_pb2.OutwardJobsServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

OUTWARD_JOBS_SERVICE_PATH_PREFIX = "/Scailo.OutwardJobsService"

def wsgi_outward_jobs_service(implementation: OutwardJobsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.OutwardJobsService/Create", implementation.create, outward_jobs.scailo_pb2.OutwardJobsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/Draft", implementation.draft, outward_jobs.scailo_pb2.OutwardJobsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/DraftUpdate", implementation.draft_update, outward_jobs.scailo_pb2.OutwardJobsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/SendForVerification", implementation.send_for_verification, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/Verify", implementation.verify, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/Approve", implementation.approve, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/SendForRevision", implementation.send_for_revision, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/RevisionUpdate", implementation.revision_update, outward_jobs.scailo_pb2.OutwardJobsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/Halt", implementation.halt, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/Discard", implementation.discard, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/Restore", implementation.restore, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/Repeat", implementation.repeat, base.scailo_pb2.RepeatWithDeliveryDate)
    app.register_unary_rpc("/Scailo.OutwardJobsService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/SendEmail", implementation.send_email, base.scailo_pb2.IdentifierWithEmailAttributes)
    app.register_unary_rpc("/Scailo.OutwardJobsService/Autofill", implementation.autofill, outward_jobs.scailo_pb2.OutwardJobsServiceAutofillRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/CreateMagicLink", implementation.create_magic_link, magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource)
    app.register_unary_rpc("/Scailo.OutwardJobsService/IsCompletable", implementation.is_completable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/IsOrdered", implementation.is_ordered, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/IsDispatched", implementation.is_dispatched, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/AddMultipleOutwardJobInwardItems", implementation.add_multiple_outward_job_inward_items, outward_jobs.scailo_pb2.OutwardJobsServiceMultipleInwardItemsCreateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/AddOutwardJobInwardItem", implementation.add_outward_job_inward_item, outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemCreateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ModifyOutwardJobInwardItem", implementation.modify_outward_job_inward_item, outward_jobs.scailo_pb2.OutwardJobsServiceInwardItemUpdateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ApproveOutwardJobInwardItem", implementation.approve_outward_job_inward_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/DeleteOutwardJobInwardItem", implementation.delete_outward_job_inward_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ReorderOutwardJobInwardItems", implementation.reorder_outward_job_inward_items, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewOutwardJobInwardItemByID", implementation.view_outward_job_inward_item_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewApprovedOutwardJobInwardItems", implementation.view_approved_outward_job_inward_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewUnapprovedOutwardJobInwardItems", implementation.view_unapproved_outward_job_inward_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewOutwardJobInwardItemHistory", implementation.view_outward_job_inward_item_history, outward_jobs.scailo_pb2.OutwardJobInwardItemHistoryRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewPaginatedApprovedOutwardJobInwardItems", implementation.view_paginated_approved_outward_job_inward_items, outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewPaginatedUnapprovedOutwardJobInwardItems", implementation.view_paginated_unapproved_outward_job_inward_items, outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/SearchInwardItemsWithPagination", implementation.search_inward_items_with_pagination, outward_jobs.scailo_pb2.OutwardJobInwardItemsSearchRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/DownloadInwardItemsCSVTemplate", implementation.download_inward_items_csv_template, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/UploadOutwardJobInwardItems", implementation.upload_outward_job_inward_items, base.scailo_pb2.IdentifierUUIDWithFile)
    app.register_unary_rpc("/Scailo.OutwardJobsService/AddMultipleOutwardJobOutwardItems", implementation.add_multiple_outward_job_outward_items, outward_jobs.scailo_pb2.OutwardJobsServiceMultipleOutwardItemsCreateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/AddOutwardJobOutwardItem", implementation.add_outward_job_outward_item, outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemCreateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ModifyOutwardJobOutwardItem", implementation.modify_outward_job_outward_item, outward_jobs.scailo_pb2.OutwardJobsServiceOutwardItemUpdateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ApproveOutwardJobOutwardItem", implementation.approve_outward_job_outward_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/DeleteOutwardJobOutwardItem", implementation.delete_outward_job_outward_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ReorderOutwardJobOutwardItems", implementation.reorder_outward_job_outward_items, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewOutwardJobOutwardItemByID", implementation.view_outward_job_outward_item_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewApprovedOutwardJobOutwardItems", implementation.view_approved_outward_job_outward_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewUnapprovedOutwardJobOutwardItems", implementation.view_unapproved_outward_job_outward_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewOutwardJobOutwardItemHistory", implementation.view_outward_job_outward_item_history, outward_jobs.scailo_pb2.OutwardJobOutwardItemHistoryRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewPaginatedApprovedOutwardJobOutwardItems", implementation.view_paginated_approved_outward_job_outward_items, outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewPaginatedUnapprovedOutwardJobOutwardItems", implementation.view_paginated_unapproved_outward_job_outward_items, outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/SearchOutwardItemsWithPagination", implementation.search_outward_items_with_pagination, outward_jobs.scailo_pb2.OutwardJobOutwardItemsSearchRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/DownloadOutwardItemsCSVTemplate", implementation.download_outward_items_csv_template, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/UploadOutwardJobOutwardItems", implementation.upload_outward_job_outward_items, base.scailo_pb2.IdentifierUUIDWithFile)
    app.register_unary_rpc("/Scailo.OutwardJobsService/AddOutwardJobContact", implementation.add_outward_job_contact, outward_jobs.scailo_pb2.OutwardJobsServiceContactCreateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ApproveOutwardJobContact", implementation.approve_outward_job_contact, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/DeleteOutwardJobContact", implementation.delete_outward_job_contact, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewOutwardJobContactByID", implementation.view_outward_job_contact_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewOutwardJobContacts", implementation.view_outward_job_contacts, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewAncillaryParametersByUUID", implementation.view_ancillary_parameters_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewWithPagination", implementation.view_with_pagination, outward_jobs.scailo_pb2.OutwardJobsServicePaginationReq)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewAssociatedPurchaseOrderIDs", implementation.view_associated_purchase_order_i_ds, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewProspectiveInwardFamilies", implementation.view_prospective_inward_families, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.OutwardJobsService/FilterProspectiveInwardFamilies", implementation.filter_prospective_inward_families, families.scailo_pb2.FilterFamiliesReqForIdentifier)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewProspectiveOutwardJobInwardItem", implementation.view_prospective_outward_job_inward_item, outward_jobs.scailo_pb2.OutwardJobInwardItemProspectiveInfoRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewInwardInventoryMatch", implementation.view_inward_inventory_match, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewProspectiveOutwardFamilies", implementation.view_prospective_outward_families, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.OutwardJobsService/FilterProspectiveOutwardFamilies", implementation.filter_prospective_outward_families, families.scailo_pb2.FilterFamiliesReqForIdentifier)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewProspectiveOutwardJobOutwardItem", implementation.view_prospective_outward_job_outward_item, outward_jobs.scailo_pb2.OutwardJobOutwardItemProspectiveInfoRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/ViewOutwardInventoryMatch", implementation.view_outward_inventory_match, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/IsDownloadable", implementation.is_downloadable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/DownloadByUUID", implementation.download_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsService/SearchAll", implementation.search_all, outward_jobs.scailo_pb2.OutwardJobsServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.OutwardJobsService/Filter", implementation.filter, outward_jobs.scailo_pb2.OutwardJobsServiceFilterReq)
    app.register_unary_rpc("/Scailo.OutwardJobsService/CountInStatus", implementation.count_in_status, base.scailo_pb2.CountInSLCStatusRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsService/Count", implementation.count, outward_jobs.scailo_pb2.OutwardJobsServiceCountReq)
    app.register_unary_rpc("/Scailo.OutwardJobsService/DownloadAsCSV", implementation.download_as_csv, outward_jobs.scailo_pb2.OutwardJobsServiceFilterReq)
    return app
