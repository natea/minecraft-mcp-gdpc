"""
Debug script for block placement in Minecraft.

This script tests placing blocks in Minecraft using direct HTTP requests.
"""

import logging
import sys
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)
logger = logging.getLogger(__name__)

# Constants
MINECRAFT_HOST = "127.0.0.1"
MINECRAFT_HTTP_PORT = 9000  # The port that works with direct HTTP requests

def place_blocks_one_by_one(x1, y1, z1, x2, y2, z2, block_type):
    """Place blocks one by one using direct HTTP requests."""
    blocks_placed = 0
    for x in range(x1, x2 + 1):
        for y in range(y1, y2 + 1):
            for z in range(z1, z2 + 1):
                try:
                    # Use direct HTTP request with port 9000 (which is working)
                    cmd = f"setblock {x} {y} {z} {block_type}"
                    logger.info(f"Executing setblock command: {cmd}")
                    response = requests.post(
                        f"http://{MINECRAFT_HOST}:{MINECRAFT_HTTP_PORT}/command?dimension=overworld",
                        data=cmd
                    )
                    result = json.loads(response.text)
                    logger.info(f"Result for {x},{y},{z}: {result}")
                    if result and any(item.get('status', 0) == 1 for item in result if isinstance(item, dict)):
                        blocks_placed += 1
                        logger.info(f"Block placed at {x},{y},{z}")
                    else:
                        logger.warning(f"Failed to place block at {x},{y},{z}: {result}")
                except Exception as e:
                    logger.error(f"Error placing block at ({x},{y},{z}): {e}")
    return blocks_placed

def main():
    """Main function to test block placement."""
    logger.info("Testing block placement...")
    
    # Test coordinates - use coordinates that are known to work
    x1, y1, z1 = 0, 65, 0
    x2, y2, z2 = 2, 65, 2
    block_type = "minecraft:stone"
    
    # Use a custom function to place blocks one by one
    logger.info(f"Placing blocks from ({x1},{y1},{z1}) to ({x2},{y2},{z2})")
    
    # Place the blocks
    blocks_placed = place_blocks_one_by_one(x1, y1, z1, x2, y2, z2, block_type)
    
    # Log the result
    if blocks_placed > 0:
        logger.info(f"Successfully placed {blocks_placed} blocks")
    else:
        logger.warning("No blocks were placed")

if __name__ == "__main__":
    main()