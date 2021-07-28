import random
import actions
import pygame
import math
import constants
import components


class Behaviour():
    def __init__(self):
        pass

    def evaluate(self, actor, engine):
        self.strategy.evaluate(actor, engine)


class KeyboardMouseInputBehaviour(Behaviour):
    def __init__(self):
        super().__init__()
        self.last_keyboard_inputs = pygame.key.get_pressed()

    def evaluate(self, actor, engine):
        events_list = pygame.event.get()
        for event in events_list:
            if event.type == pygame.QUIT:
                raise SystemExit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                cellX = math.floor(x / constants.CELL_WIDTH)
                cellY = math.floor(y / constants.CELL_HEIGHT)
                # print('clicked on ' + str(cellX) + ' ' + str(cellY))
                equipment = actor.get_component(components.Equipment)
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

                self.last_keyboard_inputs = keys


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
        # print("evaluating " + actor.name)
        path = engine.current_map.astar_search(
            (actor.x, actor.y),
            (engine.player.x, engine.player.y)
        )

        if path is None or path == []:
            return

        dx = path[0][0] - actor.x
        dy = path[0][1] - actor.y

        actor.next_action = actions.WalkAction(
            actor,
            dx, dy
        )
