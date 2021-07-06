import pygame
import constants

from engine import Engine
from sprites import *
from map import Map, DungeonTileSet
import entity_factory


def game():
    pygame.init()

    main_surface = pygame.display.set_mode((
        constants.MAP_WIDTH * constants.SPRITE_SIZE,
        constants.MAP_HEIGHT * constants.SPRITE_SIZE))
    pygame.display.set_caption("Reddit makes a roguelike")

    sprites = Sprites()
    current_map = Map(constants.MAP_WIDTH,
                      constants.MAP_HEIGHT, DungeonTileSet())

    x, y = current_map.get_empty_position()
    player = entity_factory.A_Player(sprites, x, y)
    x, y = current_map.get_empty_position()
    creature = entity_factory.A_Creature(sprites, x, y)

    entities = [player, creature]
    engine = Engine(current_map, entities)

    while (True):
        engine.update()
        engine.render(main_surface)


if __name__ == "__main__":
    game()
