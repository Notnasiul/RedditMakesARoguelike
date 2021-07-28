import constants
import components
from entity import Entity


class Actor(Entity):
    def __init__(self, x, y, name, components, behaviour, map):
        super().__init__(x, y, name, components, map)
        self.behaviour = behaviour
        self.next_action = None
        if map:
            map.entities.append(self)

    def get_action(self):
        action = self.next_action
        self.next_action = None
        return action

    @property
    def is_blocking(self):
        return self.get_component(components.IsSolid) is not None

    @property
    def is_alive(self):
        return self.get_component(components.IsDead) is None

    @property
    def is_player(self):
        return self.get_component(components.IsPlayer) is not None
