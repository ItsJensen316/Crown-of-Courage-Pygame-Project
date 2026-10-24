"""Journal illustrations composed from the game's own pixel-art assets."""

from functools import lru_cache

import pygame
from game.ui.MenuUI import actor, backdrop, bitmap


def tile(canvas, path, pos, size=40):
    canvas.blit(pygame.transform.scale(bitmap(path), (size, size)), pos)


@lru_cache(maxsize=4)
def illustration(page):
    canvas = pygame.transform.scale(backdrop(page == 3), (720, 310)).copy()
    forest = "assets/art/Level1/1-1/"
    tower = "assets/art/Level1/1-2/"
    ground = tower + "tile_30.png" if page == 3 else forest + "Tile_12.png"
    for x in range(0, 720, 40):
        tile(canvas, ground, (x, 270))
    hero = "assets/art/Player/Idle/Idle_0.png"
    if page == 1:
        actor(canvas, hero, (330, 270), 150)
        actor(canvas, "assets/art/Enemies/Hyena/Idle/Idle_0.png", (610, 270), 80, True)
    elif page == 2:
        # Reassemble the original hut, including its roof, on a 40px grid.
        for n in range(300, 320):
            tile(
                canvas,
                forest + f"Extras/Tile_{n}.png",
                (430 + (n - 300) % 4 * 40, 70 + (n - 300) // 4 * 40),
            )
        actor(canvas, hero, (270, 270), 130)
        actor(canvas, "assets/art/Old_man/Idle/Idle_0.png", (390, 270), 125, True)
        actor(canvas, "assets/art/Scenery/Well.png", (640, 270), 100)
    elif page == 3:
        for x in range(0, 720, 40):
            tile(canvas, tower + "tile_50.png", (x, 0))
        for y in range(40, 270, 40):
            tile(canvas, tower + "tile_50.png", (0, y))
            tile(canvas, tower + "tile_50.png", (680, y))
        # The keeper's real chamber landmark: a raised brick mound with ramps.
        for n, x, y in [
            (59, 120, 230),
            (59, 160, 190),
            (30, 200, 190),
            (60, 240, 190),
            (60, 280, 230),
            (64, 160, 230),
            (50, 200, 230),
            (65, 240, 230),
        ]:
            tile(canvas, tower + f"tile_{n}.png", (x, y))
        actor(canvas, "assets/art/Player/Attack/Attack_1.png", (210, 190), 135)
        actor(
            canvas,
            "assets/art/Enemies/Orc_Shaman/Attack/Attack_1.png",
            (480, 270),
            185,
            True,
        )
    else:
        # Tower doorway and original open lift, with forest beyond it.
        for y in range(0, 270, 40):
            for x in range(0, 240, 40):
                tile(canvas, tower + "tile_50.png", (x, y))
        pygame.draw.rect(canvas, (19, 24, 31), (80, 110, 100, 160))
        for n in range(152, 158):
            tile(
                canvas,
                tower + f"Extras/tile_{n}.png",
                (90 + (n - 152) % 2 * 40, 150 + (n - 152) // 2 * 40),
            )
        for y in range(0, 150, 12):
            pygame.draw.ellipse(canvas, (155, 159, 161), (126, y, 8, 17), 2)
        actor(canvas, hero, (340, 270), 140)
    return canvas
