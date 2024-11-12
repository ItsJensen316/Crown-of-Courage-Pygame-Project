import pygame
import os
import sys, csv
import json
from Object import *
from Slidable import *
from Pushable import *
from Level_manager import *
from Old_man import *

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
tiles_dimension = (45, 45)
enemy_size = (60, 90)
screen_scroll_speed = 5
current_check_point = (0, 0)
### Initializing Game Objects ###
Level = Level_manager()


By_product = {
    "Boar": 116,
    "Hyena": 117,
    "Deceased": 120,
    "Mummy": 120,
    "Orc_Berserk": 120,
    "Orc_Shaman": 120,
    "Orc_Warrior": 120,
}
Enemy_identity = {
    451: "Boar",
    452: "Deceased",
    453: "Hyena",
    454: "Mummy",
    455: "Orc_Berserk",
    456: "Orc_Shaman",
    457: "Orc_Warrior",
    458: "Old_man",
    459: "",
    460: "",
}

identity = {
    111: "Mushroom",
    112: "Mushroom",
    113: "Mushroom",
    114: "Mushroom",
    115: "Mushroom",
    116: "Meat",
    117: "Meat",
    118: "Meat",
    120: "Kit",
}

root_path = "J:/Pygame Project/"


### Getting all meta data of the levels ###
def readFile(fname):
    with open(fname, "r") as json_file:
        fileInfo = json.load(json_file)
    return fileInfo


def writeFile(sourceFile, originalFile):
    with open(originalFile, "w") as json_file:
        json.dump(sourceFile, json_file, indent=2)


def get_level_props(props):
    path = ""
    for key, value in props.items():
        path += key
        for key1, value1 in props[key].items():
            if value1["current"]:
                path += "/" + key1
                return path


Level.level_metadata = readFile("level.json")
Level.current_level = readFile("current_level.json")
Level.level_path = get_level_props(Level.current_level)
Level.map = Level.level_metadata[Level.level_path]["map"]
Level.bg_data = Level.level_metadata[Level.level_path]["background"]
speed_arr = [1, 0.2]
Level.bgx = []
Level.bgy = []
Level.x_limit[0] = Level.level_metadata[Level.level_path]["level_size"]["left"]
Level.x_limit[1] = Level.level_metadata[Level.level_path]["level_size"]["right"]
Level.y_limit[0] = Level.level_metadata[Level.level_path]["level_size"]["top"]
Level.y_limit[1] = Level.level_metadata[Level.level_path]["level_size"]["down"]



def switch_level():
    # print(level_path)
    path_sequence = Level.level_path.split("/")
    Level.current_level[path_sequence[0]][path_sequence[1]]["played"] = True
    Level.current_level[path_sequence[0]][path_sequence[1]]["current"] = False
    Level.level_path = Level.current_level[path_sequence[0]][path_sequence[1]]["next"]
    path_sequence = Level.level_path.split("/")
    Level.current_level[path_sequence[0]][path_sequence[1]]["current"] = True
    writeFile(Level.current_level, "current_level.json")
    Level.reset()
    Level.level_metadata = readFile("level.json")
    Level.current_level = readFile("current_level.json")
    Level.level_path = get_level_props(Level.current_level)
    Level.map = Level.level_metadata[Level.level_path]["map"]
    Level.bg_data = Level.level_metadata[Level.level_path]["background"]
    Level.bg_images = load_backgrounds("Assets/Backgrounds")
    loadimages1(f"Assets/{Level.level_path}")
    # reload()


def loadimages(path, tiles_dimension):
    img = pygame.image.load(path)
    img = pygame.transform.scale(img, tiles_dimension)
    return img


death_screen = loadimages("Assets/Death_screen.png", (800, 600))


### Find all the files in a path ###
def find_file(path):
    directory_path = root_path + path
    files = [
        f
        for f in os.listdir(directory_path)
        if os.path.isfile(os.path.join(directory_path, f))
    ]
    return files


### Loading all backgrounds in a level ###
performance = True


def load_backgrounds(path):
    bg_coll = []
    image_names = find_file(f"{path}/{Level.level_path}")
    for image in image_names:
        bg = (
            pygame.transform.scale(
                pygame.image.load(f"{path}/{Level.level_path}/{image}"), Level.bg_data[image]
            ).convert()
            if performance
            else pygame.transform.scale(
                pygame.image.load(f"{path}/{Level.level_path}/{image}"), Level.bg_data[image]
            )
        )
        bg_coll.append(bg)
        Level.bgx.append(0)
        Level.bgy.append(0)
    return bg_coll


Level.bg_images = load_backgrounds("Assets/Backgrounds")


# New scroll function (To be implemented)
def scroll(hero, obj, isbackground):
    if hero.screen_scroll_X:
        obj.x -= hero.char_speed * obj.speed[0] if isbackground else hero.char_speed
    if hero.screen_scroll_Y:
        obj.y -= hero.gravity * obj.speed[1] if isbackground else hero.gravity


### Appending all game objects with their properties into an array ###
def load(index, range_i, array, img, dim):
    try:
        a = identity[index]
    except:
        a = ""
    if img:
        if 90 < index <= 100:
            array.append(
                slideBlock(
                    dim[0] * tiles_dimension[0],
                    dim[1] * tiles_dimension[1],
                    tiles_dimension[0],
                    tiles_dimension[1],
                    img,
                )
            )
        elif 210 < index <= 220:
            ##            print(index)
            array.append(
                pushableObject(
                    dim[0] * tiles_dimension[0],
                    dim[1] * tiles_dimension[1],
                    45,
                    45,
                    img,
                )
            )
        elif 500 < index <= 510:
            array.append(
                oldMan(
                    dim[0] * tiles_dimension[0],
                    dim[1] * tiles_dimension[1],
                    
                    60,
                    90,
                    img,
                
                )
            )

        elif range_i[0] <= index <= range_i[1]:
            array.append(
                objects(
                    dim[0] * tiles_dimension[0],
                    dim[1] * tiles_dimension[1],
                    tiles_dimension[0],
                    tiles_dimension[1],
                    img,
                    a,
                )
            )
        return array
    else:
       
        if range_i[0] <= index <= range_i[1]:
            array.append(
                {
                    "x": dim[0] * tiles_dimension[0],
                    "y": dim[1] * tiles_dimension[1],
                    "path": f"Assets/Enemies/{Enemy_identity[index]}",
                    "identity": Enemy_identity[index],
                    "dimension": (150, 150) if index == 456 else (90, 90),
                }
            )

        return array


### Find the number of files in a path ###
def find_file_length(path):
    directory_path = root_path + path
    files = [
        f
        for f in os.listdir(directory_path)
        if os.path.isfile(os.path.join(directory_path, f))
    ]
    return len(files)


### Iterating throughout the csv file and loading all objects with their properties ###
def loadimages1(path):
    print(Level.map)
    with open(Level.map) as file:
        data = csv.reader(file)
        for all in data:
            Level.tiles_arr.append(all)
    for i in range(len(Level.tiles_arr)):
        for j in range(len(Level.tiles_arr[0])):
            img = []

            try:
                index = int(Level.tiles_arr[i][j])
                if 0 < index <= 90:
                    img.append(loadimages(f"{path}/Tile_{index}.png", tiles_dimension))
                    load(index, (0, 90), Level.tiles, img, (j, i))
                elif 90 < index <= 100:
                    img.append(loadimages(f"{path}/Tile_{index}.png", tiles_dimension))
                    load(index, (91, 100), Level.Slidables, img, (j, i))
                elif 100 < index <= 450:
                    try:
                        img.append(
                            loadimages(
                                f"{path}/Extras/Tile_{index}.png", tiles_dimension
                            )
                        )
                    except:
                        for k in range(
                            find_file_length(
                                f"{path}/Extras/Tile_{index}"
                            )
                        ):
                            img.append(
                                loadimages(
                                    f"{path}/Extras/Tile_{index}/{k+1}.png",
                                    tiles_dimension,
                                )
                            )

                    if 210 < index <= 220:
                        load(index, (211, 220), Level.Pushables, img, (j, i))
                    else:
                        load(index, (101, 110), Level.Ladder, img, (j, i))
                        load(index, (111, 130), Level.Food, img, (j, i))
                        load(index, (131, 140), Level.Door, img, (j, i))
                        load(index, (141, 170), Level.Lift, img, (j, i))
                        load(index, (171, 180), Level.Boxes, img, (j, i))
                        load(index, (181, 200), Level.Inventory, img, (j, i))
                        load(index, (201, 210), Level.Damage, img, (j, i))
                        load(index, (300, 440), Level.Rest, img, (j, i))
                        load(index, (441, 445), Level.CheckP, img, (j, i))
                        load(index, (446, 450), Level.Puzzle, img, (j, i))
                elif 500<index <= 510:
                    print("inside")
                    for k in range(find_file_length(f"Assets/Old_man/Idle")):
                        # print(k)
                        img.append(loadimages(f"Assets/Old_man/Idle/Idle_{k}.png",(60,90)))
                    print("Old man", Level.Old_man)       
                    load(index, (501,510), Level.Old_man, img, (j, i)) 
                    print("Old man", Level.Old_man)     
                elif index == 0:
                    Level.hero_pos = (j, i)

                else:
                    load(index, (451, 460), Level.Enemy, "", (j, i))
            except:
                img.append(pygame.image.load("Assets/Empty.png"))

    Level.tiles_arr[0][0] = "-1"
        


##hero_pos_initial,tiles_arr_initial,tiles_initial,ladder_initial,food_initial,door_initial,lift_initial,boxes_initial,inventory_initial,others_initial,Enmy_initial=loadimages1('Assets/Level1/1-1')
loadimages1(f"Assets/{Level.level_path}")


### Loading all the animation images ###
def loadimages2(path, Action, img_size):
    img_coll = []
    len = find_file_length(f"{path}/{Action}")
    for i in range(len):
        img = pygame.transform.scale(
            pygame.image.load(f"{path}/{Action}/{Action}_{i}.png"), img_size
        )
        img_coll.append(img)
    return img_coll


### Hover Effect in settings(on rectangles) ###
def hover(array_of_setof_button_in_rect_form_with_pos):
    mouse_pos = pygame.mouse.get_pos()
    for img, position in array_of_setof_button_in_rect_form_with_pos:
        rect = img.get_rect(center=position)
        if rect.collidepoint(mouse_pos):
            # Adjust button's position and size for hover effect
            hovered_rect = pygame.Rect(
                rect.left - 10,  # Move slightly left
                rect.top - 10,  # Move upwards
                rect.width + 15,  # Increase width
                rect.height + 15,  # Increase height
            )
            hovered_image = pygame.transform.scale(
                img, (hovered_rect.width, hovered_rect.height)
            )
            screen.blit(hovered_image, hovered_rect)
        else:
            # Draw button without hover effect
            screen.blit(img, rect)


def draw_rect(color, dimension):
    pygame.draw.rect(screen, color, dimension)


def Rect(img, pos):
    rect = img.get_rect(center=pos)
    return rect


def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)


def blur_image(surface, radius):
    # Create a blurred copy of the surface using the average blur algorithm
    blurred_surface = pygame.transform.smoothscale(
        surface, (surface.get_width() // radius, surface.get_height() // radius)
    )
    blurred_surface = pygame.transform.smoothscale(
        blurred_surface, (surface.get_width(), surface.get_height())
    )
    return blurred_surface


def set_image(img, img_size):
    Image = pygame.image.load(img)
    Image = pygame.transform.scale(Image, img_size) if img_size else Image
    return Image


### Loading the entire text from a file ###
def load_conversation(file_name):
    msg = []
    with open(file_name) as file:
        for line in file:
            msg.append(line)
    return msg
