from random import randint, choice
from gdpc import Editor, Block
from gdpc.geometry import placeCuboid, placeCuboidHollow

editor = Editor(buffering=True)

buildArea = editor.getBuildArea()

# Load world slice of the build area
editor.loadWorldSlice(cache=True)

# Get heightmap
heightmap = editor.worldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]

x = buildArea.offset.x + 1
z = buildArea.offset.z + 1

y = heightmap[3,1] - 1

height = randint(3, 7)
depth  = randint(3, 10)

# Random floor palette
floorPalette = [
    Block("stone_bricks"),
    Block("cracked_stone_bricks"),
    Block("cobblestone"),
]

# Choose wall material
wallBlock = choice([
    Block("oak_planks"),
    Block("spruce_planks"),
    Block("white_terracotta"),
    Block("green_terracotta"),
])
print(f"Chosen wall block: {wallBlock}")

# Build main shape
placeCuboidHollow(editor, (x, y, z), (x+4, y+height, z+depth), wallBlock)
placeCuboid(editor, (x, y, z), (x+4, y-5, z+depth), floorPalette)
placeCuboid(editor, (x+1, y+1, z+1), (x+3, y+height-1, z+3), Block("air"))

# Build roof: loop through distance from the middle
for dx in range(1, 4):
    yy = y + height + 2 - dx

    # Build row of stairs blocks
    leftBlock  = Block("oak_stairs", {"facing": "east"})
    rightBlock = Block("oak_stairs", {"facing": "west"})
    placeCuboid(editor, (x+2-dx, yy, z-1), (x+2-dx, yy, z+depth+1), leftBlock)
    placeCuboid(editor, (x+2+dx, yy, z-1), (x+2+dx, yy, z+depth+1), rightBlock)

    # Add upside-down accent blocks
    leftBlock  = Block("oak_stairs", {"facing": "west", "half": "top"})
    rightBlock = Block("oak_stairs", {"facing": "east", "half": "top"})
    for zz in [z-1, z+depth+1]:
        editor.placeBlock((x+2-dx+1, yy, zz), leftBlock)
        editor.placeBlock((x+2+dx-1, yy, zz), rightBlock)

# build the top row of the roof
yy = y + height + 1
placeCuboid(editor, (x+2, yy, z-1), (x+2, yy, z+depth+1), Block("oak_planks"))

# Add a door
doorBlock = Block("oak_door", {"facing": "north", "hinge": "left"})
editor.placeBlock((x+2, y+1, z), doorBlock)

# Clear some space in front of the door
placeCuboid(editor, (x+1, y+1, z-1), (x+3, y+3, z-1), Block("air"))
