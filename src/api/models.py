"""
Pydantic models for API request and response validation.
"""

from typing import List, Optional, Tuple, Dict, Any
from pydantic import BaseModel, Field, validator


# --- Status Models ---

class HealthStatus(BaseModel):
    """Response model for health check."""
    status: str = "ok"

class GDPCStatus(BaseModel):
    """Response model for GDPC connection status."""
    status: str
    minecraft_version: Optional[str] = None

# --- Coordinate and Geometry Models ---

class Position(BaseModel):
    """Represents a 3D integer position."""
    x: int
    y: int
    z: int

    @classmethod
    def from_tuple(cls, pos_tuple: Tuple[int, int, int]) -> "Position":
        return cls(x=pos_tuple[0], y=pos_tuple[1], z=pos_tuple[2])

    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.x, self.y, self.z)

class BoxModel(BaseModel):
    """Represents a 3D bounding box."""
    start: Position = Field(..., description="The starting corner (inclusive) of the box.")
    end: Position = Field(..., description="The ending corner (exclusive) of the box.")
    # Or use offset and size:
    # offset: Position
    # size: Position # Representing dx, dy, dz

    @validator('end')
    def end_must_be_greater_than_start(cls, end, values):
        start = values.get('start')
        if start and (end.x <= start.x or end.y <= start.y or end.z <= start.z):
            raise ValueError("Box end coordinates must be strictly greater than start coordinates.")
        return end

class RectModel(BaseModel):
    """Represents a 2D rectangular area (XZ plane)."""
    start_x: int
    start_z: int
    end_x: int
    end_z: int

    @validator('end_x')
    def end_x_must_be_greater_than_start_x(cls, end_x, values):
        start_x = values.get('start_x')
        if start_x is not None and end_x <= start_x:
            raise ValueError("end_x must be strictly greater than start_x.")
        return end_x

    @validator('end_z')
    def end_z_must_be_greater_than_start_z(cls, end_z, values):
        start_z = values.get('start_z')
        if start_z is not None and end_z <= start_z:
            raise ValueError("end_z must be strictly greater than start_z.")
        return end_z


# --- Block Operation Models ---

class PlaceBlocksRequest(BaseModel):
    """Request model for placing blocks."""
    start_pos: Tuple[int, int, int] = Field(..., description="Starting coordinate (x, y, z) of the region.")
    end_pos: Tuple[int, int, int] = Field(..., description="Ending coordinate (exclusive) (x, y, z) of the region.")
    blocks: List[str] = Field(..., description="List of block IDs (e.g., 'minecraft:stone'). Length must match region volume if pattern is not 'fill'.")
    pattern: str = Field("list", description="Pattern for placing blocks ('list' or 'fill'). If 'fill', the first block in 'blocks' is used.")
    do_block_updates: bool = Field(True, description="Whether to trigger block updates.")

    @validator('end_pos')
    def end_pos_must_be_greater(cls, end_pos, values):
        start_pos = values.get('start_pos')
        if start_pos and (end_pos[0] <= start_pos[0] or end_pos[1] <= start_pos[1] or end_pos[2] <= start_pos[2]):
            raise ValueError("end_pos coordinates must be strictly greater than start_pos coordinates.")
        return end_pos

    @validator('blocks')
    def check_blocks_list(cls, blocks, values):
        pattern = values.get('pattern')
        start_pos = values.get('start_pos')
        end_pos = values.get('end_pos')
        if pattern == 'list' and start_pos and end_pos:
            volume = (end_pos[0] - start_pos[0]) * (end_pos[1] - start_pos[1]) * (end_pos[2] - start_pos[2])
            if len(blocks) != volume:
                raise ValueError(f"Number of blocks ({len(blocks)}) must match region volume ({volume}) when pattern is 'list'.")
        elif pattern == 'fill' and not blocks:
             raise ValueError("Block list cannot be empty when pattern is 'fill'.")
        return blocks


class PlaceBlocksResponse(BaseModel):
    """Response model after placing blocks."""
    success: bool
    blocks_placed: Optional[int] = None # Exact count might be hard to determine reliably
    operation_id: Optional[str] = None # For async operations
    message: Optional[str] = None

class BlockInfo(BaseModel):
    """Represents information about a single block."""
    x: int
    y: int
    z: int
    block_type: str
    block_state: Optional[Dict[str, Any]] = None

class GetBlocksResponse(BaseModel):
    """Response model for getting blocks in a region."""
    blocks: List[BlockInfo]
    total: int


# --- World Operation Models ---

class BuildAreaResponse(BaseModel):
    """Response model for the build area."""
    start: Position
    end: Position # Exclusive end

class PlayerPositionResponse(BaseModel):
    """Response model for a player's position."""
    player_name: str
    position: Position

class GetPlayersResponse(BaseModel):
    """Response model listing online players and their positions."""
    players: Dict[str, Position] # Player name -> Position


# --- Structure Operation Models ---
# Add models for structure placement requests/responses later

# --- Error Model ---

class ErrorDetail(BaseModel):
    """Standard error response model."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail


# --- Authentication Models ---

class UserRegisterRequest(BaseModel):
    """Request model for user registration."""
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="securepassword")
    username: str = Field(..., min_length=3, example="minecraft_builder")

class UserResponse(BaseModel):
    """Response model for user details."""
    id: str # UUID as string
    email: str
    username: str
    created_at: str # ISO 8601 format

class AuthResponse(BaseModel):
    """Response model for successful authentication (login/register)."""
    user: UserResponse
    access_token: str
    token_type: str = "bearer"

class UserLoginRequest(BaseModel):
    """Request model for user login."""
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., example="securepassword")