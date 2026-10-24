"""Stationary story NPC; only the shared camera changes its screen position."""

import time
from pathlib import Path

import pygame


class oldMan:
    def __init__(self, x, y, w, h, img):
        self.x, self.y = x, y
        self.x_copy, self.y_copy = x, y
        self.width, self.height = w, h
        self.img_coll = img
        self._left_frames = [pygame.transform.flip(frame, True, False) for frame in img]
        self.facing_left = False
        self.index = 0
        self.action = "Idle"
        self._animation_time = time.perf_counter()
        self._frame_seconds = 0.20

    @classmethod
    def from_assets(cls, x, ground_y, scale=2.5):
        # Pad the differently cropped originals onto identical canvases before
        # scaling. Nearest-neighbour sampling keeps hard pixel-art edges.
        paths = sorted(
            Path("assets/art/Old_man/Idle").glob("Idle_*.png"),
            key=lambda path: int(path.stem.rsplit("_", 1)[1]),
        )
        originals = [pygame.image.load(str(path)).convert_alpha() for path in paths]
        width = max(frame.get_width() for frame in originals)
        height = max(frame.get_height() for frame in originals)
        size = (round(width * scale), round(height * scale))
        frames = []
        for frame in originals:
            canvas = pygame.Surface((width, height), pygame.SRCALPHA)
            canvas.blit(frame, frame.get_rect(midbottom=(width // 2, height)))
            frames.append(pygame.transform.scale(canvas, size))
        return cls(x, ground_y - size[1], size[0], size[1], frames)

    def update(self, hero):
        # Camera.follow already translates this NPC with the world. There is
        # no gravity, wandering, combat, or independent scrolling here.
        self.facing_left = hero.x + hero.width / 2 < self.x + self.width / 2
        now = time.perf_counter()
        elapsed = now - self._animation_time
        if elapsed >= self._frame_seconds:
            steps = int(elapsed / self._frame_seconds)
            self.index = (self.index + steps) % len(self.img_coll)
            self._animation_time += steps * self._frame_seconds

    def draw(self, screen):
        frames = self._left_frames if self.facing_left else self.img_coll
        screen.blit(frames[self.index], (round(self.x), round(self.y)))

    def can_talk(self, hero):
        distance = abs((self.x + self.width / 2) - (hero.x + hero.width / 2))
        feet_distance = abs(self.y + self.height - hero.y - hero.height)
        return distance <= 110 and feet_distance <= 12 and bool(hero.down)


def place_old_man(level):
    """Anchor one guide to the existing hut, leaving the CSV untouched."""
    if level.level_path != "Level1/1-1":
        return
    hut = [
        (column * 45, row * 45)
        for row, cells in enumerate(level.tiles_arr)
        for column, value in enumerate(cells)
        if 300 <= int(value) <= 319
    ]
    if not hut:
        return
    left = min(x for x, y in hut)
    ground_y = max(y for x, y in hut) + 45
    npc = oldMan.from_assets(left - 60, ground_y)
    level.Old_man[:] = [npc]
    # Preserve the nearby encounter but put its spawn outside the guide's
    # clearing. It remains a hostile enemy, never a dialogue character.
    for entry in level.Enemy:
        if left - 400 < entry["x"] < left + 250:
            entry["x"] = left - 540
            entry["y"] = ground_y - entry["dimension"][1]
