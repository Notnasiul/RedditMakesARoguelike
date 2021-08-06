
from inventory import Inventory


class Component():
    def __init__(self):
        pass


class RendererComponent(Component):
    def __init__(self, sprite):
        self.change_image(sprite)

    def change_image(self, sprite):
        self.sprite = sprite


class HealthComponent(Component):
    def __init__(self, max_hp):
        self.max_hp = max_hp
        self.hp = max_hp


class RangedWeaponComponent(Component):
    def __init__(self, name, ammoCapacity, damage, range, area, reloadTurns):
        self.name = name
        self.ammoCapacity = ammoCapacity
        self.damage = damage
        self.range = range
        self.area = area
        self.currentAmmo = ammoCapacity
        self.reloadTurns = reloadTurns
        self.reloading = 0


class InventoryComponent(Component):
    def __init__(self, capacity):
        self.inventory = Inventory(capacity)


class EquipmentComponent(Component):
    def __init__(self, main_weapon, secondary_weapon):
        self.main_weapon = main_weapon
        self.secondary_weapon = secondary_weapon


class IsPlayer(Component):
    pass


class IsDead(Component):
    pass


class IsSolid(Component):
    pass


class Consumable(Component):
    pass
