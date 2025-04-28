import pytest
from fastapi.testclient import TestClient
import uuid
import time

# Store user credentials and token globally within the module for sequential tests
# Note: This approach is simpler but less robust than using fixtures for full isolation.
# A fixture-based approach would create/delete users per test.
test_user_email = ""
test_user_password = "testpassword123" # Keep password simple for tests
access_token = ""

def generate_unique_email():
    """Generates a unique email address using a timestamp and UUID."""
    return f"testuser_{int(time.time())}_{uuid.uuid4().hex[:6]}@example.com"

from src.main import app # Assuming your FastAPI app instance is in main.py

from unittest.mock import AsyncMock, patch, MagicMock # Import MagicMock

# Mock the get_client dependency
@pytest.fixture
def mock_get_client():
    # Create a properly structured mock Supabase client
    mock_client = MagicMock()
    
    # --- Mock auth.sign_up ---
    mock_signup_response = MagicMock()
    mock_signup_user = MagicMock()
    mock_signup_user.id = "test_user_id"
    # Use a string value instead of a MagicMock
    mock_signup_user.email = ""  # Will be set dynamically
    mock_signup_user.user_metadata = {"username": "testuser"}
    mock_signup_user.created_at = "2023-01-01T00:00:00+00:00"
    
    mock_signup_session = MagicMock()
    mock_signup_session.access_token = "mock_access_token"
    
    mock_signup_response.user = mock_signup_user
    mock_signup_response.session = mock_signup_session
    
    # Configure sign_up to return the mock response
    mock_client.auth.sign_up = MagicMock(return_value=mock_signup_response)
    
    # --- Mock auth.sign_in_with_password ---
    mock_signin_response = MagicMock()
    mock_signin_user = MagicMock()
    mock_signin_user.id = "test_user_id"
    mock_signin_user.email = ""  # Will be set dynamically as string
    mock_signin_user.user_metadata = {"username": "testuser"}
    mock_signin_user.created_at = "2023-01-01T00:00:00+00:00"
    
    mock_signin_session = MagicMock()
    mock_signin_session.access_token = "mock_access_token"
    
    mock_signin_response.user = mock_signin_user
    mock_signin_response.session = mock_signin_session
    
    # Configure sign_in_with_password to return the mock response with dynamic email
    def sign_in_side_effect(data):
        global access_token
        # Set the email dynamically to match the requested email
        mock_signin_user.email = data.get("email")
        # Check for wrong password
        if data.get("password") != test_user_password:
            from gotrue.errors import AuthApiError
            raise AuthApiError(message="Invalid login credentials", status=401, code="invalid_credentials")
        # Set the global access_token upon successful login
        access_token = mock_signin_session.access_token
        return mock_signin_response
    
    mock_client.auth.sign_in_with_password = MagicMock(side_effect=sign_in_side_effect)
    
    # --- Mock auth.get_user ---
    mock_user_response = MagicMock()
    mock_user = MagicMock()
    mock_user.id = "test_user_id"
    # Use the same email as the sign-in user
    mock_user.email = mock_signin_user.email
    mock_user.user_metadata = {"username": "testuser"}
    mock_user.created_at = "2023-01-01T00:00:00+00:00"
    
    mock_user_response.user = mock_user
    
    # Configure get_user to return the mock response or raise error for invalid token
    def get_user_side_effect(token):
        if token == "invalidtoken123":
            from gotrue.errors import AuthApiError
            raise AuthApiError(message="Invalid token", status=401, code="invalid_token")
        # Set the email dynamically to match the registered user's email
        mock_user.email = test_user_email
        return mock_user_response
    
    mock_client.auth.get_user = MagicMock(side_effect=get_user_side_effect)
    
    # Configure auth.sign_up to raise AuthApiError for duplicate email test
    def sign_up_side_effect(data):
        global test_user_email
        # Check if test_user_email is already set (meaning a user was registered in a previous test)
        if test_user_email and data.get("email") == test_user_email:
            from gotrue.errors import AuthApiError
            raise AuthApiError(message="User already registered", status=409, code="23505")
        # Set the global test_user_email upon successful registration
        test_user_email = data.get("email")
        mock_signup_user.email = test_user_email
        return mock_signup_response
    
    # Store the original function
    original_sign_up = mock_client.auth.sign_up
    mock_client.auth.sign_up.side_effect = sign_up_side_effect
    
    return mock_client

# Override the get_client dependency for auth tests
@pytest.fixture(autouse=True)
def override_get_client(mock_get_client):
    from src.api import auth_router
    app.dependency_overrides[auth_router.get_client] = lambda: mock_get_client
    yield
    app.dependency_overrides.clear() # Clear overrides after each test

def test_register_user(api_client: TestClient):
    """
    Tests user registration via the /auth/register endpoint.
    """
    global test_user_email
    # Generate a unique email for this registration attempt
    current_test_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    print(f"Attempting to register user: {current_test_email}")

    response = api_client.post(
        "/v1/auth/register",
        json={"email": current_test_email, "password": test_user_password, "username": f"testuser_{uuid.uuid4().hex[:6]}"},
    )

    print(f"Register response status: {response.status_code}")
    try:
        print(f"Register response JSON: {response.json()}")
    except Exception:
        print(f"Register response text: {response.text}")

    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
    data = response.json()
    # The mock should set test_user_email upon successful registration
    assert data["user"]["email"] == current_test_email
    assert "id" in data["user"]
    assert "password" not in data["user"] # Ensure password is not returned
    print(f"Successfully registered user: {current_test_email}")


def test_register_duplicate_user(api_client: TestClient):
    """
    Tests attempting to register a user with an email that already exists.
    Depends on test_register_user having run first.
    """
    assert test_user_email, "test_user_email not set, previous test might have failed."
    print(f"Attempting to register duplicate user: {test_user_email}")

    response = api_client.post(
        "/v1/auth/register",
        json={"email": test_user_email, "password": test_user_password, "username": f"testuser_{uuid.uuid4().hex[:6]}"},
    )
    assert response.status_code == 409 # Expect Conflict for duplicate user
    data = response.json()
    assert "detail" in data
    # Check for a specific error message if Supabase/API provides one consistently
    # assert "already registered" in data["detail"].lower()
    print(f"Successfully tested duplicate registration prevention for: {test_user_email}")


def test_login_user(api_client: TestClient):
    """
    Tests user login via the /auth/login endpoint.
    Depends on test_register_user having run first.
    """
    global access_token
    assert test_user_email, "test_user_email not set, previous test might have failed."
    print(f"Attempting to log in user: {test_user_email}")

    response = api_client.post(
        "/v1/auth/login",
        json={"email": test_user_email, "password": test_user_password},
    )

    print(f"Login response status: {response.status_code}")
    try:
        print(f"Login response JSON: {response.json()}")
    except Exception:
        print(f"Login response text: {response.text}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"].lower() == "bearer"
    access_token = data["access_token"] # Store token for the next test
    assert access_token, "Access token was not received or is empty."
    print(f"Successfully logged in user: {test_user_email}")


def test_login_incorrect_password(api_client: TestClient):
    """
    Tests user login with an incorrect password.
    Depends on test_register_user having run first.
    """
    assert test_user_email, "test_user_email not set, previous test might have failed."
    print(f"Attempting to log in user with incorrect password: {test_user_email}")

    response = api_client.post(
        "/v1/auth/login",
        json={"email": test_user_email, "password": "wrongpassword"},
    )
    assert response.status_code == 401 # Expect Unauthorized
    data = response.json()
    assert "detail" in data
    # assert "Incorrect email or password" in data["detail"] # Or specific error
    print(f"Successfully tested incorrect password login for: {test_user_email}")


def test_get_user_details(api_client: TestClient):
    """
    Tests retrieving user details via the /auth/user endpoint using the access token.
    Depends on test_login_user having run first.
    """
    assert access_token, "Access token not set, previous login test might have failed."
    print(f"Attempting to get user details for: {test_user_email}")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = api_client.get("/v1/auth/user", headers=headers)

    print(f"Get user response status: {response.status_code}")
    try:
        print(f"Get user response JSON: {response.json()}")
    except Exception:
        print(f"Get user response text: {response.text}")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert data["email"] == test_user_email
    assert "id" in data
    assert "password" not in data # Ensure password is not returned
    print(f"Successfully retrieved user details for: {test_user_email}")


def test_get_user_details_no_token(api_client: TestClient):
    """
    Tests retrieving user details without providing an access token.
    """
    print("Attempting to get user details without token.")
    response = api_client.get("/v1/auth/user")
    assert response.status_code == 401 # Expect Unauthorized
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Not authenticated"
    print("Successfully tested getting user details without token.")


def test_get_user_details_invalid_token(api_client: TestClient):
    """
    Tests retrieving user details with an invalid access token.
    """
    print("Attempting to get user details with invalid token.")
    headers = {"Authorization": "Bearer invalidtoken123"}
    response = api_client.get("/v1/auth/user", headers=headers)
    assert response.status_code == 401 # Expect Unauthorized
    data = response.json()
    assert "detail" in data
    # The specific error might vary depending on Supabase/FastAPI handling
    # assert "Invalid token" in data["detail"] or "Not authenticated" in data["detail"]
    print("Successfully tested getting user details with invalid token.")