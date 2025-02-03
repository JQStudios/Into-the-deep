import pygame as pg
from math import *
from random import *
from time import *
import json
import re
# Save settings

SETTINGS_FILE = "settings.json"


def in_rect(pos, rect):
    if (rect[0] <= pos[0] <= rect[2]) and (rect[1] <= pos[1] <= rect[3]):
        return True
    else:
        return False


def load_settings():
    try:
        with open(SETTINGS_FILE, "r") as file:
            settings = json.load(file)
            return settings
    except FileNotFoundError:
        print("Could not find settings file. Creating a new one.")
        default_settings = {
            "display": {
                "size": "1280, 720",
            },
            "sounds": {
                "active": True,
            },
        }
        save_settings(default_settings)
        return default_settings

# save settings
def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)

settings = load_settings()

if settings["display"]["size"] == "FULLSCREEN":
    pg.init()
    screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
else:
    pg.init()
    screen = pg.display.set_mode((tuple(map(int, re.findall(r'\d+', settings["display"]["size"])))))

pg.init()
#screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
x_max, y_max = screen.get_size()
pg.key.set_repeat(20, 20)
pg.joystick.init()
controllers = pg.joystick.get_count()
if controllers > 0:
    controller = pg.joystick.Joystick(0)
    controller.init()
else:
    controller = None
if controllers > 1:
    controller1 = pg.joystick.Joystick(1)
    controller1.init()
elif controllers <= 0:
    controller1 = None
vibratetil = time()
vibrating = False


def get_angle(vector1, vector2):
    angle = atan2(vector2[1]-vector1[1], vector2[0]-vector1[0])
    in_degrees = degrees(angle)
    in_degrees += 90
    in_degrees = abs(360-in_degrees)
    in_degrees -= 180
    if in_degrees >= 360:
        in_degrees -= 360
    elif in_degrees < -180:
        in_degrees += 360
    return in_degrees


class Object(pg.sprite.Sprite):
    def __init__(self, x, y, image, size, hitbox=None, direction=0, speed=0):
        super().__init__()
        self.x, self.y = x, y
        width, height = image.get_size()
        scale = width/size
        self.image = pg.transform.scale(image, (width/scale, height/scale))
        if hitbox is None:
            self.hitbox = size
        else:
            self.hitbox = hitbox
        self.angle = direction
        self.speed = speed
        self.move_tick = time()
        self.move_fps = 400

    def move(self):
        timeout = (time()-self.move_tick)/(1/self.move_fps)
        self.move_tick = time()
        self.x -= sin(radians(self.angle))*self.speed*timeout
        self.y -= cos(radians(self.angle))*self.speed*timeout
        if self.x > x_max:
            self.angle += 180
        elif self.x < 0:
            self.angle += 180
        if self.y > y_max:
            self.angle += 180
        elif self.y < 0:
            self.angle += 180


class Bomb(pg.sprite.Sprite):
    def __init__(self, x, y, direction, distance, speed, image, parent):
        super().__init__()
        self.x, self.y = x, y
        self.angle = direction
        self.fly_dist = distance
        self.speed = speed
        self.flew_dist = 0
        self.image = pg.transform.rotate(image, direction)
        self.move_tick = time()
        self.move_fps = 400
        self.direction = [0, 0]
        self.parent = parent

    def move(self):
        timeout = (time()-self.move_tick)/(1/self.move_fps)
        self.move_tick = time()
        self.x -= sin(radians(self.angle))*self.speed*timeout
        self.y -= cos(radians(self.angle))*self.speed*timeout
        self.flew_dist += self.speed*timeout
        if self.angle <= 180:
            self.direction[0] = self.x-self.image.get_width()/2
        else:
            self.direction[0] = self.x+self.image.get_width()/2
        if 90 < self.angle <= 270:
            self.direction[1] = self.y+self.image.get_height()/2
        else:
            self.direction[1] = self.y-self.image.get_height()/2
        if self.flew_dist >= self.fly_dist:
            return True
        if self.x > x_max:
            return True
        elif self.x < 0:
            return True
        if self.y > y_max:
            return True
        elif self.y < 0:
            return True
        return False


class Shoot(pg.sprite.Sprite):
    def __init__(self, x, y, speed, angle, damage, image, parent=None):
        super().__init__()
        self.angle = angle
        self.image = pg.transform.rotate(image, angle)
        self.speed = speed
        self.x, self.y = x, y
        self.damage = damage
        self.direction = [0, 0]
        if parent is not None:
            self.inside = True
        else:
            self.inside = False
        self.parent = parent
        self.move_fps = 400
        self.move_tick = time()
        self.remove = False

    def delete(self):
        if self.x > x_max:
            return True
        elif self.x < 0:
            return True
        if self.y > y_max:
            return True
        elif self.y < 0:
            return True
        return False

    def move(self,):
        timeout = (time()-self.move_tick)/(1/self.move_fps)
        self.move_tick = time()
        self.x -= sin(radians(self.angle))*self.speed*timeout
        self.y -= cos(radians(self.angle))*self.speed*timeout
        if self.angle <= 180:
            self.direction[0] = self.x-self.image.get_width()/2
        else:
            self.direction[0] = self.x+self.image.get_width()/2
        if 90 < self.angle <= 270:
            self.direction[1] = self.y+self.image.get_height()/2
        else:
            self.direction[1] = self.y-self.image.get_height()/2


class Ship(pg.sprite.Sprite):
    def __init__(self, x, y, speed, agility, hp, fire_rate, cooldown, damage, size,
                 hitbox=None, image=None, auto=True, guns=None, xp=0):
        super().__init__()
        self.x, self.y = x, y
        self.angle = 0
        self.speed = speed
        self.actual_speed = speed
        self.agility = agility
        self.fire_rate = fire_rate
        self.cooldown = cooldown
        self.damage = damage
        self.image = image
        self.auto = auto
        self.glide = False
        self.x_speed = -sin(radians(self.angle))*self.speed
        self.y_speed = -cos(radians(self.angle))*self.speed
        self.brake = False
        self.left = False
        self.right = False
        width, height = image.get_size()
        scale = width/size
        self.org_image = pg.transform.scale(image, (width/scale, height/scale))
        self.image = self.org_image
        self.size = size
        if hitbox is None:
            self.hitbox = size
        else:
            self.hitbox = hitbox
        self.actual_size = size
        self.control = True
        self.control_time = 0
        self.dodge_ready = False
        self.dodge = False
        self.left_dodge = False
        self.right_dodge = False
        self.dodge_time = 0
        self.max_hp = hp
        self.hp = hp
        self.guns = guns
        self.let_go_shoot = True
        self.let_go_a = True
        self.let_go_b = True
        self.og_turn = 0
        self.move_tick = time()
        self.move_fps = 400
        self.ions = 5
        self.lock_angle = 0
        self.lock_angles = [0, 0, 0]
        self.abilities = []
        self.rect_color = (255, 255, 255)
        self.shot = time()
        self.max_shield = 100
        self.shield = 100
        self.damage_timeout = 0
        self.xp = xp
        self.weapon = 0

    def minus_shield(self, damage):
        self.damage_timeout = time()
        if self.shield >= 0:
            self.shield -= damage
            if self.shield < 0:
                self.shield = 0
        else:
            self.hp -= damage

    def run_move(self, controller=None):
        timeout = (time()-self.move_tick)/(1/self.move_fps)
        self.move(timeout, controller)
        self.move_tick = time()

    def move(self, timeout, controller=None):
        global vibrating

        self.x -= self.x_speed
        self.y -= self.y_speed

        if controllers > 0:
            if self.x <= 0:
                self.x = 0
                self.minus_shield(0.05 * timeout)
                if controller is not None:
                    if not vibrating:
                        controller.rumble(0, 1, 0)
                        vibrating = True
            if self.x >= x_max:
                self.x = x_max
                self.minus_shield(0.05 * timeout)
                if controller is not None:
                    if not vibrating:
                        controller.rumble(0, 1, 0)
                        vibrating = True
            if self.y <= 0:
                self.y = 0
                self.minus_shield(0.05 * timeout)
                if controller is not None:
                    if not vibrating:
                        controller.rumble(0, 1, 0)
                        vibrating = True
            if self.y >= y_max:
                self.y = y_max
                self.minus_shield(0.05 * timeout)
                if controller is not None:
                    if not vibrating:
                        controller.rumble(0, 1, 0)
                        vibrating = True
            else:
                vibrating = False
            if self.shield < 0:
                self.shield = 0
            if time() >= self.damage_timeout + 5:
                if self.shield < self.max_shield:
                    self.shield += 0.05 * timeout
                else:
                    self.shield = self.max_shield
            self.image = pg.transform.rotate(self.org_image, self.angle)
            self.actual_size = [self.image.get_width(), self.image.get_height()]
        else:
            if time() >= self.dodge_time+0.1:
                self.dodge_ready = False
            if not self.control:
                if time() >= self.control_time:
                    self.control = True
            if self.left_dodge:
                self.x -= sin(radians(self.angle + 90)) * self.speed * 2
                self.y -= cos(radians(self.angle + 90)) * self.speed * 2
            if self.right_dodge:
                self.x -= sin(radians(self.angle - 90)) * self.speed * 2
                self.y -= cos(radians(self.angle - 90)) * self.speed * 2
            if self.left:
                if self.dodge:
                    self.x -= sin(radians(self.angle+90))*self.speed*2
                    self.y -= cos(radians(self.angle+90))*self.speed*2
                else:
                    self.angle += self.agility
            if self.right:
                if self.dodge:
                    self.x -= sin(radians(self.angle-90))*self.speed*2
                    self.y -= cos(radians(self.angle-90))*self.speed*2
                else:
                    self.angle -= self.agility
            if self.angle >= 360:
                self.angle -= 360
            elif self.angle < 0:
                self.angle += 360
            self.image = pg.transform.rotate(self.org_image, self.angle)
            self.actual_size = [self.image.get_width(), self.image.get_height()]
            if not self.brake:
                if self.glide:
                    self.actual_speed += 0.01
                else:
                    if self.actual_speed > self.speed:
                        self.actual_speed -= 0.02
                    else:
                        self.actual_speed = self.speed
            else:
                self.actual_speed = 0

            if not self.brake:
                if self.glide:
                    self.x_speed += sin(radians(self.angle))*self.actual_speed/100*timeout
                    self.y_speed += cos(radians(self.angle))*self.actual_speed/100*timeout
                else:
                    x_speed_before = self.x_speed
                    y_speed_before = self.y_speed
                    self.x_speed = abs(self.x_speed) - abs(self.x_speed / 100)
                    self.y_speed = abs(self.y_speed) - abs(self.y_speed / 100)
                    if x_speed_before < 0:
                        self.x_speed = -self.x_speed
                    if y_speed_before < 0:
                        self.y_speed = -self.y_speed
                    self.actual_speed = self.speed
            else:
                self.actual_speed = 0

            if (not self.dodge) and (not self.left_dodge) and (not self.right_dodge):
                self.x -= sin(radians(self.angle))*self.actual_speed*timeout
                self.y -= cos(radians(self.angle))*self.actual_speed*timeout
                self.x -= self.x_speed
                self.y -= self.y_speed

            if self.x <= 0:
                self.x = 0
                self.minus_shield(0.05 * timeout)
            if self.x >= x_max:
                self.x = x_max
                self.minus_shield(0.05 * timeout)
            if self.y <= 0:
                self.y = 0
                self.minus_shield(0.05 * timeout)
            if self.y >= y_max:
                self.y = y_max
                self.minus_shield(0.05 * timeout)


class Bot(Ship):
    def __init__(self, x, y, image, hp=35, damage=1, fire_rate=0.4, botclass="Default", speed=x_max/30000):
        super().__init__(x=x, y=y, speed=speed, agility=0.4, fire_rate=fire_rate, hp=hp, cooldown=5, damage=damage,
                         size=x_max/75, image=image, guns=[-x_max/100, x_max/100])
        self.rect_color = (255, 255, 255)
        self.dead = False
        self.botclass = botclass

    def attack(self, target, obstacles, mode):
        self.left_dodge = False
        for obstacle in obstacles:
            """
            target_angle = get_angle((obstacle.x, obstacle.y), (self.x, self.y))
            anglediff = (self.angle - target_angle + 180 + 360) % 360 - 180
            if (anglediff <= 25) and (anglediff >= -25):
                if dist((self.x, self.y), (obstacle.x, obstacle.y)) <= 75:
                    self.left_dodge = True
            """
            if dist((self.x, self.y), (obstacle.x, obstacle.y)) <= 100:
                self.left_dodge = True

        timeout = (time()-self.move_tick)/(1/self.move_fps)
        # self.move(timeout)
        self.move_tick = time()

        self.angle = get_angle((self.x, self.y), (target.x, target.y))+180
        if self.angle >= 360:
            self.angle -= 360
        elif self.angle < 0:
            self.angle += 360
        self.image = pg.transform.rotate(self.org_image, self.angle)
        self.actual_size = [self.image.get_width(), self.image.get_height()]

        if self.left_dodge:
            self.x -= sin(radians(self.angle + 90)) * self.speed * 2
            self.y -= cos(radians(self.angle + 90)) * self.speed * 2
        if self.right_dodge:
            self.x -= sin(radians(self.angle - 90)) * self.speed * 2
            self.y -= cos(radians(self.angle - 90)) * self.speed * 2

        if (not self.dodge) and (not self.left_dodge) and (not self.right_dodge):
            self.x -= sin(radians(self.angle))*self.actual_speed*timeout
            self.y -= cos(radians(self.angle))*self.actual_speed*timeout
        if dist((self.x, self.y), (target.x, target.y)) < 100 and self.botclass != "Kamikaze":
            self.x += sin(radians(self.angle))*self.actual_speed*2*timeout
            self.y += cos(radians(self.angle))*self.actual_speed*2*timeout

        if self.x <= 0:
            self.x = 0
            self.hp -= 0.05 * timeout
        elif self.x >= x_max:
            self.x = x_max
            self.hp -= 0.05 * timeout
        if self.y <= 0:
            self.y = 0
            self.hp -= 0.05 * timeout
        elif self.y >= y_max:
            self.y = y_max
            self.hp -= 0.05 * timeout


class XWing(Ship):
    def __init__(self, image, abilities=None, xp=0):
        super().__init__(x=x_max/2, y=y_max/2, speed=x_max/1000, agility=1, fire_rate=0.5, hp=80,
                         cooldown=5, damage=5, size=x_max/50, image=image, guns=[-x_max/100, x_max/100], xp=xp)
        if abilities is None:
            abilities = ["flamethrower"]
        self.flamethrower = 0
        self.flamethrower_cooldown = 0
        self.grenades = 5
        self.abilities = abilities
        self.name = "X-Wing"
        self.root = None
        self.own = True
        self.buy = False
        self.price = 1000
        self.shop_x = 0.5
        self.shop_y = 0.1
        print(self.speed)


class Bomber(Ship):
    def __init__(self, image, abilities=None, xp=0):
        super().__init__(x=x_max/2, y=y_max/2, speed=x_max/2000, agility=0.6, fire_rate=0.25, hp=120,
                         cooldown=5, damage=6, size=x_max/25, hitbox=x_max/30, image=image,
                         guns=[-x_max/50, x_max/50], xp=xp)
        if abilities is None:
            abilities = ["ion_attack"]
        self.flamethrower = 0
        self.flamethrower_cooldown = 0
        self.grenades = 5
        self.abilities = abilities
        self.name = "Bomber"
        self.root = "X-Wing"
        self.own = False
        self.buy = False
        self.price = 2000
        self.shop_x = 0.5
        self.shop_y = 0.2
