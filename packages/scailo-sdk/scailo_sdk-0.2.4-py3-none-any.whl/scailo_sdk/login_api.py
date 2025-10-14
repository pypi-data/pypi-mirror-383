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

from scailo_sdk import base, login

class LoginServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_user_login_primary(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.UserLoginResponse]:
        """Low-level method to call UserLoginPrimary, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/UserLoginPrimary"
        return self._connect_client.call_unary(url, req, login.scailo_pb2.UserLoginResponse,extra_headers, timeout_seconds)


    def user_login_primary(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.UserLoginResponse:
        response = self.call_user_login_primary(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_login_as_employee_primary(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.UserLoginResponse]:
        """Low-level method to call LoginAsEmployeePrimary, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/LoginAsEmployeePrimary"
        return self._connect_client.call_unary(url, req, login.scailo_pb2.UserLoginResponse,extra_headers, timeout_seconds)


    def login_as_employee_primary(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.UserLoginResponse:
        response = self.call_login_as_employee_primary(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_login_as_employee_secondary(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.UserLoginResponse]:
        """Low-level method to call LoginAsEmployeeSecondary, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/LoginAsEmployeeSecondary"
        return self._connect_client.call_unary(url, req, login.scailo_pb2.UserLoginResponse,extra_headers, timeout_seconds)


    def login_as_employee_secondary(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.UserLoginResponse:
        response = self.call_login_as_employee_secondary(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_login_as_vendor_user(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.VendorUserLoginResponse]:
        """Low-level method to call LoginAsVendorUser, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/LoginAsVendorUser"
        return self._connect_client.call_unary(url, req, login.scailo_pb2.VendorUserLoginResponse,extra_headers, timeout_seconds)


    def login_as_vendor_user(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.VendorUserLoginResponse:
        response = self.call_login_as_vendor_user(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_login_as_client_user(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.ClientUserLoginResponse]:
        """Low-level method to call LoginAsClientUser, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/LoginAsClientUser"
        return self._connect_client.call_unary(url, req, login.scailo_pb2.ClientUserLoginResponse,extra_headers, timeout_seconds)


    def login_as_client_user(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.ClientUserLoginResponse:
        response = self.call_login_as_client_user(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_is_auth_token_valid(
        self, req: login.scailo_pb2.AuthTokenValidityRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call IsAuthTokenValid, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/IsAuthTokenValid"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)


    def is_auth_token_valid(
        self, req: login.scailo_pb2.AuthTokenValidityRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = self.call_is_auth_token_valid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_logout(
        self, req: login.scailo_pb2.LogoutRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.LogoutResponse]:
        """Low-level method to call Logout, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/Logout"
        return self._connect_client.call_unary(url, req, login.scailo_pb2.LogoutResponse,extra_headers, timeout_seconds)


    def logout(
        self, req: login.scailo_pb2.LogoutRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.LogoutResponse:
        response = self.call_logout(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_history(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.UserLoginHistoryList]:
        """Low-level method to call ViewHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/ViewHistory"
        return self._connect_client.call_unary(url, req, login.scailo_pb2.UserLoginHistoryList,extra_headers, timeout_seconds)


    def view_history(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.UserLoginHistoryList:
        response = self.call_view_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncLoginServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_user_login_primary(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.UserLoginResponse]:
        """Low-level method to call UserLoginPrimary, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/UserLoginPrimary"
        return await self._connect_client.call_unary(url, req, login.scailo_pb2.UserLoginResponse,extra_headers, timeout_seconds)

    async def user_login_primary(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.UserLoginResponse:
        response = await self.call_user_login_primary(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_login_as_employee_primary(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.UserLoginResponse]:
        """Low-level method to call LoginAsEmployeePrimary, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/LoginAsEmployeePrimary"
        return await self._connect_client.call_unary(url, req, login.scailo_pb2.UserLoginResponse,extra_headers, timeout_seconds)

    async def login_as_employee_primary(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.UserLoginResponse:
        response = await self.call_login_as_employee_primary(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_login_as_employee_secondary(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.UserLoginResponse]:
        """Low-level method to call LoginAsEmployeeSecondary, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/LoginAsEmployeeSecondary"
        return await self._connect_client.call_unary(url, req, login.scailo_pb2.UserLoginResponse,extra_headers, timeout_seconds)

    async def login_as_employee_secondary(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.UserLoginResponse:
        response = await self.call_login_as_employee_secondary(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_login_as_vendor_user(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.VendorUserLoginResponse]:
        """Low-level method to call LoginAsVendorUser, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/LoginAsVendorUser"
        return await self._connect_client.call_unary(url, req, login.scailo_pb2.VendorUserLoginResponse,extra_headers, timeout_seconds)

    async def login_as_vendor_user(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.VendorUserLoginResponse:
        response = await self.call_login_as_vendor_user(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_login_as_client_user(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.ClientUserLoginResponse]:
        """Low-level method to call LoginAsClientUser, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/LoginAsClientUser"
        return await self._connect_client.call_unary(url, req, login.scailo_pb2.ClientUserLoginResponse,extra_headers, timeout_seconds)

    async def login_as_client_user(
        self, req: login.scailo_pb2.UserLoginRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.ClientUserLoginResponse:
        response = await self.call_login_as_client_user(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_is_auth_token_valid(
        self, req: login.scailo_pb2.AuthTokenValidityRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call IsAuthTokenValid, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/IsAuthTokenValid"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)

    async def is_auth_token_valid(
        self, req: login.scailo_pb2.AuthTokenValidityRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = await self.call_is_auth_token_valid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_logout(
        self, req: login.scailo_pb2.LogoutRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.LogoutResponse]:
        """Low-level method to call Logout, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/Logout"
        return await self._connect_client.call_unary(url, req, login.scailo_pb2.LogoutResponse,extra_headers, timeout_seconds)

    async def logout(
        self, req: login.scailo_pb2.LogoutRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.LogoutResponse:
        response = await self.call_logout(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_history(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[login.scailo_pb2.UserLoginHistoryList]:
        """Low-level method to call ViewHistory, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LoginService/ViewHistory"
        return await self._connect_client.call_unary(url, req, login.scailo_pb2.UserLoginHistoryList,extra_headers, timeout_seconds)

    async def view_history(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> login.scailo_pb2.UserLoginHistoryList:
        response = await self.call_view_history(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class LoginServiceProtocol(typing.Protocol):
    def user_login_primary(self, req: ClientRequest[login.scailo_pb2.UserLoginRequest]) -> ServerResponse[login.scailo_pb2.UserLoginResponse]:
        ...
    def login_as_employee_primary(self, req: ClientRequest[login.scailo_pb2.UserLoginRequest]) -> ServerResponse[login.scailo_pb2.UserLoginResponse]:
        ...
    def login_as_employee_secondary(self, req: ClientRequest[login.scailo_pb2.UserLoginRequest]) -> ServerResponse[login.scailo_pb2.UserLoginResponse]:
        ...
    def login_as_vendor_user(self, req: ClientRequest[login.scailo_pb2.UserLoginRequest]) -> ServerResponse[login.scailo_pb2.VendorUserLoginResponse]:
        ...
    def login_as_client_user(self, req: ClientRequest[login.scailo_pb2.UserLoginRequest]) -> ServerResponse[login.scailo_pb2.ClientUserLoginResponse]:
        ...
    def is_auth_token_valid(self, req: ClientRequest[login.scailo_pb2.AuthTokenValidityRequest]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def logout(self, req: ClientRequest[login.scailo_pb2.LogoutRequest]) -> ServerResponse[login.scailo_pb2.LogoutResponse]:
        ...
    def view_history(self, req: ClientRequest[base.scailo_pb2.SimpleSearchReq]) -> ServerResponse[login.scailo_pb2.UserLoginHistoryList]:
        ...

LOGIN_SERVICE_PATH_PREFIX = "/Scailo.LoginService"

def wsgi_login_service(implementation: LoginServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.LoginService/UserLoginPrimary", implementation.user_login_primary, login.scailo_pb2.UserLoginRequest)
    app.register_unary_rpc("/Scailo.LoginService/LoginAsEmployeePrimary", implementation.login_as_employee_primary, login.scailo_pb2.UserLoginRequest)
    app.register_unary_rpc("/Scailo.LoginService/LoginAsEmployeeSecondary", implementation.login_as_employee_secondary, login.scailo_pb2.UserLoginRequest)
    app.register_unary_rpc("/Scailo.LoginService/LoginAsVendorUser", implementation.login_as_vendor_user, login.scailo_pb2.UserLoginRequest)
    app.register_unary_rpc("/Scailo.LoginService/LoginAsClientUser", implementation.login_as_client_user, login.scailo_pb2.UserLoginRequest)
    app.register_unary_rpc("/Scailo.LoginService/IsAuthTokenValid", implementation.is_auth_token_valid, login.scailo_pb2.AuthTokenValidityRequest)
    app.register_unary_rpc("/Scailo.LoginService/Logout", implementation.logout, login.scailo_pb2.LogoutRequest)
    app.register_unary_rpc("/Scailo.LoginService/ViewHistory", implementation.view_history, base.scailo_pb2.SimpleSearchReq)
    return app
