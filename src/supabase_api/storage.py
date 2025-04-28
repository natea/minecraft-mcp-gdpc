"""
Supabase storage operations module.
"""

import logging
from typing import Optional, List, Dict, Any

from .client import SupabaseManager

logger = logging.getLogger(__name__)

class SupabaseStorageManager:
    """
    Manages interactions with Supabase Storage for blueprints and assets.
    """

    def __init__(self):
        self.supabase_manager = SupabaseManager()

    async def upload_blueprint(self, file_path: str, file_content: bytes):
        """
        Uploads a blueprint file to the 'blueprints' bucket.

        Args:
            file_path: The path within the 'blueprints' bucket to upload the file to.
            file_content: The content of the blueprint file as bytes.

        Returns:
            The response data from the upload operation if successful, None otherwise.
        """
        return await self.supabase_manager.upload_file("blueprints", file_path, file_content)

    async def download_blueprint(self, file_path: str):
        """
        Downloads a blueprint file from the 'blueprints' bucket.

        Args:
            file_path: The path within the 'blueprints' bucket to download the file from.

        Returns:
            The content of the blueprint file as bytes if successful, None otherwise.
        """
        return await self.supabase_manager.download_file("blueprints", file_path)

    async def list_blueprints(self, path: Optional[str] = None):
        """
        Lists blueprint files in the 'blueprints' bucket path.

        Args:
            path: The path within the 'blueprints' bucket to list files from (optional).

        Returns:
            A list of file objects if successful, None otherwise.
        """
        return await self.supabase_manager.list_files("blueprints", path)

    async def delete_blueprints(self, file_paths: List[str]):
        """
        Deletes blueprint files from the 'blueprints' bucket.

        Args:
            file_paths: A list of paths within the 'blueprints' bucket to delete.

        Returns:
            The response data from the delete operation if successful, None otherwise.
        """
        return await self.supabase_manager.delete_file("blueprints", file_paths)

    async def upload_asset(self, file_path: str, file_content: bytes):
        """
        Uploads an asset file to the 'assets' bucket.

        Args:
            file_path: The path within the 'assets' bucket to upload the file to.
            file_content: The content of the asset file as bytes.

        Returns:
            The response data from the upload operation if successful, None otherwise.
        """
        return await self.supabase_manager.upload_file("assets", file_path, file_content)

    async def download_asset(self, file_path: str):
        """
        Downloads an asset file from the 'assets' bucket.

        Args:
            file_path: The path within the 'assets' bucket to download the file from.

        Returns:
            The content of the asset file as bytes if successful, None otherwise.
        """
        return await self.supabase_manager.download_file("assets", file_path)

    async def list_assets(self, path: Optional[str] = None):
        """
        Lists asset files in the 'assets' bucket path.

        Args:
            path: The path within the 'assets' bucket to list files from (optional).

        Returns:
            A list of file objects if successful, None otherwise.
        """
        return await self.supabase_manager.list_files("assets", path)

    async def delete_assets(self, file_paths: List[str]):
        """
        Deletes asset files from the 'assets' bucket.

        Args:
            file_paths: A list of paths within the 'assets' bucket to delete.

        Returns:
            The response data from the delete operation if successful, None otherwise.
        """
        return await self.supabase_manager.delete_file("assets", file_paths)