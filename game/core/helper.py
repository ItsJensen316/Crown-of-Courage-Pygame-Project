"""Shared display, scene loading, and cached animation assets."""

import csv
import json
import os
from functools import lru_cache

import pygame
from game.world.BreakableCrate import BreakableCrate
from game.world.Button_switch import Button
from game.core.DisplayMode import initialize
from game.items.ItemSprites import TILE_ITEMS, Collectible
from game.core.Level_manager import Level_manager
from game.world.Lift import lift
from game.world.Object import objects
from game.world.Scenery import Scenery, SCENERY_IDS
from game.actors.Old_man import oldMan, place_old_man
from game.world.Pushable import pushableObject
from game.world.Slidable import slideBlock
from game.world.TowerLock import TowerLock
from game.world.WallLamp import WallLamp

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = initialize()
tiles_dimension = (45, 45)

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
    119: "Kit",
    121: "Apple",
    120: "Kit",
}

root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + os.sep
os.chdir(root_path)


def readFile(fname):
    with open(fname, "r") as json_file:
        fileInfo = json.load(json_file)
    return fileInfo


def loadimages(path, tiles_dimension):
    # Original folders mix Tile_ and tile_ spellings; resolve just the final
    # component so the project also runs on case-sensitive filesystems.
    if not os.path.isfile(path):
        parent, name = os.path.split(path)
        matches = [
            entry for entry in os.listdir(parent) if entry.lower() == name.lower()
        ]
        if matches:
            path = os.path.join(parent, matches[0])
    img = pygame.image.load(path)
    img = pygame.transform.scale(img, tiles_dimension)
    return img


def load_backgrounds(path):
    bg_coll = []
    image_names = [
        name
        for name in Level.bg_data
        if os.path.isfile(f"{path}/{Level.level_path}/{name}")
    ]
    for image in image_names:
        width, height = Level.bg_data[image]
        # The first area's camera can move 30px vertically. Extend the art
        # to the playable ground bottom so that movement never exposes a gap.
        if Level.level_path == "Level1/1-1":
            height = max(height, 630)
        source = pygame.image.load(f"{path}/{Level.level_path}/{image}")
        # Keep alpha only on layers that actually contain transparent pixels.
        opaque = (
            source.get_masks()[3] == 0
            or pygame.mask.from_surface(source, 254).count()
            == source.get_width() * source.get_height()
        )
        if source.get_size() != (width, height):
            source = pygame.transform.scale(source, (width, height))
        bg = source.convert() if opaque else source.convert_alpha()
        bg_coll.append(bg)
        Level.bgx.append(0)
        Level.bgy.append(0)
    return bg_coll


def load(index, range_i, array, img, dim):
    a = identity.get(index, "")
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

            array.append(
                pushableObject(
                    dim[0] * tiles_dimension[0],
                    dim[1] * tiles_dimension[1],
                    tiles_dimension[0],
                    tiles_dimension[1],
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

        elif 140 < index <= 170:
            if 152 <= index <= 157:

                array.append(
                    lift(
                        dim[0] * tiles_dimension[0],
                        dim[1] * tiles_dimension[1],
                        tiles_dimension[0],
                        tiles_dimension[1],
                        [img[0]],
                        index,
                    )
                )
                array.append(
                    lift(
                        dim[0] * tiles_dimension[0],
                        dim[1] * tiles_dimension[1],
                        tiles_dimension[0],
                        tiles_dimension[1],
                        [img[1]],
                        index - 6,
                    )
                )
            else:
                array.append(
                    lift(
                        dim[0] * tiles_dimension[0],
                        dim[1] * tiles_dimension[1],
                        tiles_dimension[0],
                        tiles_dimension[1],
                        img,
                        index,
                    )
                )

        elif 460 < index <= 465:
            button_class = (
                TowerLock
                if index == 461 and Level.level_path == "Level1/1-1"
                else Button
            )
            array.append(
                button_class(
                    dim[0] * tiles_dimension[0],
                    dim[1] * tiles_dimension[1],
                    tiles_dimension[0],
                    tiles_dimension[1],
                    img,
                )
            )

        elif range_i[0] <= index <= range_i[1]:
            object_class = (
                WallLamp
                if index == 308 and Level.level_path == "Level1/1-2"
                else objects
            )
            array.append(
                object_class(
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
                    "path": f"assets/art/Enemies/{Enemy_identity[index]}",
                    "identity": Enemy_identity[index],
                    "dimension": (150, 150) if index == 456 else (90, 90),
                }
            )

        return array


def find_file_length(path):
    directory_path = root_path + path
    if not os.path.isdir(directory_path):
        parent, name = os.path.split(directory_path)
        matches = [
            entry for entry in os.listdir(parent) if entry.lower() == name.lower()
        ]
        if matches:
            directory_path = os.path.join(parent, matches[0])
    files = [
        f
        for f in os.listdir(directory_path)
        if os.path.isfile(os.path.join(directory_path, f))
    ]
    return len(files)


def loadimages1(path):
    with open(Level.map, encoding="utf-8-sig") as file:
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
                    Level.tiles[-1].tile_id = index
                    slope_tiles = (
                        {47: 1, 48: -1}
                        if Level.level_path == "Level1/1-1"
                        else {59: 1, 60: -1, 61: 1, 62: -1}
                    )
                    Level.tiles[-1].slope = slope_tiles.get(index, 0)
                    Level.tiles[-1].one_way = (
                        Level.level_path == "Level1/1-2" and index in (7, 61, 62, 63)
                    )
                elif 90 < index <= 100:
                    img.append(loadimages(f"{path}/Tile_{index}.png", tiles_dimension))
                    load(index, (91, 100), Level.Slidables, img, (j, i))
                elif index in TILE_ITEMS:
                    Level.Food.append(Collectible(j * 45, i * 45, index))
                elif index in (173, 174, 181, 182, 183, 184):
                    # Both phases share the original tower special-item artwork.
                    art = f"assets/art/Level1/1-2/Extras/tile_{index}.png"
                    group = Level.Boxes if index in (173, 174) else Level.Inventory
                    pickup = objects(
                        j * 45, i * 45, 45, 45, [loadimages(art, tiles_dimension)], ""
                    )
                    pickup.tile_id = index
                    group.append(pickup)
                elif Level.level_path == "Level1/1-1" and index in SCENERY_IDS:
                    Level.Rest.append(Scenery(j * 45, i * 45,
                                              f"{path}/Extras/Tile_{index}.png"))
                elif 100 < index <= 450:
                    try:

                        if 152 <= index <= 157:
                            img.append(
                                loadimages(
                                    f"{path}/Extras/Tile_{index}.png", tiles_dimension
                                )
                            )
                            img.append(
                                loadimages(
                                    f"{path}/Extras/Tile_{index-6}.png", tiles_dimension
                                )
                            )
                        else:
                            img.append(
                                loadimages(
                                    f"{path}/Extras/Tile_{index}.png", tiles_dimension
                                )
                            )
                    except (FileNotFoundError, pygame.error):
                        for k in range(find_file_length(f"{path}/Extras/Tile_{index}")):
                            img.append(
                                loadimages(
                                    f"{path}/Extras/Tile_{index}/{k+1}.png",
                                    tiles_dimension,
                                )
                            )

                    if 140 < index <= 170:
                        load(index, (141, 170), Level.Lift, img, (j, i))
                    elif 210 < index <= 220:
                        load(index, (211, 220), Level.Pushables, img, (j, i))

                    else:
                        load(index, (101, 110), Level.Ladder, img, (j, i))
                        load(index, (111, 130), Level.Food, img, (j, i))
                        load(index, (131, 140), Level.Door, img, (j, i))
                        if index in (172, 175):
                            Level.Boxes.append(
                                BreakableCrate(
                                    j * 45, i * 45, 45, 45, img, index, Level.Food
                                )
                            )
                        else:
                            load(index, (171, 180), Level.Boxes, img, (j, i))
                        load(index, (181, 200), Level.Inventory, img, (j, i))
                        load(index, (201, 210), Level.Damage, img, (j, i))
                        if 201 <= index <= 210:
                            Level.Damage[-1].tile_id = index
                        load(index, (300, 440), Level.Rest, img, (j, i))
                        load(index, (441, 445), Level.CheckP, img, (j, i))
                        load(index, (446, 450), Level.Puzzle, img, (j, i))
                elif 460 < index <= 465:
                    img.append(
                        loadimages(f"{path}/Extras/Tile_{index}.png", tiles_dimension)
                    )
                    load(index, (461, 465), Level.Button, img, (j, i))
                elif 500 < index <= 510:
                    if Level.level_path == "Level1/1-1":
                        continue  # The story guide is anchored to the hut below.
                    for k in range(find_file_length("assets/art/Old_man/Idle")):

                        img.append(
                            loadimages(f"assets/art/Old_man/Idle/Idle_{k}.png", (60, 90))
                        )
                    load(index, (501, 510), Level.Old_man, img, (j, i))
                elif index == 0:
                    Level.hero_pos = (j, i)

                else:
                    load(index, (451, 460), Level.Enemy, "", (j, i))
            except Exception as exc:
                raise RuntimeError(
                    f"Cannot load tile {index} at column {j}, row {i} in {Level.map}"
                ) from exc

    for decoration in Level.Rest:
        if isinstance(decoration, Scenery):
            decoration.place_on_ground(Level.tiles)

    place_old_man(Level)


@lru_cache(maxsize=256)
def loadimages2(path, Action, img_size):
    img_coll = []
    len = find_file_length(f"{path}/{Action}")
    for i in range(len):
        img = pygame.transform.scale(
            pygame.image.load(f"{path}/{Action}/{Action}_{i}.png"), img_size
        )
        img_coll.append(img)
    return img_coll


def start_level(level_path="Level1/1-1", backgrounds=True):
    """Rebuild the world for a fresh play session, retaining the shared Level object."""
    Level.reset()
    Level.level_metadata = readFile("data/config/level.json")
    Level.level_path = level_path
    props = Level.level_metadata[level_path]
    Level.map = props["map"]
    Level.bg_data = props["background"]
    Level.x_limit = [props["level_size"]["left"], props["level_size"]["right"]]
    Level.y_limit = [props["level_size"]["top"], props["level_size"]["down"]]
    Level.bg_images = load_backgrounds("assets/art/Backgrounds") if backgrounds else []
    loadimages1(f"assets/art/{level_path}")
