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
                       components.RendererComponent("hero.png"),
                       components.InventoryComponent(5),
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


def A_Bat(x, y, index, current_map):
    creature = Actor(x, y, "Bat " + str(index),
                     [
                         components.RendererComponent("bat.png"),
                         components.HealthComponent(10),
                         components.IsSolid()
    ],
        behaviours.RandomWalkBehaviour(),
        current_map)
    return creature


def A_HealingPotion(x, y, current_map):
    item = Item(x, y, "Healing Potion", [
        components.RendererComponent("healing_potion.png")
    ],
        actions.HealAction(5),
        current_map)


def A_Dinamite(x, y, current_map):
    item = Item(x, y, "Dinamite", [
        components.RendererComponent("dinamite_pack.png")
    ],
        actions.AreaAttackAction(10, 3),
        current_map)
