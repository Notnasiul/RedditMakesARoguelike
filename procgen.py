import entity_factory
import random

max_items_by_floor = [
    (1, 5),
    (4, 2)
]

max_monsters_by_floor = [
    (1, 2),
    (4, 3),
    (6, 5)
]

monster_chances = {
    0: [(entity_factory.A_Creature, 100)],
    3: [(entity_factory.A_Creature, 100)]
}

items_chances = {
    0: [(entity_factory.A_HealingPotion, 50), (entity_factory.A_Dinamite, 50)],
    3: [(entity_factory.A_HealingPotion, 20), (entity_factory.A_Dinamite, 80)],
}


def fill_with_solid(map):
    return [[map.tileset.wall
             for y in range(0, map.height)]
            for x in range(0, map.width)]


def create_cave(map):
    map.reset()
    fill_with_solid(map)
    start_walls = (int)(map.width * map.height * 0.3)
    for i in range(0, start_walls):
        x = random.randint(1, map.width-1)
        y = random.randint(1, map.height-1)
        if x != y != 5:
            map.tiles[x][y] = map.tileset.wall
    iterations = 10
    neighbour_deltas = [(x, y) for x in range(-1, 2)
                        for y in range(-1, 2) if x != 0 or y != 0]
    for j in range(0, iterations):
        tmp_tiles = map.tiles.copy()
        for x in range(1, map.width-1):
            for y in range(1, map.height-1):
                sum = 0
                for delta in neighbour_deltas:
                    dx, dy = delta
                    if map.tiles[x+dx][y+dy].blocks_path:
                        sum = sum + 1
                if tmp_tiles[x][y].blocks_path:
                    tmp_tiles[x][y] = map.tileset.floor if sum >= 3 else map.tiles.wall
                else:
                    tmp_tiles[x][y] = map.tileset.floor if sum >= 5 else map.tiles.wall
        map.tiles = tmp_tiles.copy()


def create_roomed_maze(map, map_width, map_height, max_rooms, min_room_size, max_room_size, floor):
    map.reset()
    fill_with_solid(map)
    rooms = []
    center_of_last_room = (0, 0)
    for r in range(max_rooms):
        w = random.randint(min_room_size, max_room_size)
        h = random.randint(min_room_size, max_room_size)
        x = random.randint(0, map_width - w - 1)
        y = random.randint(0, map_height - h - 1)
        room = RectangularRoom(x, y, w, h, map)
        for r in rooms:
            if room.intersect(r):
                break
        else:
            room.carve_room()
            room_count = len(rooms)
            if room_count > 0:
                last_room = rooms[-1]
                last_x, last_y = last_room.center()
                x, y, = room.center()
                if random.random() < 0.5:
                    create_horizontal_tunnel(map, last_x, x, last_y)
                    create_vertical_tunnel(map, last_y, y, x)
                else:
                    create_vertical_tunnel(map, last_y, y, last_x)
                    create_horizontal_tunnel(map, last_x, x, y)
            rooms.append(room)
            center_of_last_room = room.center()
            if room_count == 0:
                entity_factory.A_Player(
                    center_of_last_room[0], center_of_last_room[1], map)

    map.downstairs_location = center_of_last_room
    map.tiles[center_of_last_room[0]
              ][center_of_last_room[1]] = map.tileset.downstairs
    map.rooms = rooms

    place_monsters(map, floor)
    place_items(map, floor)


def place_monsters(map, floor):
    creatureindex = 0
    for room in map.rooms:
        amount = random.randint(
            0, get_max_value_for_floor(max_monsters_by_floor, floor))
        for _ in range(amount):
            x, y = room.get_empty_position()
            monster = get_entity_at_random(monster_chances, floor)[0]
            monster(x, y, creatureindex, map)
        creatureindex += 1


def place_items(map, floor):
    creatureindex = 0
    for room in map.rooms:
        amount = random.randint(
            0, get_max_value_for_floor(max_items_by_floor, floor))
        for _ in range(amount):
            x, y = room.get_empty_position()
            item = get_entity_at_random(items_chances, floor)[0]
            item(x, y, map)


def get_max_value_for_floor(weighted_chances_by_floor, floor):
    current_value = 0
    for floor_min, value in weighted_chances_by_floor:
        if floor_min > floor:
            break
        else:
            current_value = value
    return current_value


def get_entity_at_random(entity_weights, floor):
    entity_weighted_chances = {}
    for key, values in entity_weights.items():
        if key > floor:
            break
        else:
            for value in values:
                entity = value[0]
                chance = value[1]
                entity_weighted_chances[entity] = chance

    entities = list(entity_weighted_chances.keys())
    weights = list(entity_weighted_chances.values())
    chosen_entities = random.choices(entities, weights, k=1)
    return chosen_entities


def create_horizontal_tunnel(map, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2)+1):
        map.tiles[x][y] = map.tileset.floor


def create_vertical_tunnel(map, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map.tiles[x][y] = map.tileset.floor


class RectangularRoom:
    def __init__(self, x, y, width, height, current_map):
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + width, y + height
        self.current_map = current_map

    def center(self):
        centerx = (self.x1 + self.x2) // 2
        centery = (self.y1 + self.y2) // 2
        return centerx, centery

    def carve_room(self):
        for x in range(self.x1 + 1, self.x2):
            for y in range(self.y1 + 1, self.y2):
                self.current_map.tiles[x][y] = self.current_map.tileset.floor

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
            if tileFound:
                for a in self.current_map.actors:
                    if a.x == x and a.y == y:
                        tileFound = False
                for i in self.current_map.items:
                    if i.x == x and i.y == y:
                        tileFound = False
        return x, y
