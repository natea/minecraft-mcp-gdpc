"""
API Router for server status and health checks.
"""

import logging
from fastapi import APIRouter, Request, HTTPException

from ..gdpc_interface import ConnectionManager, ConnectionError as GDPCConnectionError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", tags=["Status"], summary="Check server health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "ok"}


@router.get("/gdpc-status", tags=["Status"], summary="Check GDPC connection status")
async def gdpc_status(request: Request):
    """Checks the connection status to the Minecraft GDMC HTTP Interface."""
    conn_manager: ConnectionManager = request.app.state.gdpc_conn_manager

    if not conn_manager:
        logger.error("GDPC Connection Manager not initialized.")
        raise HTTPException(status_code=503, detail="GDPC connection manager not available.")

    try:
        version = conn_manager.get_server_version()
        if version:
            return {"status": "connected", "minecraft_version": version}
        else:
            # This case might happen if get_server_version returns None without raising ConnectionError
            logger.warning("GDPC connection test returned None, but no connection error was raised.")
            raise HTTPException(status_code=503, detail="GDPC connection failed or returned unexpected data.")
    except GDPCConnectionError as e:
        logger.error(f"GDPC connection failed: {e}")
        raise HTTPException(status_code=503, detail=f"GDPC connection failed: {e}")
    except Exception as e:
        logger.error(f"Unexpected error checking GDPC status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")