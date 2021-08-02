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

    def set_target_tile(self, x, y):
        self.x = x
        self.y = y


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
                apply_damage(engine, e, weapon.damage)
                # return ActionResult(False, DamageAction(self.attacker, e, weapon.damage))

        return ActionResult(True)


class AreaAttackAction (Action):
    def __init__(self, damage, radius, x=0, y=0):
        self.damage = damage
        self.radius = radius
        self.x = x
        self.y = y

    def perform(self, engine):
        for e in engine.current_map.actors:
            x, y = self.x, self.y
            if distance(e.x, e.y, x, y) <= self.radius:
                # return ActionResult(False, DamageAction(None, e, self.damage))
                apply_damage(engine, e, self.damage)
        return ActionResult(True)


# NOT SURE ABOUT THESE... MAYBE I NEED A LIST OF NEXT_ACTIONS INSTEAD TO CHAIN DAMAGES AND KILLS!

def apply_damage(engine, defender, damage):
    health = defender.get_component(components.HealthComponent)
    if health is None:
        return

    health.hp = max(0, health.hp - damage)
    engine.message_log.add_message(
        f"{defender.name} was hit, {damage}", COLOR_ORANGE, True)
    if (health.hp == 0):
        kill(engine, defender)


def kill(engine, actor):
    engine.message_log.add_message(
        f"{actor.name} is dead", COLOR_BLOOD, True)
    renderer = actor.get_component(components.RendererComponent)
    renderer.change_image(sprites.load_sprite("tile001.png"))

    actor.remove_component(components.IsSolid)
    actor.add_component(components.IsDead())


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

    def perform(self, engine):
        print("healing")
        actor = engine.current_map.get_actor_at(self.x, self.y)
        if actor is None:
            return ActionResult(False, ImpossibleAction())
        health_component = actor.get_component(components.HealthComponent)
        if health_component is None:
            return ActionResult(False, ImpossibleAction())
        health_component.hp = min(
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
    def __init__(self, actor, item_index):
        inventoryComponent = actor.get_component(
            components.InventoryComponent)

        self.inventory = inventoryComponent.inventory
        self.item = self.inventory.items[item_index]

    def perform(self, engine):
        # TODO: find place to drop the item, update
        self.inventory.items.remove(self.item)
        engine.current_map.items.append(self.item)
        return ActionResult(True)


class ConsumeItemAction(Action):
    def __init__(self, actor, item_index):
        inventoryComponent = actor.get_component(
            components.InventoryComponent)

        self.inventory = inventoryComponent.inventory
        self.item_index = item_index
        self.actor = actor

    def perform(self, engine):
        if self.item_index >= len(self.inventory.items):
            return ActionResult(False, ImpossibleAction("Item slot is empty"))
        engine.show_inventory = False
        engine.player.behaviour = behaviours.SelectMapPositionBehaviour(
            self.on_position_selected)

        return ActionResult(False)

    def on_position_selected(self, engine, x, y):
        item = self.inventory.items[self.item_index]
        self.inventory.items.remove(item)
        engine.show_inventory = False
        engine.player.behaviour = behaviours.IngameInput()
        item.action.set_target_tile(x, y)
        self.actor.next_action = item.action


#  _   _ _____ _     ____  _____ ____  ____
# | | | | ____| |   |  _ \| ____|  _ \/ ___|
# | |_| |  _| | |   | |_) |  _| | |_) \___ \
# |  _  | |___| |___|  __/| |___|  _ < ___) |
# |_| |_|_____|_____|_|   |_____|_| \_\____/


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
