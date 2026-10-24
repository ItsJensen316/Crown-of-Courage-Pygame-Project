"""Sprite-based menus using the game's own forest, tower and character art."""

import csv
import math
from functools import lru_cache
from pathlib import Path

import pygame

GOLD = (226, 194, 123)
TEXT = (231, 234, 222)
MUTED = (155, 177, 168)
PANEL = (19, 33, 34)


@lru_cache(maxsize=32)
def text_font(size):
    return pygame.font.Font(None, size)


def label(screen, text, pos, size=24, color=TEXT, center=False):
    font = text_font(size)
    rendered = font.render(text, True, color)
    screen.blit(rendered, rendered.get_rect(center=pos) if center else pos)


@lru_cache(maxsize=160)
def bitmap(path):
    p = Path(path)
    if not p.exists():
        p = next(f for f in p.parent.iterdir() if f.name.lower() == p.name.lower())
    return pygame.image.load(str(p)).convert_alpha()


@lru_cache(maxsize=16)
def backdrop(tower=False):
    canvas = pygame.Surface((800, 600))
    canvas.fill((43, 48, 73) if tower else (28, 49, 45))
    files = (
        ["assets/art/Backgrounds/Level1/1-2/L12B1.png"]
        if tower
        else [
            "assets/art/Backgrounds/Level1/1-1/L11B1.png",
            "assets/art/Backgrounds/Level1/1-1/L11B2.png",
        ]
    )
    for path in files:
        art = bitmap(path)
        crop = art.subsurface(
            (0, 0, min(800, art.get_width()), min(600, art.get_height()))
        )
        canvas.blit(pygame.transform.scale(crop, (800, 600)), (0, 0))
    return canvas


@lru_cache(maxsize=40)
def sprite(path, height, flip=False):
    art = bitmap(path)
    art = art.subsurface(art.get_bounding_rect())
    art = pygame.transform.scale(
        art, (max(1, round(art.get_width() * height / art.get_height())), height)
    )
    return pygame.transform.flip(art, flip, False)


def actor(screen, path, foot, height, flip=False):
    art = sprite(path, height, flip)
    screen.blit(art, art.get_rect(midbottom=foot))


@lru_cache(maxsize=1)
def home_art():
    s = backdrop().copy()
    veil = pygame.Surface((800, 600), pygame.SRCALPHA)
    for y in range(600):
        pygame.draw.line(
            veil, (6, 16, 20, min(245, 80 + max(0, y - 220) // 2)), (0, y), (800, y)
        )
    s.blit(veil, (0, 0))
    for x, h, name, flip in [
        (100, 116, "Boar", False),
        (245, 145, "Orc_Berserk", False),
        (555, 145, "Orc_Shaman", True),
        (700, 125, "Hyena", True),
    ]:
        pygame.draw.ellipse(s, (12, 23, 23), (x - 55, 299, 110, 16))
        actor(s, f"assets/art/Enemies/{name}/Idle/Idle_0.png", (x, 305), h, flip)
    pygame.draw.ellipse(s, (12, 23, 23), (350, 294, 100, 19))
    actor(s, "assets/art/Player/Idle/Idle_0.png", (400, 303), 180)
    return s


def button(screen, rect, text, active=False, primary=False):
    pygame.draw.rect(screen, (8, 17, 21), rect.move(0, 4), border_radius=10)
    pygame.draw.rect(
        screen,
        (72, 67, 44) if active else (32, 47, 44) if primary else PANEL,
        rect,
        border_radius=10,
    )
    pygame.draw.rect(
        screen, GOLD if active or primary else (75, 99, 87), rect, 2, border_radius=10
    )
    label(
        screen, text, rect.center, 34 if primary else 24, GOLD if active else TEXT, True
    )


def icon(screen, kind, center):
    x, y = center
    color = GOLD
    if kind == "settings":
        pygame.draw.circle(screen, color, (x, y), 13, 3)
        pygame.draw.circle(screen, color, (x, y), 4, 2)
        for i in range(8):
            a = i * math.pi / 4
            pygame.draw.line(
                screen,
                color,
                (x + int(13 * math.cos(a)), y + int(13 * math.sin(a))),
                (x + int(19 * math.cos(a)), y + int(19 * math.sin(a))),
                3,
            )
    elif kind == "levels":
        for i in range(3):
            pygame.draw.rect(
                screen,
                color,
                (x - 20 + i * 15, y + 10 - i * 10, 12, 6),
                border_radius=1,
            )
        pygame.draw.line(screen, color, (x + 16, y - 15), (x + 16, y - 30), 2)
        pygame.draw.polygon(
            screen, color, [(x + 17, y - 30), (x + 29, y - 25), (x + 17, y - 21)]
        )
    else:
        pygame.draw.rect(screen, color, (x - 23, y - 14, 46, 31), 2, border_radius=3)
        pygame.draw.line(screen, color, (x, y - 13), (x, y + 16), 2)
        for off in [-8, 0, 8]:
            pygame.draw.line(screen, color, (x - 17, y + off), (x - 5, y + off), 1)
            pygame.draw.line(screen, color, (x + 5, y + off), (x + 17, y + off), 1)


def header(screen, title, subtitle=""):
    screen.blit(backdrop(), (0, 0))
    shade = pygame.Surface((800, 600), pygame.SRCALPHA)
    shade.fill((8, 18, 22, 225))
    screen.blit(shade, (0, 0))
    label(screen, title, (400, 43), 40, GOLD, True)
    if subtitle:
        label(screen, subtitle, (400, 82), 21, MUTED, True)
    back = pygame.Rect(28, 24, 100, 38)
    button(screen, back, "< Back", back.collidepoint(pygame.mouse.get_pos()))
    return back


@lru_cache(maxsize=2)
def thumbnail(tower=False):
    s = backdrop(tower).copy()
    level = "1-2" if tower else "1-1"
    root = Path("assets/art/Level1") / level
    with open(
        "data/maps/Level12.csv" if tower else "data/maps/Level11.csv", encoding="utf-8-sig"
    ) as source:
        rows = list(csv.reader(source))
    ox, oy = (28 * 45, 0) if tower else (150 * 45, 130)
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            n = int(v)
            x, y = c * 45 - ox, r * 45 - oy
            if x < -45 or x > 800 or y < -45 or y > 600:
                continue
            if 1 <= n <= 90:
                folder = root
                name = f"Tile_{n}.png"
            elif 101 <= n <= 110 or 201 <= n <= 210 or 300 <= n <= 440:
                folder = root / "Extras"
                name = f"Tile_{n}.png"
            else:
                continue
            try:
                art = bitmap(str(folder / name))
            except (StopIteration, FileNotFoundError):
                frames = sorted((folder / f"Tile_{n}").glob("*.png"))
                if not frames:
                    continue
                art = bitmap(str(frames[0]))
            s.blit(pygame.transform.scale(art, (45, 45)), (x, y))
    if tower:
        # A clearly framed stone platform and fire, using the tower tileset.
        for i in range(18):
            s.blit(
                pygame.transform.scale(bitmap(str(root / "tile_30.png")), (45, 45)),
                (i * 45, 470),
            )
        actor(s, "assets/art/Player/Idle/Idle_0.png", (380, 470), 105)
        actor(s, "assets/art/Enemies/Mummy/Idle/Idle_0.png", (620, 470), 105, True)
    else:
        actor(s, "assets/art/Player/Idle/Idle_0.png", (275, 410), 105)
        actor(s, "assets/art/Enemies/Orc_Berserk/Idle/Idle_0.png", (610, 410), 105, True)
    return pygame.transform.scale(s, (324, 242))
