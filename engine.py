import pygame
import constants
import components
import behaviours


class Engine():
    def __init__(self, map, entities):
        self.current_actor = 0
        self.current_map = map
        self.entities = entities
        self.objects = []

    def update(self):
        actor = self.entities[self.current_actor]
        is_alive = actor.get_component(components.IsDead) == None
        if (is_alive):
            brain = actor.get_component(behaviours.Brain)
            if (brain):
                brain.evaluate(actor, self.current_map, self)
            else:
                self.current_actor = (
                    self.current_actor + 1) % len(self.entities)

        action = actor.get_action()
        if action is not None:
            while (True):
                action_result = action.perform()
                if action_result.alternate == None:
                    break
                action = action_result.alternate

            self.current_actor = (self.current_actor + 1) % len(self.entities)

    def render(self, surface):
        surface.fill(constants.COLOR_DEFAULT_BG)

        self.current_map.draw(surface)
        for actor in self.entities:
            renderer = actor.get_component(components.RendererComponent)
            if renderer != None:
                if self.current_map.in_fov(actor.x, actor.y):
                    renderer.draw(surface, actor.x, actor.y)

        pygame.display.flip()
