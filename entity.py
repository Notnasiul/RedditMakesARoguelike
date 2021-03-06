import constants
import components


class Entity:
    def __init__(self, x, y, name, components, map):
        self.x = x
        self.y = y
        self.name = name
        self.current_map = map
        self.components = {}
        if components != None:
            self.add_components(components)

    def add_components(self, components):
        for component in components:
            self.add_component(component)
            component.owner = self

    def add_component(self, component):
        self.components[component.__class__.__name__] = component
        component.owner = self

    def get_component(self, component):
        c = self.components.get(component.__name__, None)
        return c

    def remove_component(self, component):
        del self.components[component.__name__]
