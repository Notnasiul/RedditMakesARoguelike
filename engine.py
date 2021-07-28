import pygame
import components
import behaviours
from actions import ImpossibleAction
from render_functions import *
from constants import *
import random
from message_log import MessageLog


class Engine():
    def __init__(self, map):
        self.message_log = MessageLog()
        self.current_actor = 0
        self.current_map = map
        self.player = self.current_map.entities[0]
        self.dungeon_surface = pygame.Surface(
            (GAME_WIDTH*CELL_WIDTH, GAME_HEIGHT*CELL_HEIGHT))

    def update(self):
        actor = self.current_map.entities[self.current_actor]

        # Move player
        if actor.is_player:
            self.current_map.update_fov(actor.x, actor.y, 5)
            done = self.evaluate_actions(actor)
            if done:
                actor = self.next_actor()

        # Move all enemies at the same time
        while (actor.is_player == False):
            self.evaluate_actions(actor)
            actor = self.next_actor()

    def evaluate_actions(self, actor):
        if actor.is_alive == False:
            return

        behaviour = actor.behaviour
        behaviour.evaluate(actor, self)
        action = actor.get_action()
        if action is not None:
            while (True):
                action_result = action.perform(self)
                if action_result.alternate == None:
                    return True
                else:
                    if type(action_result.alternate) == ImpossibleAction:
                        return False
                action = action_result.alternate
        return False

    def next_actor(self):
        self.current_actor = (self.current_actor +
                              1) % len(self.current_map.entities)
        return self.current_map.entities[self.current_actor]

    def render(self, surface):
        surface.fill(COLOR_BLACK)

        self.dungeon_surface.fill(COLOR_GREY_DARKER)
        self.current_map.draw(self.dungeon_surface)

        for item in self.current_map.items:
            renderer = item.get_component(components.RendererComponent)
            if renderer != None:
                if self.current_map.in_fov(item.x, item.y):
                    renderer.draw(self.dungeon_surface, item.x, item.y)

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
        # Health bar
        health = self.player.get_component(components.HealthComponent)
        render_bar(surface, 10, 475, health.hp, health.max_hp, "HP: ", 200, 25,
                   2, COLOR_DARK_MIN, COLOR_LIGHT_MIN, COLOR_BLACK)

        # Message Log
        self.message_log.render(surface, 10, 510, 750, 80)
