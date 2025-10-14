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

from scailo_sdk import base, equations_sales_bundles, magic_links

class EquationsSalesBundlesServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def create(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Draft"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DraftUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft_update(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/SendForVerification"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Verify"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Approve"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/SendForRevision"
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
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/RevisionUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def revision_update(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Halt"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Discard"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Restore"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Complete"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Repeat"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Reopen"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/CommentAdd"
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

    def call_create_magic_link(
        self, req: magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[magic_links.scailo_pb2.MagicLink]:
        """Low-level method to call CreateMagicLink, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/CreateMagicLink"
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

    def call_clone(
        self, req: base.scailo_pb2.CloneRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Clone, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Clone"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def clone(
        self, req: base.scailo_pb2.CloneRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_clone(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_equation_sales_bundle_item(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddEquationSalesBundleItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/AddEquationSalesBundleItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_equation_sales_bundle_item(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_equation_sales_bundle_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_equation_sales_bundle_item(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyEquationSalesBundleItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ModifyEquationSalesBundleItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_equation_sales_bundle_item(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_equation_sales_bundle_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_equation_sales_bundle_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveEquationSalesBundleItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ApproveEquationSalesBundleItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_equation_sales_bundle_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_equation_sales_bundle_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_equation_sales_bundle_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteEquationSalesBundleItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DeleteEquationSalesBundleItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_equation_sales_bundle_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_equation_sales_bundle_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_equation_sales_bundle_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderEquationSalesBundleItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ReorderEquationSalesBundleItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_equation_sales_bundle_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_equation_sales_bundle_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_equation_sales_bundle_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundleItem]:
        """Low-level method to call ViewEquationSalesBundleItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewEquationSalesBundleItemByID"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundleItem,extra_headers, timeout_seconds)


    def view_equation_sales_bundle_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundleItem:
        response = self.call_view_equation_sales_bundle_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_approved_equation_sales_bundle_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList]:
        """Low-level method to call ViewApprovedEquationSalesBundleItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewApprovedEquationSalesBundleItems"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList,extra_headers, timeout_seconds)


    def view_approved_equation_sales_bundle_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList:
        response = self.call_view_approved_equation_sales_bundle_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_unapproved_equation_sales_bundle_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList]:
        """Low-level method to call ViewUnapprovedEquationSalesBundleItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewUnapprovedEquationSalesBundleItems"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList,extra_headers, timeout_seconds)


    def view_unapproved_equation_sales_bundle_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList:
        response = self.call_view_unapproved_equation_sales_bundle_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_equation_sales_bundle_item_history(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList]:
        """Low-level method to call ViewEquationSalesBundleItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewEquationSalesBundleItemHistory"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList,extra_headers, timeout_seconds)


    def view_equation_sales_bundle_item_history(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList:
        response = self.call_view_equation_sales_bundle_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_approved_equation_sales_bundle_items(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedEquationSalesBundleItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewPaginatedApprovedEquationSalesBundleItems"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_approved_equation_sales_bundle_items(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse:
        response = self.call_view_paginated_approved_equation_sales_bundle_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_unapproved_equation_sales_bundle_items(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedEquationSalesBundleItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewPaginatedUnapprovedEquationSalesBundleItems"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_unapproved_equation_sales_bundle_items(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse:
        response = self.call_view_paginated_unapproved_equation_sales_bundle_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_items_with_pagination(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/SearchItemsWithPagination"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def search_items_with_pagination(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DownloadItemsTemplateAsCSV"
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

    def call_download_tree_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadTreeAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DownloadTreeAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_tree_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_tree_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_upload_equation_sales_bundle_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadEquationSalesBundleItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/UploadEquationSalesBundleItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def upload_equation_sales_bundle_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_upload_equation_sales_bundle_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewByID"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundle,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundle:
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
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewByUUID"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundle,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundle:
        response = self.call_view_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_name(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        """Low-level method to call ViewByName, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewByName"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundle,extra_headers, timeout_seconds)


    def view_by_name(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundle:
        response = self.call_view_by_name(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundle,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundle:
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
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundle,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundle:
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
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList:
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
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewAll"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList:
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
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginationResponse:
        response = self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_for_family_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        """Low-level method to call ViewForFamilyID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewForFamilyID"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundle,extra_headers, timeout_seconds)


    def view_for_family_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundle:
        response = self.call_view_for_family_id(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/IsDownloadable"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DownloadByUUID"
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
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/SearchAll"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList,extra_headers, timeout_seconds)


    def search_all(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Filter"
        return self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList,extra_headers, timeout_seconds)


    def filter(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList:
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/CountInStatus"
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
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_import_from_csv(
        self, req: base.scailo_pb2.StandardFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUIDsList]:
        """Low-level method to call ImportFromCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ImportFromCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUIDsList,extra_headers, timeout_seconds)


    def import_from_csv(
        self, req: base.scailo_pb2.StandardFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUIDsList:
        response = self.call_import_from_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncEquationsSalesBundlesServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def create(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Draft"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DraftUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft_update(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/SendForVerification"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Verify"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Approve"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/SendForRevision"
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
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/RevisionUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def revision_update(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Halt"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Discard"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Restore"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Complete"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Repeat"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Reopen"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/CommentAdd"
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

    async def call_create_magic_link(
        self, req: magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[magic_links.scailo_pb2.MagicLink]:
        """Low-level method to call CreateMagicLink, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/CreateMagicLink"
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

    async def call_clone(
        self, req: base.scailo_pb2.CloneRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Clone, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Clone"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def clone(
        self, req: base.scailo_pb2.CloneRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_clone(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_equation_sales_bundle_item(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddEquationSalesBundleItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/AddEquationSalesBundleItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_equation_sales_bundle_item(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_equation_sales_bundle_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_equation_sales_bundle_item(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyEquationSalesBundleItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ModifyEquationSalesBundleItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_equation_sales_bundle_item(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_equation_sales_bundle_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_equation_sales_bundle_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveEquationSalesBundleItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ApproveEquationSalesBundleItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_equation_sales_bundle_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_equation_sales_bundle_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_equation_sales_bundle_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteEquationSalesBundleItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DeleteEquationSalesBundleItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_equation_sales_bundle_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_equation_sales_bundle_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_equation_sales_bundle_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderEquationSalesBundleItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ReorderEquationSalesBundleItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_equation_sales_bundle_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_equation_sales_bundle_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_equation_sales_bundle_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundleItem]:
        """Low-level method to call ViewEquationSalesBundleItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewEquationSalesBundleItemByID"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundleItem,extra_headers, timeout_seconds)

    async def view_equation_sales_bundle_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundleItem:
        response = await self.call_view_equation_sales_bundle_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_approved_equation_sales_bundle_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList]:
        """Low-level method to call ViewApprovedEquationSalesBundleItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewApprovedEquationSalesBundleItems"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList,extra_headers, timeout_seconds)

    async def view_approved_equation_sales_bundle_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList:
        response = await self.call_view_approved_equation_sales_bundle_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_unapproved_equation_sales_bundle_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList]:
        """Low-level method to call ViewUnapprovedEquationSalesBundleItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewUnapprovedEquationSalesBundleItems"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList,extra_headers, timeout_seconds)

    async def view_unapproved_equation_sales_bundle_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList:
        response = await self.call_view_unapproved_equation_sales_bundle_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_equation_sales_bundle_item_history(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList]:
        """Low-level method to call ViewEquationSalesBundleItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewEquationSalesBundleItemHistory"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList,extra_headers, timeout_seconds)

    async def view_equation_sales_bundle_item_history(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList:
        response = await self.call_view_equation_sales_bundle_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_approved_equation_sales_bundle_items(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedEquationSalesBundleItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewPaginatedApprovedEquationSalesBundleItems"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_approved_equation_sales_bundle_items(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse:
        response = await self.call_view_paginated_approved_equation_sales_bundle_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_unapproved_equation_sales_bundle_items(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedEquationSalesBundleItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewPaginatedUnapprovedEquationSalesBundleItems"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_unapproved_equation_sales_bundle_items(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse:
        response = await self.call_view_paginated_unapproved_equation_sales_bundle_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_items_with_pagination(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/SearchItemsWithPagination"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def search_items_with_pagination(
        self, req: equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DownloadItemsTemplateAsCSV"
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

    async def call_download_tree_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadTreeAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DownloadTreeAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_tree_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_tree_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_upload_equation_sales_bundle_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadEquationSalesBundleItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/UploadEquationSalesBundleItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def upload_equation_sales_bundle_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_upload_equation_sales_bundle_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewByID"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundle,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundle:
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
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundle,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundle:
        response = await self.call_view_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_name(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        """Low-level method to call ViewByName, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewByName"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundle,extra_headers, timeout_seconds)

    async def view_by_name(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundle:
        response = await self.call_view_by_name(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundle,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundle:
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
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundle,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundle:
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
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList:
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
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewAll"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList:
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
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginationResponse:
        response = await self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_for_family_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        """Low-level method to call ViewForFamilyID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ViewForFamilyID"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationSalesBundle,extra_headers, timeout_seconds)

    async def view_for_family_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationSalesBundle:
        response = await self.call_view_for_family_id(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/IsDownloadable"
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DownloadByUUID"
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
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/SearchAll"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Filter"
        return await self._connect_client.call_unary(url, req, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList,extra_headers, timeout_seconds)

    async def filter(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList:
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
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/CountInStatus"
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
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_import_from_csv(
        self, req: base.scailo_pb2.StandardFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUIDsList]:
        """Low-level method to call ImportFromCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.EquationsSalesBundlesService/ImportFromCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUIDsList,extra_headers, timeout_seconds)

    async def import_from_csv(
        self, req: base.scailo_pb2.StandardFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUIDsList:
        response = await self.call_import_from_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class EquationsSalesBundlesServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft_update(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_verification(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def verify(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_revision(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def revision_update(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
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
    def create_magic_link(self, req: ClientRequest[magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource]) -> ServerResponse[magic_links.scailo_pb2.MagicLink]:
        ...
    def clone(self, req: ClientRequest[base.scailo_pb2.CloneRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_equation_sales_bundle_item(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceItemCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_equation_sales_bundle_item(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceItemUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_equation_sales_bundle_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_equation_sales_bundle_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_equation_sales_bundle_items(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_equation_sales_bundle_item_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationSalesBundleItem]:
        ...
    def view_approved_equation_sales_bundle_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList]:
        ...
    def view_unapproved_equation_sales_bundle_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList]:
        ...
    def view_equation_sales_bundle_item_history(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationSalesBundleItemHistoryRequest]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesItemsList]:
        ...
    def view_paginated_approved_equation_sales_bundle_items(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse]:
        ...
    def view_paginated_unapproved_equation_sales_bundle_items(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse]:
        ...
    def search_items_with_pagination(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginatedItemsResponse]:
        ...
    def download_items_as_csv(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def download_items_template_as_csv(self, req: ClientRequest[base.scailo_pb2.Empty]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def download_tree_as_csv(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def upload_equation_sales_bundle_items(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithFile]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        ...
    def view_by_name(self, req: ClientRequest[base.scailo_pb2.SimpleSearchReq]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        ...
    def view_with_pagination(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginationReq]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginationResponse]:
        ...
    def view_for_family_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationSalesBundle]:
        ...
    def is_downloadable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def download_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def search_all(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceSearchAllReq]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        ...
    def filter(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceFilterReq]) -> ServerResponse[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesList]:
        ...
    def count_in_status(self, req: ClientRequest[base.scailo_pb2.CountInSLCStatusRequest]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def count(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def import_from_csv(self, req: ClientRequest[base.scailo_pb2.StandardFile]) -> ServerResponse[base.scailo_pb2.IdentifierUUIDsList]:
        ...

EQUATIONS_SALES_BUNDLES_SERVICE_PATH_PREFIX = "/Scailo.EquationsSalesBundlesService"

def wsgi_equations_sales_bundles_service(implementation: EquationsSalesBundlesServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/Create", implementation.create, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCreateRequest)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/Draft", implementation.draft, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCreateRequest)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/DraftUpdate", implementation.draft_update, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/SendForVerification", implementation.send_for_verification, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/Verify", implementation.verify, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/Approve", implementation.approve, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/SendForRevision", implementation.send_for_revision, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/RevisionUpdate", implementation.revision_update, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/Halt", implementation.halt, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/Discard", implementation.discard, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/Restore", implementation.restore, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/Repeat", implementation.repeat, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/CreateMagicLink", implementation.create_magic_link, magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/Clone", implementation.clone, base.scailo_pb2.CloneRequest)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/AddEquationSalesBundleItem", implementation.add_equation_sales_bundle_item, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceItemCreateRequest)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ModifyEquationSalesBundleItem", implementation.modify_equation_sales_bundle_item, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceItemUpdateRequest)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ApproveEquationSalesBundleItem", implementation.approve_equation_sales_bundle_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/DeleteEquationSalesBundleItem", implementation.delete_equation_sales_bundle_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ReorderEquationSalesBundleItems", implementation.reorder_equation_sales_bundle_items, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewEquationSalesBundleItemByID", implementation.view_equation_sales_bundle_item_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewApprovedEquationSalesBundleItems", implementation.view_approved_equation_sales_bundle_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewUnapprovedEquationSalesBundleItems", implementation.view_unapproved_equation_sales_bundle_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewEquationSalesBundleItemHistory", implementation.view_equation_sales_bundle_item_history, equations_sales_bundles.scailo_pb2.EquationSalesBundleItemHistoryRequest)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewPaginatedApprovedEquationSalesBundleItems", implementation.view_paginated_approved_equation_sales_bundle_items, equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewPaginatedUnapprovedEquationSalesBundleItems", implementation.view_paginated_unapproved_equation_sales_bundle_items, equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/SearchItemsWithPagination", implementation.search_items_with_pagination, equations_sales_bundles.scailo_pb2.EquationSalesBundleItemsSearchRequest)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/DownloadItemsAsCSV", implementation.download_items_as_csv, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/DownloadItemsTemplateAsCSV", implementation.download_items_template_as_csv, base.scailo_pb2.Empty)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/DownloadTreeAsCSV", implementation.download_tree_as_csv, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/UploadEquationSalesBundleItems", implementation.upload_equation_sales_bundle_items, base.scailo_pb2.IdentifierUUIDWithFile)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewByName", implementation.view_by_name, base.scailo_pb2.SimpleSearchReq)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewWithPagination", implementation.view_with_pagination, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServicePaginationReq)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ViewForFamilyID", implementation.view_for_family_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/IsDownloadable", implementation.is_downloadable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/DownloadByUUID", implementation.download_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/SearchAll", implementation.search_all, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/Filter", implementation.filter, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceFilterReq)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/CountInStatus", implementation.count_in_status, base.scailo_pb2.CountInSLCStatusRequest)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/Count", implementation.count, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceCountReq)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/DownloadAsCSV", implementation.download_as_csv, equations_sales_bundles.scailo_pb2.EquationsSalesBundlesServiceFilterReq)
    app.register_unary_rpc("/Scailo.EquationsSalesBundlesService/ImportFromCSV", implementation.import_from_csv, base.scailo_pb2.StandardFile)
    return app
