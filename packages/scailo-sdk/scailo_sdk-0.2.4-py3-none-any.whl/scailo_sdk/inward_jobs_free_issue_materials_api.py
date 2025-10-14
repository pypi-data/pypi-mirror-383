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

from scailo_sdk import base, families, inward_jobs_free_issue_materials, magic_links

class InwardJobsFreeIssueMaterialsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def create(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Draft"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DraftUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft_update(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/SendForVerification"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Verify"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Approve"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/SendForRevision"
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/RevisionUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def revision_update(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Halt"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Discard"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Restore"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Complete"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Repeat"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Reopen"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/CommentAdd"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/SendEmail"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/CreateMagicLink"
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

    def call_autofill(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Autofill"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def autofill(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_autofill(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/IsCompletable"
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

    def call_add_inward_job_free_issue_material_item(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/AddInwardJobFreeIssueMaterialItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_inward_job_free_issue_material_item(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_inward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_inward_job_free_issue_material_item(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyInwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ModifyInwardJobFreeIssueMaterialItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_inward_job_free_issue_material_item(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_inward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_inward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveInwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ApproveInwardJobFreeIssueMaterialItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_inward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_inward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_inward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteInwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DeleteInwardJobFreeIssueMaterialItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_inward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_inward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_inward_job_free_issue_material_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderInwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ReorderInwardJobFreeIssueMaterialItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_inward_job_free_issue_material_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_inward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_inward_job_free_issue_material_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItem]:
        """Low-level method to call ViewInwardJobFreeIssueMaterialItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewInwardJobFreeIssueMaterialItemByID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItem,extra_headers, timeout_seconds)


    def view_inward_job_free_issue_material_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItem:
        response = self.call_view_inward_job_free_issue_material_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_approved_inward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList]:
        """Low-level method to call ViewApprovedInwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewApprovedInwardJobFreeIssueMaterialItems"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList,extra_headers, timeout_seconds)


    def view_approved_inward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList:
        response = self.call_view_approved_inward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_unapproved_inward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList]:
        """Low-level method to call ViewUnapprovedInwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewUnapprovedInwardJobFreeIssueMaterialItems"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList,extra_headers, timeout_seconds)


    def view_unapproved_inward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList:
        response = self.call_view_unapproved_inward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_inward_job_free_issue_material_item_history(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList]:
        """Low-level method to call ViewInwardJobFreeIssueMaterialItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewInwardJobFreeIssueMaterialItemHistory"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList,extra_headers, timeout_seconds)


    def view_inward_job_free_issue_material_item_history(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList:
        response = self.call_view_inward_job_free_issue_material_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_approved_inward_job_free_issue_material_items(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedInwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewPaginatedApprovedInwardJobFreeIssueMaterialItems"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_approved_inward_job_free_issue_material_items(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse:
        response = self.call_view_paginated_approved_inward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_unapproved_inward_job_free_issue_material_items(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedInwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewPaginatedUnapprovedInwardJobFreeIssueMaterialItems"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_unapproved_inward_job_free_issue_material_items(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse:
        response = self.call_view_paginated_unapproved_inward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_items_with_pagination(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/SearchItemsWithPagination"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def search_items_with_pagination(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DownloadItemsTemplateAsCSV"
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewByID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewByUUID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewByReferenceID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial,extra_headers, timeout_seconds)


    def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewAncillaryParametersByUUID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialAncillaryParameters,extra_headers, timeout_seconds)


    def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialAncillaryParameters:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewAll"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginationResponse:
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewProspectiveFamilies"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/FilterProspectiveFamilies"
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

    def call_view_prospective_inward_job_free_issue_material_item(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveInwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewProspectiveInwardJobFreeIssueMaterialItem"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemCreateRequest,extra_headers, timeout_seconds)


    def view_prospective_inward_job_free_issue_material_item(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemCreateRequest:
        response = self.call_view_prospective_inward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/IsDownloadable"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DownloadByUUID"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DownloadLabelByUUID"
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.DualQuantitiesResponse]:
        """Low-level method to call ViewAddedFamilyQuantityForSource, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewAddedFamilyQuantityForSource"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.DualQuantitiesResponse,extra_headers, timeout_seconds)


    def view_added_family_quantity_for_source(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/SearchAll"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)


    def search_all(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Filter"
        return self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)


    def filter(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList:
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/CountInStatus"
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncInwardJobsFreeIssueMaterialsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def create(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Draft"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DraftUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft_update(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/SendForVerification"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Verify"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Approve"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/SendForRevision"
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/RevisionUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def revision_update(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Halt"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Discard"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Restore"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Complete"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Repeat"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Reopen"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/CommentAdd"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/SendEmail"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/CreateMagicLink"
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

    async def call_autofill(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Autofill"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def autofill(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_autofill(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/IsCompletable"
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

    async def call_add_inward_job_free_issue_material_item(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/AddInwardJobFreeIssueMaterialItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_inward_job_free_issue_material_item(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_inward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_inward_job_free_issue_material_item(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyInwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ModifyInwardJobFreeIssueMaterialItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_inward_job_free_issue_material_item(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_inward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_inward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveInwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ApproveInwardJobFreeIssueMaterialItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_inward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_inward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_inward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteInwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DeleteInwardJobFreeIssueMaterialItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_inward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_inward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_inward_job_free_issue_material_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderInwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ReorderInwardJobFreeIssueMaterialItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_inward_job_free_issue_material_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_inward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_inward_job_free_issue_material_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItem]:
        """Low-level method to call ViewInwardJobFreeIssueMaterialItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewInwardJobFreeIssueMaterialItemByID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItem,extra_headers, timeout_seconds)

    async def view_inward_job_free_issue_material_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItem:
        response = await self.call_view_inward_job_free_issue_material_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_approved_inward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList]:
        """Low-level method to call ViewApprovedInwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewApprovedInwardJobFreeIssueMaterialItems"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList,extra_headers, timeout_seconds)

    async def view_approved_inward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList:
        response = await self.call_view_approved_inward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_unapproved_inward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList]:
        """Low-level method to call ViewUnapprovedInwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewUnapprovedInwardJobFreeIssueMaterialItems"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList,extra_headers, timeout_seconds)

    async def view_unapproved_inward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList:
        response = await self.call_view_unapproved_inward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_inward_job_free_issue_material_item_history(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList]:
        """Low-level method to call ViewInwardJobFreeIssueMaterialItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewInwardJobFreeIssueMaterialItemHistory"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList,extra_headers, timeout_seconds)

    async def view_inward_job_free_issue_material_item_history(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList:
        response = await self.call_view_inward_job_free_issue_material_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_approved_inward_job_free_issue_material_items(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedInwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewPaginatedApprovedInwardJobFreeIssueMaterialItems"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_approved_inward_job_free_issue_material_items(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse:
        response = await self.call_view_paginated_approved_inward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_unapproved_inward_job_free_issue_material_items(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedInwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewPaginatedUnapprovedInwardJobFreeIssueMaterialItems"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_unapproved_inward_job_free_issue_material_items(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse:
        response = await self.call_view_paginated_unapproved_inward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_items_with_pagination(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/SearchItemsWithPagination"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def search_items_with_pagination(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DownloadItemsTemplateAsCSV"
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewByID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewByReferenceID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial,extra_headers, timeout_seconds)

    async def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewAncillaryParametersByUUID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialAncillaryParameters,extra_headers, timeout_seconds)

    async def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialAncillaryParameters:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewAll"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList:
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
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginationResponse:
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewProspectiveFamilies"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/FilterProspectiveFamilies"
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

    async def call_view_prospective_inward_job_free_issue_material_item(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveInwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewProspectiveInwardJobFreeIssueMaterialItem"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemCreateRequest,extra_headers, timeout_seconds)

    async def view_prospective_inward_job_free_issue_material_item(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemCreateRequest:
        response = await self.call_view_prospective_inward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/IsDownloadable"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DownloadByUUID"
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DownloadLabelByUUID"
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.DualQuantitiesResponse]:
        """Low-level method to call ViewAddedFamilyQuantityForSource, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/ViewAddedFamilyQuantityForSource"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.DualQuantitiesResponse,extra_headers, timeout_seconds)

    async def view_added_family_quantity_for_source(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/SearchAll"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Filter"
        return await self._connect_client.call_unary(url, req, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList:
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
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/CountInStatus"
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InwardJobsFreeIssueMaterialsService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
class InwardJobsFreeIssueMaterialsServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft_update(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_verification(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def verify(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_revision(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def revision_update(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
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
    def autofill(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceAutofillRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def is_completable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def add_inward_job_free_issue_material_item(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_inward_job_free_issue_material_item(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_inward_job_free_issue_material_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_inward_job_free_issue_material_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_inward_job_free_issue_material_items(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_inward_job_free_issue_material_item_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItem]:
        ...
    def view_approved_inward_job_free_issue_material_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList]:
        ...
    def view_unapproved_inward_job_free_issue_material_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList]:
        ...
    def view_inward_job_free_issue_material_item_history(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemHistoryRequest]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsItemsList]:
        ...
    def view_paginated_approved_inward_job_free_issue_material_items(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        ...
    def view_paginated_unapproved_inward_job_free_issue_material_items(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        ...
    def search_items_with_pagination(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        ...
    def download_items_as_csv(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def download_items_template_as_csv(self, req: ClientRequest[base.scailo_pb2.Empty]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        ...
    def view_by_reference_id(self, req: ClientRequest[base.scailo_pb2.SimpleSearchReq]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterial]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        ...
    def view_ancillary_parameters_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialAncillaryParameters]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        ...
    def view_with_pagination(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginationReq]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginationResponse]:
        ...
    def view_prospective_families(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def filter_prospective_families(self, req: ClientRequest[families.scailo_pb2.FilterFamiliesReqForIdentifier]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def view_prospective_inward_job_free_issue_material_item(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemProspectiveInfoRequest]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemCreateRequest]:
        ...
    def is_downloadable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def download_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def download_label_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def view_added_family_quantity_for_source(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceAlreadyAddedQuantityForSourceRequest]) -> ServerResponse[base.scailo_pb2.DualQuantitiesResponse]:
        ...
    def search_all(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceSearchAllReq]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        ...
    def filter(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceFilterReq]) -> ServerResponse[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsList]:
        ...
    def count_in_status(self, req: ClientRequest[base.scailo_pb2.CountInSLCStatusRequest]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def count(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

INWARD_JOBS_FREE_ISSUE_MATERIALS_SERVICE_PATH_PREFIX = "/Scailo.InwardJobsFreeIssueMaterialsService"

def wsgi_inward_jobs_free_issue_materials_service(implementation: InwardJobsFreeIssueMaterialsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/Create", implementation.create, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/Draft", implementation.draft, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/DraftUpdate", implementation.draft_update, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/SendForVerification", implementation.send_for_verification, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/Verify", implementation.verify, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/Approve", implementation.approve, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/SendForRevision", implementation.send_for_revision, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/RevisionUpdate", implementation.revision_update, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/Halt", implementation.halt, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/Discard", implementation.discard, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/Restore", implementation.restore, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/Repeat", implementation.repeat, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/SendEmail", implementation.send_email, base.scailo_pb2.IdentifierWithEmailAttributes)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/CreateMagicLink", implementation.create_magic_link, magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/Autofill", implementation.autofill, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceAutofillRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/IsCompletable", implementation.is_completable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/AddInwardJobFreeIssueMaterialItem", implementation.add_inward_job_free_issue_material_item, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemCreateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ModifyInwardJobFreeIssueMaterialItem", implementation.modify_inward_job_free_issue_material_item, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceItemUpdateRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ApproveInwardJobFreeIssueMaterialItem", implementation.approve_inward_job_free_issue_material_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/DeleteInwardJobFreeIssueMaterialItem", implementation.delete_inward_job_free_issue_material_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ReorderInwardJobFreeIssueMaterialItems", implementation.reorder_inward_job_free_issue_material_items, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewInwardJobFreeIssueMaterialItemByID", implementation.view_inward_job_free_issue_material_item_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewApprovedInwardJobFreeIssueMaterialItems", implementation.view_approved_inward_job_free_issue_material_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewUnapprovedInwardJobFreeIssueMaterialItems", implementation.view_unapproved_inward_job_free_issue_material_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewInwardJobFreeIssueMaterialItemHistory", implementation.view_inward_job_free_issue_material_item_history, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemHistoryRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewPaginatedApprovedInwardJobFreeIssueMaterialItems", implementation.view_paginated_approved_inward_job_free_issue_material_items, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewPaginatedUnapprovedInwardJobFreeIssueMaterialItems", implementation.view_paginated_unapproved_inward_job_free_issue_material_items, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/SearchItemsWithPagination", implementation.search_items_with_pagination, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemsSearchRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/DownloadItemsAsCSV", implementation.download_items_as_csv, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/DownloadItemsTemplateAsCSV", implementation.download_items_template_as_csv, base.scailo_pb2.Empty)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewByReferenceID", implementation.view_by_reference_id, base.scailo_pb2.SimpleSearchReq)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewAncillaryParametersByUUID", implementation.view_ancillary_parameters_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewWithPagination", implementation.view_with_pagination, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServicePaginationReq)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewProspectiveFamilies", implementation.view_prospective_families, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/FilterProspectiveFamilies", implementation.filter_prospective_families, families.scailo_pb2.FilterFamiliesReqForIdentifier)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewProspectiveInwardJobFreeIssueMaterialItem", implementation.view_prospective_inward_job_free_issue_material_item, inward_jobs_free_issue_materials.scailo_pb2.InwardJobFreeIssueMaterialItemProspectiveInfoRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/IsDownloadable", implementation.is_downloadable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/DownloadByUUID", implementation.download_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/DownloadLabelByUUID", implementation.download_label_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/ViewAddedFamilyQuantityForSource", implementation.view_added_family_quantity_for_source, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceAlreadyAddedQuantityForSourceRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/SearchAll", implementation.search_all, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/Filter", implementation.filter, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceFilterReq)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/CountInStatus", implementation.count_in_status, base.scailo_pb2.CountInSLCStatusRequest)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/Count", implementation.count, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceCountReq)
    app.register_unary_rpc("/Scailo.InwardJobsFreeIssueMaterialsService/DownloadAsCSV", implementation.download_as_csv, inward_jobs_free_issue_materials.scailo_pb2.InwardJobsFreeIssueMaterialsServiceFilterReq)
    return app
