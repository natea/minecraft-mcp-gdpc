from gdpc import __version__
from gdpc import interface
from gdpc.exceptions import RequestConnectionError

# Print GDPC version
print(f"Using GDPC version: {__version__}")

# Connect to the Minecraft server via HTTP interface
try:
    # Set the host and port (default port for HTTP interface is 9000)
    # These are used implicitly by the interface functions
    host = "localhost"
    port = 9000
    
    print(f"Attempting to connect to Minecraft server at {host}:{port}")
    
    # Test connection by getting the server version
    version = interface.getVersion(host, port)
    print(f"Successfully connected to Minecraft server! Version: {version}")
    
    # Get build area
    build_area = interface.getBuildArea(host, port)
    print(f"Build area: {build_area}")
    
    # Get player positions
    players = interface.getPlayers(host, port)
    if players:
        print(f"Players online: {players}")
        # Use the first player's position for our example
        player_name = list(players.keys())[0]
        player_pos = players[player_name]["position"]
        x, y, z = int(player_pos[0]), int(player_pos[1]), int(player_pos[2])
        print(f"Using position of player {player_name}: ({x}, {y}, {z})")
        
        # Place a simple block near the player
        interface.placeBlocks(host, port, x + 3, y, z + 3, x + 3, y, z + 3, ["minecraft:stone"])
        print("Placed a stone block near the player")
        
        # Place a small structure (3x3 platform)
        blocks = ["minecraft:oak_planks"] * 9  # 9 oak plank blocks
        interface.placeBlocks(host, port, x - 1, y - 1, z - 1, x + 1, y - 1, z + 1, blocks)
        print("Created a small wooden platform under the player")
    else:
        print("No players online. Please join the server to test block placement.")
    
except RequestConnectionError as e:
    print(f"Failed to connect to the Minecraft server: {e}")
    print("Make sure the server is running with the GDMC HTTP Interface mod installed.")
    print("Check that the server is accessible at localhost:9000")
except Exception as e:
    print(f"An error occurred: {e}")
    import traceback
    traceback.print_exc()