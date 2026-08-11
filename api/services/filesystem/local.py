import asyncio
import os
from datetime import datetime
from typing import BinaryIO, Optional

import aiofiles

from .base import BaseFileSystem


class LocalFileSystem(BaseFileSystem):
    """Local filesystem implementation."""

    def __init__(self, base_path: str):
        """Initialize local filesystem.

        Args:
            base_path: Base directory path for file operations
        """
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def _get_full_path(self, file_path: str) -> str:
        """Get the full path by joining with base path."""
        return os.path.join(self.base_path, file_path)

    async def acreate_file(self, file_path: str, content: BinaryIO) -> bool:
        try:
            full_path = self._get_full_path(file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            async with aiofiles.open(full_path, "wb") as f:
                await f.write(await content.read())
            return True
        except Exception:
            return False

    async def create_temp_file(self, file_path: str) -> bool:
        try:
            full_path = self._get_full_path(file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            return True
        except Exception:
            return False

    async def aupload_file(self, local_path: str, destination_path: str) -> bool:
        try:
            full_dest_path = self._get_full_path(destination_path)
            os.makedirs(os.path.dirname(full_dest_path), exist_ok=True)

            async with (
                aiofiles.open(local_path, "rb") as src,
                aiofiles.open(full_dest_path, "wb") as dst,
            ):
                await dst.write(await src.read())
            return True
        except Exception:
            return False

    async def aget_signed_url(
        self, file_path: str, expiration: int = 3600
    ) -> Optional[str]:
        # For local filesystem, we'll create a temporary symlink with expiration
        try:
            full_path = self._get_full_path(file_path)
            if not os.path.exists(full_path):
                return None

            # Create a temporary directory for symlinks
            temp_dir = os.path.join(self.base_path, ".temp_links")
            os.makedirs(temp_dir, exist_ok=True)

            # Generate a unique temporary filename
            temp_filename = (
                f"{datetime.now().timestamp()}_{os.path.basename(file_path)}"
            )
            temp_path = os.path.join(temp_dir, temp_filename)

            # Create symlink
            os.symlink(full_path, temp_path)

            # Schedule deletion after expiration
            async def delete_after_expiration():
                await asyncio.sleep(expiration)
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

            asyncio.create_task(delete_after_expiration())

            return f"/files/{temp_filename}"
        except Exception:
            return None

    async def aget_file_metadata(self, file_path: str) -> Optional[dict]:
        try:
            full_path = self._get_full_path(file_path)
            if not os.path.exists(full_path):
                return None
            stat = os.stat(full_path)
            return {
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime),
                "modified_at": datetime.fromtimestamp(stat.st_mtime),
                "etag": None,
                "content_type": None,
            }
        except Exception:
            return None

    async def aget_presigned_put_url(
        self,
        file_path: str,
        expiration: int = 900,
        content_type: str = "text/csv",
        max_size: int = 10_485_760,
    ) -> Optional[str]:
        return None

    async def adownload_file(self, source_path: str, local_path: str) -> bool:
        try:
            full_source_path = self._get_full_path(source_path)
            if not os.path.exists(full_source_path):
                return False
            if full_source_path == local_path:
                return True
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            async with (
                aiofiles.open(full_source_path, "rb") as src,
                aiofiles.open(local_path, "wb") as dst,
            ):
                await dst.write(await src.read())
            return True
        except Exception:
            return False

    async def acopy_file(self, source_path: str, destination_path: str) -> bool:
        try:
            full_src = self._get_full_path(source_path)
            full_dst = self._get_full_path(destination_path)
            if not os.path.exists(full_src):
                return False
            os.makedirs(os.path.dirname(full_dst), exist_ok=True)
            async with (
                aiofiles.open(full_src, "rb") as src,
                aiofiles.open(full_dst, "wb") as dst,
            ):
                await dst.write(await src.read())
            return True
        except Exception:
            return False
