"""
API Router for user authentication (registration, login).
"""

import logging
from fastapi import APIRouter, Request, HTTPException, status, Depends
from supabase import Client
from gotrue.errors import AuthApiError

from .models import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    UserResponse,
    ErrorResponse,
)
from ..supabase_api import SupabaseManager

logger = logging.getLogger(__name__)

router = APIRouter(
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_409_CONFLICT: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse},
    }
)

# --- Helper to get Supabase client ---
# Using Depends for dependency injection in endpoints
async def get_client(request: Request) -> Client:
    """Dependency to get the Supabase client instance."""
    # Access the Supabase client instance stored in the app state
    supabase_client: Client = request.app.state.supabase_client
    if supabase_client is None:
        logger.error("Supabase client not initialized.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": {"code": "SUPABASE_CLIENT_UNAVAILABLE", "message": "Supabase client not available."}}
        )
    return supabase_client

# --- Authentication Endpoints ---

@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register_user(
    user_data: UserRegisterRequest,
    supabase: Client = Depends(get_client)
):
    """Registers a new user with email, password, and username."""
    try:
        # Supabase sign_up requires email and password.
        # Username is typically stored in user_metadata or a separate profiles table.
        res = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            # Store username in user_metadata during signup
            "options": {"data": {"username": user_data.username}}
        })

        if res.user is None or res.session is None:
             # Handle cases where signup might succeed but user/session is null (e.g., email verification required)
             logger.warning(f"Signup for {user_data.email} succeeded but user/session is null. Email verification might be required.")
             # Depending on flow, might return a specific message or raise an error
             raise HTTPException(
                 status_code=status.HTTP_200_OK, # Or 202 Accepted if verification needed
                 detail={"message": "Registration successful. Please check your email for verification."}
             )

        # Assuming immediate login after signup for this example
        user_resp = UserResponse(
            id=str(res.user.id),
            email=res.user.email,
            username=res.user.user_metadata.get("username", ""), # Retrieve username
            created_at=str(res.user.created_at)
        )
        return AuthResponse(user=user_resp, access_token=res.session.access_token)

    except AuthApiError as e:
        logger.error(f"Supabase registration error for {user_data.email}: {e.message}")
        status_code = status.HTTP_400_BAD_REQUEST
        error_code = "REGISTRATION_FAILED"
        if "already registered" in e.message.lower():
            status_code = status.HTTP_409_CONFLICT
            error_code = "EMAIL_EXISTS"
        elif "weak password" in e.message.lower():
             error_code = "WEAK_PASSWORD"

        raise HTTPException(
            status_code=status_code,
            detail={"error": {"code": error_code, "message": e.message}}
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration for {user_data.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred during registration."}}
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Login a user",
)
async def login_user(
    login_data: UserLoginRequest,
    supabase: Client = Depends(get_client)
):
    """Logs in a user with email and password."""
    try:
        res = supabase.auth.sign_in_with_password({
            "email": login_data.email,
            "password": login_data.password,
        })

        if res.user is None or res.session is None:
             logger.error(f"Login failed for {login_data.email}: User or session is null.")
             raise HTTPException(
                 status_code=status.HTTP_401_UNAUTHORIZED,
                 detail={"error": {"code": "LOGIN_FAILED", "message": "Login failed, user or session data missing."}}
             )

        # Fetch username from metadata or profiles table if needed
        username = res.user.user_metadata.get("username", "")
        # If username isn't in metadata, you might need another query:
        # profile = await supabase.table('user_profiles').select('username').eq('id', res.user.id).single().execute()
        # username = profile.data.get('username', '') if profile.data else ""

        user_resp = UserResponse(
            id=str(res.user.id),
            email=res.user.email,
            username=username,
            created_at=str(res.user.created_at)
        )
        return AuthResponse(user=user_resp, access_token=res.session.access_token)

    except AuthApiError as e:
        logger.error(f"Supabase login error for {login_data.email}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": e.message}}
        )
    except Exception as e:
        logger.error(f"Unexpected error during login for {login_data.email}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": {"code": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred during login."}}
        )

# --- Placeholder for JWT Dependency and /user endpoint ---
# Actual JWT validation logic needs to be implemented here
# This is a simplified placeholder
async def get_current_user(request: Request, supabase: 'Client' = Depends(get_client)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = auth_header.split(" ")[1]
    try:
        user_response = supabase.auth.get_user(token)
        if user_response.user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or user not found")
        return user_response.user
    except AuthApiError as e:
         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Authentication error: {e.message}")
    except Exception as e:
         logger.error(f"Error validating token: {e}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not validate credentials")


@router.get(
    "/user",
    response_model=UserResponse,
    summary="Get current user details",
    dependencies=[Depends(get_current_user)], # Protect this endpoint
)
async def read_users_me(current_user = Depends(get_current_user)):
    """Returns the details of the currently authenticated user."""
    # Fetch username from metadata or profiles table if needed
    username = current_user.user_metadata.get("username", "")
    # profile = await supabase.table('user_profiles').select('username').eq('id', current_user.id).single().execute()
    # username = profile.data.get('username', '') if profile.data else ""

    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        username=username,
        created_at=str(current_user.created_at)
    )