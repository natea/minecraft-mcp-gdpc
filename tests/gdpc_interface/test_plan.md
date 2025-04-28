# GDPC Interface Module Test Plan

This document outlines the testing strategy for the Python modules within the `src/gdpc_interface/` directory. The primary focus is on unit testing to ensure individual components function correctly in isolation.

## 1. Overall Strategy

-   **Framework**: `pytest` will be used as the test runner for its simplicity and features like fixtures.
-   **Mocking**: `unittest.mock` (specifically `MagicMock` and `patch`) will be used extensively to isolate components and simulate responses from the underlying `gdpc` library and the Minecraft server connection.
-   **Coverage**: Aim for high test coverage for each module, focusing on core logic, different input scenarios, and error handling.
-   **Structure**: Tests will be organized in a parallel `tests/gdpc_interface/` directory, mirroring the `src/gdpc_interface/` structure (e.g., `tests/gdpc_interface/test_connection.py`).
-   **Fixtures**: Pytest fixtures will be used to provide reusable setup, such as mock `ConnectionManager` instances.

## 2. Module-Specific Test Plans

### 2.1. `connection.py` (`tests/gdpc_interface/test_connection.py`)

-   **`ConnectionManager.__init__`**:
    -   Test initialization with default host/port (mock `os.getenv`).
    -   Test initialization with explicit host/port.
    -   Test initialization with environment variables set (mock `os.getenv`).
    -   Verify `logger.info` is called with correct message.
    -   Verify `partial` functions are created correctly (check `func` and `args`).
-   **`ConnectionManager.test_connection`**:
    -   Mock `self.get_version` to return a valid version string. Assert returns `True` and logs info.
    -   Mock `self.get_version` to raise `RequestConnectionError`. Assert returns `False` and logs error.
    -   Mock `self.get_version` to raise a generic `Exception`. Assert returns `False` and logs error.
-   **`ConnectionManager.get_server_version`**:
    -   Mock `self.get_version` to return a valid version string. Assert returns the version.
    -   Mock `self.get_version` to raise `RequestConnectionError`. Assert returns `None` and logs error.
    -   Mock `self.get_version` to raise a generic `Exception`. Assert returns `None` and logs error.

### 2.2. `utils.py` (`tests/gdpc_interface/test_utils.py`)

-   **`vec3i_to_tuple`**:
    -   Test with `ivec3` input.
    -   Test with `tuple` input.
    -   Test with `list` input.
    -   Test with invalid type input (e.g., `int`, `str`). Assert `TypeError`.
    -   Test with invalid length tuple/list. Assert `TypeError`.
    -   Test with non-integer components. Assert `TypeError` or `ValueError` is caught and `TypeError` is raised.
-   **`tuple_to_vec3i`**:
    -   Test with valid 3-integer tuple.
    -   Test with non-tuple input. Assert `TypeError`.
    -   Test with tuple of incorrect length. Assert `TypeError`.
    -   Test with tuple containing non-integers. Assert `TypeError` or `ValueError` is caught and `TypeError` is raised.
-   **`box_to_coords`**:
    -   Test with a standard `Box` object. Verify start and end tuples.
    -   Mock `vec3i_to_tuple` to ensure it's called correctly.
-   **`check_build_area`**:
    -   Test with a point clearly inside the `build_area` Box. Assert `True`.
    -   Test with a point on the edge (min corner) of the `build_area`. Assert `True`.
    -   Test with a point on the edge (max corner, exclusive) of the `build_area`. Assert `False`.
    -   Test with a point clearly outside the `build_area`. Assert `False`.
    -   Mock `ivec3` and `Box.contains` to verify interactions.
-   **`check_box_in_build_area`**:
    -   Test with a box clearly inside the `build_area`. Assert `True`.
    -   Test with a box touching the min edge of the `build_area`. Assert `True`.
    -   Test with a box touching the max edge of the `build_area`. Assert `True`.
    -   Test with a box partially outside the `build_area`. Assert `False`.
    -   Test with a box completely outside the `build_area`. Assert `False`.
    -   Mock `Box.contains` to verify it's called for both corners.

### 2.3. `block_operations.py` (`tests/gdpc_interface/test_block_operations.py`)

-   **Fixture**: Create a pytest fixture `mock_conn_manager` that provides a `MagicMock` instance of `ConnectionManager`.
-   **`BlockOperations.__init__`**:
    -   Test initialization with the `mock_conn_manager` fixture. Verify `self.conn` is set and logger is called.
-   **`BlockOperations.get_block`**:
    -   Mock `mock_conn_manager.get_blocks` to return a list with one block string. Assert the block string is returned.
    -   Mock `mock_conn_manager.get_blocks` to return an empty list. Assert `None` is returned.
    -   Mock `mock_conn_manager.get_blocks` to raise `RequestConnectionError`. Assert `None` is returned and logs error.
    -   Mock `mock_conn_manager.get_blocks` to raise a generic `Exception`. Assert `None` is returned and logs error.
    -   Verify `Box` is created correctly for the single block.
-   **`BlockOperations.set_block`**:
    -   Mock `mock_conn_manager.place_blocks` to return successfully. Assert `True` is returned.
    -   Mock `mock_conn_manager.place_blocks` to raise `RequestConnectionError`. Assert `False` is returned and logs error.
    -   Mock `mock_conn_manager.place_blocks` to raise a generic `Exception`. Assert `False` is returned and logs error.
    -   Verify `place_blocks` is called with correct coordinates (start, end) and block list.
    -   Test with `do_block_updates=True` and `False`.
-   **`BlockOperations.get_blocks_in_box`**:
    -   Mock `mock_conn_manager.get_blocks` to return a list of blocks. Assert the list is returned.
    -   Mock `mock_conn_manager.get_blocks` to raise `RequestConnectionError`. Assert `None` is returned and logs error.
    -   Mock `mock_conn_manager.get_blocks` to raise a generic `Exception`. Assert `None` is returned and logs error.
    -   Verify `get_blocks` is called with the correct `Box`.
-   **`BlockOperations.set_blocks_in_box`**:
    -   Test with a single block string (`blocks="minecraft:stone"`). Verify `place_blocks` is called with a list of the correct size. Assert `True`.
    -   Test with a list of blocks matching the box volume. Verify `place_blocks` is called with the provided list. Assert `True`.
    -   Test with a list of blocks *not* matching the box volume. Assert `False` and logs error. Verify `place_blocks` is *not* called.
    -   Test with invalid `blocks` type (e.g., `int`). Assert `False` and logs error. Verify `place_blocks` is *not* called.
    -   Mock `mock_conn_manager.place_blocks` to raise `RequestConnectionError`. Assert `False` and logs error.
    -   Mock `mock_conn_manager.place_blocks` to raise a generic `Exception`. Assert `False` and logs error.
    -   Verify `box_to_coords` (or direct calculation) provides correct start/end to `place_blocks`.

### 2.4. `world_operations.py` (`tests/gdpc_interface/test_world_operations.py`)

-   **Fixture**: Use the `mock_conn_manager` fixture.
-   **`WorldOperations.__init__`**:
    -   Test initialization. Verify `self.conn` is set and logger is called.
-   **`WorldOperations.get_build_area`**:
    -   Mock `mock_conn_manager.get_build_area` to return a valid dictionary. Assert a correctly constructed `Box` is returned.
    -   Mock `mock_conn_manager.get_build_area` to return `None` or an empty dict. Assert `None` is returned.
    -   Mock `mock_conn_manager.get_build_area` to raise `RequestConnectionError`. Assert `None` is returned and logs error.
    -   Mock `mock_conn_manager.get_build_area` to raise a generic `Exception`. Assert `None` is returned and logs error.
-   **`WorldOperations.get_players`**:
    -   Mock `mock_conn_manager.get_players` to return a player info dictionary. Assert the dictionary is returned.
    -   Mock `mock_conn_manager.get_players` to raise `RequestConnectionError`. Assert `None` is returned and logs error.
    -   Mock `mock_conn_manager.get_players` to raise a generic `Exception`. Assert `None` is returned and logs error.
-   **`WorldOperations.get_player_position`**:
    -   Mock `self.get_players` to return player info including the target player with valid position. Assert the correct `ivec3` position is returned.
    -   Mock `self.get_players` to return player info *without* the target player. Assert `None` is returned and logs warning.
    -   Mock `self.get_players` to return player info *with* the target player but *missing* "position" key. Assert `None` is returned and logs warning.
    -   Mock `self.get_players` to return player info *with* the target player but *invalid* position data (e.g., wrong length). Assert `None` is returned and logs warning.
    -   Mock `self.get_players` to return `None`. Assert `None` is returned and logs warning.
-   **`WorldOperations.get_heightmap`**:
    -   Patch `gdpc_interface.world_operations.interface.getHeightmap` to return a list of heights. Assert the list is returned.
    -   Patch `gdpc_interface.world_operations.interface.getHeightmap` to raise `RequestConnectionError`. Assert `None` is returned and logs error.
    -   Patch `gdpc_interface.world_operations.interface.getHeightmap` to raise a generic `Exception`. Assert `None` is returned and logs error.
    -   Verify `getHeightmap` is called with correct host, port, rect, and type.

### 2.5. `structure_operations.py` (`tests/gdpc_interface/test_structure_operations.py`)

-   **Fixture**: Use the `mock_conn_manager` fixture.
-   **Fixture**: Create a fixture `sample_nbt_data` that returns a simple `nbtlib.Compound` object.
-   **Fixture**: Create a fixture `sample_nbt_bytes` that returns the byte representation of `sample_nbt_data`.
-   **`StructureOperations.__init__`**:
    -   Test initialization. Verify `self.conn` is set and logger is called.
-   **`StructureOperations.place_structure`**:
    -   Mock `mock_conn_manager.place_structure` to return successfully. Use `sample_nbt_data`. Assert `True`.
    -   Verify `nbtlib.BytesIO` and `nbt_data.write` are called correctly to serialize NBT.
    -   Verify `place_structure` is called on the mock connection with the correct NBT *bytes* and other parameters (pos, rotation, mirror, etc.).
    -   Test with different combinations of optional arguments (rotation, mirror, pivot, includes_entities, do_block_updates).
    -   Mock `mock_conn_manager.place_structure` to raise `RequestConnectionError`. Assert `False` and logs error.
    -   Mock `mock_conn_manager.place_structure` to raise a generic `Exception`. Assert `False` and logs error.
-   **`StructureOperations.get_structure`**:
    -   Mock `mock_conn_manager.get_structure` to return `sample_nbt_bytes`. Assert the returned value is an `nbtlib.Compound` matching `sample_nbt_data`.
    -   Verify `nbtlib.load` is called correctly with the bytes.
    -   Mock `mock_conn_manager.get_structure` to return empty bytes or `None`. Assert `None` is returned and logs warning.
    -   Mock `mock_conn_manager.get_structure` to raise `RequestConnectionError`. Assert `None` is returned and logs error.
    -   Mock `mock_conn_manager.get_structure` to return malformed bytes (causing `nbtlib.load` to raise `MalformedResponseError`). Assert `None` is returned and logs error.
    -   Mock `mock_conn_manager.get_structure` to raise a generic `Exception`. Assert `None` is returned and logs error.
    -   Test with `includes_entities=True` and `False`.
    -   Test with `saves_to_disk=True` (verify warning is logged).

### 2.6. `exceptions.py`

-   No specific tests needed for this file as it only defines exception classes. Tests in other modules will verify that these exceptions are raised correctly where appropriate (though mocking often prevents the actual underlying library from raising them during unit tests).

## 3. Execution

-   Tests will be run using the `pytest` command from the project root directory.
-   Coverage reports can be generated using `pytest --cov=src/gdpc_interface`.

This plan provides a solid foundation for unit testing the GDPC interface layer.