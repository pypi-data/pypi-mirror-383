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

from scailo_sdk import base, families, magic_links, sales_quotations

class SalesQuotationsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def create(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/Draft"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/DraftUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft_update(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.SalesQuotationsService/SendForVerification"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Verify"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Approve"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/SendForRevision"
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/RevisionUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def revision_update(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Halt"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Discard"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Restore"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Complete"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Repeat"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Reopen"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/CommentAdd"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/SendEmail"
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/Autofill"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def autofill(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_autofill(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_amend(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Amend, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/Amend"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def amend(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_amend(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.SalesQuotationsService/CreateMagicLink"
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

    def call_add_multiple_sales_quotation_items(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceMultipleItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddMultipleSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/AddMultipleSalesQuotationItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_multiple_sales_quotation_items(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceMultipleItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_multiple_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_sales_quotation_item(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call AddSalesQuotationItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/AddSalesQuotationItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def add_sales_quotation_item(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_add_sales_quotation_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_sales_quotation_item(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call ModifySalesQuotationItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ModifySalesQuotationItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def modify_sales_quotation_item(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_modify_sales_quotation_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_sales_quotation_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveSalesQuotationItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ApproveSalesQuotationItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_sales_quotation_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_sales_quotation_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_sales_quotation_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteSalesQuotationItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/DeleteSalesQuotationItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_sales_quotation_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_sales_quotation_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_sales_quotation_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ReorderSalesQuotationItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_sales_quotation_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_sales_quotation_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationItem]:
        """Low-level method to call ViewSalesQuotationItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationItemByID"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationItem,extra_headers, timeout_seconds)


    def view_sales_quotation_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationItem:
        response = self.call_view_sales_quotation_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_sales_quotation_item_price(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.PriceResponse]:
        """Low-level method to call ViewSalesQuotationItemPrice, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationItemPrice"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.PriceResponse,extra_headers, timeout_seconds)


    def view_sales_quotation_item_price(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.PriceResponse:
        response = self.call_view_sales_quotation_item_price(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_approved_sales_quotation_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationItemsList]:
        """Low-level method to call ViewApprovedSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewApprovedSalesQuotationItems"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationItemsList,extra_headers, timeout_seconds)


    def view_approved_sales_quotation_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationItemsList:
        response = self.call_view_approved_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_unapproved_sales_quotation_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationItemsList]:
        """Low-level method to call ViewUnapprovedSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewUnapprovedSalesQuotationItems"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationItemsList,extra_headers, timeout_seconds)


    def view_unapproved_sales_quotation_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationItemsList:
        response = self.call_view_unapproved_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_sales_quotation_item_history(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationItemsList]:
        """Low-level method to call ViewSalesQuotationItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationItemHistory"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationItemsList,extra_headers, timeout_seconds)


    def view_sales_quotation_item_history(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationItemsList:
        response = self.call_view_sales_quotation_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_approved_sales_quotation_items(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewPaginatedApprovedSalesQuotationItems"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_approved_sales_quotation_items(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse:
        response = self.call_view_paginated_approved_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_unapproved_sales_quotation_items(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewPaginatedUnapprovedSalesQuotationItems"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_unapproved_sales_quotation_items(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse:
        response = self.call_view_paginated_unapproved_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_items_with_pagination(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/SearchItemsWithPagination"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def search_items_with_pagination(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.SalesQuotationsService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/DownloadItemsTemplateAsCSV"
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

    def call_upload_sales_quotation_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/UploadSalesQuotationItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def upload_sales_quotation_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_upload_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_sales_quotation_contact(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceContactCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddSalesQuotationContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/AddSalesQuotationContact"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_sales_quotation_contact(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceContactCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_sales_quotation_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_sales_quotation_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveSalesQuotationContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ApproveSalesQuotationContact"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_sales_quotation_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_sales_quotation_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_sales_quotation_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteSalesQuotationContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/DeleteSalesQuotationContact"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_sales_quotation_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_sales_quotation_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_sales_quotation_contact_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationContact]:
        """Low-level method to call ViewSalesQuotationContactByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationContactByID"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationContact,extra_headers, timeout_seconds)


    def view_sales_quotation_contact_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationContact:
        response = self.call_view_sales_quotation_contact_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_sales_quotation_contacts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationContactsList]:
        """Low-level method to call ViewSalesQuotationContacts, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationContacts"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationContactsList,extra_headers, timeout_seconds)


    def view_sales_quotation_contacts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationContactsList:
        response = self.call_view_sales_quotation_contacts(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_sales_quotation_reference(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceReferenceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddSalesQuotationReference, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/AddSalesQuotationReference"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_sales_quotation_reference(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceReferenceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_sales_quotation_reference(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_sales_quotation_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveSalesQuotationReference, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ApproveSalesQuotationReference"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_sales_quotation_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_sales_quotation_reference(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_sales_quotation_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteSalesQuotationReference, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/DeleteSalesQuotationReference"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_sales_quotation_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_sales_quotation_reference(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_sales_quotation_reference_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationReference]:
        """Low-level method to call ViewSalesQuotationReferenceByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationReferenceByID"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationReference,extra_headers, timeout_seconds)


    def view_sales_quotation_reference_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationReference:
        response = self.call_view_sales_quotation_reference_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_sales_quotation_references(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationReferencesList]:
        """Low-level method to call ViewSalesQuotationReferences, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationReferences"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationReferencesList,extra_headers, timeout_seconds)


    def view_sales_quotation_references(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationReferencesList:
        response = self.call_view_sales_quotation_references(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotation]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewByID"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotation,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotation:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotation]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewByUUID"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotation,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotation:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotation]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewByReferenceID"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotation,extra_headers, timeout_seconds)


    def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotation:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotation]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotation,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotation:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotation]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotation,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotation:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsList:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewAll"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsList:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsServicePaginationResponse:
        response = self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_amendments(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.AmendmentLogsList]:
        """Low-level method to call ViewAmendments, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewAmendments"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.AmendmentLogsList,extra_headers, timeout_seconds)


    def view_amendments(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.AmendmentLogsList:
        response = self.call_view_amendments(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewProspectiveFamilies"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/FilterProspectiveFamilies"
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

    def call_view_prospective_sales_quotation_item(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveSalesQuotationItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewProspectiveSalesQuotationItem"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsServiceItemCreateRequest,extra_headers, timeout_seconds)


    def view_prospective_sales_quotation_item(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsServiceItemCreateRequest:
        response = self.call_view_prospective_sales_quotation_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_associated_sales_orders_i_ds(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call ViewAssociatedSalesOrdersIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewAssociatedSalesOrdersIDs"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def view_associated_sales_orders_i_ds(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_view_associated_sales_orders_i_ds(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.SalesQuotationsService/IsDownloadable"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/DownloadByUUID"
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/SearchAll"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsList,extra_headers, timeout_seconds)


    def search_all(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/Filter"
        return self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsList,extra_headers, timeout_seconds)


    def filter(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsList:
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
        url = self.base_url + "/Scailo.SalesQuotationsService/CountInStatus"
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncSalesQuotationsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def create(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/Draft"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/DraftUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft_update(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.SalesQuotationsService/SendForVerification"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Verify"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Approve"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/SendForRevision"
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/RevisionUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def revision_update(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Halt"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Discard"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Restore"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Complete"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Repeat"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/Reopen"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/CommentAdd"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/SendEmail"
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/Autofill"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def autofill(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_autofill(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_amend(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Amend, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/Amend"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def amend(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_amend(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.SalesQuotationsService/CreateMagicLink"
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

    async def call_add_multiple_sales_quotation_items(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceMultipleItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddMultipleSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/AddMultipleSalesQuotationItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_multiple_sales_quotation_items(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceMultipleItemsCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_multiple_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_sales_quotation_item(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call AddSalesQuotationItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/AddSalesQuotationItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def add_sales_quotation_item(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_add_sales_quotation_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_sales_quotation_item(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call ModifySalesQuotationItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ModifySalesQuotationItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def modify_sales_quotation_item(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_modify_sales_quotation_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_sales_quotation_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveSalesQuotationItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ApproveSalesQuotationItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_sales_quotation_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_sales_quotation_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_sales_quotation_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteSalesQuotationItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/DeleteSalesQuotationItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_sales_quotation_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_sales_quotation_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_sales_quotation_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ReorderSalesQuotationItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_sales_quotation_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_sales_quotation_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationItem]:
        """Low-level method to call ViewSalesQuotationItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationItemByID"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationItem,extra_headers, timeout_seconds)

    async def view_sales_quotation_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationItem:
        response = await self.call_view_sales_quotation_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_sales_quotation_item_price(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.PriceResponse]:
        """Low-level method to call ViewSalesQuotationItemPrice, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationItemPrice"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.PriceResponse,extra_headers, timeout_seconds)

    async def view_sales_quotation_item_price(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.PriceResponse:
        response = await self.call_view_sales_quotation_item_price(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_approved_sales_quotation_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationItemsList]:
        """Low-level method to call ViewApprovedSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewApprovedSalesQuotationItems"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationItemsList,extra_headers, timeout_seconds)

    async def view_approved_sales_quotation_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationItemsList:
        response = await self.call_view_approved_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_unapproved_sales_quotation_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationItemsList]:
        """Low-level method to call ViewUnapprovedSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewUnapprovedSalesQuotationItems"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationItemsList,extra_headers, timeout_seconds)

    async def view_unapproved_sales_quotation_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationItemsList:
        response = await self.call_view_unapproved_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_sales_quotation_item_history(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationItemsList]:
        """Low-level method to call ViewSalesQuotationItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationItemHistory"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationItemsList,extra_headers, timeout_seconds)

    async def view_sales_quotation_item_history(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationItemsList:
        response = await self.call_view_sales_quotation_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_approved_sales_quotation_items(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewPaginatedApprovedSalesQuotationItems"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_approved_sales_quotation_items(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse:
        response = await self.call_view_paginated_approved_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_unapproved_sales_quotation_items(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewPaginatedUnapprovedSalesQuotationItems"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_unapproved_sales_quotation_items(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse:
        response = await self.call_view_paginated_unapproved_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_items_with_pagination(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/SearchItemsWithPagination"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def search_items_with_pagination(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.SalesQuotationsService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/DownloadItemsTemplateAsCSV"
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

    async def call_upload_sales_quotation_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadSalesQuotationItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/UploadSalesQuotationItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def upload_sales_quotation_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_upload_sales_quotation_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_sales_quotation_contact(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceContactCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddSalesQuotationContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/AddSalesQuotationContact"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_sales_quotation_contact(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceContactCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_sales_quotation_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_sales_quotation_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveSalesQuotationContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ApproveSalesQuotationContact"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_sales_quotation_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_sales_quotation_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_sales_quotation_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteSalesQuotationContact, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/DeleteSalesQuotationContact"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_sales_quotation_contact(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_sales_quotation_contact(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_sales_quotation_contact_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationContact]:
        """Low-level method to call ViewSalesQuotationContactByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationContactByID"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationContact,extra_headers, timeout_seconds)

    async def view_sales_quotation_contact_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationContact:
        response = await self.call_view_sales_quotation_contact_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_sales_quotation_contacts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationContactsList]:
        """Low-level method to call ViewSalesQuotationContacts, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationContacts"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationContactsList,extra_headers, timeout_seconds)

    async def view_sales_quotation_contacts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationContactsList:
        response = await self.call_view_sales_quotation_contacts(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_sales_quotation_reference(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceReferenceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddSalesQuotationReference, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/AddSalesQuotationReference"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_sales_quotation_reference(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceReferenceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_sales_quotation_reference(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_sales_quotation_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveSalesQuotationReference, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ApproveSalesQuotationReference"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_sales_quotation_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_sales_quotation_reference(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_sales_quotation_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteSalesQuotationReference, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/DeleteSalesQuotationReference"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_sales_quotation_reference(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_sales_quotation_reference(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_sales_quotation_reference_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationReference]:
        """Low-level method to call ViewSalesQuotationReferenceByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationReferenceByID"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationReference,extra_headers, timeout_seconds)

    async def view_sales_quotation_reference_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationReference:
        response = await self.call_view_sales_quotation_reference_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_sales_quotation_references(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationReferencesList]:
        """Low-level method to call ViewSalesQuotationReferences, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewSalesQuotationReferences"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationReferencesList,extra_headers, timeout_seconds)

    async def view_sales_quotation_references(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationReferencesList:
        response = await self.call_view_sales_quotation_references(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotation]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewByID"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotation,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotation:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotation]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotation,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotation:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotation]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewByReferenceID"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotation,extra_headers, timeout_seconds)

    async def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotation:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotation]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotation,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotation:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotation]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotation,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotation:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsList:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewAll"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsList:
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
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsServicePaginationResponse:
        response = await self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_amendments(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.AmendmentLogsList]:
        """Low-level method to call ViewAmendments, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewAmendments"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.AmendmentLogsList,extra_headers, timeout_seconds)

    async def view_amendments(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.AmendmentLogsList:
        response = await self.call_view_amendments(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewProspectiveFamilies"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/FilterProspectiveFamilies"
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

    async def call_view_prospective_sales_quotation_item(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveSalesQuotationItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewProspectiveSalesQuotationItem"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsServiceItemCreateRequest,extra_headers, timeout_seconds)

    async def view_prospective_sales_quotation_item(
        self, req: sales_quotations.scailo_pb2.SalesQuotationItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsServiceItemCreateRequest:
        response = await self.call_view_prospective_sales_quotation_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_associated_sales_orders_i_ds(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call ViewAssociatedSalesOrdersIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/ViewAssociatedSalesOrdersIDs"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def view_associated_sales_orders_i_ds(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_view_associated_sales_orders_i_ds(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.SalesQuotationsService/IsDownloadable"
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
        url = self.base_url + "/Scailo.SalesQuotationsService/DownloadByUUID"
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/SearchAll"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[sales_quotations.scailo_pb2.SalesQuotationsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/Filter"
        return await self._connect_client.call_unary(url, req, sales_quotations.scailo_pb2.SalesQuotationsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> sales_quotations.scailo_pb2.SalesQuotationsList:
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
        url = self.base_url + "/Scailo.SalesQuotationsService/CountInStatus"
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.SalesQuotationsService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: sales_quotations.scailo_pb2.SalesQuotationsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
class SalesQuotationsServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft_update(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_verification(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def verify(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_revision(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def revision_update(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
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
    def autofill(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceAutofillRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def amend(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def create_magic_link(self, req: ClientRequest[magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource]) -> ServerResponse[magic_links.scailo_pb2.MagicLink]:
        ...
    def add_multiple_sales_quotation_items(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceMultipleItemsCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_sales_quotation_item(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceItemCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def modify_sales_quotation_item(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceItemUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def approve_sales_quotation_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_sales_quotation_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_sales_quotation_items(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_sales_quotation_item_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationItem]:
        ...
    def view_sales_quotation_item_price(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationItemProspectiveInfoRequest]) -> ServerResponse[base.scailo_pb2.PriceResponse]:
        ...
    def view_approved_sales_quotation_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationItemsList]:
        ...
    def view_unapproved_sales_quotation_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationItemsList]:
        ...
    def view_sales_quotation_item_history(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationItemHistoryRequest]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationItemsList]:
        ...
    def view_paginated_approved_sales_quotation_items(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse]:
        ...
    def view_paginated_unapproved_sales_quotation_items(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse]:
        ...
    def search_items_with_pagination(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationsServicePaginatedItemsResponse]:
        ...
    def download_items_as_csv(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def download_items_template_as_csv(self, req: ClientRequest[base.scailo_pb2.Empty]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def upload_sales_quotation_items(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithFile]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def add_sales_quotation_contact(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceContactCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_sales_quotation_contact(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_sales_quotation_contact(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_sales_quotation_contact_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationContact]:
        ...
    def view_sales_quotation_contacts(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationContactsList]:
        ...
    def add_sales_quotation_reference(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceReferenceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_sales_quotation_reference(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_sales_quotation_reference(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_sales_quotation_reference_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationReference]:
        ...
    def view_sales_quotation_references(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationReferencesList]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotation]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotation]:
        ...
    def view_by_reference_id(self, req: ClientRequest[base.scailo_pb2.SimpleSearchReq]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotation]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotation]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotation]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationsList]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationsList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationsList]:
        ...
    def view_with_pagination(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServicePaginationReq]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationsServicePaginationResponse]:
        ...
    def view_amendments(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[base.scailo_pb2.AmendmentLogsList]:
        ...
    def view_prospective_families(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def filter_prospective_families(self, req: ClientRequest[families.scailo_pb2.FilterFamiliesReqForIdentifier]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def view_prospective_sales_quotation_item(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationItemProspectiveInfoRequest]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationsServiceItemCreateRequest]:
        ...
    def view_associated_sales_orders_i_ds(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def is_downloadable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def download_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def search_all(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceSearchAllReq]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationsList]:
        ...
    def filter(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceFilterReq]) -> ServerResponse[sales_quotations.scailo_pb2.SalesQuotationsList]:
        ...
    def count_in_status(self, req: ClientRequest[base.scailo_pb2.CountInSLCStatusRequest]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def count(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[sales_quotations.scailo_pb2.SalesQuotationsServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

SALES_QUOTATIONS_SERVICE_PATH_PREFIX = "/Scailo.SalesQuotationsService"

def wsgi_sales_quotations_service(implementation: SalesQuotationsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Create", implementation.create, sales_quotations.scailo_pb2.SalesQuotationsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Draft", implementation.draft, sales_quotations.scailo_pb2.SalesQuotationsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/DraftUpdate", implementation.draft_update, sales_quotations.scailo_pb2.SalesQuotationsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/SendForVerification", implementation.send_for_verification, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Verify", implementation.verify, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Approve", implementation.approve, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/SendForRevision", implementation.send_for_revision, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/RevisionUpdate", implementation.revision_update, sales_quotations.scailo_pb2.SalesQuotationsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Halt", implementation.halt, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Discard", implementation.discard, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Restore", implementation.restore, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Repeat", implementation.repeat, base.scailo_pb2.RepeatWithDeliveryDate)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/SendEmail", implementation.send_email, base.scailo_pb2.IdentifierWithEmailAttributes)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Autofill", implementation.autofill, sales_quotations.scailo_pb2.SalesQuotationsServiceAutofillRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Amend", implementation.amend, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/CreateMagicLink", implementation.create_magic_link, magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/AddMultipleSalesQuotationItems", implementation.add_multiple_sales_quotation_items, sales_quotations.scailo_pb2.SalesQuotationsServiceMultipleItemsCreateRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/AddSalesQuotationItem", implementation.add_sales_quotation_item, sales_quotations.scailo_pb2.SalesQuotationsServiceItemCreateRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ModifySalesQuotationItem", implementation.modify_sales_quotation_item, sales_quotations.scailo_pb2.SalesQuotationsServiceItemUpdateRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ApproveSalesQuotationItem", implementation.approve_sales_quotation_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/DeleteSalesQuotationItem", implementation.delete_sales_quotation_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ReorderSalesQuotationItems", implementation.reorder_sales_quotation_items, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewSalesQuotationItemByID", implementation.view_sales_quotation_item_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewSalesQuotationItemPrice", implementation.view_sales_quotation_item_price, sales_quotations.scailo_pb2.SalesQuotationItemProspectiveInfoRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewApprovedSalesQuotationItems", implementation.view_approved_sales_quotation_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewUnapprovedSalesQuotationItems", implementation.view_unapproved_sales_quotation_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewSalesQuotationItemHistory", implementation.view_sales_quotation_item_history, sales_quotations.scailo_pb2.SalesQuotationItemHistoryRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewPaginatedApprovedSalesQuotationItems", implementation.view_paginated_approved_sales_quotation_items, sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewPaginatedUnapprovedSalesQuotationItems", implementation.view_paginated_unapproved_sales_quotation_items, sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/SearchItemsWithPagination", implementation.search_items_with_pagination, sales_quotations.scailo_pb2.SalesQuotationItemsSearchRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/DownloadItemsAsCSV", implementation.download_items_as_csv, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/DownloadItemsTemplateAsCSV", implementation.download_items_template_as_csv, base.scailo_pb2.Empty)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/UploadSalesQuotationItems", implementation.upload_sales_quotation_items, base.scailo_pb2.IdentifierUUIDWithFile)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/AddSalesQuotationContact", implementation.add_sales_quotation_contact, sales_quotations.scailo_pb2.SalesQuotationsServiceContactCreateRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ApproveSalesQuotationContact", implementation.approve_sales_quotation_contact, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/DeleteSalesQuotationContact", implementation.delete_sales_quotation_contact, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewSalesQuotationContactByID", implementation.view_sales_quotation_contact_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewSalesQuotationContacts", implementation.view_sales_quotation_contacts, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/AddSalesQuotationReference", implementation.add_sales_quotation_reference, sales_quotations.scailo_pb2.SalesQuotationsServiceReferenceCreateRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ApproveSalesQuotationReference", implementation.approve_sales_quotation_reference, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/DeleteSalesQuotationReference", implementation.delete_sales_quotation_reference, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewSalesQuotationReferenceByID", implementation.view_sales_quotation_reference_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewSalesQuotationReferences", implementation.view_sales_quotation_references, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewByReferenceID", implementation.view_by_reference_id, base.scailo_pb2.SimpleSearchReq)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewWithPagination", implementation.view_with_pagination, sales_quotations.scailo_pb2.SalesQuotationsServicePaginationReq)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewAmendments", implementation.view_amendments, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewProspectiveFamilies", implementation.view_prospective_families, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/FilterProspectiveFamilies", implementation.filter_prospective_families, families.scailo_pb2.FilterFamiliesReqForIdentifier)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewProspectiveSalesQuotationItem", implementation.view_prospective_sales_quotation_item, sales_quotations.scailo_pb2.SalesQuotationItemProspectiveInfoRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/ViewAssociatedSalesOrdersIDs", implementation.view_associated_sales_orders_i_ds, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/IsDownloadable", implementation.is_downloadable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/DownloadByUUID", implementation.download_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/SearchAll", implementation.search_all, sales_quotations.scailo_pb2.SalesQuotationsServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Filter", implementation.filter, sales_quotations.scailo_pb2.SalesQuotationsServiceFilterReq)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/CountInStatus", implementation.count_in_status, base.scailo_pb2.CountInSLCStatusRequest)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/Count", implementation.count, sales_quotations.scailo_pb2.SalesQuotationsServiceCountReq)
    app.register_unary_rpc("/Scailo.SalesQuotationsService/DownloadAsCSV", implementation.download_as_csv, sales_quotations.scailo_pb2.SalesQuotationsServiceFilterReq)
    return app
