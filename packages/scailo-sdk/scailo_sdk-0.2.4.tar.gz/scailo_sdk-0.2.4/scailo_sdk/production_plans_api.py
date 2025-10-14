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

from scailo_sdk import base, families, magic_links, production_plans

class ProductionPlansServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def create(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/Draft"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/DraftUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def draft_update(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ProductionPlansService/SendForVerification"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Verify"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Approve"
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
        url = self.base_url + "/Scailo.ProductionPlansService/SendForRevision"
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/RevisionUpdate"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def revision_update(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ProductionPlansService/Halt"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Discard"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Restore"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Complete"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Repeat"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Reopen"
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
        url = self.base_url + "/Scailo.ProductionPlansService/CommentAdd"
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
        url = self.base_url + "/Scailo.ProductionPlansService/SendEmail"
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
        url = self.base_url + "/Scailo.ProductionPlansService/CreateMagicLink"
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/Autofill"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def autofill(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ProductionPlansService/IsCompletable"
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

    def call_add_production_plan_item(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddProductionPlanItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/AddProductionPlanItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_production_plan_item(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_production_plan_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_production_plan_item(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyProductionPlanItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ModifyProductionPlanItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_production_plan_item(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_production_plan_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_approve_production_plan_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveProductionPlanItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ApproveProductionPlanItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def approve_production_plan_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_approve_production_plan_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_production_plan_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteProductionPlanItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/DeleteProductionPlanItem"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_production_plan_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_production_plan_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_production_plan_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderProductionPlanItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ReorderProductionPlanItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_production_plan_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_production_plan_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_production_plan_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlanItem]:
        """Low-level method to call ViewProductionPlanItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewProductionPlanItemByID"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlanItem,extra_headers, timeout_seconds)


    def view_production_plan_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlanItem:
        response = self.call_view_production_plan_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_approved_production_plan_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansItemsList]:
        """Low-level method to call ViewApprovedProductionPlanItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewApprovedProductionPlanItems"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansItemsList,extra_headers, timeout_seconds)


    def view_approved_production_plan_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansItemsList:
        response = self.call_view_approved_production_plan_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_unapproved_production_plan_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansItemsList]:
        """Low-level method to call ViewUnapprovedProductionPlanItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewUnapprovedProductionPlanItems"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansItemsList,extra_headers, timeout_seconds)


    def view_unapproved_production_plan_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansItemsList:
        response = self.call_view_unapproved_production_plan_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_production_plan_item_history(
        self, req: production_plans.scailo_pb2.ProductionPlanItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansItemsList]:
        """Low-level method to call ViewProductionPlanItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewProductionPlanItemHistory"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansItemsList,extra_headers, timeout_seconds)


    def view_production_plan_item_history(
        self, req: production_plans.scailo_pb2.ProductionPlanItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansItemsList:
        response = self.call_view_production_plan_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_approved_production_plan_items(
        self, req: production_plans.scailo_pb2.ProductionPlanItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedProductionPlanItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewPaginatedApprovedProductionPlanItems"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_approved_production_plan_items(
        self, req: production_plans.scailo_pb2.ProductionPlanItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse:
        response = self.call_view_paginated_approved_production_plan_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_unapproved_production_plan_items(
        self, req: production_plans.scailo_pb2.ProductionPlanItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedProductionPlanItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewPaginatedUnapprovedProductionPlanItems"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def view_paginated_unapproved_production_plan_items(
        self, req: production_plans.scailo_pb2.ProductionPlanItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse:
        response = self.call_view_paginated_unapproved_production_plan_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_items_with_pagination(
        self, req: production_plans.scailo_pb2.ProductionPlanItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/SearchItemsWithPagination"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse,extra_headers, timeout_seconds)


    def search_items_with_pagination(
        self, req: production_plans.scailo_pb2.ProductionPlanItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.ProductionPlansService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.ProductionPlansService/DownloadItemsTemplateAsCSV"
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

    def call_upload_production_plan_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadProductionPlanItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/UploadProductionPlanItems"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def upload_production_plan_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_upload_production_plan_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlan]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewByID"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlan,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlan:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlan]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewByUUID"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlan,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlan:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlan]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewByReferenceID"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlan,extra_headers, timeout_seconds)


    def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlan:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlan]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlan,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlan:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlan]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlan,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlan:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansList:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlanAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewAncillaryParametersByUUID"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlanAncillaryParameters,extra_headers, timeout_seconds)


    def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlanAncillaryParameters:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewAll"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansList:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: production_plans.scailo_pb2.ProductionPlansServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: production_plans.scailo_pb2.ProductionPlansServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansServicePaginationResponse:
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
        url = self.base_url + "/Scailo.ProductionPlansService/ViewProspectiveFamilies"
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
        url = self.base_url + "/Scailo.ProductionPlansService/FilterProspectiveFamilies"
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

    def call_view_prospective_production_plan_item(
        self, req: production_plans.scailo_pb2.ProductionPlanItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveProductionPlanItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewProspectiveProductionPlanItem"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansServiceItemCreateRequest,extra_headers, timeout_seconds)


    def view_prospective_production_plan_item(
        self, req: production_plans.scailo_pb2.ProductionPlanItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansServiceItemCreateRequest:
        response = self.call_view_prospective_production_plan_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_remaining_production_quantity(
        self, req: production_plans.scailo_pb2.ProductionPlanItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call ViewRemainingProductionQuantity, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewRemainingProductionQuantity"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)


    def view_remaining_production_quantity(
        self, req: production_plans.scailo_pb2.ProductionPlanItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = self.call_view_remaining_production_quantity(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_production_statistics(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlanProductionStatisticsList]:
        """Low-level method to call ViewProductionStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewProductionStatistics"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlanProductionStatisticsList,extra_headers, timeout_seconds)


    def view_production_statistics(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlanProductionStatisticsList:
        response = self.call_view_production_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_families_in_production_plan(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call ViewFamiliesInProductionPlan, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewFamiliesInProductionPlan"
        return self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)


    def view_families_in_production_plan(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = self.call_view_families_in_production_plan(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter_families_in_production_plan(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call FilterFamiliesInProductionPlan, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/FilterFamiliesInProductionPlan"
        return self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)


    def filter_families_in_production_plan(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = self.call_filter_families_in_production_plan(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_added_family_quantity_for_source(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call ViewAddedFamilyQuantityForSource, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewAddedFamilyQuantityForSource"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)


    def view_added_family_quantity_for_source(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = self.call_view_added_family_quantity_for_source(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.ProductionPlansService/IsDownloadable"
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
        url = self.base_url + "/Scailo.ProductionPlansService/DownloadByUUID"
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/SearchAll"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansList,extra_headers, timeout_seconds)


    def search_all(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/Filter"
        return self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansList,extra_headers, timeout_seconds)


    def filter(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansList:
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
        url = self.base_url + "/Scailo.ProductionPlansService/CountInStatus"
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncProductionPlansServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def create(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Draft, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/Draft"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DraftUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/DraftUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def draft_update(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ProductionPlansService/SendForVerification"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Verify"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Approve"
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
        url = self.base_url + "/Scailo.ProductionPlansService/SendForRevision"
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call RevisionUpdate, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/RevisionUpdate"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def revision_update(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ProductionPlansService/Halt"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Discard"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Restore"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Complete"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Repeat"
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
        url = self.base_url + "/Scailo.ProductionPlansService/Reopen"
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
        url = self.base_url + "/Scailo.ProductionPlansService/CommentAdd"
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
        url = self.base_url + "/Scailo.ProductionPlansService/SendEmail"
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
        url = self.base_url + "/Scailo.ProductionPlansService/CreateMagicLink"
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call Autofill, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/Autofill"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def autofill(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceAutofillRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ProductionPlansService/IsCompletable"
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

    async def call_add_production_plan_item(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddProductionPlanItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/AddProductionPlanItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_production_plan_item(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceItemCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_production_plan_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_production_plan_item(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyProductionPlanItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ModifyProductionPlanItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_production_plan_item(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceItemUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_production_plan_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_approve_production_plan_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ApproveProductionPlanItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ApproveProductionPlanItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def approve_production_plan_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_approve_production_plan_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_production_plan_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteProductionPlanItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/DeleteProductionPlanItem"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_production_plan_item(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_production_plan_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_production_plan_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderProductionPlanItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ReorderProductionPlanItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_production_plan_items(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_production_plan_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_production_plan_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlanItem]:
        """Low-level method to call ViewProductionPlanItemByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewProductionPlanItemByID"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlanItem,extra_headers, timeout_seconds)

    async def view_production_plan_item_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlanItem:
        response = await self.call_view_production_plan_item_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_approved_production_plan_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansItemsList]:
        """Low-level method to call ViewApprovedProductionPlanItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewApprovedProductionPlanItems"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansItemsList,extra_headers, timeout_seconds)

    async def view_approved_production_plan_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansItemsList:
        response = await self.call_view_approved_production_plan_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_unapproved_production_plan_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansItemsList]:
        """Low-level method to call ViewUnapprovedProductionPlanItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewUnapprovedProductionPlanItems"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansItemsList,extra_headers, timeout_seconds)

    async def view_unapproved_production_plan_items(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansItemsList:
        response = await self.call_view_unapproved_production_plan_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_production_plan_item_history(
        self, req: production_plans.scailo_pb2.ProductionPlanItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansItemsList]:
        """Low-level method to call ViewProductionPlanItemHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewProductionPlanItemHistory"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansItemsList,extra_headers, timeout_seconds)

    async def view_production_plan_item_history(
        self, req: production_plans.scailo_pb2.ProductionPlanItemHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansItemsList:
        response = await self.call_view_production_plan_item_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_approved_production_plan_items(
        self, req: production_plans.scailo_pb2.ProductionPlanItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedApprovedProductionPlanItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewPaginatedApprovedProductionPlanItems"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_approved_production_plan_items(
        self, req: production_plans.scailo_pb2.ProductionPlanItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse:
        response = await self.call_view_paginated_approved_production_plan_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_unapproved_production_plan_items(
        self, req: production_plans.scailo_pb2.ProductionPlanItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse]:
        """Low-level method to call ViewPaginatedUnapprovedProductionPlanItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewPaginatedUnapprovedProductionPlanItems"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def view_paginated_unapproved_production_plan_items(
        self, req: production_plans.scailo_pb2.ProductionPlanItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse:
        response = await self.call_view_paginated_unapproved_production_plan_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_items_with_pagination(
        self, req: production_plans.scailo_pb2.ProductionPlanItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse]:
        """Low-level method to call SearchItemsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/SearchItemsWithPagination"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse,extra_headers, timeout_seconds)

    async def search_items_with_pagination(
        self, req: production_plans.scailo_pb2.ProductionPlanItemsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse:
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
        url = self.base_url + "/Scailo.ProductionPlansService/DownloadItemsAsCSV"
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
        url = self.base_url + "/Scailo.ProductionPlansService/DownloadItemsTemplateAsCSV"
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

    async def call_upload_production_plan_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadProductionPlanItems, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/UploadProductionPlanItems"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def upload_production_plan_items(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_upload_production_plan_items(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlan]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewByID"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlan,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlan:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlan]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlan,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlan:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlan]:
        """Low-level method to call ViewByReferenceID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewByReferenceID"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlan,extra_headers, timeout_seconds)

    async def view_by_reference_id(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlan:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlan]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlan,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlan:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlan]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlan,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlan:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansList:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlanAncillaryParameters]:
        """Low-level method to call ViewAncillaryParametersByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewAncillaryParametersByUUID"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlanAncillaryParameters,extra_headers, timeout_seconds)

    async def view_ancillary_parameters_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlanAncillaryParameters:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewAll"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansList:
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
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: production_plans.scailo_pb2.ProductionPlansServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: production_plans.scailo_pb2.ProductionPlansServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansServicePaginationResponse:
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
        url = self.base_url + "/Scailo.ProductionPlansService/ViewProspectiveFamilies"
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
        url = self.base_url + "/Scailo.ProductionPlansService/FilterProspectiveFamilies"
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

    async def call_view_prospective_production_plan_item(
        self, req: production_plans.scailo_pb2.ProductionPlanItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansServiceItemCreateRequest]:
        """Low-level method to call ViewProspectiveProductionPlanItem, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewProspectiveProductionPlanItem"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansServiceItemCreateRequest,extra_headers, timeout_seconds)

    async def view_prospective_production_plan_item(
        self, req: production_plans.scailo_pb2.ProductionPlanItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansServiceItemCreateRequest:
        response = await self.call_view_prospective_production_plan_item(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_remaining_production_quantity(
        self, req: production_plans.scailo_pb2.ProductionPlanItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call ViewRemainingProductionQuantity, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewRemainingProductionQuantity"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)

    async def view_remaining_production_quantity(
        self, req: production_plans.scailo_pb2.ProductionPlanItemProspectiveInfoRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = await self.call_view_remaining_production_quantity(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_production_statistics(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlanProductionStatisticsList]:
        """Low-level method to call ViewProductionStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewProductionStatistics"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlanProductionStatisticsList,extra_headers, timeout_seconds)

    async def view_production_statistics(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlanProductionStatisticsList:
        response = await self.call_view_production_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_families_in_production_plan(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call ViewFamiliesInProductionPlan, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewFamiliesInProductionPlan"
        return await self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)

    async def view_families_in_production_plan(
        self, req: base.scailo_pb2.IdentifierWithSearchKey,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = await self.call_view_families_in_production_plan(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter_families_in_production_plan(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[families.scailo_pb2.FamiliesList]:
        """Low-level method to call FilterFamiliesInProductionPlan, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/FilterFamiliesInProductionPlan"
        return await self._connect_client.call_unary(url, req, families.scailo_pb2.FamiliesList,extra_headers, timeout_seconds)

    async def filter_families_in_production_plan(
        self, req: families.scailo_pb2.FilterFamiliesReqForIdentifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> families.scailo_pb2.FamiliesList:
        response = await self.call_filter_families_in_production_plan(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_added_family_quantity_for_source(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call ViewAddedFamilyQuantityForSource, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/ViewAddedFamilyQuantityForSource"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)

    async def view_added_family_quantity_for_source(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceAlreadyAddedQuantityForSourceRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = await self.call_view_added_family_quantity_for_source(req, extra_headers, timeout_seconds)
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
        url = self.base_url + "/Scailo.ProductionPlansService/IsDownloadable"
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
        url = self.base_url + "/Scailo.ProductionPlansService/DownloadByUUID"
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/SearchAll"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[production_plans.scailo_pb2.ProductionPlansList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/Filter"
        return await self._connect_client.call_unary(url, req, production_plans.scailo_pb2.ProductionPlansList,extra_headers, timeout_seconds)

    async def filter(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> production_plans.scailo_pb2.ProductionPlansList:
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
        url = self.base_url + "/Scailo.ProductionPlansService/CountInStatus"
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: production_plans.scailo_pb2.ProductionPlansServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ProductionPlansService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: production_plans.scailo_pb2.ProductionPlansServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
class ProductionPlansServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlansServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlansServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def draft_update(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlansServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_verification(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def verify(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def send_for_revision(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def revision_update(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlansServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
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
    def autofill(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlansServiceAutofillRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def is_completable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def add_production_plan_item(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlansServiceItemCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_production_plan_item(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlansServiceItemUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def approve_production_plan_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_production_plan_item(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_production_plan_items(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_production_plan_item_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlanItem]:
        ...
    def view_approved_production_plan_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlansItemsList]:
        ...
    def view_unapproved_production_plan_items(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlansItemsList]:
        ...
    def view_production_plan_item_history(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlanItemHistoryRequest]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlansItemsList]:
        ...
    def view_paginated_approved_production_plan_items(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlanItemsSearchRequest]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse]:
        ...
    def view_paginated_unapproved_production_plan_items(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlanItemsSearchRequest]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse]:
        ...
    def search_items_with_pagination(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlanItemsSearchRequest]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlansServicePaginatedItemsResponse]:
        ...
    def download_items_as_csv(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def download_items_template_as_csv(self, req: ClientRequest[base.scailo_pb2.Empty]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def upload_production_plan_items(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithFile]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlan]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlan]:
        ...
    def view_by_reference_id(self, req: ClientRequest[base.scailo_pb2.SimpleSearchReq]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlan]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlan]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlan]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlansList]:
        ...
    def view_ancillary_parameters_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlanAncillaryParameters]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlansList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlansList]:
        ...
    def view_with_pagination(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlansServicePaginationReq]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlansServicePaginationResponse]:
        ...
    def view_prospective_families(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def filter_prospective_families(self, req: ClientRequest[families.scailo_pb2.FilterFamiliesReqForIdentifier]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def view_prospective_production_plan_item(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlanItemProspectiveInfoRequest]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlansServiceItemCreateRequest]:
        ...
    def view_remaining_production_quantity(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlanItemProspectiveInfoRequest]) -> ServerResponse[base.scailo_pb2.QuantityResponse]:
        ...
    def view_production_statistics(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlanProductionStatisticsList]:
        ...
    def view_families_in_production_plan(self, req: ClientRequest[base.scailo_pb2.IdentifierWithSearchKey]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def filter_families_in_production_plan(self, req: ClientRequest[families.scailo_pb2.FilterFamiliesReqForIdentifier]) -> ServerResponse[families.scailo_pb2.FamiliesList]:
        ...
    def view_added_family_quantity_for_source(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlansServiceAlreadyAddedQuantityForSourceRequest]) -> ServerResponse[base.scailo_pb2.QuantityResponse]:
        ...
    def is_downloadable(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def download_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def search_all(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlansServiceSearchAllReq]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlansList]:
        ...
    def filter(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlansServiceFilterReq]) -> ServerResponse[production_plans.scailo_pb2.ProductionPlansList]:
        ...
    def count_in_status(self, req: ClientRequest[base.scailo_pb2.CountInSLCStatusRequest]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def count(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlansServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[production_plans.scailo_pb2.ProductionPlansServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

PRODUCTION_PLANS_SERVICE_PATH_PREFIX = "/Scailo.ProductionPlansService"

def wsgi_production_plans_service(implementation: ProductionPlansServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.ProductionPlansService/Create", implementation.create, production_plans.scailo_pb2.ProductionPlansServiceCreateRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/Draft", implementation.draft, production_plans.scailo_pb2.ProductionPlansServiceCreateRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/DraftUpdate", implementation.draft_update, production_plans.scailo_pb2.ProductionPlansServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/SendForVerification", implementation.send_for_verification, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ProductionPlansService/Verify", implementation.verify, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ProductionPlansService/Approve", implementation.approve, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ProductionPlansService/SendForRevision", implementation.send_for_revision, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ProductionPlansService/RevisionUpdate", implementation.revision_update, production_plans.scailo_pb2.ProductionPlansServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/Halt", implementation.halt, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ProductionPlansService/Discard", implementation.discard, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ProductionPlansService/Restore", implementation.restore, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ProductionPlansService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ProductionPlansService/Repeat", implementation.repeat, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ProductionPlansService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ProductionPlansService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ProductionPlansService/SendEmail", implementation.send_email, base.scailo_pb2.IdentifierWithEmailAttributes)
    app.register_unary_rpc("/Scailo.ProductionPlansService/CreateMagicLink", implementation.create_magic_link, magic_links.scailo_pb2.MagicLinksServiceCreateRequestForSpecificResource)
    app.register_unary_rpc("/Scailo.ProductionPlansService/Autofill", implementation.autofill, production_plans.scailo_pb2.ProductionPlansServiceAutofillRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/IsCompletable", implementation.is_completable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ProductionPlansService/AddProductionPlanItem", implementation.add_production_plan_item, production_plans.scailo_pb2.ProductionPlansServiceItemCreateRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ModifyProductionPlanItem", implementation.modify_production_plan_item, production_plans.scailo_pb2.ProductionPlansServiceItemUpdateRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ApproveProductionPlanItem", implementation.approve_production_plan_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.ProductionPlansService/DeleteProductionPlanItem", implementation.delete_production_plan_item, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ReorderProductionPlanItems", implementation.reorder_production_plan_items, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewProductionPlanItemByID", implementation.view_production_plan_item_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewApprovedProductionPlanItems", implementation.view_approved_production_plan_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewUnapprovedProductionPlanItems", implementation.view_unapproved_production_plan_items, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewProductionPlanItemHistory", implementation.view_production_plan_item_history, production_plans.scailo_pb2.ProductionPlanItemHistoryRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewPaginatedApprovedProductionPlanItems", implementation.view_paginated_approved_production_plan_items, production_plans.scailo_pb2.ProductionPlanItemsSearchRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewPaginatedUnapprovedProductionPlanItems", implementation.view_paginated_unapproved_production_plan_items, production_plans.scailo_pb2.ProductionPlanItemsSearchRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/SearchItemsWithPagination", implementation.search_items_with_pagination, production_plans.scailo_pb2.ProductionPlanItemsSearchRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/DownloadItemsAsCSV", implementation.download_items_as_csv, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ProductionPlansService/DownloadItemsTemplateAsCSV", implementation.download_items_template_as_csv, base.scailo_pb2.Empty)
    app.register_unary_rpc("/Scailo.ProductionPlansService/UploadProductionPlanItems", implementation.upload_production_plan_items, base.scailo_pb2.IdentifierUUIDWithFile)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewByReferenceID", implementation.view_by_reference_id, base.scailo_pb2.SimpleSearchReq)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewAncillaryParametersByUUID", implementation.view_ancillary_parameters_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewWithPagination", implementation.view_with_pagination, production_plans.scailo_pb2.ProductionPlansServicePaginationReq)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewProspectiveFamilies", implementation.view_prospective_families, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.ProductionPlansService/FilterProspectiveFamilies", implementation.filter_prospective_families, families.scailo_pb2.FilterFamiliesReqForIdentifier)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewProspectiveProductionPlanItem", implementation.view_prospective_production_plan_item, production_plans.scailo_pb2.ProductionPlanItemProspectiveInfoRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewRemainingProductionQuantity", implementation.view_remaining_production_quantity, production_plans.scailo_pb2.ProductionPlanItemProspectiveInfoRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewProductionStatistics", implementation.view_production_statistics, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewFamiliesInProductionPlan", implementation.view_families_in_production_plan, base.scailo_pb2.IdentifierWithSearchKey)
    app.register_unary_rpc("/Scailo.ProductionPlansService/FilterFamiliesInProductionPlan", implementation.filter_families_in_production_plan, families.scailo_pb2.FilterFamiliesReqForIdentifier)
    app.register_unary_rpc("/Scailo.ProductionPlansService/ViewAddedFamilyQuantityForSource", implementation.view_added_family_quantity_for_source, production_plans.scailo_pb2.ProductionPlansServiceAlreadyAddedQuantityForSourceRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/IsDownloadable", implementation.is_downloadable, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ProductionPlansService/DownloadByUUID", implementation.download_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ProductionPlansService/SearchAll", implementation.search_all, production_plans.scailo_pb2.ProductionPlansServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.ProductionPlansService/Filter", implementation.filter, production_plans.scailo_pb2.ProductionPlansServiceFilterReq)
    app.register_unary_rpc("/Scailo.ProductionPlansService/CountInStatus", implementation.count_in_status, base.scailo_pb2.CountInSLCStatusRequest)
    app.register_unary_rpc("/Scailo.ProductionPlansService/Count", implementation.count, production_plans.scailo_pb2.ProductionPlansServiceCountReq)
    app.register_unary_rpc("/Scailo.ProductionPlansService/DownloadAsCSV", implementation.download_as_csv, production_plans.scailo_pb2.ProductionPlansServiceFilterReq)
    return app
