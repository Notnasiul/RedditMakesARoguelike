from actor import Actor
import components
import behaviours
import sprites


def A_Player(x, y, current_map):
    player = Actor(x, y, "Player",
                   [
                       components.IsPlayer(),
                       components.RendererComponent(
                           sprites.load_sprite("tile025.png")),
                       components.Equipment(
                           components.RangedWeaponComponent(
                               "Colt", 6, 10, 10, 1, 1),
                           components.RangedWeaponComponent(
                               "Dinamite", 6, 25, 10, 3, 1)
                       )
                   ],
                   behaviours.KeyboardMouseInputBehaviour(),
                   current_map)
    return player


def A_Creature(x, y, current_map):
    creature = Actor(x, y, "Creature",
                     [
                         components.RendererComponent(
                             sprites.load_sprite("tile123.png")),
                         components.HealthComponent(10)
                     ],
                     behaviours.RandomWalkBehaviour(),
                     current_map)
    return creature
