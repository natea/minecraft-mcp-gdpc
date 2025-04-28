"""
Supabase client initialization module.
"""

import logging
import os
from typing import Optional

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