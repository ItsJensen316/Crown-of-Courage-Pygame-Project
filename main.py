import pygame
from helper import *
from settings import *
#from Level1_1 import *
from Level1_12 import *
from Story import *
from Levels import *
import json

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# Initialize Pygame
pygame.init()
# Constants for screen dimensions

pygame.display.set_caption("Game Home Page")
# Font for button text
font = pygame.font.Font(None, 36)
# //helpful function 
key_map = {
    "a": pygame.K_a, "b": pygame.K_b, "c": pygame.K_c, "d": pygame.K_d, "e": pygame.K_e, "f": pygame.K_f, "g": pygame.K_g,
    "h": pygame.K_h, "i": pygame.K_i, "j": pygame.K_j, "k": pygame.K_k, "l": pygame.K_l, "m": pygame.K_m, "n": pygame.K_n,
    "o": pygame.K_o, "p": pygame.K_p, "q": pygame.K_q, "r": pygame.K_r, "s": pygame.K_s, "t": pygame.K_t, "u": pygame.K_u,
    "v": pygame.K_v, "w": pygame.K_w, "x": pygame.K_x, "y": pygame.K_y, "z": pygame.K_z,
    "[0]": pygame.K_0, "[1]": pygame.K_1, "[2]": pygame.K_2, "[3]": pygame.K_3, "[4]": pygame.K_4, "[5]": pygame.K_5, "[6]": pygame.K_6,
    "[7]": pygame.K_7, "[8]": pygame.K_8, "[9]": pygame.K_9,
    "space": pygame.K_SPACE, "return": pygame.K_RETURN,
    "tab": pygame.K_TAB,
    "left shift": pygame.K_LSHIFT, "right shift": pygame.K_RSHIFT, "left ctrl": pygame.K_LCTRL, "right ctrl": pygame.K_RCTRL,
    "left alt": pygame.K_LALT, "right alt": pygame.K_RALT,
    "up": pygame.K_UP, "down": pygame.K_DOWN, "left": pygame.K_LEFT, "right": pygame.K_RIGHT,
    "caps lock": pygame.K_CAPSLOCK
}
def readFile(fname):
        with open(fname, "r") as json_file:
             fileInfo= json.load(json_file)
        return fileInfo

# home_page
def home_page():
    # Load images
    background_image =set_image('./home_img/homeBg.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
    play_text=set_image('./home_img/playText.png',(100,50))
    game_start_image = set_image("./home_img/play.png" ,(400, 100)) 
    settings_image = set_image('./home_img/setting.png', (100, 50))
    story_image = set_image("./home_img/book.png", (100, 50))
    level_image = set_image("./home_img/level.png", (100, 50))
    #home components
    play_btn_pos=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2 +50)
    play_text_pos=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2 +55)
    level_img_pos=(400,500)
    setting_img_pos=(250,500)
    story_img_pos=(550,500)
    # start engine
    while True:
        keys=readFile("control_key.json")
        settings=readFile("setting.json")
        for index, (action, key) in enumerate(keys.items()):
            keys[action]=key_map[keys[action]]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()

                if Rect(game_start_image,play_btn_pos).collidepoint(mouse_pos):
                    level2(keys,settings)
                    # Handle game start button click
                    print("Game Started!")
                elif Rect(settings_image,setting_img_pos).collidepoint(mouse_pos):
                    # Handle settings button click
                    print("Settings Clicked!")
                    setting()
                elif Rect(story_image,story_img_pos).collidepoint(mouse_pos):
                    # Handle story button click
                    print("Story Clicked!")
                    StoryBook()
                elif Rect(level_image,level_img_pos).collidepoint(mouse_pos):
                    # Handle level button click
                    print("Level Clicked!")
                    Levels()
                    
        
        # Blit background image
        screen.blit(background_image, (0, 0))
        screen.blit(game_start_image,Rect(game_start_image,play_btn_pos))
        hover( [
            (play_text,play_text_pos),
            (settings_image, setting_img_pos),
            (story_image, story_img_pos),
            (level_image, level_img_pos)
        ])
        pygame.display.flip()

# setting_page
  


# Main game loop
while True:
    home_page()
