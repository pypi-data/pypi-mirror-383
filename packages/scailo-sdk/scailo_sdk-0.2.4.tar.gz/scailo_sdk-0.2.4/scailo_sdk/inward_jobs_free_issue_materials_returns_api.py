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

from scailo_sdk import base, families, inventory, inward_jobs_free_issue_materials_returns, magic_links

class InwardJobsFreeIssueMaterialsReturnsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def create(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Draft"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DraftUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft_update(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SendForVerification"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Verify"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Approve"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SendForRevision"
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/RevisionUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def revision_update(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Halt"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Discard"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Restore"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Complete"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Repeat"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Reopen"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/CommentAdd"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SendEmail"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/CreateMagicLink"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/IsCompletable"
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

    def call_add_inward_job_free_issue_material_return_item(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/AddInwardJobFreeIssueMaterialReturnItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_inward_job_free_issue_material_return_item(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_inward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_inward_job_free_issue_material_return_item(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyInwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ModifyInwardJobFreeIssueMaterialReturnItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_inward_job_free_issue_material_return_item(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_inward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_inward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveInwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ApproveInwardJobFreeIssueMaterialReturnItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_inward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_inward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_inward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteInwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DeleteInwardJobFreeIssueMaterialReturnItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_inward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_inward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_inward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderInwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ReorderInwardJobFreeIssueMaterialReturnItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_inward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_inward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_inward_job_free_issue_material_return_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem]:
        """Low-level method to call ViewInwardJobFreeIssueMaterialReturnItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewInwardJobFreeIssueMaterialReturnItemByID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem,extra_headers, timeout_seconds)


    def view_inward_job_free_issue_material_return_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem:
        response = self.call_view_inward_job_free_issue_material_return_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_inward_job_free_issue_material_return_item_by_inventory_hash(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem]:
        """Low-level method to call ViewInwardJobFreeIssueMaterialReturnItemByInventoryHash, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewInwardJobFreeIssueMaterialReturnItemByInventoryHash"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem,extra_headers, timeout_seconds)


    def view_inward_job_free_issue_material_return_item_by_inventory_hash(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem:
        response = self.call_view_inward_job_free_issue_material_return_item_by_inventory_hash(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_approved_inward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList]:
        """Low-level method to call ViewApprovedInwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewApprovedInwardJobFreeIssueMaterialReturnItems"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList,extra_headers, timeout_seconds)


    def view_approved_inward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList:
        response = self.call_view_approved_inward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_unapproved_inward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList]:
        """Low-level method to call ViewUnapprovedInwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewUnapprovedInwardJobFreeIssueMaterialReturnItems"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList,extra_headers, timeout_seconds)


    def view_unapproved_inward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList:
        response = self.call_view_unapproved_inward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_inward_job_free_issue_material_return_item_history(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList]:
        """Low-level method to call ViewInwardJobFreeIssueMaterialReturnItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewInwardJobFreeIssueMaterialReturnItemHistory"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList,extra_headers, timeout_seconds)


    def view_inward_job_free_issue_material_return_item_history(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList:
        response = self.call_view_inward_job_free_issue_material_return_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_approved_inward_job_free_issue_material_return_items(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedInwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewPaginatedApprovedInwardJobFreeIssueMaterialReturnItems"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_approved_inward_job_free_issue_material_return_items(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse:
        response = self.call_view_paginated_approved_inward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_unapproved_inward_job_free_issue_material_return_items(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedInwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewPaginatedUnapprovedInwardJobFreeIssueMaterialReturnItems"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_unapproved_inward_job_free_issue_material_return_items(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse:
        response = self.call_view_paginated_unapproved_inward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_items_with_pagination(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SearchItemsWithPagination"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def search_items_with_pagination(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadItemsTemplateAsCSV"
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewByID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewByUUID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewByReferenceID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)


    def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewAncillaryParametersByUUID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnAncillaryParameters,extra_headers, timeout_seconds)


    def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnAncillaryParameters:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewAll"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginationResponse:
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewProspectiveFamilies"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/FilterProspectiveFamilies"
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

    def call_view_prospective_inward_job_free_issue_material_return_item(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveInwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewProspectiveInwardJobFreeIssueMaterialReturnItem"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest,extra_headers, timeout_seconds)


    def view_prospective_inward_job_free_issue_material_return_item(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest:
        response = self.call_view_prospective_inward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SearchReturnableInventory"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/FilterReturnableInventory"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/IsDownloadable"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadByUUID"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadLabelByUUID"
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.DualQuantitiesResponse]:
        """Low-level method to call ViewAddedFamilyQuantityForSource, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewAddedFamilyQuantityForSource"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.DualQuantitiesResponse,extra_headers, timeout_seconds)


    def view_added_family_quantity_for_source(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SearchAll"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)


    def search_all(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Filter"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)


    def filter(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList:
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/CountInStatus"
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncInwardJobsFreeIssueMaterialsReturnsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def create(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Draft"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DraftUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft_update(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SendForVerification"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Verify"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Approve"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SendForRevision"
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/RevisionUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def revision_update(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Halt"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Discard"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Restore"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Complete"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Repeat"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Reopen"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/CommentAdd"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SendEmail"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/CreateMagicLink"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/IsCompletable"
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

    async def call_add_inward_job_free_issue_material_return_item(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/AddInwardJobFreeIssueMaterialReturnItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_inward_job_free_issue_material_return_item(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_inward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_inward_job_free_issue_material_return_item(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyInwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ModifyInwardJobFreeIssueMaterialReturnItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_inward_job_free_issue_material_return_item(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_inward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_inward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveInwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ApproveInwardJobFreeIssueMaterialReturnItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_inward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_inward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_inward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteInwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DeleteInwardJobFreeIssueMaterialReturnItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_inward_job_free_issue_material_return_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_inward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_inward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderInwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ReorderInwardJobFreeIssueMaterialReturnItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_inward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_inward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_inward_job_free_issue_material_return_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem]:
        """Low-level method to call ViewInwardJobFreeIssueMaterialReturnItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewInwardJobFreeIssueMaterialReturnItemByID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem,extra_headers, timeout_seconds)

    async def view_inward_job_free_issue_material_return_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem:
        response = await self.call_view_inward_job_free_issue_material_return_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_inward_job_free_issue_material_return_item_by_inventory_hash(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem]:
        """Low-level method to call ViewInwardJobFreeIssueMaterialReturnItemByInventoryHash, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewInwardJobFreeIssueMaterialReturnItemByInventoryHash"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem,extra_headers, timeout_seconds)

    async def view_inward_job_free_issue_material_return_item_by_inventory_hash(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem:
        response = await self.call_view_inward_job_free_issue_material_return_item_by_inventory_hash(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_approved_inward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList]:
        """Low-level method to call ViewApprovedInwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewApprovedInwardJobFreeIssueMaterialReturnItems"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList,extra_headers, timeout_seconds)

    async def view_approved_inward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList:
        response = await self.call_view_approved_inward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_unapproved_inward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList]:
        """Low-level method to call ViewUnapprovedInwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewUnapprovedInwardJobFreeIssueMaterialReturnItems"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList,extra_headers, timeout_seconds)

    async def view_unapproved_inward_job_free_issue_material_return_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList:
        response = await self.call_view_unapproved_inward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_inward_job_free_issue_material_return_item_history(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList]:
        """Low-level method to call ViewInwardJobFreeIssueMaterialReturnItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewInwardJobFreeIssueMaterialReturnItemHistory"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList,extra_headers, timeout_seconds)

    async def view_inward_job_free_issue_material_return_item_history(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList:
        response = await self.call_view_inward_job_free_issue_material_return_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_approved_inward_job_free_issue_material_return_items(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedInwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewPaginatedApprovedInwardJobFreeIssueMaterialReturnItems"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_approved_inward_job_free_issue_material_return_items(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse:
        response = await self.call_view_paginated_approved_inward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_unapproved_inward_job_free_issue_material_return_items(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedInwardJobFreeIssueMaterialReturnItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewPaginatedUnapprovedInwardJobFreeIssueMaterialReturnItems"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_unapproved_inward_job_free_issue_material_return_items(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse:
        response = await self.call_view_paginated_unapproved_inward_job_free_issue_material_return_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_items_with_pagination(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SearchItemsWithPagination"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def search_items_with_pagination(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadItemsTemplateAsCSV"
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewByID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewByReferenceID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)

    async def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewAncillaryParametersByUUID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnAncillaryParameters,extra_headers, timeout_seconds)

    async def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnAncillaryParameters:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewAll"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginationResponse:
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewProspectiveFamilies"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/FilterProspectiveFamilies"
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

    async def call_view_prospective_inward_job_free_issue_material_return_item(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveInwardJobFreeIssueMaterialReturnItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewProspectiveInwardJobFreeIssueMaterialReturnItem"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest,extra_headers, timeout_seconds)

    async def view_prospective_inward_job_free_issue_material_return_item(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest:
        response = await self.call_view_prospective_inward_job_free_issue_material_return_item(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SearchReturnableInventory"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/FilterReturnableInventory"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/IsDownloadable"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadByUUID"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadLabelByUUID"
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.DualQuantitiesResponse]:
        """Low-level method to call ViewAddedFamilyQuantityForSource, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewAddedFamilyQuantityForSource"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.DualQuantitiesResponse,extra_headers, timeout_seconds)

    async def view_added_family_quantity_for_source(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SearchAll"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Filter"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList:
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/CountInStatus"
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
class InwardJobsFreeIssueMaterialsReturnsServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft_update(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_verification(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def verify(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_revision(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def revision_update(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
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
    def add_inward_job_free_issue_material_return_item(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_inward_job_free_issue_material_return_item(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_inward_job_free_issue_material_return_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_inward_job_free_issue_material_return_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_inward_job_free_issue_material_return_items(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_inward_job_free_issue_material_return_item_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem]:
        ...
    def view_inward_job_free_issue_material_return_item_by_inventory_hash(self, req: ClientRequest[base.scailo_pb2.SimpleSearchReq]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItem]:
        ...
    def view_approved_inward_job_free_issue_material_return_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList]:
        ...
    def view_unapproved_inward_job_free_issue_material_return_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList]:
        ...
    def view_inward_job_free_issue_material_return_item_history(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemHistoryRequest]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsItemsList]:
        ...
    def view_paginated_approved_inward_job_free_issue_material_return_items(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        ...
    def view_paginated_unapproved_inward_job_free_issue_material_return_items(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        ...
    def search_items_with_pagination(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginatedItemsResponse]:
        ...
    def download_items_as_csv(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def download_items_template_as_csv(self, req: ClientRequest[base.scailo_pb2.Empty]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        ...
    def view_by_reference_id(self, req: ClientRequest[base.scailo_pb2.SimpleSearchReq]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturn]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        ...
    def view_ancillary_parameters_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnAncillaryParameters]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        ...
    def view_with_pagination(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginationReq]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginationResponse]:
        ...
    def view_prospective_families(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def filter_prospective_families(self, req: ClientRequest[families.scailo_pb2.FilterFamiliesReqForIdentifier]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def view_prospective_inward_job_free_issue_material_return_item(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemProspectiveInfoRequest]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest]:
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
    def view_added_family_quantity_for_source(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceAlreadyAddedQuantityForSourceRequest]) -> ServerResponse[base.scailo_pb2.DualQuantitiesResponse]:
        ...
    def search_all(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceSearchAllReq]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        ...
    def filter(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceFilterReq]) -> ServerResponse[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsList]:
        ...
    def count_in_status(self, req: ClientRequest[base.scailo_pb2.CountInSLCStatusRequest]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def count(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

INWARD_JOBS_FREE_ISSUE_MATERIALS_RETURNS_SERVICE_PATH_PREFIX = "/Scailo.InwardJobsFreeIssueMaterialsReturnsService"

def wsgi_inward_jobs_free_issue_materials_returns_service(implementation: InwardJobsFreeIssueMaterialsReturnsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Create", implementation.create, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Draft", implementation.draft, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DraftUpdate", implementation.draft_update, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SendForVerification", implementation.send_for_verification, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Verify", implementation.verify, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Approve", implementation.approve, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SendForRevision", implementation.send_for_revision, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/RevisionUpdate", implementation.revision_update, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Halt", implementation.halt, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Discard", implementation.discard, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Restore", implementation.restore, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Repeat", implementation.repeat, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SendEmail", implementation.send_email, base.scailo_pb2.IdentifierWithEmailAttributes)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/CreateMagicLink", implementation.create_magic_link, magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/IsCompletable", implementation.is_completable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/AddInwardJobFreeIssueMaterialReturnItem", implementation.add_inward_job_free_issue_material_return_item, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemCreateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ModifyInwardJobFreeIssueMaterialReturnItem", implementation.modify_inward_job_free_issue_material_return_item, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceItemUpdateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ApproveInwardJobFreeIssueMaterialReturnItem", implementation.approve_inward_job_free_issue_material_return_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DeleteInwardJobFreeIssueMaterialReturnItem", implementation.delete_inward_job_free_issue_material_return_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ReorderInwardJobFreeIssueMaterialReturnItems", implementation.reorder_inward_job_free_issue_material_return_items, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewInwardJobFreeIssueMaterialReturnItemByID", implementation.view_inward_job_free_issue_material_return_item_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewInwardJobFreeIssueMaterialReturnItemByInventoryHash", implementation.view_inward_job_free_issue_material_return_item_by_inventory_hash, base.scailo_pb2.SimpleSearchReq)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewApprovedInwardJobFreeIssueMaterialReturnItems", implementation.view_approved_inward_job_free_issue_material_return_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewUnapprovedInwardJobFreeIssueMaterialReturnItems", implementation.view_unapproved_inward_job_free_issue_material_return_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewInwardJobFreeIssueMaterialReturnItemHistory", implementation.view_inward_job_free_issue_material_return_item_history, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemHistoryRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewPaginatedApprovedInwardJobFreeIssueMaterialReturnItems", implementation.view_paginated_approved_inward_job_free_issue_material_return_items, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewPaginatedUnapprovedInwardJobFreeIssueMaterialReturnItems", implementation.view_paginated_unapproved_inward_job_free_issue_material_return_items, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SearchItemsWithPagination", implementation.search_items_with_pagination, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemsSearchRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadItemsAsCSV", implementation.download_items_as_csv, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadItemsTemplateAsCSV", implementation.download_items_template_as_csv, base.scailo_pb2.Empty)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewByReferenceID", implementation.view_by_reference_id, base.scailo_pb2.SimpleSearchReq)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewAncillaryParametersByUUID", implementation.view_ancillary_parameters_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewWithPagination", implementation.view_with_pagination, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServicePaginationReq)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewProspectiveFamilies", implementation.view_prospective_families, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/FilterProspectiveFamilies", implementation.filter_prospective_families, families.scailo_pb2.FilterFamiliesReqForIdentifier)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewProspectiveInwardJobFreeIssueMaterialReturnItem", implementation.view_prospective_inward_job_free_issue_material_return_item, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobFreeIssueMaterialReturnItemProspectiveInfoRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SearchReturnableInventory", implementation.search_returnable_inventory, inventory.scailo_pb2.SearchReturnableInventoryForIdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/FilterReturnableInventory", implementation.filter_returnable_inventory, inventory.scailo_pb2.FilterReturnableInventoryForIdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/IsDownloadable", implementation.is_downloadable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadByUUID", implementation.download_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadLabelByUUID", implementation.download_label_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/ViewAddedFamilyQuantityForSource", implementation.view_added_family_quantity_for_source, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceAlreadyAddedQuantityForSourceRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/SearchAll", implementation.search_all, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Filter", implementation.filter, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceFilterReq)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/CountInStatus", implementation.count_in_status, base.scailo_pb2.CountInSLCStatusRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/Count", implementation.count, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceCountReq)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsReturnsService/DownloadAsCSV", implementation.download_as_csv, inward_jobs_free_issue_materials_returns.scailo_pb2.InwardJobsFreeIssueMaterialsReturnsServiceFilterReq)
    return app
