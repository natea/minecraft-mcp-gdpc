"""
Provides functions for retrieving information about the Minecraft world.
"""

import logging
from typing import Optional, Dict, List, Tuple

from gdpc.vector_tools import Vec3iLike, Box, Rect, ivec3
from gdpc.exceptions import RequestConnectionError

from .connection import ConnectionManager

logger = logging.getLogger(__name__)

PlayerInfo = Dict[str, Dict] # e.g., {"PlayerName": {"position": [x, y, z], ...}}
Heightmap = List[int] # List of y-values


class WorldOperations:
    """Handles retrieving information about the world state."""

    def __init__(self, connection_manager: ConnectionManager):
        """
        Initializes WorldOperations with a ConnectionManager.

        Args:
            connection_manager: An instance of ConnectionManager.
        """
        self.conn = connection_manager
        logger.info("WorldOperations initialized.")

    def get_build_area(self) -> Optional[Box]:
        """
        Gets the build area defined by the GDMC HTTP Interface mod.

        Returns:
            A gdpc.vector_tools.Box representing the build area, or None on error.
        """
        try:
            build_area_dict = self.conn.get_build_area()
            if build_area_dict:
                # The dict format is {'xFrom': x1, 'yFrom': y1, 'zFrom': z1, 'xTo': x2, 'yTo': y2, 'zTo': z2}
                # Box takes offset and size.
                offset = ivec3(build_area_dict['xFrom'], build_area_dict['yFrom'], build_area_dict['zFrom'])
                # Size is (to - from), assuming 'to' is exclusive in GDPC Box context?
                # Let's assume 'to' is inclusive for coordinates, so size is to - from + 1
                # However, GDPC Box size is exclusive, so size = to - from
                size = ivec3(
                    build_area_dict['xTo'] - build_area_dict['xFrom'],
                    build_area_dict['yTo'] - build_area_dict['yFrom'],
                    build_area_dict['zTo'] - build_area_dict['zFrom']
                )
                box = Box(offset, size)
                logger.debug(f"Retrieved build area: {box}")
                return box
            return None
        except RequestConnectionError as e:
            logger.error(f"Connection error getting build area: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting build area: {e}")
            return None

    def get_players(self) -> Optional[PlayerInfo]:
        """
        Gets information about all online players.

        Returns:
            A dictionary where keys are player names and values are dictionaries
            containing player data (like position), or None on error.
        """
        try:
            players = self.conn.get_players()
            logger.debug(f"Retrieved player info: {players}")
            return players
        except RequestConnectionError as e:
            logger.error(f"Connection error getting players: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting players: {e}")
            return None

    def get_player_position(self, player_name: str) -> Optional[Vec3iLike]:
        """
        Gets the position of a specific player.

        Args:
            player_name: The name of the player.

        Returns:
            An ivec3 representing the player's position, or None if player not found or error.
        """
        players = self.get_players()
        if players and player_name in players:
            pos_list = players[player_name].get("position")
            if pos_list and len(pos_list) == 3:
                pos = ivec3(int(pos_list[0]), int(pos_list[1]), int(pos_list[2]))
                logger.debug(f"Position for player {player_name}: {pos}")
                return pos
            else:
                logger.warning(f"Position data not found or invalid for player {player_name}.")
                return None
        else:
            logger.warning(f"Player {player_name} not found or error retrieving players.")
            return None

    def get_heightmap(self, rect: Rect, heightmap_type: str = "WORLD_SURFACE") -> Optional[Heightmap]:
        """
        Gets the heightmap for a specified rectangular area.

        Args:
            rect: A gdpc.vector_tools.Rect defining the area (x, z coordinates).
            heightmap_type: The type of heightmap to retrieve (e.g., "WORLD_SURFACE",
                              "MOTION_BLOCKING", "OCEAN_FLOOR").

        Returns:
            A list of integers representing the y-coordinates for each (x, z) pair
            in the rectangle (ordered x, z), or None on error.
        """
        try:
            # The underlying gdpc function requires host, port, rect, and type
            heightmap = interface.getHeightmap(self.conn.host, self.conn.port, rect, heightmap_type)
            logger.debug(f"Retrieved heightmap of type '{heightmap_type}' for rect {rect}.")
            return heightmap
        except RequestConnectionError as e:
            logger.error(f"Connection error getting heightmap for {rect}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting heightmap for {rect}: {e}")
            return None


# Example usage (can be removed later)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn_manager = ConnectionManager()
    if conn_manager.test_connection():
        world_ops = WorldOperations(conn_manager)

        build_area = world_ops.get_build_area()
        if build_area:
            print(f"Build Area: {build_area}")

        players = world_ops.get_players()
        if players:
            print(f"Players online: {list(players.keys())}")
            first_player = list(players.keys())[0]
            player_pos = world_ops.get_player_position(first_player)
            if player_pos:
                print(f"Position of {first_player}: {player_pos}")

                # Get heightmap around player
                area = Rect(player_pos.x - 5, player_pos.z - 5, 11, 11) # 11x11 area
                heights = world_ops.get_heightmap(area)
                if heights:
                    print(f"Heightmap around player (size {len(heights)}): {heights[:10]}...") # Print first 10
        else:
            print("No players online.")