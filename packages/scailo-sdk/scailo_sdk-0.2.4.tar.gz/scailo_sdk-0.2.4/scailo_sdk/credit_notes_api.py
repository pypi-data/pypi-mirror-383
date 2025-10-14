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

from scailo_sdk import base, credit_notes, families, magic_links

class CreditNotesServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def create(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/Draft"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: credit_notes.scailo_pb2.CreditNotesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/DraftUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft_update(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.CreditNotesService/SendForVerification"
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
        url = self.base_url + "/Scailo.CreditNotesService/Verify"
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
        url = self.base_url + "/Scailo.CreditNotesService/Approve"
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
        url = self.base_url + "/Scailo.CreditNotesService/SendForRevision"
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
        self, req: credit_notes.scailo_pb2.CreditNotesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/RevisionUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def revision_update(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.CreditNotesService/Halt"
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
        url = self.base_url + "/Scailo.CreditNotesService/Discard"
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
        url = self.base_url + "/Scailo.CreditNotesService/Restore"
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
        url = self.base_url + "/Scailo.CreditNotesService/Complete"
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
        url = self.base_url + "/Scailo.CreditNotesService/Repeat"
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
        url = self.base_url + "/Scailo.CreditNotesService/Reopen"
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
        url = self.base_url + "/Scailo.CreditNotesService/CommentAdd"
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
        url = self.base_url + "/Scailo.CreditNotesService/SendEmail"
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
        self, req: credit_notes.scailo_pb2.CreditNotesServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/Autofill"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def autofill(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.CreditNotesService/CreateMagicLink"
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

    def call_add_multiple_credit_note_items(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceMultipleItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddMultipleCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/AddMultipleCreditNoteItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_multiple_credit_note_items(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceMultipleItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_multiple_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_credit_note_item(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddCreditNoteItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/AddCreditNoteItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_credit_note_item(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_credit_note_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_credit_note_item(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyCreditNoteItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ModifyCreditNoteItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_credit_note_item(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_credit_note_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_credit_note_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveCreditNoteItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ApproveCreditNoteItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_credit_note_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_credit_note_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_credit_note_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteCreditNoteItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/DeleteCreditNoteItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_credit_note_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_credit_note_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_credit_note_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ReorderCreditNoteItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_credit_note_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_credit_note_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteItem]:
        """Low-level method to call ViewCreditNoteItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewCreditNoteItemByID"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteItem,extra_headers, timeout_seconds)


    def view_credit_note_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteItem:
        response = self.call_view_credit_note_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_approved_credit_note_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteItemsList]:
        """Low-level method to call ViewApprovedCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewApprovedCreditNoteItems"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteItemsList,extra_headers, timeout_seconds)


    def view_approved_credit_note_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteItemsList:
        response = self.call_view_approved_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_unapproved_credit_note_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteItemsList]:
        """Low-level method to call ViewUnapprovedCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewUnapprovedCreditNoteItems"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteItemsList,extra_headers, timeout_seconds)


    def view_unapproved_credit_note_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteItemsList:
        response = self.call_view_unapproved_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_credit_note_item_history(
        self, req: credit_notes.scailo_pb2.CreditNoteItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteItemsList]:
        """Low-level method to call ViewCreditNoteItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewCreditNoteItemHistory"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteItemsList,extra_headers, timeout_seconds)


    def view_credit_note_item_history(
        self, req: credit_notes.scailo_pb2.CreditNoteItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteItemsList:
        response = self.call_view_credit_note_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_approved_credit_note_items(
        self, req: credit_notes.scailo_pb2.CreditNoteItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewPaginatedApprovedCreditNoteItems"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_approved_credit_note_items(
        self, req: credit_notes.scailo_pb2.CreditNoteItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse:
        response = self.call_view_paginated_approved_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_unapproved_credit_note_items(
        self, req: credit_notes.scailo_pb2.CreditNoteItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewPaginatedUnapprovedCreditNoteItems"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_unapproved_credit_note_items(
        self, req: credit_notes.scailo_pb2.CreditNoteItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse:
        response = self.call_view_paginated_unapproved_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_items_with_pagination(
        self, req: credit_notes.scailo_pb2.CreditNoteItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/SearchItemsWithPagination"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def search_items_with_pagination(
        self, req: credit_notes.scailo_pb2.CreditNoteItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.CreditNotesService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.CreditNotesService/DownloadItemsTemplateAsCSV"
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

    def call_upload_credit_note_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/UploadCreditNoteItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def upload_credit_note_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_upload_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_credit_note_reference(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceReferenceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddCreditNoteReference, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/AddCreditNoteReference"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_credit_note_reference(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceReferenceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_credit_note_reference(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_credit_note_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveCreditNoteReference, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ApproveCreditNoteReference"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_credit_note_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_credit_note_reference(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_credit_note_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteCreditNoteReference, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/DeleteCreditNoteReference"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_credit_note_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_credit_note_reference(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_credit_note_reference_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteReference]:
        """Low-level method to call ViewCreditNoteReferenceByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewCreditNoteReferenceByID"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteReference,extra_headers, timeout_seconds)


    def view_credit_note_reference_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteReference:
        response = self.call_view_credit_note_reference_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_credit_note_references(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteReferencesList]:
        """Low-level method to call ViewCreditNoteReferences, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewCreditNoteReferences"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteReferencesList,extra_headers, timeout_seconds)


    def view_credit_note_references(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteReferencesList:
        response = self.call_view_credit_note_references(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNote]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewByID"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNote,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNote:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNote]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewByUUID"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNote,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNote:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNote]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewByReferenceID"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNote,extra_headers, timeout_seconds)


    def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNote:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNote]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNote,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNote:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNote]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNote,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNote:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesList:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewAncillaryParametersByUUID"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteAncillaryParameters,extra_headers, timeout_seconds)


    def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteAncillaryParameters:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewAll"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesList:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: credit_notes.scailo_pb2.CreditNotesServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: credit_notes.scailo_pb2.CreditNotesServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesServicePaginationResponse:
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
        url = self.base_url + "/Scailo.CreditNotesService/ViewProspectiveFamilies"
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
        url = self.base_url + "/Scailo.CreditNotesService/FilterProspectiveFamilies"
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

    def call_view_prospective_credit_note_item(
        self, req: credit_notes.scailo_pb2.CreditNoteItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveCreditNoteItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewProspectiveCreditNoteItem"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesServiceItemCreateRequest,extra_headers, timeout_seconds)


    def view_prospective_credit_note_item(
        self, req: credit_notes.scailo_pb2.CreditNoteItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesServiceItemCreateRequest:
        response = self.call_view_prospective_credit_note_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_returned_statistics(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteReturnStatisticsList]:
        """Low-level method to call ViewReturnedStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewReturnedStatistics"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteReturnStatisticsList,extra_headers, timeout_seconds)


    def view_returned_statistics(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteReturnStatisticsList:
        response = self.call_view_returned_statistics(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.CreditNotesService/IsDownloadable"
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
        url = self.base_url + "/Scailo.CreditNotesService/DownloadByUUID"
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

    def call_view_added_family_quantity_for_source(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.DualQuantitiesResponse]:
        """Low-level method to call ViewAddedFamilyQuantityForSource, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewAddedFamilyQuantityForSource"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.DualQuantitiesResponse,extra_headers, timeout_seconds)


    def view_added_family_quantity_for_source(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: credit_notes.scailo_pb2.CreditNotesServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/SearchAll"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesList,extra_headers, timeout_seconds)


    def search_all(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/Filter"
        return self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesList,extra_headers, timeout_seconds)


    def filter(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesList:
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
        url = self.base_url + "/Scailo.CreditNotesService/CountInStatus"
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
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = self.call_count(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_accrued_value(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.SumResponse]:
        """Low-level method to call AccruedValue, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/AccruedValue"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.SumResponse,extra_headers, timeout_seconds)


    def accrued_value(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.SumResponse:
        response = self.call_accrued_value(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_download_as_csv(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncCreditNotesServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def create(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/Draft"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: credit_notes.scailo_pb2.CreditNotesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/DraftUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft_update(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.CreditNotesService/SendForVerification"
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
        url = self.base_url + "/Scailo.CreditNotesService/Verify"
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
        url = self.base_url + "/Scailo.CreditNotesService/Approve"
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
        url = self.base_url + "/Scailo.CreditNotesService/SendForRevision"
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
        self, req: credit_notes.scailo_pb2.CreditNotesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/RevisionUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def revision_update(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.CreditNotesService/Halt"
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
        url = self.base_url + "/Scailo.CreditNotesService/Discard"
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
        url = self.base_url + "/Scailo.CreditNotesService/Restore"
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
        url = self.base_url + "/Scailo.CreditNotesService/Complete"
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
        url = self.base_url + "/Scailo.CreditNotesService/Repeat"
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
        url = self.base_url + "/Scailo.CreditNotesService/Reopen"
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
        url = self.base_url + "/Scailo.CreditNotesService/CommentAdd"
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
        url = self.base_url + "/Scailo.CreditNotesService/SendEmail"
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
        self, req: credit_notes.scailo_pb2.CreditNotesServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/Autofill"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def autofill(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.CreditNotesService/CreateMagicLink"
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

    async def call_add_multiple_credit_note_items(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceMultipleItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddMultipleCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/AddMultipleCreditNoteItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_multiple_credit_note_items(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceMultipleItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_multiple_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_credit_note_item(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddCreditNoteItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/AddCreditNoteItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_credit_note_item(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_credit_note_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_credit_note_item(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyCreditNoteItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ModifyCreditNoteItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_credit_note_item(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_credit_note_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_credit_note_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveCreditNoteItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ApproveCreditNoteItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_credit_note_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_credit_note_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_credit_note_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteCreditNoteItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/DeleteCreditNoteItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_credit_note_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_credit_note_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_credit_note_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ReorderCreditNoteItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_credit_note_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_credit_note_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteItem]:
        """Low-level method to call ViewCreditNoteItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewCreditNoteItemByID"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteItem,extra_headers, timeout_seconds)

    async def view_credit_note_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteItem:
        response = await self.call_view_credit_note_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_approved_credit_note_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteItemsList]:
        """Low-level method to call ViewApprovedCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewApprovedCreditNoteItems"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteItemsList,extra_headers, timeout_seconds)

    async def view_approved_credit_note_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteItemsList:
        response = await self.call_view_approved_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_unapproved_credit_note_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteItemsList]:
        """Low-level method to call ViewUnapprovedCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewUnapprovedCreditNoteItems"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteItemsList,extra_headers, timeout_seconds)

    async def view_unapproved_credit_note_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteItemsList:
        response = await self.call_view_unapproved_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_credit_note_item_history(
        self, req: credit_notes.scailo_pb2.CreditNoteItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteItemsList]:
        """Low-level method to call ViewCreditNoteItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewCreditNoteItemHistory"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteItemsList,extra_headers, timeout_seconds)

    async def view_credit_note_item_history(
        self, req: credit_notes.scailo_pb2.CreditNoteItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteItemsList:
        response = await self.call_view_credit_note_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_approved_credit_note_items(
        self, req: credit_notes.scailo_pb2.CreditNoteItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewPaginatedApprovedCreditNoteItems"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_approved_credit_note_items(
        self, req: credit_notes.scailo_pb2.CreditNoteItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse:
        response = await self.call_view_paginated_approved_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_unapproved_credit_note_items(
        self, req: credit_notes.scailo_pb2.CreditNoteItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewPaginatedUnapprovedCreditNoteItems"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_unapproved_credit_note_items(
        self, req: credit_notes.scailo_pb2.CreditNoteItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse:
        response = await self.call_view_paginated_unapproved_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_items_with_pagination(
        self, req: credit_notes.scailo_pb2.CreditNoteItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/SearchItemsWithPagination"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def search_items_with_pagination(
        self, req: credit_notes.scailo_pb2.CreditNoteItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.CreditNotesService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.CreditNotesService/DownloadItemsTemplateAsCSV"
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

    async def call_upload_credit_note_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadCreditNoteItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/UploadCreditNoteItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def upload_credit_note_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_upload_credit_note_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_credit_note_reference(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceReferenceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddCreditNoteReference, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/AddCreditNoteReference"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_credit_note_reference(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceReferenceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_credit_note_reference(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_credit_note_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveCreditNoteReference, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ApproveCreditNoteReference"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_credit_note_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_credit_note_reference(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_credit_note_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteCreditNoteReference, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/DeleteCreditNoteReference"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_credit_note_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_credit_note_reference(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_credit_note_reference_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteReference]:
        """Low-level method to call ViewCreditNoteReferenceByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewCreditNoteReferenceByID"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteReference,extra_headers, timeout_seconds)

    async def view_credit_note_reference_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteReference:
        response = await self.call_view_credit_note_reference_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_credit_note_references(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteReferencesList]:
        """Low-level method to call ViewCreditNoteReferences, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewCreditNoteReferences"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteReferencesList,extra_headers, timeout_seconds)

    async def view_credit_note_references(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteReferencesList:
        response = await self.call_view_credit_note_references(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNote]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewByID"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNote,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNote:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNote]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNote,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNote:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNote]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewByReferenceID"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNote,extra_headers, timeout_seconds)

    async def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNote:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNote]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNote,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNote:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNote]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNote,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNote:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesList:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewAncillaryParametersByUUID"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteAncillaryParameters,extra_headers, timeout_seconds)

    async def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteAncillaryParameters:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewAll"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesList:
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
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: credit_notes.scailo_pb2.CreditNotesServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: credit_notes.scailo_pb2.CreditNotesServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesServicePaginationResponse:
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
        url = self.base_url + "/Scailo.CreditNotesService/ViewProspectiveFamilies"
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
        url = self.base_url + "/Scailo.CreditNotesService/FilterProspectiveFamilies"
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

    async def call_view_prospective_credit_note_item(
        self, req: credit_notes.scailo_pb2.CreditNoteItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveCreditNoteItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewProspectiveCreditNoteItem"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesServiceItemCreateRequest,extra_headers, timeout_seconds)

    async def view_prospective_credit_note_item(
        self, req: credit_notes.scailo_pb2.CreditNoteItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesServiceItemCreateRequest:
        response = await self.call_view_prospective_credit_note_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_returned_statistics(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNoteReturnStatisticsList]:
        """Low-level method to call ViewReturnedStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewReturnedStatistics"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNoteReturnStatisticsList,extra_headers, timeout_seconds)

    async def view_returned_statistics(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNoteReturnStatisticsList:
        response = await self.call_view_returned_statistics(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.CreditNotesService/IsDownloadable"
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
        url = self.base_url + "/Scailo.CreditNotesService/DownloadByUUID"
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

    async def call_view_added_family_quantity_for_source(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.DualQuantitiesResponse]:
        """Low-level method to call ViewAddedFamilyQuantityForSource, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/ViewAddedFamilyQuantityForSource"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.DualQuantitiesResponse,extra_headers, timeout_seconds)

    async def view_added_family_quantity_for_source(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: credit_notes.scailo_pb2.CreditNotesServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/SearchAll"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[credit_notes.scailo_pb2.CreditNotesList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/Filter"
        return await self._connect_client.call_unary(url, req, credit_notes.scailo_pb2.CreditNotesList,extra_headers, timeout_seconds)

    async def filter(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> credit_notes.scailo_pb2.CreditNotesList:
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
        url = self.base_url + "/Scailo.CreditNotesService/CountInStatus"
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
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = await self.call_count(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_accrued_value(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.SumResponse]:
        """Low-level method to call AccruedValue, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/AccruedValue"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.SumResponse,extra_headers, timeout_seconds)

    async def accrued_value(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.SumResponse:
        response = await self.call_accrued_value(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_download_as_csv(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.CreditNotesService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: credit_notes.scailo_pb2.CreditNotesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
class CreditNotesServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft_update(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_verification(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def verify(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_revision(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def revision_update(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
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
    def autofill(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceAutofillRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def create_magic_link(self, req: ClientRequest[magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource]) -> ServerResponse[magic_links.scailo_pb2.MagicLink]:
        ...
    def add_multiple_credit_note_items(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceMultipleItemsCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_credit_note_item(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceItemCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_credit_note_item(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceItemUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_credit_note_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_credit_note_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_credit_note_items(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_credit_note_item_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[credit_notes.scailo_pb2.CreditNoteItem]:
        ...
    def view_approved_credit_note_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[credit_notes.scailo_pb2.CreditNoteItemsList]:
        ...
    def view_unapproved_credit_note_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[credit_notes.scailo_pb2.CreditNoteItemsList]:
        ...
    def view_credit_note_item_history(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNoteItemHistoryRequest]) -> ServerResponse[credit_notes.scailo_pb2.CreditNoteItemsList]:
        ...
    def view_paginated_approved_credit_note_items(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNoteItemsSearchRequest]) -> ServerResponse[credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse]:
        ...
    def view_paginated_unapproved_credit_note_items(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNoteItemsSearchRequest]) -> ServerResponse[credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse]:
        ...
    def search_items_with_pagination(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNoteItemsSearchRequest]) -> ServerResponse[credit_notes.scailo_pb2.CreditNotesServicePaginatedItemsResponse]:
        ...
    def download_items_as_csv(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def download_items_template_as_csv(self, req: ClientRequest[base.scailo_pb2.Empty]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def upload_credit_note_items(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithFile]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def add_credit_note_reference(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceReferenceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_credit_note_reference(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_credit_note_reference(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_credit_note_reference_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[credit_notes.scailo_pb2.CreditNoteReference]:
        ...
    def view_credit_note_references(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[credit_notes.scailo_pb2.CreditNoteReferencesList]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[credit_notes.scailo_pb2.CreditNote]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[credit_notes.scailo_pb2.CreditNote]:
        ...
    def view_by_reference_id(self, req: ClientRequest[base.scailo_pb2.SimpleSearchReq]) -> ServerResponse[credit_notes.scailo_pb2.CreditNote]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[credit_notes.scailo_pb2.CreditNote]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[credit_notes.scailo_pb2.CreditNote]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[credit_notes.scailo_pb2.CreditNotesList]:
        ...
    def view_ancillary_parameters_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[credit_notes.scailo_pb2.CreditNoteAncillaryParameters]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[credit_notes.scailo_pb2.CreditNotesList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[credit_notes.scailo_pb2.CreditNotesList]:
        ...
    def view_with_pagination(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServicePaginationReq]) -> ServerResponse[credit_notes.scailo_pb2.CreditNotesServicePaginationResponse]:
        ...
    def view_prospective_families(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def filter_prospective_families(self, req: ClientRequest[families.scailo_pb2.FilterFamiliesReqForIdentifier]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def view_prospective_credit_note_item(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNoteItemProspectiveInfoRequest]) -> ServerResponse[credit_notes.scailo_pb2.CreditNotesServiceItemCreateRequest]:
        ...
    def view_returned_statistics(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[credit_notes.scailo_pb2.CreditNoteReturnStatisticsList]:
        ...
    def is_downloadable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def download_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def view_added_family_quantity_for_source(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceAlreadyAddedQuantityForSourceRequest]) -> ServerResponse[base.scailo_pb2.DualQuantitiesResponse]:
        ...
    def search_all(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceSearchAllReq]) -> ServerResponse[credit_notes.scailo_pb2.CreditNotesList]:
        ...
    def filter(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceFilterReq]) -> ServerResponse[credit_notes.scailo_pb2.CreditNotesList]:
        ...
    def count_in_status(self, req: ClientRequest[base.scailo_pb2.CountInSLCStatusRequest]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def count(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def accrued_value(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceCountReq]) -> ServerResponse[base.scailo_pb2.SumResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[credit_notes.scailo_pb2.CreditNotesServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

CREDIT_NOTES_SERVICE_PATH_PREFIX = "/Scailo.CreditNotesService"

def wsgi_credit_notes_service(implementation: CreditNotesServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.CreditNotesService/Create", implementation.create, credit_notes.scailo_pb2.CreditNotesServiceCreateRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/Draft", implementation.draft, credit_notes.scailo_pb2.CreditNotesServiceCreateRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/DraftUpdate", implementation.draft_update, credit_notes.scailo_pb2.CreditNotesServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/SendForVerification", implementation.send_for_verification, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/Verify", implementation.verify, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/Approve", implementation.approve, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/SendForRevision", implementation.send_for_revision, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/RevisionUpdate", implementation.revision_update, credit_notes.scailo_pb2.CreditNotesServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/Halt", implementation.halt, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/Discard", implementation.discard, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/Restore", implementation.restore, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/Repeat", implementation.repeat, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/SendEmail", implementation.send_email, base.scailo_pb2.IdentifierWithEmailAttributes)
    app.register_unary_rpc("/Scailo.CreditNotesService/Autofill", implementation.autofill, credit_notes.scailo_pb2.CreditNotesServiceAutofillRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/CreateMagicLink", implementation.create_magic_link, magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource)
    app.register_unary_rpc("/Scailo.CreditNotesService/AddMultipleCreditNoteItems", implementation.add_multiple_credit_note_items, credit_notes.scailo_pb2.CreditNotesServiceMultipleItemsCreateRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/AddCreditNoteItem", implementation.add_credit_note_item, credit_notes.scailo_pb2.CreditNotesServiceItemCreateRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/ModifyCreditNoteItem", implementation.modify_credit_note_item, credit_notes.scailo_pb2.CreditNotesServiceItemUpdateRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/ApproveCreditNoteItem", implementation.approve_credit_note_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/DeleteCreditNoteItem", implementation.delete_credit_note_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/ReorderCreditNoteItems", implementation.reorder_credit_note_items, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewCreditNoteItemByID", implementation.view_credit_note_item_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewApprovedCreditNoteItems", implementation.view_approved_credit_note_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewUnapprovedCreditNoteItems", implementation.view_unapproved_credit_note_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewCreditNoteItemHistory", implementation.view_credit_note_item_history, credit_notes.scailo_pb2.CreditNoteItemHistoryRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewPaginatedApprovedCreditNoteItems", implementation.view_paginated_approved_credit_note_items, credit_notes.scailo_pb2.CreditNoteItemsSearchRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewPaginatedUnapprovedCreditNoteItems", implementation.view_paginated_unapproved_credit_note_items, credit_notes.scailo_pb2.CreditNoteItemsSearchRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/SearchItemsWithPagination", implementation.search_items_with_pagination, credit_notes.scailo_pb2.CreditNoteItemsSearchRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/DownloadItemsAsCSV", implementation.download_items_as_csv, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.CreditNotesService/DownloadItemsTemplateAsCSV", implementation.download_items_template_as_csv, base.scailo_pb2.Empty)
    app.register_unary_rpc("/Scailo.CreditNotesService/UploadCreditNoteItems", implementation.upload_credit_note_items, base.scailo_pb2.IdentifierUUIDWithFile)
    app.register_unary_rpc("/Scailo.CreditNotesService/AddCreditNoteReference", implementation.add_credit_note_reference, credit_notes.scailo_pb2.CreditNotesServiceReferenceCreateRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/ApproveCreditNoteReference", implementation.approve_credit_note_reference, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/DeleteCreditNoteReference", implementation.delete_credit_note_reference, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewCreditNoteReferenceByID", implementation.view_credit_note_reference_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewCreditNoteReferences", implementation.view_credit_note_references, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewByReferenceID", implementation.view_by_reference_id, base.scailo_pb2.SimpleSearchReq)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewAncillaryParametersByUUID", implementation.view_ancillary_parameters_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewWithPagination", implementation.view_with_pagination, credit_notes.scailo_pb2.CreditNotesServicePaginationReq)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewProspectiveFamilies", implementation.view_prospective_families, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.CreditNotesService/FilterProspectiveFamilies", implementation.filter_prospective_families, families.scailo_pb2.FilterFamiliesReqForIdentifier)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewProspectiveCreditNoteItem", implementation.view_prospective_credit_note_item, credit_notes.scailo_pb2.CreditNoteItemProspectiveInfoRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewReturnedStatistics", implementation.view_returned_statistics, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.CreditNotesService/IsDownloadable", implementation.is_downloadable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.CreditNotesService/DownloadByUUID", implementation.download_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.CreditNotesService/ViewAddedFamilyQuantityForSource", implementation.view_added_family_quantity_for_source, credit_notes.scailo_pb2.CreditNotesServiceAlreadyAddedQuantityForSourceRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/SearchAll", implementation.search_all, credit_notes.scailo_pb2.CreditNotesServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.CreditNotesService/Filter", implementation.filter, credit_notes.scailo_pb2.CreditNotesServiceFilterReq)
    app.register_unary_rpc("/Scailo.CreditNotesService/CountInStatus", implementation.count_in_status, base.scailo_pb2.CountInSLCStatusRequest)
    app.register_unary_rpc("/Scailo.CreditNotesService/Count", implementation.count, credit_notes.scailo_pb2.CreditNotesServiceCountReq)
    app.register_unary_rpc("/Scailo.CreditNotesService/AccruedValue", implementation.accrued_value, credit_notes.scailo_pb2.CreditNotesServiceCountReq)
    app.register_unary_rpc("/Scailo.CreditNotesService/DownloadAsCSV", implementation.download_as_csv, credit_notes.scailo_pb2.CreditNotesServiceFilterReq)
    return app
