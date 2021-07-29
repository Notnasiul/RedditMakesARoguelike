class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    @property
    def is_full(self):
        return len(self.items) == self.capacity
