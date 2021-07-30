from actor import Actor
from item import Item
import components
import behaviours
import actions
import sprites


def A_Player(x, y, current_map):
    player = Actor(x, y, "Player",
                   [
                       components.IsPlayer(),
                       components.HealthComponent(10),
                       components.RendererComponent(
                           sprites.load_sprite("tile025.png")),
                       components.InventoryComponent(1),
                       components.EquipmentComponent(
                           components.RangedWeaponComponent(
                               "Colt", 6, 10, 10, 1, 1),
                           components.RangedWeaponComponent(
                               "Dinamite", 6, 25, 10, 3, 1)
                       ),
                       components.IsSolid()
                   ],
                   behaviours.IngameInput(),
                   current_map)
    return player


def A_Creature(x, y, index, current_map):
    creature = Actor(x, y, "Creature " + str(index),
                     [
                         components.RendererComponent(
                             sprites.load_sprite("tile123.png")),
                         components.HealthComponent(10),
                         components.IsSolid()
    ],
        behaviours.RandomWalkBehaviour(),
        current_map)
    return creature


def A_HealingPotion(x, y, current_map):
    item = Item(x, y, "Healing Potion", [
        components.RendererComponent(
            sprites.load_sprite("tile759.png")),
        components.Consumable()
    ],
        actions.HealAction,
        current_map)
