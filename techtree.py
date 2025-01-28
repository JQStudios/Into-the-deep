from classes import *
import json
import time as tm

data = [0, []]
level = 0
xwingpng = pg.image.load("xwing.png")
bomberpng = pg.image.load("bomber.png")
xfieldmax = x_max
yfieldmax = y_max

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
              fat=False, italic=False):
    text = content.split("\n")
    if len(text) >= 2:
        del text[0]
    font = pg.font.SysFont('ubuntumono', end_size, fat, italic)
    show_y = start_y
    for line in text:
        info = font.render(line, True, color)
        if centring == 0:
            screen.blit(info, (start_x-info.get_width()/2, show_y-info.get_height()/2))
        elif centring == 1:
            screen.blit(info, (start_x, show_y-info.get_height()/2))
        else:
            screen.blit(info, (start_x-info.get_width(), show_y-info.get_height()/2))
        show_y += info.get_height()
    return show_y-start_y

def AnimatedText(Start_x, Start_y, End_x, End_y, content, time, type="c", color=(255, 255, 0), intervalSek=0, end_size=50, centring=0, updateinterval=0.1):
    global GlobalAnimation
    steps = int(time/updateinterval)
    interval = int(intervalSek/updateinterval)
    if steps > GlobalAnimation:
        GlobalAnimation += 1
        if interval>GlobalAnimation:
            tm.sleep(updateinterval)
            x, y = Start_x, Start_y
            show_text(content, color, x, y, end_size, centring=centring)
        else:
            tm.sleep(updateinterval)
            LocalGlobalAnimation = (GlobalAnimation -interval)/steps
            if type == "c":
                x = Start_x + LocalGlobalAnimation * (End_x - Start_x)
                y = Start_y + LocalGlobalAnimation * (End_y - Start_y)
                show_text(content, color, x, y, end_size, centring=centring)
    else:
        x = End_x
        y = End_y
        show_text(content, color, x, y, end_size, centring=centring)


def treeing():
    used = True
    ships = [XWing(xwingpng, None, 0), Bomber(bomberpng, None, 0)]
    while used:
        screen.fill((0, 0, 0))
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    used = False
            if event.type == pg.MOUSEBUTTONUP:
                for ship in ships:
                    if in_rect(pg.mouse.get_pos(),
                               [ship.x-ship.image.get_width()/2, ship.y-ship.image.get_height()/2,
                                ship.x+ship.image.get_width()/2, ship.y+ship.image.get_height()/2]):
                        if ship.own:
                            show_text("Select", (0, 255, 0), x_max, centring=-1)
                        elif ship.buy:
                            show_text("Buy", (0, 255, 255), x_max, centring=-1)


        for xp in data[1]:
            for ship in ships:
                if xp[0] == ship.name:
                    ship.xp = xp[1]
        for ship in ships:
            ship.x, ship.y = ship.shop_x*xfieldmax, ship.shop_y*yfieldmax
        for ship in ships:
            for ship1 in ships:
                if ship1.name == ship.root:
                    ship.root = ship1
            if ship.root is not None:
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
