import pygame as pg
from classes import screen, x_max, y_max, settings, save_settings, LoadData
from mission import PlayMission
from credits import play_video
import sys, subprocess
import time
from techtree import *
import random
import ast
import math


ButtonSound = pg.mixer.Sound("menu-button-88360.mp3")
MessageSound = pg.mixer.Sound("button-124476.mp3")

def dashboard():
    pg.init()
    pg.font.init()
    font = pg.font.Font("assets/fonts/Starjedi.ttf", 22)
    MessageSound = pg.mixer.Sound("button-124476.mp3")


    pg.display.set_caption("Dashboard")
    buttons = []
    running = True
    message = None
    size_x, size_y = button_dynamic_size(100, 100, y_max - y_max / 6, 200)
    FT = True
    OldMessage = None
    while running:
        settings = load_settings()
        sounds = settings["sounds"]["active"]
        buttons = []
        screen.fill((0, 0, 0))
        buttons = CreateMenu(x_max / 15, y_max / 10, 200, 150, 4, y_max / 6, 0, "v", "MenuButton", pg.mouse.get_pos(),
                             ["missions", "options", "techtree", "quit"], ["missions", "options", "techtree", "quit"],
                             buttons)
        if buttons != None:
            pg.draw.rect(screen, (0, 0, 0), (x_max / 3, y_max / 8, x_max / 2, y_max / 1.5))
        if buttons == None:
            buttons = updateMenus(buttons)
        DisplayMenus(buttons, pg.mouse.get_pos())
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
            if event.type == pg.MOUSEBUTTONDOWN:
                mousepos = pg.mouse.get_pos()
                CheckMenu(buttons, mousepos)

# Level Bar
        LevelBar(x_max/4, y_max/50, x_max/2, y_max/15, screen)
# Balance  
        ShowBalance(x_max, y_max / 50, screen)
# Message
        message = get_message()

        if message:
            if FT:
                if sounds:
                    pg.mixer.Sound.play(MessageSound)
            FT = False
            if not message == None:
                message.update()
            if message.is_done() or not message == OldMessage and not OldMessage == None:
                FT = True # First time called
                message = None
                get_message(RESET=True)
            OldMessage = message
        pg.display.update()
        pg.display.update()

print(f"{TimeStamp()} menu.py imported")
ImageNormal = pg.image.load("ButtonNormal2.png")
ImageHover = pg.image.load("ButtonHover2.png")
MissionImageNormal = pg.image.load("MissionSelectiontile.png")
MissionImageHover = pg.image.load("MissionSelectiontileHover.png")
BackgroundImg = pg.image.load("MainBackground.png")
CoinImg = pg.image.load("coins-solid.png")
CoingImgWhite = pg.image.load("coins-solid-white.png")
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
if 'Missions' not in globals():
    Missions = []
pg.font.init() 
font = pg.font.Font("assets/fonts/Starjedi.ttf", 22)
BigFont = pg.font.Font("assets/fonts/Starjedi.ttf", 33)
DescriptionFont = pg.font.Font("assets/fonts/Starjedi.ttf", 12)
color_hover=(175,175,175)
color_normal=(255,255,255)
GlobalCoinAnimation = 1

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
# Title
            ND = self.DisplayText.split(";", 1)
            name, description = ND[0].strip(), ND[1].strip()
            text_surface = font.render(name, True, (0, 0, 0))
            text_rect = text_surface.get_rect(topleft=(x+self.size_x/8,y + self.size_y/7))
            screen.blit(text_surface, text_rect)
# Descrition
            wrapped_lines = wrap_text(description, DescriptionFont, self.size_x/1.3, (0,0,0))
            y_offset = y + self.size_y // 3.3
            for line in wrapped_lines:
                line_surface = DescriptionFont.render(line, True, (0, 0, 0))
                line_rect = line_surface.get_rect(topleft=(x+x/2.4, y_offset))
                screen.blit(line_surface, line_rect)
                y_offset += line_surface.get_height()/1.7

class Message:
    def __init__(self, text, screen, color = (0, 0, 0), duration=0.2, speed=50):
        self.text = text
        self.screen = screen
        self.duration = duration
        self.speed = speed
        self.start_time = time()
        self.text_surface = font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surface.get_rect(center=(screen.get_width() // 2, -self.text_surface.get_height()))
        self.state = "sliding_in"
        self.background_color = color  # Background color (black)
        self.padding = 10  # Padding around the text

    def ease_out_cubic(self, t):
        return 1 - pow(1 - t, 3)

    def update(self):
        current_time = time()
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
                if CheckButton(button.x, button.y, button.size_x, button.size_y, mousepos):
                    button.drawButton(button.x, button.y, screen, False)
                else:
                    button.drawButton(button.x, button.y, screen, True)

def CheckMenu(buttons, mousepos=[0,0]):
    i=0
    for button in buttons:
        if CheckButton(button.x, button.y, button.size_x, button.size_y, mousepos):
            execButtonAction(button.action, button.x, button.y)
        i+=1

def execButtonAction(action, button_x, button_y):
    global MenuDisplayID, caller_level1_x, caller_level1_y, caller_level2_x, caller_level2_y, NewMessage, Missions
    MissionSplit = action.split(";", 1)
    settings = load_settings()
    if settings["sounds"]["active"]:
        pg.mixer.Sound.play(ButtonSound)
    if action == "techtree":
        treeing()
    if action=="play":
        dashboard()
    elif action == "missions":
        Missions = SelectMissions()
        MenuDisplayID=10
    elif action=="options":
        MenuDisplayID = 1
    elif action=="credits":
        play_video("CreditsAnimation.mp4", x_max, y_max, "Credits")
    elif action=="main_menu":
        MenuDisplayID = 0
    elif action=="quit":
        sys.exit()
    elif action == "controls":
        caller_level1_x, caller_level1_y = button_x, button_y
        MenuDisplayID = 8
        NewMessage = display_message(screen, f"Controls are currently set to {settings["controls"]["ControlMethod"].lower()}")
    elif action=="sounds":
        caller_level1_x, caller_level1_y = button_x, button_y
        MenuDisplayID = 2
        if settings["sounds"]["active"] == True:
            NewMessage = display_message(screen, f"Sounds is currently on", (0, 191, 255))
        else:
            NewMessage = display_message(screen, f"Sounds is currently off", (0, 191, 255))
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
    elif action=="SoundsOn":
        settings["sounds"]["active"] = True
        save_settings(settings)
    elif action=="SoundsOff":
        settings["sounds"]["active"] = False
        save_settings(settings)
    elif action == "AUTO" or action == "XBOX" or action == "KEYBOARD":
        settings["controls"]["ControlMethod"] = action
        save_settings(settings)
    elif MissionSplit[0] == "StartMission":
        Mission = Mission = ast.literal_eval(MissionSplit[1].strip())
        data = LoadData()
        print(f"{TimeStamp()} Starting Mission")
        PlayMission(data["Selection"], None, Mission['BC'], Mission['MT'], Mission["RW"])
        print(f"{TimeStamp()} Mission Finished")
    else:
        NewMessage = display_message(screen, f"error: uknown action: {action}", (200, 0, 0))

def updateMenus(buttons):
    if buttons == None:
        oldlocalbuttons = []
    else:
        oldlocalbuttons = buttons
    localbuttons = []
    if MenuDisplayID > 0 and MenuDisplayID < 10:
        newlocalbuttons = CreateMenu(x_max/15, y_max/10, 200, 150, 4, y_max/6, True, "v", "MenuButton", pg.mouse.get_pos(), ["controls", "sounds", "display", "main_menu"], ["controls", "sounds", "display", "main menu"], oldlocalbuttons)
        for button in newlocalbuttons:
            localbuttons.append(button)
    if MenuDisplayID == 8:
        newlocalbuttons = CreateMenu(caller_level1_x + x_max/5, caller_level1_y, 200, 150, 3, y_max/6, True, "v", "MenuButton", pg.mouse.get_pos(), ["AUTO", "XBOX", "KEYBOARD"], ["auto", "controller(x-box)", "keyboard + mouse"], oldlocalbuttons)
        for button in newlocalbuttons:
            localbuttons.append(button)
    if MenuDisplayID == 2:
        newlocalbuttons = CreateMenu(caller_level1_x + x_max/5, caller_level1_y, 200, 150, 2, y_max/6, True, "v", "MenuButton", pg.mouse.get_pos(), ["SoundsOn", "SoundsOff"], ["on", "off"], oldlocalbuttons)
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
    if MenuDisplayID == 10:
        newlocalbuttons = CreateMenu(x_max/15, y_max/20, 300, 225, 3, y_max/4, 10, "v", "MissionButton", pg.mouse.get_pos(), [f"StartMission; {Missions[0]}", f"StartMission; {Missions[1]}", f"StartMission; {Missions[2]}"], [f"{Missions[0]['MT']}; {Missions[0]['MD']}", f"{Missions[1]['MT']}; {Missions[1]['MD']}", f"{Missions[2]['MT']}; {Missions[2]['MD']}"], oldlocalbuttons)
        for button in newlocalbuttons:
            localbuttons.append(button)
    return localbuttons

# Message functions
def display_message(screen, text, color = (0, 0, 0), duration=2, speed=5):
    message = Message(text, screen, color, duration, speed)
    return message
def get_message(RESET=False):
    global NewMessage
    if RESET:
        NewMessage = None
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



def CheckButton(x, y, size_x, size_y, pos):
    if (x <= pos[0] <= x +size_x) and \
        (y <= pos[1] <= y+size_y):
        return True
    

def button_dynamic_size(original_width, original_height, y, size_x=None):
    aspect_ratio = original_width / original_height
    size_y = int(size_x * aspect_ratio)
    newsize_x = int(size_x * aspect_ratio)

    while size_y + y > y_max:
        size_y = int(size_x * aspect_ratio)
        newsize_x = int(size_x * aspect_ratio)
        aspect_ratio -= 0.05
    print(f"{TimeStamp()} dinamicly changed button size to {aspect_ratio}, new dimensionens are {newsize_x}x{size_y}")
    return newsize_x, size_y

def wrap_text(text, font, max_width, text_color):
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

# Select Missions
def SelectMissions():
# MissionType = MT, MissionDescription = MD, BotCount = BC, Difficulty = DC, Reward = RW
    MissionTypes=["destroy", "free for all", "defend"]
    MissionDescriptions=["destroy every enemy target given by an operator.", "be the last one to survive in an every body against every body situation",
                         "prevent bots from reaching the bottom of the screen"]
    i = 0
    Missions = []
    while i < 3:
        RandomMission=random.randint(0, (len(MissionTypes)-1))
        Missions.append(
            {
                "MT": MissionTypes[RandomMission],
                "MD": MissionDescriptions[RandomMission],
                "BC": 10,
                "DC": 100,
                "RW": 800
            }
        )
        i += 1
    return Missions

# Level System

def LevelBar(x,y, size_x, size_y, screen):
    level = GetLevel()
    BaseLevel = math.floor(level)
    NextLevel = BaseLevel+1
    # Base Level Text
    pg.draw.rect(screen, (135, 145, 153), (x - x_max / 25, y, (x - (x - (x_max / 50)))*2, size_y))
    show_text(str(BaseLevel), (0, 0, 0), x - x_max / 50 , y + size_y/2, 50, 0, False, False, 255, None)
    # Next Level Text
    pg.draw.rect(screen, (135, 145, 153), (x + size_x, y, (x - (x - (x_max / 50)))*2, size_y))
    show_text(str(NextLevel), (0, 0, 0), x + size_x + x_max / 50 , y + size_y/2, 50, 0, False, False, 255, None)
    pg.draw.rect(screen, (44, 117, 255), (x, y, size_x * (level % 1), size_y))
    # Hollow Level Bar
    i = 1
    while i <= 10:
        pg.draw.rect(screen, (255, 255, 255), (x + (i-1) * (size_x/10), y, size_x/10, size_y), int(x_max/600))
        i += 1


# Balance system
def ShowBalance(x, y, screen, color=(0,0,0)):
    global GlobalCoinAnimation
    Balance = LoadData()["Balance"]
    if color == (255,255,255):
        ScaledCoinsImg = pg.transform.scale(CoingImgWhite, (50,50))
    else:
        ScaledCoinsImg = pg.transform.scale(CoinImg, (50,50))
    text_size_x, text_size_y = show_text(str(Balance), (color), x * GlobalCoinAnimation, y, 50, 1, False, False, 0)
    if CheckButton(x - ScaledCoinsImg.get_width(), y, ScaledCoinsImg.get_width(), ScaledCoinsImg.get_height(), pg.mouse.get_pos()):
        screen.blit(ScaledCoinsImg, ((x * GlobalCoinAnimation) - ScaledCoinsImg.get_width() - 10, y))
        text_size_x, text_size_y = show_text(str(Balance), (color), x * GlobalCoinAnimation, y + text_size_y / 1.5, 50, 1)
        if GlobalCoinAnimation >= (x_max-text_size_x)/x_max:
            GlobalCoinAnimation -= 0.002
    else:
        screen.blit(ScaledCoinsImg, ((x * GlobalCoinAnimation) - ScaledCoinsImg.get_width() - 10, y))
        text_size_x, text_size_y = show_text(str(Balance), (color), x * GlobalCoinAnimation, y + text_size_y / 1.5, 50, 1)
        if GlobalCoinAnimation < 1:
            GlobalCoinAnimation += 0.002
