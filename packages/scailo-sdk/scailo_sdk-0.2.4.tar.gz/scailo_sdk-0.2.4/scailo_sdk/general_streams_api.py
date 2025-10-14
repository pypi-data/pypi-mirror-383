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

from scailo_sdk import base, general_streams

class GeneralStreamsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def create(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Update, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/Update"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def update(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.GeneralStreamsService/Cancel"
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
        url = self.base_url + "/Scailo.GeneralStreamsService/Complete"
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
        url = self.base_url + "/Scailo.GeneralStreamsService/Reopen"
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
        url = self.base_url + "/Scailo.GeneralStreamsService/Repeat"
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
        url = self.base_url + "/Scailo.GeneralStreamsService/CommentAdd"
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
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceMessageCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddMessage, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/AddMessage"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def add_message(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceMessageCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.GeneralStreamsService/SaveMessageForLater"
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
        url = self.base_url + "/Scailo.GeneralStreamsService/DeleteMessage"
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamMessage]:
        """Low-level method to call ViewMessageByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewMessageByUUID"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamMessage,extra_headers, timeout_seconds)


    def view_message_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamMessage:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamMessagesList]:
        """Low-level method to call ViewMessages, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewMessages"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamMessagesList,extra_headers, timeout_seconds)


    def view_messages(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamMessagesList:
        response = self.call_view_messages(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_messages(
        self, req: general_streams.scailo_pb2.GeneralStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse]:
        """Low-level method to call ViewPaginatedMessages, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewPaginatedMessages"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse,extra_headers, timeout_seconds)


    def view_paginated_messages(
        self, req: general_streams.scailo_pb2.GeneralStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse:
        response = self.call_view_paginated_messages(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_messages_with_pagination(
        self, req: general_streams.scailo_pb2.GeneralStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse]:
        """Low-level method to call SearchMessagesWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/SearchMessagesWithPagination"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse,extra_headers, timeout_seconds)


    def search_messages_with_pagination(
        self, req: general_streams.scailo_pb2.GeneralStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamMessageReceiptsList]:
        """Low-level method to call ViewMessageReceipts, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewMessageReceipts"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamMessageReceiptsList,extra_headers, timeout_seconds)


    def view_message_receipts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamMessageReceiptsList:
        response = self.call_view_message_receipts(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_internal_subscriber(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceInternalSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInternalSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/AddInternalSubscriber"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_internal_subscriber(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceInternalSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.GeneralStreamsService/DeleteInternalSubscriber"
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamInternalSubscriber]:
        """Low-level method to call ViewInternalSubscriberByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewInternalSubscriberByID"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamInternalSubscriber,extra_headers, timeout_seconds)


    def view_internal_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamInternalSubscriber:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamInternalSubscribersList]:
        """Low-level method to call ViewInternalSubscribers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewInternalSubscribers"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamInternalSubscribersList,extra_headers, timeout_seconds)


    def view_internal_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamInternalSubscribersList:
        response = self.call_view_internal_subscribers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_import_internal_subscribers_from_team(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportInternalSubscribersFromTeam, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ImportInternalSubscribersFromTeam"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def import_internal_subscribers_from_team(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportInternalSubscribersFromDepartment, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ImportInternalSubscribersFromDepartment"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def import_internal_subscribers_from_department(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_import_internal_subscribers_from_department(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStream]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewByID"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStream,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStream:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStream]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewByUUID"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStream,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStream:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStream]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStream,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStream:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStream]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStream,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStream:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsList:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewAll"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsList:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: general_streams.scailo_pb2.GeneralStreamsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: general_streams.scailo_pb2.GeneralStreamsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsServicePaginationResponse:
        response = self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_all(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/SearchAll"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsList,extra_headers, timeout_seconds)


    def search_all(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/Filter"
        return self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsList,extra_headers, timeout_seconds)


    def filter(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsList:
        response = self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_count(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncGeneralStreamsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def create(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Update, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/Update"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def update(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.GeneralStreamsService/Cancel"
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
        url = self.base_url + "/Scailo.GeneralStreamsService/Complete"
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
        url = self.base_url + "/Scailo.GeneralStreamsService/Reopen"
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
        url = self.base_url + "/Scailo.GeneralStreamsService/Repeat"
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
        url = self.base_url + "/Scailo.GeneralStreamsService/CommentAdd"
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
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceMessageCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddMessage, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/AddMessage"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def add_message(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceMessageCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.GeneralStreamsService/SaveMessageForLater"
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
        url = self.base_url + "/Scailo.GeneralStreamsService/DeleteMessage"
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamMessage]:
        """Low-level method to call ViewMessageByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewMessageByUUID"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamMessage,extra_headers, timeout_seconds)

    async def view_message_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamMessage:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamMessagesList]:
        """Low-level method to call ViewMessages, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewMessages"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamMessagesList,extra_headers, timeout_seconds)

    async def view_messages(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamMessagesList:
        response = await self.call_view_messages(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_messages(
        self, req: general_streams.scailo_pb2.GeneralStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse]:
        """Low-level method to call ViewPaginatedMessages, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewPaginatedMessages"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse,extra_headers, timeout_seconds)

    async def view_paginated_messages(
        self, req: general_streams.scailo_pb2.GeneralStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse:
        response = await self.call_view_paginated_messages(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_messages_with_pagination(
        self, req: general_streams.scailo_pb2.GeneralStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse]:
        """Low-level method to call SearchMessagesWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/SearchMessagesWithPagination"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse,extra_headers, timeout_seconds)

    async def search_messages_with_pagination(
        self, req: general_streams.scailo_pb2.GeneralStreamMessagesSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamMessageReceiptsList]:
        """Low-level method to call ViewMessageReceipts, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewMessageReceipts"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamMessageReceiptsList,extra_headers, timeout_seconds)

    async def view_message_receipts(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamMessageReceiptsList:
        response = await self.call_view_message_receipts(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_internal_subscriber(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceInternalSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddInternalSubscriber, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/AddInternalSubscriber"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_internal_subscriber(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceInternalSubscriberCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.GeneralStreamsService/DeleteInternalSubscriber"
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamInternalSubscriber]:
        """Low-level method to call ViewInternalSubscriberByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewInternalSubscriberByID"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamInternalSubscriber,extra_headers, timeout_seconds)

    async def view_internal_subscriber_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamInternalSubscriber:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamInternalSubscribersList]:
        """Low-level method to call ViewInternalSubscribers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewInternalSubscribers"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamInternalSubscribersList,extra_headers, timeout_seconds)

    async def view_internal_subscribers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamInternalSubscribersList:
        response = await self.call_view_internal_subscribers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_import_internal_subscribers_from_team(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportInternalSubscribersFromTeam, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ImportInternalSubscribersFromTeam"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def import_internal_subscribers_from_team(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportInternalSubscribersFromDepartment, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ImportInternalSubscribersFromDepartment"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def import_internal_subscribers_from_department(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceImportInternalSubscribersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_import_internal_subscribers_from_department(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStream]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewByID"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStream,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStream:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStream]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStream,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStream:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStream]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStream,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStream:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStream]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStream,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStream:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsList:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewAll"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsList:
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
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: general_streams.scailo_pb2.GeneralStreamsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: general_streams.scailo_pb2.GeneralStreamsServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsServicePaginationResponse:
        response = await self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_all(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/SearchAll"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_streams.scailo_pb2.GeneralStreamsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/Filter"
        return await self._connect_client.call_unary(url, req, general_streams.scailo_pb2.GeneralStreamsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_streams.scailo_pb2.GeneralStreamsList:
        response = await self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_count(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralStreamsService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: general_streams.scailo_pb2.GeneralStreamsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
class GeneralStreamsServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[general_streams.scailo_pb2.GeneralStreamsServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def update(self, req: ClientRequest[general_streams.scailo_pb2.GeneralStreamsServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
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
    def add_message(self, req: ClientRequest[general_streams.scailo_pb2.GeneralStreamsServiceMessageCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def save_message_for_later(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def delete_message(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def view_message_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[general_streams.scailo_pb2.GeneralStreamMessage]:
        ...
    def view_messages(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[general_streams.scailo_pb2.GeneralStreamMessagesList]:
        ...
    def view_paginated_messages(self, req: ClientRequest[general_streams.scailo_pb2.GeneralStreamMessagesSearchRequest]) -> ServerResponse[general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse]:
        ...
    def search_messages_with_pagination(self, req: ClientRequest[general_streams.scailo_pb2.GeneralStreamMessagesSearchRequest]) -> ServerResponse[general_streams.scailo_pb2.GeneralStreamsServicePaginatedMessagesResponse]:
        ...
    def view_message_receipts(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[general_streams.scailo_pb2.GeneralStreamMessageReceiptsList]:
        ...
    def add_internal_subscriber(self, req: ClientRequest[general_streams.scailo_pb2.GeneralStreamsServiceInternalSubscriberCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_internal_subscriber(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_internal_subscriber_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[general_streams.scailo_pb2.GeneralStreamInternalSubscriber]:
        ...
    def view_internal_subscribers(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[general_streams.scailo_pb2.GeneralStreamInternalSubscribersList]:
        ...
    def import_internal_subscribers_from_team(self, req: ClientRequest[general_streams.scailo_pb2.GeneralStreamsServiceImportInternalSubscribersRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def import_internal_subscribers_from_department(self, req: ClientRequest[general_streams.scailo_pb2.GeneralStreamsServiceImportInternalSubscribersRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[general_streams.scailo_pb2.GeneralStream]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[general_streams.scailo_pb2.GeneralStream]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[general_streams.scailo_pb2.GeneralStream]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[general_streams.scailo_pb2.GeneralStream]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[general_streams.scailo_pb2.GeneralStreamsList]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[general_streams.scailo_pb2.GeneralStreamsList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[general_streams.scailo_pb2.GeneralStreamsList]:
        ...
    def view_with_pagination(self, req: ClientRequest[general_streams.scailo_pb2.GeneralStreamsServicePaginationReq]) -> ServerResponse[general_streams.scailo_pb2.GeneralStreamsServicePaginationResponse]:
        ...
    def search_all(self, req: ClientRequest[general_streams.scailo_pb2.GeneralStreamsServiceSearchAllReq]) -> ServerResponse[general_streams.scailo_pb2.GeneralStreamsList]:
        ...
    def filter(self, req: ClientRequest[general_streams.scailo_pb2.GeneralStreamsServiceFilterReq]) -> ServerResponse[general_streams.scailo_pb2.GeneralStreamsList]:
        ...
    def count(self, req: ClientRequest[general_streams.scailo_pb2.GeneralStreamsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[general_streams.scailo_pb2.GeneralStreamsServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...

GENERAL_STREAMS_SERVICE_PATH_PREFIX = "/Scailo.GeneralStreamsService"

def wsgi_general_streams_service(implementation: GeneralStreamsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.GeneralStreamsService/Create", implementation.create, general_streams.scailo_pb2.GeneralStreamsServiceCreateRequest)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/Update", implementation.update, general_streams.scailo_pb2.GeneralStreamsServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/Cancel", implementation.cancel, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/Repeat", implementation.repeat, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/AddMessage", implementation.add_message, general_streams.scailo_pb2.GeneralStreamsServiceMessageCreateRequest)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/SaveMessageForLater", implementation.save_message_for_later, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/DeleteMessage", implementation.delete_message, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewMessageByUUID", implementation.view_message_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewMessages", implementation.view_messages, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewPaginatedMessages", implementation.view_paginated_messages, general_streams.scailo_pb2.GeneralStreamMessagesSearchRequest)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/SearchMessagesWithPagination", implementation.search_messages_with_pagination, general_streams.scailo_pb2.GeneralStreamMessagesSearchRequest)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewMessageReceipts", implementation.view_message_receipts, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/AddInternalSubscriber", implementation.add_internal_subscriber, general_streams.scailo_pb2.GeneralStreamsServiceInternalSubscriberCreateRequest)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/DeleteInternalSubscriber", implementation.delete_internal_subscriber, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewInternalSubscriberByID", implementation.view_internal_subscriber_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewInternalSubscribers", implementation.view_internal_subscribers, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ImportInternalSubscribersFromTeam", implementation.import_internal_subscribers_from_team, general_streams.scailo_pb2.GeneralStreamsServiceImportInternalSubscribersRequest)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ImportInternalSubscribersFromDepartment", implementation.import_internal_subscribers_from_department, general_streams.scailo_pb2.GeneralStreamsServiceImportInternalSubscribersRequest)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/ViewWithPagination", implementation.view_with_pagination, general_streams.scailo_pb2.GeneralStreamsServicePaginationReq)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/SearchAll", implementation.search_all, general_streams.scailo_pb2.GeneralStreamsServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/Filter", implementation.filter, general_streams.scailo_pb2.GeneralStreamsServiceFilterReq)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/Count", implementation.count, general_streams.scailo_pb2.GeneralStreamsServiceCountReq)
    app.register_unary_rpc("/Scailo.GeneralStreamsService/DownloadAsCSV", implementation.download_as_csv, general_streams.scailo_pb2.GeneralStreamsServiceFilterReq)
    return app
