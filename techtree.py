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
    ships = [XWing(xwingpng, None, 0), Bomber(bomberpng, None, 0)]
    while used:
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
                            print("play")
                        elif ship.buy:
                            print("buy")


        try:
            with open('data.json') as f:
                data = json.load(f)
                print(data)
        except:
            with open("data.json", "w") as outfile:
                json.dump(data, outfile)
                print("File created")

        for xp in data[1]:
            for ship in ships:
                if xp[0] == ship.name:
                    ship.xp = xp[1]
        for ship in ships:
            ship.x, ship.y = ship.shop_x*xfieldmax, ship.shop_y*yfieldmax
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
            screen.blit(ship.image, (ship.x-ship.image.get_width()/2, ship.y-ship.image.get_height()/2))
            color = (100, 100, 100)
            if ship.buy:
                color = (200, 200, 200)
            if ship.own:
                color = (0, 255, 0)
            pg.draw.rect(screen, color, [ship.x-ship.image.get_width()/2, ship.y-ship.image.get_height()/2,
                                         ship.image.get_width(), ship.image.get_height()], 2)
        pg.display.update()
