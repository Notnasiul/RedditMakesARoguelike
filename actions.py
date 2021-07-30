import components
import behaviours
import math
import sprites
from constants import *


class ActionResult:
    def __init__(self, success, alternate=None):
        self.alternate = alternate
        self.success = success


class Action:
    def perform(self, engine):
        print("WARNING: Action has no perform")
        return ActionResult(False, None)


class ImpossibleAction:
    def __init__(self, message=None):
        self.message = message

    def perform(self, engine):
        if self.message is not None:
            engine.message_log.add_message(
                self.message, COLOR_LIGHT_MAX, True)
        return ActionResult(True, None)


class WaitAction:
    def perform(self, engine):
        return ActionResult(True)


class WalkAction(Action):
    def __init__(self, actor, dx, dy):
        self.actor = actor
        self.dx = dx
        self.dy = dy

    def perform(self, engine):
        if self.dx == 0 and self.dy == 0:
            return ActionResult(True)

        xx = self.actor.x + self.dx
        yy = self.actor.y + self.dy
        current_map = engine.current_map

        tile_is_blocked = current_map.tiles[xx][yy].blocks_path == True
        if tile_is_blocked:
            return ActionResult(False, BumpAction(self.actor, xx, yy))

        occupant = current_map.get_actor_at(xx, yy)
        if occupant and occupant.is_alive:
            return ActionResult(False, MeleeAttackAction(self.actor, occupant))

        self.actor.x += self.dx
        self.actor.y += self.dy

        return ActionResult(True)


class MeleeAttackAction (Action):
    def __init__(self, attacker, defender):
        self.attacker = attacker
        self.defender = defender

    def perform(self, engine):
        # get melee weapon, use to deal damage
        engine.message_log.add_message(
            f"{self.attacker.name} attacks {self.defender.name} for {1} hp", COLOR_LIGHT_MAX, True)
        return ActionResult(False, DamageAction(self.attacker, self.defender, 1))


class RangeAttackAction (Action):
    def __init__(self, rangedWeaponComponent, attacker, attackedCell):
        self.rangedWeaponComponent = rangedWeaponComponent
        self.attacker = attacker
        self.attackedCell = attackedCell

    def perform(self, engine):
        weapon = self.rangedWeaponComponent
        if weapon is None:
            return ActionResult(False, None)

        # get all objects at tilePosition
        for e in engine.current_map.actors:
            x, y = self.attackedCell
            if distance(e.x, e.y, x, y) <= weapon.area:
                engine.message_log.add_message(
                    f"{self.attacker.name} attacks {e.name} for {weapon.damage} hp", COLOR_LIGHT_MAX, True)
                return ActionResult(False, DamageAction(self.attacker, e, weapon.damage))

        return ActionResult(True)


class DamageAction (Action):
    def __init__(self, attacker, defender, damage):
        self.attacker = attacker
        self.defender = defender
        self.damage = damage

    def perform(self, engine):
        health = self.defender.get_component(components.HealthComponent)
        if health is None:
            return ActionResult(False, None)

        health.hp = max(0, health.hp - self.damage)
        engine.message_log.add_message(
            f"{self.defender.name} was hit, {self.damage}", COLOR_ORANGE, True)
        if (health.hp == 0):
            return ActionResult(False, KillAction(self.attacker, self.defender))

        return ActionResult(True)


class KillAction (Action):
    def __init__(self, attacker, defender):
        self.attacker = attacker
        self.defender = defender

    def perform(self, engine):
        engine.message_log.add_message(
            f"{self.defender.name} is dead", COLOR_BLOOD, True)
        renderer = self.defender.get_component(components.RendererComponent)
        renderer.change_image(sprites.load_sprite("tile001.png"))

        self.defender.remove_component(components.IsSolid)
        self.defender.add_component(components.IsDead())
        return ActionResult(True)


class BumpAction (Action):
    def __init__(self, actor, x, y):
        self.actor = actor
        self.x = x
        self.y = y

    def perform(self, engine):
        return ActionResult(False, ImpossibleAction())


class PosessAction (Action):
    def __init__(self, attacker, defender):
        self.attacker = attacker
        self.defender = defender

    def perform(self, engine):
        # print("posessing: " + self.defender.name)
        self.attacker.remove_component(components.IsPlayer)
        self.defender.add_component(components.IsPlayer())
        return ActionResult(True)


class HealAction(Action):
    def __init__(self, heal_amount):
        self.heal_amount = heal_amount
        self.x, self.y = targetxy

    def perform(self, engine):
        actor = engine.current_map.get_actor_at(self.x, self.y)
        if actor is None:
            return ActionResult(False, ImpossibleAction())
        health_component = actor.get_component(components.HealthComponent)
        if health_component is None:
            return ActionResult(False, ImpossibleAction())
        health_component.hp = max(
            health_component.max_hp, health_component.hp + self.heal_amount)
        return ActionResult(True)

# INVENTORY RELATED ACTIONS


class OpenInventory(Action):
    def __init__(self, actor):
        self.actor = actor

    def perform(self, engine):
        inventoryComponent = self.actor.get_component(
            components.InventoryComponent)
        if inventoryComponent is None:
            return ActionResult(False, ImpossibleAction("WTF? No inventory?"))

        engine.show_inventory = True
        engine.player.behaviour = behaviours.InventoryInputBehavior()
        return None


class CloseInventory(Action):
    def __init__(self, actor):
        self.actor = actor

    def perform(self, engine):
        engine.show_inventory = False
        engine.player.behaviour = behaviours.IngameInput()
        return None


class SelecInventoryItem(Action):
    def __init__(self, actor, item_index):
        self.item_index = item_index
        self.actor = actor

    def perform(self, engine):
        inventoryComponent = self.actor.get_component(
            components.InventoryComponent)
        inventory = inventoryComponent.inventory

        item = inventory.get_item(self.item_index)
        if item is not None:
            print(f"item {inventory.get_item(self.item_index).name} selected")

        return None


class PickItemAction(Action):
    def __init__(self, actor, x, y):
        self.actor = actor
        self.x = x
        self.y = y

    def perform(self, engine):
        item = engine.current_map.get_item_at(self.x, self.y)
        if item is None:
            return ActionResult(False, ImpossibleAction("Nothing here to pick"))

        inventoryComponent = self.actor.get_component(
            components.InventoryComponent)
        if inventoryComponent is None:
            return ActionResult(False, ImpossibleAction("WTF? No inventory?"))

        inventory = inventoryComponent.inventory
        if inventory.is_full:
            return ActionResult(False, ImpossibleAction("Inventory is full!"))

        engine.current_map.items.remove(item)
        inventory.items.append(item)
        engine.message_log.add_message(
            f"{self.actor.name} picks {item.name}", COLOR_LIGHT_MAX, True)

        return ActionResult(True)


class DropItemAction(Action):
    def __init__(self, inventory, item):
        self.inventory = inventory
        self.item = item

    def perform(self, engine, current_owner):
        self.inventory.items.remove(item)
        return ActionResult(True)
#  _   _ _____ _     ____  _____ ____  ____
# | | | | ____| |   |  _ \| ____|  _ \/ ___|
# | |_| |  _| | |   | |_) |  _| | |_) \___ \
# |  _  | |___| |___|  __/| |___|  _ < ___) |
# |_| |_|_____|_____|_|   |_____|_| \_\____/


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
