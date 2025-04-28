"""
Supabase client initialization module.
"""

import logging
import os
from typing import Optional, List, Dict, Any

from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

async def init_supabase_client() -> Optional[Client]:
    """
    Initializes and returns a Supabase client instance.
    
    Returns:
        Optional[Client]: The initialized Supabase client, or None if initialization fails.
    """
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        logger.error("Supabase URL or Key not found in environment variables.")
        return None
    
    try:
        logger.info(f"Initializing Supabase client for URL: {supabase_url[:20]}...")
        client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully.")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}", exc_info=True)
        return None

class SupabaseManager:
    """
    Manages interactions with Supabase for the template API.
    This class provides methods to interact with the templates, template versions,
    and user favorites tables in Supabase.
    """
    
    def __init__(self):
        self.client = None
        
    async def get_client(self) -> Client:
        """
        Returns the initialized Supabase client instance.
        Initializes if not already done.
        
        Returns:
            Client: The initialized Supabase client.
        """
        if self.client is None:
            self.client = await init_supabase_client()
            if self.client is None:
                raise Exception("Failed to initialize Supabase client")
        return self.client
    
    async def get_templates(self, search_term=None, tags=None, limit=20, offset=0):
        """
        Retrieves templates from the database with optional filtering and pagination.
        
        Args:
            search_term: Optional term to search in template titles or descriptions.
            tags: Optional list of tags to filter by.
            limit: The maximum number of templates to return.
            offset: The number of templates to skip.
            
        Returns:
            A list of template dictionaries.
        """
        client = await self.get_client()
        try:
            query = client.table('templates').select('*')
            
            if search_term:
                query = query.or_(f'name.ilike.%{search_term}%,description.ilike.%{search_term}%')
                
            if tags and len(tags) > 0:
                # Filter by tags (assuming tags is stored as an array in Supabase)
                for tag in tags:
                    query = query.contains('tags', [tag])
                    
            response = await query.limit(limit).offset(offset).execute()
            
            if response.data:
                logger.info(f"Retrieved {len(response.data)} templates")
                return response.data
            else:
                logger.info("No templates found matching criteria")
                return []
        except Exception as e:
            logger.error(f"Error retrieving templates: {e}", exc_info=True)
            return []
    
    async def create_template(self, template_data: Dict[str, Any]):
        """
        Creates a new template in the database.
        
        Args:
            template_data: Dictionary containing the template data.
            
        Returns:
            The created template if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            response = await client.table('templates').insert(template_data).execute()
            if response.data and len(response.data) > 0:
                logger.info(f"Template created with ID: {response.data[0]['id']}")
                return response.data[0]
            else:
                logger.error("Failed to create template: No data returned")
                return None
        except Exception as e:
            logger.error(f"Error creating template: {e}", exc_info=True)
            return None
    
    async def get_template_by_id(self, template_id: str):
        """
        Retrieves a template by its ID.
        
        Args:
            template_id: The ID of the template to retrieve.
            
        Returns:
            The template if found, None otherwise.
        """
        client = await self.get_client()
        try:
            response = await client.table('templates').select('*').eq('id', template_id).single().execute()
            if response.data:
                logger.info(f"Retrieved template with ID: {template_id}")
                return response.data
            else:
                logger.info(f"Template with ID {template_id} not found")
                return None
        except Exception as e:
            logger.error(f"Error retrieving template {template_id}: {e}", exc_info=True)
            return None
    
    async def update_template_by_id(self, template_id: str, template_data: Dict[str, Any]):
        """
        Updates a template by its ID.
        
        Args:
            template_id: The ID of the template to update.
            template_data: Dictionary containing the updated template data.
            
        Returns:
            The updated template if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            response = await client.table('templates').update(template_data).eq('id', template_id).execute()
            if response.data and len(response.data) > 0:
                logger.info(f"Updated template with ID: {template_id}")
                return response.data[0]
            else:
                logger.error(f"Failed to update template {template_id}: No data returned")
                return None
        except Exception as e:
            logger.error(f"Error updating template {template_id}: {e}", exc_info=True)
            return None
    
    async def delete_template_by_id(self, template_id: str):
        """
        Deletes a template by its ID.
        
        Args:
            template_id: The ID of the template to delete.
            
        Returns:
            True if successful, False otherwise.
        """
        client = await self.get_client()
        try:
            response = await client.table('templates').delete().eq('id', template_id).execute()
            if response.data is not None:
                logger.info(f"Deleted template with ID: {template_id}")
                return True
            else:
                logger.error(f"Failed to delete template {template_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting template {template_id}: {e}", exc_info=True)
            return False
    
    async def get_template_versions_by_template_id(self, template_id: str):
        """
        Retrieves all versions of a template.
        
        Args:
            template_id: The ID of the template.
            
        Returns:
            A list of template versions.
        """
        client = await self.get_client()
        try:
            response = await client.table('template_versions').select('*').eq('template_id', template_id).execute()
            if response.data:
                logger.info(f"Retrieved {len(response.data)} versions for template {template_id}")
                return response.data
            else:
                logger.info(f"No versions found for template {template_id}")
                return []
        except Exception as e:
            logger.error(f"Error retrieving versions for template {template_id}: {e}", exc_info=True)
            return []
    
    async def create_template_version(self, version_data: Dict[str, Any]):
        """
        Creates a new version for a template.
        
        Args:
            version_data: Dictionary containing the version data.
            
        Returns:
            The created version if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            response = await client.table('template_versions').insert(version_data).execute()
            if response.data and len(response.data) > 0:
                logger.info(f"Created version for template {version_data.get('template_id')}")
                return response.data[0]
            else:
                logger.error(f"Failed to create version for template {version_data.get('template_id')}")
                return None
        except Exception as e:
            logger.error(f"Error creating version for template {version_data.get('template_id')}: {e}", exc_info=True)
            return None
    
    async def activate_template_version(self, version_id: str, template_id: str):
        """
        Activates a specific version of a template and deactivates all others.
        
        Args:
            version_id: The ID of the version to activate.
            template_id: The ID of the template.
            
        Returns:
            The activated version if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            # First deactivate all versions for this template
            await client.table('template_versions').update({'is_active': False}).eq('template_id', template_id).execute()
            
            # Then activate the specified version
            response = await client.table('template_versions').update({'is_active': True}).eq('id', version_id).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"Activated version {version_id} for template {template_id}")
                return response.data[0]
            else:
                logger.error(f"Failed to activate version {version_id} for template {template_id}")
                return None
        except Exception as e:
            logger.error(f"Error activating version {version_id} for template {template_id}: {e}", exc_info=True)
            return None
    
    async def add_favorite_template(self, user_id: str, template_id: str):
        """
        Adds a template to a user's favorites.
        
        Args:
            user_id: The ID of the user.
            template_id: The ID of the template to favorite.
            
        Returns:
            The created favorite record if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            response = await client.table('user_favorites').insert({
                'user_id': user_id,
                'template_id': template_id
            }).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"User {user_id} favorited template {template_id}")
                return response.data[0]
            else:
                logger.error(f"Failed to add template {template_id} to favorites for user {user_id}")
                return None
        except Exception as e:
            logger.error(f"Error adding template {template_id} to favorites for user {user_id}: {e}", exc_info=True)
            return None
    
    async def remove_favorite_template(self, user_id: str, template_id: str):
        """
        Removes a template from a user's favorites.
        
        Args:
            user_id: The ID of the user.
            template_id: The ID of the template to unfavorite.
            
        Returns:
            True if successful, False otherwise.
        """
        client = await self.get_client()
        try:
            response = await client.table('user_favorites').delete().eq('user_id', user_id).eq('template_id', template_id).execute()
            
            if response.data is not None:
                logger.info(f"User {user_id} unfavorited template {template_id}")
                return True
            else:
                logger.error(f"Failed to remove template {template_id} from favorites for user {user_id}")
                return False
        except Exception as e:
            logger.error(f"Error removing template {template_id} from favorites for user {user_id}: {e}", exc_info=True)
            return False
    
    async def get_user_favorite_templates(self, user_id: str):
        """
        Retrieves all templates favorited by a user.
        
        Args:
            user_id: The ID of the user.
            
        Returns:
            A list of favorited templates.
        """
        client = await self.get_client()
        try:
            # First get the favorite records
            favorites_response = await client.table('user_favorites').select('template_id').eq('user_id', user_id).execute()
            
            if not favorites_response.data or len(favorites_response.data) == 0:
                logger.info(f"User {user_id} has no favorite templates")
                return []
            
            # Extract template IDs
            template_ids = [fav['template_id'] for fav in favorites_response.data]
            
            # Then get the actual templates
            templates = []
            for template_id in template_ids:
                template_response = await client.table('templates').select('*').eq('id', template_id).execute()
                if template_response.data and len(template_response.data) > 0:
                    templates.append(template_response.data[0])
            
            logger.info(f"Retrieved {len(templates)} favorite templates for user {user_id}")
            return templates
        except Exception as e:
            logger.error(f"Error retrieving favorite templates for user {user_id}: {e}", exc_info=True)
            return []

    async def upload_file(self, bucket_name: str, file_path: str, file_content: bytes):
        """
        Uploads a file to a specified Supabase storage bucket.

        Args:
            bucket_name: The name of the storage bucket.
            file_path: The path within the bucket to upload the file to.
            file_content: The content of the file as bytes.

        Returns:
            The response data from the upload operation if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            response = client.storage.from_(bucket_name).upload(file_path, file_content)
            if response.data:
                logger.info(f"Successfully uploaded file to {bucket_name}/{file_path}")
                return response.data
            else:
                logger.error(f"Failed to upload file to {bucket_name}/{file_path}: No data returned")
                return None
        except Exception as e:
            logger.error(f"Error uploading file to {bucket_name}/{file_path}: {e}", exc_info=True)
            return None

    async def download_file(self, bucket_name: str, file_path: str):
        """
        Downloads a file from a specified Supabase storage bucket.

        Args:
            bucket_name: The name of the storage bucket.
            file_path: The path within the bucket to download the file from.

        Returns:
            The content of the file as bytes if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            response = client.storage.from_(bucket_name).download(file_path)
            if response:
                logger.info(f"Successfully downloaded file from {bucket_name}/{file_path}")
                return response
            else:
                logger.error(f"Failed to download file from {bucket_name}/{file_path}: No data returned")
                return None
        except Exception as e:
            logger.error(f"Error downloading file from {bucket_name}/{file_path}: {e}", exc_info=True)
            return None

    async def list_files(self, bucket_name: str, path: Optional[str] = None):
        """
        Lists files in a specified Supabase storage bucket path.

        Args:
            bucket_name: The name of the storage bucket.
            path: The path within the bucket to list files from (optional).

        Returns:
            A list of file objects if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            response = client.storage.from_(bucket_name).list(path)
            if response:
                logger.info(f"Successfully listed files in {bucket_name}/{path or ''}")
                return response
            else:
                logger.info(f"No files found in {bucket_name}/{path or ''}")
                return []
        except Exception as e:
            logger.error(f"Error listing files in {bucket_name}/{path or ''}: {e}", exc_info=True)
            return None

    async def delete_file(self, bucket_name: str, file_paths: List[str]):
        """
        Deletes files from a specified Supabase storage bucket.

        Args:
            bucket_name: The name of the storage bucket.
            file_paths: A list of paths within the bucket to delete.

        Returns:
            The response data from the delete operation if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            response = client.storage.from_(bucket_name).remove(file_paths)
            if response.data:
                logger.info(f"Successfully deleted files from {bucket_name}: {file_paths}")
                return response.data
            else:
                logger.error(f"Failed to delete files from {bucket_name}: {file_paths}: No data returned")
                return None
        except Exception as e:
            logger.error(f"Error deleting files from {bucket_name}: {file_paths}: {e}", exc_info=True)
            return None