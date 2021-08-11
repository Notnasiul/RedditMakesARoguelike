from actions import ImpossibleAction
from constants import *
from message_log import MessageLog
from map import Map, GameWorld, DungeonTileSet


class Engine():
    def __init__(self):
        self.message_log = MessageLog()
        self.current_actor = 0
        self.current_map = Map(MAP_WIDTH, MAP_HEIGHT, DungeonTileSet())
        self.game_world = GameWorld(
            self, (MAP_WIDTH, MAP_HEIGHT), MAX_ROOMS, (MIN_ROOM_SIZE, MAX_ROOM_SIZE), 0)
        self.game_world.generate_floor()
        self.player = self.current_map.actors[0]
        self.help_message = ""
        self.show_inventory = False
        self.in_game = True

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
