import pygame
import components
import behaviours
from render_functions import *
from constants import *


class Engine():
    def __init__(self, map):
        self.current_actor = 0
        self.current_map = map

        self.dungeon_surface = pygame.Surface(
            (GAME_WIDTH*CELL_WIDTH, GAME_HEIGHT*CELL_HEIGHT))

    def update(self):
        actor = self.current_map.entities[self.current_actor]
        is_alive = actor.get_component(components.IsDead) == None
        if (is_alive):
            behaviour = actor.behaviour
            if (behaviour):
                behaviour.evaluate(actor, self.current_map, self)
            else:
                self.current_actor = (
                    self.current_actor + 1) % len(self.current_map.entities)
        else:

            self.current_actor = (
                self.current_actor + 1) % len(self.current_map.entities)

        action = actor.get_action()
        if action is not None:
            while (True):
                action_result = action.perform()
                if action_result.alternate == None:
                    break
                action = action_result.alternate

            self.current_actor = (self.current_actor +
                                  1) % len(self.current_map.entities)

    def render(self, surface):
        surface.fill(COLOR_BLACK)

        # render dungeon
        self.dungeon_surface.fill(COLOR_GREY_DARKER)
        self.current_map.draw(self.dungeon_surface)
        for actor in self.current_map.entities:
            renderer = actor.get_component(components.RendererComponent)
            if renderer != None:
                if self.current_map.in_fov(actor.x, actor.y):
                    renderer.draw(self.dungeon_surface, actor.x, actor.y)
        surface.blit(self.dungeon_surface, pygame.Rect(
            0, 0, GAME_WIDTH*CELL_WIDTH, GAME_HEIGHT*CELL_HEIGHT))

        self.render_UI(surface)
        pygame.display.flip()

    def render_UI(self, surface):
        render_bar(surface, 10, 10, 25, 75, "HP: ", 200, 20,
                   2, COLOR_GREY_DARKER, COLOR_GREY, COLOR_WHITE)
