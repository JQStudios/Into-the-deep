from classes import *
import json
import time as tm
import random
import math
import menu

data = []
level = 0
xwingpng = pg.image.load("xwing.png")
bomberpng = pg.image.load("bomber.png")
lightcruiserpng = pg.image.load("LightCruiser.png")
xfieldmax = x_max
yfieldmax = y_max
logs = []
GlobalAnimation = 1




def show_text(content, color=(255, 255, 0), start_x=x_max/2, start_y=100, end_size=50, centring=0, 
              fat=False, italic=False, alpha=255, font=None):
    text = content.split("\n")
    if len(text) >= 2:
        del text[0]
    if font is None:
        font = pg.font.SysFont('ubuntumono', end_size, fat, italic)
        
    show_y = start_y
    max_width = 0

    for line in text:
        info = font.render(line, True, color)
        info.set_alpha(alpha)

        if centring == 0:
            screen.blit(info, (start_x - info.get_width() / 2, show_y - info.get_height() / 2))
        elif centring == 1:
            screen.blit(info, (start_x, show_y - info.get_height() / 2))
        else:
            screen.blit(info, (start_x - info.get_width(), show_y - info.get_height() / 2))
        
        max_width = max(max_width, info.get_width())
        
        show_y += info.get_height()

    total_height = show_y - start_y

    return max_width, total_height

def ResetAnimations():
    global GlobalAnimation
    GlobalAnimation = 1

def AnimatedText(Start_x, Start_y, End_x, End_y, content, time, type="constant", color=(255, 255, 0), intervalSek=0, AnimationGroup=False,
                 end_size=50, centring=0, updateinterval=0.1):
    # Types: constant, fade
    # constant: constant movement text animation
    # fade: constant fade text animation
    # Time: How long should the animation take?(in sek), IntervalSek: How long should the interval be?(if you don't want an interval, set it to 0 or None), Update: How often should the animation be updated?(like frames)
    # AnimationGroup: Select a leader wich you'll set animation group to False, the other animations you will set AnimationGroup to True the leader will do the tm.sleeps so the animations need to be equal in time and updateinterval
    # ResetAnimations(): use it before you use new animtions
    global GlobalAnimation, logs
    steps = int(time / updateinterval)
    if not intervalSek == None and not intervalSek == 0:
        interval = int(intervalSek / updateinterval)
    else:
        interval = 0
    done = False

    if steps > GlobalAnimation:
        if not AnimationGroup:
            GlobalAnimation += 1
            tm.sleep(updateinterval)
        if interval > GlobalAnimation:
            if type == "constant":
                x, y = Start_x, Start_y
                alpha = 255
            elif type == "fade":
                x, y = End_x, End_y
                alpha = int(Start_x)
            show_text(content, color, x, y, end_size, centring=centring, alpha=alpha)
        else:
            LocalGlobalAnimation = (GlobalAnimation - interval) / (steps - interval)

            if type == "constant":
                x = Start_x + LocalGlobalAnimation * (End_x - Start_x)
                y = Start_y + LocalGlobalAnimation * (End_y - Start_y)
                alpha = 255

            elif type == "fade":
                x, y = End_x, End_y
                alpha = int(Start_x + LocalGlobalAnimation * (Start_y - Start_x))
                alpha = max(0, min(255, alpha))

            show_text(content, color, x, y, end_size, centring=centring, alpha=alpha)
    else:
        done = True
        x, y = End_x, End_y
        alpha = int(Start_y) if type == "fade" else 255
        show_text(content, color, x, y, end_size, centring=centring, alpha=alpha)
    
    return done

import math
import pygame as pg

def ZoomInRect(screen, center, min_size, progress):
    done = False
    alpha = min(255, int(255 * progress * 2))

    ease_in = 1 - math.cos((progress * math.pi) / 2)
    
    max_size = (min_size[0] * 6, min_size[1] * 6)  
    current_width = max_size[0] - (max_size[0] - min_size[0]) * ease_in
    current_height = max_size[1] - (max_size[1] - min_size[1]) * ease_in
    if current_width <= min_size[0]:
        current_width = min_size[0]
        current_height = min_size[1]
        done = True


    rect = pg.Rect(0, 0, current_width, current_height)
    rect.center = center

    surface = pg.Surface((rect.width, rect.height), pg.SRCALPHA)
    
    border_color = (0, 255, 0, alpha)
    border_width = 2

    pg.draw.rect(surface, border_color, surface.get_rect(), border_width)

    screen.blit(surface, rect.topleft)

    return done
def InfoBox(x, y, size_x, size_y, Title, Unlocketion, speed, damage, hp, color=(255, 255, 0), textColor=(255, 255, 255)):
    pg.draw.rect(screen, color, (x, y, size_x, size_y))
    show_text(Title, textColor, x + size_x / 20, y + size_y / 4, 60, 1, True, False)
    line_y = y + size_y / 2.5
    pg.draw.line(screen, (255,255,255), (x + size_x / 25, line_y), (x + size_x - size_x / 25, line_y))
    TextSize_x, TextSize_y = show_text(Unlocketion, textColor, x + size_x / 20, y + size_y - size_y/2, 22, 1, True, False)
    show_text(speed, textColor, x + size_x / 20, y + size_y - size_y/2 + (TextSize_y*1.2) , 22, 1, True, False)
    show_text(damage, textColor, x + size_x / 20, y + size_y - size_y/2 + (TextSize_y*2.4), 22, 1, True, False)
    show_text(hp, textColor, x + size_x / 20, y + size_y  -size_y/2 + (TextSize_y*3.6), 22, 1, True, False)


def TechtreeAction(action = "select", ship_name = "X-Wing", data=None, price = None):
    if data == None:
        print("No data specified")
        return ""
    if action == "select":
        data["Selection"] = ship_name
    if action == "unlock":
        if ship_name == "X-Wing":
            newData = {
                "Name": ship_name,
                "XP": 0,
                "Owned": True,
                "Bought": True
            }
        else:
            newData = {
                "Name": ship_name,
                "XP": 0,
                "Owned": True,
                "Bought": False
            }
        data["ShipsData"][ship_name] = newData
    if action == "buy":
        data["ShipsData"][ship_name]["Bought"] = True
        if price == None:
            print("No price specified")
            return ""
        data["Balance"] -= price
    return data    


def treeing():
    data = LoadData()
    stars = []
    i=0
    while i < 100: 
        stars.append((random.randint(0, x_max), random.randint(0, y_max)))
        i += 1
    used = True
    ships = [XWing(xwingpng, None, 0), Bomber(bomberpng, None, 0), LightCruiser(lightcruiserpng, None, 0)]
    for ship in ships:
        for shipdata in data["ShipsData"].values():
            if ship.name == shipdata["Name"]:
                ship.own = shipdata["Owned"]
                ship.buy = shipdata["Bought"]
                print(f"{ship.name}: owned: {ship.own}, bought: {ship.buy}")
    overwritelines = True
    Selected_x, Selected_y = 0, 0
    start, end, t = (0, 0), (0, 0), 0
    blink = 0
    zoom_active = False
    while used:
        screen.fill((0, 0, 0))
        for star in stars:
            pg.draw.circle(screen, (255, 255, 255), star, 2)
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    used = False
            if event.type == pg.MOUSEBUTTONUP:
                start, end, t = (0, 0), (0, 0), 0
                overwritelines = False
                zoom_active = False
                zoom_progress = 0
                for ship in ships:
                    if in_rect(pg.mouse.get_pos(),
                               [ship.x-ship.image.get_width()/2, ship.y-ship.image.get_height()/2,
                                ship.x+ship.image.get_width()/2, ship.y+ship.image.get_height()/2]):
                        if ship.own:
                            pass
            if event.type == pg.MOUSEBUTTONDOWN:
                overwritelines = True
                Selected_x, Selected_y = pg.mouse.get_pos()
                for ship in ships:
                    if ship.x - ship.image.get_width()/2 < Selected_x < ship.x+ship.image.get_width()/2 and ship.y - ship.image.get_width()/2 < Selected_y < ship.y+ship.image.get_height()/2:
                            if ship.root is not None:
                                start, end, t = (ship.root.x, ship.root.y), (ship.x, ship.y), 0
                            if ship.own:
                                zoom_active = True
                                zoom_progress = 0
                                zoom_x, zoom_y, zoom_min_size_x, zoom_min_size_y = ship.x, ship.y, ship.image.get_width(), ship.image.get_height()
                                zoom_speed = 0.002
                                zoom_action = "buy"
                            if ship.buy:
                                zoom_active = True
                                zoom_progress = 0
                                zoom_x, zoom_y, zoom_min_size_x, zoom_min_size_y = ship.x, ship.y, ship.image.get_width(), ship.image.get_height()
                                zoom_speed = 0.02
                                zoom_action = "select"
                                zoom_select = ship.name
        if zoom_active:
            zoom_progress += zoom_speed
            if ZoomInRect(screen, (zoom_x, zoom_y), (zoom_min_size_x, zoom_min_size_y), zoom_progress) and zoom_action == "buy":
                for ship in ships:
                    if ship.x == zoom_x and data["ShipsData"][ship.name]["Bought"] == False:
                        ship.buy = True
                        data = TechtreeAction("buy", ship.name, data, ship.price)
            if ZoomInRect(screen, (zoom_x, zoom_y), (zoom_min_size_x, zoom_min_size_y), zoom_progress) and zoom_action == "select":
                data = TechtreeAction("select", zoom_select, data)
        if overwritelines:
            t = min(t + 0.00025, 1) 
            current_end = (start[0] + (end[0] - start[0]) * t, start[1] + (end[1] - start[1]) * t)
            pg.draw.line(screen, (44, 117, 255), start, current_end, 4)
            if t == 1:
                for ship in ships:
                    if ship.x - ship.image.get_width()/2 < Selected_x < ship.x+ship.image.get_width()/2 and ship.y - ship.image.get_width()/2 < Selected_y < ship.y+ship.image.get_height()/2:
                            if ship.root is not None and ship.own == False:
                                ship.own = True
                                found = False
                                for shipdata in data["ShipsData"].values():
                                    if shipdata["Name"] == ship.root.name:
                                        data = TechtreeAction("unlock", ship.name, data)
                                        found = True
                                        break
                                if not found:
                                    print(f"Couldn't find root ship for {ship.name}")
                                    ship.own = False
        for ship in ships:
            for ShipData in data["ShipsData"].values():
                try:
                    if ShipData["Name"] == ship.name:
                        ship.own = ShipData["Owned"]
                        ship.buy = ShipData["Bought"]
                        ship.xp = ShipData["XP"]
                        if ship.name == data["Selection"]:
                            ship.select = True
                        else:
                            ship.select = False
                        break
                except Exception as e:
                    ship.own = False
                    ship.buy = False
            ship.x, ship.y = ship.shop_x*xfieldmax, ship.shop_y*yfieldmax
            if ship.x - ship.image.get_width()/2 < pg.mouse.get_pos()[0] < ship.x+ship.image.get_width()/2 and ship.y - ship.image.get_width()/2 < pg.mouse.get_pos()[1] < ship.y+ship.image.get_height()/2:
                    if ship.root is not None:
                        if ship.own == False:
                            if blink >= 0 and blink <= 125 and ship.UnlockXP <= ship.root.xp:
                                InfoBox(ship.x + ship.image.get_width()/3, ship.y+ship.image.get_height()/3, x_max/4, y_max/4, f"Hold To Unlock", f"{ship.root.name}: {ship.root.xp}/{ship.UnlockXP} XP", f"speed: {ship.speed}", f"damage: {ship.damage}", f"HP: {ship.hp}", (44, 117, 255))
                                blink += 1
                            else:
                                #overwritting Blink
                                blink = 150
                            if blink >= 125 and blink <= 250:
                                InfoBox(ship.x + ship.image.get_width()/3, ship.y+ship.image.get_height()/3, x_max/4, y_max/4, f"{ship.name}", f"{ship.root.name}: {ship.root.xp}/{ship.UnlockXP} XP", f"speed: {ship.speed}", f"damage: {ship.damage}", f"HP: {ship.hp}", (44, 117, 255))
                                blink += 1
                            if blink >= 250:
                                blink = 0
                        elif ship.price <= data["Balance"] and ship.buy == False and ship.own == True:
                            if blink >= 0 and blink <= 125:
                                InfoBox(ship.x + ship.image.get_width()/3, ship.y+ship.image.get_height()/3, x_max/4, y_max/4, f"Hold To Buy", f"Price: {data["Balance"]}/{ship.price}", f"speed: {ship.speed}", f"damage: {ship.damage}", f"HP: {ship.hp}", (44, 117, 255))
                                blink += 1
                            if blink >= 125 and blink <= 250:
                                InfoBox(ship.x + ship.image.get_width()/3, ship.y+ship.image.get_height()/3, x_max/4, y_max/4, f"{ship.name}", f"Price: {data["Balance"]}/{ship.price}", f"speed: {ship.speed}", f"damage: {ship.damage}", f"HP: {ship.hp}", (44, 117, 255))
                                blink += 1
                            if blink >= 250:
                                blink = 0
                        else:
                            InfoBox(ship.x + ship.image.get_width()/3, ship.y+ship.image.get_height()/3, x_max/4, y_max/4, str(ship.name), f"XP: {ship.xp}", f"speed: {ship.speed}", f"damage: {ship.damage}", f"HP: {ship.hp}", (44, 117, 255))

                    else:
                        InfoBox(ship.x + ship.image.get_width()/3, ship.y+ship.image.get_height()/3, x_max/4, y_max/4, str(ship.name), f"Root ship: {ship.xp}", f"speed: {ship.speed}", f"damage: {ship.damage}", f"HP: {ship.hp}", (44, 117, 255))
        for ship in ships:
            for ship1 in ships:
                if ship1.name == ship.root:
                    ship.root = ship1
            if ship.root is not None and overwritelines is False:
                pg.draw.line(screen, (150, 150, 150), (ship.x, ship.y), (ship.root.x, ship.root.y))
            screen.blit(ship.image, (ship.x-ship.image.get_width()/2, ship.y-ship.image.get_height()/2))
            color = (100, 100, 100)
            if ship.select:
                color = (0, 255, 0)
            elif ship.buy:
                color = (0,0,200)
            elif ship.own:
                color = (200,200,200)
            pg.draw.rect(screen, color, [ship.x-ship.image.get_width()/2, ship.y-ship.image.get_height()/2,
                                         ship.image.get_width(), ship.image.get_height()], 2)
        menu.ShowBalance(x_max, y_max / 50, screen, (255,255,255))
        pg.display.update()
    SaveData(data)
