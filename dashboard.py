from menu import *
from classes import screen, x_max, y_max

pg.init()
pg.font.init()
font = pg.font.Font("assets/fonts/Starjedi.ttf", 22)


pg.display.set_caption("Dashboard")
buttons = []
running = True
message = None
size_x, size_y =  button_dynamic_size(100, 100, y_max - y_max / 6, 200)
while running:
    buttons = []
    screen.fill((0, 0, 0))
    buttons = CreateMenu(x_max/15, y_max/10, 200, 150, 4, y_max/6, 0, "v", "MenuButton", pg.mouse.get_pos(), ["missions", "options", "techtree", "quit"], ["missions", "options", "techtree", "quit"], buttons)
    if buttons != None:
        pg.draw.rect(screen, (0,0,0), (x_max/3, y_max/8, x_max/2, y_max/1.5))
    if buttons == None:
        buttons = updateMenus(buttons)
    DisplayMenus(buttons, pg.mouse.get_pos())
    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                execButtonAction("main_menu", 0, 0)
                pass
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