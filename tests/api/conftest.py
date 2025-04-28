import pytest
from fastapi.testclient import TestClient
import os
from dotenv import load_dotenv
import sys

# Add project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added project root to sys.path: {project_root}")

# Load environment variables from a .env.test file if it exists
# This allows overriding Supabase credentials for testing
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env.test')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path, override=True)
    print(f"Loaded test environment variables from: {dotenv_path}")
else:
    # Fallback to .env or system environment variables if .env.test is not found
    load_dotenv(override=True) # Load from default .env or system vars
    print("Attempted to load environment variables from default locations (.env or system).")
    import os
    print(f"SUPABASE_URL after loading: {os.getenv('SUPABASE_URL')}")
    print(f"SUPABASE_KEY after loading: {os.getenv('SUPABASE_KEY')}")


# Import the FastAPI app *after* loading environment variables
# to ensure Supabase client uses the correct (potentially overridden) credentials
import importlib

# Use importlib to dynamically import the app
try:
    main_module = importlib.import_module("src.main")
    app = main_module.app
except ImportError as e:
    print(f"Error importing app from src.main: {e}")
    # Handle the error appropriately, maybe raise it or set app to None
    app = None # Set app to None to allow collection to proceed and fail tests gracefully

@pytest.fixture(scope="function") # Change scope to function
def api_client():
    """
    Provides a FastAPI TestClient instance for making requests to the API.
    Scope is 'function' to ensure a fresh client for each test.
    """
    with TestClient(app) as client:
        print("TestClient created.")
        # You could add setup logic here if needed, e.g.,
        # - Ensuring the test database is clean
        # - Seeding initial data
        yield client
        # Teardown logic can go here, e.g., cleaning up test data
        print("TestClient teardown.")

# Example fixture to potentially mock GDPC connection if needed later
# @pytest.fixture
# def mock_gdpc_connection(mocker):
#     mock = mocker.patch('src.gdpc_interface.connection.GDPCConnection')
#     mock.return_value.is_connected.return_value = True # Example mock behavior
#     return mock