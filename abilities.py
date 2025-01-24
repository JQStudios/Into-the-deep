from classes import *

shoots = []
frag_grenades = []

frag = pg.image.load("frag.png")
size = x_max/250
scale = frag.get_width()/size
frag = pg.transform.scale(frag, (frag.get_width()/scale, frag.get_height()/scale))

frag_grenade = pg.image.load("frag_grenade.png")
size = x_max/150
scale = frag_grenade.get_width()/size
frag_grenade = pg.transform.scale(frag_grenade, (frag_grenade.get_width()/scale, frag_grenade.get_height()/scale))

red_blast = pg.image.load("red_blast.png")
size = x_max/250
scale = red_blast.get_width()/size
red_blast = pg.transform.scale(red_blast, (red_blast.get_width()/scale, red_blast.get_height()/scale))

fireball = pg.image.load("fireball.png")
size = x_max/150
scale = fireball.get_width()/size
fireball = pg.transform.scale(fireball, (fireball.get_width()/scale, fireball.get_height()/scale))


def flamethrower(parent, speed, chance=10, spread=5):
    if randint(0, chance) == 0:
        direction = int(parent.angle)
        direction = randint(direction-spread, direction+spread)
        if direction < 0:
            direction += 360
        elif direction >= 360:
            direction -= 360
        shoots.append(Shoot(parent.x, parent.y, speed, direction, 1, fireball, parent))


def frag_explosion(obj):
    for i in range(0, 75):
        shoots.append(Shoot(obj.x, obj.y, 8, randint(0, 360), 2, frag))
    frag_grenades.remove(obj)
