"""
API Router for server status and health checks.
"""

import logging
from fastapi import APIRouter, Request, HTTPException, status

from ..gdpc_interface import ConnectionManager, ConnectionError as GDPCConnectionError
from .models import HealthStatus, GDPCStatus, ErrorResponse # Import models

logger = logging.getLogger(__name__)
router = APIRouter(
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
        status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse},
    }
)


@router.get(
    "/health",
    tags=["Status"],
    summary="Check server health",
    response_model=HealthStatus, # Use response model
)
async def health_check():
    """Basic health check endpoint."""
    return HealthStatus(status="ok")


@router.get(
    "/gdpc-status",
    tags=["Status"],
    summary="Check GDPC connection status",
    response_model=GDPCStatus, # Use response model
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {"model": ErrorResponse}}, # Specific error response
)
async def gdpc_status(request: Request):
    """Checks the connection status to the Minecraft GDMC HTTP Interface."""
    conn_manager: ConnectionManager = request.app.state.gdpc_conn_manager

    if not conn_manager:
        logger.error("GDPC Connection Manager not initialized.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": {"code": "GDPC_MANAGER_UNAVAILABLE", "message": "GDPC connection manager not available."}}
        )

    try:
        version = conn_manager.get_server_version()
        if version:
            return GDPCStatus(status="connected", minecraft_version=version)
        else:
            # This case might happen if get_server_version returns None without raising ConnectionError
            logger.warning("GDPC connection test returned None, but no connection error was raised.")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={"error": {"code": "GDPC_UNEXPECTED_RESPONSE", "message": "GDPC connection failed or returned unexpected data."}}
            )
    except GDPCConnectionError as e:
        logger.error(f"GDPC connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": {"code": "GDPC_CONNECTION_FAILED", "message": f"GDPC connection failed: {e}"}}
        )
    except Exception as e:
        logger.error(f"Unexpected error checking GDPC status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_SERVER_ERROR", "message": f"An unexpected error occurred: {e}"}}
        )