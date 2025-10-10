"""
同步二进制大对象服务
"""
import hashlib
from pathlib import Path
from typing import Optional, Union, BinaryIO, Iterator, List

from .base_file_service import BaseFileService
from ...enums import UploadMode
from ...errors import ValidationError
from ...rpc import SyncGrpcClient
from ...schemas import FileUploadResponse, UploadUrlResponse, BatchDownloadUrlResponse, DownloadUrlInfo, GcsUrlInfo, GetGcsUrlResponse, BatchGcsUrlResponse, CompressionStatusResponse, GetVariantsResponse, RecompressionResponse, VariantDownloadUrlResponse, CompressedVariant, BatchFileStatusResponse, FileStatusInfo, FileStatusDetails, FileUploadStatus, FileCompressionStatus, FileSyncStatus
from ...utils import HttpUploader, HttpDownloader, retry_with_backoff, get_file_mime_type


class SyncBlobService(BaseFileService):
    """同步文件（二进制大对象）服务"""

    def __init__(self, client: SyncGrpcClient):
        """
        初始化文件（二进制大对象）服务

        Args:
            client: 同步gRPC客户端
        """
        self.client = client
        self.http_uploader = HttpUploader()
        self.http_downloader = HttpDownloader()

    @retry_with_backoff(max_retries=3)
    def _upload_file(
            self,
            file_name: str,
            content: Union[bytes, BinaryIO, Path],
            folder_id: Optional[str] = None,
            file_type: str = "dat",
            mime_type: Optional[str] = None,
            is_temporary: Optional[bool] = False,
            expire_seconds: Optional[int] = None,
            keep_original_filename: Optional[bool] = False,
            request_id: Optional[str] = None,
            **metadata
    ) -> FileUploadResponse:
        """
        直接上传文件

        Args:
            file_name: 文件名
            content: 文件内容（字节、文件对象或路径）
            folder_id: 文件夹ID
            file_type: 文件类型
            mime_type: MIME类型
            is_temporary: 是否为临时文件
            expire_seconds: 过期秒数
            keep_original_filename: 是否保留原始文件名（默认False）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）

        Returns:
            文件信息
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        # 处理不同类型的内容
        if isinstance(content, Path):
            if not content.exists():
                raise ValidationError(f"文件不存在: {content}")
            with open(content, "rb") as f:
                file_bytes = f.read()
            if not mime_type:
                mime_type = get_file_mime_type(content)
        elif isinstance(content, bytes):
            file_bytes = content
        elif hasattr(content, 'read'):
            file_bytes = content.read()
        else:
            raise ValidationError("不支持的内容类型")

        # 构建请求
        request = file_service_pb2.UploadFileRequest(
            file_name=file_name,
            content=file_bytes,
            file_type=file_type,
            mime_type=mime_type or "application/octet-stream",
            is_temporary=is_temporary,
            expire_seconds=expire_seconds,
            keep_original_filename=keep_original_filename,
        )

        if folder_id:
            request.folder_id = folder_id

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        # 发送请求
        response = stub.UploadFile(request, metadata=grpc_metadata)

        # 转换响应
        return FileUploadResponse(
            file=self._convert_file_info(response.file),
            upload_file=self._convert_upload_file_info(response.upload_file),
        )

    def _upload_stream(
            self,
            file_name: str,
            content: Union[bytes, BinaryIO, Path],
            file_size: int,
            folder_id: Optional[str],
            file_type: str,
            mime_type: str,
            file_hash: str,
            is_temporary: Optional[bool] = False,
            expire_seconds: Optional[int] = None,
            keep_original_filename: Optional[bool] = False,
            request_id: Optional[str] = None,
            **metadata
    ) -> FileUploadResponse:
        """客户端直传实现（GCS 直传）"""
        
        # 获取上传URL，以及对应的文件和上传文件信息
        upload_url_resp = self.generate_upload_url(
            file_name=file_name,
            file_size=file_size,
            folder_id=folder_id,
            file_type=file_type,
            mime_type=mime_type,
            file_hash=file_hash,
            is_temporary=is_temporary,
            expire_seconds=expire_seconds if is_temporary and expire_seconds else None,
            keep_original_filename=keep_original_filename,
            request_id=request_id,
            **metadata
        )

        # 如果URL为空，说明文件已存在（哈希重复），直接返回
        if not upload_url_resp.upload_url:
            return FileUploadResponse(
                file=upload_url_resp.file,
                upload_file=upload_url_resp.upload_file
            )

        # 构建HTTP头，包含Content-Type和固定的Cache-Control
        headers = {
            "Content-Type": mime_type,
            "Cache-Control": "public, max-age=86400"  # 24小时公共缓存
        }

        # 上传文件到对象存储
        self.http_uploader.upload(
            url=upload_url_resp.upload_url,
            content=content,
            headers=headers,
            total_size=file_size,
        )

        # 确认上传完成
        self.confirm_upload_completed(
            file_id=upload_url_resp.file.id,
            request_id=request_id,
            **metadata
        )

        # 返回文件信息
        return FileUploadResponse(
            file=upload_url_resp.file,
            upload_file=upload_url_resp.upload_file
        )

    def _upload_resumable(
            self,
            file_name: str,
            content: Union[bytes, BinaryIO, Path],
            file_size: int,
            folder_id: Optional[str],
            file_type: str,
            mime_type: str,
            file_hash: str,
            is_temporary: Optional[bool] = False,
            expire_seconds: Optional[int] = None,
            keep_original_filename: Optional[bool] = False,
            request_id: Optional[str] = None,
            **metadata
    ) -> FileUploadResponse:
        """断点续传实现（GCS 直传）"""
        
        # 获取断点续传URL，以及对应的文件和上传文件信息
        upload_url_resp = self.generate_resumable_upload_url(
            file_name=file_name,
            file_size=file_size,
            folder_id=folder_id,
            file_type=file_type,
            mime_type=mime_type,
            file_hash=file_hash,
            is_temporary=is_temporary,
            expire_seconds=expire_seconds if is_temporary and expire_seconds else None,
            keep_original_filename=keep_original_filename,
            request_id=request_id,
            **metadata
        )

        # 如果URL为空，说明文件已存在（哈希重复），直接返回
        if not upload_url_resp.upload_url:
            return FileUploadResponse(
                file=upload_url_resp.file,
                upload_file=upload_url_resp.upload_file
            )

        # 构建HTTP头，包含Content-Type和固定的Cache-Control
        headers = {
            "Content-Type": mime_type,
            "Cache-Control": "public, max-age=86400"  # 24小时公共缓存
        }

        # 开启断点续传
        upload_url = self.http_uploader.start_resumable_session(
            url=upload_url_resp.upload_url,
            total_file_size=file_size,
            mime_type=mime_type,
        )

        # 上传文件到对象存储
        self.http_uploader.upload(
            url=upload_url,
            content=content,
            headers=headers,
            total_size=file_size,
            is_resume=True
        )

        # 确认上传完成
        self.confirm_upload_completed(
            file_id=upload_url_resp.file.id,
            request_id=request_id,
            **metadata
        )

        # 返回文件信息
        return FileUploadResponse(
            file=upload_url_resp.file,
            upload_file=upload_url_resp.upload_file
        )

    def confirm_upload_completed(self, file_id: str, request_id: Optional[str] = None,
                                 **metadata) -> None:
        """
        确认上传完成

        Args:
            file_id: 文件ID
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        request = file_service_pb2.UploadCompletedRequest(file_id=file_id)

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        stub.ConfirmUploadCompleted(request, metadata=grpc_metadata)

    def generate_resumable_upload_url(
            self,
            file_name: str,
            file_size: int,
            folder_id: Optional[str] = None,
            file_type: str = "dat",
            mime_type: str = None,
            file_hash: str = None,
            is_temporary: Optional[bool] = False,
            expire_seconds: Optional[int] = None,
            keep_original_filename: Optional[bool] = False,
            request_id: Optional[str] = None,
            **metadata
    ) -> UploadUrlResponse:
        """
        生成断点续传URL

        Args:
            file_name: 文件名
            file_size: 文件大小
            folder_id: 文件夹ID
            file_type: 文件类型
            mime_type: MIME类型
            file_hash: 文件哈希
            is_temporary: 是否为临时文件
            expire_seconds: 过期秒数
            keep_original_filename: 是否保留原始文件名（默认False）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）

        Returns:
            上传URL响应
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        request = file_service_pb2.UploadUrlRequest(
            file_name=file_name,
            file_size=file_size,
            file_type=file_type,
            mime_type=mime_type or "application/octet-stream",
            file_hash=file_hash,
            is_temporary=is_temporary,
            expire_seconds=expire_seconds if is_temporary and expire_seconds else None,
            keep_original_filename=keep_original_filename,
        )

        if folder_id:
            request.folder_id = folder_id

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        response = stub.GenerateResumableUploadUrl(request, metadata=grpc_metadata)

        return UploadUrlResponse(
            file=self._convert_file_info(response.file),
            upload_file=self._convert_upload_file_info(response.upload_file),
            upload_url=response.url
        )

    def generate_upload_url(
            self,
            file_name: str,
            file_size: int,
            folder_id: Optional[str] = None,
            file_type: str = "dat",
            mime_type: str = None,
            file_hash: str = None,
            is_temporary: Optional[bool] = False,
            expire_seconds: Optional[int] = None,
            keep_original_filename: Optional[bool] = False,
            request_id: Optional[str] = None,
            **metadata
    ) -> UploadUrlResponse:
        """
        生成上传URL（用于客户端直传）

        Args:
            file_name: 文件名
            file_size: 文件大小
            folder_id: 文件夹ID
            file_type: 文件类型
            mime_type: MIME类型
            file_hash: 文件哈希
            is_temporary: 是否为临时文件
            expire_seconds: 过期秒数
            keep_original_filename: 是否保留原始文件名（默认False）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）

        Returns:
            上传URL响应
            注意：如果文件哈希已存在（重复上传），upload_url 会为空，
            此时应直接使用返回的 file 和 upload_file 信息，无需再次上传
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        request = file_service_pb2.UploadUrlRequest(
            file_name=file_name,
            file_size=file_size,
            file_type=file_type,
            mime_type=mime_type or "application/octet-stream",
            file_hash=file_hash,
            is_temporary=is_temporary,
            expire_seconds=expire_seconds if is_temporary and expire_seconds else None,
            keep_original_filename=keep_original_filename,
        )

        if folder_id:
            request.folder_id = folder_id

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        response = stub.GenerateUploadUrl(request, metadata=grpc_metadata)

        return UploadUrlResponse(
            file=self._convert_file_info(response.file),
            upload_file=self._convert_upload_file_info(response.upload_file),
            upload_url=response.url
        )

    def upload(
            self,
            file: Optional[Union[str, Path, BinaryIO, bytes]] = None,
            *,
            folder_id: Optional[str] = None,
            mode: Optional[UploadMode] = UploadMode.NORMAL,
            is_temporary: Optional[bool] = False,
            expire_seconds: Optional[int] = None,
            keep_original_filename: Optional[bool] = False,
            url: Optional[str] = None,
            file_name: Optional[str] = None,
            mime_type: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> FileUploadResponse:
        """
        统一的文件上传接口

        Args:
            file: 文件路径、Path对象、文件对象或字节数据（当使用url参数时可省略）
            folder_id: 目标文件夹ID（可选）
            mode: 上传模式（NORMAL/DIRECT/RESUMABLE/STREAM）
            is_temporary: 是否为临时文件
            expire_seconds: 过期秒数
            keep_original_filename: 是否保留原始文件名（默认False）
            url: 要下载并上传的URL（可选）
            file_name: 当使用url参数时指定的文件名（可选）
            mime_type: MIME类型（可选，用于推断文件扩展名，特别适用于AI生成的字节数据）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据

        Returns:
            文件信息

        Note:
            必须提供 file 或 url 参数之一
            
            当传入bytes或BinaryIO且未提供file_name时，建议提供mime_type以确保正确的文件扩展名推断
            
            Cache-Control 头在 GCS 直传模式（STREAM/RESUMABLE）下自动设置为 "public, max-age=86400"
        """
        # 参数验证：必须提供 file 或 url 之一
        if file is None and not url:
            raise ValidationError("必须提供 file 或 url 参数之一")

        # 如果提供了URL，先下载文件
        if url:
            # 下载文件到内存
            downloaded_content = self.http_downloader.download(url)

            # 如果没有指定文件名，从URL中提取
            if not file_name:
                from urllib.parse import urlparse
                from pathlib import Path as PathLib
                parsed_url = urlparse(url)
                url_path = PathLib(parsed_url.path)
                file_name = url_path.name if url_path.name else f"download_{hashlib.md5(url.encode()).hexdigest()[:8]}"

            # 使用下载的内容作为file参数
            file = downloaded_content

            # MIME类型优先级：用户指定 > 内容检测 > URL文件名推断
            if mime_type:
                # 用户明确提供的MIME类型优先级最高，无需进行内容检测
                final_mime_type = mime_type
            else:
                # 用户未提供MIME类型，进行内容检测和文件名推断
                content_detected_mime = self._detect_mime_from_content(downloaded_content)
                url_filename_mime = get_file_mime_type(Path(file_name))
                
                if content_detected_mime != "application/octet-stream":
                    # 内容检测到了具体的MIME类型，使用内容检测的
                    final_mime_type = content_detected_mime
                else:
                    # 内容检测失败，使用从URL文件名推断的MIME类型
                    final_mime_type = url_filename_mime
            
            # 提取文件信息，传入最终确定的MIME类型
            _, content, file_size, extract_mime_type, extract_file_type, file_hash = self._extract_file_info(file, final_mime_type)

            # file_name已经在上面设置了（要么是用户指定的，要么是从URL提取的）
            extracted_file_name = file_name
            
            # 使用最终确定的MIME类型
            mime_type = final_mime_type

            # 基于最终MIME类型计算文件扩展名
            file_type = extract_file_type
        else:
            # 解析文件参数，提取文件信息
            # 如果用户指定了文件名，先从文件名推断MIME类型，然后传给_extract_file_info
            if file_name:
                # 用户指定了文件名，优先使用用户提供的MIME类型，否则从文件名推断
                if mime_type:
                    file_name_mime_type = mime_type
                else:
                    file_name_mime_type = get_file_mime_type(Path(file_name))
                extracted_file_name, content, file_size, extract_mime_type, extract_file_type, file_hash = self._extract_file_info(
                    file, file_name_mime_type)
                # 使用用户指定的文件名
                extracted_file_name = file_name
                mime_type = file_name_mime_type
                file_type = Path(extracted_file_name).suffix.lstrip('.').lower() if Path(
                    extracted_file_name).suffix else 'dat'
            else:
                # 没有指定文件名，传入用户提供的MIME类型（如果有）
                extracted_file_name, content, file_size, extract_mime_type, extract_file_type, file_hash = self._extract_file_info(
                    file, mime_type)
                # 如果用户指定了MIME类型，使用用户指定的，否则使用检测的
                if not mime_type:
                    mime_type = extract_mime_type
                file_type = extract_file_type

        # 根据文件大小自动选择上传模式
        if mode == UploadMode.NORMAL:
            ten_mb = 1024 * 1024 * 10
            hundred_mb = 1024 * 1024 * 100
            if file_size >= ten_mb and file_size < hundred_mb:  # 10MB
                mode = UploadMode.STREAM  # 大文件自动使用流式上传模式
            elif file_size > hundred_mb:
                mode = UploadMode.RESUMABLE  # 特大文件自动使用断点续传模式

        # 根据上传模式执行不同的上传逻辑
        if mode == UploadMode.NORMAL:
            # 普通上传（通过gRPC）- 不需要 Cache-Control
            return self._upload_file(
                file_name=extracted_file_name,
                content=content,
                folder_id=folder_id,
                file_type=file_type,
                mime_type=mime_type,
                is_temporary=is_temporary,
                expire_seconds=expire_seconds if is_temporary and expire_seconds else None,
                keep_original_filename=keep_original_filename,
                request_id=request_id,
                **metadata
            )

        elif mode == UploadMode.STREAM:
            # 流式上传 - 需要 Cache-Control
            return self._upload_stream(
                file_name=extracted_file_name,
                content=content,
                file_size=file_size,
                folder_id=folder_id,
                file_type=file_type,
                mime_type=mime_type,
                file_hash=file_hash,
                is_temporary=is_temporary,
                expire_seconds=expire_seconds if is_temporary and expire_seconds else None,
                keep_original_filename=keep_original_filename,
                request_id=request_id,
                **metadata
            )

        elif mode == UploadMode.RESUMABLE:
            # 断点续传 - 需要 Cache-Control
            return self._upload_resumable(
                file_name=extracted_file_name,
                content=content,
                file_size=file_size,
                folder_id=folder_id,
                file_type=file_type,
                mime_type=mime_type,
                file_hash=file_hash,
                is_temporary=is_temporary,
                expire_seconds=expire_seconds if is_temporary and expire_seconds else None,
                keep_original_filename=keep_original_filename,
                request_id=request_id,
                **metadata
            )

        else:
            raise ValidationError(f"不支持的上传模式: {mode}")

    def generate_download_url(
            self,
            file_id: str,
            *,
            is_cdn: Optional[bool] = True,
            expire_seconds: Optional[int] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> str:
        """
        生成下载URL

        Args:
            file_id: 文件ID
            is_cdn: 是否返回CDN的URL
            expire_seconds: 过期时间（秒）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）

        Returns:
            下载URL
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        request = file_service_pb2.DownloadUrlRequest(file_id=file_id, is_cdn=is_cdn,
                                                      expire_seconds=expire_seconds if expire_seconds else None)

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        download_url_resp = stub.GenerateDownloadUrl(request, metadata=grpc_metadata)

        return download_url_resp.url

    def download(
            self,
            file_id: str,
            save_path: Optional[Union[str, Path]] = None,
            chunk_size: Optional[int] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> Union[bytes, Path, Iterator[bytes]]:
        """
        统一的文件下载接口

        Args:
            file_id: 文件ID
            save_path: 保存路径（如果为None，返回字节数据）
            chunk_size: 分片大小
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据

        Returns:
            - NORMAL模式：下载的内容（字节）或保存的文件路径
            - STREAM模式：返回迭代器，逐块返回数据
        """

        # 获取下载URL
        download_url = self.generate_download_url(file_id, request_id=request_id, **metadata)

        return self.http_downloader.download(
            url=download_url,
            save_path=save_path,
            chunk_size=chunk_size,
        )

    def download_to_bytes(
            self,
            file_id: str,
            *,
            request_id: Optional[str] = None,
            **metadata
    ) -> bytes:
        """
        下载文件并返回字节数据

        Args:
            file_id: 文件ID
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据

        Returns:
            文件的字节数据
        """
        # 获取下载URL
        download_url = self.generate_download_url(file_id, request_id=request_id, **metadata)

        # 下载到内存并返回字节数据
        return self.http_downloader.download(url=download_url, save_path=None)

    def batch_generate_download_url(
            self,
            file_ids: List[str],
            *,
            is_cdn: Optional[bool] = True,
            expire_seconds: Optional[int] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> BatchDownloadUrlResponse:
        """
        批量生成下载URL

        Args:
            file_ids: 文件ID列表
            is_cdn: 是否返回CDN的URL
            expire_seconds: 过期时间（秒）
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）

        Returns:
            批量下载URL响应
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        request = file_service_pb2.BatchDownloadUrlRequest(
            file_ids=file_ids,
            is_cdn=is_cdn,
            expire_seconds=expire_seconds if expire_seconds else None
        )

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        response = stub.BatchGenerateDownloadUrl(request, metadata=grpc_metadata)

        # 转换响应
        download_urls = []
        for url_info in response.download_urls:
            download_urls.append(DownloadUrlInfo(
                file_id=url_info.file_id,
                url=url_info.url,
                mime_type=url_info.mime_type,
                error=url_info.error if url_info.HasField('error') else None
            ))

        return BatchDownloadUrlResponse(download_urls=download_urls)

    def get_gcs_url(
            self,
            file_id: str,
            *,
            request_id: Optional[str] = None,
            **metadata
    ) -> GetGcsUrlResponse:
        """
        获取文件的GCS URL

        Args:
            file_id: 文件ID
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）

        Returns:
            GCS URL响应，包含URL和MIME类型
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        request = file_service_pb2.GetGcsUrlRequest(file_id=file_id)

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        response = stub.GetGcsUrl(request, metadata=grpc_metadata)

        return GetGcsUrlResponse(
            gcs_url=response.gcs_url,
            mime_type=response.mime_type
        )

    def batch_get_gcs_url(
            self,
            file_ids: List[str],
            *,
            request_id: Optional[str] = None,
            **metadata
    ) -> BatchGcsUrlResponse:
        """
        批量获取文件的GCS URL

        Args:
            file_ids: 文件ID列表
            request_id: 请求ID（可选，如果不提供则自动生成）
            **metadata: 额外的元数据（如 x-org-id, x-user-id 等）

        Returns:
            批量GCS URL响应
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc

        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)

        request = file_service_pb2.BatchGetGcsUrlRequest(file_ids=file_ids)

        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)

        response = stub.BatchGetGcsUrl(request, metadata=grpc_metadata)

        # 转换响应
        gcs_urls = []
        for url_info in response.gcs_urls:
            gcs_urls.append(GcsUrlInfo(
                file_id=url_info.file_id,
                gcs_url=url_info.gcs_url,
                mime_type=url_info.mime_type,
                error=url_info.error if url_info.HasField('error') else None
            ))

        return BatchGcsUrlResponse(gcs_urls=gcs_urls)

    def get_compression_status(
            self,
            file_id: str,
            *,
            request_id: Optional[str] = None,
            **metadata
    ) -> CompressionStatusResponse:
        """
        获取文件压缩状态
        
        Args:
            file_id: 文件ID
            request_id: 请求ID，用于追踪
            **metadata: 额外的gRPC元数据
            
        Returns:
            CompressionStatusResponse: 压缩状态响应
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc
        
        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)
        
        request = file_service_pb2.CompressionStatusRequest(file_id=file_id)
        
        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)
        
        response = stub.GetCompressionStatus(request, metadata=grpc_metadata)
        
        # 转换压缩变体
        variants = []
        for variant in response.variants:
            variants.append(CompressedVariant(
                variant_name=variant.variant_name,
                variant_type=variant.variant_type,
                media_type=variant.media_type,
                width=variant.width,
                height=variant.height,
                file_size=variant.file_size,
                format=variant.format,
                quality=variant.quality if variant.quality else None,
                duration=variant.duration if variant.duration else None,
                bitrate=variant.bitrate if variant.bitrate else None,
                fps=variant.fps if variant.fps else None,
                compression_ratio=variant.compression_ratio,
                stored_path=variant.stored_path
            ))
        
        return CompressionStatusResponse(
            status=response.status,
            error_message=response.error_message if response.error_message else None,
            variants=variants
        )

    def get_compressed_variants(
            self,
            file_id: str,
            *,
            variant_type: Optional[str] = None,
            request_id: Optional[str] = None,
            **metadata
    ) -> GetVariantsResponse:
        """
        获取文件的压缩变体
        
        Args:
            file_id: 文件ID
            variant_type: 变体类型(image, video, thumbnail)
            request_id: 请求ID，用于追踪
            **metadata: 额外的gRPC元数据
            
        Returns:
            GetVariantsResponse: 压缩变体响应
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc
        
        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)
        
        request = file_service_pb2.GetVariantsRequest(file_id=file_id)
        if variant_type:
            request.variant_type = variant_type
        
        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)
        
        response = stub.GetCompressedVariants(request, metadata=grpc_metadata)
        
        # 转换压缩变体
        variants = []
        for variant in response.variants:
            variants.append(CompressedVariant(
                variant_name=variant.variant_name,
                variant_type=variant.variant_type,
                media_type=variant.media_type,
                width=variant.width,
                height=variant.height,
                file_size=variant.file_size,
                format=variant.format,
                quality=variant.quality if variant.quality else None,
                duration=variant.duration if variant.duration else None,
                bitrate=variant.bitrate if variant.bitrate else None,
                fps=variant.fps if variant.fps else None,
                compression_ratio=variant.compression_ratio,
                stored_path=variant.stored_path
            ))
        
        return GetVariantsResponse(variants=variants)

    def trigger_recompression(
            self,
            file_id: str,
            *,
            force_reprocess: bool = False,
            request_id: Optional[str] = None,
            **metadata
    ) -> RecompressionResponse:
        """
        触发文件重新压缩
        
        Args:
            file_id: 文件ID
            force_reprocess: 是否强制重新处理
            request_id: 请求ID，用于追踪
            **metadata: 额外的gRPC元数据
            
        Returns:
            RecompressionResponse: 重新压缩响应
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc
        
        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)
        
        request = file_service_pb2.RecompressionRequest(
            file_id=file_id,
            force_reprocess=force_reprocess
        )
        
        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)
        
        response = stub.TriggerRecompression(request, metadata=grpc_metadata)
        
        return RecompressionResponse(
            task_id=response.task_id,
            status=response.status
        )

    def generate_variant_download_url(
            self,
            file_id: str,
            variant_name: str,
            *,
            expire_seconds: int = 3600,
            is_cdn: bool = False,
            request_id: Optional[str] = None,
            **metadata
    ) -> VariantDownloadUrlResponse:
        """
        生成变体下载URL
        
        Args:
            file_id: 文件ID
            variant_name: 变体名称(large/medium/small/thumbnail)
            expire_seconds: 过期时间（秒）
            is_cdn: 是否使用CDN
            request_id: 请求ID，用于追踪
            **metadata: 额外的gRPC元数据
            
        Returns:
            VariantDownloadUrlResponse: 变体下载URL响应
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc
        
        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)
        
        request = file_service_pb2.VariantDownloadUrlRequest(
            file_id=file_id,
            variant_name=variant_name,
            expire_seconds=expire_seconds,
            is_cdn=is_cdn
        )
        
        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)
        
        response = stub.GenerateVariantDownloadUrl(request, metadata=grpc_metadata)
        
        # 转换变体信息
        variant_info = None
        if response.variant_info:
            variant_info = CompressedVariant(
                variant_name=response.variant_info.variant_name,
                variant_type=response.variant_info.variant_type,
                media_type=response.variant_info.media_type,
                width=response.variant_info.width,
                height=response.variant_info.height,
                file_size=response.variant_info.file_size,
                format=response.variant_info.format,
                quality=response.variant_info.quality if response.variant_info.quality else None,
                duration=response.variant_info.duration if response.variant_info.duration else None,
                bitrate=response.variant_info.bitrate if response.variant_info.bitrate else None,
                fps=response.variant_info.fps if response.variant_info.fps else None,
                compression_ratio=response.variant_info.compression_ratio,
                stored_path=response.variant_info.stored_path
            )
        
        return VariantDownloadUrlResponse(
            url=response.url,
            error=response.error if response.error else None,
            variant_info=variant_info
        )

    def batch_get_file_status(
        self,
        file_ids: List[str],
        *,
        include_details: Optional[bool] = False,
        request_id: Optional[str] = None,
        **metadata
    ) -> BatchFileStatusResponse:
        """
        批量获取文件状态
        
        Args:
            file_ids: 文件ID列表（最多100个）
            include_details: 是否包含详细状态信息（默认False）
            request_id: 请求ID，用于追踪
            **metadata: 额外的gRPC元数据
            
        Returns:
            BatchFileStatusResponse: 批量文件状态响应
        """
        from ...rpc.gen import file_service_pb2, file_service_pb2_grpc
        
        stub = self.client.get_stub(file_service_pb2_grpc.FileServiceStub)
        
        request = file_service_pb2.BatchFileStatusRequest(
            file_ids=file_ids,
            include_details=include_details if include_details is not None else False
        )
        
        # 构建元数据
        grpc_metadata = self.client.build_metadata(request_id=request_id, **metadata)
        
        response = stub.BatchGetFileStatus(request, metadata=grpc_metadata)
        
        # 转换文件状态信息
        statuses = []
        for status_info in response.statuses:
            # 转换状态详情（如果存在）
            details = None
            if status_info.HasField('details'):
                details = FileStatusDetails(
                    file_size=status_info.details.file_size if status_info.details.HasField('file_size') else None,
                    storage_type=status_info.details.storage_type if status_info.details.HasField('storage_type') else None,
                    storage_region=status_info.details.storage_region if status_info.details.HasField('storage_region') else None,
                    compression_task_id=status_info.details.compression_task_id if status_info.details.HasField('compression_task_id') else None,
                    compression_variants_count=status_info.details.compression_variants_count if status_info.details.HasField('compression_variants_count') else None,
                    compression_progress=status_info.details.compression_progress if status_info.details.HasField('compression_progress') else None,
                    sync_regions_total=status_info.details.sync_regions_total if status_info.details.HasField('sync_regions_total') else None,
                    sync_regions_completed=status_info.details.sync_regions_completed if status_info.details.HasField('sync_regions_completed') else None,
                    sync_pending_regions=list(status_info.details.sync_pending_regions)
                )
            
            # 转换枚举值
            upload_status = self._convert_upload_status(status_info.upload_status)
            compression_status = self._convert_compression_status(status_info.compression_status)
            sync_status = self._convert_sync_status(status_info.sync_status)
            
            statuses.append(FileStatusInfo(
                file_id=status_info.file_id,
                upload_status=upload_status,
                compression_status=compression_status,
                sync_status=sync_status,
                details=details,
                error_message=status_info.error_message if status_info.HasField('error_message') else None
            ))
        
        return BatchFileStatusResponse(
            statuses=statuses,
            timestamp=response.timestamp,
            cache_hit_count=response.cache_hit_count
        )

    def _convert_upload_status(self, proto_status: int) -> FileUploadStatus:
        """转换上传状态枚举"""
        status_map = {
            0: FileUploadStatus.UPLOAD_UNKNOWN,
            1: FileUploadStatus.UPLOAD_PENDING,
            2: FileUploadStatus.UPLOAD_PROCESSING,
            3: FileUploadStatus.UPLOAD_COMPLETED,
            4: FileUploadStatus.UPLOAD_FAILED,
            5: FileUploadStatus.UPLOAD_FILE_NOT_FOUND,
        }
        return status_map.get(proto_status, FileUploadStatus.UPLOAD_UNKNOWN)

    def _convert_compression_status(self, proto_status: int) -> FileCompressionStatus:
        """转换压缩状态枚举"""
        status_map = {
            0: FileCompressionStatus.COMPRESSION_UNKNOWN,
            1: FileCompressionStatus.COMPRESSION_NOT_APPLICABLE,
            2: FileCompressionStatus.COMPRESSION_PENDING,
            3: FileCompressionStatus.COMPRESSION_PROCESSING,
            4: FileCompressionStatus.COMPRESSION_COMPLETED,
            5: FileCompressionStatus.COMPRESSION_FAILED,
            6: FileCompressionStatus.COMPRESSION_SKIPPED,
            7: FileCompressionStatus.COMPRESSION_FILE_NOT_FOUND,
        }
        return status_map.get(proto_status, FileCompressionStatus.COMPRESSION_UNKNOWN)

    def _convert_sync_status(self, proto_status: int) -> FileSyncStatus:
        """转换同步状态枚举"""
        status_map = {
            0: FileSyncStatus.SYNC_UNKNOWN,
            1: FileSyncStatus.SYNC_NOT_REQUIRED,
            2: FileSyncStatus.SYNC_PENDING,
            3: FileSyncStatus.SYNC_PROCESSING,
            4: FileSyncStatus.SYNC_PARTIAL,
            5: FileSyncStatus.SYNC_COMPLETED,
            6: FileSyncStatus.SYNC_FAILED,
            7: FileSyncStatus.SYNC_FILE_NOT_FOUND,
        }
        return status_map.get(proto_status, FileSyncStatus.SYNC_UNKNOWN)
