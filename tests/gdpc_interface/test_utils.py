import pytest
from unittest.mock import MagicMock

from gdpc.vector_tools import ivec3, Box

# Import functions to test
from src.gdpc_interface.utils import (
    vec3i_to_tuple,
    tuple_to_vec3i,
    box_to_coords,
    check_build_area,
    check_box_in_build_area
)

# Tests for vec3i_to_tuple
def test_vec3i_to_tuple_ivec3():
    """Test converting ivec3 to tuple."""
    vec = ivec3(1, 2, 3)
    assert vec3i_to_tuple(vec) == (1, 2, 3)

def test_vec3i_to_tuple_tuple():
    """Test converting tuple to tuple (should pass through)."""
    tup = (4, 5, 6)
    assert vec3i_to_tuple(tup) == (4, 5, 6)

def test_vec3i_to_tuple_list():
    """Test converting list to tuple."""
    lst = [7, 8, 9]
    assert vec3i_to_tuple(lst) == (7, 8, 9)

def test_vec3i_to_tuple_float_components():
    """Test converting list/tuple with float components."""
    lst = [7.0, 8.1, 9.9]
    assert vec3i_to_tuple(lst) == (7, 8, 9) # Should truncate to int

def test_vec3i_to_tuple_invalid_type():
    """Test with invalid input type."""
    with pytest.raises(TypeError, match="Could not convert .* to integer tuple"):
        vec3i_to_tuple("not a vector")
    # Test with another invalid type (int) - should also raise the "Could not convert" error
    with pytest.raises(TypeError, match="Could not convert .* to integer tuple"):
        vec3i_to_tuple(123)

def test_vec3i_to_tuple_invalid_length():
    """Test with tuple/list of incorrect length."""
    with pytest.raises(TypeError, match="Could not convert .* to integer tuple"):
        vec3i_to_tuple((1, 2))
    # Test with another invalid length - should also raise the "Could not convert" error
    with pytest.raises(TypeError, match="Could not convert .* to integer tuple"):
        vec3i_to_tuple([1, 2, 3, 4])

def test_vec3i_to_tuple_non_numeric():
    """Test with non-numeric components."""
    with pytest.raises(TypeError, match="Could not convert"):
        vec3i_to_tuple((1, "two", 3))

# Tests for tuple_to_vec3i
def test_tuple_to_vec3i_valid():
    """Test converting a valid tuple to ivec3."""
    tup = (10, 20, 30)
    expected_vec = ivec3(10, 20, 30)
    assert tuple_to_vec3i(tup) == expected_vec

def test_tuple_to_vec3i_invalid_type():
    """Test converting non-tuple input."""
    with pytest.raises(TypeError, match="Input must be a tuple"):
        tuple_to_vec3i([1, 2, 3])
    with pytest.raises(TypeError, match="Input must be a tuple"):
        tuple_to_vec3i("1, 2, 3")

def test_tuple_to_vec3i_invalid_length():
    """Test converting tuple with incorrect length."""
    with pytest.raises(TypeError, match="Input must be a tuple of 3 integers"):
        tuple_to_vec3i((1, 2))
    with pytest.raises(TypeError, match="Input must be a tuple of 3 integers"):
        tuple_to_vec3i((1, 2, 3, 4))

def test_tuple_to_vec3i_non_numeric():
    """Test converting tuple with non-numeric components."""
    with pytest.raises(TypeError, match="Could not convert"):
        tuple_to_vec3i((10, "twenty", 30))

# Tests for box_to_coords
def test_box_to_coords_valid():
    """Test converting a Box to start and end coordinates."""
    box = Box(offset=(10, 20, 30), size=(5, 6, 7))
    expected_start = (10, 20, 30)
    expected_end = (15, 26, 37) # offset + size
    start, end = box_to_coords(box)
    assert start == expected_start
    assert end == expected_end

# Tests for check_build_area
@pytest.fixture
def build_area():
    """Fixture for a sample build area Box."""
    return Box(offset=(0, 0, 0), size=(100, 100, 100))

def test_check_build_area_inside(build_area):
    """Test point inside build area."""
    pos = (50, 50, 50)
    assert check_build_area(pos, build_area) is True

def test_check_build_area_min_edge(build_area):
    """Test point on the minimum edge (inclusive)."""
    pos = (0, 0, 0)
    assert check_build_area(pos, build_area) is True

def test_check_build_area_max_edge(build_area):
    """Test point on the maximum edge (exclusive)."""
    pos = (100, 50, 50) # x = offset.x + size.x
    assert check_build_area(pos, build_area) is False
    pos = (50, 100, 50)
    assert check_build_area(pos, build_area) is False
    pos = (50, 50, 100)
    assert check_build_area(pos, build_area) is False
    pos = (99, 99, 99) # Last valid point
    assert check_build_area(pos, build_area) is True


def test_check_build_area_outside(build_area):
    """Test point outside build area."""
    pos = (150, 50, 50)
    assert check_build_area(pos, build_area) is False
    pos = (-10, 50, 50)
    assert check_build_area(pos, build_area) is False

# Tests for check_box_in_build_area
def test_check_box_in_build_area_fully_inside(build_area):
    """Test box fully inside build area."""
    box = Box(offset=(10, 10, 10), size=(20, 20, 20))
    assert check_box_in_build_area(box, build_area) is True

def test_check_box_in_build_area_touching_min_edge(build_area):
    """Test box touching the minimum edge."""
    box = Box(offset=(0, 0, 0), size=(10, 10, 10))
    assert check_box_in_build_area(box, build_area) is True

def test_check_box_in_build_area_touching_max_edge(build_area):
    """Test box touching the maximum edge."""
    # Last valid block is at (99, 99, 99)
    # Box offset (90,90,90) size (10,10,10) -> ends at (100,100,100) exclusive
    # End corner inclusive is (99, 99, 99)
    box = Box(offset=(90, 90, 90), size=(10, 10, 10))
    assert check_box_in_build_area(box, build_area) is True

def test_check_box_in_build_area_partially_outside(build_area):
    """Test box partially outside build area."""
    # Starts inside, ends outside
    box = Box(offset=(80, 80, 80), size=(30, 30, 30))
    assert check_box_in_build_area(box, build_area) is False
    # Starts outside, ends inside
    box = Box(offset=(-10, 0, 0), size=(20, 20, 20))
    assert check_box_in_build_area(box, build_area) is False

def test_check_box_in_build_area_fully_outside(build_area):
    """Test box fully outside build area."""
    box = Box(offset=(110, 110, 110), size=(10, 10, 10))
    assert check_box_in_build_area(box, build_area) is False

def test_check_box_in_build_area_mock_contains(build_area):
    """Verify Box.contains is called correctly."""
    mock_build_area = MagicMock(spec=Box)
    mock_build_area.contains.return_value = True # Assume it contains for this check

    box_to_check = Box(offset=(10, 10, 10), size=(5, 5, 5))
    start_corner = ivec3(10, 10, 10)
    end_corner_inclusive = ivec3(14, 14, 14)

    check_box_in_build_area(box_to_check, mock_build_area)

    # Check if contains was called with the correct corners
    mock_build_area.contains.assert_any_call(start_corner)
    mock_build_area.contains.assert_any_call(end_corner_inclusive)
    assert mock_build_area.contains.call_count == 2