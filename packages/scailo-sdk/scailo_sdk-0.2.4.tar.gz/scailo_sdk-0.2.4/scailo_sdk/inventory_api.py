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

from scailo_sdk import base, inventory

class InventoryServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_view_by_hash(
        self, req: inventory.scailo_pb2.InventoryHashSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventory]:
        """Low-level method to call ViewByHash, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewByHash"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventory,extra_headers, timeout_seconds)


    def view_by_hash(
        self, req: inventory.scailo_pb2.InventoryHashSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventory:
        response = self.call_view_by_hash(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_by_short_url(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventory]:
        """Low-level method to call ViewByShortURL, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewByShortURL"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventory,extra_headers, timeout_seconds)


    def view_by_short_url(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventory:
        response = self.call_view_by_short_url(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_issuable(
        self, req: inventory.scailo_pb2.IssuableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewIssuable, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewIssuable"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def view_issuable(
        self, req: inventory.scailo_pb2.IssuableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_view_issuable(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_issued_for_goods_dispatch(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewIssuedForGoodsDispatch, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewIssuedForGoodsDispatch"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def view_issued_for_goods_dispatch(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_view_issued_for_goods_dispatch(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_issued_for_outward_job_free_issue_material(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewIssuedForOutwardJobFreeIssueMaterial, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewIssuedForOutwardJobFreeIssueMaterial"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def view_issued_for_outward_job_free_issue_material(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_view_issued_for_outward_job_free_issue_material(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_admitted_from_goods_receipt(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewAdmittedFromGoodsReceipt, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewAdmittedFromGoodsReceipt"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def view_admitted_from_goods_receipt(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_view_admitted_from_goods_receipt(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_admitted_from_inward_job_free_issue_material(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewAdmittedFromInwardJobFreeIssueMaterial, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewAdmittedFromInwardJobFreeIssueMaterial"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def view_admitted_from_inward_job_free_issue_material(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_view_admitted_from_inward_job_free_issue_material(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_admitted_from_production_plan(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewAdmittedFromProductionPlan, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewAdmittedFromProductionPlan"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def view_admitted_from_production_plan(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_view_admitted_from_production_plan(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_returnable_for_purchase_order(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewReturnableForPurchaseOrder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewReturnableForPurchaseOrder"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def view_returnable_for_purchase_order(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_view_returnable_for_purchase_order(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_returnable_for_inward_job(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewReturnableForInwardJob, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewReturnableForInwardJob"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def view_returnable_for_inward_job(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_view_returnable_for_inward_job(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_returnable_for_stock_issuance(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewReturnableForStockIssuance, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewReturnableForStockIssuance"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def view_returnable_for_stock_issuance(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_view_returnable_for_stock_issuance(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_returnable_for_sales_order(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewReturnableForSalesOrder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewReturnableForSalesOrder"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def view_returnable_for_sales_order(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_view_returnable_for_sales_order(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_returnable_for_outward_job(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewReturnableForOutwardJob, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewReturnableForOutwardJob"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def view_returnable_for_outward_job(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_view_returnable_for_outward_job(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_quantity_remaining(
        self, req: inventory.scailo_pb2.InventoryServiceFamilyQuantityReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call ViewQuantityRemaining, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewQuantityRemaining"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)


    def view_quantity_remaining(
        self, req: inventory.scailo_pb2.InventoryServiceFamilyQuantityReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = self.call_view_quantity_remaining(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_count_work_in_progress(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call CountWorkInProgress, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/CountWorkInProgress"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)


    def count_work_in_progress(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = self.call_count_work_in_progress(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_count_indented(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call CountIndented, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/CountIndented"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)


    def count_indented(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = self.call_count_indented(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_count_ordered(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call CountOrdered, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/CountOrdered"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)


    def count_ordered(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = self.call_count_ordered(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_base_demand_quantity(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call ViewBaseDemandQuantity, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewBaseDemandQuantity"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)


    def view_base_demand_quantity(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = self.call_view_base_demand_quantity(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_adjusted_demand_quantity(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call ViewAdjustedDemandQuantity, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewAdjustedDemandQuantity"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)


    def view_adjusted_demand_quantity(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = self.call_view_adjusted_demand_quantity(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_required_quantity(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call ViewRequiredQuantity, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewRequiredQuantity"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)


    def view_required_quantity(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = self.call_view_required_quantity(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_consolidated_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.ConsolidatedInventoryStatistics]:
        """Low-level method to call ViewConsolidatedStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewConsolidatedStatistics"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.ConsolidatedInventoryStatistics,extra_headers, timeout_seconds)


    def view_consolidated_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.ConsolidatedInventoryStatistics:
        response = self.call_view_consolidated_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_in_storage(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewInStorage, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewInStorage"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)


    def view_in_storage(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = self.call_view_in_storage(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_work_in_progress_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.InventoryWorkInProgressStatistics]:
        """Low-level method to call ViewWorkInProgressStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewWorkInProgressStatistics"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.InventoryWorkInProgressStatistics,extra_headers, timeout_seconds)


    def view_work_in_progress_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.InventoryWorkInProgressStatistics:
        response = self.call_view_work_in_progress_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_indented_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.InventoryIndentedStatistics]:
        """Low-level method to call ViewIndentedStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewIndentedStatistics"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.InventoryIndentedStatistics,extra_headers, timeout_seconds)


    def view_indented_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.InventoryIndentedStatistics:
        response = self.call_view_indented_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_ordered_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.InventoryOrderedStatistics]:
        """Low-level method to call ViewOrderedStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewOrderedStatistics"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.InventoryOrderedStatistics,extra_headers, timeout_seconds)


    def view_ordered_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.InventoryOrderedStatistics:
        response = self.call_view_ordered_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_detailed_demand(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.InventoryDetailedDemand]:
        """Low-level method to call ViewDetailedDemand, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewDetailedDemand"
        return self._connect_client.call_unary(url, req, inventory.scailo_pb2.InventoryDetailedDemand,extra_headers, timeout_seconds)


    def view_detailed_demand(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.InventoryDetailedDemand:
        response = self.call_view_detailed_demand(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncInventoryServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_view_by_hash(
        self, req: inventory.scailo_pb2.InventoryHashSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventory]:
        """Low-level method to call ViewByHash, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewByHash"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventory,extra_headers, timeout_seconds)

    async def view_by_hash(
        self, req: inventory.scailo_pb2.InventoryHashSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventory:
        response = await self.call_view_by_hash(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_by_short_url(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventory]:
        """Low-level method to call ViewByShortURL, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewByShortURL"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventory,extra_headers, timeout_seconds)

    async def view_by_short_url(
        self, req: base.scailo_pb2.SimpleSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventory:
        response = await self.call_view_by_short_url(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_issuable(
        self, req: inventory.scailo_pb2.IssuableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewIssuable, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewIssuable"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def view_issuable(
        self, req: inventory.scailo_pb2.IssuableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_view_issuable(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_issued_for_goods_dispatch(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewIssuedForGoodsDispatch, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewIssuedForGoodsDispatch"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def view_issued_for_goods_dispatch(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_view_issued_for_goods_dispatch(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_issued_for_outward_job_free_issue_material(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewIssuedForOutwardJobFreeIssueMaterial, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewIssuedForOutwardJobFreeIssueMaterial"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def view_issued_for_outward_job_free_issue_material(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_view_issued_for_outward_job_free_issue_material(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_admitted_from_goods_receipt(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewAdmittedFromGoodsReceipt, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewAdmittedFromGoodsReceipt"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def view_admitted_from_goods_receipt(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_view_admitted_from_goods_receipt(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_admitted_from_inward_job_free_issue_material(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewAdmittedFromInwardJobFreeIssueMaterial, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewAdmittedFromInwardJobFreeIssueMaterial"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def view_admitted_from_inward_job_free_issue_material(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_view_admitted_from_inward_job_free_issue_material(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_admitted_from_production_plan(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewAdmittedFromProductionPlan, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewAdmittedFromProductionPlan"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def view_admitted_from_production_plan(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_view_admitted_from_production_plan(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_returnable_for_purchase_order(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewReturnableForPurchaseOrder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewReturnableForPurchaseOrder"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def view_returnable_for_purchase_order(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_view_returnable_for_purchase_order(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_returnable_for_inward_job(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewReturnableForInwardJob, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewReturnableForInwardJob"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def view_returnable_for_inward_job(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_view_returnable_for_inward_job(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_returnable_for_stock_issuance(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewReturnableForStockIssuance, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewReturnableForStockIssuance"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def view_returnable_for_stock_issuance(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_view_returnable_for_stock_issuance(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_returnable_for_sales_order(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewReturnableForSalesOrder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewReturnableForSalesOrder"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def view_returnable_for_sales_order(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_view_returnable_for_sales_order(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_returnable_for_outward_job(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewReturnableForOutwardJob, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewReturnableForOutwardJob"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def view_returnable_for_outward_job(
        self, req: inventory.scailo_pb2.ReturnableInventorySearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_view_returnable_for_outward_job(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_quantity_remaining(
        self, req: inventory.scailo_pb2.InventoryServiceFamilyQuantityReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call ViewQuantityRemaining, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewQuantityRemaining"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)

    async def view_quantity_remaining(
        self, req: inventory.scailo_pb2.InventoryServiceFamilyQuantityReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = await self.call_view_quantity_remaining(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_count_work_in_progress(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call CountWorkInProgress, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/CountWorkInProgress"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)

    async def count_work_in_progress(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = await self.call_count_work_in_progress(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_count_indented(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call CountIndented, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/CountIndented"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)

    async def count_indented(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = await self.call_count_indented(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_count_ordered(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call CountOrdered, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/CountOrdered"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)

    async def count_ordered(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = await self.call_count_ordered(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_base_demand_quantity(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call ViewBaseDemandQuantity, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewBaseDemandQuantity"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)

    async def view_base_demand_quantity(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = await self.call_view_base_demand_quantity(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_adjusted_demand_quantity(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call ViewAdjustedDemandQuantity, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewAdjustedDemandQuantity"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)

    async def view_adjusted_demand_quantity(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = await self.call_view_adjusted_demand_quantity(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_required_quantity(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.QuantityResponse]:
        """Low-level method to call ViewRequiredQuantity, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewRequiredQuantity"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.QuantityResponse,extra_headers, timeout_seconds)

    async def view_required_quantity(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.QuantityResponse:
        response = await self.call_view_required_quantity(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_consolidated_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.ConsolidatedInventoryStatistics]:
        """Low-level method to call ViewConsolidatedStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewConsolidatedStatistics"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.ConsolidatedInventoryStatistics,extra_headers, timeout_seconds)

    async def view_consolidated_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.ConsolidatedInventoryStatistics:
        response = await self.call_view_consolidated_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_in_storage(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.GenericInventoryList]:
        """Low-level method to call ViewInStorage, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewInStorage"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.GenericInventoryList,extra_headers, timeout_seconds)

    async def view_in_storage(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.GenericInventoryList:
        response = await self.call_view_in_storage(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_work_in_progress_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.InventoryWorkInProgressStatistics]:
        """Low-level method to call ViewWorkInProgressStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewWorkInProgressStatistics"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.InventoryWorkInProgressStatistics,extra_headers, timeout_seconds)

    async def view_work_in_progress_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.InventoryWorkInProgressStatistics:
        response = await self.call_view_work_in_progress_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_indented_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.InventoryIndentedStatistics]:
        """Low-level method to call ViewIndentedStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewIndentedStatistics"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.InventoryIndentedStatistics,extra_headers, timeout_seconds)

    async def view_indented_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.InventoryIndentedStatistics:
        response = await self.call_view_indented_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_ordered_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.InventoryOrderedStatistics]:
        """Low-level method to call ViewOrderedStatistics, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewOrderedStatistics"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.InventoryOrderedStatistics,extra_headers, timeout_seconds)

    async def view_ordered_statistics(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.InventoryOrderedStatistics:
        response = await self.call_view_ordered_statistics(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_detailed_demand(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[inventory.scailo_pb2.InventoryDetailedDemand]:
        """Low-level method to call ViewDetailedDemand, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.InventoryService/ViewDetailedDemand"
        return await self._connect_client.call_unary(url, req, inventory.scailo_pb2.InventoryDetailedDemand,extra_headers, timeout_seconds)

    async def view_detailed_demand(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> inventory.scailo_pb2.InventoryDetailedDemand:
        response = await self.call_view_detailed_demand(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class InventoryServiceProtocol(typing.Protocol):
    def view_by_hash(self, req: ClientRequest[inventory.scailo_pb2.InventoryHashSearchReq]) -> ServerResponse[inventory.scailo_pb2.GenericInventory]:
        ...
    def view_by_short_url(self, req: ClientRequest[base.scailo_pb2.SimpleSearchReq]) -> ServerResponse[inventory.scailo_pb2.GenericInventory]:
        ...
    def view_issuable(self, req: ClientRequest[inventory.scailo_pb2.IssuableInventorySearchReq]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def view_issued_for_goods_dispatch(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def view_issued_for_outward_job_free_issue_material(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def view_admitted_from_goods_receipt(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def view_admitted_from_inward_job_free_issue_material(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def view_admitted_from_production_plan(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def view_returnable_for_purchase_order(self, req: ClientRequest[inventory.scailo_pb2.ReturnableInventorySearchReq]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def view_returnable_for_inward_job(self, req: ClientRequest[inventory.scailo_pb2.ReturnableInventorySearchReq]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def view_returnable_for_stock_issuance(self, req: ClientRequest[inventory.scailo_pb2.ReturnableInventorySearchReq]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def view_returnable_for_sales_order(self, req: ClientRequest[inventory.scailo_pb2.ReturnableInventorySearchReq]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def view_returnable_for_outward_job(self, req: ClientRequest[inventory.scailo_pb2.ReturnableInventorySearchReq]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def view_quantity_remaining(self, req: ClientRequest[inventory.scailo_pb2.InventoryServiceFamilyQuantityReq]) -> ServerResponse[base.scailo_pb2.QuantityResponse]:
        ...
    def count_work_in_progress(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[base.scailo_pb2.QuantityResponse]:
        ...
    def count_indented(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[base.scailo_pb2.QuantityResponse]:
        ...
    def count_ordered(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[base.scailo_pb2.QuantityResponse]:
        ...
    def view_base_demand_quantity(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[base.scailo_pb2.QuantityResponse]:
        ...
    def view_adjusted_demand_quantity(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[base.scailo_pb2.QuantityResponse]:
        ...
    def view_required_quantity(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[base.scailo_pb2.QuantityResponse]:
        ...
    def view_consolidated_statistics(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inventory.scailo_pb2.ConsolidatedInventoryStatistics]:
        ...
    def view_in_storage(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inventory.scailo_pb2.GenericInventoryList]:
        ...
    def view_work_in_progress_statistics(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inventory.scailo_pb2.InventoryWorkInProgressStatistics]:
        ...
    def view_indented_statistics(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inventory.scailo_pb2.InventoryIndentedStatistics]:
        ...
    def view_ordered_statistics(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inventory.scailo_pb2.InventoryOrderedStatistics]:
        ...
    def view_detailed_demand(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[inventory.scailo_pb2.InventoryDetailedDemand]:
        ...

INVENTORY_SERVICE_PATH_PREFIX = "/Scailo.InventoryService"

def wsgi_inventory_service(implementation: InventoryServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.InventoryService/ViewByHash", implementation.view_by_hash, inventory.scailo_pb2.InventoryHashSearchReq)
    app.register_unary_rpc("/Scailo.InventoryService/ViewByShortURL", implementation.view_by_short_url, base.scailo_pb2.SimpleSearchReq)
    app.register_unary_rpc("/Scailo.InventoryService/ViewIssuable", implementation.view_issuable, inventory.scailo_pb2.IssuableInventorySearchReq)
    app.register_unary_rpc("/Scailo.InventoryService/ViewIssuedForGoodsDispatch", implementation.view_issued_for_goods_dispatch, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewIssuedForOutwardJobFreeIssueMaterial", implementation.view_issued_for_outward_job_free_issue_material, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewAdmittedFromGoodsReceipt", implementation.view_admitted_from_goods_receipt, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewAdmittedFromInwardJobFreeIssueMaterial", implementation.view_admitted_from_inward_job_free_issue_material, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewAdmittedFromProductionPlan", implementation.view_admitted_from_production_plan, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewReturnableForPurchaseOrder", implementation.view_returnable_for_purchase_order, inventory.scailo_pb2.ReturnableInventorySearchReq)
    app.register_unary_rpc("/Scailo.InventoryService/ViewReturnableForInwardJob", implementation.view_returnable_for_inward_job, inventory.scailo_pb2.ReturnableInventorySearchReq)
    app.register_unary_rpc("/Scailo.InventoryService/ViewReturnableForStockIssuance", implementation.view_returnable_for_stock_issuance, inventory.scailo_pb2.ReturnableInventorySearchReq)
    app.register_unary_rpc("/Scailo.InventoryService/ViewReturnableForSalesOrder", implementation.view_returnable_for_sales_order, inventory.scailo_pb2.ReturnableInventorySearchReq)
    app.register_unary_rpc("/Scailo.InventoryService/ViewReturnableForOutwardJob", implementation.view_returnable_for_outward_job, inventory.scailo_pb2.ReturnableInventorySearchReq)
    app.register_unary_rpc("/Scailo.InventoryService/ViewQuantityRemaining", implementation.view_quantity_remaining, inventory.scailo_pb2.InventoryServiceFamilyQuantityReq)
    app.register_unary_rpc("/Scailo.InventoryService/CountWorkInProgress", implementation.count_work_in_progress, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/CountIndented", implementation.count_indented, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/CountOrdered", implementation.count_ordered, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewBaseDemandQuantity", implementation.view_base_demand_quantity, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewAdjustedDemandQuantity", implementation.view_adjusted_demand_quantity, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewRequiredQuantity", implementation.view_required_quantity, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewConsolidatedStatistics", implementation.view_consolidated_statistics, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewInStorage", implementation.view_in_storage, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewWorkInProgressStatistics", implementation.view_work_in_progress_statistics, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewIndentedStatistics", implementation.view_indented_statistics, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewOrderedStatistics", implementation.view_ordered_statistics, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.InventoryService/ViewDetailedDemand", implementation.view_detailed_demand, base.scailo_pb2.Identifier)
    return app
