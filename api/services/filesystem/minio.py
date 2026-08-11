import asyncio
import json
from typing import Any, BinaryIO, Dict, Optional

from loguru import logger
from minio import Minio
from minio.error import S3Error

from .base import BaseFileSystem


class MinioFileSystem(BaseFileSystem):
    """MinIO implementation of the filesystem interface for OSS users.

    Two endpoints, two different purposes:
    - endpoint (host:port) + secure (bool): used by the MinIO SDK for
      container-to-container calls. The SDK requires these split.
    - public_endpoint (full URL, e.g. "https://example.com"): used verbatim
      when building URLs that browsers will fetch. Required.
    """

    def __init__(
        self,
        endpoint: str = "localhost:9000",
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        bucket_name: str = "voice-audio",
        secure: bool = False,
        public_endpoint: Optional[str] = None,
    ):
        if not public_endpoint:
            raise ValueError(
                "MinioFileSystem requires public_endpoint (set MINIO_PUBLIC_ENDPOINT). "
                "Expected a full URL with scheme, e.g. 'http://localhost:9000' or 'https://example.com'."
            )
        if not (
            public_endpoint.startswith("http://")
            or public_endpoint.startswith("https://")
        ):
            raise ValueError(
                f"MINIO_PUBLIC_ENDPOINT must include a scheme (http:// or https://), got: {public_endpoint!r}"
            )

        self.bucket_name = bucket_name
        self.endpoint = endpoint
        self.public_endpoint = public_endpoint.rstrip("/")
        self.secure = secure
        self.access_key = access_key
        self.secret_key = secret_key

        import os
        import tempfile
        from .local import LocalFileSystem
        storage_dir = os.getenv(
            "DOGRAH_STORAGE_DIR", os.path.join(tempfile.gettempdir(), "dograh_storage")
        )
        self._local_fallback = LocalFileSystem(storage_dir)

        # Client for internal operations (uploads, etc.)
        self.client = Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=secure
        )

        # Ensure bucket exists and configure anonymous access (using internal client)
        try:
            if not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)

            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"],
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": "*"},
                        "Action": ["s3:ListBucket"],
                        "Resource": [f"arn:aws:s3:::{self.bucket_name}"],
                    },
                ],
            }

            self.client.set_bucket_policy(self.bucket_name, json.dumps(policy))
        except Exception as e:
            logger.debug(f"Bucket setup note: {e}")
            pass

    async def acreate_file(self, file_path: str, content: BinaryIO) -> bool:
        try:
            data = await content.read()

            def _put():
                self.client.put_object(
                    self.bucket_name,
                    file_path,
                    data=bytes(data),
                    length=len(data),
                )

            await asyncio.to_thread(_put)
            await self._local_fallback.acreate_file(file_path, content)
            return True
        except Exception as e:
            logger.warning(f"MinIO create_file note ({e}), using local disk fallback")
            return await self._local_fallback.acreate_file(file_path, content)

    async def aupload_file(self, local_path: str, destination_path: str) -> bool:
        try:

            def _fput():
                self.client.fput_object(self.bucket_name, destination_path, local_path)

            await asyncio.to_thread(_fput)
            await self._local_fallback.aupload_file(local_path, destination_path)
            return True
        except Exception as e:
            logger.warning(f"MinIO upload note ({e}), storing to local disk fallback")
            return await self._local_fallback.aupload_file(local_path, destination_path)

    async def aget_signed_url(
        self,
        file_path: str,
        expiration: int = 3600,
        force_inline: bool = False,
        use_internal_endpoint: bool = False,
    ) -> Optional[str]:
        try:
            if use_internal_endpoint:
                protocol = "https" if self.secure else "http"
                base = f"{protocol}://{self.endpoint}"
            else:
                base = self.public_endpoint
            return f"{base}/{self.bucket_name}/{file_path}"
        except Exception as e:
            logger.error(f"Error generating MinIO URL: {e}")
            return None

    async def aget_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get MinIO object metadata."""
        try:

            def _stat():
                return self.client.stat_object(self.bucket_name, file_path)

            stat = await asyncio.to_thread(_stat)
            return {
                "size": stat.size,
                "created_at": stat.last_modified,
                "modified_at": stat.last_modified,
                "etag": stat.etag.strip('"') if stat.etag else None,
                "content_type": stat.content_type,
                "storage_class": None,  # MinIO doesn't have storage classes like S3
            }
        except Exception:
            return await self._local_fallback.aget_file_metadata(file_path)

    async def aget_presigned_put_url(
        self,
        file_path: str,
        expiration: int = 900,
        content_type: str = "text/csv",
        max_size: int = 10_485_760,
    ) -> Optional[str]:
        """Generate an unsigned URL for direct file upload.

        For local MinIO development with anonymous upload enabled, we return
        a simple unsigned URL instead of a presigned URL. This avoids signature
        mismatch issues when the internal endpoint (minio:9000) differs from
        the public endpoint (localhost:9000).

        The bucket policy allows anonymous s3:PutObject, so no signature is needed.
        """
        try:
            url = f"{self.public_endpoint}/{self.bucket_name}/{file_path}"
            logger.debug(f"Generated unsigned upload URL: {url}")
            return url
        except Exception as e:
            logger.error(f"Error generating MinIO upload URL: {e}")
            return None

    async def adownload_file(self, source_path: str, local_path: str) -> bool:
        """Download a file from MinIO to local path."""
        try:

            def _fget():
                self.client.fget_object(self.bucket_name, source_path, local_path)

            await asyncio.to_thread(_fget)
            return True
        except Exception as e:
            logger.debug(f"MinIO download note ({e}), trying local disk fallback")
            return await self._local_fallback.adownload_file(source_path, local_path)

    async def acopy_file(self, source_path: str, destination_path: str) -> bool:
        """Copy a file within MinIO (server-side copy)."""
        try:
            from minio.commonconfig import CopySource

            def _copy():
                self.client.copy_object(
                    self.bucket_name,
                    destination_path,
                    CopySource(self.bucket_name, source_path),
                )

            await asyncio.to_thread(_copy)
            return True
        except Exception:
            return await self._local_fallback.acopy_file(source_path, destination_path)
