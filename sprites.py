import pygame
from os import path
import constants


class Sprites:
    def __init__(self):
        root_folder = path.dirname(__file__)
        # Images
        img_folder = path.join(root_folder, "data", "tiles")

        self.PLAYER = pygame.image.load(
            path.join(img_folder, "tile025.png")).convert_alpha()
        self.CREATURE = pygame.image.load(
            path.join(img_folder, "tile123.png")).convert_alpha()
        #self.WALL = pygame.image.load(
        #    path.join(img_folder, "tile586.png")).convert_alpha()
        #self.WALL_DARK = pygame.image.load(
        #    path.join(img_folder, "tile016.png")).convert_alpha()
        #self.FLOOR = pygame.image.load(
        #    path.join(img_folder, "tile587.png")).convert_alpha()
        #self.FLOOR_DARK = pygame.image.load(
        #    path.join(img_folder, "tile002.png")).convert_alpha()
        self.WALL = pygame.Surface((16,16))
        self.WALL.fill((194,194,199))
        self.WALL_DARK = pygame.Surface((16,16))
        self.WALL_DARK.fill((0,0,100))
        self.FLOOR = pygame.Surface((16,16))
        self.FLOOR.fill((95,87,79))
        self.FLOOR_DARK = pygame.Surface((16,16))
        self.FLOOR_DARK.fill((50,50,150))

