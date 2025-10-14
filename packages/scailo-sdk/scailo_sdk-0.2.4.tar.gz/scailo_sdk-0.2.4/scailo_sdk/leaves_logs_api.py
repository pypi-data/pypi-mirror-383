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

from scailo_sdk import base, leaves_logs

class LeavesLogsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_filter(
        self, req: leaves_logs.scailo_pb2.LeavesLogsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_logs.scailo_pb2.LeavesLogsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesLogsService/Filter"
        return self._connect_client.call_unary(url, req, leaves_logs.scailo_pb2.LeavesLogsList,extra_headers, timeout_seconds)


    def filter(
        self, req: leaves_logs.scailo_pb2.LeavesLogsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_logs.scailo_pb2.LeavesLogsList:
        response = self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_count_employee_leaves(
        self, req: leaves_logs.scailo_pb2.LeavesLogsCountEmployeeLeavesRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call CountEmployeeLeaves, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesLogsService/CountEmployeeLeaves"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count_employee_leaves(
        self, req: leaves_logs.scailo_pb2.LeavesLogsCountEmployeeLeavesRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = self.call_count_employee_leaves(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_count(
        self, req: leaves_logs.scailo_pb2.LeavesLogsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesLogsService/Count"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def count(
        self, req: leaves_logs.scailo_pb2.LeavesLogsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = self.call_count(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncLeavesLogsServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_filter(
        self, req: leaves_logs.scailo_pb2.LeavesLogsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[leaves_logs.scailo_pb2.LeavesLogsList]:
        """Low-level method to call Filter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesLogsService/Filter"
        return await self._connect_client.call_unary(url, req, leaves_logs.scailo_pb2.LeavesLogsList,extra_headers, timeout_seconds)

    async def filter(
        self, req: leaves_logs.scailo_pb2.LeavesLogsServiceFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> leaves_logs.scailo_pb2.LeavesLogsList:
        response = await self.call_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_count_employee_leaves(
        self, req: leaves_logs.scailo_pb2.LeavesLogsCountEmployeeLeavesRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call CountEmployeeLeaves, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesLogsService/CountEmployeeLeaves"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count_employee_leaves(
        self, req: leaves_logs.scailo_pb2.LeavesLogsCountEmployeeLeavesRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = await self.call_count_employee_leaves(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_count(
        self, req: leaves_logs.scailo_pb2.LeavesLogsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call Count, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.LeavesLogsService/Count"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def count(
        self, req: leaves_logs.scailo_pb2.LeavesLogsServiceCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = await self.call_count(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class LeavesLogsServiceProtocol(typing.Protocol):
    def filter(self, req: ClientRequest[leaves_logs.scailo_pb2.LeavesLogsServiceFilterReq]) -> ServerResponse[leaves_logs.scailo_pb2.LeavesLogsList]:
        ...
    def count_employee_leaves(self, req: ClientRequest[leaves_logs.scailo_pb2.LeavesLogsCountEmployeeLeavesRequest]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...
    def count(self, req: ClientRequest[leaves_logs.scailo_pb2.LeavesLogsServiceCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...

LEAVES_LOGS_SERVICE_PATH_PREFIX = "/Scailo.LeavesLogsService"

def wsgi_leaves_logs_service(implementation: LeavesLogsServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.LeavesLogsService/Filter", implementation.filter, leaves_logs.scailo_pb2.LeavesLogsServiceFilterReq)
    app.register_unary_rpc("/Scailo.LeavesLogsService/CountEmployeeLeaves", implementation.count_employee_leaves, leaves_logs.scailo_pb2.LeavesLogsCountEmployeeLeavesRequest)
    app.register_unary_rpc("/Scailo.LeavesLogsService/Count", implementation.count, leaves_logs.scailo_pb2.LeavesLogsServiceCountReq)
    return app
