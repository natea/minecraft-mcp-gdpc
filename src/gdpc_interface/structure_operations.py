"""
Provides functions for interacting with structures (NBT format) in the Minecraft world.
"""

import logging
from typing import Optional, Dict, Any

import nbtlib
from gdpc.vector_tools import Vec3iLike, Box, ivec3
from gdpc.exceptions import RequestConnectionError

from .connection import ConnectionManager

logger = logging.getLogger(__name__)

NbtData = nbtlib.Compound  # Represents parsed NBT data


class StructureOperations:
    """Handles placing and retrieving structures (NBT data)."""

    def __init__(self, connection_manager: ConnectionManager):
        """
        Initializes StructureOperations with a ConnectionManager.

        Args:
            connection_manager: An instance of ConnectionManager.
        """
        self.conn = connection_manager
        logger.info("StructureOperations initialized.")

    def place_structure(
        self,
        pos: Vec3iLike,
        nbt_data: NbtData,
        rotation: int = 0,
        mirror: str = "NONE",
        pivot: Optional[Vec3iLike] = None,
        includes_entities: bool = True,
        do_block_updates: bool = True,
        custom_flags: str = "",
    ) -> bool:
        """
        Places a structure defined by NBT data at a specific position.

        Args:
            pos: The (x, y, z) coordinates for the structure's origin.
            nbt_data: The structure data as an nbtlib.Compound object.
            rotation: Rotation angle (0, 90, 180, 270).
            mirror: Mirroring axis ("NONE", "LEFT_RIGHT", "FRONT_BACK").
            pivot: Pivot point for rotation/mirroring relative to pos.
            includes_entities: Whether to include entities from the NBT data.
            do_block_updates: Whether to trigger block updates.
            custom_flags: Additional flags for placement.

        Returns:
            True if the operation was likely successful, False otherwise.
        """
        try:
            # Convert nbtlib object back to bytes or string if needed by gdpc
            # Assuming gdpc interface.placeStructure expects NBT string/bytes
            # Let's check gdpc source or assume it handles nbtlib objects directly
            # Update: gdpc interface.placeStructure expects raw NBT bytes.
            with nbtlib.BytesIO() as bytes_io:
                nbt_data.write(bytes_io, byteorder='big') # Minecraft uses big-endian
                nbt_bytes = bytes_io.getvalue()

            result = self.conn.place_structure(
                pos,
                nbt_bytes, # Pass raw bytes
                rotation=rotation,
                mirror=mirror,
                pivot=pivot,
                includeEntities=includes_entities,
                doBlockUpdates=do_block_updates,
                customFlags=custom_flags,
            )
            logger.debug(f"Placed structure at {pos}. Result: {result}")
            return True
        except RequestConnectionError as e:
            logger.error(f"Connection error placing structure at {pos}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error placing structure at {pos}: {e}")
            return False

    def get_structure(
        self,
        box: Box,
        includes_entities: bool = True,
        saves_to_disk: bool = False, # Note: gdpc interface doesn't directly save
    ) -> Optional[NbtData]:
        """
        Retrieves the structure (blocks and optionally entities) within a bounding box.

        Args:
            box: A gdpc.vector_tools.Box defining the region.
            includes_entities: Whether to include entities in the NBT data.
            saves_to_disk: (Not directly supported by gdpc interface.getStructure)

        Returns:
            An nbtlib.Compound object representing the structure, or None on error.
        """
        if saves_to_disk:
            logger.warning("saves_to_disk=True is not directly supported by gdpc interface.getStructure. "
                           "The NBT data will be returned in memory.")

        try:
            # gdpc interface.getStructure returns raw NBT bytes
            nbt_bytes = self.conn.get_structure(
                box,
                includeEntities=includes_entities
            )

            if nbt_bytes:
                # Parse the raw bytes using nbtlib
                with nbtlib.BytesIO(nbt_bytes) as bytes_io:
                    nbt_data = nbtlib.load(bytes_io, byteorder='big')
                logger.debug(f"Retrieved structure from box {box}.")
                return nbt_data # Return parsed nbtlib object
            else:
                logger.warning(f"Received empty response when getting structure from {box}.")
                return None
        except RequestConnectionError as e:
            logger.error(f"Connection error getting structure from {box}: {e}")
            return None
        except nbtlib.MalformedResponseError as e:
             logger.error(f"Error parsing NBT data received from server for box {box}: {e}")
             return None
        except Exception as e:
            logger.error(f"Unexpected error getting structure from {box}: {e}")
            return None

# Example usage (can be removed later)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn_manager = ConnectionManager()
    if conn_manager.test_connection():
        struct_ops = StructureOperations(conn_manager)

        # Example: Get player position
        try:
            players = conn_manager.get_players()
            if players:
                player_name = list(players.keys())[0]
                player_pos_raw = players[player_name]["position"]
                player_pos = ivec3(int(player_pos_raw[0]), int(player_pos_raw[1]), int(player_pos_raw[2]))
                print(f"Player position: {player_pos}")

                # 1. Get a small structure near the player
                capture_box = Box(offset=player_pos + ivec3(2, 0, 2), size=(3, 3, 3))
                print(f"Attempting to capture structure in box: {capture_box}")
                captured_nbt = struct_ops.get_structure(capture_box)

                if captured_nbt:
                    print(f"Successfully captured structure NBT: {captured_nbt.name if captured_nbt.name else 'Unnamed'}")
                    # print(captured_nbt.pretty()) # Can be very verbose

                    # 2. Place the captured structure nearby
                    place_pos = player_pos + ivec3(6, 0, 6)
                    print(f"Attempting to place captured structure at: {place_pos}")
                    if struct_ops.place_structure(place_pos, captured_nbt):
                        print(f"Successfully placed structure at {place_pos}")
                    else:
                        print(f"Failed to place structure at {place_pos}")
                else:
                    print(f"Failed to capture structure from {capture_box}")

            else:
                print("No players online.")
        except Exception as e:
            print(f"Error during example execution: {e}")
            import traceback
            traceback.print_exc()