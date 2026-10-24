"""16px collectible art, shared by world pickups and inventory.

Pixels are defined here so the art remains editable alongside the game code.
Nearest-neighbour scaling, a shared outline/palette, and stable pickup hitboxes
keep the sprites consistent with the forest's pixel art.
"""

import math
import time
from functools import lru_cache

import pygame
from game.world.Object import objects

PALETTE = {
    ".": (0, 0, 0, 0),
    "o": "#302b2d",
    "s": "#594039",
    "b": "#936043",
    "r": "#b95143",
    "R": "#d67a58",
    "h": "#ecc28a",
    "c": "#e1d2ac",
    "w": "#f5e7bf",
    "g": "#547447",
    "G": "#91a05c",
    "a": "#bc873e",
    "A": "#ddaa55",
    "v": "#708f91",
    "V": "#b3c4b3",
}

PATTERNS = {
    "mushroom": (
        "................",
        "................",
        ".....oooooo.....",
        "....orrwRrro....",
        "...orrRRrrwro...",
        "..orwrrrRRrrro..",
        "..orrRRrwrrrro..",
        ".osssrrrrrrrsso.",
        "..ooooocccoooo..",
        "......owcco.....",
        "......owcco.....",
        ".....owccco.....",
        ".....occchco....",
        ".....osssso.....",
        "......oooo......",
        "................",
    ),
    "cluster": (
        "................",
        "....ooooo.......",
        "...orRwRro......",
        "..orrRrrrro.....",
        "..ossssssso.....",
        "...oowcooo......",
        "....owco.oooo...",
        "....occoorrRro..",
        ".ooooocoosssso..",
        "orRrroccoocco...",
        "ossssooccoocco..",
        ".ooccooccccco...",
        "..occoocccco....",
        "...oossssso.....",
        ".....ooooo......",
        "................",
    ),
    "morel": (
        "................",
        ".......oo.......",
        "......oaao......",
        ".....oabAao.....",
        ".....obasbo.....",
        "....oabasAao....",
        "....oAbababo....",
        "....obasabAo....",
        "....oabAbabo....",
        ".....oabAao.....",
        "......occo......",
        "......owco......",
        ".....owccco.....",
        ".....osssso.....",
        "......oooo......",
        "................",
    ),
    "apple": (
        "................",
        "........oooo....",
        ".......oGGgo....",
        "......obooo.....",
        "......obo.......",
        "...ooooooooo....",
        "..orRRrrorRro...",
        ".orRwrRrrrRRrro.",
        ".orRrrRRrrrrrro.",
        ".orRRrrrrrrrsro.",
        "..orrrrrrrrsro..",
        "..orrrrrrrssro..",
        "...orrssssso....",
        "....ossssoo.....",
        ".....oooo.......",
        "................",
    ),
    "meat": (
        "................",
        "................",
        ".....oooooo.....",
        "...oohhhhRroo...",
        "..ohRRrrRRrrho..",
        ".ohRrssrrrRRrho.",
        ".oRrrscRrrssrho.",
        ".ohRrsccRrrRrho.",
        ".osrRrrRRrrrhso.",
        ".osshRRrrRhhso..",
        "..osshhhhhhsso..",
        "...osssssssso...",
        "....ooooooo.....",
        "................",
        "................",
        "................",
    ),
    "drumstick": (
        "................",
        ".....oooo.......",
        "...ooARRroo.....",
        "..oARhRRRrro....",
        "..oARRRrrrrro...",
        "..oARrrrRrsso...",
        "...orrrrssso....",
        "....ossssoo.....",
        ".....oooco......",
        ".......owco.....",
        "........owco....",
        ".......oowcco...",
        ".......owccwo...",
        "........oooo....",
        "................",
        "................",
    ),
    "rations": (
        "................",
        "................",
        ".....oooooo.....",
        "...ooAhAAaao....",
        "..oAhAAbAaaao...",
        ".oAAaAAbAaaaso..",
        ".oAaAbbbAAasso..",
        ".oAaaAAbAasso...",
        "..oaaAAbassso...",
        "...oaaaassso....",
        "....ossssso.....",
        ".....ooooo......",
        "................",
        "................",
        "................",
        "................",
    ),
    "potion": (
        "................",
        "......oooo......",
        ".....obAhbo.....",
        ".....osbbso.....",
        "......oVVo......",
        "......oVVo......",
        ".....oVwVVo.....",
        "....oVwrrVVo....",
        "...oVwRrrrVVo...",
        "...oVwRrrrVVo...",
        "...oVrRrrrsVo...",
        "...oVrrrrssVo...",
        "....oVrrssVo....",
        ".....oVVVVo.....",
        "......oooo......",
        "................",
    ),
}

TILE_ITEMS = {
    111: ("Mushroom", "mushroom", "red"),
    112: ("Mushroom", "cluster", "gold"),
    113: ("Mushroom", "mushroom", "brown"),
    114: ("Mushroom", "morel", "gold"),
    115: ("Mushroom", "cluster", "red"),
    116: ("Meat", "meat", "red"),
    117: ("Rations", "rations", "gold"),
    118: ("Meat", "drumstick", "red"),
    119: ("Kit", "potion", "red"),
    120: ("Kit", "potion", "red"),
    121: ("Apple", "apple", "red"),
}
INVENTORY_TILES = {
    "Mushroom": 111,
    "Meat": 116,
    "Apple": 121,
    "Kit": 120,
    "Rations": 117,
}
DISPLAY_NAMES = {
    "Rations": "rations",
    "Mushroom": "mushroom",
    "Meat": "food",
    "Apple": "apple",
    "Kit": "healing potion",
}


@lru_cache(maxsize=32)
def item_icon(tile_id, size=32):
    _, pattern_name, variant = TILE_ITEMS[tile_id]
    colors = dict(PALETTE)
    if variant == "gold":
        colors.update(r="#b3813d", R="#d2a454")
    elif variant == "brown":
        colors.update(r="#8c5942", R="#b57d50")
    canvas = pygame.Surface((16, 16), pygame.SRCALPHA)
    pattern = PATTERNS[pattern_name]
    for y, row in enumerate(pattern):
        if len(row) > 16:
            raise ValueError(f"Item pattern too wide: {pattern_name}, row {y}")
        for x, token in enumerate(row):
            if token != ".":
                canvas.set_at((x, y), pygame.Color(colors[token]))
    return pygame.transform.scale(canvas, (size, size))


class Collectible(objects):
    """Decorative motion changes the drawing only, never the pickup hitbox."""

    ICON_SIZE = 32
    BOB_HEIGHT = 1.5
    BOB_PERIOD = 2.6

    def __init__(self, x, y, tile_id):
        identity = TILE_ITEMS[tile_id][0]
        super().__init__(x, y, 45, 45, [item_icon(tile_id, self.ICON_SIZE)], identity)
        self.tile_id = tile_id
        self._phase = (x * 0.013 + y * 0.017) % math.tau
        self._elapsed = 0.0
        self._last_time = time.perf_counter()
        self._shadow = pygame.Surface((26, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(self._shadow, (27, 31, 25, 85), (0, 1, 26, 6))

    def update(self, hero):
        now = time.perf_counter()
        self._elapsed += min(0.05, max(0.0, now - self._last_time))
        self._last_time = now
        # The shared Camera already moves x/y; don't scroll a second time.

    def draw(self, screen):
        icon = self.img_coll[0]
        bob = (
            math.sin(self._elapsed * math.tau / self.BOB_PERIOD + self._phase)
            * self.BOB_HEIGHT
        )
        center_x = round(self.x + self.width / 2)
        bottom = round(self.y + self.height - 5 - bob)
        screen.blit(
            self._shadow,
            self._shadow.get_rect(
                midbottom=(center_x, round(self.y + self.height - 1))
            ),
        )
        screen.blit(icon, icon.get_rect(midbottom=(center_x, bottom)))
        # One subdued glint signals a pickup without neon halos.
        if math.sin(self._elapsed * 1.6 + self._phase) > 0.88:
            px, py = center_x + 13, bottom - 26
            pygame.draw.line(screen, (221, 195, 125), (px - 2, py), (px + 2, py))
            pygame.draw.line(screen, (221, 195, 125), (px, py - 2), (px, py + 2))


@lru_cache(maxsize=8)
def key_icon(size=32):
    """Gold key in the collectible palette."""
    rows = [
        "................",
        "................",
        "...ooooo........",
        "..oAAAAAo.......",
        "..oAh.hAo.......",
        "..oAh.hAo.......",
        "..oAAAAAo.......",
        "...ooAoo........",
        ".....Ao.........",
        ".....Ao.........",
        ".....AAAAo......",
        ".....AAooo......",
        ".....AAAAo......",
        ".....ooooo......",
        "................",
        "................",
    ]
    colors = {"o": "#302b2d", "A": "#edb83c", "h": "#fff0a0"}
    canvas = pygame.Surface((16, 16), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, c in enumerate(row):
            if c in colors:
                canvas.set_at((x, y), pygame.Color(colors[c]))
    return pygame.transform.scale(canvas, (size, size))
