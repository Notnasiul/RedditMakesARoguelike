import pygame
import components
import os
import textwrap
import sprites
from constants import *
import math


class Renderer():
    def __init__(self):
        self.sprites = sprites.SpriteDealer()

        self.base_res = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        self.double_res = pygame.Surface(
            (GAME_RESOLUTION_X, GAME_RESOLUTION_Y))

        self.dungeon_surface = pygame.Surface(
            (MAP_WIDTH*CELL_WIDTH, MAP_HEIGHT*CELL_HEIGHT))

        self.dungeon_surfacex2 = pygame.Surface(
            (self.dungeon_surface.get_width()*2, self.dungeon_surface.get_height()*2))

        self.inventory_surface = pygame.Surface(
            (250, 400))

        self.CURSOR = self.sprites.get_sprite("cursor.png")

        self.small_font = pygame.font.Font(os.path.join(
            "data", "fonts", "PressStart2P-Regular.ttf"), 8)
        self.mid_font = pygame.font.Font(os.path.join(
            "data", "fonts", "PressStart2P-Regular.ttf"), 16)
        self.large_font = pygame.font.Font(os.path.join(
            "data", "fonts", "PressStart2P-Regular.ttf"), 24)

    def render_game(self, engine, surface):
        surface.fill(COLOR_BLACK)
        self.base_res.fill(COLOR_BLACK)
        self.dungeon_surface.fill(COLOR_BLACK)

        # DRAW MAP
        for y in range(0, MAP_HEIGHT):
            for x in range(0, MAP_WIDTH):
                in_fov = (x, y) in engine.current_map.fov
                visited = (x, y) in engine.current_map.visited
                if in_fov and not visited:
                    engine.current_map.visited[x, y] = True

                #visited = True

                sprite_key = engine.current_map.tiles[x][y].get_tile_sprite(
                    True, visited
                )
                if sprite_key:
                    sprite = self.sprites.get_sprite(sprite_key)
                    # px = engine.player.x
                    # py = engine.player.y
                    # distance_to_player = math.sqrt(
                    #     (x-px)*(x-px) + (y-py)*(y-py))
                    # dist_mod = 1 - distance_to_player / 5

                    lit = pygame.Surface((CELL_HEIGHT, CELL_WIDTH))
                    lit.blit(sprite, (0, 0))
                    # dist_mod = 1 - max(0.25, min(1, distance_to_player / 5))
                    lit_mod = 1 if in_fov else 0.2 if visited else 0
                    if lit_mod < 1:
                        lit.fill((lit_mod*255, lit_mod*128, lit_mod*64, 255),
                                 special_flags=pygame.BLEND_MULT)
                    else:
                        lit = sprite
                    self.dungeon_surface.blit(lit, (x * CELL_WIDTH,
                                                    y * CELL_HEIGHT))
                    # self.dungeon_surface.blit(sprite, (x * CELL_WIDTH,
                    #                                  y * CELL_HEIGHT))

        # DRAW ITEMS
        for item in engine.current_map.items:
            renderer = item.get_component(components.RendererComponent)
            if renderer != None:
                if engine.current_map.in_fov(item.x, item.y):
                    sprite = self.sprites.get_sprite(renderer.sprite)
                    if sprite:
                        self.dungeon_surface.blit(sprite, (item.x * CELL_WIDTH,
                                                           item.y * CELL_HEIGHT))
        # DRAW ACTORS
        for actor in engine.current_map.actors:
            renderer = actor.get_component(components.RendererComponent)
            if renderer != None:
                if engine.current_map.in_fov(actor.x, actor.y):
                    sprite = self.sprites.get_sprite(renderer.sprite)
                    if sprite:
                        self.dungeon_surface.blit(sprite, (actor.x * CELL_WIDTH,
                                                           actor.y * CELL_HEIGHT))

        self.base_res.blit(self.dungeon_surface, (0, 0))
        self.render_UI(engine, self.base_res)
        mx, my = pygame.mouse.get_pos()
        self.base_res.blit(self.CURSOR, (mx/2-8, my/2-8))

        pygame.transform.scale(
            self.base_res, (GAME_RESOLUTION_X, GAME_RESOLUTION_Y), self.double_res)
        surface.blit(self.double_res, (0, 0))

        pygame.display.flip()

    def render_UI(self, engine, surface):
        # Health bar
        health = engine.player.get_component(components.HealthComponent)
        self.render_bar(surface, 8, GAME_HEIGHT-84, health.hp, health.max_hp, "HP", 200, 15,
                        2, COLOR_DARK_MAX, COLOR_LIGHT_MIN, COLOR_BLACK)

        # Message Log
        self.render_message_log(engine, surface, 8,
                                GAME_HEIGHT-64, GAME_WIDTH, 50)

        if engine.show_inventory:
            self.render_actor_inventory(engine, surface, engine.player)

        # Help
        if engine.help_message is not "":
            label = self.small_font.render(
                f"{engine.help_message}", True, COLOR_DARK_MAX)
            lw = label.get_width() * 1.5
            lh = label.get_height()
            x = GAME_WIDTH/2 - lw/2
            y = GAME_HEIGHT - lh*2.5
            message_area = pygame.draw.rect(surface, COLOR_LIGHT_MED,
                                            pygame.Rect(x, y, lw, lh*2))
            pygame.draw.rect(surface, COLOR_DARK_MIN,
                             pygame.Rect(x, y, lw, lh*2), 1)
            surface.blit(label, (x + message_area.width/2 - label.get_width() /
                                 2, y + message_area.height/2 - lh/2))

    def render_actor_inventory(self, engine, surface, actor):
        inventoryComponent = actor.get_component(components.InventoryComponent)
        number_of_items_in_inventory = len(inventoryComponent.inventory.items)

        self.inventory_surface.fill(COLOR_LIGHT_MED)

        window_width = self.inventory_surface.get_width()
        window_height = self.inventory_surface.get_height()

        title = self.small_font.render("INVENTORY", True, COLOR_DARK_MAX)
        self.inventory_surface.blit(
            title, (window_width/2-title.get_width()/2, 15))

        if number_of_items_in_inventory == 0:
            text = self.small_font.render(
                "-- Empty --", True, COLOR_DARK_MAX)
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

        pygame.draw.rect(self.inventory_surface, COLOR_DARK_MAX,
                         self.inventory_surface.get_rect(),  1)
        surface.blit(self.inventory_surface, (GAME_WIDTH-window_width, 0))

    def render_bar(self, surface, x, y, value, max_value, text, width, height, border, bkg_color, fg_color, txt_color):

        pygame.draw.rect(surface, bkg_color, pygame.Rect(x, y, width, height))
        if value > 0:
            pygame.draw.rect(surface, fg_color, pygame.Rect(
                x+border, y+border,
                width * (value/max_value) - border*2, height-border*2))

        label = self.small_font.render(
            f"{text}: {value}/{max_value}", True, txt_color)
        surface.blit(label, (x+border*2, y + height/2 - 3))

    def render_message_log(self, engine, surface, x, y, width, height):
        y_offset = 0
        messages = engine.message_log.messages
        for message in reversed(messages):
            for line in reversed(textwrap.wrap(message.full_text, width)):
                label = self.small_font.render(line, True, message.color)
                surface.blit(label, (x, y+y_offset))
                y_offset += 10
                if y_offset > height:
                    return

    #
    #   MAIN MENU
    #

    def render_main_menu(self, surface):
        title_text = self.large_font.render(
            "Howling Dog Mine", True, COLOR_LIGHT_MAX)
        new_game_text = self.mid_font.render(
            "1) New game", True, COLOR_LIGHT_MAX)
        continue_game_text = self.mid_font.render(
            "2) Continue", True, COLOR_LIGHT_MAX)

        surface.fill(COLOR_BLACK)
        surface.blit(
            title_text, (GAME_RESOLUTION_X//2 - title_text.get_rect().centerx, GAME_RESOLUTION_Y//2 - title_text.get_rect().centery))
        surface.blit(
            new_game_text, (GAME_RESOLUTION_X//2 -
                            new_game_text.get_rect().centerx, GAME_RESOLUTION_Y//2 + 150))
        surface.blit(
            continue_game_text, (GAME_RESOLUTION_X//2 -
                                 continue_game_text.get_rect().centerx, GAME_RESOLUTION_Y//2 + 175))
        pygame.display.flip()
