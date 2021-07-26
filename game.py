import pygame
from constants import *

from engine import Engine
from sprites import *
from map import Map, DungeonTileSet
import entity_factory


def game():
    pygame.init()
    main_surface = pygame.display.set_mode(
        (GAME_WIDTH, GAME_HEIGHT))
    pygame.display.set_caption("Reddit makes a roguelike")

    current_map = Map(MAP_WIDTH, MAP_HEIGHT, DungeonTileSet())

    x, y = current_map.get_empty_position()
    player = entity_factory.A_Player(x, y, current_map)

    engine = Engine(current_map)

    while (True):
        engine.update()
        engine.render(main_surface)


if __name__ == "__main__":
    game()
