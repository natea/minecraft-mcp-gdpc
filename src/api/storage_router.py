"""
API endpoints for Supabase storage operations.
"""

import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from typing import List, Optional

from ..supabase_api.storage import SupabaseStorageManager
from ..api.auth_router import get_current_user # Assuming get_current_user is in auth_router

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/storage",
    tags=["storage"],
    responses={404: {"description": "Not found"}},
)

@router.post("/blueprints/upload/")
async def upload_blueprint(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user) # Protect endpoint with authentication
):
    """
    Uploads a blueprint file to the 'blueprints' bucket.
    """
    storage_manager = SupabaseStorageManager()
    try:
        # You might want to include user ID or other metadata in the file path
        file_path = f"user_{user['id']}/{file.filename}"
        content = await file.read()
        response = await storage_manager.upload_blueprint(file_path, content)
        if response:
            return {"message": "Blueprint uploaded successfully", "data": response}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload blueprint",
            )
    except Exception as e:
        logger.error(f"Error uploading blueprint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during blueprint upload",
        )

@router.get("/blueprints/download/{file_path:path}")
async def download_blueprint(
    file_path: str,
    user: dict = Depends(get_current_user) # Protect endpoint with authentication
):
    """
    Downloads a blueprint file from the 'blueprints' bucket.
    """
    storage_manager = SupabaseStorageManager()
    try:
        # Ensure the user is authorized to download this file if necessary
        # For now, assuming any authenticated user can download if they know the path
        content = await storage_manager.download_blueprint(file_path)
        if content:
            # You might need to set appropriate Content-Disposition headers
            return content
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blueprint not found",
            )
    except Exception as e:
        logger.error(f"Error downloading blueprint {file_path}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during blueprint download",
        )

@router.get("/blueprints/list/")
async def list_blueprints(
    path: Optional[str] = None,
    user: dict = Depends(get_current_user) # Protect endpoint with authentication
):
    """
    Lists blueprint files in the 'blueprints' bucket path.
    """
    storage_manager = SupabaseStorageManager()
    try:
        # You might want to restrict listing to the user's own directory
        list_path = f"user_{user['id']}/{path}" if path else f"user_{user['id']}"
        files = await storage_manager.list_blueprints(list_path)
        if files is not None:
            return {"files": files}
        else:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list blueprints",
            )
    except Exception as e:
        logger.error(f"Error listing blueprints in path {path}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during blueprint listing",
        )

@router.delete("/blueprints/delete/")
async def delete_blueprints(
    file_paths: List[str],
    user: dict = Depends(get_current_user) # Protect endpoint with authentication
):
    """
    Deletes blueprint files from the 'blueprints' bucket.
    """
    storage_manager = SupabaseStorageManager()
    try:
        # Ensure the user is authorized to delete these files
        # You might need to prepend user ID to file_paths
        response = await storage_manager.delete_blueprints(file_paths)
        if response:
            return {"message": "Blueprints deleted successfully", "data": response}
        else:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete blueprints",
            )
    except Exception as e:
        logger.error(f"Error deleting blueprints {file_paths}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during blueprint deletion",
        )

@router.post("/assets/upload/")
async def upload_asset(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user) # Protect endpoint with authentication
):
    """
    Uploads an asset file to the 'assets' bucket.
    """
    storage_manager = SupabaseStorageManager()
    try:
        # You might want to include user ID or other metadata in the file path
        file_path = f"user_{user['id']}/{file.filename}"
        content = await file.read()
        response = await storage_manager.upload_asset(file_path, content)
        if response:
            return {"message": "Asset uploaded successfully", "data": response}
        else:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload asset",
            )
    except Exception as e:
        logger.error(f"Error uploading asset: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during asset upload",
        )

@router.get("/assets/download/{file_path:path}")
async def download_asset(
    file_path: str,
    user: dict = Depends(get_current_user) # Protect endpoint with authentication
):
    """
    Downloads an asset file from the 'assets' bucket.
    """
    storage_manager = SupabaseStorageManager()
    try:
        # Ensure the user is authorized to download this file if necessary
        content = await storage_manager.download_asset(file_path)
        if content:
            # You might need to set appropriate Content-Disposition headers
            return content
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found",
            )
    except Exception as e:
        logger.error(f"Error downloading asset {file_path}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during asset download",
        )

@router.get("/assets/list/")
async def list_assets(
    path: Optional[str] = None,
    user: dict = Depends(get_current_user) # Protect endpoint with authentication
):
    """
    Lists asset files in the 'assets' bucket path.
    """
    storage_manager = SupabaseStorageManager()
    try:
        # You might want to restrict listing to the user's own directory
        list_path = f"user_{user['id']}/{path}" if path else f"user_{user['id']}"
        files = await storage_manager.list_assets(list_path)
        if files is not None:
            return {"files": files}
        else:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to list assets",
            )
    except Exception as e:
        logger.error(f"Error listing assets in path {path}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during asset listing",
        )

@router.delete("/assets/delete/")
async def delete_assets(
    file_paths: List[str],
    user: dict = Depends(get_current_user) # Protect endpoint with authentication
):
    """
    Deletes asset files from the 'assets' bucket.
    """
    storage_manager = SupabaseStorageManager()
    try:
        # Ensure the user is authorized to delete these files
        # You might need to prepend user ID to file_paths
        response = await storage_manager.delete_assets(file_paths)
        if response:
            return {"message": "Assets deleted successfully", "data": response}
        else:
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete assets",
            )
    except Exception as e:
        logger.error(f"Error deleting assets {file_paths}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during asset deletion",
        )