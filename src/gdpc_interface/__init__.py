"""
GDPC Interface Layer

This package provides a higher-level interface to interact with the GDPC library,
abstracting away some of the direct function calls and providing a more
structured approach to Minecraft world manipulation.
"""

# Import key components to make them available at the package level
from .connection import ConnectionManager
from .block_operations import BlockOperations
from .world_operations import WorldOperations
from .structure_operations import StructureOperations
from .exceptions import (
    GDPCInterfaceError,
    ConnectionError,
    BuildAreaError,
    InvalidBlockError,
    InvalidOperationError,
    PlayerNotFoundError,
    NBTError,
    CommandError,
    TimeoutError,
    RateLimitError,
)
from .utils import vec3i_to_tuple, tuple_to_vec3i, box_to_coords, check_build_area, check_box_in_build_area

__version__ = "0.1.0"

__all__ = [
    "ConnectionManager",
    "BlockOperations",
    "WorldOperations",
    "StructureOperations",
    "GDPCInterfaceError",
    "ConnectionError",
    "BuildAreaError",
    "InvalidBlockError",
    "InvalidOperationError",
    "PlayerNotFoundError",
    "NBTError",
    "CommandError",
    "TimeoutError",
    "RateLimitError",
    "vec3i_to_tuple",
    "tuple_to_vec3i",
    "box_to_coords",
    "check_build_area",
    "check_box_in_build_area",
    "__version__",
]