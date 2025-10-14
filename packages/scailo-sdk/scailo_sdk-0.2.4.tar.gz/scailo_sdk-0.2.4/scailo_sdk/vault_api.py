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

from scailo_sdk import base, roles, vault, vault_commons, vault_files, vault_folders

class VaultServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: urllib3.PoolManager | None = None,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = ConnectClient(http_client, protocol)
    def call_initiate_file(
        self, req: vault_files.scailo_pb2.VaultFileInitiateFileRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFileInitiateFileResponse]:
        """Low-level method to call InitiateFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/InitiateFile"
        return self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFileInitiateFileResponse,extra_headers, timeout_seconds)


    def initiate_file(
        self, req: vault_files.scailo_pb2.VaultFileInitiateFileRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFileInitiateFileResponse:
        response = self.call_initiate_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_file_chunk(
        self, req: vault_files.scailo_pb2.VaultFileAddChunkRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddFileChunk, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/AddFileChunk"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def add_file_chunk(
        self, req: vault_files.scailo_pb2.VaultFileAddChunkRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_add_file_chunk(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_complete_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call CompleteFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/CompleteFile"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def complete_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_complete_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_rename_file(
        self, req: vault_files.scailo_pb2.VaultFileRenameFileRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call RenameFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/RenameFile"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def rename_file(
        self, req: vault_files.scailo_pb2.VaultFileRenameFileRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_rename_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_unzip_file(
        self, req: vault_files.scailo_pb2.VaultFileUnzipRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call UnzipFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/UnzipFile"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def unzip_file(
        self, req: vault_files.scailo_pb2.VaultFileUnzipRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_unzip_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_persist_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call PersistFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/PersistFile"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def persist_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_persist_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_move_file(
        self, req: vault_files.scailo_pb2.VaultFileMoveFileRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call MoveFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/MoveFile"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def move_file(
        self, req: vault_files.scailo_pb2.VaultFileMoveFileRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_move_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call DeleteFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DeleteFile"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def delete_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_delete_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_file_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionAddRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddFilePermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/AddFilePermission"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def add_file_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionAddRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_add_file_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_file_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionModifyRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call ModifyFilePermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ModifyFilePermission"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def modify_file_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionModifyRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_modify_file_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_file_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call DeleteFilePermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DeleteFilePermission"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def delete_file_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_delete_file_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_download_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DownloadFile"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_download_file_version(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadFileVersion, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DownloadFileVersion"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_file_version(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_file_version(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_file_logo(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call ViewFileLogo, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileLogo"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def view_file_logo(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_view_file_logo(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_file_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFile]:
        """Low-level method to call ViewFileByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileByUUID"
        return self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFile,extra_headers, timeout_seconds)


    def view_file_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFile:
        response = self.call_view_file_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_file_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFile]:
        """Low-level method to call ViewFileByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileByID"
        return self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFile,extra_headers, timeout_seconds)


    def view_file_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFile:
        response = self.call_view_file_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_file_chunk(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFileVersionChunk]:
        """Low-level method to call ViewFileChunk, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileChunk"
        return self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFileVersionChunk,extra_headers, timeout_seconds)


    def view_file_chunk(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFileVersionChunk:
        response = self.call_view_file_chunk(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_file_chunk_metadata(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFileVersionChunk]:
        """Low-level method to call ViewFileChunkMetadata, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileChunkMetadata"
        return self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFileVersionChunk,extra_headers, timeout_seconds)


    def view_file_chunk_metadata(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFileVersionChunk:
        response = self.call_view_file_chunk_metadata(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_file_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.VaultPermission]:
        """Low-level method to call ViewFilePermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFilePermission"
        return self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.VaultPermission,extra_headers, timeout_seconds)


    def view_file_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.VaultPermission:
        response = self.call_view_file_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_does_file_exist(
        self, req: vault_commons.scailo_pb2.VaultDuplicateCheckReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call DoesFileExist, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DoesFileExist"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)


    def does_file_exist(
        self, req: vault_commons.scailo_pb2.VaultDuplicateCheckReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = self.call_does_file_exist(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_file_versions(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFileVersionsList]:
        """Low-level method to call ViewFileVersions, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileVersions"
        return self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFileVersionsList,extra_headers, timeout_seconds)


    def view_file_versions(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFileVersionsList:
        response = self.call_view_file_versions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_file_access_logs(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.VaultAccessLogsList]:
        """Low-level method to call ViewFileAccessLogs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileAccessLogs"
        return self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.VaultAccessLogsList,extra_headers, timeout_seconds)


    def view_file_access_logs(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.VaultAccessLogsList:
        response = self.call_view_file_access_logs(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_folder(
        self, req: vault_folders.scailo_pb2.VaultFolderAddRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/AddFolder"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def add_folder(
        self, req: vault_folders.scailo_pb2.VaultFolderAddRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_add_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_move_folder(
        self, req: vault_folders.scailo_pb2.VaultFolderMoveFolderRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call MoveFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/MoveFolder"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def move_folder(
        self, req: vault_folders.scailo_pb2.VaultFolderMoveFolderRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_move_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_rename_folder(
        self, req: vault_folders.scailo_pb2.VaultFolderRenameFolderRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call RenameFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/RenameFolder"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def rename_folder(
        self, req: vault_folders.scailo_pb2.VaultFolderRenameFolderRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_rename_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call DeleteFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DeleteFolder"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def delete_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_delete_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_zip_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call ZipFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ZipFolder"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def zip_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_zip_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_add_folder_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionAddRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddFolderPermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/AddFolderPermission"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def add_folder_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionAddRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_add_folder_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_modify_folder_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionModifyRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call ModifyFolderPermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ModifyFolderPermission"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def modify_folder_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionModifyRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_modify_folder_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_delete_folder_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call DeleteFolderPermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DeleteFolderPermission"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)


    def delete_folder_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = self.call_delete_folder_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_folder_by_id(
        self, req: base.scailo_pb2.IdentifierZeroable,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_folders.scailo_pb2.VaultFolder]:
        """Low-level method to call ViewFolderByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFolderByID"
        return self._connect_client.call_unary(url, req, vault_folders.scailo_pb2.VaultFolder,extra_headers, timeout_seconds)


    def view_folder_by_id(
        self, req: base.scailo_pb2.IdentifierZeroable,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_folders.scailo_pb2.VaultFolder:
        response = self.call_view_folder_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_folder_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_folders.scailo_pb2.VaultFolder]:
        """Low-level method to call ViewFolderByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFolderByUUID"
        return self._connect_client.call_unary(url, req, vault_folders.scailo_pb2.VaultFolder,extra_headers, timeout_seconds)


    def view_folder_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_folders.scailo_pb2.VaultFolder:
        response = self.call_view_folder_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_folder_download_status(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_folders.scailo_pb2.VaultFolderDownload]:
        """Low-level method to call ViewFolderDownloadStatus, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFolderDownloadStatus"
        return self._connect_client.call_unary(url, req, vault_folders.scailo_pb2.VaultFolderDownload,extra_headers, timeout_seconds)


    def view_folder_download_status(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_folders.scailo_pb2.VaultFolderDownload:
        response = self.call_view_folder_download_status(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_download_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DownloadFolder"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)


    def download_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = self.call_download_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_accessible_files_in_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFilesList]:
        """Low-level method to call ViewAccessibleFilesInFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewAccessibleFilesInFolder"
        return self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFilesList,extra_headers, timeout_seconds)


    def view_accessible_files_in_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFilesList:
        response = self.call_view_accessible_files_in_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_accessible_folders_in_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_folders.scailo_pb2.VaultFoldersList]:
        """Low-level method to call ViewAccessibleFoldersInFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewAccessibleFoldersInFolder"
        return self._connect_client.call_unary(url, req, vault_folders.scailo_pb2.VaultFoldersList,extra_headers, timeout_seconds)


    def view_accessible_folders_in_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_folders.scailo_pb2.VaultFoldersList:
        response = self.call_view_accessible_folders_in_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_accessible_resources_in_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.VaultResourcesList]:
        """Low-level method to call ViewAccessibleResourcesInFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewAccessibleResourcesInFolder"
        return self._connect_client.call_unary(url, req, vault.scailo_pb2.VaultResourcesList,extra_headers, timeout_seconds)


    def view_accessible_resources_in_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.VaultResourcesList:
        response = self.call_view_accessible_resources_in_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_folder_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.VaultPermission]:
        """Low-level method to call ViewFolderPermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFolderPermission"
        return self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.VaultPermission,extra_headers, timeout_seconds)


    def view_folder_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.VaultPermission:
        response = self.call_view_folder_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_does_folder_exist(
        self, req: vault_commons.scailo_pb2.VaultDuplicateCheckReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call DoesFolderExist, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DoesFolderExist"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)


    def does_folder_exist(
        self, req: vault_commons.scailo_pb2.VaultDuplicateCheckReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = self.call_does_folder_exist(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_folder_access_logs(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.VaultAccessLogsList]:
        """Low-level method to call ViewFolderAccessLogs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFolderAccessLogs"
        return self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.VaultAccessLogsList,extra_headers, timeout_seconds)


    def view_folder_access_logs(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.VaultAccessLogsList:
        response = self.call_view_folder_access_logs(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_view_passthrough_roles_for_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[roles.scailo_pb2.RolesList]:
        """Low-level method to call ViewPassthroughRolesForFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewPassthroughRolesForFolder"
        return self._connect_client.call_unary(url, req, roles.scailo_pb2.RolesList,extra_headers, timeout_seconds)


    def view_passthrough_roles_for_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> roles.scailo_pb2.RolesList:
        response = self.call_view_passthrough_roles_for_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_search(
        self, req: vault_commons.scailo_pb2.VaultSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.VaultSearchResponsesList]:
        """Low-level method to call Search, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/Search"
        return self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.VaultSearchResponsesList,extra_headers, timeout_seconds)


    def search(
        self, req: vault_commons.scailo_pb2.VaultSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.VaultSearchResponsesList:
        response = self.call_search(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_setup_gi_x(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.GiXAppRun]:
        """Low-level method to call SetupGiX, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/SetupGiX"
        return self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.GiXAppRun,extra_headers, timeout_seconds)


    def setup_gi_x(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.GiXAppRun:
        response = self.call_setup_gi_x(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_gi_x_relay_delete(
        self, req: vault.scailo_pb2.GiXRelayReqWithoutBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.GiXRelayResponse]:
        """Low-level method to call GiXRelayDELETE, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXRelayDELETE"
        return self._connect_client.call_unary(url, req, vault.scailo_pb2.GiXRelayResponse,extra_headers, timeout_seconds)


    def gi_x_relay_delete(
        self, req: vault.scailo_pb2.GiXRelayReqWithoutBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.GiXRelayResponse:
        response = self.call_gi_x_relay_delete(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_gi_x_relay_get(
        self, req: vault.scailo_pb2.GiXRelayReqWithoutBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.GiXRelayResponse]:
        """Low-level method to call GiXRelayGET, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXRelayGET"
        return self._connect_client.call_unary(url, req, vault.scailo_pb2.GiXRelayResponse,extra_headers, timeout_seconds)


    def gi_x_relay_get(
        self, req: vault.scailo_pb2.GiXRelayReqWithoutBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.GiXRelayResponse:
        response = self.call_gi_x_relay_get(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_gi_x_relay_head(
        self, req: vault.scailo_pb2.GiXRelayReqWithoutBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.GiXRelayResponse]:
        """Low-level method to call GiXRelayHEAD, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXRelayHEAD"
        return self._connect_client.call_unary(url, req, vault.scailo_pb2.GiXRelayResponse,extra_headers, timeout_seconds)


    def gi_x_relay_head(
        self, req: vault.scailo_pb2.GiXRelayReqWithoutBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.GiXRelayResponse:
        response = self.call_gi_x_relay_head(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_gi_x_relay_patch(
        self, req: vault.scailo_pb2.GiXRelayReqWithBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.GiXRelayResponse]:
        """Low-level method to call GiXRelayPATCH, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXRelayPATCH"
        return self._connect_client.call_unary(url, req, vault.scailo_pb2.GiXRelayResponse,extra_headers, timeout_seconds)


    def gi_x_relay_patch(
        self, req: vault.scailo_pb2.GiXRelayReqWithBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.GiXRelayResponse:
        response = self.call_gi_x_relay_patch(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_gi_x_relay_post(
        self, req: vault.scailo_pb2.GiXRelayReqWithBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.GiXRelayResponse]:
        """Low-level method to call GiXRelayPOST, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXRelayPOST"
        return self._connect_client.call_unary(url, req, vault.scailo_pb2.GiXRelayResponse,extra_headers, timeout_seconds)


    def gi_x_relay_post(
        self, req: vault.scailo_pb2.GiXRelayReqWithBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.GiXRelayResponse:
        response = self.call_gi_x_relay_post(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_gi_x_relay_put(
        self, req: vault.scailo_pb2.GiXRelayReqWithBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.GiXRelayResponse]:
        """Low-level method to call GiXRelayPUT, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXRelayPUT"
        return self._connect_client.call_unary(url, req, vault.scailo_pb2.GiXRelayResponse,extra_headers, timeout_seconds)


    def gi_x_relay_put(
        self, req: vault.scailo_pb2.GiXRelayReqWithBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.GiXRelayResponse:
        response = self.call_gi_x_relay_put(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_gi_x_filter(
        self, req: vault_commons.scailo_pb2.GiXAppRunFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.GiXAppRunsList]:
        """Low-level method to call GiXFilter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXFilter"
        return self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.GiXAppRunsList,extra_headers, timeout_seconds)


    def gi_x_filter(
        self, req: vault_commons.scailo_pb2.GiXAppRunFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.GiXAppRunsList:
        response = self.call_gi_x_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    def call_gi_x_count(
        self, req: vault_commons.scailo_pb2.GiXAppRunCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call GiXCount, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXCount"
        return self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)


    def gi_x_count(
        self, req: vault_commons.scailo_pb2.GiXAppRunCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = self.call_gi_x_count(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


class AsyncVaultServiceClient:
    def __init__(
        self,
        base_url: str,
        http_client: aiohttp.ClientSession,
        protocol: ConnectProtocol = ConnectProtocol.CONNECT_PROTOBUF,
    ):
        self.base_url = base_url
        self._connect_client = AsyncConnectClient(http_client, protocol)

    async def call_initiate_file(
        self, req: vault_files.scailo_pb2.VaultFileInitiateFileRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFileInitiateFileResponse]:
        """Low-level method to call InitiateFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/InitiateFile"
        return await self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFileInitiateFileResponse,extra_headers, timeout_seconds)

    async def initiate_file(
        self, req: vault_files.scailo_pb2.VaultFileInitiateFileRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFileInitiateFileResponse:
        response = await self.call_initiate_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_file_chunk(
        self, req: vault_files.scailo_pb2.VaultFileAddChunkRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddFileChunk, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/AddFileChunk"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def add_file_chunk(
        self, req: vault_files.scailo_pb2.VaultFileAddChunkRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_add_file_chunk(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_complete_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call CompleteFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/CompleteFile"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def complete_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_complete_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_rename_file(
        self, req: vault_files.scailo_pb2.VaultFileRenameFileRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call RenameFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/RenameFile"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def rename_file(
        self, req: vault_files.scailo_pb2.VaultFileRenameFileRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_rename_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_unzip_file(
        self, req: vault_files.scailo_pb2.VaultFileUnzipRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call UnzipFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/UnzipFile"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def unzip_file(
        self, req: vault_files.scailo_pb2.VaultFileUnzipRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_unzip_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_persist_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call PersistFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/PersistFile"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def persist_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_persist_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_move_file(
        self, req: vault_files.scailo_pb2.VaultFileMoveFileRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call MoveFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/MoveFile"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def move_file(
        self, req: vault_files.scailo_pb2.VaultFileMoveFileRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_move_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call DeleteFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DeleteFile"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def delete_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_delete_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_file_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionAddRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddFilePermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/AddFilePermission"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def add_file_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionAddRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_add_file_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_file_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionModifyRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call ModifyFilePermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ModifyFilePermission"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def modify_file_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionModifyRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_modify_file_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_file_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call DeleteFilePermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DeleteFilePermission"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def delete_file_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_delete_file_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_download_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadFile, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DownloadFile"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_file(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_file(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_download_file_version(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadFileVersion, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DownloadFileVersion"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_file_version(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_file_version(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_file_logo(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call ViewFileLogo, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileLogo"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def view_file_logo(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_view_file_logo(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_file_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFile]:
        """Low-level method to call ViewFileByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileByUUID"
        return await self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFile,extra_headers, timeout_seconds)

    async def view_file_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFile:
        response = await self.call_view_file_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_file_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFile]:
        """Low-level method to call ViewFileByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileByID"
        return await self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFile,extra_headers, timeout_seconds)

    async def view_file_by_id(
        self, req: base.scailo_pb2.Identifier,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFile:
        response = await self.call_view_file_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_file_chunk(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFileVersionChunk]:
        """Low-level method to call ViewFileChunk, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileChunk"
        return await self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFileVersionChunk,extra_headers, timeout_seconds)

    async def view_file_chunk(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFileVersionChunk:
        response = await self.call_view_file_chunk(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_file_chunk_metadata(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFileVersionChunk]:
        """Low-level method to call ViewFileChunkMetadata, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileChunkMetadata"
        return await self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFileVersionChunk,extra_headers, timeout_seconds)

    async def view_file_chunk_metadata(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFileVersionChunk:
        response = await self.call_view_file_chunk_metadata(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_file_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.VaultPermission]:
        """Low-level method to call ViewFilePermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFilePermission"
        return await self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.VaultPermission,extra_headers, timeout_seconds)

    async def view_file_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.VaultPermission:
        response = await self.call_view_file_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_does_file_exist(
        self, req: vault_commons.scailo_pb2.VaultDuplicateCheckReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call DoesFileExist, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DoesFileExist"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)

    async def does_file_exist(
        self, req: vault_commons.scailo_pb2.VaultDuplicateCheckReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = await self.call_does_file_exist(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_file_versions(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFileVersionsList]:
        """Low-level method to call ViewFileVersions, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileVersions"
        return await self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFileVersionsList,extra_headers, timeout_seconds)

    async def view_file_versions(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFileVersionsList:
        response = await self.call_view_file_versions(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_file_access_logs(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.VaultAccessLogsList]:
        """Low-level method to call ViewFileAccessLogs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFileAccessLogs"
        return await self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.VaultAccessLogsList,extra_headers, timeout_seconds)

    async def view_file_access_logs(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.VaultAccessLogsList:
        response = await self.call_view_file_access_logs(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_folder(
        self, req: vault_folders.scailo_pb2.VaultFolderAddRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/AddFolder"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def add_folder(
        self, req: vault_folders.scailo_pb2.VaultFolderAddRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_add_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_move_folder(
        self, req: vault_folders.scailo_pb2.VaultFolderMoveFolderRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call MoveFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/MoveFolder"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def move_folder(
        self, req: vault_folders.scailo_pb2.VaultFolderMoveFolderRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_move_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_rename_folder(
        self, req: vault_folders.scailo_pb2.VaultFolderRenameFolderRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call RenameFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/RenameFolder"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def rename_folder(
        self, req: vault_folders.scailo_pb2.VaultFolderRenameFolderRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_rename_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call DeleteFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DeleteFolder"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def delete_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_delete_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_zip_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call ZipFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ZipFolder"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def zip_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_zip_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_add_folder_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionAddRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call AddFolderPermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/AddFolderPermission"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def add_folder_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionAddRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_add_folder_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_modify_folder_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionModifyRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call ModifyFolderPermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ModifyFolderPermission"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def modify_folder_permission(
        self, req: vault_commons.scailo_pb2.VaultPermissionModifyRequest,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_modify_folder_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_delete_folder_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.IdentifierUUID]:
        """Low-level method to call DeleteFolderPermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DeleteFolderPermission"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.IdentifierUUID,extra_headers, timeout_seconds)

    async def delete_folder_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.IdentifierUUID:
        response = await self.call_delete_folder_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_folder_by_id(
        self, req: base.scailo_pb2.IdentifierZeroable,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_folders.scailo_pb2.VaultFolder]:
        """Low-level method to call ViewFolderByID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFolderByID"
        return await self._connect_client.call_unary(url, req, vault_folders.scailo_pb2.VaultFolder,extra_headers, timeout_seconds)

    async def view_folder_by_id(
        self, req: base.scailo_pb2.IdentifierZeroable,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_folders.scailo_pb2.VaultFolder:
        response = await self.call_view_folder_by_id(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_folder_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_folders.scailo_pb2.VaultFolder]:
        """Low-level method to call ViewFolderByUUID, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFolderByUUID"
        return await self._connect_client.call_unary(url, req, vault_folders.scailo_pb2.VaultFolder,extra_headers, timeout_seconds)

    async def view_folder_by_uuid(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_folders.scailo_pb2.VaultFolder:
        response = await self.call_view_folder_by_uuid(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_folder_download_status(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_folders.scailo_pb2.VaultFolderDownload]:
        """Low-level method to call ViewFolderDownloadStatus, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFolderDownloadStatus"
        return await self._connect_client.call_unary(url, req, vault_folders.scailo_pb2.VaultFolderDownload,extra_headers, timeout_seconds)

    async def view_folder_download_status(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_folders.scailo_pb2.VaultFolderDownload:
        response = await self.call_view_folder_download_status(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_download_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.StandardFile]:
        """Low-level method to call DownloadFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DownloadFolder"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.StandardFile,extra_headers, timeout_seconds)

    async def download_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.StandardFile:
        response = await self.call_download_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_accessible_files_in_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_files.scailo_pb2.VaultFilesList]:
        """Low-level method to call ViewAccessibleFilesInFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewAccessibleFilesInFolder"
        return await self._connect_client.call_unary(url, req, vault_files.scailo_pb2.VaultFilesList,extra_headers, timeout_seconds)

    async def view_accessible_files_in_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_files.scailo_pb2.VaultFilesList:
        response = await self.call_view_accessible_files_in_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_accessible_folders_in_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_folders.scailo_pb2.VaultFoldersList]:
        """Low-level method to call ViewAccessibleFoldersInFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewAccessibleFoldersInFolder"
        return await self._connect_client.call_unary(url, req, vault_folders.scailo_pb2.VaultFoldersList,extra_headers, timeout_seconds)

    async def view_accessible_folders_in_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_folders.scailo_pb2.VaultFoldersList:
        response = await self.call_view_accessible_folders_in_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_accessible_resources_in_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.VaultResourcesList]:
        """Low-level method to call ViewAccessibleResourcesInFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewAccessibleResourcesInFolder"
        return await self._connect_client.call_unary(url, req, vault.scailo_pb2.VaultResourcesList,extra_headers, timeout_seconds)

    async def view_accessible_resources_in_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.VaultResourcesList:
        response = await self.call_view_accessible_resources_in_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_folder_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.VaultPermission]:
        """Low-level method to call ViewFolderPermission, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFolderPermission"
        return await self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.VaultPermission,extra_headers, timeout_seconds)

    async def view_folder_permission(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.VaultPermission:
        response = await self.call_view_folder_permission(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_does_folder_exist(
        self, req: vault_commons.scailo_pb2.VaultDuplicateCheckReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.BooleanResponse]:
        """Low-level method to call DoesFolderExist, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/DoesFolderExist"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.BooleanResponse,extra_headers, timeout_seconds)

    async def does_folder_exist(
        self, req: vault_commons.scailo_pb2.VaultDuplicateCheckReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.BooleanResponse:
        response = await self.call_does_folder_exist(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_folder_access_logs(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.VaultAccessLogsList]:
        """Low-level method to call ViewFolderAccessLogs, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewFolderAccessLogs"
        return await self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.VaultAccessLogsList,extra_headers, timeout_seconds)

    async def view_folder_access_logs(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.VaultAccessLogsList:
        response = await self.call_view_folder_access_logs(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_view_passthrough_roles_for_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[roles.scailo_pb2.RolesList]:
        """Low-level method to call ViewPassthroughRolesForFolder, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/ViewPassthroughRolesForFolder"
        return await self._connect_client.call_unary(url, req, roles.scailo_pb2.RolesList,extra_headers, timeout_seconds)

    async def view_passthrough_roles_for_folder(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> roles.scailo_pb2.RolesList:
        response = await self.call_view_passthrough_roles_for_folder(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_search(
        self, req: vault_commons.scailo_pb2.VaultSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.VaultSearchResponsesList]:
        """Low-level method to call Search, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/Search"
        return await self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.VaultSearchResponsesList,extra_headers, timeout_seconds)

    async def search(
        self, req: vault_commons.scailo_pb2.VaultSearchReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.VaultSearchResponsesList:
        response = await self.call_search(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_setup_gi_x(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.GiXAppRun]:
        """Low-level method to call SetupGiX, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/SetupGiX"
        return await self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.GiXAppRun,extra_headers, timeout_seconds)

    async def setup_gi_x(
        self, req: base.scailo_pb2.IdentifierUUID,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.GiXAppRun:
        response = await self.call_setup_gi_x(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_gi_x_relay_delete(
        self, req: vault.scailo_pb2.GiXRelayReqWithoutBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.GiXRelayResponse]:
        """Low-level method to call GiXRelayDELETE, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXRelayDELETE"
        return await self._connect_client.call_unary(url, req, vault.scailo_pb2.GiXRelayResponse,extra_headers, timeout_seconds)

    async def gi_x_relay_delete(
        self, req: vault.scailo_pb2.GiXRelayReqWithoutBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.GiXRelayResponse:
        response = await self.call_gi_x_relay_delete(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_gi_x_relay_get(
        self, req: vault.scailo_pb2.GiXRelayReqWithoutBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.GiXRelayResponse]:
        """Low-level method to call GiXRelayGET, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXRelayGET"
        return await self._connect_client.call_unary(url, req, vault.scailo_pb2.GiXRelayResponse,extra_headers, timeout_seconds)

    async def gi_x_relay_get(
        self, req: vault.scailo_pb2.GiXRelayReqWithoutBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.GiXRelayResponse:
        response = await self.call_gi_x_relay_get(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_gi_x_relay_head(
        self, req: vault.scailo_pb2.GiXRelayReqWithoutBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.GiXRelayResponse]:
        """Low-level method to call GiXRelayHEAD, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXRelayHEAD"
        return await self._connect_client.call_unary(url, req, vault.scailo_pb2.GiXRelayResponse,extra_headers, timeout_seconds)

    async def gi_x_relay_head(
        self, req: vault.scailo_pb2.GiXRelayReqWithoutBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.GiXRelayResponse:
        response = await self.call_gi_x_relay_head(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_gi_x_relay_patch(
        self, req: vault.scailo_pb2.GiXRelayReqWithBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.GiXRelayResponse]:
        """Low-level method to call GiXRelayPATCH, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXRelayPATCH"
        return await self._connect_client.call_unary(url, req, vault.scailo_pb2.GiXRelayResponse,extra_headers, timeout_seconds)

    async def gi_x_relay_patch(
        self, req: vault.scailo_pb2.GiXRelayReqWithBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.GiXRelayResponse:
        response = await self.call_gi_x_relay_patch(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_gi_x_relay_post(
        self, req: vault.scailo_pb2.GiXRelayReqWithBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.GiXRelayResponse]:
        """Low-level method to call GiXRelayPOST, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXRelayPOST"
        return await self._connect_client.call_unary(url, req, vault.scailo_pb2.GiXRelayResponse,extra_headers, timeout_seconds)

    async def gi_x_relay_post(
        self, req: vault.scailo_pb2.GiXRelayReqWithBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.GiXRelayResponse:
        response = await self.call_gi_x_relay_post(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_gi_x_relay_put(
        self, req: vault.scailo_pb2.GiXRelayReqWithBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault.scailo_pb2.GiXRelayResponse]:
        """Low-level method to call GiXRelayPUT, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXRelayPUT"
        return await self._connect_client.call_unary(url, req, vault.scailo_pb2.GiXRelayResponse,extra_headers, timeout_seconds)

    async def gi_x_relay_put(
        self, req: vault.scailo_pb2.GiXRelayReqWithBody,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault.scailo_pb2.GiXRelayResponse:
        response = await self.call_gi_x_relay_put(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_gi_x_filter(
        self, req: vault_commons.scailo_pb2.GiXAppRunFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[vault_commons.scailo_pb2.GiXAppRunsList]:
        """Low-level method to call GiXFilter, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXFilter"
        return await self._connect_client.call_unary(url, req, vault_commons.scailo_pb2.GiXAppRunsList,extra_headers, timeout_seconds)

    async def gi_x_filter(
        self, req: vault_commons.scailo_pb2.GiXAppRunFilterReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> vault_commons.scailo_pb2.GiXAppRunsList:
        response = await self.call_gi_x_filter(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg

    async def call_gi_x_count(
        self, req: vault_commons.scailo_pb2.GiXAppRunCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> UnaryOutput[base.scailo_pb2.CountResponse]:
        """Low-level method to call GiXCount, granting access to errors and metadata"""
        url = self.base_url + "/Scailo.VaultService/GiXCount"
        return await self._connect_client.call_unary(url, req, base.scailo_pb2.CountResponse,extra_headers, timeout_seconds)

    async def gi_x_count(
        self, req: vault_commons.scailo_pb2.GiXAppRunCountReq,extra_headers: HeaderInput | None=None, timeout_seconds: float | None=None
    ) -> base.scailo_pb2.CountResponse:
        response = await self.call_gi_x_count(req, extra_headers, timeout_seconds)
        err = response.error()
        if err is not None:
            raise err
        msg = response.message()
        if msg is None:
            raise ConnectProtocolError('missing response message')
        return msg


@typing.runtime_checkable
class VaultServiceProtocol(typing.Protocol):
    def initiate_file(self, req: ClientRequest[vault_files.scailo_pb2.VaultFileInitiateFileRequest]) -> ServerResponse[vault_files.scailo_pb2.VaultFileInitiateFileResponse]:
        ...
    def add_file_chunk(self, req: ClientRequest[vault_files.scailo_pb2.VaultFileAddChunkRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def complete_file(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def rename_file(self, req: ClientRequest[vault_files.scailo_pb2.VaultFileRenameFileRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def unzip_file(self, req: ClientRequest[vault_files.scailo_pb2.VaultFileUnzipRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def persist_file(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def move_file(self, req: ClientRequest[vault_files.scailo_pb2.VaultFileMoveFileRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def delete_file(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def add_file_permission(self, req: ClientRequest[vault_commons.scailo_pb2.VaultPermissionAddRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def modify_file_permission(self, req: ClientRequest[vault_commons.scailo_pb2.VaultPermissionModifyRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def delete_file_permission(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def download_file(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def download_file_version(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def view_file_logo(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def view_file_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault_files.scailo_pb2.VaultFile]:
        ...
    def view_file_by_id(self, req: ClientRequest[base.scailo_pb2.Identifier]) -> ServerResponse[vault_files.scailo_pb2.VaultFile]:
        ...
    def view_file_chunk(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault_files.scailo_pb2.VaultFileVersionChunk]:
        ...
    def view_file_chunk_metadata(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault_files.scailo_pb2.VaultFileVersionChunk]:
        ...
    def view_file_permission(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault_commons.scailo_pb2.VaultPermission]:
        ...
    def does_file_exist(self, req: ClientRequest[vault_commons.scailo_pb2.VaultDuplicateCheckReq]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def view_file_versions(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault_files.scailo_pb2.VaultFileVersionsList]:
        ...
    def view_file_access_logs(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault_commons.scailo_pb2.VaultAccessLogsList]:
        ...
    def add_folder(self, req: ClientRequest[vault_folders.scailo_pb2.VaultFolderAddRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def move_folder(self, req: ClientRequest[vault_folders.scailo_pb2.VaultFolderMoveFolderRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def rename_folder(self, req: ClientRequest[vault_folders.scailo_pb2.VaultFolderRenameFolderRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def delete_folder(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def zip_folder(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def add_folder_permission(self, req: ClientRequest[vault_commons.scailo_pb2.VaultPermissionAddRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def modify_folder_permission(self, req: ClientRequest[vault_commons.scailo_pb2.VaultPermissionModifyRequest]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def delete_folder_permission(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.IdentifierUUID]:
        ...
    def view_folder_by_id(self, req: ClientRequest[base.scailo_pb2.IdentifierZeroable]) -> ServerResponse[vault_folders.scailo_pb2.VaultFolder]:
        ...
    def view_folder_by_uuid(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault_folders.scailo_pb2.VaultFolder]:
        ...
    def view_folder_download_status(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault_folders.scailo_pb2.VaultFolderDownload]:
        ...
    def download_folder(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[base.scailo_pb2.StandardFile]:
        ...
    def view_accessible_files_in_folder(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault_files.scailo_pb2.VaultFilesList]:
        ...
    def view_accessible_folders_in_folder(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault_folders.scailo_pb2.VaultFoldersList]:
        ...
    def view_accessible_resources_in_folder(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault.scailo_pb2.VaultResourcesList]:
        ...
    def view_folder_permission(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault_commons.scailo_pb2.VaultPermission]:
        ...
    def does_folder_exist(self, req: ClientRequest[vault_commons.scailo_pb2.VaultDuplicateCheckReq]) -> ServerResponse[base.scailo_pb2.BooleanResponse]:
        ...
    def view_folder_access_logs(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault_commons.scailo_pb2.VaultAccessLogsList]:
        ...
    def view_passthrough_roles_for_folder(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[roles.scailo_pb2.RolesList]:
        ...
    def search(self, req: ClientRequest[vault_commons.scailo_pb2.VaultSearchReq]) -> ServerResponse[vault_commons.scailo_pb2.VaultSearchResponsesList]:
        ...
    def setup_gi_x(self, req: ClientRequest[base.scailo_pb2.IdentifierUUID]) -> ServerResponse[vault_commons.scailo_pb2.GiXAppRun]:
        ...
    def gi_x_relay_delete(self, req: ClientRequest[vault.scailo_pb2.GiXRelayReqWithoutBody]) -> ServerResponse[vault.scailo_pb2.GiXRelayResponse]:
        ...
    def gi_x_relay_get(self, req: ClientRequest[vault.scailo_pb2.GiXRelayReqWithoutBody]) -> ServerResponse[vault.scailo_pb2.GiXRelayResponse]:
        ...
    def gi_x_relay_head(self, req: ClientRequest[vault.scailo_pb2.GiXRelayReqWithoutBody]) -> ServerResponse[vault.scailo_pb2.GiXRelayResponse]:
        ...
    def gi_x_relay_patch(self, req: ClientRequest[vault.scailo_pb2.GiXRelayReqWithBody]) -> ServerResponse[vault.scailo_pb2.GiXRelayResponse]:
        ...
    def gi_x_relay_post(self, req: ClientRequest[vault.scailo_pb2.GiXRelayReqWithBody]) -> ServerResponse[vault.scailo_pb2.GiXRelayResponse]:
        ...
    def gi_x_relay_put(self, req: ClientRequest[vault.scailo_pb2.GiXRelayReqWithBody]) -> ServerResponse[vault.scailo_pb2.GiXRelayResponse]:
        ...
    def gi_x_filter(self, req: ClientRequest[vault_commons.scailo_pb2.GiXAppRunFilterReq]) -> ServerResponse[vault_commons.scailo_pb2.GiXAppRunsList]:
        ...
    def gi_x_count(self, req: ClientRequest[vault_commons.scailo_pb2.GiXAppRunCountReq]) -> ServerResponse[base.scailo_pb2.CountResponse]:
        ...

VAULT_SERVICE_PATH_PREFIX = "/Scailo.VaultService"

def wsgi_vault_service(implementation: VaultServiceProtocol) -> WSGIApplication:
    app = ConnectWSGI()
    app.register_unary_rpc("/Scailo.VaultService/InitiateFile", implementation.initiate_file, vault_files.scailo_pb2.VaultFileInitiateFileRequest)
    app.register_unary_rpc("/Scailo.VaultService/AddFileChunk", implementation.add_file_chunk, vault_files.scailo_pb2.VaultFileAddChunkRequest)
    app.register_unary_rpc("/Scailo.VaultService/CompleteFile", implementation.complete_file, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/RenameFile", implementation.rename_file, vault_files.scailo_pb2.VaultFileRenameFileRequest)
    app.register_unary_rpc("/Scailo.VaultService/UnzipFile", implementation.unzip_file, vault_files.scailo_pb2.VaultFileUnzipRequest)
    app.register_unary_rpc("/Scailo.VaultService/PersistFile", implementation.persist_file, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/MoveFile", implementation.move_file, vault_files.scailo_pb2.VaultFileMoveFileRequest)
    app.register_unary_rpc("/Scailo.VaultService/DeleteFile", implementation.delete_file, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/AddFilePermission", implementation.add_file_permission, vault_commons.scailo_pb2.VaultPermissionAddRequest)
    app.register_unary_rpc("/Scailo.VaultService/ModifyFilePermission", implementation.modify_file_permission, vault_commons.scailo_pb2.VaultPermissionModifyRequest)
    app.register_unary_rpc("/Scailo.VaultService/DeleteFilePermission", implementation.delete_file_permission, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/DownloadFile", implementation.download_file, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/DownloadFileVersion", implementation.download_file_version, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ViewFileLogo", implementation.view_file_logo, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ViewFileByUUID", implementation.view_file_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ViewFileByID", implementation.view_file_by_id, base.scailo_pb2.Identifier)
    app.register_unary_rpc("/Scailo.VaultService/ViewFileChunk", implementation.view_file_chunk, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ViewFileChunkMetadata", implementation.view_file_chunk_metadata, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ViewFilePermission", implementation.view_file_permission, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/DoesFileExist", implementation.does_file_exist, vault_commons.scailo_pb2.VaultDuplicateCheckReq)
    app.register_unary_rpc("/Scailo.VaultService/ViewFileVersions", implementation.view_file_versions, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ViewFileAccessLogs", implementation.view_file_access_logs, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/AddFolder", implementation.add_folder, vault_folders.scailo_pb2.VaultFolderAddRequest)
    app.register_unary_rpc("/Scailo.VaultService/MoveFolder", implementation.move_folder, vault_folders.scailo_pb2.VaultFolderMoveFolderRequest)
    app.register_unary_rpc("/Scailo.VaultService/RenameFolder", implementation.rename_folder, vault_folders.scailo_pb2.VaultFolderRenameFolderRequest)
    app.register_unary_rpc("/Scailo.VaultService/DeleteFolder", implementation.delete_folder, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ZipFolder", implementation.zip_folder, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/AddFolderPermission", implementation.add_folder_permission, vault_commons.scailo_pb2.VaultPermissionAddRequest)
    app.register_unary_rpc("/Scailo.VaultService/ModifyFolderPermission", implementation.modify_folder_permission, vault_commons.scailo_pb2.VaultPermissionModifyRequest)
    app.register_unary_rpc("/Scailo.VaultService/DeleteFolderPermission", implementation.delete_folder_permission, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ViewFolderByID", implementation.view_folder_by_id, base.scailo_pb2.IdentifierZeroable)
    app.register_unary_rpc("/Scailo.VaultService/ViewFolderByUUID", implementation.view_folder_by_uuid, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ViewFolderDownloadStatus", implementation.view_folder_download_status, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/DownloadFolder", implementation.download_folder, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ViewAccessibleFilesInFolder", implementation.view_accessible_files_in_folder, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ViewAccessibleFoldersInFolder", implementation.view_accessible_folders_in_folder, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ViewAccessibleResourcesInFolder", implementation.view_accessible_resources_in_folder, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ViewFolderPermission", implementation.view_folder_permission, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/DoesFolderExist", implementation.does_folder_exist, vault_commons.scailo_pb2.VaultDuplicateCheckReq)
    app.register_unary_rpc("/Scailo.VaultService/ViewFolderAccessLogs", implementation.view_folder_access_logs, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/ViewPassthroughRolesForFolder", implementation.view_passthrough_roles_for_folder, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/Search", implementation.search, vault_commons.scailo_pb2.VaultSearchReq)
    app.register_unary_rpc("/Scailo.VaultService/SetupGiX", implementation.setup_gi_x, base.scailo_pb2.IdentifierUUID)
    app.register_unary_rpc("/Scailo.VaultService/GiXRelayDELETE", implementation.gi_x_relay_delete, vault.scailo_pb2.GiXRelayReqWithoutBody)
    app.register_unary_rpc("/Scailo.VaultService/GiXRelayGET", implementation.gi_x_relay_get, vault.scailo_pb2.GiXRelayReqWithoutBody)
    app.register_unary_rpc("/Scailo.VaultService/GiXRelayHEAD", implementation.gi_x_relay_head, vault.scailo_pb2.GiXRelayReqWithoutBody)
    app.register_unary_rpc("/Scailo.VaultService/GiXRelayPATCH", implementation.gi_x_relay_patch, vault.scailo_pb2.GiXRelayReqWithBody)
    app.register_unary_rpc("/Scailo.VaultService/GiXRelayPOST", implementation.gi_x_relay_post, vault.scailo_pb2.GiXRelayReqWithBody)
    app.register_unary_rpc("/Scailo.VaultService/GiXRelayPUT", implementation.gi_x_relay_put, vault.scailo_pb2.GiXRelayReqWithBody)
    app.register_unary_rpc("/Scailo.VaultService/GiXFilter", implementation.gi_x_filter, vault_commons.scailo_pb2.GiXAppRunFilterReq)
    app.register_unary_rpc("/Scailo.VaultService/GiXCount", implementation.gi_x_count, vault_commons.scailo_pb2.GiXAppRunCountReq)
    return app
