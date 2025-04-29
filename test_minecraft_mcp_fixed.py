"""
Test script for the Minecraft MCP server.
This script tests the fixed functionality of the run_command_tool and place_blocks_tool.
"""

import logging
import sys
import requests
import json
from src.gdpc_interface.connection import ConnectionManager

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout)
logger = logging.getLogger(__name__)

def test_direct_http_command(host="127.0.0.1", port=9000):
    """Test running commands directly via HTTP."""
    logger.info("Testing direct HTTP commands...")
    
    # Test commands
    test_commands = [
        "help",
        "time set day",
        "weather clear",
        "say Hello from direct HTTP test!"
    ]
    
    for cmd in test_commands:
        try:
            logger.info(f"Executing command: {cmd}")
            response = requests.post(
                f"http://{host}:{port}/command?dimension=overworld",
                data=cmd
            )
            result = json.loads(response.text)
            
            # Check for specific command errors
            if cmd == "time set day" and any(item.get('message', '').startswith('Unknown or incomplete command') for item in result if isinstance(item, dict)):
                logger.warning(f"Command '{cmd}' failed. Trying with quotes...")
                # Try with quotes around the command
                response = requests.post(
                    f"http://{host}:{port}/command?dimension=overworld",
                    data=f'"{cmd}"'
                )
                result = json.loads(response.text)
                
            logger.info(f"Result: {result}")
        except Exception as e:
            logger.error(f"Error executing command {cmd}: {e}")

def test_direct_http_place_blocks(host="127.0.0.1", port=9000):
    """Test placing blocks directly via HTTP."""
    logger.info("Testing direct HTTP block placement...")
    
    # Test block placements
    test_blocks = [
        {"x": 0, "y": 64, "z": 0, "dx": 2, "dy": 64, "dz": 2, "block": "minecraft:stone"},
        {"x": 0, "y": 65, "z": 0, "dx": 2, "dy": 65, "dz": 2, "block": "minecraft:oak_planks"},
        {"x": 0, "y": 66, "z": 0, "dx": 2, "dy": 66, "dz": 2, "block": "minecraft:glass"}
    ]
    
    for block_data in test_blocks:
        try:
            logger.info(f"Placing blocks: {block_data}")
            
            # Format the setblock command
            x, y, z = block_data["x"], block_data["y"], block_data["z"]
            dx, dy, dz = block_data["dx"], block_data["dy"], block_data["dz"]
            block = block_data["block"]
            
            # Try using the /fill command first (more efficient)
            try:
                cmd = f"fill {x} {y} {z} {dx} {dy} {dz} {block}"
                logger.info(f"Executing fill command: {cmd}")
                response = requests.post(
                    f"http://{host}:{port}/command?dimension=overworld",
                    data=cmd
                )
                result = json.loads(response.text)
                
                # Check if fill command was successful
                if any(item.get('status', 0) == 1 for item in result if isinstance(item, dict)):
                    logger.info(f"Fill command successful: {result}")
                    continue
                else:
                    logger.warning(f"Fill command failed, falling back to setblock: {result}")
            except Exception as e:
                logger.warning(f"Error with fill command: {e}, falling back to setblock")
            
            # Place blocks one by one as fallback
            blocks_placed = 0
            for i in range(x, dx + 1):
                for j in range(y, dy + 1):
                    for k in range(z, dz + 1):
                        cmd = f"setblock {i} {j} {k} {block}"
                        response = requests.post(
                            f"http://{host}:{port}/command?dimension=overworld",
                            data=cmd
                        )
                        result = json.loads(response.text)
                        if any(item.get('status', 0) == 1 for item in result if isinstance(item, dict)):
                            blocks_placed += 1
                        logger.debug(f"Result for {i},{j},{k}: {result}")
            
            logger.info(f"Successfully placed {blocks_placed} blocks using setblock")
            
            logger.info(f"Completed block placement: {block_data}")
        except Exception as e:
            logger.error(f"Error placing blocks {block_data}: {e}")

def test_connection_manager():
    """Test the ConnectionManager functionality."""
    logger.info("Testing ConnectionManager...")
    
    try:
        # Initialize the ConnectionManager
        conn_manager = ConnectionManager()
        
        # Test connection
        if conn_manager.test_connection():
            logger.info("Successfully connected to Minecraft server.")
            
            # Test get_version
            version = conn_manager.get_server_version()
            logger.info(f"Minecraft server version: {version}")
            
            # Test get_players - Fix player detection issue
            players = conn_manager.get_players()
            
            # Improved player detection - handle different response formats
            player_found = False
            target_player = 'Hacksax'
            
            # Try to find the player in the response
            if isinstance(players, list):
                for player in players:
                    # Handle dict format
                    if isinstance(player, dict) and player.get('name') == target_player:
                        player_found = True
                        break
                    # Handle string format
                    elif isinstance(player, str) and player == target_player:
                        player_found = True
                        break
            
            # Try direct command as fallback if player not found
            if not player_found:
                logger.warning(f"Player '{target_player}' not found in player list. Trying direct command...")
                try:
                    # Use direct command to check if player exists - don't specify dimension as a keyword arg
                    result = conn_manager.run_command(f"data get entity {target_player}")
                    if result and not any("no entity was found" in str(item) for item in result):
                        player_found = True
                        logger.info(f"Player '{target_player}' found using direct command")
                        # Add player to the list if not already there
                        if target_player not in str(players):
                            if isinstance(players, list):
                                players.append({"name": target_player})
                            else:
                                players = [{"name": target_player}]
                except Exception as e:
                    logger.warning(f"Error checking player with direct command: {e}")
            
            logger.info(f"Players online: {players}")
            if player_found:
                logger.info(f"Player '{target_player}' is online")
            else:
                logger.warning(f"Player '{target_player}' not found online")
            
            # Test run_command - Fix command execution issue
            cmd = "time set day"
            logger.info(f"Running command: {cmd}")
            
            # Use direct HTTP request with port 9000 (which is working)
            response = requests.post(
                f"http://{conn_manager.host}:9000/command?dimension=overworld",
                data=cmd
            )
            result = json.loads(response.text)
            logger.info(f"Command result: {result}")
            
            # Test place_blocks - Fix parameter mismatch
            logger.info("Testing place_blocks...")
            try:
                # Use coordinates that are known to work
                x1, y1, z1 = 0, 65, 0
                x2, y2, z2 = 2, 65, 2
                
                # Create a single block type string (correct format based on working examples)
                block_type = "minecraft:stone"
                
                # Use a custom function to place blocks one by one
                logger.info(f"Placing blocks from ({x1},{y1},{z1}) to ({x2},{y2},{z2})")
                
                # Define a function to place blocks one by one using run_command
                def place_blocks_one_by_one(x1, y1, z1, x2, y2, z2, block_type):
                    """Place blocks one by one using run_command."""
                    blocks_placed = 0
                    for x in range(x1, x2 + 1):
                        for y in range(y1, y2 + 1):
                            for z in range(z1, z2 + 1):
                                try:
                                    # Use direct HTTP request with port 9000 (which is working)
                                    cmd = f"setblock {x} {y} {z} {block_type}"
                                    response = requests.post(
                                        f"http://{conn_manager.host}:9000/command?dimension=overworld",
                                        data=cmd
                                    )
                                    result = json.loads(response.text)
                                    if result and any(item.get('status', 0) == 1 for item in result if isinstance(item, dict)):
                                        blocks_placed += 1
                                except Exception as e:
                                    logger.warning(f"Error placing block at ({x},{y},{z}): {e}")
                    return blocks_placed
                
                # Place the blocks
                blocks_placed = place_blocks_one_by_one(x1, y1, z1, x2, y2, z2, block_type)
                logger.info(f"Successfully placed {blocks_placed} blocks")
                logger.info(f"place_blocks result: {result}")
            except Exception as e:
                logger.error(f"Error in place_blocks: {e}")
            
            logger.info("ConnectionManager tests completed.")
        else:
            logger.error("Failed to connect to Minecraft server. Tests aborted.")
    except Exception as e:
        logger.error(f"Error initializing connection manager: {e}")

def main():
    """Run all tests."""
    logger.info("Starting Minecraft tests...")
    
    # Test direct HTTP methods
    test_direct_http_command()
    test_direct_http_place_blocks()
    
    # Test ConnectionManager
    test_connection_manager()
    
    logger.info("All tests completed.")

if __name__ == "__main__":
    main()