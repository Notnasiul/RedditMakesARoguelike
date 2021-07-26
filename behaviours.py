import random
import actions
import pygame
import math
import constants
import components


class Behaviour():
    def __init__(self):
        pass

    def evaluate(self, actor, map, engine):
        self.strategy.evaluate(actor, map, engine)


class KeyboardMouseInputBehaviour(Behaviour):
    def evaluate(self, actor, current_map, engine):
        current_map.update_fov(actor.x, actor.y, 5)
        events_list = pygame.event.get()
        for event in events_list:
            if event.type == pygame.QUIT:
                raise SystemExit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    actor.next_action = actions.WalkAction(
                        actor, engine, 0, -1)
                if event.key == pygame.K_DOWN:
                    actor.next_action = actions.WalkAction(
                        actor, engine, 0, 1)
                if event.key == pygame.K_LEFT:
                    actor.next_action = actions.WalkAction(
                        actor, engine, -1, 0)
                if event.key == pygame.K_RIGHT:
                    actor.next_action = actions.WalkAction(
                        actor, engine, 1, 0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                cellX = math.floor(x / constants.CELL_WIDTH)
                cellY = math.floor(y / constants.CELL_HEIGHT)
                print('clicked on ' + str(cellX) + ' ' + str(cellY))
                equipment = actor.get_component(components.Equipment)
                weapon = None
                if event.button == 1:
                    weapon = equipment.main_weapon
                if event.button == 3:
                    weapon = equipment.secondary_weapon
                if weapon != None:
                    actor.next_action = actions.RangeAttackAction(
                        weapon, actor, (cellX, cellY), engine)


class RandomWalkBehaviour():
    def evaluate(self, actor, map, engine):
        dx = random.randint(-1, 1)
        dy = 0 if dx != 0 else random.randint(-1, 1)
        actor.next_action = actions.WalkAction(
            actor,
            engine,
            dx, dy
        )
