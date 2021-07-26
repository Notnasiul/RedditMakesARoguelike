import constants


class Actor:
    def __init__(self, x, y, name, components, behaviour, map):
        self.x = x
        self.y = y
        self.name = name
        if map:
            map.entities.append(self)

        self.next_action = None
        self.components = {}
        if components != None:
            self.add_components(components)
        self.behaviour = behaviour

    def add_components(self, components):
        for component in components:
            self.add_component(component)

    def add_component(self, component):
        self.components[component.__class__.__name__] = component

    def get_component(self, component):
        c = self.components.get(component.__name__, None)
        return c

    def remove_component(self, component):
        del self.components[component.__name__]

    def get_action(self):
        action = self.next_action
        self.next_action = None
        return action
