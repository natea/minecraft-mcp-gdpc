"""
Initializes and provides access to the Supabase client instance.
"""

import logging
import os
from typing import Optional

# Use the official Supabase Python client which supports async operations
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

supabase_url: Optional[str] = os.getenv("SUPABASE_URL")
supabase_key: Optional[str] = os.getenv("SUPABASE_KEY")
supabase_service_key: Optional[str] = os.getenv("SUPABASE_SERVICE_KEY") # For admin operations

supabase_client: Optional[Client] = None

class SupabaseManager:
    """
    Manages interactions with the Supabase backend.
    """
    def __init__(self):
        self.client: Optional[Client] = None
        self.admin_client: Optional[Client] = None

    async def init_clients(self):
        """
        Initializes the Supabase clients using environment variables.
        """
        if self.client and self.admin_client:
            return

        if not supabase_url or not supabase_key:
            logger.error("Supabase URL or Key not found in environment variables. Cannot initialize client.")
            raise Exception("Supabase URL or Key missing for client.")

        try:
            logger.info(f"Initializing Supabase client for URL: {supabase_url[:20]}...")
            self.client = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}", exc_info=True)
            raise Exception("Supabase client could not be initialized.")

        if not supabase_url or not supabase_service_key:
            logger.error("Supabase URL or Service Key not found in environment variables. Cannot initialize admin client.")
            # Don't raise an exception here, admin client is not always required
            self.admin_client = None
        else:
            try:
                logger.info("Initializing Supabase admin client...")
                self.admin_client = create_client(supabase_url, supabase_service_key)
                logger.info("Supabase admin client initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase admin client: {e}", exc_info=True)
                self.admin_client = None # Ensure admin_client is None on failure


    async def get_client(self) -> Client:
        """
        Returns the initialized Supabase client instance. Initializes if not already done.

        Raises:
            Exception: If the client cannot be initialized.

        Returns:
            The initialized AsyncClient instance.
        """
        if self.client is None:
            await self.init_clients()
        if self.client is None:
             raise Exception("Supabase client could not be initialized. Check configuration.")
        return self.client

    async def get_admin_client(self) -> Client:
        """
        Returns the initialized Supabase client instance using the service key for admin operations.

        Raises:
            Exception: If the client cannot be initialized or service key is missing.

        Returns:
            The initialized AsyncClient instance with admin privileges.
        """
        if self.admin_client is None:
            await self.init_clients()
        if self.admin_client is None:
             raise Exception("Supabase admin client could not be initialized. Check configuration and service key.")
        return self.admin_client


    # Authentication methods
    async def sign_up(self, email, password, username):
        """
        Signs up a new user and creates a corresponding profile.

        Args:
            email: The user's email address.
            password: The user's password.
            username: The user's desired username.

        Returns:
            The user object if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            # Create user
            user = client.auth.sign_up(email=email, password=password)
            if user.user:
                # Create profile
                await client.table('profiles').insert({
                    'id': user.user.id,
                    'username': username
                }).execute()
                logger.info(f"User signed up and profile created for {email}")
                return user.user
            else:
                logger.error(f"Supabase sign up failed for {email}: {user.error.message if user.error else 'Unknown error'}")
                return None
        except Exception as e:
            logger.error(f"An error occurred during sign up for {email}: {e}", exc_info=True)
            return None

    async def sign_in(self, email, password):
        """
        Signs in an existing user.

        Args:
            email: The user's email address.
            password: The user's password.

        Returns:
            The session object if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            session = client.auth.sign_in_with_password(email=email, password=password)
            if session.user:
                logger.info(f"User signed in: {email}")
                return session
            else:
                logger.error(f"Supabase sign in failed for {email}: {session.error.message if session.error else 'Unknown error'}")
                return None
        except Exception as e:
            logger.error(f"An error occurred during sign in for {email}: {e}", exc_info=True)
            return None

    # Template methods
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
            query = client.from_('templates').select('*')

            if search_term:
                query = query.or_(f'title.ilike.%{search_term}%,description.ilike.%{search_term}%')

            if tags:
                # Assuming tags are stored as a text array or similar in the 'templates' table
                # This might need adjustment based on the actual schema
                query = query.filter('tags', 'cs', tags) # 'cs' stands for 'contains' for array types

            query = query.limit(limit).offset(offset)

            response = await query.execute()

            if response.data:
                logger.info(f"Retrieved {len(response.data)} templates.")
                return response.data
            else:
                logger.info("No templates found matching the criteria.")
                return []
        except Exception as e:
            logger.error(f"An error occurred while retrieving templates: {e}", exc_info=True)
            return []

    async def create_template(self, template_data):
        """
        Creates a new template in the database.

        Args:
            template_data: A dictionary containing the template data.

        Returns:
            The created template data if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            response = await client.from_('templates').insert(template_data).execute()
            if response.data:
                logger.info(f"Template created with ID: {response.data[0].get('id')}")
                return response.data[0]
            else:
                logger.error(f"Supabase template creation failed: {response.error.message if response.error else 'Unknown error'}")
                return None
        except Exception as e:
            logger.error(f"An error occurred while creating template: {e}", exc_info=True)
            return None

    async def get_template_by_id(self, template_id: str):
        """
        Retrieves a template from the database by its ID.

        Args:
            template_id: The ID of the template.

        Returns:
            The template data if found, None otherwise.
        """
        client = await self.get_client()
        try:
            response = await client.from_('templates').select('*').eq('id', template_id).single().execute()
            if response.data:
                logger.info(f"Retrieved template with ID: {template_id}")
                return response.data
            else:
                logger.info(f"Template with ID {template_id} not found.")
                return None
        except Exception as e:
            logger.error(f"An error occurred while retrieving template with ID {template_id}: {e}", exc_info=True)
            return None

    async def update_template_by_id(self, template_id: str, update_data: dict):
        """
        Updates a template in the database by its ID.

        Args:
            template_id: The ID of the template.
            update_data: A dictionary containing the data to update.
        Returns:
            The updated template data if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            response = await client.from_('templates').update(update_data).eq('id', template_id).execute()
            if response.data:
                logger.info(f"Template with ID {template_id} updated.")
                return response.data[0]
            else:
                logger.error(f"Supabase template update failed for ID {template_id}: {response.error.message if response.error else 'Unknown error'}")
                return None
        except Exception as e:
            logger.error(f"An error occurred while updating template with ID {template_id}: {e}", exc_info=True)
            return None

    async def delete_template_by_id(self, template_id: str):
        """
        Deletes a template from the database by its ID.

        Args:
            template_id: The ID of the template.

        Returns:
            True if successful, False otherwise.
        """
        client = await self.get_client()
        try:
            response = await client.from_('templates').delete().eq('id', template_id).execute()
            if response.data:
                logger.info(f"Template with ID {template_id} deleted.")
                return True
            else:
                logger.error(f"Supabase template deletion failed for ID {template_id}: {response.error.message if response.error else 'Unknown error'}")
                return False
        except Exception as e:
            logger.error(f"An error occurred while deleting template with ID {template_id}: {e}", exc_info=True)
            return False

    async def get_template_versions_by_template_id(self, template_id: str):
        """
        Retrieves all versions for a given template ID.

        Args:
            template_id: The ID of the template.

        Returns:
            A list of template version dictionaries.
        """
        client = await self.get_client()
        try:
            response = await client.from_('template_versions').select('*').eq('template_id', template_id).execute()
            if response.data:
                logger.info(f"Retrieved {len(response.data)} versions for template ID: {template_id}")
                return response.data
            else:
                logger.info(f"No versions found for template ID: {template_id}")
                return []
        except Exception as e:
            logger.error(f"An error occurred while retrieving versions for template ID {template_id}: {e}", exc_info=True)
            return []

    async def create_template_version(self, version_data: dict):
        """
        Creates a new template version.

        Args:
            version_data: A dictionary containing the template version data.

        Returns:
            The created template version data if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            response = await client.from_('template_versions').insert(version_data).execute()
            if response.data:
                logger.info(f"Template version created with ID: {response.data[0].get('id')}")
                return response.data[0]
            else:
                logger.error(f"Supabase template version creation failed: {response.error.message if response.error else 'Unknown error'}")
                return None
        except Exception as e:
            logger.error(f"An error occurred while creating template version: {e}", exc_info=True)
            return None

    async def activate_template_version(self, version_id: str, template_id: str):
        """
        Sets a specific template version as active and deactivates others for the same template.

        Args:
            version_id: The ID of the template version to activate.
            template_id: The ID of the parent template.

        Returns:
            The activated template version data if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            # Deactivate all other versions for this template
            await client.from_('template_versions').update({'is_active': False}).eq('template_id', template_id).neq('id', version_id).execute()

            # Activate the specified version
            response = await client.from_('template_versions').update({'is_active': True}).eq('id', version_id).execute()

            if response.data:
                logger.info(f"Template version with ID {version_id} activated for template ID {template_id}.")
                return response.data[0]
            else:
                logger.error(f"Supabase template version activation failed for ID {version_id}: {response.error.message if response.error else 'Unknown error'}")
                return None
        except Exception as e:
            logger.error(f"An error occurred while activating template version with ID {version_id}: {e}", exc_info=True)
            return None

    async def add_favorite_template(self, user_id: str, template_id: str):
        """
        Adds a template to a user's favorites.

        Args:
            user_id: The ID of the user.
            template_id: The ID of the template to favorite.

        Returns:
            The created favorite data if successful, None otherwise.
        """
        client = await self.get_client()
        try:
            response = await client.from_('user_favorites').insert({
                'user_id': user_id,
                'template_id': template_id
            }).execute()
            if response.data:
                logger.info(f"Template {template_id} added to favorites for user {user_id}.")
                return response.data[0]
            else:
                logger.error(f"Supabase add favorite failed for user {user_id}, template {template_id}: {response.error.message if response.error else 'Unknown error'}")
                return None
        except Exception as e:
            logger.error(f"An error occurred while adding favorite for user {user_id}, template {template_id}: {e}", exc_info=True)
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
            response = await client.from_('user_favorites').delete().eq('user_id', user_id).eq('template_id', template_id).execute()
            if response.data:
                logger.info(f"Template {template_id} removed from favorites for user {user_id}.")
                return True
            else:
                logger.error(f"Supabase remove favorite failed for user {user_id}, template {template_id}: {response.error.message if response.error else 'Unknown error'}")
                return False
        except Exception as e:
            logger.error(f"An error occurred while removing favorite for user {user_id}, template {template_id}: {e}", exc_info=True)
            return False

    async def get_user_favorite_templates(self, user_id: str):
        """
        Retrieves a user's favorite templates.

        Args:
            user_id: The ID of the user.

        Returns:
            A list of favorite template dictionaries.
        """
        client = await self.get_client()
        try:
            # This assumes a join or relationship is set up in Supabase to get template details
            # If not, a separate query to the 'templates' table might be needed for each favorite
            response = await client.from_('user_favorites').select('*, templates(*)').eq('user_id', user_id).execute()
            if response.data:
                logger.info(f"Retrieved {len(response.data)} favorite templates for user {user_id}.")
                # Extract the nested template data
                favorite_templates = [item['templates'] for item in response.data if 'templates' in item and item['templates'] is not None]
                return favorite_templates
            else:
                logger.info(f"No favorite templates found for user {user_id}.")
                return []
        except Exception as e:
            logger.error(f"An error occurred while retrieving favorite templates for user {user_id}: {e}", exc_info=True)
            return []

    # Additional methods for other tables

# Example usage (can be removed later)
async def main():
    logging.basicConfig(level=logging.INFO)
    try:
        # Instantiate SupabaseManager and use its methods
        supabase_manager = SupabaseManager()
        client = await supabase_manager.get_client()
        # Example: List tables (requires admin privileges usually, use admin client)
        # admin_client = await supabase_manager.get_admin_client()
        # tables = await admin_client.table('pg_tables').select('tablename').execute()
        # print("Tables:", tables)
        print("Supabase client obtained successfully.")
    except Exception as e:
        print(f"Error getting Supabase client: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())