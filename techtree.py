from classes import *
import json
import time as tm
import random

data = [0, []]
level = 0
xwingpng = pg.image.load("xwing.png")
bomberpng = pg.image.load("bomber.png")
xfieldmax = x_max
yfieldmax = y_max
logs = []
GlobalAnimation = 1

try:
    with open('data.json') as f:
        data = json.load(f)
        print(data)
except:
    with open("data.json", "w") as outfile:
        json.dump(data, outfile)
        print("File created")


def show_text(content, color=(255, 255, 0), start_x=x_max/2, start_y=100, end_size=50, centring=0, 
              fat=False, italic=False, alpha=255):
    text = content.split("\n")
    if len(text) >= 2:
        del text[0]

    font = pg.font.SysFont('ubuntumono', end_size, fat, italic)
    show_y = start_y

    for line in text:
        info = font.render(line, True, color)
        info.set_alpha(alpha)

        if centring == 0:
            screen.blit(info, (start_x - info.get_width() / 2, show_y - info.get_height() / 2))
        elif centring == 1:
            screen.blit(info, (start_x, show_y - info.get_height() / 2))
        else:
            screen.blit(info, (start_x - info.get_width(), show_y - info.get_height() / 2))
        
        show_y += info.get_height()

    return show_y - start_y

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

def InfoBox(x, y, size_x, size_y, Title, Unlocketion,  color=(255, 255, 0), textColor=(255, 255, 255)):
    pg.draw.rect(screen, (color), (x, y, size_x, size_y))
    show_text(Title, textColor, x + size_x / 20, y + size_y / 4, 50, 1, True, False)
    show_text(Unlocketion, textColor, x + size_x / 20, y + size_y - size_y/4, 22, 1, True, False)


def treeing():
    stars = []
    i=0
    while i < 100: 
        stars.append((random.randint(0, x_max), random.randint(0, y_max)))
        i += 1
    used = True
    ships = [XWing(xwingpng, None, 0), Bomber(bomberpng, None, 0)]
    overwritelines = True
    Selected_x, Selected_y = 0, 0
    start, end, t = (0, 0), (0, 0), 0
    blink = 0
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
                for ship in ships:
                    if in_rect(pg.mouse.get_pos(),
                               [ship.x-ship.image.get_width()/2, ship.y-ship.image.get_height()/2,
                                ship.x+ship.image.get_width()/2, ship.y+ship.image.get_height()/2]):
                        if ship.own:
                            data[2] = ship.name
            if event.type == pg.MOUSEBUTTONDOWN:
                overwritelines = True
                Selected_x, Selected_y = pg.mouse.get_pos()
                for ship in ships:
                    if ship.x - ship.image.get_width()/2 < Selected_x < ship.x+ship.image.get_width()/2 and ship.y - ship.image.get_width()/2 < Selected_y < ship.y+ship.image.get_height()/2:
                            if ship.root is not None:
                                start, end, t = (ship.root.x, ship.root.y), (ship.x, ship.y), 0
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
                                for xp in data[1]:
                                    if xp[0] == ship.root.name:
                                        xp[1] = xp[1] - ship.price
                                        found = True
                                        break
                                if not found:
                                    print("Couldn't find root ship")
                                    ship.own = False
        for xp in data[1]:
            for ship in ships:
                if xp[0] == ship.name:
                    ship.xp = xp[1]
                    if ship.xp > 0:
                        ship.own = True
        for ship in ships:
            ship.x, ship.y = ship.shop_x*xfieldmax, ship.shop_y*yfieldmax
            if ship.x - ship.image.get_width()/2 < pg.mouse.get_pos()[0] < ship.x+ship.image.get_width()/2 and ship.y - ship.image.get_width()/2 < pg.mouse.get_pos()[1] < ship.y+ship.image.get_height()/2:
                    if ship.root is not None:
                        if ship.price <= ship.root.xp:
                            if blink >= 0 and blink <= 125:
                                InfoBox(ship.x + ship.image.get_width()/3, ship.y+ship.image.get_height()/3, x_max/4, y_max/8, f"Hold To Unlock", f"{ship.root.name}: {ship.root.xp}/{ship.price}", (44, 117, 255))
                                blink += 1
                            if blink >= 125 and blink <= 250:
                                InfoBox(ship.x + ship.image.get_width()/3, ship.y+ship.image.get_height()/3, x_max/4, y_max/8, f"{ship.name}", f"{ship.root.name}: {ship.root.xp}/{ship.price}", (44, 117, 255))
                                blink += 1
                            if blink >= 250:
                                blink = 0
                        else:
                            InfoBox(ship.x + ship.image.get_width()/3, ship.y+ship.image.get_height()/3, x_max/4, y_max/8, str(ship.name), f"{ship.root.name}: {ship.root.xp}/{ship.price}", (44, 117, 255))

                    else:
                        InfoBox(ship.x + ship.image.get_width()/3, ship.y+ship.image.get_height()/3, x_max/4, y_max/8, str(ship.name), f"Root ship: {ship.xp}", (44, 117, 255))
        for ship in ships:
            for ship1 in ships:
                if ship1.name == ship.root:
                    ship.root = ship1
            if ship.root is not None and overwritelines is False:
                pg.draw.line(screen, (150, 150, 150), (ship.x, ship.y), (ship.root.x, ship.root.y))
                if ship.root.xp >= 1000:
                    if data[0] >= ship.price:
                        ship.buy = True
            screen.blit(ship.image, (ship.x-ship.image.get_width()/2, ship.y-ship.image.get_height()/2))
            color = (100, 100, 100)
            if ship.buy:
                color = (200, 200, 200)
            if ship.own:
                color = (0, 255, 0)
            pg.draw.rect(screen, color, [ship.x-ship.image.get_width()/2, ship.y-ship.image.get_height()/2,
                                         ship.image.get_width(), ship.image.get_height()], 2)
        pg.display.update()

    with open("data.json", "w") as outfile:
        json.dump(data, outfile)
