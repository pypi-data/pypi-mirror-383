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

from scailo_sdk import base, general_settings

class GeneralSettingsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_update_settings(
        self, req: general_settings.scailo_pb2.GeneralSettingsUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call UpdateSettings, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralSettingsService/UpdateSettings"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def update_settings(
        self, req: general_settings.scailo_pb2.GeneralSettingsUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_update_settings(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_settings(
        self, req: base.scailo_pb2.Empty,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_settings.scailo_pb2.GeneralSettings]:
        """Low-level method to call ViewSettings, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralSettingsService/ViewSettings"
        return self._connect_client.call_unary(url, req, general_settings.scailo_pb2.GeneralSettings,extra_headers, timeout_seconds)


    def view_settings(
        self, req: base.scailo_pb2.Empty,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_settings.scailo_pb2.GeneralSettings:
        response = self.call_view_settings(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_update_organization_logo(
        self, req: base.scailo_pb2.StandardFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call UpdateOrganizationLogo, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralSettingsService/UpdateOrganizationLogo"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)


    def update_organization_logo(
        self, req: base.scailo_pb2.StandardFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = self.call_update_organization_logo(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_organization_logo(
        self, req: base.scailo_pb2.Empty,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.ImageResponse]:
        """Low-level method to call ViewOrganizationLogo, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralSettingsService/ViewOrganizationLogo"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.ImageResponse,extra_headers, timeout_seconds)


    def view_organization_logo(
        self, req: base.scailo_pb2.Empty,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.ImageResponse:
        response = self.call_view_organization_logo(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncGeneralSettingsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_update_settings(
        self, req: general_settings.scailo_pb2.GeneralSettingsUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call UpdateSettings, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralSettingsService/UpdateSettings"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def update_settings(
        self, req: general_settings.scailo_pb2.GeneralSettingsUpdateRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_update_settings(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_settings(
        self, req: base.scailo_pb2.Empty,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[general_settings.scailo_pb2.GeneralSettings]:
        """Low-level method to call ViewSettings, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralSettingsService/ViewSettings"
        return await self._connect_client.call_unary(url, req, general_settings.scailo_pb2.GeneralSettings,extra_headers, timeout_seconds)

    async def view_settings(
        self, req: base.scailo_pb2.Empty,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> general_settings.scailo_pb2.GeneralSettings:
        response = await self.call_view_settings(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_update_organization_logo(
        self, req: base.scailo_pb2.StandardFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierResponse]:
        """Low-level method to call UpdateOrganizationLogo, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralSettingsService/UpdateOrganizationLogo"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierResponse,extra_headers, timeout_seconds)

    async def update_organization_logo(
        self, req: base.scailo_pb2.StandardFile,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierResponse:
        response = await self.call_update_organization_logo(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_organization_logo(
        self, req: base.scailo_pb2.Empty,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.ImageResponse]:
        """Low-level method to call ViewOrganizationLogo, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.GeneralSettingsService/ViewOrganizationLogo"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.ImageResponse,extra_headers, timeout_seconds)

    async def view_organization_logo(
        self, req: base.scailo_pb2.Empty,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.ImageResponse:
        response = await self.call_view_organization_logo(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class GeneralSettingsServiceProtocol(typing.Protocol):
    def update_settings(self, req: ClientRequest[general_settings.scailo_pb2.GeneralSettingsUpdateRequest]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_settings(self, req: ClientRequest[base.scailo_pb2.Empty]) -> ServerResponse[general_settings.scailo_pb2.GeneralSettings]:
        ...
    def update_organization_logo(self, req: ClientRequest[base.scailo_pb2.StandardFile]) -> ServerResponse[base.scailo_pb2.IdentifierResponse]:
        ...
    def view_organization_logo(self, req: ClientRequest[base.scailo_pb2.Empty]) -> ServerResponse[base.scailo_pb2.ImageResponse]:
        ...

GENERAL_SETTINGS_SERVICE_PATH_PREFIX = "/Scailo.GeneralSettingsService"

def wsgi_general_settings_service(implementation: GeneralSettingsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.GeneralSettingsService/UpdateSettings", implementation.update_settings, general_settings.scailo_pb2.GeneralSettingsUpdateRequest)
    app.register_unary_rpc("/Scailo.GeneralSettingsService/ViewSettings", implementation.view_settings, base.scailo_pb2.Empty)
    app.register_unary_rpc("/Scailo.GeneralSettingsService/UpdateOrganizationLogo", implementation.update_organization_logo, base.scailo_pb2.StandardFile)
    app.register_unary_rpc("/Scailo.GeneralSettingsService/ViewOrganizationLogo", implementation.view_organization_logo, base.scailo_pb2.Empty)
    return app
