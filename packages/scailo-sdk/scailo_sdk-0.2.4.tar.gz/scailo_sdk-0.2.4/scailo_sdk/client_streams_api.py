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

from scailo_sdk import base, client_streams

class ClientStreamsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def create(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: client_streams.scailo_pb2.ClientStreamsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Update, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/Update"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def update(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ClientStreamsService/Cancel"
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
        url = self.base_url + "/Scailo.ClientStreamsService/Complete"
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
        url = self.base_url + "/Scailo.ClientStreamsService/Reopen"
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
        url = self.base_url + "/Scailo.ClientStreamsService/Repeat"
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
        url = self.base_url + "/Scailo.ClientStreamsService/CommentAdd"
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
        self, req: client_streams.scailo_pb2.ClientStreamsServiceMessageCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddMessage, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/AddMessage"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def add_message(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceMessageCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ClientStreamsService/SaveMessageForLater"
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
        url = self.base_url + "/Scailo.ClientStreamsService/DeleteMessage"
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamMessage]:
        """Low-level method to call ViewMessageByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewMessageByUUID"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamMessage,extra_headers, timeout_seconds)


    def view_message_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamMessage:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamMessagesList]:
        """Low-level method to call ViewMessages, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewMessages"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamMessagesList,extra_headers, timeout_seconds)


    def view_messages(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamMessagesList:
        response = self.call_view_messages(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_messages(
        self, req: client_streams.scailo_pb2.ClientStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse]:
        """Low-level method to call ViewPaginatedMessages, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewPaginatedMessages"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse,extra_headers, timeout_seconds)


    def view_paginated_messages(
        self, req: client_streams.scailo_pb2.ClientStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse:
        response = self.call_view_paginated_messages(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_messages_with_pagination(
        self, req: client_streams.scailo_pb2.ClientStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse]:
        """Low-level method to call SearchMessagesWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/SearchMessagesWithPagination"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse,extra_headers, timeout_seconds)


    def search_messages_with_pagination(
        self, req: client_streams.scailo_pb2.ClientStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamMessageReceiptsList]:
        """Low-level method to call ViewMessageReceipts, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewMessageReceipts"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamMessageReceiptsList,extra_headers, timeout_seconds)


    def view_message_receipts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamMessageReceiptsList:
        response = self.call_view_message_receipts(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_internal_subscriber(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceInternalSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInternalSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/AddInternalSubscriber"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_internal_subscriber(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceInternalSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ClientStreamsService/DeleteInternalSubscriber"
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamInternalSubscriber]:
        """Low-level method to call ViewInternalSubscriberByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewInternalSubscriberByID"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamInternalSubscriber,extra_headers, timeout_seconds)


    def view_internal_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamInternalSubscriber:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamInternalSubscribersList]:
        """Low-level method to call ViewInternalSubscribers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewInternalSubscribers"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamInternalSubscribersList,extra_headers, timeout_seconds)


    def view_internal_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamInternalSubscribersList:
        response = self.call_view_internal_subscribers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_import_internal_subscribers_from_team(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportInternalSubscribersFromTeam, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ImportInternalSubscribersFromTeam"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def import_internal_subscribers_from_team(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: client_streams.scailo_pb2.ClientStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportInternalSubscribersFromDepartment, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ImportInternalSubscribersFromDepartment"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def import_internal_subscribers_from_department(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_import_internal_subscribers_from_department(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_client_subscriber(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceClientSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddClientSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/AddClientSubscriber"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_client_subscriber(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceClientSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_client_subscriber(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_client_subscriber(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteClientSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/DeleteClientSubscriber"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_client_subscriber(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_client_subscriber(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_client_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamClientSubscriber]:
        """Low-level method to call ViewClientSubscriberByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewClientSubscriberByID"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamClientSubscriber,extra_headers, timeout_seconds)


    def view_client_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamClientSubscriber:
        response = self.call_view_client_subscriber_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_client_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamClientSubscribersList]:
        """Low-level method to call ViewClientSubscribers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewClientSubscribers"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamClientSubscribersList,extra_headers, timeout_seconds)


    def view_client_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamClientSubscribersList:
        response = self.call_view_client_subscribers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStream]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewByID"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStream,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStream:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStream]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewByUUID"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStream,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStream:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStream]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStream,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStream:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStream]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStream,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStream:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsList:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewAll"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsList:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: client_streams.scailo_pb2.ClientStreamsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: client_streams.scailo_pb2.ClientStreamsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsServicePaginationResponse:
        response = self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_all(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/SearchAll"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsList,extra_headers, timeout_seconds)


    def search_all(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/Filter"
        return self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsList,extra_headers, timeout_seconds)


    def filter(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsList:
        response = self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_count(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: client_streams.scailo_pb2.ClientStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncClientStreamsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def create(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: client_streams.scailo_pb2.ClientStreamsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Update, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/Update"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def update(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ClientStreamsService/Cancel"
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
        url = self.base_url + "/Scailo.ClientStreamsService/Complete"
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
        url = self.base_url + "/Scailo.ClientStreamsService/Reopen"
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
        url = self.base_url + "/Scailo.ClientStreamsService/Repeat"
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
        url = self.base_url + "/Scailo.ClientStreamsService/CommentAdd"
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
        self, req: client_streams.scailo_pb2.ClientStreamsServiceMessageCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddMessage, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/AddMessage"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def add_message(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceMessageCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ClientStreamsService/SaveMessageForLater"
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
        url = self.base_url + "/Scailo.ClientStreamsService/DeleteMessage"
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamMessage]:
        """Low-level method to call ViewMessageByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewMessageByUUID"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamMessage,extra_headers, timeout_seconds)

    async def view_message_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamMessage:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamMessagesList]:
        """Low-level method to call ViewMessages, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewMessages"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamMessagesList,extra_headers, timeout_seconds)

    async def view_messages(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamMessagesList:
        response = await self.call_view_messages(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_messages(
        self, req: client_streams.scailo_pb2.ClientStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse]:
        """Low-level method to call ViewPaginatedMessages, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewPaginatedMessages"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse,extra_headers, timeout_seconds)

    async def view_paginated_messages(
        self, req: client_streams.scailo_pb2.ClientStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse:
        response = await self.call_view_paginated_messages(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_messages_with_pagination(
        self, req: client_streams.scailo_pb2.ClientStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse]:
        """Low-level method to call SearchMessagesWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/SearchMessagesWithPagination"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse,extra_headers, timeout_seconds)

    async def search_messages_with_pagination(
        self, req: client_streams.scailo_pb2.ClientStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamMessageReceiptsList]:
        """Low-level method to call ViewMessageReceipts, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewMessageReceipts"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamMessageReceiptsList,extra_headers, timeout_seconds)

    async def view_message_receipts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamMessageReceiptsList:
        response = await self.call_view_message_receipts(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_internal_subscriber(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceInternalSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInternalSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/AddInternalSubscriber"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_internal_subscriber(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceInternalSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ClientStreamsService/DeleteInternalSubscriber"
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamInternalSubscriber]:
        """Low-level method to call ViewInternalSubscriberByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewInternalSubscriberByID"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamInternalSubscriber,extra_headers, timeout_seconds)

    async def view_internal_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamInternalSubscriber:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamInternalSubscribersList]:
        """Low-level method to call ViewInternalSubscribers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewInternalSubscribers"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamInternalSubscribersList,extra_headers, timeout_seconds)

    async def view_internal_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamInternalSubscribersList:
        response = await self.call_view_internal_subscribers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_import_internal_subscribers_from_team(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportInternalSubscribersFromTeam, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ImportInternalSubscribersFromTeam"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def import_internal_subscribers_from_team(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: client_streams.scailo_pb2.ClientStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportInternalSubscribersFromDepartment, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ImportInternalSubscribersFromDepartment"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def import_internal_subscribers_from_department(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_import_internal_subscribers_from_department(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_client_subscriber(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceClientSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddClientSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/AddClientSubscriber"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_client_subscriber(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceClientSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_client_subscriber(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_client_subscriber(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteClientSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/DeleteClientSubscriber"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_client_subscriber(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_client_subscriber(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_client_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamClientSubscriber]:
        """Low-level method to call ViewClientSubscriberByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewClientSubscriberByID"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamClientSubscriber,extra_headers, timeout_seconds)

    async def view_client_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamClientSubscriber:
        response = await self.call_view_client_subscriber_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_client_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamClientSubscribersList]:
        """Low-level method to call ViewClientSubscribers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewClientSubscribers"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamClientSubscribersList,extra_headers, timeout_seconds)

    async def view_client_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamClientSubscribersList:
        response = await self.call_view_client_subscribers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStream]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewByID"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStream,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStream:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStream]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStream,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStream:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStream]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStream,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStream:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStream]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStream,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStream:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsList:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewAll"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsList:
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
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: client_streams.scailo_pb2.ClientStreamsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: client_streams.scailo_pb2.ClientStreamsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsServicePaginationResponse:
        response = await self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_all(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/SearchAll"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[client_streams.scailo_pb2.ClientStreamsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/Filter"
        return await self._connect_client.call_unary(url, req, client_streams.scailo_pb2.ClientStreamsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> client_streams.scailo_pb2.ClientStreamsList:
        response = await self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_count(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: client_streams.scailo_pb2.ClientStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ClientStreamsService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: client_streams.scailo_pb2.ClientStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
class ClientStreamsServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def update(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
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
    def add_message(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamsServiceMessageCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def save_message_for_later(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def delete_message(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def view_message_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamMessage]:
        ...
    def view_messages(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamMessagesList]:
        ...
    def view_paginated_messages(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamMessagesSearchRequest]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse]:
        ...
    def search_messages_with_pagination(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamMessagesSearchRequest]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamsServicePaginatedMessagesResponse]:
        ...
    def view_message_receipts(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamMessageReceiptsList]:
        ...
    def add_internal_subscriber(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamsServiceInternalSubscriberCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_internal_subscriber(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_internal_subscriber_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamInternalSubscriber]:
        ...
    def view_internal_subscribers(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamInternalSubscribersList]:
        ...
    def import_internal_subscribers_from_team(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamsServiceImportInternalSubscribersRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def import_internal_subscribers_from_department(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamsServiceImportInternalSubscribersRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_client_subscriber(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamsServiceClientSubscriberCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_client_subscriber(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_client_subscriber_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamClientSubscriber]:
        ...
    def view_client_subscribers(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamClientSubscribersList]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[client_streams.scailo_pb2.ClientStream]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[client_streams.scailo_pb2.ClientStream]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[client_streams.scailo_pb2.ClientStream]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[client_streams.scailo_pb2.ClientStream]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamsList]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamsList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamsList]:
        ...
    def view_with_pagination(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamsServicePaginationReq]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamsServicePaginationResponse]:
        ...
    def search_all(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamsServiceSearchAllReq]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamsList]:
        ...
    def filter(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamsServiceFilterReq]) -> ServerResponse[client_streams.scailo_pb2.ClientStreamsList]:
        ...
    def count(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[client_streams.scailo_pb2.ClientStreamsServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

CLIENT_STREAMS_SERVICE_PATH_PREFIX = "/Scailo.ClientStreamsService"

def wsgi_client_streams_service(implementation: ClientStreamsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.ClientStreamsService/Create", implementation.create, client_streams.scailo_pb2.ClientStreamsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.ClientStreamsService/Update", implementation.update, client_streams.scailo_pb2.ClientStreamsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.ClientStreamsService/Cancel", implementation.cancel, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ClientStreamsService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ClientStreamsService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ClientStreamsService/Repeat", implementation.repeat, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ClientStreamsService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ClientStreamsService/AddMessage", implementation.add_message, client_streams.scailo_pb2.ClientStreamsServiceMessageCreateRequest)
    app.register_unary_rpc("/Scailo.ClientStreamsService/SaveMessageForLater", implementation.save_message_for_later, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ClientStreamsService/DeleteMessage", implementation.delete_message, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewMessageByUUID", implementation.view_message_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewMessages", implementation.view_messages, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewPaginatedMessages", implementation.view_paginated_messages, client_streams.scailo_pb2.ClientStreamMessagesSearchRequest)
    app.register_unary_rpc("/Scailo.ClientStreamsService/SearchMessagesWithPagination", implementation.search_messages_with_pagination, client_streams.scailo_pb2.ClientStreamMessagesSearchRequest)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewMessageReceipts", implementation.view_message_receipts, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ClientStreamsService/AddInternalSubscriber", implementation.add_internal_subscriber, client_streams.scailo_pb2.ClientStreamsServiceInternalSubscriberCreateRequest)
    app.register_unary_rpc("/Scailo.ClientStreamsService/DeleteInternalSubscriber", implementation.delete_internal_subscriber, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewInternalSubscriberByID", implementation.view_internal_subscriber_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewInternalSubscribers", implementation.view_internal_subscribers, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ImportInternalSubscribersFromTeam", implementation.import_internal_subscribers_from_team, client_streams.scailo_pb2.ClientStreamsServiceImportInternalSubscribersRequest)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ImportInternalSubscribersFromDepartment", implementation.import_internal_subscribers_from_department, client_streams.scailo_pb2.ClientStreamsServiceImportInternalSubscribersRequest)
    app.register_unary_rpc("/Scailo.ClientStreamsService/AddClientSubscriber", implementation.add_client_subscriber, client_streams.scailo_pb2.ClientStreamsServiceClientSubscriberCreateRequest)
    app.register_unary_rpc("/Scailo.ClientStreamsService/DeleteClientSubscriber", implementation.delete_client_subscriber, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewClientSubscriberByID", implementation.view_client_subscriber_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewClientSubscribers", implementation.view_client_subscribers, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ClientStreamsService/ViewWithPagination", implementation.view_with_pagination, client_streams.scailo_pb2.ClientStreamsServicePaginationReq)
    app.register_unary_rpc("/Scailo.ClientStreamsService/SearchAll", implementation.search_all, client_streams.scailo_pb2.ClientStreamsServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.ClientStreamsService/Filter", implementation.filter, client_streams.scailo_pb2.ClientStreamsServiceFilterReq)
    app.register_unary_rpc("/Scailo.ClientStreamsService/Count", implementation.count, client_streams.scailo_pb2.ClientStreamsServiceCountReq)
    app.register_unary_rpc("/Scailo.ClientStreamsService/DownloadAsCSV", implementation.download_as_csv, client_streams.scailo_pb2.ClientStreamsServiceFilterReq)
    return app
