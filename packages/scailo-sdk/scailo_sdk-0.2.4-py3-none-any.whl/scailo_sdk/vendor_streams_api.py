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

from scailo_sdk import base, vendor_streams

class VendorStreamsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def create(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_create(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_update(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Update, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Update"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def update(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_update(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_cancel(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Cancel, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Cancel"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def cancel(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_cancel(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_complete(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Complete, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Complete"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def complete(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_complete(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reopen(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Reopen, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Reopen"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def reopen(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_reopen(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_repeat(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Repeat, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Repeat"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def repeat(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_repeat(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_comment_add(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call CommentAdd, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/CommentAdd"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def comment_add(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_comment_add(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_message(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceMessageCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddMessage, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/AddMessage"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def add_message(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceMessageCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_add_message(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_save_message_for_later(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call SaveMessageForLater, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/SaveMessageForLater"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def save_message_for_later(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_save_message_for_later(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_message(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call DeleteMessage, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/DeleteMessage"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def delete_message(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_delete_message(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_message_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamMessage]:
        """Low-level method to call ViewMessageByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewMessageByUUID"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamMessage,extra_headers, timeout_seconds)


    def view_message_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamMessage:
        response = self.call_view_message_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_messages(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamMessagesList]:
        """Low-level method to call ViewMessages, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewMessages"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamMessagesList,extra_headers, timeout_seconds)


    def view_messages(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamMessagesList:
        response = self.call_view_messages(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_messages(
        self, req: vendor_streams.scailo_pb2.VendorStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse]:
        """Low-level method to call ViewPaginatedMessages, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewPaginatedMessages"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse,extra_headers, timeout_seconds)


    def view_paginated_messages(
        self, req: vendor_streams.scailo_pb2.VendorStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse:
        response = self.call_view_paginated_messages(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_messages_with_pagination(
        self, req: vendor_streams.scailo_pb2.VendorStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse]:
        """Low-level method to call SearchMessagesWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/SearchMessagesWithPagination"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse,extra_headers, timeout_seconds)


    def search_messages_with_pagination(
        self, req: vendor_streams.scailo_pb2.VendorStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse:
        response = self.call_search_messages_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_message_receipts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamMessageReceiptsList]:
        """Low-level method to call ViewMessageReceipts, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewMessageReceipts"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamMessageReceiptsList,extra_headers, timeout_seconds)


    def view_message_receipts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamMessageReceiptsList:
        response = self.call_view_message_receipts(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_internal_subscriber(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceInternalSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInternalSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/AddInternalSubscriber"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_internal_subscriber(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceInternalSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_internal_subscriber(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_internal_subscriber(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteInternalSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/DeleteInternalSubscriber"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_internal_subscriber(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_internal_subscriber(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_internal_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamInternalSubscriber]:
        """Low-level method to call ViewInternalSubscriberByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewInternalSubscriberByID"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamInternalSubscriber,extra_headers, timeout_seconds)


    def view_internal_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamInternalSubscriber:
        response = self.call_view_internal_subscriber_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_internal_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamInternalSubscribersList]:
        """Low-level method to call ViewInternalSubscribers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewInternalSubscribers"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamInternalSubscribersList,extra_headers, timeout_seconds)


    def view_internal_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamInternalSubscribersList:
        response = self.call_view_internal_subscribers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_import_internal_subscribers_from_team(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportInternalSubscribersFromTeam, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ImportInternalSubscribersFromTeam"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def import_internal_subscribers_from_team(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_import_internal_subscribers_from_team(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_import_internal_subscribers_from_department(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportInternalSubscribersFromDepartment, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ImportInternalSubscribersFromDepartment"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def import_internal_subscribers_from_department(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_import_internal_subscribers_from_department(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_vendor_subscriber(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceVendorSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddVendorSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/AddVendorSubscriber"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_vendor_subscriber(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceVendorSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_vendor_subscriber(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_vendor_subscriber(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteVendorSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/DeleteVendorSubscriber"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_vendor_subscriber(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_vendor_subscriber(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_vendor_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamVendorSubscriber]:
        """Low-level method to call ViewVendorSubscriberByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewVendorSubscriberByID"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamVendorSubscriber,extra_headers, timeout_seconds)


    def view_vendor_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamVendorSubscriber:
        response = self.call_view_vendor_subscriber_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_vendor_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamVendorSubscribersList]:
        """Low-level method to call ViewVendorSubscribers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewVendorSubscribers"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamVendorSubscribersList,extra_headers, timeout_seconds)


    def view_vendor_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamVendorSubscribersList:
        response = self.call_view_vendor_subscribers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStream]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewByID"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStream,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStream:
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
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStream]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewByUUID"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStream,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStream:
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
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStream]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStream,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStream:
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
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStream]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStream,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStream:
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
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsList:
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
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewAll"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsList:
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
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsServicePaginationResponse:
        response = self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_all(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/SearchAll"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsList,extra_headers, timeout_seconds)


    def search_all(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Filter"
        return self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsList,extra_headers, timeout_seconds)


    def filter(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsList:
        response = self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_count(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncVendorStreamsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def create(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_create(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_update(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Update, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Update"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def update(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_update(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_cancel(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Cancel, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Cancel"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def cancel(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_cancel(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_complete(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Complete, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Complete"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def complete(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_complete(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reopen(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Reopen, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Reopen"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def reopen(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_reopen(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_repeat(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Repeat, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Repeat"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def repeat(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_repeat(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_comment_add(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call CommentAdd, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/CommentAdd"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def comment_add(
        self, req: base.scailo_pb2.IdentifierUUIDWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_comment_add(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_message(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceMessageCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddMessage, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/AddMessage"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def add_message(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceMessageCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_add_message(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_save_message_for_later(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call SaveMessageForLater, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/SaveMessageForLater"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def save_message_for_later(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_save_message_for_later(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_message(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call DeleteMessage, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/DeleteMessage"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def delete_message(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_delete_message(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_message_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamMessage]:
        """Low-level method to call ViewMessageByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewMessageByUUID"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamMessage,extra_headers, timeout_seconds)

    async def view_message_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamMessage:
        response = await self.call_view_message_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_messages(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamMessagesList]:
        """Low-level method to call ViewMessages, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewMessages"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamMessagesList,extra_headers, timeout_seconds)

    async def view_messages(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamMessagesList:
        response = await self.call_view_messages(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_messages(
        self, req: vendor_streams.scailo_pb2.VendorStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse]:
        """Low-level method to call ViewPaginatedMessages, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewPaginatedMessages"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse,extra_headers, timeout_seconds)

    async def view_paginated_messages(
        self, req: vendor_streams.scailo_pb2.VendorStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse:
        response = await self.call_view_paginated_messages(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_messages_with_pagination(
        self, req: vendor_streams.scailo_pb2.VendorStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse]:
        """Low-level method to call SearchMessagesWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/SearchMessagesWithPagination"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse,extra_headers, timeout_seconds)

    async def search_messages_with_pagination(
        self, req: vendor_streams.scailo_pb2.VendorStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse:
        response = await self.call_search_messages_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_message_receipts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamMessageReceiptsList]:
        """Low-level method to call ViewMessageReceipts, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewMessageReceipts"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamMessageReceiptsList,extra_headers, timeout_seconds)

    async def view_message_receipts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamMessageReceiptsList:
        response = await self.call_view_message_receipts(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_internal_subscriber(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceInternalSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInternalSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/AddInternalSubscriber"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_internal_subscriber(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceInternalSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_internal_subscriber(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_internal_subscriber(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteInternalSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/DeleteInternalSubscriber"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_internal_subscriber(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_internal_subscriber(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_internal_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamInternalSubscriber]:
        """Low-level method to call ViewInternalSubscriberByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewInternalSubscriberByID"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamInternalSubscriber,extra_headers, timeout_seconds)

    async def view_internal_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamInternalSubscriber:
        response = await self.call_view_internal_subscriber_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_internal_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamInternalSubscribersList]:
        """Low-level method to call ViewInternalSubscribers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewInternalSubscribers"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamInternalSubscribersList,extra_headers, timeout_seconds)

    async def view_internal_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamInternalSubscribersList:
        response = await self.call_view_internal_subscribers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_import_internal_subscribers_from_team(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportInternalSubscribersFromTeam, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ImportInternalSubscribersFromTeam"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def import_internal_subscribers_from_team(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_import_internal_subscribers_from_team(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_import_internal_subscribers_from_department(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportInternalSubscribersFromDepartment, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ImportInternalSubscribersFromDepartment"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def import_internal_subscribers_from_department(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_import_internal_subscribers_from_department(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_vendor_subscriber(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceVendorSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddVendorSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/AddVendorSubscriber"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_vendor_subscriber(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceVendorSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_vendor_subscriber(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_vendor_subscriber(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteVendorSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/DeleteVendorSubscriber"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_vendor_subscriber(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_vendor_subscriber(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_vendor_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamVendorSubscriber]:
        """Low-level method to call ViewVendorSubscriberByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewVendorSubscriberByID"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamVendorSubscriber,extra_headers, timeout_seconds)

    async def view_vendor_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamVendorSubscriber:
        response = await self.call_view_vendor_subscriber_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_vendor_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamVendorSubscribersList]:
        """Low-level method to call ViewVendorSubscribers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewVendorSubscribers"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamVendorSubscribersList,extra_headers, timeout_seconds)

    async def view_vendor_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamVendorSubscribersList:
        response = await self.call_view_vendor_subscribers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStream]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewByID"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStream,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStream:
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
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStream]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStream,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStream:
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
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStream]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStream,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStream:
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
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStream]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStream,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStream:
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
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsList:
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
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewAll"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsList:
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
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsServicePaginationResponse:
        response = await self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_all(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/SearchAll"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vendor_streams.scailo_pb2.VendorStreamsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Filter"
        return await self._connect_client.call_unary(url, req, vendor_streams.scailo_pb2.VendorStreamsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vendor_streams.scailo_pb2.VendorStreamsList:
        response = await self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_count(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VendorStreamsService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: vendor_streams.scailo_pb2.VendorStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
class VendorStreamsServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def update(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def cancel(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def complete(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def reopen(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def repeat(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def comment_add(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def add_message(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamsServiceMessageCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def save_message_for_later(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def delete_message(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def view_message_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamMessage]:
        ...
    def view_messages(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamMessagesList]:
        ...
    def view_paginated_messages(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamMessagesSearchRequest]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse]:
        ...
    def search_messages_with_pagination(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamMessagesSearchRequest]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamsServicePaginatedMessagesResponse]:
        ...
    def view_message_receipts(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamMessageReceiptsList]:
        ...
    def add_internal_subscriber(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamsServiceInternalSubscriberCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_internal_subscriber(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_internal_subscriber_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamInternalSubscriber]:
        ...
    def view_internal_subscribers(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamInternalSubscribersList]:
        ...
    def import_internal_subscribers_from_team(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamsServiceImportInternalSubscribersRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def import_internal_subscribers_from_department(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamsServiceImportInternalSubscribersRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_vendor_subscriber(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamsServiceVendorSubscriberCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_vendor_subscriber(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_vendor_subscriber_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamVendorSubscriber]:
        ...
    def view_vendor_subscribers(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamVendorSubscribersList]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStream]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStream]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStream]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStream]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamsList]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamsList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamsList]:
        ...
    def view_with_pagination(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamsServicePaginationReq]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamsServicePaginationResponse]:
        ...
    def search_all(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamsServiceSearchAllReq]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamsList]:
        ...
    def filter(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamsServiceFilterReq]) -> ServerResponse[vendor_streams.scailo_pb2.VendorStreamsList]:
        ...
    def count(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[vendor_streams.scailo_pb2.VendorStreamsServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

VENDOR_STREAMS_SERVICE_PATH_PREFIX = "/Scailo.VendorStreamsService"

def wsgi_vendor_streams_service(implementation: VendorStreamsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.VendorStreamsService/Create", implementation.create, vendor_streams.scailo_pb2.VendorStreamsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.VendorStreamsService/Update", implementation.update, vendor_streams.scailo_pb2.VendorStreamsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.VendorStreamsService/Cancel", implementation.cancel, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.VendorStreamsService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.VendorStreamsService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.VendorStreamsService/Repeat", implementation.repeat, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.VendorStreamsService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.VendorStreamsService/AddMessage", implementation.add_message, vendor_streams.scailo_pb2.VendorStreamsServiceMessageCreateRequest)
    app.register_unary_rpc("/Scailo.VendorStreamsService/SaveMessageForLater", implementation.save_message_for_later, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VendorStreamsService/DeleteMessage", implementation.delete_message, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewMessageByUUID", implementation.view_message_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewMessages", implementation.view_messages, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewPaginatedMessages", implementation.view_paginated_messages, vendor_streams.scailo_pb2.VendorStreamMessagesSearchRequest)
    app.register_unary_rpc("/Scailo.VendorStreamsService/SearchMessagesWithPagination", implementation.search_messages_with_pagination, vendor_streams.scailo_pb2.VendorStreamMessagesSearchRequest)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewMessageReceipts", implementation.view_message_receipts, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VendorStreamsService/AddInternalSubscriber", implementation.add_internal_subscriber, vendor_streams.scailo_pb2.VendorStreamsServiceInternalSubscriberCreateRequest)
    app.register_unary_rpc("/Scailo.VendorStreamsService/DeleteInternalSubscriber", implementation.delete_internal_subscriber, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewInternalSubscriberByID", implementation.view_internal_subscriber_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewInternalSubscribers", implementation.view_internal_subscribers, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ImportInternalSubscribersFromTeam", implementation.import_internal_subscribers_from_team, vendor_streams.scailo_pb2.VendorStreamsServiceImportInternalSubscribersRequest)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ImportInternalSubscribersFromDepartment", implementation.import_internal_subscribers_from_department, vendor_streams.scailo_pb2.VendorStreamsServiceImportInternalSubscribersRequest)
    app.register_unary_rpc("/Scailo.VendorStreamsService/AddVendorSubscriber", implementation.add_vendor_subscriber, vendor_streams.scailo_pb2.VendorStreamsServiceVendorSubscriberCreateRequest)
    app.register_unary_rpc("/Scailo.VendorStreamsService/DeleteVendorSubscriber", implementation.delete_vendor_subscriber, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewVendorSubscriberByID", implementation.view_vendor_subscriber_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewVendorSubscribers", implementation.view_vendor_subscribers, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VendorStreamsService/ViewWithPagination", implementation.view_with_pagination, vendor_streams.scailo_pb2.VendorStreamsServicePaginationReq)
    app.register_unary_rpc("/Scailo.VendorStreamsService/SearchAll", implementation.search_all, vendor_streams.scailo_pb2.VendorStreamsServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.VendorStreamsService/Filter", implementation.filter, vendor_streams.scailo_pb2.VendorStreamsServiceFilterReq)
    app.register_unary_rpc("/Scailo.VendorStreamsService/Count", implementation.count, vendor_streams.scailo_pb2.VendorStreamsServiceCountReq)
    app.register_unary_rpc("/Scailo.VendorStreamsService/DownloadAsCSV", implementation.download_as_csv, vendor_streams.scailo_pb2.VendorStreamsServiceFilterReq)
    return app
