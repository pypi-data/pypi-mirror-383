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

from scailo_sdk import forms_fields_data

class FormsFieldsDataServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_view_form_field_data_history(
        self, req: forms_fields_data.scailo_pb2.FormFieldDatumHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[forms_fields_data.scailo_pb2.FormFieldDatumList]:
        """Low-level method to call ViewFormFieldDataHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.FormsFieldsDataService/ViewFormFieldDataHistory"
        return self._connect_client.call_unary(url, req, forms_fields_data.scailo_pb2.FormFieldDatumList,extra_headers, timeout_seconds)


    def view_form_field_data_history(
        self, req: forms_fields_data.scailo_pb2.FormFieldDatumHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> forms_fields_data.scailo_pb2.FormFieldDatumList:
        response = self.call_view_form_field_data_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncFormsFieldsDataServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_view_form_field_data_history(
        self, req: forms_fields_data.scailo_pb2.FormFieldDatumHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[forms_fields_data.scailo_pb2.FormFieldDatumList]:
        """Low-level method to call ViewFormFieldDataHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.FormsFieldsDataService/ViewFormFieldDataHistory"
        return await self._connect_client.call_unary(url, req, forms_fields_data.scailo_pb2.FormFieldDatumList,extra_headers, timeout_seconds)

    async def view_form_field_data_history(
        self, req: forms_fields_data.scailo_pb2.FormFieldDatumHistoryRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> forms_fields_data.scailo_pb2.FormFieldDatumList:
        response = await self.call_view_form_field_data_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class FormsFieldsDataServiceProtocol(typing.Protocol):
    def view_form_field_data_history(self, req: ClientRequest[forms_fields_data.scailo_pb2.FormFieldDatumHistoryRequest]) -> ServerResponse[forms_fields_data.scailo_pb2.FormFieldDatumList]:
        ...

FORMS_FIELDS_DATA_SERVICE_PATH_PREFIX = "/Scailo.FormsFieldsDataService"

def wsgi_forms_fields_data_service(implementation: FormsFieldsDataServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.FormsFieldsDataService/ViewFormFieldDataHistory", implementation.view_form_field_data_history, forms_fields_data.scailo_pb2.FormFieldDatumHistoryRequest)
    return app
