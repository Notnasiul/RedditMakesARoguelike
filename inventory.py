class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    @property
    def is_full(self):
        return len(self.items) == self.capacity

    def get_item(self, item_index):
        if item_index >= len(self.items):
            return None
        return self.items[item_index]
