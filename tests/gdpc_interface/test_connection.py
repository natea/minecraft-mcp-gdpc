import importlib # Add importlib for reloading
import logging
import os
import pytest
from unittest.mock import patch, MagicMock, ANY
from functools import partial

# Import the module to test
from src.gdpc_interface.connection import ConnectionManager
from gdpc_interface.connection import ConnectionManager # Remove DEFAULT_HOST, DEFAULT_PORT import
from gdpc.exceptions import InterfaceConnectionError
from gdpc import interface # Import for patching

# Mock the gdpc interface functions used by ConnectionManager
# We need to patch them where they are looked up (in the connection module)
@pytest.fixture(autouse=True)
def mock_gdpc_interface():
    """Automatically mock gdpc.interface functions for all tests."""
    with patch('src.gdpc_interface.connection.interface.getVersion', return_value="1.18.2") as mock_get_version, \
         patch('src.gdpc_interface.connection.interface.getBuildArea', return_value={'xFrom': 0, 'yFrom': 0, 'zFrom': 0, 'xTo': 10, 'yTo': 10, 'zTo': 10}) as mock_get_build_area, \
         patch('src.gdpc_interface.connection.interface.getPlayers', return_value={"Player1": {"position": [0, 64, 0]}}) as mock_get_players, \
         patch('src.gdpc_interface.connection.interface.getBlocks', return_value=["minecraft:stone"]) as mock_get_blocks, \
         patch('src.gdpc_interface.connection.interface.placeBlocks', return_value="ok") as mock_place_blocks, \
         patch('src.gdpc_interface.connection.interface.runCommand', return_value="ok") as mock_run_command:
        # Yield the mocks if needed, though often just patching is enough
        yield {
            "getVersion": mock_get_version,
            "getBuildArea": mock_get_build_area,
            "getPlayers": mock_get_players,
            "getBlocks": mock_get_blocks,
            "placeBlocks": mock_place_blocks,
            "runCommand": mock_run_command,
        }

# Test ConnectionManager Initialization
def test_connection_manager_init_defaults():
    """Test initialization with default host/port (no env vars)."""
    with patch('src.gdpc_interface.connection.os.getenv') as mock_getenv:
        mock_getenv.side_effect = lambda key, default: default # Simulate no env vars set
        # Patch getLogger to return our mock logger instance
        mock_logger_instance = MagicMock()
        mock_logger_instance.level = logging.DEBUG
        with patch('src.gdpc_interface.connection.logging.getLogger') as mock_getLogger:
            mock_getLogger.return_value = mock_logger_instance
            # Reload the connection module to ensure it uses the patched logger
            from src.gdpc_interface import connection # Import the module to reload
            importlib.reload(connection)
            # Import ConnectionManager *after* reload
            from src.gdpc_interface.connection import ConnectionManager
            manager = ConnectionManager()
            assert manager.host == "localhost" # Assuming default if not in env
            assert manager.port == 9000       # Assuming default if not in env
            # Assert on the specific mock instance
            mock_logger_instance.info.assert_called_once_with(f"GDPC Interface configured for localhost:9000")
            # Check if partials are created (basic check)
            assert isinstance(manager.get_version, partial)
            assert manager.get_version.func == interface.getVersion
            assert manager.get_version.args == ("localhost", 9000)

def test_connection_manager_init_explicit():
    """Test initialization with explicit host/port."""
    mock_logger_instance = MagicMock()
    mock_logger_instance.level = logging.DEBUG
    with patch('src.gdpc_interface.connection.logging.getLogger') as mock_getLogger:
        mock_getLogger.return_value = mock_logger_instance
        # Reload the connection module
        from src.gdpc_interface import connection
        importlib.reload(connection)
        from src.gdpc_interface.connection import ConnectionManager
        manager = ConnectionManager(host="192.168.1.100", port=12345)
        assert manager.host == "192.168.1.100"
        assert manager.port == 12345
        mock_logger_instance.info.assert_called_once_with(f"GDPC Interface configured for 192.168.1.100:12345")
        assert manager.get_version.args == ("192.168.1.100", 12345)

@patch.dict(os.environ, {"MINECRAFT_HOST": "env.host", "MINECRAFT_HTTP_PORT": "9999"})
def test_connection_manager_init_env_vars():
    """Test initialization with environment variables set."""
    # Need to reload the module or patch the constants if they are set at import time
    # Easier to patch os.getenv directly within the test scope
    with patch('src.gdpc_interface.connection.os.getenv') as mock_getenv:
        # Define the side effect based on the key
        def getenv_side_effect(key, default=None):
            if key == "MINECRAFT_HOST":
                return "env.host"
            elif key == "MINECRAFT_HTTP_PORT":
                return "9999"
            return default
        mock_getenv.side_effect = getenv_side_effect

        mock_logger_instance = MagicMock()
        mock_logger_instance.level = logging.DEBUG
        with patch('src.gdpc_interface.connection.logging.getLogger') as mock_getLogger:
            mock_getLogger.return_value = mock_logger_instance
            # Reload the connection module
            from src.gdpc_interface import connection
            importlib.reload(connection)
            from src.gdpc_interface.connection import ConnectionManager
            manager = ConnectionManager() # Should now pick up mocked env vars
            assert manager.host == "env.host"
            assert manager.port == 9999
            # Assert on the specific mock instance
            mock_logger_instance.info.assert_called_once_with(f"GDPC Interface configured for env.host:9999")
            assert manager.get_version.args == ("env.host", 9999)


# Test ConnectionManager Methods
def test_test_connection_success(mock_gdpc_interface):
    """Test test_connection successful case."""
    # manager = ConnectionManager() # Move instantiation inside the patch block
    mock_gdpc_interface["getVersion"].return_value = "1.19" # Ensure mock returns something
    mock_logger_instance = MagicMock()
    mock_logger_instance.level = logging.DEBUG
    with patch('src.gdpc_interface.connection.logging.getLogger') as mock_getLogger:
        mock_getLogger.return_value = mock_logger_instance
        # Reload module and re-instantiate manager
        from src.gdpc_interface import connection
        importlib.reload(connection)
        from src.gdpc_interface.connection import ConnectionManager
        manager = ConnectionManager() # Instantiate *after* reload
        result = manager.test_connection()
        assert result is True
        mock_gdpc_interface["getVersion"].assert_called_once()
        # Check that the success message was logged, allowing for the init message too
        mock_logger_instance.info.assert_any_call("Successfully connected to Minecraft server. Version: 1.19")
        mock_logger_instance.error.assert_not_called() # Use the correct mock instance

def test_test_connection_connection_error(mock_gdpc_interface):
    """Test test_connection with InterfaceConnectionError."""
    # manager = ConnectionManager() # Move instantiation inside the patch block
    mock_gdpc_interface["getVersion"].side_effect = InterfaceConnectionError("Connection refused")
    mock_logger_instance = MagicMock()
    mock_logger_instance.level = logging.DEBUG
    with patch('src.gdpc_interface.connection.logging.getLogger') as mock_getLogger:
        mock_getLogger.return_value = mock_logger_instance
        # Reload module and re-instantiate manager
        from src.gdpc_interface import connection
        importlib.reload(connection)
        from src.gdpc_interface.connection import ConnectionManager
        manager = ConnectionManager() # Instantiate *after* reload
        result = manager.test_connection()
        assert result is False
        mock_gdpc_interface["getVersion"].assert_called_once()
        mock_logger_instance.error.assert_called_once_with(f"Failed to connect to Minecraft server at {manager.host}:{manager.port}: Connection refused")
        # No need to assert info not called, as init logs info. Focus on error log.

def test_test_connection_generic_error(mock_gdpc_interface):
    """Test test_connection with a generic Exception."""
    # manager = ConnectionManager() # Move instantiation inside the patch block
    mock_gdpc_interface["getVersion"].side_effect = Exception("Something went wrong")
    mock_logger_instance = MagicMock()
    mock_logger_instance.level = logging.DEBUG
    with patch('src.gdpc_interface.connection.logging.getLogger') as mock_getLogger:
        mock_getLogger.return_value = mock_logger_instance
        # Reload module and re-instantiate manager
        from src.gdpc_interface import connection
        importlib.reload(connection)
        from src.gdpc_interface.connection import ConnectionManager
        manager = ConnectionManager() # Instantiate *after* reload
        result = manager.test_connection()
        assert result is False
        mock_gdpc_interface["getVersion"].assert_called_once()
        mock_logger_instance.error.assert_called_once_with(f"An unexpected error occurred during connection test: Something went wrong")
        # No need to assert info not called, as init logs info. Focus on error log.

def test_get_server_version_success(mock_gdpc_interface):
    """Test get_server_version successful case."""
    manager = ConnectionManager()
    mock_gdpc_interface["getVersion"].return_value = "1.20"
    version = manager.get_server_version()
    assert version == "1.20"
    mock_gdpc_interface["getVersion"].assert_called_once()

def test_get_server_version_connection_error(mock_gdpc_interface):
    """Test get_server_version with InterfaceConnectionError."""
    # manager = ConnectionManager() # Move instantiation inside the patch block
    mock_gdpc_interface["getVersion"].side_effect = InterfaceConnectionError("Timeout")
    mock_logger_instance = MagicMock()
    mock_logger_instance.level = logging.DEBUG
    with patch('src.gdpc_interface.connection.logging.getLogger') as mock_getLogger:
        mock_getLogger.return_value = mock_logger_instance
        # Reload module and re-instantiate manager
        from src.gdpc_interface import connection
        importlib.reload(connection)
        from src.gdpc_interface.connection import ConnectionManager
        manager = ConnectionManager() # Instantiate *after* reload
        version = manager.get_server_version()
        assert version is None
        mock_gdpc_interface["getVersion"].assert_called_once()
        mock_logger_instance.error.assert_called_once_with(f"Connection error getting server version: Timeout")

def test_get_server_version_generic_error(mock_gdpc_interface):
    """Test get_server_version with a generic Exception."""
    # manager = ConnectionManager() # Move instantiation inside the patch block
    mock_gdpc_interface["getVersion"].side_effect = Exception("Bad response")
    mock_logger_instance = MagicMock()
    mock_logger_instance.level = logging.DEBUG
    with patch('src.gdpc_interface.connection.logging.getLogger') as mock_getLogger:
        mock_getLogger.return_value = mock_logger_instance
        # Reload module and re-instantiate manager
        from src.gdpc_interface import connection
        importlib.reload(connection)
        from src.gdpc_interface.connection import ConnectionManager
        manager = ConnectionManager() # Instantiate *after* reload
        version = manager.get_server_version()
        assert version is None
        mock_gdpc_interface["getVersion"].assert_called_once()
        mock_logger_instance.error.assert_called_once_with(f"Unexpected error getting server version: Bad response")