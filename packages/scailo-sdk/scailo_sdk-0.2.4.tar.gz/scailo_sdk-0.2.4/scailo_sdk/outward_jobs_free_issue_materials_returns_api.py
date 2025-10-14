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

from scailo_sdk import base, families, inventory, magic_links, outward_jobs_free_issue_materials_returns

class OutwardJobsFreeIssueMaterialsReturnsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def create(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Draft"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DraftUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft_update(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SendForVerification"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Verify"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Approve"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SendForRevision"
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
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/RevisionUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def revision_update(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Halt"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Discard"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Restore"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Complete"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Repeat"
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

    def call_reopen(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Reopen, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Reopen"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/CommentAdd"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SendEmail"
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

    def call_create_magic_link(
        self, req: magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[magic_links.scailo_pb2.MagicLink]:
        """Low-level method to call CreateMagicLink, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/CreateMagicLink"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/IsCompletable"
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

    def call_add_outward_job_free_issue_material_return_item(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddOutwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/AddOutwardJobFreeIssueMaterialReturnItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_outward_job_free_issue_material_return_item(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_outward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_outward_job_free_issue_material_return_item(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyOutwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ModifyOutwardJobFreeIssueMaterialReturnItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_outward_job_free_issue_material_return_item(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_outward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_outward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveOutwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ApproveOutwardJobFreeIssueMaterialReturnItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_outward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_outward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_outward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteOutwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DeleteOutwardJobFreeIssueMaterialReturnItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_outward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_outward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_outward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderOutwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ReorderOutwardJobFreeIssueMaterialReturnItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_outward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_outward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_job_free_issue_material_return_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem]:
        """Low-level method to call ViewOutwardJobFreeIssueMaterialReturnItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewOutwardJobFreeIssueMaterialReturnItemByID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem,extra_headers, timeout_seconds)


    def view_outward_job_free_issue_material_return_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem:
        response = self.call_view_outward_job_free_issue_material_return_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_job_free_issue_material_return_item_by_inventory_hash(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem]:
        """Low-level method to call ViewOutwardJobFreeIssueMaterialReturnItemByInventoryHash, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewOutwardJobFreeIssueMaterialReturnItemByInventoryHash"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem,extra_headers, timeout_seconds)


    def view_outward_job_free_issue_material_return_item_by_inventory_hash(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem:
        response = self.call_view_outward_job_free_issue_material_return_item_by_inventory_hash(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_approved_outward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList]:
        """Low-level method to call ViewApprovedOutwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewApprovedOutwardJobFreeIssueMaterialReturnItems"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList,extra_headers, timeout_seconds)


    def view_approved_outward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList:
        response = self.call_view_approved_outward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_unapproved_outward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList]:
        """Low-level method to call ViewUnapprovedOutwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewUnapprovedOutwardJobFreeIssueMaterialReturnItems"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList,extra_headers, timeout_seconds)


    def view_unapproved_outward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList:
        response = self.call_view_unapproved_outward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_job_free_issue_material_return_item_history(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList]:
        """Low-level method to call ViewOutwardJobFreeIssueMaterialReturnItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewOutwardJobFreeIssueMaterialReturnItemHistory"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList,extra_headers, timeout_seconds)


    def view_outward_job_free_issue_material_return_item_history(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList:
        response = self.call_view_outward_job_free_issue_material_return_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_approved_outward_job_free_issue_material_return_items(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedOutwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewPaginatedApprovedOutwardJobFreeIssueMaterialReturnItems"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_approved_outward_job_free_issue_material_return_items(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse:
        response = self.call_view_paginated_approved_outward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_unapproved_outward_job_free_issue_material_return_items(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedOutwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewPaginatedUnapprovedOutwardJobFreeIssueMaterialReturnItems"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_unapproved_outward_job_free_issue_material_return_items(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse:
        response = self.call_view_paginated_unapproved_outward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_items_with_pagination(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SearchItemsWithPagination"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def search_items_with_pagination(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse:
        response = self.call_search_items_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_download_items_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadItemsAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadItemsAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_items_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_items_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_download_items_template_as_csv(
        self, req: base.scailo_pb2.Empty,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadItemsTemplateAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadItemsTemplateAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_items_template_as_csv(
        self, req: base.scailo_pb2.Empty,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_items_template_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewByID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewByUUID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn:
        response = self.call_view_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewByReferenceID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)


    def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn:
        response = self.call_view_by_reference_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewAncillaryParametersByUUID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnAncillaryParameters,extra_headers, timeout_seconds)


    def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnAncillaryParameters:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewAll"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginationResponse:
        response = self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_prospective_families(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call ViewProspectiveFamilies, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewProspectiveFamilies"
        return self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)


    def view_prospective_families(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = self.call_view_prospective_families(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter_prospective_families(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call FilterProspectiveFamilies, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/FilterProspectiveFamilies"
        return self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)


    def filter_prospective_families(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = self.call_filter_prospective_families(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_prospective_outward_job_free_issue_material_return_item(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveOutwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewProspectiveOutwardJobFreeIssueMaterialReturnItem"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest,extra_headers, timeout_seconds)


    def view_prospective_outward_job_free_issue_material_return_item(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest:
        response = self.call_view_prospective_outward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_returnable_inventory(
        self, req: inventory.scailo_pb2.SearchReturnableInventoryForIdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call SearchReturnableInventory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SearchReturnableInventory"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def search_returnable_inventory(
        self, req: inventory.scailo_pb2.SearchReturnableInventoryForIdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_search_returnable_inventory(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter_returnable_inventory(
        self, req: inventory.scailo_pb2.FilterReturnableInventoryForIdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call FilterReturnableInventory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/FilterReturnableInventory"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def filter_returnable_inventory(
        self, req: inventory.scailo_pb2.FilterReturnableInventoryForIdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_filter_returnable_inventory(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/IsDownloadable"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadByUUID"
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

    def call_download_label_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadLabelByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadLabelByUUID"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_label_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_label_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_added_family_quantity_for_source(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.DualQuantitiesResponse]:
        """Low-level method to call ViewAddedFamilyQuantityForSource, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewAddedFamilyQuantityForSource"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.DualQuantitiesResponse,extra_headers, timeout_seconds)


    def view_added_family_quantity_for_source(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.DualQuantitiesResponse:
        response = self.call_view_added_family_quantity_for_source(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_all(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SearchAll"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)


    def search_all(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Filter"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)


    def filter(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList:
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/CountInStatus"
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
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncOutwardJobsFreeIssueMaterialsReturnsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def create(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Draft"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DraftUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft_update(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SendForVerification"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Verify"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Approve"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SendForRevision"
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
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/RevisionUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def revision_update(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Halt"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Discard"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Restore"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Complete"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Repeat"
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

    async def call_reopen(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Reopen, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Reopen"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/CommentAdd"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SendEmail"
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

    async def call_create_magic_link(
        self, req: magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[magic_links.scailo_pb2.MagicLink]:
        """Low-level method to call CreateMagicLink, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/CreateMagicLink"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/IsCompletable"
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

    async def call_add_outward_job_free_issue_material_return_item(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddOutwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/AddOutwardJobFreeIssueMaterialReturnItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_outward_job_free_issue_material_return_item(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_outward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_outward_job_free_issue_material_return_item(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyOutwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ModifyOutwardJobFreeIssueMaterialReturnItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_outward_job_free_issue_material_return_item(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_outward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_outward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveOutwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ApproveOutwardJobFreeIssueMaterialReturnItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_outward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_outward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_outward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteOutwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DeleteOutwardJobFreeIssueMaterialReturnItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_outward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_outward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_outward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderOutwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ReorderOutwardJobFreeIssueMaterialReturnItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_outward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_outward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_job_free_issue_material_return_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem]:
        """Low-level method to call ViewOutwardJobFreeIssueMaterialReturnItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewOutwardJobFreeIssueMaterialReturnItemByID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem,extra_headers, timeout_seconds)

    async def view_outward_job_free_issue_material_return_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem:
        response = await self.call_view_outward_job_free_issue_material_return_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_job_free_issue_material_return_item_by_inventory_hash(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem]:
        """Low-level method to call ViewOutwardJobFreeIssueMaterialReturnItemByInventoryHash, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewOutwardJobFreeIssueMaterialReturnItemByInventoryHash"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem,extra_headers, timeout_seconds)

    async def view_outward_job_free_issue_material_return_item_by_inventory_hash(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem:
        response = await self.call_view_outward_job_free_issue_material_return_item_by_inventory_hash(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_approved_outward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList]:
        """Low-level method to call ViewApprovedOutwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewApprovedOutwardJobFreeIssueMaterialReturnItems"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList,extra_headers, timeout_seconds)

    async def view_approved_outward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList:
        response = await self.call_view_approved_outward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_unapproved_outward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList]:
        """Low-level method to call ViewUnapprovedOutwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewUnapprovedOutwardJobFreeIssueMaterialReturnItems"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList,extra_headers, timeout_seconds)

    async def view_unapproved_outward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList:
        response = await self.call_view_unapproved_outward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_job_free_issue_material_return_item_history(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList]:
        """Low-level method to call ViewOutwardJobFreeIssueMaterialReturnItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewOutwardJobFreeIssueMaterialReturnItemHistory"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList,extra_headers, timeout_seconds)

    async def view_outward_job_free_issue_material_return_item_history(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList:
        response = await self.call_view_outward_job_free_issue_material_return_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_approved_outward_job_free_issue_material_return_items(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedOutwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewPaginatedApprovedOutwardJobFreeIssueMaterialReturnItems"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_approved_outward_job_free_issue_material_return_items(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse:
        response = await self.call_view_paginated_approved_outward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_unapproved_outward_job_free_issue_material_return_items(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedOutwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewPaginatedUnapprovedOutwardJobFreeIssueMaterialReturnItems"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_unapproved_outward_job_free_issue_material_return_items(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse:
        response = await self.call_view_paginated_unapproved_outward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_items_with_pagination(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SearchItemsWithPagination"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def search_items_with_pagination(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse:
        response = await self.call_search_items_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_download_items_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadItemsAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadItemsAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_items_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_items_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_download_items_template_as_csv(
        self, req: base.scailo_pb2.Empty,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadItemsTemplateAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadItemsTemplateAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_items_template_as_csv(
        self, req: base.scailo_pb2.Empty,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_items_template_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewByID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn:
        response = await self.call_view_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewByReferenceID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)

    async def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn:
        response = await self.call_view_by_reference_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewAncillaryParametersByUUID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnAncillaryParameters,extra_headers, timeout_seconds)

    async def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnAncillaryParameters:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewAll"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginationResponse:
        response = await self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_prospective_families(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call ViewProspectiveFamilies, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewProspectiveFamilies"
        return await self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)

    async def view_prospective_families(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = await self.call_view_prospective_families(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter_prospective_families(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call FilterProspectiveFamilies, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/FilterProspectiveFamilies"
        return await self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)

    async def filter_prospective_families(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = await self.call_filter_prospective_families(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_prospective_outward_job_free_issue_material_return_item(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveOutwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewProspectiveOutwardJobFreeIssueMaterialReturnItem"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest,extra_headers, timeout_seconds)

    async def view_prospective_outward_job_free_issue_material_return_item(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest:
        response = await self.call_view_prospective_outward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_returnable_inventory(
        self, req: inventory.scailo_pb2.SearchReturnableInventoryForIdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call SearchReturnableInventory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SearchReturnableInventory"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def search_returnable_inventory(
        self, req: inventory.scailo_pb2.SearchReturnableInventoryForIdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_search_returnable_inventory(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter_returnable_inventory(
        self, req: inventory.scailo_pb2.FilterReturnableInventoryForIdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call FilterReturnableInventory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/FilterReturnableInventory"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def filter_returnable_inventory(
        self, req: inventory.scailo_pb2.FilterReturnableInventoryForIdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_filter_returnable_inventory(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/IsDownloadable"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadByUUID"
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

    async def call_download_label_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadLabelByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadLabelByUUID"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_label_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_label_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_added_family_quantity_for_source(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.DualQuantitiesResponse]:
        """Low-level method to call ViewAddedFamilyQuantityForSource, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewAddedFamilyQuantityForSource"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.DualQuantitiesResponse,extra_headers, timeout_seconds)

    async def view_added_family_quantity_for_source(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.DualQuantitiesResponse:
        response = await self.call_view_added_family_quantity_for_source(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_all(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SearchAll"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Filter"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList:
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/CountInStatus"
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
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
class OutwardJobsFreeIssueMaterialsReturnsServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft_update(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_verification(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def verify(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_revision(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def revision_update(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
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
    def reopen(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def comment_add(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_email(self, req: ClientRequest[base.scailo_pb2.IdentifierWithEmailAttributes]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def create_magic_link(self, req: ClientRequest[magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource]) -> ServerResponse[magic_links.scailo_pb2.MagicLink]:
        ...
    def is_completable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def add_outward_job_free_issue_material_return_item(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_outward_job_free_issue_material_return_item(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_outward_job_free_issue_material_return_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_outward_job_free_issue_material_return_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_outward_job_free_issue_material_return_items(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_outward_job_free_issue_material_return_item_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem]:
        ...
    def view_outward_job_free_issue_material_return_item_by_inventory_hash(self, req: ClientRequest[base.scailo_pb2.SimpleSearchReq]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItem]:
        ...
    def view_approved_outward_job_free_issue_material_return_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList]:
        ...
    def view_unapproved_outward_job_free_issue_material_return_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList]:
        ...
    def view_outward_job_free_issue_material_return_item_history(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemHistoryRequest]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsItemsList]:
        ...
    def view_paginated_approved_outward_job_free_issue_material_return_items(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        ...
    def view_paginated_unapproved_outward_job_free_issue_material_return_items(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        ...
    def search_items_with_pagination(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        ...
    def download_items_as_csv(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def download_items_template_as_csv(self, req: ClientRequest[base.scailo_pb2.Empty]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        ...
    def view_by_reference_id(self, req: ClientRequest[base.scailo_pb2.SimpleSearchReq]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturn]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        ...
    def view_ancillary_parameters_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnAncillaryParameters]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        ...
    def view_with_pagination(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginationReq]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginationResponse]:
        ...
    def view_prospective_families(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def filter_prospective_families(self, req: ClientRequest[families.scailo_pb2.FilterFamiliesReqForIdentifier]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def view_prospective_outward_job_free_issue_material_return_item(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemProspectiveInfoRequest]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest]:
        ...
    def search_returnable_inventory(self, req: ClientRequest[inventory.scailo_pb2.SearchReturnableInventoryForIdentifierUUID]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def filter_returnable_inventory(self, req: ClientRequest[inventory.scailo_pb2.FilterReturnableInventoryForIdentifierUUID]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def is_downloadable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def download_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def download_label_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def view_added_family_quantity_for_source(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceAlreadyAddedQuantityForSourceRequest]) -> ServerResponse[base.scailo_pb2.DualQuantitiesResponse]:
        ...
    def search_all(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceSearchAllReq]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        ...
    def filter(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceFilterReq]) -> ServerResponse[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsList]:
        ...
    def count_in_status(self, req: ClientRequest[base.scailo_pb2.CountInSLCStatusRequest]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def count(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

OUTWARD_JOBS_FREE_ISSUE_MATERIALS_RETURNS_SERVICE_PATH_PREFIX = "/Scailo.OutwardJobsFreeIssueMaterialsReturnsService"

def wsgi_outward_jobs_free_issue_materials_returns_service(implementation: OutwardJobsFreeIssueMaterialsReturnsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Create", implementation.create, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Draft", implementation.draft, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DraftUpdate", implementation.draft_update, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SendForVerification", implementation.send_for_verification, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Verify", implementation.verify, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Approve", implementation.approve, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SendForRevision", implementation.send_for_revision, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/RevisionUpdate", implementation.revision_update, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Halt", implementation.halt, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Discard", implementation.discard, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Restore", implementation.restore, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Repeat", implementation.repeat, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SendEmail", implementation.send_email, base.scailo_pb2.IdentifierWithEmailAttributes)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/CreateMagicLink", implementation.create_magic_link, magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/IsCompletable", implementation.is_completable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/AddOutwardJobFreeIssueMaterialReturnItem", implementation.add_outward_job_free_issue_material_return_item, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ModifyOutwardJobFreeIssueMaterialReturnItem", implementation.modify_outward_job_free_issue_material_return_item, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceItemUpdateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ApproveOutwardJobFreeIssueMaterialReturnItem", implementation.approve_outward_job_free_issue_material_return_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DeleteOutwardJobFreeIssueMaterialReturnItem", implementation.delete_outward_job_free_issue_material_return_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ReorderOutwardJobFreeIssueMaterialReturnItems", implementation.reorder_outward_job_free_issue_material_return_items, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewOutwardJobFreeIssueMaterialReturnItemByID", implementation.view_outward_job_free_issue_material_return_item_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewOutwardJobFreeIssueMaterialReturnItemByInventoryHash", implementation.view_outward_job_free_issue_material_return_item_by_inventory_hash, base.scailo_pb2.SimpleSearchReq)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewApprovedOutwardJobFreeIssueMaterialReturnItems", implementation.view_approved_outward_job_free_issue_material_return_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewUnapprovedOutwardJobFreeIssueMaterialReturnItems", implementation.view_unapproved_outward_job_free_issue_material_return_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewOutwardJobFreeIssueMaterialReturnItemHistory", implementation.view_outward_job_free_issue_material_return_item_history, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemHistoryRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewPaginatedApprovedOutwardJobFreeIssueMaterialReturnItems", implementation.view_paginated_approved_outward_job_free_issue_material_return_items, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewPaginatedUnapprovedOutwardJobFreeIssueMaterialReturnItems", implementation.view_paginated_unapproved_outward_job_free_issue_material_return_items, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SearchItemsWithPagination", implementation.search_items_with_pagination, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemsSearchRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadItemsAsCSV", implementation.download_items_as_csv, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadItemsTemplateAsCSV", implementation.download_items_template_as_csv, base.scailo_pb2.Empty)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewByReferenceID", implementation.view_by_reference_id, base.scailo_pb2.SimpleSearchReq)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewAncillaryParametersByUUID", implementation.view_ancillary_parameters_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewWithPagination", implementation.view_with_pagination, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServicePaginationReq)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewProspectiveFamilies", implementation.view_prospective_families, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/FilterProspectiveFamilies", implementation.filter_prospective_families, families.scailo_pb2.FilterFamiliesReqForIdentifier)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewProspectiveOutwardJobFreeIssueMaterialReturnItem", implementation.view_prospective_outward_job_free_issue_material_return_item, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobFreeIssueMaterialReturnItemProspectiveInfoRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SearchReturnableInventory", implementation.search_returnable_inventory, inventory.scailo_pb2.SearchReturnableInventoryForIdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/FilterReturnableInventory", implementation.filter_returnable_inventory, inventory.scailo_pb2.FilterReturnableInventoryForIdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/IsDownloadable", implementation.is_downloadable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadByUUID", implementation.download_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadLabelByUUID", implementation.download_label_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/ViewAddedFamilyQuantityForSource", implementation.view_added_family_quantity_for_source, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceAlreadyAddedQuantityForSourceRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/SearchAll", implementation.search_all, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Filter", implementation.filter, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceFilterReq)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/CountInStatus", implementation.count_in_status, base.scailo_pb2.CountInSLCStatusRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/Count", implementation.count, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceCountReq)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsReturnsService/DownloadAsCSV", implementation.download_as_csv, outward_jobs_free_issue_materials_returns.scailo_pb2.OutwardJobsFreeIssueMaterialsReturnsServiceFilterReq)
    return app
