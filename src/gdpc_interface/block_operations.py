"""
Provides functions for interacting with blocks in the Minecraft world.
"""

import logging
from typing import List, Optional, Union, Tuple

from gdpc.vector_tools import Vec3iLike, Box, Rect, ivec3
from gdpc.exceptions import RequestConnectionError

from .connection import ConnectionManager

logger = logging.getLogger(__name__)

Block = str  # Represents a block type string, e.g., "minecraft:stone"
BlockList = List[Block]
Position = Vec3iLike


class BlockOperations:
    """Handles getting and setting blocks in the Minecraft world."""

    def __init__(self, connection_manager: ConnectionManager):
        """
        Initializes BlockOperations with a ConnectionManager.

        Args:
            connection_manager: An instance of ConnectionManager.
        """
        self.conn = connection_manager
        logger.info("BlockOperations initialized.")

    def get_block(self, pos: Position) -> Optional[Block]:
        """
        Gets the block type at a specific position.

        Args:
            pos: The (x, y, z) coordinates of the block.

        Returns:
            The block type string, or None if an error occurs.
        """
        try:
            # getBlocks requires a Box, so create a 1x1x1 box
            box = Box(pos, (1, 1, 1))
            blocks = self.conn.get_blocks(box)
            if blocks:
                # Assuming the result is a flat list for the box
                return blocks[0]
            return None
        except RequestConnectionError as e:
            logger.error(f"Connection error getting block at {pos}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting block at {pos}: {e}")
            return None

    def set_block(self, pos: Position, block: Block, do_block_updates: bool = True) -> bool:
        """
        Sets a block at a specific position.

        Args:
            pos: The (x, y, z) coordinates to place the block.
            block: The block type string (e.g., "minecraft:stone").
            do_block_updates: Whether to trigger block updates after placement.

        Returns:
            True if the operation was likely successful, False otherwise.
            Note: GDPC placeBlocks doesn't return explicit success/failure per block.
        """
        try:
            # placeBlocks requires start and end coordinates and a list of blocks
            start = ivec3(*pos)
            end = start + ivec3(1, 1, 1) # 1x1x1 region
            result = self.conn.place_blocks(start.x, start.y, start.z, end.x, end.y, end.z, [block], doBlockUpdates=do_block_updates)
            logger.debug(f"Set block at {pos} to {block}. Result: {result}")
            # The underlying gdpc function returns the response text, not a boolean.
            # We assume success if no exception is raised.
            return True
        except RequestConnectionError as e:
            logger.error(f"Connection error setting block at {pos}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting block at {pos}: {e}")
            return False

    def get_blocks_in_box(self, box: Box) -> Optional[BlockList]:
        """
        Gets all block types within a specified bounding box.

        Args:
            box: A gdpc.vector_tools.Box defining the region.

        Returns:
            A list of block type strings in the order x, z, y, or None on error.
        """
        try:
            blocks = self.conn.get_blocks(box)
            logger.debug(f"Retrieved {len(blocks)} blocks from box {box}.")
            return blocks
        except RequestConnectionError as e:
            logger.error(f"Connection error getting blocks in box {box}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting blocks in box {box}: {e}")
            return None

    def set_blocks_in_box(self, box: Box, blocks: Union[Block, BlockList], do_block_updates: bool = True) -> bool:
        """
        Sets blocks within a specified bounding box.

        Args:
            box: A gdpc.vector_tools.Box defining the region.
            blocks: Either a single block type string (to fill the box) or a list
                    of block type strings matching the box volume (ordered x, z, y).
            do_block_updates: Whether to trigger block updates after placement.

        Returns:
            True if the operation was likely successful, False otherwise.
        """
        try:
            start = box.offset
            end = start + box.size
            block_list: BlockList
            if isinstance(blocks, str):
                # Fill the box with a single block type
                volume = box.volume
                block_list = [blocks] * volume
            elif isinstance(blocks, list):
                # Use the provided list, ensure it matches the volume
                if len(blocks) != box.volume:
                    logger.error(f"Block list length ({len(blocks)}) does not match box volume ({box.volume}).")
                    return False
                block_list = blocks
            else:
                logger.error(f"Invalid 'blocks' type: {type(blocks)}. Must be str or list.")
                return False

            result = self.conn.place_blocks(start.x, start.y, start.z, end.x, end.y, end.z, block_list, doBlockUpdates=do_block_updates)
            logger.debug(f"Set blocks in box {box}. Result: {result}")
            return True
        except RequestConnectionError as e:
            logger.error(f"Connection error setting blocks in box {box}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error setting blocks in box {box}: {e}")
            return False

# Example usage (can be removed later)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn_manager = ConnectionManager()
    if conn_manager.test_connection():
        block_ops = BlockOperations(conn_manager)

        # Example: Get player position (assuming WorldOperations exists or we get it directly)
        try:
            players = conn_manager.get_players()
            if players:
                player_name = list(players.keys())[0]
                player_pos_raw = players[player_name]["position"]
                player_pos = ivec3(int(player_pos_raw[0]), int(player_pos_raw[1]), int(player_pos_raw[2]))
                print(f"Player position: {player_pos}")

                # Get block at player's feet
                feet_pos = player_pos + ivec3(0, -1, 0)
                block_at_feet = block_ops.get_block(feet_pos)
                print(f"Block at player's feet ({feet_pos}): {block_at_feet}")

                # Set a gold block nearby
                gold_pos = player_pos + ivec3(5, 0, 0)
                if block_ops.set_block(gold_pos, "minecraft:gold_block"):
                    print(f"Successfully placed gold block at {gold_pos}")

                # Set a 3x3 glass platform nearby
                platform_box = Box(offset=player_pos + ivec3(-1, -1, 3), size=(3, 1, 3))
                if block_ops.set_blocks_in_box(platform_box, "minecraft:glass"):
                     print(f"Successfully placed glass platform near {player_pos + ivec3(0, -1, 4)}")

            else:
                print("No players online.")
        except Exception as e:
            print(f"Error during example execution: {e}")