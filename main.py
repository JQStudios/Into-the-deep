from menu import *
from classes import screen, x_max, y_max

pg.init()
pg.font.init()
font = pg.font.Font("assets/fonts/Starjedi.ttf", 22)
pg.mixer.init()

# example

pg.display.set_caption("Menu Example")
buttons = []
running = True
message = None
size_x, size_y = button_dynamic_size(100, 100, y_max - y_max / 6, 200)
while running:
    buttons = []
    screen.fill((0, 0, 0))
    buttons = CreateMenu(x_max/20,y_max-y_max/6, size_x, size_y, 4, x_max/4, 0, "h", "MenuButton", pg.mouse.get_pos(), ["play", "options", "credits", "quit"], ["play", "options", "credits", "quit"], buttons)
    if buttons is None:
        buttons = updateMenus(buttons)
    DisplayMenus(buttons, pg.mouse.get_pos())
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                execButtonAction("main_menu", 0, 0)
        if event.type == pg.MOUSEBUTTONDOWN:
            mousepos = pg.mouse.get_pos()
            CheckMenu(buttons, mousepos)
    
    message = get_message()
    
    if message:
        message.update()
        if message.is_done():
            message = None

    pg.display.update()
pg.quit()
