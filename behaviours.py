import random
import actions
import pygame
import math
import constants
import components

import lzma
import pickle


class Behaviour():
    def __init__(self):
        pass

    def evaluate(self, actor, engine):
        self.strategy.evaluate(actor, engine)

    def get_cell_at_mouse_position(self, event):
        x, y = event.pos
        cellX = (x+0.5) // constants.CELL_WIDTH
        cellY = (y+0.5) // constants.CELL_HEIGHT
        cellX //= 2
        cellY //= 2
        return cellX, cellY


class IngameInput(Behaviour):
    def evaluate(self, actor, engine):
        engine.help_message = ""
        events_list = pygame.event.get()
        for event in events_list:
            if event.type == pygame.QUIT:
                raise SystemExit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                cellX, cellY = self.get_cell_at_mouse_position(event)
                equipment = actor.get_component(components.EquipmentComponent)
                weapon = None
                if event.button == 1:
                    weapon = equipment.main_weapon
                if event.button == 3:
                    weapon = equipment.secondary_weapon
                if weapon != None:
                    actor.next_action = actions.RangeAttackAction(
                        weapon, actor, (cellX, cellY))

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()

                if keys[pygame.K_ESCAPE]:
                    actor.next_action = actions.ExitGameAction(actor)

                if keys[pygame.K_UP]:
                    actor.next_action = actions.WalkAction(
                        actor, 0, -1)
                if keys[pygame.K_DOWN]:
                    actor.next_action = actions.WalkAction(
                        actor, 0, 1)
                if keys[pygame.K_LEFT]:
                    actor.next_action = actions.WalkAction(
                        actor, -1, 0)
                if keys[pygame.K_RIGHT]:
                    actor.next_action = actions.WalkAction(
                        actor, 1, 0)
                if keys[pygame.K_SPACE]:
                    actor.next_action = actions.WaitAction()
                if keys[pygame.K_LESS]:
                    actor.next_action = actions.TakeStairsAction(actor)
                if keys[pygame.K_g]:
                    actor.next_action = actions.PickItemAction(
                        actor, actor.x, actor.y)
                if keys[pygame.K_i]:
                    actor.next_action = actions.OpenInventory(actor)

                if keys[pygame.K_s]:
                    save_data = pickle.dumps(engine)
                    with open("test.savedata", "wb") as f:
                        f.write(save_data)


class InventoryInputBehavior(Behaviour):
    def evaluate(self, actor, engine):
        engine.help_message = "Select item to use (a-z)"
        events_list = pygame.event.get()
        for event in events_list:
            if event.type == pygame.QUIT:
                raise SystemExit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Maybe we can select things using Mouse at some point?
                pass

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    actor.next_action = actions.CloseInventory(actor)
                else:
                    item_index = event.key-97
                    if 0 <= item_index < 26:
                        # actor.next_action = actions.SelecInventoryItem(
                        #   actor, item_index)
                        actor.next_action = actions.ConsumeItemAction(
                            actor, item_index)


class ExitGameBehavior(Behaviour):
    def evaluate(self, actor, engine):
        engine.help_message = "Exit game? Press ESC again or any other key to contine"
        events_list = pygame.event.get()
        for event in events_list:
            if event.type == pygame.QUIT:
                raise SystemExit()

            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:
                    engine.in_game = False
                else:
                    actor.next_action = actions.ContinueGameAction(actor)


class SelectMapPositionBehaviour(Behaviour):
    def __init__(self, on_position_selected):
        self.on_position_selected = on_position_selected

    def evaluate(self, actor, engine):
        engine.help_message = "Click on map to use item"
        events_list = pygame.event.get()
        for event in events_list:
            if event.type == pygame.QUIT:
                raise SystemExit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                cellX, cellY = self.get_cell_at_mouse_position(event)
                self.on_position_selected(engine, cellX, cellY)


class RandomWalkBehaviour():
    def evaluate(self, actor, engine):
        dx = random.randint(-1, 1)
        dy = 0 if dx != 0 else random.randint(-1, 1)
        actor.next_action = actions.WalkAction(
            actor,
            dx, dy
        )


class ChasingBehaviour():
    def __init__(self):
        self.target = None

    def evaluate(self, actor, engine):
        path = engine.current_map.astar_search(
            (actor.x, actor.y),
            (engine.player.x, engine.player.y)
        )

        if path is None or path == []:
            return

        dx = path[0][0] - actor.x
        dy = path[0][1] - actor.y

        if len(path) > 5:
            dx = random.randint(-1, 1)
            dy = 0 if dx != 0 else random.randint(-1, 1)

        actor.next_action = actions.WalkAction(
            actor,
            dx, dy
        )
