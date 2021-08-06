import pygame
from constants import *

from engine import Engine
from sprites import *
from map import Map, DungeonTileSet
import entity_factory
import os

import pickle
from renderer import Renderer


class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Reddit makes a roguelike")
        self.main_surface = pygame.display.set_mode(
            (GAME_WIDTH, GAME_HEIGHT))
        self.renderer = Renderer()
        self.clock = pygame.time.Clock()

    def load_game(self):
        if os.path.isfile("test.savedata"):
            with open("test.savedata", "rb") as f:
                self.engine = pickle.loads(f.read())
                assert isinstance(self.engine, Engine)

    def start_new_game(self):
        current_map = Map(MAP_WIDTH, MAP_HEIGHT, DungeonTileSet())
        x, y = current_map.rooms[0].get_empty_position()
        player = entity_factory.A_Player(x, y, current_map)
        self.engine = Engine(current_map)
        self.engine.player = player
        self.engine.message_log.add_message(
            "Welcome!", COLOR_TRUE_WHITE, False)

    def begin_game(self):
        self.run()

    def run(self):
        self.engine.in_game = True
        while (self.engine.in_game):
            dt = self.clock.tick(15)
            self.engine.update()
            self.renderer.render_game(self.engine, self.main_surface)
        self.main_menu()

    def main_menu(self):
        in_main_menu = True
        while (in_main_menu):
            dt = self.clock.tick(15)
            self.renderer.render_main_menu(self.main_surface)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.start_new_game()
                        in_main_menu = False
                    if event.key == pygame.K_2:
                        self.load_game()
                        in_main_menu = False
        self.begin_game()


game = Game()
if __name__ == "__main__":
    game.main_menu()
