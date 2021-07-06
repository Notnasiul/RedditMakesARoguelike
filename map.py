from os import X_OK
import constants
import pygame
import random
from sprites import *
import fov


class Tile:
    def __init__(self, lit_sprite, dark_sprite, blocks_path, blocks_sight):
        self.block_path = blocks_path
        self.blocks_sight = blocks_sight
        self.explored = False
        self.lit_sprite = lit_sprite
        self.dark_sprite = dark_sprite

    def draw(self, surface, x, y, inFov, visited):
        sprite = None
        if inFov:
            sprite = self.lit_sprite
        else:
            if visited:
                sprite = self.dark_sprite
        if sprite:
            surface.blit(sprite, (x * constants.CELL_WIDTH, y * constants.CELL_HEIGHT))

class Map:
    def __init__(self, width, height, tileset):
        self.width = constants.MAP_WIDTH
        self.height = constants.MAP_HEIGHT
        self.rooms = []

        self.tileset = tileset

        self.tiles = self.fill_with_solid(self.width, self.height)
        self.visited = {}
        self.fov = {}
        
        self.create_roomed_maze(constants.MAP_WIDTH, constants.MAP_HEIGHT, constants.MAX_ROOMS,
                                constants.MIN_ROOM_SIZE, constants.MAX_ROOM_SIZE)

    def update_fov(self, x, y, sight_range):
        self.fov = fov.FOV_Bresenham(x, y, sight_range, self)        

    def draw(self, surface):
        for x in range(0, constants.MAP_WIDTH):
            for y in range(0, constants.MAP_HEIGHT):
                in_fov = (x,y) in self.fov
                visited = (x,y) in self.visited
                if in_fov and not visited:
                    self.visited[x,y] = True

                self.tiles[x][y].draw(surface,x,y,in_fov,visited)

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def in_fov(self, x, y):
        return (x,y) in self.fov
            

    def get_empty_position(self):
        tileFound = False
        tile = None
        x,y = 0,0
        while (tileFound == False):
            x = random.randint(1, self.width-1)
            y = random.randint(1, self.height-1)
            tile = self.tiles[x][y]
            tileFound = tile.block_path == False
        return x, y

    def fill_with_solid(self, width, height):
        return [[self.tileset.wall
                 for y in range(0, height)]
                for x in range(0, width)]

    def create_cave(self):
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
                        if self.tiles[x+dx][y+dy].block_path:
                            sum = sum + 1
                    if tmp_tiles[x][y].block_path:
                        tmp_tiles[x][y] = self.tileset.floor if sum >= 3 else self.tiles.wall
                    else:
                        tmp_tiles[x][y] = self.tileset.floor if sum >= 5 else self.tiles.wall
            self.tiles = tmp_tiles.copy()

    def create_roomed_maze(self, map_width, map_height, max_rooms, min_room_size, max_room_size):
        rooms = []

        for r in range(max_rooms):
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            x = random.randint(0, map_width - w - 1)
            y = random.randint(0, map_height - h - 1)

            room = RectangularRoom(x, y, w, h)
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
        
        self.rooms = rooms

    def create_horizontal_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2)+1):
            print(x)
            self.tiles[x][y] = self.tileset.floor

    def create_vertical_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y] = self.tileset.floor

class RectangularRoom:
    def __init__(self, x, y, width, height):
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + width, y + height

    def center(self):
        centerx = (self.x1 + self.x2) // 2
        centery = (self.y1 + self.y2) // 2
        return centerx, centery

    def carve_room(self, map):
        for x in range(self.x1 + 1, self.x2):
            for y in range(self.y1 + 1, self.y2):
                map.tiles[x][y]  = map.tileset.floor

    def intersect(self, other):
        return self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1


class DungeonTileSet:
    def __init__(self):
        sprites = Sprites()
        self.wall = Tile(sprites.WALL,sprites.WALL_DARK,True,True)
        self.floor = Tile(sprites.FLOOR,sprites.FLOOR_DARK,False,False)

