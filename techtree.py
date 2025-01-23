from classes import *
import json

data = [0, []]
level = 0
xwingpng = pg.image.load("xwing.png")
bomberpng = pg.image.load("bomber.png")
xfieldmax = x_max
yfieldmax = y_max


def treeing():
    used = True
    while used:
        try:
            with open('data.json') as f:
                data = json.load(f)
                print(data)
        except:
            with open("data.json", "w") as outfile:
                json.dump(data, outfile)
                print("File created")

        ships = [XWing(xwingpng, None, 0), Bomber(bomberpng, None, 0)]
        for xp in data[1]:
            for ship in ships:
                if xp[0] == ship.name:
                    ship.xp = xp[1]
        for ship in ships:
            ship.x, ship.y = randint(0, x_max), randint(0, y_max)
        screen.fill((0, 0, 0))
        for ship in ships:
            for ship1 in ships:
                if ship1.name == ship.root:
                    ship.root = ship1
            if ship.root is not None:
                pg.draw.line(screen, (150, 150, 150), (ship.x, ship.y), (ship.root.x, ship.root.y))
                if ship.root.xp >= 1000:
                    if data[0] >= ship.price:
                        ship.buy = True
            screen.blit(ship.image, (ship.shop_x*xfieldmax-ship.image.get_width()/2,
                                     ship.shop_y*yfieldmax-ship.image.get_height()/2))
            color = (100, 100, 100)
            if ship.buy:
                color = (200, 200, 200)
            if ship.own:
                color = (0, 255, 0)
            pg.draw.rect(screen, color, [ship.x-ship.image.get_width()/2, ship.y-ship.image.get_height()/2,
                                         ship.image.get_width(), ship.image.get_height()], 2)
            pg.display.update()
