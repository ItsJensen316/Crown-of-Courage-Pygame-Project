"""Tile 308: animate only the flame, with a soft unbounded-looking halo."""

import math

import pygame
from game.world.Object import objects


class WallLamp(objects):
    _cache = {}

    def __init__(self, x, y, w, h, img, identity):
        super().__init__(x, y, w, h, img, identity)
        source = img[0]
        cache_key = (w, h, pygame.image.tobytes(source, "RGBA"))
        if cache_key not in self._cache:
            native = pygame.transform.scale(source, (32, 32))
            base = native.copy()
            fire = pygame.Surface((32, 18), pygame.SRCALPHA)
            for px in range(32):
                for py in range(32):
                    color = native.get_at((px, py))
                    # Discard the old image's rectangular, translucent halo.
                    if color.a < 200 or py < 18:
                        base.set_at((px, py), (0, 0, 0, 0))
                    if py < 18 and color.a >= 200 and color.r > 200 and color.g > 80:
                        fire.set_at((px, py), color)
            frames = []
            for shift, height in [
                (-1, 17),
                (0, 18),
                (1, 16),
                (0, 17),
                (-1, 18),
                (1, 17),
            ]:
                frame = base.copy()
                flame = pygame.transform.scale(fire, (32, height))
                # The flame always meets the fixed rim at native row 18.
                frame.blit(flame, (shift, 18 - height))
                frames.append(pygame.transform.scale(frame, (w, h)))
            glows = []
            for strength in range(8):
                glow = pygame.Surface((128, 128))
                for px in range(128):
                    for py in range(128):
                        distance = math.hypot(px - 64, py - 64) / 58
                        power = max(0, 1 - distance * distance) ** 3 * (
                            0.7 + strength * 0.04
                        )
                        glow.set_at(
                            (px, py),
                            (round(70 * power), round(40 * power), round(7 * power)),
                        )
                glows.append(glow)
            self._cache[cache_key] = (frames, glows)
        self.frames, self.glows = self._cache[cache_key]
        self.phase = (x * 7 + y * 11) % 600

    def draw(self, screen):
        tick = pygame.time.get_ticks() + self.phase
        center = (round(self.x + self.width / 2), round(self.y + 14))
        pulse = round((math.sin(tick / 170) + 1) * 3.5)
        glow = self.glows[pulse]
        screen.blit(
            glow, glow.get_rect(center=center), special_flags=pygame.BLEND_RGB_ADD
        )
        screen.blit(
            self.frames[(tick // 95) % len(self.frames)], (round(self.x), round(self.y))
        )
