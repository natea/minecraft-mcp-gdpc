"""
Utility functions for the GDPC interface layer.
"""

import logging
from typing import Tuple, List, Union

from gdpc.vector_tools import Vec3iLike, Box, Rect, ivec3

logger = logging.getLogger(__name__)


def vec3i_to_tuple(vec: Vec3iLike) -> Tuple[int, int, int]:
    """Converts a Vec3iLike object to a tuple of integers."""
    try:
        # Handle potential ivec3 or tuple/list inputs
        if hasattr(vec, 'x') and hasattr(vec, 'y') and hasattr(vec, 'z'):
            return int(vec.x), int(vec.y), int(vec.z)
        elif isinstance(vec, (list, tuple)) and len(vec) == 3:
            return int(vec[0]), int(vec[1]), int(vec[2])
        else:
            raise TypeError(f"Input must be Vec3iLike (e.g., ivec3, tuple, list), got {type(vec)}")
    except (ValueError, TypeError) as e:
        logger.error(f"Error converting vector {vec} to tuple: {e}")
        raise TypeError(f"Could not convert {vec} to integer tuple.") from e

def tuple_to_vec3i(pos: Tuple[int, int, int]) -> ivec3:
    """Converts a tuple of integers to an ivec3 object."""
    if not isinstance(pos, tuple) or len(pos) != 3:
        raise TypeError(f"Input must be a tuple of 3 integers, got {pos}")
    try:
        return ivec3(int(pos[0]), int(pos[1]), int(pos[2]))
    except (ValueError, TypeError) as e:
        logger.error(f"Error converting tuple {pos} to ivec3: {e}")
        raise TypeError(f"Could not convert {pos} to ivec3.") from e

def box_to_coords(box: Box) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
    """Converts a Box object to start and end coordinate tuples."""
    start = vec3i_to_tuple(box.offset)
    # Box size is exclusive, so end coord is offset + size - 1 ? No, GDPC uses exclusive end.
    # Let's return the exclusive end coordinate (offset + size)
    end_vec = box.offset + box.size
    end = vec3i_to_tuple(end_vec)
    return start, end

def check_build_area(pos: Vec3iLike, build_area: Box) -> bool:
    """Checks if a position is within the build area."""
    point = ivec3(*vec3i_to_tuple(pos)) # Ensure it's an ivec3 for comparison
    return build_area.contains(point)

def check_box_in_build_area(box: Box, build_area: Box) -> bool:
    """Checks if a given box is entirely within the build area."""
    # Check if both the start and the end corner (exclusive) are within the build area
    # Note: Box.contains checks if a point is within [offset, offset + size)
    start_corner = box.offset
    end_corner_inclusive = box.offset + box.size - ivec3(1, 1, 1) # Last block inside the box

    return build_area.contains(start_corner) and build_area.contains(end_corner_inclusive)


# Example usage (can be removed later)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    vec = ivec3(10, 20, 30)
    tup = vec3i_to_tuple(vec)
    print(f"ivec3 {vec} to tuple: {tup}")

    tup2 = (15, 25, 35)
    vec2 = tuple_to_vec3i(tup2)
    print(f"Tuple {tup2} to ivec3: {vec2}")

    box = Box(offset=(0, 60, 0), size=(10, 5, 10))
    start_coord, end_coord = box_to_coords(box)
    print(f"Box {box} to coords: start={start_coord}, end={end_coord}")

    build_area_box = Box(offset=(-100, 0, -100), size=(200, 256, 200))
    pos_inside = (50, 70, 50)
    pos_outside = (-110, 70, 50)
    print(f"Is {pos_inside} in build area {build_area_box}? {check_build_area(pos_inside, build_area_box)}")
    print(f"Is {pos_outside} in build area {build_area_box}? {check_build_area(pos_outside, build_area_box)}")

    box_inside = Box(offset=(10, 60, 10), size=(5, 5, 5))
    box_outside = Box(offset=(95, 60, 95), size=(10, 10, 10)) # Touches edge
    box_way_outside = Box(offset=(150, 60, 150), size=(10, 10, 10))
    print(f"Is {box_inside} in build area? {check_box_in_build_area(box_inside, build_area_box)}")
    print(f"Is {box_outside} in build area? {check_box_in_build_area(box_outside, build_area_box)}")
    print(f"Is {box_way_outside} in build area? {check_box_in_build_area(box_way_outside, build_area_box)}")