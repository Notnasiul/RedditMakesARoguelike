import constants
import components
from entity import Entity


class Item(Entity):
    def __init__(self, x, y, name, components, map):
        super().__init__(x, y, name, components, map)
        if map:
            map.items.append(self)
