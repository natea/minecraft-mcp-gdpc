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

async def init_supabase_client() -> Optional[Client]:
    """
    Initializes the Supabase client using environment variables.

    Returns:
        An initialized AsyncClient instance, or None if configuration is missing.
    """
    global supabase_client
    if supabase_client:
        return supabase_client

    if not supabase_url or not supabase_key:
        logger.error("Supabase URL or Key not found in environment variables. Cannot initialize client.")
        return None

    try:
        logger.info(f"Initializing Supabase client for URL: {supabase_url[:20]}...") # Log partial URL
        # Standard Supabase client doesn't use await for creation
        supabase_client = create_client(supabase_url, supabase_key)
        logger.info("Supabase client initialized successfully.")
        return supabase_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}", exc_info=True)
        return None

async def get_supabase_client() -> Client:
    """
    Returns the initialized Supabase client instance. Initializes if not already done.

    Raises:
        Exception: If the client cannot be initialized.

    Returns:
        The initialized AsyncClient instance.
    """
    client = await init_supabase_client()
    if client is None:
        raise Exception("Supabase client could not be initialized. Check configuration.")
    return client

async def get_supabase_admin_client() -> Client:
    """
    Returns the initialized Supabase client instance using the service key for admin operations.

    Raises:
        Exception: If the client cannot be initialized or service key is missing.

    Returns:
        The initialized AsyncClient instance with admin privileges.
    """
    if not supabase_url or not supabase_service_key:
        logger.error("Supabase URL or Service Key not found in environment variables. Cannot initialize admin client.")
        raise Exception("Supabase URL or Service Key missing for admin client.")

    try:
        # Using standard Supabase client with service key
        logger.info("Initializing Supabase admin client...")
        admin_client = create_client(supabase_url, supabase_service_key)
        logger.info("Supabase admin client initialized successfully.")
        return admin_client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase admin client: {e}", exc_info=True)
        raise Exception("Supabase admin client could not be initialized.")


# Example usage (can be removed later)
async def main():
    logging.basicConfig(level=logging.INFO)
    try:
        client = await get_supabase_client()
        # Example: List tables (requires admin privileges usually, use admin client)
        # admin_client = await get_supabase_admin_client()
        # tables = await admin_client.table('pg_tables').select('tablename').execute()
        # print("Tables:", tables)
        print("Supabase client obtained successfully.")
    except Exception as e:
        print(f"Error getting Supabase client: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())