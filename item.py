import constants
import components
from entity import Entity


class Item(Entity):
    def __init__(self, x, y, name, components, action, current_map):
        super().__init__(x, y, name, components, current_map)
        if current_map:
            current_map.items.append(self)
        self.action = action

    def activate(self, x, y):
        pass
