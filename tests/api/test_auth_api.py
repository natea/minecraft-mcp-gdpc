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
    mock_client = MagicMock()
    
    # Mock the auth methods used in auth_router
    mock_client = MagicMock()

    # Mock the return value of sign_up
    mock_signup_response = MagicMock()
    mock_signup_response.user = MagicMock()
    mock_signup_response.user.id = "test_user_id"
    mock_signup_response.user.email = "test@example.com"
    mock_signup_response.user.user_metadata = {"username": "testuser"}
    mock_signup_response.user.created_at = "2023-01-01T00:00:00+00:00"
    mock_signup_response.session = MagicMock()
    mock_signup_response.session.access_token = "mock_access_token"

    mock_client.auth.sign_up = MagicMock(return_value=mock_signup_response) # Use MagicMock directly

    # Mock the return value of sign_in_with_password
    mock_signin_response = MagicMock()
    mock_signin_response.user = MagicMock()
    mock_signin_response.user.id = "test_user_id"
    mock_signin_response.user.email = "test@example.com"
    mock_signin_response.user.user_metadata = {"username": "testuser"}
    mock_signin_response.user.created_at = "2023-01-01T00:00:00+00:00"
    mock_signin_response.session = MagicMock()
    mock_signin_response.session.access_token = "mock_access_token"

    mock_client.auth.sign_in_with_password = MagicMock(return_value=mock_signin_response) # Use MagicMock directly

    # Mock the get_user method within the mocked Supabase client (not async)
    mock_client.auth.get_user = MagicMock()

    # Mock the return value of get_user to have a user_metadata attribute
    mock_user = MagicMock()
    mock_user.id = "test_user_id"
    mock_user.email = "test@example.com"
    mock_user.user_metadata = {"username": "testuser"}
    mock_user.created_at = "2023-01-01T00:00:00+00:00" # Add created_at

    mock_user_response = MagicMock()
    mock_user_response.user = mock_user

    mock_client.auth.get_user.return_value = mock_user_response

    return mock_client # Return the mock client for dependency override

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
    # Use a simpler email format for testing
    test_user_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    print(f"Attempting to register user: {test_user_email}")

    response = api_client.post(
        "/v1/auth/register",
        json={"email": test_user_email, "password": test_user_password, "username": f"testuser_{uuid.uuid4().hex[:6]}"},
    )

    print(f"Register response status: {response.status_code}")
    try:
        print(f"Register response JSON: {response.json()}")
    except Exception:
        print(f"Register response text: {response.text}")


    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.text}"
    data = response.json()
    assert data["user"]["email"] == test_user_email
    assert "id" in data["user"]
    assert "password" not in data["user"] # Ensure password is not returned
    print(f"Successfully registered user: {test_user_email}")


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