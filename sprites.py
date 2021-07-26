import pygame
from os import path
from constants import *

root_folder = path.dirname(__file__)
img_folder = path.join(root_folder, "data", "tiles")


def load_sprite(filename):
    return pygame.image.load(path.join(img_folder, filename)).convert_alpha()


def fake_sprite(color):
    spr = pygame.Surface((CELL_WIDTH, CELL_WIDTH))
    spr.fill(color)
    return spr
