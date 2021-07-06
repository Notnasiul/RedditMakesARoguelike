from actor import Actor
import components
import behaviours
import sprites


def A_Player(sprites, x, y):
    player = Actor(x, y, "Player",
                   [
                       components.IsPlayer(),
                       behaviours.Brain(
                           behaviours.KeyboardMouseInputStrategy()),
                       components.RendererComponent(
                           sprites.PLAYER),
                       components.Equipment(
                           components.RangedWeaponComponent(
                               "Colt", 6, 10, 10, 1, 1),
                           components.RangedWeaponComponent(
                               "Dinamite", 6, 25, 10, 3, 1)
                       )
                   ])
    return player


def A_Creature(sprites, x, y):
    creature = Actor(x, y, "Creature",
                     [
                         behaviours.Brain(behaviours.RandomWalkStrategy()),
                         components.RendererComponent(
                             sprites.CREATURE),
                         components.HealthComponent(10)
                     ])
    return creature
