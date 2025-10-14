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

from scailo_sdk import activities, base

class ActivitiesServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_create(
        self, req: activities.scailo_pb2.ActivitiesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/Create"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def create(
        self, req: activities.scailo_pb2.ActivitiesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: activities.scailo_pb2.ActivitiesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Update, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/Update"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def update(
        self, req: activities.scailo_pb2.ActivitiesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ActivitiesService/Cancel"
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
        url = self.base_url + "/Scailo.ActivitiesService/Complete"
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
        url = self.base_url + "/Scailo.ActivitiesService/Reopen"
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
        url = self.base_url + "/Scailo.ActivitiesService/Repeat"
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
        url = self.base_url + "/Scailo.ActivitiesService/CommentAdd"
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

    def call_send_email(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call SendEmail, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/SendEmail"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def send_email(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_send_email(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_action(
        self, req: activities.scailo_pb2.ActivitiesServiceActionCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddAction, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/AddAction"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_action(
        self, req: activities.scailo_pb2.ActivitiesServiceActionCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_action(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_action_with_timer(
        self, req: activities.scailo_pb2.ActivitiesServiceActionWithTimerCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddActionWithTimer, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/AddActionWithTimer"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_action_with_timer(
        self, req: activities.scailo_pb2.ActivitiesServiceActionWithTimerCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_action_with_timer(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_action(
        self, req: activities.scailo_pb2.ActivitiesServiceActionUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyAction, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ModifyAction"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def modify_action(
        self, req: activities.scailo_pb2.ActivitiesServiceActionUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_modify_action(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_action(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteAction, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DeleteAction"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_action(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_action(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_reorder_actions(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderActions, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ReorderActions"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def reorder_actions(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_reorder_actions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_action_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityAction]:
        """Low-level method to call ViewActionByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewActionByID"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityAction,extra_headers, timeout_seconds)


    def view_action_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityAction:
        response = self.call_view_action_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_action_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityActionStatistics]:
        """Low-level method to call ViewActionStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewActionStatistics"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityActionStatistics,extra_headers, timeout_seconds)


    def view_action_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityActionStatistics:
        response = self.call_view_action_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_actions(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityActionsList]:
        """Low-level method to call ViewActions, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewActions"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityActionsList,extra_headers, timeout_seconds)


    def view_actions(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityActionsList:
        response = self.call_view_actions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_action_history(
        self, req: activities.scailo_pb2.ActivityActionHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityActionsList]:
        """Low-level method to call ViewActionHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewActionHistory"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityActionsList,extra_headers, timeout_seconds)


    def view_action_history(
        self, req: activities.scailo_pb2.ActivityActionHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityActionsList:
        response = self.call_view_action_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_actions(
        self, req: activities.scailo_pb2.ActivityActionsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse]:
        """Low-level method to call ViewPaginatedActions, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewPaginatedActions"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse,extra_headers, timeout_seconds)


    def view_paginated_actions(
        self, req: activities.scailo_pb2.ActivityActionsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse:
        response = self.call_view_paginated_actions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_actions_with_pagination(
        self, req: activities.scailo_pb2.ActivityActionsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse]:
        """Low-level method to call SearchActionsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/SearchActionsWithPagination"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse,extra_headers, timeout_seconds)


    def search_actions_with_pagination(
        self, req: activities.scailo_pb2.ActivityActionsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse:
        response = self.call_search_actions_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_download_actions_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadActionsAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DownloadActionsAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_actions_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_actions_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_upload_activity_actions(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadActivityActions, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/UploadActivityActions"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)


    def upload_activity_actions(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = self.call_upload_activity_actions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_activity_tag_association(
        self, req: activities.scailo_pb2.ActivitiesServiceActivityTagAssociationCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddActivityTagAssociation, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/AddActivityTagAssociation"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_activity_tag_association(
        self, req: activities.scailo_pb2.ActivitiesServiceActivityTagAssociationCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_activity_tag_association(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_activity_tag_association(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteActivityTagAssociation, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DeleteActivityTagAssociation"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_activity_tag_association(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_activity_tag_association(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_activity_tag_association_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityTagAssociation]:
        """Low-level method to call ViewActivityTagAssociationByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewActivityTagAssociationByID"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityTagAssociation,extra_headers, timeout_seconds)


    def view_activity_tag_association_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityTagAssociation:
        response = self.call_view_activity_tag_association_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_activity_tag_associations(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityTagAssociationsList]:
        """Low-level method to call ViewActivityTagAssociations, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewActivityTagAssociations"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityTagAssociationsList,extra_headers, timeout_seconds)


    def view_activity_tag_associations(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityTagAssociationsList:
        response = self.call_view_activity_tag_associations(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_owner(
        self, req: activities.scailo_pb2.ActivitiesServiceOwnerCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddOwner, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/AddOwner"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_owner(
        self, req: activities.scailo_pb2.ActivitiesServiceOwnerCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_owner(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_owner(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteOwner, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DeleteOwner"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_owner(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_owner(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_owner_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityOwner]:
        """Low-level method to call ViewOwnerByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewOwnerByID"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityOwner,extra_headers, timeout_seconds)


    def view_owner_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityOwner:
        response = self.call_view_owner_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_owners(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityOwnersList]:
        """Low-level method to call ViewOwners, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewOwners"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityOwnersList,extra_headers, timeout_seconds)


    def view_owners(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityOwnersList:
        response = self.call_view_owners(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_import_owners_from_team(
        self, req: activities.scailo_pb2.ActivitiesServiceImportOwnersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportOwnersFromTeam, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ImportOwnersFromTeam"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def import_owners_from_team(
        self, req: activities.scailo_pb2.ActivitiesServiceImportOwnersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_import_owners_from_team(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_import_owners_from_department(
        self, req: activities.scailo_pb2.ActivitiesServiceImportOwnersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportOwnersFromDepartment, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ImportOwnersFromDepartment"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def import_owners_from_department(
        self, req: activities.scailo_pb2.ActivitiesServiceImportOwnersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_import_owners_from_department(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_supervisor(
        self, req: activities.scailo_pb2.ActivitiesServiceSupervisorCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddSupervisor, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/AddSupervisor"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_supervisor(
        self, req: activities.scailo_pb2.ActivitiesServiceSupervisorCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_supervisor(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_supervisor(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteSupervisor, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DeleteSupervisor"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def delete_supervisor(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_delete_supervisor(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_supervisor_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitySupervisor]:
        """Low-level method to call ViewSupervisorByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewSupervisorByID"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitySupervisor,extra_headers, timeout_seconds)


    def view_supervisor_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitySupervisor:
        response = self.call_view_supervisor_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_supervisors(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitySupervisorsList]:
        """Low-level method to call ViewSupervisors, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewSupervisors"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitySupervisorsList,extra_headers, timeout_seconds)


    def view_supervisors(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitySupervisorsList:
        response = self.call_view_supervisors(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_timer(
        self, req: activities.scailo_pb2.ActivitiesServiceTimerCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddTimer, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/AddTimer"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def add_timer(
        self, req: activities.scailo_pb2.ActivitiesServiceTimerCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_add_timer(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_end_timer(
        self, req: activities.scailo_pb2.ActivitiesServiceTimerEndRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call EndTimer, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/EndTimer"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def end_timer(
        self, req: activities.scailo_pb2.ActivitiesServiceTimerEndRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_end_timer(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_timer_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityTimer]:
        """Low-level method to call ViewTimerByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewTimerByID"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityTimer,extra_headers, timeout_seconds)


    def view_timer_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityTimer:
        response = self.call_view_timer_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_timers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityTimersList]:
        """Low-level method to call ViewTimers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewTimers"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityTimersList,extra_headers, timeout_seconds)


    def view_timers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityTimersList:
        response = self.call_view_timers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_paginated_timers(
        self, req: activities.scailo_pb2.ActivityTimersSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse]:
        """Low-level method to call ViewPaginatedTimers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewPaginatedTimers"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse,extra_headers, timeout_seconds)


    def view_paginated_timers(
        self, req: activities.scailo_pb2.ActivityTimersSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse:
        response = self.call_view_paginated_timers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_timers_with_pagination(
        self, req: activities.scailo_pb2.ActivityTimersSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse]:
        """Low-level method to call SearchTimersWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/SearchTimersWithPagination"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse,extra_headers, timeout_seconds)


    def search_timers_with_pagination(
        self, req: activities.scailo_pb2.ActivityTimersSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse:
        response = self.call_search_timers_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_download_timers_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadTimersAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DownloadTimersAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_timers_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_timers_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.Activity]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewByID"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.Activity,extra_headers, timeout_seconds)


    def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.Activity:
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
    ) -> UnaryOutput[activities.scailo_pb2.Activity]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewByUUID"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.Activity,extra_headers, timeout_seconds)


    def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.Activity:
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
    ) -> UnaryOutput[activities.scailo_pb2.Activity]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewEssentialByID"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.Activity,extra_headers, timeout_seconds)


    def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.Activity:
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
    ) -> UnaryOutput[activities.scailo_pb2.Activity]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewEssentialByUUID"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.Activity,extra_headers, timeout_seconds)


    def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.Activity:
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
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewFromIDs"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesList,extra_headers, timeout_seconds)


    def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesList:
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
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewAll"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesList,extra_headers, timeout_seconds)


    def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesList:
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
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewAllForEntityUUID"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesList,extra_headers, timeout_seconds)


    def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesList:
        response = self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_with_pagination(
        self, req: activities.scailo_pb2.ActivitiesServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewWithPagination"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesServicePaginationResponse,extra_headers, timeout_seconds)


    def view_with_pagination(
        self, req: activities.scailo_pb2.ActivitiesServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesServicePaginationResponse:
        response = self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_statistics(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityStatistics]:
        """Low-level method to call ViewStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewStatistics"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityStatistics,extra_headers, timeout_seconds)


    def view_statistics(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityStatistics:
        response = self.call_view_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search_all(
        self, req: activities.scailo_pb2.ActivitiesServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/SearchAll"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesList,extra_headers, timeout_seconds)


    def search_all(
        self, req: activities.scailo_pb2.ActivitiesServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesList:
        response = self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_filter(
        self, req: activities.scailo_pb2.ActivitiesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/Filter"
        return self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesList,extra_headers, timeout_seconds)


    def filter(
        self, req: activities.scailo_pb2.ActivitiesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesList:
        response = self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_count(
        self, req: activities.scailo_pb2.ActivitiesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: activities.scailo_pb2.ActivitiesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: activities.scailo_pb2.ActivitiesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DownloadAsCSV"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_as_csv(
        self, req: activities.scailo_pb2.ActivitiesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ActivitiesService/ImportFromCSV"
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


class AsyncActivitiesServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_create(
        self, req: activities.scailo_pb2.ActivitiesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Create, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/Create"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def create(
        self, req: activities.scailo_pb2.ActivitiesServiceCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: activities.scailo_pb2.ActivitiesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call Update, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/Update"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def update(
        self, req: activities.scailo_pb2.ActivitiesServiceUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ActivitiesService/Cancel"
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
        url = self.base_url + "/Scailo.ActivitiesService/Complete"
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
        url = self.base_url + "/Scailo.ActivitiesService/Reopen"
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
        url = self.base_url + "/Scailo.ActivitiesService/Repeat"
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
        url = self.base_url + "/Scailo.ActivitiesService/CommentAdd"
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

    async def call_send_email(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call SendEmail, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/SendEmail"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def send_email(
        self, req: base.scailo_pb2.IdentifierWithEmailAttributes,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_send_email(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_action(
        self, req: activities.scailo_pb2.ActivitiesServiceActionCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddAction, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/AddAction"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_action(
        self, req: activities.scailo_pb2.ActivitiesServiceActionCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_action(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_action_with_timer(
        self, req: activities.scailo_pb2.ActivitiesServiceActionWithTimerCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddActionWithTimer, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/AddActionWithTimer"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_action_with_timer(
        self, req: activities.scailo_pb2.ActivitiesServiceActionWithTimerCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_action_with_timer(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_action(
        self, req: activities.scailo_pb2.ActivitiesServiceActionUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ModifyAction, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ModifyAction"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def modify_action(
        self, req: activities.scailo_pb2.ActivitiesServiceActionUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_modify_action(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_action(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteAction, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DeleteAction"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_action(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_action(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_reorder_actions(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ReorderActions, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ReorderActions"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def reorder_actions(
        self, req: base.scailo_pb2.ReorderItemsRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_reorder_actions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_action_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityAction]:
        """Low-level method to call ViewActionByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewActionByID"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityAction,extra_headers, timeout_seconds)

    async def view_action_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityAction:
        response = await self.call_view_action_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_action_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityActionStatistics]:
        """Low-level method to call ViewActionStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewActionStatistics"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityActionStatistics,extra_headers, timeout_seconds)

    async def view_action_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityActionStatistics:
        response = await self.call_view_action_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_actions(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityActionsList]:
        """Low-level method to call ViewActions, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewActions"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityActionsList,extra_headers, timeout_seconds)

    async def view_actions(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityActionsList:
        response = await self.call_view_actions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_action_history(
        self, req: activities.scailo_pb2.ActivityActionHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityActionsList]:
        """Low-level method to call ViewActionHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewActionHistory"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityActionsList,extra_headers, timeout_seconds)

    async def view_action_history(
        self, req: activities.scailo_pb2.ActivityActionHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityActionsList:
        response = await self.call_view_action_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_actions(
        self, req: activities.scailo_pb2.ActivityActionsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse]:
        """Low-level method to call ViewPaginatedActions, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewPaginatedActions"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse,extra_headers, timeout_seconds)

    async def view_paginated_actions(
        self, req: activities.scailo_pb2.ActivityActionsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse:
        response = await self.call_view_paginated_actions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_actions_with_pagination(
        self, req: activities.scailo_pb2.ActivityActionsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse]:
        """Low-level method to call SearchActionsWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/SearchActionsWithPagination"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse,extra_headers, timeout_seconds)

    async def search_actions_with_pagination(
        self, req: activities.scailo_pb2.ActivityActionsSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse:
        response = await self.call_search_actions_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_download_actions_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadActionsAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DownloadActionsAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_actions_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_actions_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_upload_activity_actions(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifiersList]:
        """Low-level method to call UploadActivityActions, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/UploadActivityActions"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifiersList,extra_headers, timeout_seconds)

    async def upload_activity_actions(
        self, req: base.scailo_pb2.IdentifierUUIDWithFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifiersList:
        response = await self.call_upload_activity_actions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_activity_tag_association(
        self, req: activities.scailo_pb2.ActivitiesServiceActivityTagAssociationCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddActivityTagAssociation, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/AddActivityTagAssociation"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_activity_tag_association(
        self, req: activities.scailo_pb2.ActivitiesServiceActivityTagAssociationCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_activity_tag_association(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_activity_tag_association(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteActivityTagAssociation, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DeleteActivityTagAssociation"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_activity_tag_association(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_activity_tag_association(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_activity_tag_association_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityTagAssociation]:
        """Low-level method to call ViewActivityTagAssociationByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewActivityTagAssociationByID"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityTagAssociation,extra_headers, timeout_seconds)

    async def view_activity_tag_association_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityTagAssociation:
        response = await self.call_view_activity_tag_association_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_activity_tag_associations(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityTagAssociationsList]:
        """Low-level method to call ViewActivityTagAssociations, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewActivityTagAssociations"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityTagAssociationsList,extra_headers, timeout_seconds)

    async def view_activity_tag_associations(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityTagAssociationsList:
        response = await self.call_view_activity_tag_associations(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_owner(
        self, req: activities.scailo_pb2.ActivitiesServiceOwnerCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddOwner, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/AddOwner"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_owner(
        self, req: activities.scailo_pb2.ActivitiesServiceOwnerCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_owner(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_owner(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteOwner, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DeleteOwner"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_owner(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_owner(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_owner_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityOwner]:
        """Low-level method to call ViewOwnerByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewOwnerByID"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityOwner,extra_headers, timeout_seconds)

    async def view_owner_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityOwner:
        response = await self.call_view_owner_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_owners(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityOwnersList]:
        """Low-level method to call ViewOwners, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewOwners"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityOwnersList,extra_headers, timeout_seconds)

    async def view_owners(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityOwnersList:
        response = await self.call_view_owners(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_import_owners_from_team(
        self, req: activities.scailo_pb2.ActivitiesServiceImportOwnersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportOwnersFromTeam, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ImportOwnersFromTeam"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def import_owners_from_team(
        self, req: activities.scailo_pb2.ActivitiesServiceImportOwnersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_import_owners_from_team(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_import_owners_from_department(
        self, req: activities.scailo_pb2.ActivitiesServiceImportOwnersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call ImportOwnersFromDepartment, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ImportOwnersFromDepartment"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def import_owners_from_department(
        self, req: activities.scailo_pb2.ActivitiesServiceImportOwnersRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_import_owners_from_department(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_supervisor(
        self, req: activities.scailo_pb2.ActivitiesServiceSupervisorCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddSupervisor, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/AddSupervisor"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_supervisor(
        self, req: activities.scailo_pb2.ActivitiesServiceSupervisorCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_supervisor(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_supervisor(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call DeleteSupervisor, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DeleteSupervisor"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def delete_supervisor(
        self, req: base.scailo_pb2.IdentifierWithUserComment,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_delete_supervisor(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_supervisor_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitySupervisor]:
        """Low-level method to call ViewSupervisorByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewSupervisorByID"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitySupervisor,extra_headers, timeout_seconds)

    async def view_supervisor_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitySupervisor:
        response = await self.call_view_supervisor_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_supervisors(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitySupervisorsList]:
        """Low-level method to call ViewSupervisors, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewSupervisors"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitySupervisorsList,extra_headers, timeout_seconds)

    async def view_supervisors(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitySupervisorsList:
        response = await self.call_view_supervisors(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_timer(
        self, req: activities.scailo_pb2.ActivitiesServiceTimerCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call AddTimer, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/AddTimer"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def add_timer(
        self, req: activities.scailo_pb2.ActivitiesServiceTimerCreateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_add_timer(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_end_timer(
        self, req: activities.scailo_pb2.ActivitiesServiceTimerEndRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call EndTimer, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/EndTimer"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def end_timer(
        self, req: activities.scailo_pb2.ActivitiesServiceTimerEndRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_end_timer(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_timer_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityTimer]:
        """Low-level method to call ViewTimerByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewTimerByID"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityTimer,extra_headers, timeout_seconds)

    async def view_timer_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityTimer:
        response = await self.call_view_timer_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_timers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityTimersList]:
        """Low-level method to call ViewTimers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewTimers"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityTimersList,extra_headers, timeout_seconds)

    async def view_timers(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityTimersList:
        response = await self.call_view_timers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_paginated_timers(
        self, req: activities.scailo_pb2.ActivityTimersSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse]:
        """Low-level method to call ViewPaginatedTimers, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewPaginatedTimers"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse,extra_headers, timeout_seconds)

    async def view_paginated_timers(
        self, req: activities.scailo_pb2.ActivityTimersSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse:
        response = await self.call_view_paginated_timers(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_timers_with_pagination(
        self, req: activities.scailo_pb2.ActivityTimersSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse]:
        """Low-level method to call SearchTimersWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/SearchTimersWithPagination"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse,extra_headers, timeout_seconds)

    async def search_timers_with_pagination(
        self, req: activities.scailo_pb2.ActivityTimersSearchRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse:
        response = await self.call_search_timers_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_download_timers_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadTimersAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DownloadTimersAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_timers_as_csv(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_timers_as_csv(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.Activity]:
        """Low-level method to call ViewByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewByID"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.Activity,extra_headers, timeout_seconds)

    async def view_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.Activity:
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
    ) -> UnaryOutput[activities.scailo_pb2.Activity]:
        """Low-level method to call ViewByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewByUUID"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.Activity,extra_headers, timeout_seconds)

    async def view_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.Activity:
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
    ) -> UnaryOutput[activities.scailo_pb2.Activity]:
        """Low-level method to call ViewEssentialByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewEssentialByID"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.Activity,extra_headers, timeout_seconds)

    async def view_essential_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.Activity:
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
    ) -> UnaryOutput[activities.scailo_pb2.Activity]:
        """Low-level method to call ViewEssentialByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewEssentialByUUID"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.Activity,extra_headers, timeout_seconds)

    async def view_essential_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.Activity:
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
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesList]:
        """Low-level method to call ViewFromIDs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewFromIDs"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesList,extra_headers, timeout_seconds)

    async def view_from_i_ds(
        self, req: base.scailo_pb2.IdentifiersList,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesList:
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
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesList]:
        """Low-level method to call ViewAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewAll"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesList,extra_headers, timeout_seconds)

    async def view_all(
        self, req: base.scailo_pb2.ActiveStatus,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesList:
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
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesList]:
        """Low-level method to call ViewAllForEntityUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewAllForEntityUUID"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesList,extra_headers, timeout_seconds)

    async def view_all_for_entity_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesList:
        response = await self.call_view_all_for_entity_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_with_pagination(
        self, req: activities.scailo_pb2.ActivitiesServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesServicePaginationResponse]:
        """Low-level method to call ViewWithPagination, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewWithPagination"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesServicePaginationResponse,extra_headers, timeout_seconds)

    async def view_with_pagination(
        self, req: activities.scailo_pb2.ActivitiesServicePaginationReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesServicePaginationResponse:
        response = await self.call_view_with_pagination(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_statistics(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivityStatistics]:
        """Low-level method to call ViewStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/ViewStatistics"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivityStatistics,extra_headers, timeout_seconds)

    async def view_statistics(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivityStatistics:
        response = await self.call_view_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search_all(
        self, req: activities.scailo_pb2.ActivitiesServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesList]:
        """Low-level method to call SearchAll, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/SearchAll"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesList,extra_headers, timeout_seconds)

    async def search_all(
        self, req: activities.scailo_pb2.ActivitiesServiceSearchAllReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesList:
        response = await self.call_search_all(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_filter(
        self, req: activities.scailo_pb2.ActivitiesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[activities.scailo_pb2.ActivitiesList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/Filter"
        return await self._connect_client.call_unary(url, req, activities.scailo_pb2.ActivitiesList,extra_headers, timeout_seconds)

    async def filter(
        self, req: activities.scailo_pb2.ActivitiesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> activities.scailo_pb2.ActivitiesList:
        response = await self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_count(
        self, req: activities.scailo_pb2.ActivitiesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: activities.scailo_pb2.ActivitiesServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        self, req: activities.scailo_pb2.ActivitiesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadAsCSV, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.ActivitiesService/DownloadAsCSV"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_as_csv(
        self, req: activities.scailo_pb2.ActivitiesServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
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
        url = self.base_url + "/Scailo.ActivitiesService/ImportFromCSV"
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
class ActivitiesServiceProtocol(typing.Protocol):
    def create(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def update(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
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
    def send_email(self, req: ClientRequest[base.scailo_pb2.IdentifierWithEmailAttributes]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def add_action(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceActionCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_action_with_timer(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceActionWithTimerCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def modify_action(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceActionUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_action(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def reorder_actions(self, req: ClientRequest[base.scailo_pb2.ReorderItemsRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_action_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[activities.scailo_pb2.ActivityAction]:
        ...
    def view_action_statistics(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[activities.scailo_pb2.ActivityActionStatistics]:
        ...
    def view_actions(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[activities.scailo_pb2.ActivityActionsList]:
        ...
    def view_action_history(self, req: ClientRequest[activities.scailo_pb2.ActivityActionHistoryRequest]) -> ServerResponse[activities.scailo_pb2.ActivityActionsList]:
        ...
    def view_paginated_actions(self, req: ClientRequest[activities.scailo_pb2.ActivityActionsSearchRequest]) -> ServerResponse[activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse]:
        ...
    def search_actions_with_pagination(self, req: ClientRequest[activities.scailo_pb2.ActivityActionsSearchRequest]) -> ServerResponse[activities.scailo_pb2.ActivitiesServicePaginatedActionsResponse]:
        ...
    def download_actions_as_csv(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def upload_activity_actions(self, req: ClientRequest[base.scailo_pb2.IdentifierUUIDWithFile]) -> ServerResponse[base.scailo_pb2.IdentifiersList]:
        ...
    def add_activity_tag_association(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceActivityTagAssociationCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_activity_tag_association(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_activity_tag_association_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[activities.scailo_pb2.ActivityTagAssociation]:
        ...
    def view_activity_tag_associations(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[activities.scailo_pb2.ActivityTagAssociationsList]:
        ...
    def add_owner(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceOwnerCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_owner(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_owner_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[activities.scailo_pb2.ActivityOwner]:
        ...
    def view_owners(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[activities.scailo_pb2.ActivityOwnersList]:
        ...
    def import_owners_from_team(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceImportOwnersRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def import_owners_from_department(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceImportOwnersRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def add_supervisor(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceSupervisorCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def delete_supervisor(self, req: ClientRequest[base.scailo_pb2.IdentifierWithUserComment]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_supervisor_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[activities.scailo_pb2.ActivitySupervisor]:
        ...
    def view_supervisors(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[activities.scailo_pb2.ActivitySupervisorsList]:
        ...
    def add_timer(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceTimerCreateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def end_timer(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceTimerEndRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_timer_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[activities.scailo_pb2.ActivityTimer]:
        ...
    def view_timers(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[activities.scailo_pb2.ActivityTimersList]:
        ...
    def view_paginated_timers(self, req: ClientRequest[activities.scailo_pb2.ActivityTimersSearchRequest]) -> ServerResponse[activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse]:
        ...
    def search_timers_with_pagination(self, req: ClientRequest[activities.scailo_pb2.ActivityTimersSearchRequest]) -> ServerResponse[activities.scailo_pb2.ActivitiesServicePaginatedTimersResponse]:
        ...
    def download_timers_as_csv(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def view_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[activities.scailo_pb2.Activity]:
        ...
    def view_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[activities.scailo_pb2.Activity]:
        ...
    def view_essential_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[activities.scailo_pb2.Activity]:
        ...
    def view_essential_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[activities.scailo_pb2.Activity]:
        ...
    def view_from_i_ds(self, req: ClientRequest[base.scailo_pb2.IdentifiersList]) -> ServerResponse[activities.scailo_pb2.ActivitiesList]:
        ...
    def view_all(self, req: ClientRequest[base.scailo_pb2.ActiveStatus]) -> ServerResponse[activities.scailo_pb2.ActivitiesList]:
        ...
    def view_all_for_entity_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[activities.scailo_pb2.ActivitiesList]:
        ...
    def view_with_pagination(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServicePaginationReq]) -> ServerResponse[activities.scailo_pb2.ActivitiesServicePaginationResponse]:
        ...
    def view_statistics(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[activities.scailo_pb2.ActivityStatistics]:
        ...
    def search_all(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceSearchAllReq]) -> ServerResponse[activities.scailo_pb2.ActivitiesList]:
        ...
    def filter(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceFilterReq]) -> ServerResponse[activities.scailo_pb2.ActivitiesList]:
        ...
    def count(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def download_as_csv(self, req: ClientRequest[activities.scailo_pb2.ActivitiesServiceFilterReq]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def import_from_csv(self, req: ClientRequest[base.scailo_pb2.StandardFile]) -> ServerResponse[base.scailo_pb2.IdentifierUUIDsList]:
        ...

ACTIVITIES_SERVICE_PATH_PREFIX = "/Scailo.ActivitiesService"

def wsgi_activities_service(implementation: ActivitiesServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.ActivitiesService/Create", implementation.create, activities.scailo_pb2.ActivitiesServiceCreateRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/Update", implementation.update, activities.scailo_pb2.ActivitiesServiceUpdateRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/Cancel", implementation.cancel, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ActivitiesService/Complete", implementation.complete, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ActivitiesService/Reopen", implementation.reopen, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ActivitiesService/Repeat", implementation.repeat, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ActivitiesService/CommentAdd", implementation.comment_add, base.scailo_pb2.IdentifierUUIDWithUserComment)
    app.register_unary_rpc("/Scailo.ActivitiesService/SendEmail", implementation.send_email, base.scailo_pb2.IdentifierWithEmailAttributes)
    app.register_unary_rpc("/Scailo.ActivitiesService/AddAction", implementation.add_action, activities.scailo_pb2.ActivitiesServiceActionCreateRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/AddActionWithTimer", implementation.add_action_with_timer, activities.scailo_pb2.ActivitiesServiceActionWithTimerCreateRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/ModifyAction", implementation.modify_action, activities.scailo_pb2.ActivitiesServiceActionUpdateRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/DeleteAction", implementation.delete_action, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.ActivitiesService/ReorderActions", implementation.reorder_actions, base.scailo_pb2.ReorderItemsRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewActionByID", implementation.view_action_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewActionStatistics", implementation.view_action_statistics, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewActions", implementation.view_actions, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewActionHistory", implementation.view_action_history, activities.scailo_pb2.ActivityActionHistoryRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewPaginatedActions", implementation.view_paginated_actions, activities.scailo_pb2.ActivityActionsSearchRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/SearchActionsWithPagination", implementation.search_actions_with_pagination, activities.scailo_pb2.ActivityActionsSearchRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/DownloadActionsAsCSV", implementation.download_actions_as_csv, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ActivitiesService/UploadActivityActions", implementation.upload_activity_actions, base.scailo_pb2.IdentifierUUIDWithFile)
    app.register_unary_rpc("/Scailo.ActivitiesService/AddActivityTagAssociation", implementation.add_activity_tag_association, activities.scailo_pb2.ActivitiesServiceActivityTagAssociationCreateRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/DeleteActivityTagAssociation", implementation.delete_activity_tag_association, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewActivityTagAssociationByID", implementation.view_activity_tag_association_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewActivityTagAssociations", implementation.view_activity_tag_associations, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ActivitiesService/AddOwner", implementation.add_owner, activities.scailo_pb2.ActivitiesServiceOwnerCreateRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/DeleteOwner", implementation.delete_owner, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewOwnerByID", implementation.view_owner_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewOwners", implementation.view_owners, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ActivitiesService/ImportOwnersFromTeam", implementation.import_owners_from_team, activities.scailo_pb2.ActivitiesServiceImportOwnersRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/ImportOwnersFromDepartment", implementation.import_owners_from_department, activities.scailo_pb2.ActivitiesServiceImportOwnersRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/AddSupervisor", implementation.add_supervisor, activities.scailo_pb2.ActivitiesServiceSupervisorCreateRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/DeleteSupervisor", implementation.delete_supervisor, base.scailo_pb2.IdentifierWithUserComment)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewSupervisorByID", implementation.view_supervisor_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewSupervisors", implementation.view_supervisors, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ActivitiesService/AddTimer", implementation.add_timer, activities.scailo_pb2.ActivitiesServiceTimerCreateRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/EndTimer", implementation.end_timer, activities.scailo_pb2.ActivitiesServiceTimerEndRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewTimerByID", implementation.view_timer_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewTimers", implementation.view_timers, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewPaginatedTimers", implementation.view_paginated_timers, activities.scailo_pb2.ActivityTimersSearchRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/SearchTimersWithPagination", implementation.search_timers_with_pagination, activities.scailo_pb2.ActivityTimersSearchRequest)
    app.register_unary_rpc("/Scailo.ActivitiesService/DownloadTimersAsCSV", implementation.download_timers_as_csv, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewByID", implementation.view_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewByUUID", implementation.view_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewEssentialByID", implementation.view_essential_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewEssentialByUUID", implementation.view_essential_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewFromIDs", implementation.view_from_i_ds, base.scailo_pb2.IdentifiersList)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewAll", implementation.view_all, base.scailo_pb2.ActiveStatus)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewAllForEntityUUID", implementation.view_all_for_entity_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewWithPagination", implementation.view_with_pagination, activities.scailo_pb2.ActivitiesServicePaginationReq)
    app.register_unary_rpc("/Scailo.ActivitiesService/ViewStatistics", implementation.view_statistics, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.ActivitiesService/SearchAll", implementation.search_all, activities.scailo_pb2.ActivitiesServiceSearchAllReq)
    app.register_unary_rpc("/Scailo.ActivitiesService/Filter", implementation.filter, activities.scailo_pb2.ActivitiesServiceFilterReq)
    app.register_unary_rpc("/Scailo.ActivitiesService/Count", implementation.count, activities.scailo_pb2.ActivitiesServiceCountReq)
    app.register_unary_rpc("/Scailo.ActivitiesService/DownloadAsCSV", implementation.download_as_csv, activities.scailo_pb2.ActivitiesServiceFilterReq)
    app.register_unary_rpc("/Scailo.ActivitiesService/ImportFromCSV", implementation.import_from_csv, base.scailo_pb2.StandardFile)
    return app
