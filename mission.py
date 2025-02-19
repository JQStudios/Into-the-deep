from abilities import *
from techtree import *

laser = pg.mixer.Sound("retro-laser-1-236669.mp3")
laser.set_volume(0.2)
weapon = 0


def create_bot(mode):
    ExtraBots, HPFactor = GetDifficultyFactors()
    speed = x_max / 30000
    if mode == "free for all":
        botclass = random.choice(["Default", "FlameBot", "Sniper", "Heavy"])
        if botclass == "Default":
            hp = 100 * HPFactor
            damage = 5
            rate = 0.4
        elif botclass == "FlameBot":
            hp = 80 * HPFactor
            damage = 0
            rate = -1
        elif botclass == "Sniper":
            hp = 50 * HPFactor
            damage = 10
            rate = 1.5
        else:
            hp = 120 * HPFactor
            damage = 2.5
            rate = 0.3
    else:
        botclass = random.choice(["Default", "FlameBot", "Kamikaze", "Sniper", "Heavy"])
        if botclass == "Default":
            hp = 35 * HPFactor
            damage = 1
            rate = 0.4
        elif botclass == "FlameBot":
            hp = 20 * HPFactor
            damage = 0
            rate = -1
        elif botclass == "Kamikaze":
            hp = 50 * HPFactor
            damage = 0
            rate = -1
            speed = x_max / 7500
        elif botclass == "Sniper":
            hp = 10 * HPFactor
            damage = 3
            rate = 2
        else:
            hp = 50 * HPFactor
            damage = 0.5
            rate = 0.3
    return hp, damage, rate, speed, botclass


def PlayMission(ship_class, fighters, botcount, mode, reward):
    global weapon
    settings = load_settings()
    sounds = settings["sounds"]["active"]
    print(f"Sound Active: {sounds}")
    data = LoadData()
    XP = 0
    result = False
    currency = data["Balance"]
    vibratetil = 0
    asteroidpng = pg.image.load("asteroid.png")
    dronepng = pg.image.load("drone.png")
    ship_class = ship_class
    ExtraBots, HPFactor = GetDifficultyFactors()
    if ship_class == "X-Wing":
        fighter = XWing(image=xwingpng)
    elif ship_class == "Bomber":
        fighter = Bomber(image=bomberpng)
    elif ship_class == "LightCruiser":
        fighter = LightCruiser(image=lightcruiserpng)
    for ShipData in data["ShipsData"].values():
        if ShipData["Name"] == fighter.name:
            print(ShipData["XP"])
            fighter.xp = ShipData["XP"]
            startXP = ShipData["XP"]
            break
    objects = []
    for nr in range(0, 16):
        objects.append(Object(randint(0, x_max), randint(0, y_max), asteroidpng, x_max/27.5))
        objects[len(objects)-1].speed = randint(0, 10)
        objects[len(objects)-1].speed *= 0.01
        objects[len(objects)-1].angle = randint(0, 359)
    bots = []
    if mode == "free for all":
        botcount = 4 + int(ExtraBots * 0.5)
        reward = reward * 0.5
    elif mode == "defend":
        botcount = 0
    else:
        botcount = 8 + ExtraBots
    reward = int(reward * (HPFactor/2))
    botclass = "Default"
    for nr in range(0, botcount):
        hp, damage, rate, speed, botclass = create_bot(mode)
        bots.append(Bot(randint(0, x_max), randint(0, y_max), dronepng, fire_rate=rate, hp=hp,
                        damage=damage, botclass=botclass, speed=speed))
    spawn_time = time()
    print(f"Spawned {len(bots)} with HP * {HPFactor} and {ExtraBots} extra bots in {spawn_time}s")
    weapon = 0

    def minus_shield(obj, damage):
        if time() >= spawn_time+2:
            obj.damage_timeout = time()
            print(spawn_time-time())
            if obj.shield > 0:
                obj.shield -= damage
                if obj.shield < 0:
                    obj.shield = 0
            else:
                obj.hp -= damage

    def in_rect(pos, rect):
        if (rect[0] <= pos[0] <= rect[2]) and (rect[1] <= pos[1] <= rect[3]):
            return True
        else:
            return False

    def control_overlaps(obj, obj1):
        if type(obj) is not list:
            rect = [obj.x-obj.hitbox/2, obj.y-obj.hitbox/2, obj.x+obj.hitbox/2, obj.y+obj.hitbox/2]
            poses = [(rect[0], rect[1]), (rect[2], rect[1]), (rect[0], rect[3]), (rect[2], rect[3])]
        else:
            rect = []
            poses = [obj]

        if type(obj1) is not list:
            rect1 = [obj1.x-obj1.hitbox/2, obj1.y-obj1.hitbox/2, obj1.x+obj1.hitbox/2, obj1.y+obj1.hitbox/2]
            poses1 = [(rect1[0], rect1[1]), (rect1[2], rect1[1]), (rect1[0], rect1[3]), (rect1[2], rect1[3])]
        else:
            rect1 = []
            poses1 = [obj1]

        if len(rect1) > 0:
            for pos in poses:
                if in_rect(pos, rect1):
                    return True
        if len(rect) > 0:
            for pos1 in poses1:
                if in_rect(pos1, rect):
                    return True
        return False

    def ion_attack(x, y, radius, delay, self):
        ships = [fighter]
        ships.remove(self)
        for ship in ships:
            if dist((ship.x, ship.y), (x, y)) <= radius:
                ship.control = False
                ship.control_time = time()+delay

    def target_system(obj, obj1, angle=None, diff=15):
        if angle is None:
            angle = obj.angle
        selected = []
        obj.lock_angle = obj.angle
        if obj.guns is not None:
            for gun in obj.guns:
                nr = obj.guns.index(gun)
                obj.lock_angles[nr] = obj.angle
        for nr in range(len(obj1)):
            impact_dist = dist((obj.x, obj.y), (obj1[nr].x, obj1[nr].y))
            ticks = impact_dist / 10
            impact_x = obj1[nr].x - sin(radians(obj1[nr].angle)) * obj1[nr].actual_speed * ticks
            impact_y = obj1[nr].y - cos(radians(obj1[nr].angle)) * obj1[nr].actual_speed * ticks
            target_angle = get_angle((obj1[nr].x, obj1[nr].y), (obj.x, obj.y))
            anglediff = (angle - target_angle + 180 + 360) % 360 - 180
            if (anglediff <= diff) and (anglediff >= -diff):
                selected.append([obj1[nr], impact_dist])

        if len(selected) > 0:
            selected.sort(key=lambda a: a[1])
            impact_dist = dist((obj.x, obj.y), (selected[0][0].x, selected[0][0].y))
            ticks = impact_dist / 10
            impact_x = selected[0][0].x - sin(radians(selected[0][0].angle)) * selected[0][0].actual_speed * ticks
            impact_y = selected[0][0].y - cos(radians(selected[0][0].angle)) * selected[0][0].actual_speed * ticks
            target_angle = get_angle((impact_x, impact_y), (obj.x, obj.y))
            selected[0][0].rect_color = (255, 0, 0)
            obj.lock_angle = target_angle
            if obj.guns is not None:
                for gun in obj.guns:
                    angle = get_angle((obj.x - sin(radians(obj.angle + 90)) * gun,
                                       obj.y - cos(radians(obj.angle + 90)) * gun), (impact_x, impact_y))
                    nr = obj.guns.index(gun)
                    obj.lock_angles[nr] = angle + 180
            return selected[0][0]
        else:
            return None

    def controller_check(obj, controller_obj, enemies):
        global weapon
        if abs(controller_obj.get_axis(0)) >= 0.1 or abs(controller_obj.get_axis(1)) >= 0.1:
            obj.angle = get_angle((0, 0), (-controller_obj.get_axis(0), -controller_obj.get_axis(1)))
            obj.x_speed = -controller_obj.get_axis(0) * obj.speed * 2
            obj.y_speed = -controller_obj.get_axis(1) * obj.speed * 2
        else:
            obj.x_speed = 0
            obj.y_speed = 0
        if abs(controller_obj.get_axis(2)) >= 0.3 or abs(controller_obj.get_axis(3)) >= 0.3:
            weapon_angle = get_angle((0, 0), (-controller_obj.get_axis(2), -controller_obj.get_axis(3)))
            if weapon == 0:
                shoot_angle = weapon_angle
                pg.draw.polygon(screen, (255, 0, 0), [(obj.x, obj.y),
                                                      (obj.x - sin(radians(shoot_angle - 20)) * 400,
                                                       obj.y - cos(radians(shoot_angle - 20)) * 400),
                                                      (obj.x - sin(radians(shoot_angle + 20)) * 400,
                                                       obj.y - cos(radians(shoot_angle + 20)) * 400), (obj.x, obj.y)],
                                2)
                target = target_system(obj, enemies, shoot_angle, 20)
                if target is not None:
                    target.rect_color = (255, 0, 0)
                    if time() >= obj.shot + obj.fire_rate:
                        if obj.guns is None:
                            shoots.append(Shoot(obj.x, obj.y, obj.actual_speed + 10, obj.lock_angle,
                                                obj.damage, red_blast, obj))
                            if sounds:
                                pg.mixer.Sound.play(laser)
                        else:
                            for gun in obj.guns:
                                nr = obj.guns.index(gun)
                                img = pg.transform.scale(red_blast, (1, 1))
                                shoots.append(Shoot(obj.x - sin(radians(obj.angle + 90)) * gun,
                                                    obj.y - cos(radians(obj.angle + 90)) * gun,
                                                    obj.actual_speed + 10, obj.lock_angles[nr],
                                                    obj.damage, red_blast, obj))
                            if sounds:
                                pg.mixer.Sound.play(laser)
                        obj.shot = time()
            elif weapon == 1:
                if obj.fuel > 0:
                    obj.fuel -= 2
                    flamethrower(fighter, fighter.speed + 3, chance=10, spread=4, angle=weapon_angle)
        if not controller_obj.get_button(4):
            obj.let_go_b = True
        else:
            if obj.let_go_b:
                obj.let_go_b = False
                weapon -= 1
        if not controller_obj.get_button(5):
            obj.let_go_b = True
        else:
            if obj.let_go_b:
                obj.let_go_b = False
                weapon += 1
        if weapon > 1:
            weapon = 0
        elif weapon < 0:
            weapon = 1

    running = True
    stars = []
    while len(stars) <= 100:
        stars.append((random.randint(0, x_max), random.randint(0, y_max)))
    bot_spawn = time()-8
    bot_start = time()
    while running:
        if dist((fighter.x, fighter.y), (pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])) >= 5:
            fighter.angle = get_angle((fighter.x, fighter.y), (pg.mouse.get_pos()[0], pg.mouse.get_pos()[1])) + 180
            fighter.stop = False
        else:
            fighter.stop = True
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False

                if event.key == pg.K_a:
                    fighter.left = True
                if event.key == pg.K_d:
                    fighter.right = True
                if event.key == pg.K_w:
                    fighter.glide = True
                if event.key == pg.K_s:
                    fighter.brake = True
            if event.type == pg.KEYUP:
                if event.key == pg.K_a:
                    fighter.left = False
                if event.key == pg.K_d:
                    fighter.right = False
                if event.key == pg.K_w:
                    fighter.glide = False
                if event.key == pg.K_s:
                    fighter.brake = False

                if fighter.control:
                    if event.key == pg.K_a:
                        fighter.left = False
                        fighter.dodge_ready = True
                        fighter.dodge_time = time()
                        if fighter.dodge:
                            fighter.dodge = False
                    if event.key == pg.K_d:
                        fighter.right = False
                        fighter.dodge_ready = True
                        fighter.dodge_time = time()
                        if fighter.dodge:
                            fighter.dodge = False
                    if event.key == pg.K_w:
                        fighter.glide = False
                    if event.key == pg.K_s:
                        fighter.brake = False
            if event.type == pg.MOUSEBUTTONDOWN:
                if weapon == 0:
                    fighter.flaming = False
                    fighter.shooting = True
                    if time() >= fighter.shot + fighter.fire_rate:
                        if fighter.guns is None:
                            shoots.append(Shoot(fighter.x, fighter.y, fighter.actual_speed + 10, fighter.lock_angle,
                                                fighter.damage, red_blast, fighter))
                        else:
                            for gun in fighter.guns:
                                nr = fighter.guns.index(gun)
                                shoots.append(Shoot(fighter.x - sin(radians(fighter.angle + 90)) * gun,
                                                    fighter.y - cos(radians(fighter.angle + 90)) * gun,
                                                    fighter.actual_speed + 10, fighter.lock_angles[nr],
                                                    fighter.damage, red_blast, fighter))
                        if sounds:
                            pg.mixer.Sound.play(laser)
                        fighter.shot = time()
                elif weapon == 1:
                    fighter.flaming = True
                    fighter.shooting = False
            if event.type == pg.MOUSEBUTTONUP:
                fighter.flaming = False
                fighter.shooting = False
            if event.type == pg.MOUSEWHEEL:
                if event.y == 1:
                    weapon -= 1
                if event.y == -1:
                    weapon += 1
                if weapon > 1:
                    weapon = 0
                if weapon < 0:
                    weapon = 1

        screen.fill((0, 0, 0))
# Stars
        for star in stars:
            pg.draw.circle(screen, (255, 255, 255), star, 1)
        if mode == "defend":
            if time() >= bot_start+120:
                running = False
                result = True
            if time() >= bot_spawn+10:
                bot_spawn = time()
                for x in range(0, 5):
                    hp, damage, rate, speed, botclass = create_bot(mode)
                    bots.append(Bot((x_max/6)*(x+1), 0, dronepng, hp, damage, rate, botclass, speed))
        if controllers > 0:
            controller_check(fighter, controller, bots, objects)

        for obj in objects:
            obj.move()
            pg.draw.rect(screen, (255, 0, 0), [obj.x-obj.hitbox/2, obj.y-obj.hitbox/2,
                                               obj.hitbox, obj.hitbox], 2)
            screen.blit(obj.image, (obj.x-obj.image.get_width()/2, obj.y-obj.image.get_height()/2))
        for obj in objects:
            if control_overlaps(obj, fighter):
                minus_shield(fighter, 100)
                if controllers >= 1:
                    vibratetil = time()+0.3
                    controller.rumble(0, 1, 0)
                objects.remove(obj)
                break

        for shoot in shoots:
            if shoot.delete():
                shoots.remove(shoot)
                break
        for shoot in shoots:
            shoot.move()
            if shoot.inside:
                if not control_overlaps(shoot.direction, shoot.parent):
                    shoot.inside = False
        removables = []
        for shoot in shoots:
            if not shoot.inside:
                for asteroid in objects:
                    if control_overlaps(shoot.direction, asteroid):
                        removables.append(shoot)
                        shoot.remove = True
                for bot in bots:
                    if control_overlaps(shoot.direction, bot):
                        if not bot.dead:
                            bot.hp -= shoot.damage
                            removables.append(shoot)
                            shoot.remove = True
                if control_overlaps(shoot.direction, fighter):
                    minus_shield(fighter, shoot.damage)
                    removables.append(shoot)
                    shoot.remove = True
            screen.blit(shoot.image, (shoot.x-shoot.image.get_width()/2, shoot.y-shoot.image.get_height()/2))
        while len(removables) > 0:
            shoot = removables[0]
            if shoot in shoots:
                shoots.remove(shoot)
                removables.remove(shoot)
            else:
                removables = []

        for bot in bots:
            target = None
            if mode == "free for all":
                enemies = [(fighter, dist((fighter.x, fighter.y), (bot.x, bot.y)))]
                for bot1 in bots:
                    if bot1 != bot:
                        enemies.append((bot1, dist((bot1.x, bot1.y), (bot.x, bot.y))))
                enemies = sorted(enemies, key=lambda tup: tup[1])
                if not bot.dead:
                    bot.attack(enemies[0][0], objects)
                    target = enemies[0][0]
            elif mode == "defend":
                if dist((bot.x, bot.y), (fighter.x, fighter.y)) <= x_max/4:
                    bot.attack(fighter, objects)
                    target = fighter
                else:
                    bot.attack(None, objects)
                if bot.y >= y_max:
                    running = False
                    result = False
            else:
                if not bot.dead:
                    bot.attack(fighter, objects)
                    target = fighter
            pg.draw.rect(screen, bot.rect_color, [bot.x - bot.hitbox / 2, bot.y - bot.hitbox / 2,
                                                  bot.hitbox, bot.hitbox], 2)
            screen.blit(bot.image, (bot.x - bot.actual_size[0] / 2, bot.y - bot.actual_size[1] / 2))
            pg.draw.line(screen, (255, 0, 0), (bot.x - bot.hitbox / 2, bot.y - bot.hitbox / 2 - 10),
                         ((bot.x - bot.hitbox / 2) + bot.hp * (bot.hitbox / bot.max_hp), bot.y - bot.hitbox / 2 - 10),
                         4)
            if control_overlaps(fighter, bot):
                if not bot.dead:
                    if fighter.shield > 0:
                        fighter.shield -= bot.hp
                        bot.hp = 0
                    else:
                        bothp = bot.hp
                        bot.hp -= fighter.hp
                        fighter.hp -= bothp
            if time() >= bot.shot + bot.fire_rate:
                if not bot.dead and target is not None:
                    bot.shot = time()
                    if bot.botclass == "Sniper":
                        target_system(bot, [fighter])
                        for gun in bot.guns:
                            nr = bot.guns.index(gun)
                            shoots.append(Shoot(bot.x - sin(radians(bot.angle + 90)) * gun,
                                                bot.y - cos(radians(bot.angle + 90)) * gun,
                                                bot.actual_speed + 10, bot.lock_angles[nr],
                                                bot.damage, red_blast, bot))
                    if bot.botclass != "FlameBot" and bot.botclass != "Kamikaze" and bot.botclass != "Sniper":
                        if bot.guns is None:
                            shoots.append(Shoot(bot.x, bot.y, bot.actual_speed + 10, bot.angle,
                                                bot.damage, red_blast, fighter))
                            if sounds:
                                pg.mixer.Sound.play(laser)
                        else:
                            for gun in bot.guns:
                                nr = bot.guns.index(gun)
                                shoots.append(Shoot(bot.x - sin(radians(bot.angle + 90)) * gun,
                                                    bot.y - cos(radians(bot.angle + 90)) * gun,
                                                    bot.actual_speed + 10, bot.angle,
                                                    bot.damage, red_blast, bot))
                                if sounds:
                                    pg.mixer.Sound.play(laser)
                    elif bot.botclass == "FlameBot":
                        flamethrower(bot, 0.3, 7)

        for bot in bots:
            if bot.hp <= 0:
                if not bot.dead:
                    bot.death_time = time() + 2
                    bot.dead = True
                else:
                    if time() >= bot.death_time:
                        bots.remove(bot)
                        XP += 50
                        break
                    else:
                        flame = pg.image.load("fireball.png")
                        flame = pg.transform.scale(flame, (100, 100))
                        screen.blit(flame, (bot.x - flame.get_width() / 2, bot.y - flame.get_height() / 2))

        fighter.run_move(controller)
        if fighter.flaming:
            if fighter.fuel > 0:
                fighter.fuel -= 2
                flamethrower(fighter, fighter.speed + 3, chance=8, spread=4)
        if fighter.shooting:
            if time() >= fighter.shot + fighter.fire_rate:
                if fighter.guns is None:
                    shoots.append(Shoot(fighter.x, fighter.y, fighter.actual_speed + 10, fighter.lock_angle,
                                        fighter.damage, red_blast, fighter))
                else:
                    for gun in fighter.guns:
                        nr = fighter.guns.index(gun)
                        shoots.append(Shoot(fighter.x - sin(radians(fighter.angle + 90)) * gun,
                                            fighter.y - cos(radians(fighter.angle + 90)) * gun,
                                            fighter.actual_speed + 10, fighter.lock_angles[nr],
                                            fighter.damage, red_blast, fighter))
                if sounds:
                    pg.mixer.Sound.play(laser)
                fighter.shot = time()
        screen.blit(fighter.image,
                    (int(fighter.x - fighter.actual_size[0] / 2), int(fighter.y - fighter.actual_size[1] / 2)))
        pg.draw.rect(screen, fighter.rect_color, [int(fighter.x - fighter.hitbox / 2), int(fighter.y - fighter.hitbox / 2),
                                                  int(fighter.hitbox), int(fighter.hitbox)], 2)
        if fighter.rect_color == (0, 0, 0):
            length = fighter.shield*((fighter.hitbox*4)/fighter.max_shield)
            if length > fighter.hitbox:
                rest = fighter.hitbox
            else:
                rest = length
            pg.draw.line(screen, (0, 255, 200), (fighter.x-fighter.hitbox/2, fighter.y-fighter.hitbox/2),
                         ((fighter.x-fighter.hitbox/2)+rest, fighter.y-fighter.hitbox/2), 4)
            if length > fighter.hitbox*2:
                rest = fighter.hitbox
            elif length > fighter.hitbox:
                rest = length-fighter.hitbox
            else:
                rest = 0
            if rest > 0:
                pg.draw.line(screen, (0, 255, 200), (fighter.x-2+fighter.hitbox/2, fighter.y-fighter.hitbox/2),
                             (fighter.x-2+fighter.hitbox/2, (fighter.y-fighter.hitbox/2)+rest), 4)
            if length > fighter.hitbox*3:
                rest = fighter.hitbox
            elif length > fighter.hitbox*2:
                rest = length-fighter.hitbox*2
            else:
                rest = 0
            if rest > 0:
                pg.draw.line(screen, (0, 255, 200), (fighter.x+fighter.hitbox/2, fighter.y-2+fighter.hitbox/2),
                             ((fighter.x+fighter.hitbox/2)-rest, fighter.y-2+fighter.hitbox/2), 4)
            rest = length-fighter.hitbox*3
            if rest < 0:
                rest = 0
            if rest > 0:
                pg.draw.line(screen, (0, 255, 200), (fighter.x-fighter.hitbox/2, fighter.y+fighter.hitbox/2),
                             (fighter.x-fighter.hitbox/2, (fighter.y+fighter.hitbox/2)-rest), 4)
        fighter.rect_color = (255, 255, 255)
        if fighter.shield >= 1:
            fighter.rect_color = (0, 0, 0)
        color = (255, 0, 0)
        if fighter.shield > 0:
            color = (0, 255, 200)
        show_text(str(int(fighter.hp)), color, int(fighter.x), int(fighter.y - fighter.size))

        targets = [fighter]
        for bot in bots:
            targets.append(bot)
        for bot in bots:
            targets.append(bot)
            bot.rect_color = (255, 255, 255)
        targets = []
        for bot in bots:
            targets.append(bot)
        bot = target_system(fighter, targets)
        if bot is not None:
            bot.rect_color = (255, 0, 0)
        for bot in bots:
            targets.append(bot)
        if mode == "defend":
            show_text(str(120-int(time()-bot_start)))
        pg.display.update()

        if mode != "defend":
            if len(bots) <= 0:
                screen.fill((0, 0, 0))
                result = True
                fighter.xp += XP + 100
                currency += reward
                running = False

        value = 1
        if (fighter.hp <= 0) or (value <= 0):
            running = False
        if controller is not None:
            if time() > vibratetil and not vibrating:
                controller.stop_rumble()

    found = False
    for ShipData in data["ShipsData"].values():
        if ShipData["Name"] == fighter.name:
            ShipData["XP"] = fighter.xp
            found = True
            break
    if not found:
        data["ShipsData"][fighter.name] = {
            "Name": fighter.name,
            "XP": fighter.xp
        }
    data["Balance"] = currency
    data["TotalXP"] += fighter.xp - startXP
    SaveData(data)
    DisplayResults(result, data["TotalXP"], reward, fighter.xp-startXP)


def DisplayResults(result, XP, reward, extra_exp):
    ResetAnimations()
    running = True
    TotalXPDelta = XP - extra_exp
    XPDelta = 0
    RewardDelta = 0
    while running:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                        done = False
                        ResetAnimations()
                        if result == True:
                            while not done:
                                screen.fill((0, 0, 0))
                                done = AnimatedText(255, 0, x_max/2, y_max/3, f"Battle Won", 0.5, "fade", (255,255,255), None, False, 200, 0, 0.01)
                                AnimatedText(255, 0, x_max/2, y_max/2, f"Reward: {reward}", 0.5, "fade", (255,255,255), None, True, 50, 0, 0.01)
                                AnimatedText(255, 0, x_max/2, y_max/2+50, f"XP: {extra_exp}", 0.5, "fade", (255,255,255), None, True, 50, 0, 0.01)
                                AnimatedText(255, 0, x_max/2, y_max/2+100, f"Total XP: {XP}", 0.5, "fade", (255,255,255), None, True, 50, 0, 0.01)
                                pg.display.update()
                        else:
                            while not done:
                                screen.fill((0, 0, 0))
                                done = AnimatedText(255, 0, x_max/2, y_max/2, f"Battle Lost", 0.5, "fade", (255,0,0), None, False, 200, 0, 0.01)
                                pg.display.update()
                        running = False
        screen.fill((0, 0, 0))
        TotalXPDelta = min(TotalXPDelta + 1, XP)
        RewardDelta = min(RewardDelta + 1, reward)
        XPDelta = min(XPDelta + 1, extra_exp)
        if result == True and running == True:
            if AnimatedText(x_max/2, y_max/2, x_max/2, y_max/3, f"Battle Won", 5, "constant", (255,255,255), 1, False, 200):
                show_text(f"Reward: {int(RewardDelta)}", (255, 255, 255), x_max/2, y_max/2)
                show_text(f"XP: {int(XPDelta)}", (255, 255, 255), x_max/2, y_max/2+50)
                show_text(f"Total XP: {int(TotalXPDelta)}", (255, 255, 255), x_max/2, y_max/2+100)
        if result == False and running == True:
            show_text(f"Battle Lost", (255,0,0), x_max/2, y_max/2, 200)
        show_text("Press Space to continue", (255, 255, 255), x_max/2, y_max - y_max / 10, 40)
        pg.display.update()