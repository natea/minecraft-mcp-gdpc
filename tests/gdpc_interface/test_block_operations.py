import pytest
from unittest.mock import MagicMock, patch, ANY

from gdpc.vector_tools import ivec3, Box
from gdpc.exceptions import InterfaceConnectionError

# Import the module and class to test
from src.gdpc_interface.connection import ConnectionManager # Needed for type hint and fixture
from src.gdpc_interface.block_operations import BlockOperations, Position, Block

# Fixture for a mocked ConnectionManager
@pytest.fixture
def mock_conn_manager():
    """Provides a MagicMock instance of ConnectionManager."""
    mock = MagicMock(spec=ConnectionManager)
    # Configure mock attributes if needed, e.g., host/port for logging
    mock.host = "mockhost"
    mock.port = 9000
    # Mock the specific methods used by BlockOperations
    mock.get_blocks = MagicMock()
    mock.place_blocks = MagicMock()
    return mock

# Fixture for BlockOperations instance with mocked connection
@pytest.fixture
def block_ops(mock_conn_manager):
    """Provides a BlockOperations instance initialized with the mock ConnectionManager."""
    return BlockOperations(mock_conn_manager)

# Test Initialization
def test_block_operations_init(mock_conn_manager):
    """Test BlockOperations initialization."""
    with patch('src.gdpc_interface.block_operations.logger') as mock_logger:
        ops = BlockOperations(mock_conn_manager)
        assert ops.conn == mock_conn_manager
        mock_logger.info.assert_called_once_with("BlockOperations initialized.")

# Test get_block
def test_get_block_success(block_ops, mock_conn_manager):
    """Test get_block successful case."""
    pos: Position = (10, 20, 30)
    expected_block: Block = "minecraft:dirt"
    mock_conn_manager.get_blocks.return_value = [expected_block]

    block = block_ops.get_block(pos)

    assert block == expected_block
    expected_box = Box(offset=ivec3(10, 20, 30), size=(1, 1, 1))
    mock_conn_manager.get_blocks.assert_called_once_with(expected_box)

def test_get_block_empty_result(block_ops, mock_conn_manager):
    """Test get_block when the underlying call returns an empty list."""
    pos: Position = (10, 20, 30)
    mock_conn_manager.get_blocks.return_value = []

    block = block_ops.get_block(pos)

    assert block is None
    expected_box = Box(offset=ivec3(10, 20, 30), size=(1, 1, 1))
    mock_conn_manager.get_blocks.assert_called_once_with(expected_box)

def test_get_block_connection_error(block_ops, mock_conn_manager):
    """Test get_block with InterfaceConnectionError."""
    pos: Position = (10, 20, 30)
    mock_conn_manager.get_blocks.side_effect = InterfaceConnectionError("Network Error")

    with patch('src.gdpc_interface.block_operations.logger') as mock_logger:
        block = block_ops.get_block(pos)
        assert block is None
        mock_logger.error.assert_called_once_with(f"Connection error getting block at {pos}: Network Error")

def test_get_block_generic_error(block_ops, mock_conn_manager):
    """Test get_block with a generic Exception."""
    pos: Position = (10, 20, 30)
    mock_conn_manager.get_blocks.side_effect = Exception("Unexpected issue")

    with patch('src.gdpc_interface.block_operations.logger') as mock_logger:
        block = block_ops.get_block(pos)
        assert block is None
        mock_logger.error.assert_called_once_with(f"Unexpected error getting block at {pos}: Unexpected issue")

# Test set_block
@pytest.mark.parametrize("do_updates", [True, False])
def test_set_block_success(block_ops, mock_conn_manager, do_updates):
    """Test set_block successful case."""
    pos: Position = (5, 6, 7)
    block_to_set: Block = "minecraft:gold_block"
    mock_conn_manager.place_blocks.return_value = "ok" # Simulate success response

    result = block_ops.set_block(pos, block_to_set, do_block_updates=do_updates)

    assert result is True
    start = ivec3(5, 6, 7)
    end = start + ivec3(1, 1, 1)
    mock_conn_manager.place_blocks.assert_called_once_with(
        start.x, start.y, start.z, end.x, end.y, end.z, [block_to_set], doBlockUpdates=do_updates
    )

def test_set_block_connection_error(block_ops, mock_conn_manager):
    """Test set_block with InterfaceConnectionError."""
    pos: Position = (5, 6, 7)
    block_to_set: Block = "minecraft:gold_block"
    mock_conn_manager.place_blocks.side_effect = InterfaceConnectionError("Failed")

    with patch('src.gdpc_interface.block_operations.logger') as mock_logger:
        result = block_ops.set_block(pos, block_to_set)
        assert result is False
        mock_logger.error.assert_called_once_with(f"Connection error setting block at {pos}: Failed")

def test_set_block_generic_error(block_ops, mock_conn_manager):
    """Test set_block with a generic Exception."""
    pos: Position = (5, 6, 7)
    block_to_set: Block = "minecraft:gold_block"
    mock_conn_manager.place_blocks.side_effect = Exception("Server error")

    with patch('src.gdpc_interface.block_operations.logger') as mock_logger:
        result = block_ops.set_block(pos, block_to_set)
        assert result is False
        mock_logger.error.assert_called_once_with(f"Unexpected error setting block at {pos}: Server error")

# Test get_blocks_in_box
def test_get_blocks_in_box_success(block_ops, mock_conn_manager):
    """Test get_blocks_in_box successful case."""
    box = Box(offset=(0, 0, 0), size=(2, 2, 2))
    expected_blocks = ["minecraft:stone"] * box.volume
    mock_conn_manager.get_blocks.return_value = expected_blocks

    blocks = block_ops.get_blocks_in_box(box)

    assert blocks == expected_blocks
    mock_conn_manager.get_blocks.assert_called_once_with(box)

def test_get_blocks_in_box_connection_error(block_ops, mock_conn_manager):
    """Test get_blocks_in_box with InterfaceConnectionError."""
    box = Box(offset=(0, 0, 0), size=(2, 2, 2))
    mock_conn_manager.get_blocks.side_effect = InterfaceConnectionError("Timeout")

    with patch('src.gdpc_interface.block_operations.logger') as mock_logger:
        blocks = block_ops.get_blocks_in_box(box)
        assert blocks is None
        mock_logger.error.assert_called_once_with(f"Connection error getting blocks in box {box}: Timeout")

def test_get_blocks_in_box_generic_error(block_ops, mock_conn_manager):
    """Test get_blocks_in_box with a generic Exception."""
    box = Box(offset=(0, 0, 0), size=(2, 2, 2))
    mock_conn_manager.get_blocks.side_effect = Exception("Internal error")

    with patch('src.gdpc_interface.block_operations.logger') as mock_logger:
        blocks = block_ops.get_blocks_in_box(box)
        assert blocks is None
        mock_logger.error.assert_called_once_with(f"Unexpected error getting blocks in box {box}: Internal error")

# Test set_blocks_in_box
@pytest.mark.parametrize("do_updates", [True, False])
def test_set_blocks_in_box_single_block_success(block_ops, mock_conn_manager, do_updates):
    """Test set_blocks_in_box with a single block type."""
    box = Box(offset=(1, 1, 1), size=(2, 3, 4)) # volume = 24
    block_type: Block = "minecraft:glass"
    mock_conn_manager.place_blocks.return_value = "ok"

    result = block_ops.set_blocks_in_box(box, block_type, do_block_updates=do_updates)

    assert result is True
    start = box.offset
    end = start + box.size
    expected_block_list = [block_type] * box.volume
    mock_conn_manager.place_blocks.assert_called_once_with(
        start.x, start.y, start.z, end.x, end.y, end.z, expected_block_list, doBlockUpdates=do_updates
    )

@pytest.mark.parametrize("do_updates", [True, False])
def test_set_blocks_in_box_list_success(block_ops, mock_conn_manager, do_updates):
    """Test set_blocks_in_box with a list of blocks matching volume."""
    box = Box(offset=(1, 1, 1), size=(1, 2, 1)) # volume = 2
    block_list: List[Block] = ["minecraft:dirt", "minecraft:grass_block"]
    mock_conn_manager.place_blocks.return_value = "ok"

    result = block_ops.set_blocks_in_box(box, block_list, do_block_updates=do_updates)

    assert result is True
    start = box.offset
    end = start + box.size
    mock_conn_manager.place_blocks.assert_called_once_with(
        start.x, start.y, start.z, end.x, end.y, end.z, block_list, doBlockUpdates=do_updates
    )

def test_set_blocks_in_box_list_mismatch(block_ops, mock_conn_manager):
    """Test set_blocks_in_box with a list of blocks not matching volume."""
    box = Box(offset=(1, 1, 1), size=(2, 2, 2)) # volume = 8
    block_list: List[Block] = ["minecraft:stone"] * 7 # Incorrect length

    with patch('src.gdpc_interface.block_operations.logger') as mock_logger:
        result = block_ops.set_blocks_in_box(box, block_list)
        assert result is False
        mock_logger.error.assert_called_once_with(f"Block list length ({len(block_list)}) does not match box volume ({box.volume}).")
        mock_conn_manager.place_blocks.assert_not_called()

def test_set_blocks_in_box_invalid_type(block_ops, mock_conn_manager):
    """Test set_blocks_in_box with invalid 'blocks' type."""
    box = Box(offset=(1, 1, 1), size=(2, 2, 2))
    invalid_blocks = 123 # Not str or list

    with patch('src.gdpc_interface.block_operations.logger') as mock_logger:
        result = block_ops.set_blocks_in_box(box, invalid_blocks)
        assert result is False
        mock_logger.error.assert_called_once_with(f"Invalid 'blocks' type: {type(invalid_blocks)}. Must be str or list.")
        mock_conn_manager.place_blocks.assert_not_called()

def test_set_blocks_in_box_connection_error(block_ops, mock_conn_manager):
    """Test set_blocks_in_box with InterfaceConnectionError."""
    box = Box(offset=(1, 1, 1), size=(2, 2, 2))
    block_type: Block = "minecraft:stone"
    mock_conn_manager.place_blocks.side_effect = InterfaceConnectionError("Bad Gateway")

    with patch('src.gdpc_interface.block_operations.logger') as mock_logger:
        result = block_ops.set_blocks_in_box(box, block_type)
        assert result is False
        mock_logger.error.assert_called_once_with(f"Connection error setting blocks in box {box}: Bad Gateway")

def test_set_blocks_in_box_generic_error(block_ops, mock_conn_manager):
    """Test set_blocks_in_box with a generic Exception."""
    box = Box(offset=(1, 1, 1), size=(2, 2, 2))
    block_type: Block = "minecraft:stone"
    mock_conn_manager.place_blocks.side_effect = Exception("Crashed")

    with patch('src.gdpc_interface.block_operations.logger') as mock_logger:
        result = block_ops.set_blocks_in_box(box, block_type)
        assert result is False
        mock_logger.error.assert_called_once_with(f"Unexpected error setting blocks in box {box}: Crashed")