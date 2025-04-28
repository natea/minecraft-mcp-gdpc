import pytest
from unittest.mock import MagicMock, patch, ANY

from gdpc.vector_tools import ivec3, Box, Rect, Vec3iLike
from gdpc.exceptions import InterfaceConnectionError

# Import the module and class to test
from src.gdpc_interface.connection import ConnectionManager # Needed for type hint and fixture
from src.gdpc_interface.world_operations import WorldOperations, PlayerInfo

# Fixture for a mocked ConnectionManager (similar to other test files)
@pytest.fixture
def mock_conn_manager():
    """Provides a MagicMock instance of ConnectionManager."""
    mock = MagicMock(spec=ConnectionManager)
    mock.host = "mockhost"
    mock.port = 9000
    # Mock the specific methods used by WorldOperations from ConnectionManager
    mock.get_build_area = MagicMock()
    mock.get_players = MagicMock()
    # Note: getHeightmap is called directly from gdpc.interface, not ConnectionManager
    return mock

# Fixture for WorldOperations instance with mocked connection
@pytest.fixture
def world_ops(mock_conn_manager):
    """Provides a WorldOperations instance initialized with the mock ConnectionManager."""
    return WorldOperations(mock_conn_manager)

# Test Initialization
def test_world_operations_init(mock_conn_manager):
    """Test WorldOperations initialization."""
    with patch('src.gdpc_interface.world_operations.logger') as mock_logger:
        ops = WorldOperations(mock_conn_manager)
        assert ops.conn == mock_conn_manager
        mock_logger.info.assert_called_once_with("WorldOperations initialized.")

# Test get_build_area
def test_get_build_area_success(world_ops, mock_conn_manager):
    """Test get_build_area successful case."""
    raw_build_area = {'xFrom': 10, 'yFrom': 0, 'zFrom': 20, 'xTo': 110, 'yTo': 100, 'zTo': 120}
    mock_conn_manager.get_build_area.return_value = raw_build_area

    expected_box = Box(offset=(10, 0, 20), size=(100, 100, 100)) # size = to - from
    box = world_ops.get_build_area()

    assert box == expected_box
    mock_conn_manager.get_build_area.assert_called_once()

def test_get_build_area_empty_result(world_ops, mock_conn_manager):
    """Test get_build_area when the underlying call returns None or empty."""
    mock_conn_manager.get_build_area.return_value = None
    assert world_ops.get_build_area() is None

    mock_conn_manager.get_build_area.return_value = {}
    assert world_ops.get_build_area() is None # Should handle missing keys gracefully

def test_get_build_area_connection_error(world_ops, mock_conn_manager):
    """Test get_build_area with InterfaceConnectionError."""
    mock_conn_manager.get_build_area.side_effect = InterfaceConnectionError("Failed to fetch")
    with patch('src.gdpc_interface.world_operations.logger') as mock_logger:
        box = world_ops.get_build_area()
        assert box is None
        mock_logger.error.assert_called_once_with("Connection error getting build area: Failed to fetch")

def test_get_build_area_generic_error(world_ops, mock_conn_manager):
    """Test get_build_area with a generic Exception."""
    mock_conn_manager.get_build_area.side_effect = Exception("Something broke")
    with patch('src.gdpc_interface.world_operations.logger') as mock_logger:
        box = world_ops.get_build_area()
        assert box is None
        mock_logger.error.assert_called_once_with("Unexpected error getting build area: Something broke")

# Test get_players
def test_get_players_success(world_ops, mock_conn_manager):
    """Test get_players successful case."""
    expected_players: PlayerInfo = {"Alice": {"position": [1, 2, 3]}, "Bob": {"position": [4, 5, 6]}}
    mock_conn_manager.get_players.return_value = expected_players

    players = world_ops.get_players()
    assert players == expected_players
    mock_conn_manager.get_players.assert_called_once()

def test_get_players_connection_error(world_ops, mock_conn_manager):
    """Test get_players with InterfaceConnectionError."""
    mock_conn_manager.get_players.side_effect = InterfaceConnectionError("Cannot reach server")
    with patch('src.gdpc_interface.world_operations.logger') as mock_logger:
        players = world_ops.get_players()
        assert players is None
        mock_logger.error.assert_called_once_with("Connection error getting players: Cannot reach server")

def test_get_players_generic_error(world_ops, mock_conn_manager):
    """Test get_players with a generic Exception."""
    mock_conn_manager.get_players.side_effect = Exception("Data parsing failed")
    with patch('src.gdpc_interface.world_operations.logger') as mock_logger:
        players = world_ops.get_players()
        assert players is None
        mock_logger.error.assert_called_once_with("Unexpected error getting players: Data parsing failed")

# Test get_player_position
def test_get_player_position_success(world_ops, mock_conn_manager):
    """Test get_player_position successful case."""
    player_name = "Alice"
    players_info: PlayerInfo = {player_name: {"position": [10, 20, 30]}, "Bob": {"position": [4, 5, 6]}}
    mock_conn_manager.get_players.return_value = players_info # Mock the underlying call

    expected_pos = ivec3(10, 20, 30)
    pos = world_ops.get_player_position(player_name)
    assert pos == expected_pos

@patch('src.gdpc_interface.world_operations.WorldOperations.get_players') # Patch the method within the class
def test_get_player_position_player_not_found(mock_get_players, world_ops):
    """Test get_player_position when player is not in the returned list."""
    player_name = "Charlie"
    players_info: PlayerInfo = {"Alice": {"position": [1, 2, 3]}}
    mock_get_players.return_value = players_info

    with patch('src.gdpc_interface.world_operations.logger') as mock_logger:
        pos = world_ops.get_player_position(player_name)
        assert pos is None
        mock_logger.warning.assert_called_once_with(f"Player {player_name} not found or error retrieving players.")

@patch('src.gdpc_interface.world_operations.WorldOperations.get_players')
def test_get_player_position_missing_pos_key(mock_get_players, world_ops):
    """Test get_player_position when player data lacks 'position' key."""
    player_name = "Alice"
    players_info: PlayerInfo = {player_name: {"some_other_data": True}}
    mock_get_players.return_value = players_info

    with patch('src.gdpc_interface.world_operations.logger') as mock_logger:
        pos = world_ops.get_player_position(player_name)
        assert pos is None
        mock_logger.warning.assert_called_once_with(f"Position data not found or invalid for player {player_name}.")

@patch('src.gdpc_interface.world_operations.WorldOperations.get_players')
def test_get_player_position_invalid_pos_data(mock_get_players, world_ops):
    """Test get_player_position when player position data is invalid."""
    player_name = "Alice"
    players_info: PlayerInfo = {player_name: {"position": [1, 2]}} # Wrong length
    mock_get_players.return_value = players_info

    with patch('src.gdpc_interface.world_operations.logger') as mock_logger:
        pos = world_ops.get_player_position(player_name)
        assert pos is None
        mock_logger.warning.assert_called_once_with(f"Position data not found or invalid for player {player_name}.")

@patch('src.gdpc_interface.world_operations.WorldOperations.get_players')
def test_get_player_position_get_players_fails(mock_get_players, world_ops):
    """Test get_player_position when the initial get_players call returns None."""
    player_name = "Alice"
    mock_get_players.return_value = None

    with patch('src.gdpc_interface.world_operations.logger') as mock_logger:
        pos = world_ops.get_player_position(player_name)
        assert pos is None
        mock_logger.warning.assert_called_once_with(f"Player {player_name} not found or error retrieving players.")

# Test get_heightmap
# Patch 'interface' within the world_operations module's scope
@patch('gdpc.interface.getHeightmap')
def test_get_heightmap_success(mock_get_heightmap, world_ops, mock_conn_manager):
    """Test get_heightmap successful case."""
    rect = Rect(offset=(0, 0), size=(10, 10)) # Use 2D offset and size for Rect
    heightmap_type = "MOTION_BLOCKING"
    expected_heights = [64] * (10 * 10)
    mock_get_heightmap.return_value = expected_heights

    heights = world_ops.get_heightmap(rect, heightmap_type)

    assert heights == expected_heights
    mock_get_heightmap.assert_called_once_with(
        mock_conn_manager.host, mock_conn_manager.port, rect, heightmap_type
    )

@patch('gdpc.interface.getHeightmap')
def test_get_heightmap_connection_error(mock_get_heightmap, world_ops):
    """Test get_heightmap with InterfaceConnectionError."""
    rect = Rect(offset=(0, 0), size=(10, 10)) # Use 2D offset and size
    mock_get_heightmap.side_effect = InterfaceConnectionError("No response")

    with patch('src.gdpc_interface.world_operations.logger') as mock_logger:
        heights = world_ops.get_heightmap(rect)
        assert heights is None
        mock_logger.error.assert_called_once_with(f"Connection error getting heightmap for {rect}: No response")

@patch('gdpc.interface.getHeightmap')
def test_get_heightmap_generic_error(mock_get_heightmap, world_ops):
    """Test get_heightmap with a generic Exception."""
    rect = Rect(offset=(0, 0), size=(10, 10)) # Use 2D offset and size
    mock_get_heightmap.side_effect = Exception("Calculation error")

    with patch('src.gdpc_interface.world_operations.logger') as mock_logger:
        heights = world_ops.get_heightmap(rect)
        assert heights is None
        mock_logger.error.assert_called_once_with(f"Unexpected error getting heightmap for {rect}: Calculation error")