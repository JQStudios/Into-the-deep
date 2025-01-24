from classes import *


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


def check_button(button, pos):
    if (button[0] <= pos[0] <= button[0]+button[2]) and \
            (button[1] <= pos[1] <= button[1]+button[3]):
        return True


running = True
selected = []
ship_class = None
ok = False
state = 0
buttons = []


def select_mode(pos):
    global buttons
    buttons = [[(x_max/5)*1-50, y_max/2, 100, 100, (0, 255, 0), 2, "Arcade"],
               [(x_max/5)*2.5-50, y_max/2, 100, 100, (0, 255, 0), 2, "Coop"],
               [(x_max/5)*4-50, y_max/2, 100, 100, (0, 255, 0), 2, "1 v 1"]]
    if check_button(buttons[0], pos):
        return 0, 1
    elif check_button(buttons[1], pos):
        return 1, 1
    elif check_button(buttons[2], pos):
        return 2, 1
    else:
        return 0, 0


def select_ship(pos):
    global selected, ok, ship_class, buttons
    buttons = [[x_max / 2 - 50, y_max - 100, 100, 100, (0, 255, 0), 2, "Start"],
               [x_max / 7 - 50, y_max - 500, 100, 100, (255, 0, 0), 2, "X-Wing"],
               [(x_max / 7) * 2 - 50, y_max - 500, 100, 100, (255, 0, 0), 2, "Bomber"]]

    if check_button(buttons[0], pos):
        if len(selected) >= 1:
            ok = True
    if check_button(buttons[1], pos):
        ship_class = "x_wing"
        if "ship" not in selected:
            selected.append("ship")
    if check_button(buttons[2], pos):
        ship_class = "bomber"
        if "ship" not in selected:
            selected.append("ship")


def select_ships(pos):
    global selected, ok, ship_class, buttons
    buttons = [[x_max / 2 - 50, y_max - 100, 100, 100, (0, 255, 0), 2, "Start"],
               [x_max / 7 - 50, y_max - 500, 100, 100, (255, 0, 0), 2, "X-Wing"],
               [(x_max / 7) * 2 - 50, y_max - 500, 100, 100, (255, 0, 0), 2, "Bomber"]]

    if check_button(buttons[0], pos):
        if len(selected) >= 2:
            ok = True
    if check_button(buttons[1], pos):
        ship_class = "x_wing"
        if "ship" not in selected:
            selected.append("ship")
    if check_button(buttons[2], pos):
        ship_class = "bomber"
        if "ship" not in selected:
            selected.append("ship")


def select():
    global running, ok, ship_class, state, selected, buttons
    mode = 0
    ship1_class = None
    fighters = 0
    mode, state = select_mode((0, 0))

    while not ok:
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                mousepos = pg.mouse.get_pos()
                if state == 0:
                    mode, state = select_mode(mousepos)
                    if mode == 0:
                        fighters = 1
                        bots = 10
                    elif mode == 1:
                        fighters = 2
                        bots = 15
                    else:
                        fighters = 2
                        bots = 0
                elif state == 1:
                    if mode == 0:
                        select_ship(mousepos)
                    else:
                        select_ships(mousepos)

        if not running:
            ok = True
        screen.fill((0, 0, 0))
        for button in buttons:
            pg.draw.rect(screen, button[4], [button[0], button[1], button[2], button[3]], button[5])
            show_text(button[6], button[4], button[0]+button[2]/2, button[1]+button[3]/2)
        pg.display.update()
    return ship_class, ship1_class, fighters, bots
