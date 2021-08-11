from constants import *
import random
import fov
import entity_factory
import lzma
import pickle


class GameWorld:
    def __init__(self, engine, size, max_rooms, min_max_room_size, max_monsters_per_room, max_items_per_room, current_floor):
        self.engine = engine
        self.width, self.height = size
        self.max_rooms = max_rooms
        self.min_room_size = min_max_room_size[0]
        self.max_room_size = min_max_room_size[1]
        self.max_monsters_per_room = max_monsters_per_room
        self.max_items_per_room = max_items_per_room
        self.current_floor = current_floor

    def generate_floor(self):
        self.current_floor += 1
        self.engine.current_map.create_roomed_maze(
            self.width, self.height, self.max_rooms, self.min_room_size, self.max_room_size, self.max_monsters_per_room, self.max_items_per_room)


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
        self.tiles = self.fill_with_solid(self.width, self.height)
        self.rooms = []
        self.actors = []
        self.items = []
        self.visited = {}
        self.fov = {}
        self.downstairs_location = (0, 0)

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

    #
    #
    # UTILITIES
    #
    #

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
    #
    #
    #   BUILDING MAPS
    #
    #

    def fill_with_solid(self, width, height):
        return [[self.tileset.wall
                 for y in range(0, height)]
                for x in range(0, width)]

    def create_cave(self):
        self.fill_with_solid(self.width, self.height)
        start_walls = (int)(self.width * self.height * 0.3)
        for i in range(0, start_walls):
            x = random.randint(1, self.width-1)
            y = random.randint(1, self.height-1)
            if x != y != 5:
                self.tiles[x][y] = self.tileset.wall
        iterations = 10
        neighbour_deltas = [(x, y) for x in range(-1, 2)
                            for y in range(-1, 2) if x != 0 or y != 0]
        for j in range(0, iterations):
            tmp_tiles = self.tiles.copy()
            for x in range(1, self.width-1):
                for y in range(1, self.height-1):
                    sum = 0
                    for delta in neighbour_deltas:
                        dx, dy = delta
                        if self.tiles[x+dx][y+dy].blocks_path:
                            sum = sum + 1
                    if tmp_tiles[x][y].blocks_path:
                        tmp_tiles[x][y] = self.tileset.floor if sum >= 3 else self.tiles.wall
                    else:
                        tmp_tiles[x][y] = self.tileset.floor if sum >= 5 else self.tiles.wall
            self.tiles = tmp_tiles.copy()

    def create_roomed_maze(self, map_width, map_height, max_rooms, min_room_size, max_room_size, max_monsters_per_room, max_items_per_room):
        self.reset()
        self.fill_with_solid(self.width, self.height)
        rooms = []
        center_of_last_room = (0, 0)
        for r in range(max_rooms):
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            x = random.randint(0, map_width - w - 1)
            y = random.randint(0, map_height - h - 1)
            room = RectangularRoom(x, y, w, h, self)
            for r in rooms:
                if room.intersect(r):
                    break
            else:
                room.carve_room(self)
                room_count = len(rooms)
                if room_count > 0:
                    last_room = rooms[-1]
                    last_x, last_y = last_room.center()
                    x, y, = room.center()
                    if random.random() < 0.5:
                        self.create_horizontal_tunnel(last_x, x, last_y)
                        self.create_vertical_tunnel(last_y, y, x)
                    else:
                        self.create_vertical_tunnel(last_y, y, last_x)
                        self.create_horizontal_tunnel(last_x, x, y)
                rooms.append(room)
                center_of_last_room = room.center()
                if room_count == 0:
                    entity_factory.A_Player(
                        center_of_last_room[0], center_of_last_room[1], self)

        self.downstairs_location = center_of_last_room
        self.tiles[center_of_last_room[0]
                   ][center_of_last_room[1]] = self.tileset.downstairs

        creatureindex = 0

        for room in rooms:
            x, y = room.get_empty_position()
            entity_factory.A_Creature(x, y, creatureindex, self)
            creatureindex += 1
            x, y = room.get_empty_position()
            entity_factory.A_HealingPotion(x, y, self)
            x, y = room.get_empty_position()
            entity_factory.A_Dinamite(x, y, self)
        self.rooms = rooms

    def create_horizontal_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2)+1):
            self.tiles[x][y] = self.tileset.floor

    def create_vertical_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y] = self.tileset.floor


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


class RectangularRoom:
    def __init__(self, x, y, width, height, current_map):
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + width, y + height
        self.current_map = current_map

    def center(self):
        centerx = (self.x1 + self.x2) // 2
        centery = (self.y1 + self.y2) // 2
        return centerx, centery

    def carve_room(self, map):
        for x in range(self.x1 + 1, self.x2):
            for y in range(self.y1 + 1, self.y2):
                map.tiles[x][y] = map.tileset.floor

    def intersect(self, other):
        return self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1

    def get_empty_position(self):
        tileFound = False
        tile = None
        x, y = 0, 0
        while (tileFound == False):
            x = random.randint(self.x1+1, self.x2-1)
            y = random.randint(self.y1+1, self.y2-1)
            tile = self.current_map.tiles[x][y]
            tileFound = tile.blocks_path == False
        return x, y


class DungeonTileSet:
    def __init__(self):
        self.wall = Tile("wall_light_dirt.png",
                         "wall_dark_dirt.png", True, True)
        self.floor = Tile("floor_light.png", "floor_dark.png", False, False)
        self.downstairs = Tile("mine_door.png", "mine_door.png", False, False)
