import pygame
from os import path
from constants import *


class SpriteDealer ():
    def __init__(self):
        self.root_folder = path.dirname(__file__)
        self.img_folder = path.join(self.root_folder, "data", "tiles")
        self.sprites = {}

    def get_sprite(self, key):
        if key in self.sprites:
            return self.sprites[key]
        else:
            sprite = self.load_sprite(key)
            self.sprites[key] = sprite
            return sprite

    def load_sprite(self, filename):
        return pygame.image.load(path.join(self.img_folder, filename)).convert_alpha()

    def fake_sprite(self, color):
        spr = pygame.Surface((CELL_WIDTH, CELL_WIDTH))
        spr.fill(color)
        return spr
