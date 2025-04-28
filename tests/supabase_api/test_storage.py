"""
Unit tests for Supabase storage operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.supabase_api.storage import SupabaseStorageManager

# Mock the SupabaseManager and its methods
@pytest.fixture
def mock_supabase_manager():
    manager = MagicMock()
    manager.upload_file = AsyncMock()
    manager.download_file = AsyncMock()
    manager.list_files = AsyncMock()
    manager.delete_file = AsyncMock()
    return manager

# Mock the SupabaseStorageManager to use the mocked SupabaseManager
@pytest.fixture
def storage_manager(mock_supabase_manager):
    manager = SupabaseStorageManager()
    manager.supabase_manager = mock_supabase_manager
    return manager

@pytest.mark.asyncio
async def test_upload_blueprint(storage_manager, mock_supabase_manager):
    mock_supabase_manager.upload_file.return_value = {"key": "value"}
    file_path = "test/blueprint.schem"
    file_content = b"blueprint_data"
    response = await storage_manager.upload_blueprint(file_path, file_content)
    mock_supabase_manager.upload_file.assert_called_once_with("blueprints", file_path, file_content)
    assert response == {"key": "value"}

@pytest.mark.asyncio
async def test_download_blueprint(storage_manager, mock_supabase_manager):
    mock_supabase_manager.download_file.return_value = b"blueprint_data"
    file_path = "test/blueprint.schem"
    content = await storage_manager.download_blueprint(file_path)
    mock_supabase_manager.download_file.assert_called_once_with("blueprints", file_path)
    assert content == b"blueprint_data"

@pytest.mark.asyncio
async def test_list_blueprints(storage_manager, mock_supabase_manager):
    mock_supabase_manager.list_files.return_value = [{"name": "file1"}, {"name": "file2"}]
    path = "test"
    files = await storage_manager.list_blueprints(path)
    mock_supabase_manager.list_files.assert_called_once_with("blueprints", path)
    assert files == [{"name": "file1"}, {"name": "file2"}]

@pytest.mark.asyncio
async def test_delete_blueprints(storage_manager, mock_supabase_manager):
    mock_supabase_manager.delete_file.return_value = {"message": "deleted"}
    file_paths = ["test/file1.schem", "test/file2.schem"]
    response = await storage_manager.delete_blueprints(file_paths)
    mock_supabase_manager.delete_file.assert_called_once_with("blueprints", file_paths)
    assert response == {"message": "deleted"}

@pytest.mark.asyncio
async def test_upload_asset(storage_manager, mock_supabase_manager):
    mock_supabase_manager.upload_file.return_value = {"key": "value"}
    file_path = "test/asset.png"
    file_content = b"asset_data"
    response = await storage_manager.upload_asset(file_path, file_content)
    mock_supabase_manager.upload_file.assert_called_once_with("assets", file_path, file_content)
    assert response == {"key": "value"}

@pytest.mark.asyncio
async def test_download_asset(storage_manager, mock_supabase_manager):
    mock_supabase_manager.download_file.return_value = b"asset_data"
    file_path = "test/asset.png"
    content = await storage_manager.download_asset(file_path)
    mock_supabase_manager.download_file.assert_called_once_with("assets", file_path)
    assert content == b"asset_data"

@pytest.mark.asyncio
async def test_list_assets(storage_manager, mock_supabase_manager):
    mock_supabase_manager.list_files.return_value = [{"name": "asset1"}, {"name": "asset2"}]
    path = "test"
    files = await storage_manager.list_assets(path)
    mock_supabase_manager.list_files.assert_called_once_with("assets", path)
    assert files == [{"name": "asset1"}, {"name": "asset2"}]

@pytest.mark.asyncio
async def test_delete_assets(storage_manager, mock_supabase_manager):
    mock_supabase_manager.delete_file.return_value = {"message": "deleted"}
    file_paths = ["test/asset1.png", "test/asset2.png"]
    response = await storage_manager.delete_assets(file_paths)
    mock_supabase_manager.delete_file.assert_called_once_with("assets", file_paths)
    assert response == {"message": "deleted"}