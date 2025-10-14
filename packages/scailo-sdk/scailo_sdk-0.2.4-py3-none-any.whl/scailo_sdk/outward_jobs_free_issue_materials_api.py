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

from scailo_sdk import base, families, magic_links, outward_jobs_free_issue_materials

class OutwardJobsFreeIssueMaterialsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def create(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Draft"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DraftUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft_update(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/SendForVerification"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Verify"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Approve"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/SendForRevision"
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/RevisionUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def revision_update(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Halt"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Discard"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Restore"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Complete"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Repeat"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Reopen"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/CommentAdd"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/SendEmail"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/CreateMagicLink"
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Autofill"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def autofill(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/IsCompletable"
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

    def call_add_outward_job_free_issue_material_item(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddOutwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/AddOutwardJobFreeIssueMaterialItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_outward_job_free_issue_material_item(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_outward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_outward_job_free_issue_material_item(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyOutwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ModifyOutwardJobFreeIssueMaterialItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_outward_job_free_issue_material_item(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_outward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_outward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveOutwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ApproveOutwardJobFreeIssueMaterialItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_outward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_outward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_outward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteOutwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DeleteOutwardJobFreeIssueMaterialItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_outward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_outward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_outward_job_free_issue_material_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderOutwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ReorderOutwardJobFreeIssueMaterialItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_outward_job_free_issue_material_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_outward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_job_free_issue_material_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem]:
        """Low-level method to call ViewOutwardJobFreeIssueMaterialItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewOutwardJobFreeIssueMaterialItemByID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem,extra_headers, timeout_seconds)


    def view_outward_job_free_issue_material_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem:
        response = self.call_view_outward_job_free_issue_material_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_job_free_issue_material_item_by_inventory_hash(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem]:
        """Low-level method to call ViewOutwardJobFreeIssueMaterialItemByInventoryHash, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewOutwardJobFreeIssueMaterialItemByInventoryHash"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem,extra_headers, timeout_seconds)


    def view_outward_job_free_issue_material_item_by_inventory_hash(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem:
        response = self.call_view_outward_job_free_issue_material_item_by_inventory_hash(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_approved_outward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList]:
        """Low-level method to call ViewApprovedOutwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewApprovedOutwardJobFreeIssueMaterialItems"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList,extra_headers, timeout_seconds)


    def view_approved_outward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList:
        response = self.call_view_approved_outward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_unapproved_outward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList]:
        """Low-level method to call ViewUnapprovedOutwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewUnapprovedOutwardJobFreeIssueMaterialItems"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList,extra_headers, timeout_seconds)


    def view_unapproved_outward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList:
        response = self.call_view_unapproved_outward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_outward_job_free_issue_material_item_history(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList]:
        """Low-level method to call ViewOutwardJobFreeIssueMaterialItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewOutwardJobFreeIssueMaterialItemHistory"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList,extra_headers, timeout_seconds)


    def view_outward_job_free_issue_material_item_history(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList:
        response = self.call_view_outward_job_free_issue_material_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_approved_outward_job_free_issue_material_items(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedOutwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewPaginatedApprovedOutwardJobFreeIssueMaterialItems"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_approved_outward_job_free_issue_material_items(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse:
        response = self.call_view_paginated_approved_outward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_unapproved_outward_job_free_issue_material_items(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedOutwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewPaginatedUnapprovedOutwardJobFreeIssueMaterialItems"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_unapproved_outward_job_free_issue_material_items(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse:
        response = self.call_view_paginated_unapproved_outward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_items_with_pagination(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/SearchItemsWithPagination"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def search_items_with_pagination(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadItemsTemplateAsCSV"
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewByID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewByUUID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewByReferenceID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial,extra_headers, timeout_seconds)


    def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewAncillaryParametersByUUID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialAncillaryParameters,extra_headers, timeout_seconds)


    def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialAncillaryParameters:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewAll"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginationResponse:
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewProspectiveFamilies"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/FilterProspectiveFamilies"
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

    def call_view_prospective_outward_job_free_issue_material_item(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveOutwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewProspectiveOutwardJobFreeIssueMaterialItem"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemCreateRequest,extra_headers, timeout_seconds)


    def view_prospective_outward_job_free_issue_material_item(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemCreateRequest:
        response = self.call_view_prospective_outward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/IsDownloadable"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadByUUID"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadLabelByUUID"
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.DualQuantitiesResponse]:
        """Low-level method to call ViewAddedFamilyQuantityForSource, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewAddedFamilyQuantityForSource"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.DualQuantitiesResponse,extra_headers, timeout_seconds)


    def view_added_family_quantity_for_source(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/SearchAll"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)


    def search_all(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Filter"
        return self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)


    def filter(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList:
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/CountInStatus"
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncOutwardJobsFreeIssueMaterialsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def create(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Draft"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DraftUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft_update(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/SendForVerification"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Verify"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Approve"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/SendForRevision"
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/RevisionUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def revision_update(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Halt"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Discard"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Restore"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Complete"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Repeat"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Reopen"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/CommentAdd"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/SendEmail"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/CreateMagicLink"
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Autofill"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def autofill(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/IsCompletable"
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

    async def call_add_outward_job_free_issue_material_item(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddOutwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/AddOutwardJobFreeIssueMaterialItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_outward_job_free_issue_material_item(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_outward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_outward_job_free_issue_material_item(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyOutwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ModifyOutwardJobFreeIssueMaterialItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_outward_job_free_issue_material_item(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_outward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_outward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveOutwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ApproveOutwardJobFreeIssueMaterialItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_outward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_outward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_outward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteOutwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DeleteOutwardJobFreeIssueMaterialItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_outward_job_free_issue_material_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_outward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_outward_job_free_issue_material_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderOutwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ReorderOutwardJobFreeIssueMaterialItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_outward_job_free_issue_material_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_outward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_job_free_issue_material_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem]:
        """Low-level method to call ViewOutwardJobFreeIssueMaterialItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewOutwardJobFreeIssueMaterialItemByID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem,extra_headers, timeout_seconds)

    async def view_outward_job_free_issue_material_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem:
        response = await self.call_view_outward_job_free_issue_material_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_job_free_issue_material_item_by_inventory_hash(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem]:
        """Low-level method to call ViewOutwardJobFreeIssueMaterialItemByInventoryHash, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewOutwardJobFreeIssueMaterialItemByInventoryHash"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem,extra_headers, timeout_seconds)

    async def view_outward_job_free_issue_material_item_by_inventory_hash(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem:
        response = await self.call_view_outward_job_free_issue_material_item_by_inventory_hash(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_approved_outward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList]:
        """Low-level method to call ViewApprovedOutwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewApprovedOutwardJobFreeIssueMaterialItems"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList,extra_headers, timeout_seconds)

    async def view_approved_outward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList:
        response = await self.call_view_approved_outward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_unapproved_outward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList]:
        """Low-level method to call ViewUnapprovedOutwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewUnapprovedOutwardJobFreeIssueMaterialItems"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList,extra_headers, timeout_seconds)

    async def view_unapproved_outward_job_free_issue_material_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList:
        response = await self.call_view_unapproved_outward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_outward_job_free_issue_material_item_history(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList]:
        """Low-level method to call ViewOutwardJobFreeIssueMaterialItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewOutwardJobFreeIssueMaterialItemHistory"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList,extra_headers, timeout_seconds)

    async def view_outward_job_free_issue_material_item_history(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList:
        response = await self.call_view_outward_job_free_issue_material_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_approved_outward_job_free_issue_material_items(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedOutwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewPaginatedApprovedOutwardJobFreeIssueMaterialItems"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_approved_outward_job_free_issue_material_items(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse:
        response = await self.call_view_paginated_approved_outward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_unapproved_outward_job_free_issue_material_items(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedOutwardJobFreeIssueMaterialItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewPaginatedUnapprovedOutwardJobFreeIssueMaterialItems"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_unapproved_outward_job_free_issue_material_items(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse:
        response = await self.call_view_paginated_unapproved_outward_job_free_issue_material_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_items_with_pagination(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/SearchItemsWithPagination"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def search_items_with_pagination(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadItemsTemplateAsCSV"
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewByID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewByReferenceID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial,extra_headers, timeout_seconds)

    async def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewAncillaryParametersByUUID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialAncillaryParameters,extra_headers, timeout_seconds)

    async def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialAncillaryParameters:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewAll"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList:
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
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginationResponse:
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewProspectiveFamilies"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/FilterProspectiveFamilies"
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

    async def call_view_prospective_outward_job_free_issue_material_item(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveOutwardJobFreeIssueMaterialItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewProspectiveOutwardJobFreeIssueMaterialItem"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemCreateRequest,extra_headers, timeout_seconds)

    async def view_prospective_outward_job_free_issue_material_item(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemCreateRequest:
        response = await self.call_view_prospective_outward_job_free_issue_material_item(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/IsDownloadable"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadByUUID"
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadLabelByUUID"
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.DualQuantitiesResponse]:
        """Low-level method to call ViewAddedFamilyQuantityForSource, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/ViewAddedFamilyQuantityForSource"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.DualQuantitiesResponse,extra_headers, timeout_seconds)

    async def view_added_family_quantity_for_source(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/SearchAll"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Filter"
        return await self._connect_client.call_unary(url, req, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList:
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
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/CountInStatus"
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
class OutwardJobsFreeIssueMaterialsServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft_update(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_verification(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def verify(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_revision(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def revision_update(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
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
    def autofill(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceAutofillRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def is_completable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def add_outward_job_free_issue_material_item(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_outward_job_free_issue_material_item(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_outward_job_free_issue_material_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_outward_job_free_issue_material_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_outward_job_free_issue_material_items(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_outward_job_free_issue_material_item_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem]:
        ...
    def view_outward_job_free_issue_material_item_by_inventory_hash(self, req: ClientRequest[base.scailo_pb2.SimpleSearchReq]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItem]:
        ...
    def view_approved_outward_job_free_issue_material_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList]:
        ...
    def view_unapproved_outward_job_free_issue_material_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList]:
        ...
    def view_outward_job_free_issue_material_item_history(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemHistoryRequest]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsItemsList]:
        ...
    def view_paginated_approved_outward_job_free_issue_material_items(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        ...
    def view_paginated_unapproved_outward_job_free_issue_material_items(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        ...
    def search_items_with_pagination(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginatedItemsResponse]:
        ...
    def download_items_as_csv(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def download_items_template_as_csv(self, req: ClientRequest[base.scailo_pb2.Empty]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        ...
    def view_by_reference_id(self, req: ClientRequest[base.scailo_pb2.SimpleSearchReq]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterial]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        ...
    def view_ancillary_parameters_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialAncillaryParameters]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        ...
    def view_with_pagination(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginationReq]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginationResponse]:
        ...
    def view_prospective_families(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def filter_prospective_families(self, req: ClientRequest[families.scailo_pb2.FilterFamiliesReqForIdentifier]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def view_prospective_outward_job_free_issue_material_item(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemProspectiveInfoRequest]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemCreateRequest]:
        ...
    def is_downloadable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def download_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def download_label_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def view_added_family_quantity_for_source(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceAlreadyAddedQuantityForSourceRequest]) -> ServerResponse[base.scailo_pb2.DualQuantitiesResponse]:
        ...
    def search_all(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceSearchAllReq]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        ...
    def filter(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceFilterReq]) -> ServerResponse[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsList]:
        ...
    def count_in_status(self, req: ClientRequest[base.scailo_pb2.CountInSLCStatusRequest]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def count(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

OUTWARD_JOBS_FREE_ISSUE_MATERIALS_SERVICE_PATH_PREFIX = "/Scailo.OutwardJobsFreeIssueMaterialsService"

def wsgi_outward_jobs_free_issue_materials_service(implementation: OutwardJobsFreeIssueMaterialsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/Create", implementation.create, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/Draft", implementation.draft, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/DraftUpdate", implementation.draft_update, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/SendForVerification", implementation.send_for_verification, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/Verify", implementation.verify, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/Approve", implementation.approve, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/SendForRevision", implementation.send_for_revision, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/RevisionUpdate", implementation.revision_update, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/Halt", implementation.halt, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/Discard", implementation.discard, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/Restore", implementation.restore, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/Repeat", implementation.repeat, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/SendEmail", implementation.send_email, base.scailo_pb2.IdentifierWithEmailAttributes)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/CreateMagicLink", implementation.create_magic_link, magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/Autofill", implementation.autofill, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceAutofillRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/IsCompletable", implementation.is_completable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/AddOutwardJobFreeIssueMaterialItem", implementation.add_outward_job_free_issue_material_item, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemCreateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ModifyOutwardJobFreeIssueMaterialItem", implementation.modify_outward_job_free_issue_material_item, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceItemUpdateRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ApproveOutwardJobFreeIssueMaterialItem", implementation.approve_outward_job_free_issue_material_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/DeleteOutwardJobFreeIssueMaterialItem", implementation.delete_outward_job_free_issue_material_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ReorderOutwardJobFreeIssueMaterialItems", implementation.reorder_outward_job_free_issue_material_items, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewOutwardJobFreeIssueMaterialItemByID", implementation.view_outward_job_free_issue_material_item_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewOutwardJobFreeIssueMaterialItemByInventoryHash", implementation.view_outward_job_free_issue_material_item_by_inventory_hash, base.scailo_pb2.SimpleSearchReq)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewApprovedOutwardJobFreeIssueMaterialItems", implementation.view_approved_outward_job_free_issue_material_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewUnapprovedOutwardJobFreeIssueMaterialItems", implementation.view_unapproved_outward_job_free_issue_material_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewOutwardJobFreeIssueMaterialItemHistory", implementation.view_outward_job_free_issue_material_item_history, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemHistoryRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewPaginatedApprovedOutwardJobFreeIssueMaterialItems", implementation.view_paginated_approved_outward_job_free_issue_material_items, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewPaginatedUnapprovedOutwardJobFreeIssueMaterialItems", implementation.view_paginated_unapproved_outward_job_free_issue_material_items, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/SearchItemsWithPagination", implementation.search_items_with_pagination, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemsSearchRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadItemsAsCSV", implementation.download_items_as_csv, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadItemsTemplateAsCSV", implementation.download_items_template_as_csv, base.scailo_pb2.Empty)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewByReferenceID", implementation.view_by_reference_id, base.scailo_pb2.SimpleSearchReq)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewAncillaryParametersByUUID", implementation.view_ancillary_parameters_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewWithPagination", implementation.view_with_pagination, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServicePaginationReq)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewProspectiveFamilies", implementation.view_prospective_families, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/FilterProspectiveFamilies", implementation.filter_prospective_families, families.scailo_pb2.FilterFamiliesReqForIdentifier)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewProspectiveOutwardJobFreeIssueMaterialItem", implementation.view_prospective_outward_job_free_issue_material_item, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobFreeIssueMaterialItemProspectiveInfoRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/IsDownloadable", implementation.is_downloadable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadByUUID", implementation.download_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadLabelByUUID", implementation.download_label_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/ViewAddedFamilyQuantityForSource", implementation.view_added_family_quantity_for_source, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceAlreadyAddedQuantityForSourceRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/SearchAll", implementation.search_all, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/Filter", implementation.filter, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceFilterReq)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/CountInStatus", implementation.count_in_status, base.scailo_pb2.CountInSLCStatusRequest)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/Count", implementation.count, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceCountReq)
    app.register_unary_rpc("/Scailo.OutwardJobsFreeIssueMaterialsService/DownloadAsCSV", implementation.download_as_csv, outward_jobs_free_issue_materials.scailo_pb2.OutwardJobsFreeIssueMaterialsServiceFilterReq)
    return app
