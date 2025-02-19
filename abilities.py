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


def flamethrower(parent, speed, chance=10, spread=5, angle=None):
    if angle is None:
        angle = parent.angle
    if randint(0, chance) == 0:
        direction = int(angle)
        direction = randint(direction-spread, direction+spread)
        if direction < 0:
            direction += 360
        elif direction >= 360:
            direction -= 360
        shoots.append(Shoot(parent.x, parent.y, speed, direction, 3, fireball, parent))


def frag_explosion(asteroid):
    for i in range(0, 75):
        shoots.append(Shoot(asteroid.x, asteroid.y, 8, randint(0, 360), 2, frag))
    frag_grenades.remove(asteroid)


def teleport(obj, enemies, asteroids):
    porting = True
    pressed = True
    while porting:
        print("porting")
        targetx = obj.x
        targety = obj.y
        targetx += controller.get_axis(2)
        targety += controller.get_axis(3)
        screen.fill((0, 0, 0))
        for enemy in enemies:
            pg.draw.rect(screen, enemy.rect_color, [enemy.x - enemy.hitbox / 2, enemy.y - enemy.hitbox / 2,
                                                  enemy.hitbox, enemy.hitbox], 2)
            screen.blit(enemy.image, (enemy.x - enemy.actual_size[0] / 2, enemy.y - enemy.actual_size[1] / 2))
            pg.draw.line(screen, (255, 0, 0), (enemy.x - enemy.hitbox / 2, enemy.y - enemy.hitbox / 2 - 10),
                         ((enemy.x-enemy.hitbox/2)+enemy.hp*(enemy.hitbox/enemy.max_hp), enemy.y-enemy.hitbox/2-10), 4)
        for asteroid in asteroids:
            pg.draw.rect(screen, (255, 0, 0), [asteroid.x - asteroid.hitbox / 2, asteroid.y - asteroid.hitbox / 2,
                                               asteroid.hitbox, asteroid.hitbox], 2)
            screen.blit(asteroid.image, (asteroid.x-asteroid.image.get_width()/2, asteroid.y-asteroid.image.get_height()/2))
        screen.blit(obj.image, (int(obj.x - obj.actual_size[0] / 2), int(obj.y - obj.actual_size[1] / 2)))
        pg.draw.rect(screen, obj.rect_color,
                     [int(obj.x - obj.hitbox / 2), int(obj.y - obj.hitbox / 2),
                      int(obj.hitbox), int(obj.hitbox)], 2)
        pg.draw.circle(screen, (0, 100, 255), (targetx, targety), 100, 2)
        pg.display.update()
        if controller.get_button(0) is True:
            print("pressed")
            if not pressed:
                obj.x = targetx
                obj.y = targety
                for enemy in enemies:
                    if dist((obj.x, obj.y), (enemy.x, enemy.y)) <= 200:
                        enemy.hp -= 10
                print("port ended")
        else:
            pressed = False
            print("pressed deactivated")
