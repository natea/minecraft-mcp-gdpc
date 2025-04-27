"""
Manages the connection to the Minecraft GDMC HTTP Interface.
"""

import logging
import os
from functools import partial
from typing import Optional

from gdpc import interface
from gdpc.exceptions import RequestConnectionError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

DEFAULT_HOST = os.getenv("MINECRAFT_HOST", "localhost")
DEFAULT_PORT = int(os.getenv("MINECRAFT_HTTP_PORT", 9000))


class ConnectionManager:
    """Handles connection details and provides configured interface functions."""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        Initializes the ConnectionManager.

        Args:
            host: The hostname or IP address of the Minecraft server.
                  Defaults to MINECRAFT_HOST environment variable or 'localhost'.
            port: The port number of the GDMC HTTP Interface.
                  Defaults to MINECRAFT_HTTP_PORT environment variable or 9000.
        """
        self.host = host or DEFAULT_HOST
        self.port = port or DEFAULT_PORT
        logger.info(f"GDPC Interface configured for {self.host}:{self.port}")

        # Pre-configure interface functions with host and port
        self.get_version = partial(interface.getVersion, self.host, self.port)
        self.get_build_area = partial(interface.getBuildArea, self.host, self.port)
        self.get_players = partial(interface.getPlayers, self.host, self.port)
        self.get_blocks = partial(interface.getBlocks, self.host, self.port)
        self.place_blocks = partial(interface.placeBlocks, self.host, self.port)
        self.run_command = partial(interface.runCommand, self.host, self.port)
        # Add other interface functions as needed...

    def test_connection(self) -> bool:
        """
        Tests the connection to the Minecraft server.

        Returns:
            True if the connection is successful, False otherwise.
        """
        try:
            version = self.get_version()
            logger.info(f"Successfully connected to Minecraft server. Version: {version}")
            return True
        except RequestConnectionError as e:
            logger.error(f"Failed to connect to Minecraft server at {self.host}:{self.port}: {e}")
            return False
        except Exception as e:
            logger.error(f"An unexpected error occurred during connection test: {e}")
            return False

    # Example usage of a pre-configured function
    def get_server_version(self) -> Optional[str]:
        """Gets the Minecraft server version."""
        try:
            return self.get_version()
        except RequestConnectionError as e:
            logger.error(f"Connection error getting server version: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting server version: {e}")
            return None


# Example usage (can be removed later)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    conn_manager = ConnectionManager()
    if conn_manager.test_connection():
        build_area = conn_manager.get_build_area()
        print(f"Build Area: {build_area}")
        players = conn_manager.get_players()
        print(f"Players: {players}")