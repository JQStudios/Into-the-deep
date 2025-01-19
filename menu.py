import pygame as pg
from classes import screen, x_max, y_max, settings, save_settings
import sys, subprocess
import time


print("menu.py imported")
ImageNormal = pg.image.load("ButtonNormal2.png")
ImageHover = pg.image.load("ButtonHover2.png")
MissionImageNormal = pg.image.load("MissionSelectiontile.png")
MissionImageHover = pg.image.load("MissionSelectiontileHover.png")
BackgroundImg = pg.image.load("MainBackground.png")
if 'MenuDisplayID' not in globals():
    MenuDisplayID = 0
if 'NewMessage' not in globals():
    NewMessage = None

if 'BackgroundZoomX' not in globals():
    BackgroundZoomX = None
if 'BackgroundZoomY' not in globals():
    BackgroundZoomY = None

if 'caller_level1_x' not in globals():
    caller_level1_x = 0
if 'caller_level1_y' not in globals():
    caller_level1_y = 0
if 'caller_level2_x' not in globals():
    caller_level2_x = 0
if 'caller_level2_y' not in globals():
    caller_level2_y = 0
pg.font.init() 
font = pg.font.Font("assets/fonts/Starjedi.ttf", 22)
DescriptionFont = pg.font.Font("assets/fonts/Starjedi.ttf", 12)
color_hover=(175,175,175)
color_normal=(255,255,255)


# Classes

class button(pg.sprite.Sprite):
    def __init__(self, x, y, size_x, size_y, DisplayText, type="MenuButton", action=None):
        super().__init__()
        self.x = x
        self.y = y
        self.size_x = size_x
        self.size_y = size_y
        self.action = action
        self.DisplayText = DisplayText
        self.type = type

    def drawButton(self, x, y,  screen, hover=False):
        if self.type == "MenuButton":
            if hover:
                ScaledImageNormal = pg.transform.scale(ImageNormal, (self.size_x, self.size_y))
                screen.blit(ScaledImageNormal, (x, y))

            else:
                ScaledImageHover = pg.transform.scale(ImageHover, (self.size_x, self.size_y))
                screen.blit(ScaledImageHover, (x, y))


            text_surface = font.render(self.DisplayText, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(x + self.size_x // 2, y + self.size_y // 2 - self.size_y // 20))
            screen.blit(text_surface, text_rect)
        if self.type == "MissionButton":
            if hover:
                ScaledImageNormal = pg.transform.scale(MissionImageNormal, (self.size_x, self.size_y))
                screen.blit(ScaledImageNormal, (x, y))

            else:
                ScaledImageHover = pg.transform.scale(MissionImageHover, (self.size_x, self.size_y))
                screen.blit(ScaledImageHover, (x, y))
            name, description = self.DisplayText.split(":", 1)
            name, description = name.strip(), description.strip()
            text_surface = font.render(name, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(x + self.size_x // 2, y + self.size_y // 2 - self.size_y // 20))
            screen.blit(text_surface, text_rect)
            wrapped_lines = wrap_text(description, DescriptionFont, self.size_x)
            y_offset = 50
            for line in wrapped_lines:
                line_surface = DescriptionFont.render(line, True, (255,255,255))
                screen.blit(line_surface, (50, y_offset))
                y_offset += line_surface.get_height() + 5

class Message:
    def __init__(self, text, screen, color = (0, 0, 0), duration=0.2, speed=50):
        self.text = text
        self.screen = screen
        self.duration = duration
        self.speed = speed
        self.start_time = time.time()
        self.text_surface = font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surface.get_rect(center=(screen.get_width() // 2, -self.text_surface.get_height()))
        self.state = "sliding_in"
        self.background_color = color  # Background color (black)
        self.padding = 10  # Padding around the text

    def ease_out_cubic(self, t):
        return 1 - pow(1 - t, 3)

    def update(self):
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        if self.state == "sliding_in":
            t = elapsed_time / (self.screen.get_height() // 64 / self.speed)
            t = min(max(t, 0), 1)  # Clamp t to the range [0, 1]
            eased_t = self.ease_out_cubic(t)
            self.text_rect.y = int(eased_t * (self.screen.get_height() // 20))
            if self.text_rect.y >= self.screen.get_height() // 20:
                self.text_rect.y = self.screen.get_height() // 20
                self.state = "displaying"
                self.start_time = current_time

        elif self.state == "displaying":
            if elapsed_time >= self.duration:
                self.state = "sliding_out"
                self.start_time = current_time

        elif self.state == "sliding_out":
            t = elapsed_time / (self.screen.get_height() // 12 / self.speed)
            t = min(max(t, 0), 1)  # Clamp t to the range [0, 1]
            eased_t = self.ease_out_cubic(t)
            self.text_rect.y = int(self.screen.get_height() // 20 - eased_t * (self.screen.get_height() // 4))
            if self.text_rect.y <= -self.text_surface.get_height():
                self.state = "done"

        # Draw the background rectangle
        background_rect = pg.Rect(
            self.text_rect.left - self.padding,
            self.text_rect.top - self.padding,
            self.text_rect.width + 2 * self.padding,
            self.text_rect.height + 2 * self.padding
        )
        pg.draw.rect(self.screen, self.background_color, background_rect)

        # Draw the text
        self.screen.blit(self.text_surface, self.text_rect)

    def is_done(self):
        return self.state == "done"



# Main functions
def CreateMenu(x, y, size_x, size_y, button_count, spacing, SelfMenuDisplayID, direction="h", type="MenuButton", mousepos=[0,0], actions=[], DisplayTexts=[], buttons=[]):
    # Background
    global BackgroundZoomX, BackgroundZoomY
    if BackgroundZoomX == None and BackgroundZoomY == None:
        BackgroundZoomX, BackgroundZoomY = calculate_fullscreen_dimensions(BackgroundImg.get_width(), BackgroundImg.get_height(), x_max, y_max)
    #pg.draw.rect(screen, (100, 100, 100), (0,0, x_max, y_max), int(y_max - y_max / 32))
    ScaledBackgroundImg = pg.transform.scale(BackgroundImg, (BackgroundZoomX, BackgroundZoomY))
    screen.blit(ScaledBackgroundImg, (0,0))
    if SelfMenuDisplayID == MenuDisplayID or SelfMenuDisplayID == True:
        
        i = 0
        local_buttons = []
        if direction == "h":
            while i<button_count:
                if len(buttons) == 0:
                    local_buttons.append(button(x+(i*spacing), y, size_x, size_y, DisplayTexts[i], type, actions[i]))
                else:
                    local_buttons = buttons
                i+=1
        if direction == "v":
            while i<button_count:
                if len(buttons) == 0:
                    local_buttons.append(button(x, y+(i*spacing), size_x, size_y, DisplayTexts[i],type, actions[i]))
                else:
                    local_buttons = buttons
                i+=1
        return local_buttons
    
def DisplayMenus(buttons, mousepos=[0,0]):
    if buttons != None:
            for button in buttons:
                if check_button(button, mousepos):
                    button.drawButton(button.x, button.y, screen, False)
                else:
                    button.drawButton(button.x, button.y, screen, True)

def CheckMenu(buttons, mousepos=[0,0]):
    i=0
    for button in buttons:
        if check_button(button, mousepos):
            execButtonAction(button.action, button.x, button.y)
        i+=1

def execButtonAction(action, button_x, button_y):
    global MenuDisplayID, caller_level1_x, caller_level1_y, caller_level2_x, caller_level2_y, NewMessage
    if action=="play":
        print("play")
        subprocess.run(['python', 'dashboard.py'])        
    elif action=="options":
        MenuDisplayID = 1
    elif action=="main_menu":
        MenuDisplayID = 0
    elif action=="quit":
        sys.exit()
    elif action=="display":
        caller_level1_x, caller_level1_y = button_x, button_y
        MenuDisplayID = 4
        if settings["display"]["size"] == "FULLSCREEN":
            NewMessage = display_message(screen, f"the display is currently in fullscreen ({x_max}x{y_max})", (0, 191, 255))
        else:
            Display_Size = [int(num) for num in settings["display"]["size"].split(',')]
            NewMessage = display_message(screen, f"current display size is {Display_Size[0]}x{Display_Size[1]}", (0, 191, 255))
    elif action=="display_size":
        caller_level2_x, caller_level2_y = button_x, button_y
        MenuDisplayID = 5
    elif action=="fullscreen":
        settings["display"]["size"] = "FULLSCREEN"
        save_settings(settings)
        NewMessage = display_message(screen, f"you need to restart your Game to apply the changes made.", (0, 191, 255))

    elif action=="800x600":
        settings["display"]["size"] = "800, 600"
        save_settings(settings)
        NewMessage = display_message(screen, f"you need to restart your Game to apply the changes made.", (0, 191, 255))

    elif action=="1280x720":
        settings["display"]["size"] = "1280, 720"
        save_settings(settings)
        NewMessage = display_message(screen, f"you need to restart your Game to apply the changes made.", (0, 191, 255))

    elif action=="1920x1080":
        settings["display"]["size"] = "1920, 1080"
        save_settings(settings)
        NewMessage = display_message(screen, f"you need to restart your Game to apply the changes made.", (0, 191, 255))

    else:
        NewMessage = display_message(screen, f"error: uknown action: {action}", (200, 0, 0))

def updateMenus(buttons):
    if buttons == None:
        oldlocalbuttons = []
    else:
        oldlocalbuttons = buttons
    localbuttons = []
    if MenuDisplayID > 0 and MenuDisplayID < 6:
        newlocalbuttons = CreateMenu(x_max/15, y_max/10, 200, 150, 4, y_max/6, True, "v", "MenuButton", pg.mouse.get_pos(), ["graphics", "controls", "display", "main_menu"], ["graphics", "controls", "display", "main menu"], oldlocalbuttons)
        for button in newlocalbuttons:
            localbuttons.append(button)
    if MenuDisplayID > 3 and MenuDisplayID < 6:
        newlocalbuttons = CreateMenu(caller_level1_x + x_max/5, caller_level1_y, 200, 150, 2, y_max/6, True, "v", "MenuButton", pg.mouse.get_pos(), ["display_size", "fullscreen"], ["Display Size", "Fullscreen"], oldlocalbuttons)
        for button in newlocalbuttons:
            localbuttons.append(button)
    if MenuDisplayID == 5:
        newlocalbuttons = CreateMenu(caller_level2_x + x_max/5, caller_level2_y, 200, 150, 3, y_max/6, 5, "v", "MenuButton", pg.mouse.get_pos(), ["800x600", "1280x720", "1920x1080"], ["800x600", "1280x720", "1920x1080"], oldlocalbuttons)
        for button in newlocalbuttons:
            localbuttons.append(button)
    return localbuttons

# Message functions
def display_message(screen, text, color = (0, 0, 0), duration=2, speed=5):
    message = Message(text, screen, color, duration, speed)
    return message
def get_message():
    return NewMessage
# Support Functions

def centered(size_x):
    return x_max/2-size_x/2

def calculate_fullscreen_dimensions(image_width, image_height, screen_width, screen_height):
    image_aspect = image_width / image_height
    screen_aspect = screen_width / screen_height

    if image_aspect > screen_aspect:
        scale_factor = screen_height / image_height
    else:
        scale_factor = screen_width / image_width

    new_width = int(image_width * scale_factor)
    new_height = int(image_height * scale_factor)
    
    return new_width, new_height


def check_button(button, pos):
    if (button.x <= pos[0] <= button.x +button.size_x) and \
        (button.y <= pos[1] <= button.y+button.size_y):
        return True
    
def button_dynamic_size(original_width, original_height, y, size_x=None):
    aspect_ratio = original_width / original_height
    size_y = int(size_x * aspect_ratio)
    newsize_x = int(size_x * aspect_ratio)

    while size_y + y > y_max:
        size_y = int(size_x * aspect_ratio)
        newsize_x = int(size_x * aspect_ratio)
        aspect_ratio -= 0.05
    print(f"dinamicly changed button size to {aspect_ratio}, new dimensionens are {newsize_x}x{size_y}")
    return newsize_x, size_y

def wrap_text(text, font, max_width):
    words = text.split(' ')  # Split text into words
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        # Render the current line to check its width
        line_surface = font.render(' '.join(current_line), True, text_color)
        if line_surface.get_width() > max_width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]

    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))

    return lines