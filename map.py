from constants import *
import random
import fov
import entity_factory
import lzma
import pickle
import procgen


class GameWorld:
    def __init__(self, engine, size, max_rooms, min_max_room_size, current_floor):
        self.engine = engine
        self.width, self.height = size
        self.max_rooms = max_rooms
        self.min_room_size = min_max_room_size[0]
        self.max_room_size = min_max_room_size[1]
        self.current_floor = current_floor

    def generate_floor(self):
        self.current_floor += 1
        self.engine.current_map.build_level(
            self.width, self.height, self.max_rooms, self.min_room_size, self.max_room_size, self.current_floor)


class Tile:
    def __init__(self, lit_sprite, dark_sprite, blocks_path, blocks_sight):
        self.blocks_path = blocks_path
        self.blocks_sight = blocks_sight
        self.explored = False
        self.lit_sprite = lit_sprite
        self.dark_sprite = dark_sprite

    def get_tile_sprite(self, inFov, visited):
        sprite = None
        if inFov:
            sprite = self.lit_sprite
        else:
            if visited:
                sprite = self.dark_sprite
        return sprite


class Map:
    def __init__(self, width, height, tileset):
        self.width = width
        self.height = height
        self.tileset = tileset
        self.reset()

    def reset(self):
        self.tiles = procgen.fill_with_solid(self)
        self.rooms = []
        self.actors = []
        self.items = []
        self.visited = {}
        self.fov = {}
        self.downstairs_location = (0, 0)

    def build_level(self, map_width, map_height, max_rooms, min_room_size, max_room_size, floor):
        self.reset()
        procgen.fill_with_solid(self)
        procgen.create_roomed_maze(self, map_width, map_height, max_rooms,
                                   min_room_size, max_room_size, floor)

    def update_fov(self, x, y, sight_range):
        self.fov = fov.FOV_Bresenham(x, y, sight_range, self)

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def in_fov(self, x, y):
        return (x, y) in self.fov

    def get_empty_position(self):
        tileFound = False
        tile = None
        x, y = 0, 0
        while (tileFound == False):
            x = random.randint(1, self.width-1)
            y = random.randint(1, self.height-1)
            tile = self.tiles[x][y]
            tileFound = tile.blocks_path == False
        return x, y

    def get_actor_at(self, x, y):
        for e in self.actors:
            if (e.x == x and e.y == y):
                return e
        return None

    def get_item_at(self, x, y):
        for i in self.items:
            if (i.x == x and i.y == y):
                return i
        return None

    def get_four_neighbours(self, x, y):
        neighbour_deltas = [(x, y) for x in range(-1, 2)
                            for y in range(-1, 2) if x != 0 or y != 0]
        neighbours = []
        for delta in neighbour_deltas:
            dx, dy = delta
            xx = x + dx
            yy = y + dy
            if 0 < xx and xx < width and 0 < yy and 0 < height:
                neighbours.append(self.tiles[x+dx][y+dy])

    def astar_search(self, start, end):
        open = []
        closed = []
        start_node = Node(start, None)
        goal_node = Node(end, None)
        open.append(start_node)
        while len(open) > 0:
            open.sort()
            current_node = open.pop(0)
            closed.append(current_node)
            if current_node.position == goal_node.position:
                path = []
                while current_node != start_node:
                    path.append(current_node.position)
                    current_node = current_node.parent
                return path[::-1]
            (x, y) = current_node.position
            neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
            random.shuffle(neighbors)
            for next in neighbors:
                (x, y) = next
                blocks_path = self.tiles[x][y].blocks_path
                if blocks_path:
                    continue
                neighbor = Node(next, current_node)
                if neighbor in closed:
                    continue
                neighbor.g = abs(neighbor.position[0] - start_node.position[0]) + abs(
                    neighbor.position[1] - start_node.position[1])
                neighbor.h = abs(neighbor.position[0] - goal_node.position[0]) + abs(
                    neighbor.position[1] - goal_node.position[1])
                neighbor.f = neighbor.g + neighbor.h
                if not neighbor in open:
                    open.append(neighbor)
                else:
                    for o in open:
                        if o == neighbor and neighbor.f > o.f:
                            open.append(neighbor)
        return None


class Node:
    # Initialize the class
    def __init__(self, position, parent):
        self.position = position
        self.parent = parent
        self.g = 0  # Distance to start node
        self.h = 0  # Distance to goal node
        self.f = 0  # Total cost
    # Compare nodes

    def __eq__(self, other):
        return self.position == other.position
    # Sort nodes

    def __lt__(self, other):
        return self.f < other.f
    # Print node

    def __repr__(self):
        return ('({0},{1})'.format(self.position, self.f))


class DungeonTileSet:
    def __init__(map):
        map.wall = Tile("wall_light_dirt.png",
                        "wall_dark_dirt.png", True, True)
        map.floor = Tile("floor_light.png", "floor_dark.png", False, False)
        map.downstairs = Tile("mine_door.png", "mine_door.png", False, False)
