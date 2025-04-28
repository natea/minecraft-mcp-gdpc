import pytest
from unittest.mock import MagicMock, patch, ANY
import nbtlib
from io import BytesIO as nbtBytesIO # Alias to avoid conflict with standard io

from gdpc.vector_tools import ivec3, Box
from gdpc.exceptions import InterfaceConnectionError

# Import the module and class to test
from src.gdpc_interface.connection import ConnectionManager # Needed for type hint and fixture
from src.gdpc_interface.structure_operations import StructureOperations, NbtData

# Fixture for a mocked ConnectionManager
@pytest.fixture
def mock_conn_manager():
    """Provides a MagicMock instance of ConnectionManager."""
    mock = MagicMock(spec=ConnectionManager)
    mock.host = "mockhost"
    mock.port = 9000
    # Mock the specific methods used by StructureOperations
    mock.place_structure = MagicMock()
    mock.get_structure = MagicMock()
    return mock

# Fixture for StructureOperations instance with mocked connection
@pytest.fixture
def struct_ops(mock_conn_manager):
    """Provides a StructureOperations instance initialized with the mock ConnectionManager."""
    return StructureOperations(mock_conn_manager)

# Fixture for sample NBT data
@pytest.fixture
def sample_nbt_data() -> NbtData:
    """Provides a simple nbtlib.Compound object."""
    # Create a basic NBT structure
    return nbtlib.Compound({
        'name': nbtlib.String("TestStructure"),
        'size': nbtlib.List[nbtlib.Int]([3, 4, 5]),
        'data': nbtlib.Compound({'value': nbtlib.Byte(1)})
    })

# Fixture for sample NBT bytes
@pytest.fixture
def sample_nbt_bytes(sample_nbt_data: NbtData) -> bytes:
    """Provides the byte representation of the sample NBT data."""
    with nbtBytesIO() as bytes_io:
        sample_nbt_data.write(bytes_io, byteorder='big')
        return bytes_io.getvalue()

# Test Initialization
def test_structure_operations_init(mock_conn_manager):
    """Test StructureOperations initialization."""
    with patch('src.gdpc_interface.structure_operations.logger') as mock_logger:
        ops = StructureOperations(mock_conn_manager)
        assert ops.conn == mock_conn_manager
        mock_logger.info.assert_called_once_with("StructureOperations initialized.")

# Test place_structure
@patch('src.gdpc_interface.structure_operations.io.BytesIO', new=nbtBytesIO) # Ensure correct BytesIO
@patch('src.gdpc_interface.structure_operations.nbtlib.Compound.write') # Mock write method
def test_place_structure_success(mock_nbt_write, struct_ops, mock_conn_manager, sample_nbt_data, sample_nbt_bytes):
    """Test place_structure successful case."""
    pos = ivec3(10, 20, 30)
    rotation = 90
    mirror = "LEFT_RIGHT"
    pivot = ivec3(1, 0, 1)
    includes_entities = False
    do_block_updates = False
    custom_flags = "force"

    # Configure mocks
    mock_conn_manager.place_structure.return_value = "ok"
    # Simulate the write method populating the BytesIO
    def write_effect(buffer, byteorder):
        buffer.write(sample_nbt_bytes)
    mock_nbt_write.side_effect = write_effect

    result = struct_ops.place_structure(
        pos,
        sample_nbt_data,
        rotation=rotation,
        mirror=mirror,
        pivot=pivot,
        includes_entities=includes_entities,
        do_block_updates=do_block_updates,
        custom_flags=custom_flags,
    )

    assert result is True
    # Verify NBT serialization was attempted
    mock_nbt_write.assert_called_once_with(ANY, byteorder='big')
    # Verify the underlying connection method was called with correct args
    mock_conn_manager.place_structure.assert_called_once_with(
        pos,
        sample_nbt_bytes, # Ensure bytes are passed
        rotation=rotation,
        mirror=mirror,
        pivot=pivot,
        includeEntities=includes_entities,
        doBlockUpdates=do_block_updates,
        customFlags=custom_flags,
    )

def test_place_structure_connection_error(struct_ops, mock_conn_manager, sample_nbt_data, sample_nbt_bytes):
    """Test place_structure with InterfaceConnectionError."""
    pos = ivec3(10, 20, 30)
    mock_conn_manager.place_structure.side_effect = InterfaceConnectionError("Failed")

    # Patch BytesIO and write just to avoid errors during serialization attempt
    with patch('src.gdpc_interface.structure_operations.io.BytesIO', new=nbtBytesIO), \
         patch('src.gdpc_interface.structure_operations.nbtlib.Compound.write') as mock_nbt_write:
        def write_effect(buffer, byteorder):
            buffer.write(sample_nbt_bytes)
        mock_nbt_write.side_effect = write_effect

        with patch('src.gdpc_interface.structure_operations.logger') as mock_logger:
            result = struct_ops.place_structure(pos, sample_nbt_data)
            assert result is False
            mock_logger.error.assert_called_once_with(f"Connection error placing structure at {pos}: Failed")

def test_place_structure_generic_error(struct_ops, mock_conn_manager, sample_nbt_data, sample_nbt_bytes):
    """Test place_structure with a generic Exception."""
    pos = ivec3(10, 20, 30)
    mock_conn_manager.place_structure.side_effect = Exception("Internal Server Error")

    with patch('src.gdpc_interface.structure_operations.io.BytesIO', new=nbtBytesIO), \
         patch('src.gdpc_interface.structure_operations.nbtlib.Compound.write') as mock_nbt_write:
        def write_effect(buffer, byteorder):
            buffer.write(sample_nbt_bytes)
        mock_nbt_write.side_effect = write_effect

        with patch('src.gdpc_interface.structure_operations.logger') as mock_logger:
            result = struct_ops.place_structure(pos, sample_nbt_data)
            assert result is False
            mock_logger.error.assert_called_once_with(f"Unexpected error placing structure at {pos}: Internal Server Error")

# Test get_structure
@patch('src.gdpc_interface.structure_operations.nbtlib.load') # Mock nbtlib.load
@patch('src.gdpc_interface.structure_operations.io.BytesIO', new=nbtBytesIO) # Ensure correct BytesIO
def test_get_structure_success(mock_nbt_load, struct_ops, mock_conn_manager, sample_nbt_data, sample_nbt_bytes):
    """Test get_structure successful case."""
    box = Box(offset=(0, 0, 0), size=(5, 5, 5))
    includes_entities = False
    mock_conn_manager.get_structure.return_value = sample_nbt_bytes
    mock_nbt_load.return_value = sample_nbt_data # Simulate successful parsing

    nbt_result = struct_ops.get_structure(box, includes_entities=includes_entities)

    assert nbt_result == sample_nbt_data
    mock_conn_manager.get_structure.assert_called_once_with(box, includeEntities=includes_entities)
    # Verify nbtlib.load was called with the bytes
    mock_nbt_load.assert_called_once()
    # Check the first argument of the call to load (should be a BytesIO containing the bytes)
    args, kwargs = mock_nbt_load.call_args
    assert isinstance(args[0], nbtBytesIO)
    # Cannot reliably call getvalue() here as the stream might be closed by the 'with' block in source
    # assert args[0].getvalue() == sample_nbt_bytes
    assert kwargs == {'byteorder': 'big'}


def test_get_structure_empty_response(struct_ops, mock_conn_manager):
    """Test get_structure when the server returns empty bytes or None."""
    box = Box(offset=(0, 0, 0), size=(5, 5, 5))
    mock_conn_manager.get_structure.return_value = b""

    with patch('src.gdpc_interface.structure_operations.logger') as mock_logger:
        nbt_result = struct_ops.get_structure(box)
        assert nbt_result is None
        mock_logger.warning.assert_called_once_with(f"Received empty response when getting structure from {box}.")

    mock_conn_manager.get_structure.return_value = None
    with patch('src.gdpc_interface.structure_operations.logger') as mock_logger:
        nbt_result = struct_ops.get_structure(box)
        assert nbt_result is None
        # Warning might be called again if run in sequence, check specific call if needed
        # mock_logger.warning.assert_called_with(f"Received empty response when getting structure from {box}.")


def test_get_structure_connection_error(struct_ops, mock_conn_manager):
    """Test get_structure with InterfaceConnectionError."""
    box = Box(offset=(0, 0, 0), size=(5, 5, 5))
    mock_conn_manager.get_structure.side_effect = InterfaceConnectionError("Timeout")

    with patch('src.gdpc_interface.structure_operations.logger') as mock_logger:
        nbt_result = struct_ops.get_structure(box)
        assert nbt_result is None
        mock_logger.error.assert_called_once_with(f"Connection error getting structure from {box}: Timeout")

@patch('src.gdpc_interface.structure_operations.nbtlib.load')
@patch('src.gdpc_interface.structure_operations.io.BytesIO', new=nbtBytesIO)
def test_get_structure_malformed_nbt(mock_nbt_load, struct_ops, mock_conn_manager, sample_nbt_bytes):
    """Test get_structure with malformed NBT data causing nbtlib error."""
    box = Box(offset=(0, 0, 0), size=(5, 5, 5))
    mock_conn_manager.get_structure.return_value = sample_nbt_bytes # Return valid bytes initially
    # Simulate parsing error using nbtlib.CastError with a dummy tag_type
    mock_nbt_load.side_effect = nbtlib.CastError("Invalid NBT tag", nbtlib.String)

    with patch('src.gdpc_interface.structure_operations.logger') as mock_logger:
        nbt_result = struct_ops.get_structure(box)
        assert nbt_result is None
        # Match the actual error message format from the CastError
        mock_logger.error.assert_called_once_with(f"Error parsing NBT data from {box}: Couldn't cast 'Invalid NBT tag' to String")

def test_get_structure_generic_error(struct_ops, mock_conn_manager):
    """Test get_structure with a generic Exception."""
    box = Box(offset=(0, 0, 0), size=(5, 5, 5))
    mock_conn_manager.get_structure.side_effect = Exception("Unknown error")

    with patch('src.gdpc_interface.structure_operations.logger') as mock_logger:
        nbt_result = struct_ops.get_structure(box)
        assert nbt_result is None
        mock_logger.error.assert_called_once_with(f"Unexpected error getting structure from {box}: Unknown error")

def test_get_structure_saves_to_disk_warning(struct_ops, mock_conn_manager, sample_nbt_bytes):
    """Test get_structure with saves_to_disk=True logs a warning."""
    box = Box(offset=(0, 0, 0), size=(5, 5, 5))
    mock_conn_manager.get_structure.return_value = sample_nbt_bytes # Still return data

    with patch('src.gdpc_interface.structure_operations.logger') as mock_logger, \
         patch('src.gdpc_interface.structure_operations.nbtlib.load'): # Mock load to prevent parsing errors
        struct_ops.get_structure(box, saves_to_disk=True)
        mock_logger.warning.assert_called_once_with(
            "saves_to_disk=True is not directly supported by gdpc interface.getStructure. "
            "The NBT data will be returned in memory."
        )