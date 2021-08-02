import pygame
import components
import behaviours
from actions import ImpossibleAction
from render_functions import *
from constants import *
import random
from message_log import MessageLog
import os


class Engine():
    def __init__(self, map):
        self.message_log = MessageLog()
        self.current_actor = 0
        self.current_map = map
        self.player = self.current_map.actors[0]

        self.dungeon_surface = pygame.Surface(
            (MAP_WIDTH*CELL_WIDTH, MAP_HEIGHT*CELL_HEIGHT))

        self.dungeon_surfacex2 = pygame.Surface(
            (self.dungeon_surface.get_width()*2, self.dungeon_surface.get_height()*2))

        self.inventory_surface = pygame.Surface(
            (250, 400))

        self.show_inventory = False

        self.small_font = pygame.font.Font(os.path.join(
            "data", "fonts", "PressStart2P-Regular.ttf"), 8)
        self.mid_font = pygame.font.Font(os.path.join(
            "data", "fonts", "PressStart2P-Regular.ttf"), 16)

        self.help_message = ""

    def __getstate__(self):
        d = dict(self.__dict__)
        del d['dungeon_surface']
        del d['dungeon_surfacex2']
        del d['inventory_surface']
        del d['small_font']
        del d['mid_font']
        return d

    def update(self):
        actor = self.current_map.actors[self.current_actor]

        # Process player Input
        if actor.is_player and actor.is_alive:
            self.current_map.update_fov(actor.x, actor.y, 5)
            done = self.evaluate_actions(actor)
            if done:
                actor = self.next_actor()
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise SystemExit()

        # Move all enemies at the same time
        while (actor.is_player == False):
            self.evaluate_actions(actor)
            actor = self.next_actor()

    def evaluate_actions(self, actor):
        if actor.is_alive == False:
            return True

        behaviour = actor.behaviour
        behaviour.evaluate(actor, self)
        action = actor.get_action()
        if action is not None:
            while (True):
                action_result = action.perform(self)
                if action_result == None:
                    return False
                if action_result.alternate == None:
                    return True
                if type(action_result.alternate) == ImpossibleAction:
                    action_result.alternate.perform(self)
                    return False
                action = action_result.alternate

    def next_actor(self):
        self.current_actor = (self.current_actor +
                              1) % len(self.current_map.actors)
        return self.current_map.actors[self.current_actor]

    def render(self, surface):
        surface.fill(COLOR_BLACK)
        self.dungeon_surface.fill(COLOR_BLACK)
        self.current_map.draw(self.dungeon_surface)

        for item in self.current_map.items:
            renderer = item.get_component(components.RendererComponent)
            if renderer != None:
                if self.current_map.in_fov(item.x, item.y):
                    renderer.draw(self.dungeon_surface, item.x, item.y)

        for actor in self.current_map.actors:
            renderer = actor.get_component(components.RendererComponent)
            if renderer != None:
                if self.current_map.in_fov(actor.x, actor.y):
                    renderer.draw(self.dungeon_surface, actor.x, actor.y)

        pygame.transform.scale(self.dungeon_surface, (self.dungeon_surfacex2.get_width(
        ), self.dungeon_surfacex2.get_height()), self.dungeon_surfacex2)
        surface.blit(self.dungeon_surface, (0, 0))

        self.render_UI(surface)

        if self.show_inventory:
            self.render_actor_inventory(surface, self.player)

        pygame.display.flip()

    def render_UI(self, surface):
        # Health bar
        health = self.player.get_component(components.HealthComponent)
        render_bar(self, surface, 10, 475, health.hp, health.max_hp, "HP", 200, 25,
                   2, COLOR_DARK_MAX, COLOR_LIGHT_MIN, COLOR_BLACK)

        # Message Log
        self.message_log.render(self, surface, 10, 510, 750, 80)

        # Help
        if self.help_message is not "":
            label = self.small_font.render(
                f"{self.help_message}", True, COLOR_DARK_MAX)
            lw = label.get_width()
            lh = label.get_height()
            x = GAME_WIDTH/2 - lw/2
            y = GAME_HEIGHT - lh*2.5
            message_area = pygame.draw.rect(surface, COLOR_LIGHT_MED,
                                            pygame.Rect(x, y, label.get_width()*1.5, label.get_height()*2))
            surface.blit(label, (x + message_area.width/2 - lw /
                                 2, y + message_area.height/2 - lh/2))

    def render_actor_inventory(self, surface, actor):
        inventoryComponent = actor.get_component(components.InventoryComponent)
        number_of_items_in_inventory = len(inventoryComponent.inventory.items)

        self.inventory_surface.fill(COLOR_LIGHT_MED)

        window_width = self.inventory_surface.get_width()
        window_height = self.inventory_surface.get_height()

        title = self.small_font.render("INVENTORY", True, COLOR_DARK_MAX)
        self.inventory_surface.blit(
            title, (window_width/2-title.get_width()/2, 15))

        if number_of_items_in_inventory == 0:
            text = self.small_font.render("-- Empty --", True, COLOR_DARK_MAX)
            self.inventory_surface.blit(
                text, (window_width/2-text.get_width()/2, 40))
        else:
            items = inventoryComponent.inventory.items
            for i in range(number_of_items_in_inventory):
                item = items[i]
                item_key = chr(ord("a") + i)
                entry = self.small_font.render(
                    f"({item_key}) {item.name}", True, COLOR_DARK_MIN)
                self.inventory_surface.blit(entry, (5, 40+i*12))

        surface.blit(self.inventory_surface, (GAME_WIDTH-window_width, 0))
