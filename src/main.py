"""
Main application file for the FastMCP server.
Initializes the FastAPI application and includes routers.
"""

import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables from .env file
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

# --- Application Setup ---
app = FastAPI(
    title="Minecraft MCP Server",
    description="API server for programmatic Minecraft world manipulation using GDPC.",
    version="0.1.0",
    # Add other FastAPI configurations like docs_url, redoc_url if needed
)

# --- Middleware ---
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Exception Handlers ---
# Example: Generic exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception for request {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )

# --- Routers ---
# Import and include API routers
from .api import status_router, auth_router # Import auth_router
# from .api import world_router, template_router # Placeholder for future routers

app.include_router(status_router.router, prefix="/v1", tags=["Status"]) # Add status router
from .api import template_router # Import template_router

app.include_router(template_router.router, prefix="/v1/templates", tags=["Templates"])
app.include_router(auth_router.router, prefix="/v1/auth", tags=["Authentication"]) # Add auth router
# app.include_router(world_router.router, prefix="/v1/worlds", tags=["Worlds"])
# app.include_router(template_router.router, prefix="/v1/templates", tags=["Templates"])

# --- Root Endpoint ---
# Keep the root endpoint for basic accessibility check
@app.get("/", include_in_schema=False) # Exclude from OpenAPI docs if desired
async def read_root():
    """Root endpoint providing basic server status."""
    return {"status": "ok", "message": "Welcome to the Minecraft MCP Server!"}

# --- Startup and Shutdown Events ---
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Minecraft MCP Server...")
    # Initialize resources like database connections, GDPC connection manager, Supabase client, etc.

    # Initialize GDPC Connection Manager
    try:
        from .gdpc_interface import ConnectionManager
        app.state.gdpc_conn_manager = ConnectionManager()
        if not app.state.gdpc_conn_manager.test_connection():
            logger.warning("Failed to connect to Minecraft server on startup. Check server status and configuration.")
        else:
            logger.info("GDPC Connection Manager initialized and connection tested successfully.")
    except ImportError:
        logger.error("Could not import ConnectionManager. Ensure gdpc_interface package is correctly structured.")
        app.state.gdpc_conn_manager = None
    except Exception as e:
        logger.error(f"Error initializing GDPC Connection Manager: {e}", exc_info=True)
        app.state.gdpc_conn_manager = None

    # Initialize Supabase Client
    try:
        from .supabase.client import init_supabase_client
        app.state.supabase_client = await init_supabase_client()
        if app.state.supabase_client is None:
             logger.warning("Failed to initialize Supabase client. Check environment variables (SUPABASE_URL, SUPABASE_KEY).")
        else:
             logger.info("Supabase client initialized successfully.")
    except ImportError:
        logger.error("Could not import init_supabase_client. Ensure supabase package is correctly structured.")
        app.state.supabase_client = None
    except Exception as e:
        logger.error(f"Error initializing Supabase client: {e}", exc_info=True)
        app.state.supabase_client = None

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Minecraft MCP Server...")
    # Clean up resources
    pass

# --- Main Execution ---
if __name__ == "__main__":
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    RELOAD = os.getenv("ENVIRONMENT", "development") == "development"

    logger.info(f"Starting server on {HOST}:{PORT} (Reload: {RELOAD})")
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level=LOG_LEVEL.lower(),
    )