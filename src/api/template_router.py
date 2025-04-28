"""
API endpoints for template management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from typing import List, Optional
from ..supabase_api import SupabaseManager
from .models import TemplateCreate, TemplateUpdate, TemplateResponse, TemplateVersionCreate, TemplateVersionResponse, UserFavoriteResponse
from .auth_router import get_current_user # Assuming auth module exists and has get_current_user
import uuid

router = APIRouter(tags=["templates"])

async def get_supabase_manager(request: Request):
    """
    Dependency to get the Supabase manager from the app state.
    """
    if not hasattr(request.app.state, "supabase_manager"):
        request.app.state.supabase_manager = SupabaseManager()
    return request.app.state.supabase_manager

@router.get("/")
async def get_templates(
    request: Request,
    search: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    limit: int = 20,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """
    List all templates with optional filtering and pagination.
    """
    supabase_manager = await get_supabase_manager(request)
    templates = await supabase_manager.get_templates(search_term=search, tags=tags, limit=limit, offset=offset)
    return templates

@router.post("/")
async def create_template(
    request: Request,
    template: dict,
    current_user = Depends(get_current_user)
):
    """
    Create a new template.
    """
    supabase_manager = await get_supabase_manager(request)
    created_template = await supabase_manager.create_template(template)
    if created_template:
        return created_template
    raise HTTPException(status_code=500, detail="Failed to create template")

@router.get("/{template_id}")
async def get_template(request: Request, template_id: str, current_user = Depends(get_current_user)):
    """
    Get a specific template by ID.
    """
    supabase_manager = await get_supabase_manager(request)
    template = await supabase_manager.get_template_by_id(template_id)
    if template:
        return template
    raise HTTPException(status_code=404, detail="Template not found")

@router.put("/{template_id}")
async def update_template(
    request: Request,
    template_id: str,
    template: dict,
    current_user = Depends(get_current_user)
):
    """
    Update an existing template.
    """
    supabase_manager = await get_supabase_manager(request)
    updated_template = await supabase_manager.update_template_by_id(template_id, template)
    if updated_template:
        return updated_template
    raise HTTPException(status_code=404, detail="Template not found or failed to update")

@router.delete("/{template_id}")
async def delete_template(request: Request, template_id: str, current_user = Depends(get_current_user)):
    """
    Delete a template by ID.
    """
    supabase_manager = await get_supabase_manager(request)
    success = await supabase_manager.delete_template_by_id(template_id)
    if success:
        return {"message": "Template deleted successfully"}
    raise HTTPException(status_code=404, detail="Template not found or failed to delete")

@router.get("/{template_id}/versions")
async def get_template_versions(request: Request, template_id: str, current_user = Depends(get_current_user)):
    """
    List all versions of a template.
    """
    supabase_manager = await get_supabase_manager(request)
    versions = await supabase_manager.get_template_versions_by_template_id(template_id)
    return versions

@router.post("/{template_id}/versions")
async def create_template_version(
    request: Request,
    template_id: str,
    version: dict,
    current_user = Depends(get_current_user)
):
    """
    Create a new version for a template.
    """
    supabase_manager = await get_supabase_manager(request)
    version_data_dict = {"template_id": template_id, **version}
    created_version = await supabase_manager.create_template_version(version_data_dict)
    if created_version:
        return created_version
    raise HTTPException(status_code=500, detail="Failed to create template version")

@router.put("/{template_id}/versions/{version_id}/activate")
async def activate_template_version(
    request: Request,
    template_id: str,
    version_id: str,
    current_user = Depends(get_current_user)
):
    """
    Set a specific version of a template as active.
    """
    supabase_manager = await get_supabase_manager(request)
    activated_version = await supabase_manager.activate_template_version(version_id, template_id)
    if activated_version:
        return activated_version
    raise HTTPException(status_code=500, detail="Failed to activate template version")

@router.post("/{template_id}/favorite")
async def like_template(request: Request, template_id: str, current_user = Depends(get_current_user)):
    """
    Add a template to the current user's favorites.
    """
    supabase_manager = await get_supabase_manager(request)
    user_id = current_user["id"] if isinstance(current_user, dict) else current_user.id
    favorite = await supabase_manager.add_favorite_template(user_id, template_id)
    if favorite:
        return favorite
    raise HTTPException(status_code=500, detail="Failed to add template to favorites")

@router.delete("/{template_id}/favorite")
async def unlike_template(request: Request, template_id: str, current_user = Depends(get_current_user)):
    """
    Remove a template from the current user's favorites.
    """
    supabase_manager = await get_supabase_manager(request)
    user_id = current_user["id"] if isinstance(current_user, dict) else current_user.id
    success = await supabase_manager.remove_favorite_template(user_id, template_id)
    if success:
        return {"message": "Template removed from favorites successfully"}
    raise HTTPException(status_code=500, detail="Failed to remove template from favorites")

@router.get("/users/me/favorites")
async def get_user_favorites(request: Request, current_user = Depends(get_current_user)):
    """
    List the current user's favorite templates.
    """
    supabase_manager = await get_supabase_manager(request)
    user_id = current_user["id"] if isinstance(current_user, dict) else current_user.id
    favorite_templates = await supabase_manager.get_user_favorite_templates(user_id)
    return favorite_templates