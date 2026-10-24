"""Forest tile 461 is a glowing puzzle lock, not a tower pressure switch."""

import math

import pygame


class TowerLock:
    is_tower_lock = True
    _halos = None

    def __init__(self, x, y, w, h, img):
        self.x, self.y, self.width, self.height = x, y, w, h
        self.img_coll = img
        self.pressed = False
        self.unlocked = False
        if TowerLock._halos is None:
            TowerLock._halos = []
            for strength in range(8):
                halo = pygame.Surface((100, 100))
                for px in range(100):
                    for py in range(100):
                        radius = math.hypot(px - 50, py - 50) / 46
                        power = max(0, 1 - radius * radius) ** 3 * (
                            0.65 + strength * 0.07
                        )
                        halo.set_at(
                            (px, py),
                            (round(90 * power), round(58 * power), round(12 * power)),
                        )
                TowerLock._halos.append(halo)

    def update(self, hero):
        pass  # Camera translates this marker once per frame.

    def draw(self, screen):
        if self.unlocked:
            return
        now = pygame.time.get_ticks() / 1000
        center = (round(self.x + self.width / 2), round(self.y + self.height / 2))
        pulse = round((math.sin(now * 3) + 1) * 3.5)
        halo = self._halos[pulse]
        screen.blit(
            halo, halo.get_rect(center=center), special_flags=pygame.BLEND_RGB_ADD
        )
        screen.blit(
            self.img_coll[0], (round(self.x), round(self.y + math.sin(now * 2) * 1.5))
        )
        for i in range(3):
            angle = now * 0.8 + i * math.tau / 3
            x = round(center[0] + math.cos(angle) * 25)
            y = round(center[1] + math.sin(angle) * 24)
            pygame.draw.line(screen, (255, 224, 125), (x - 2, y), (x + 2, y))
            pygame.draw.line(screen, (255, 224, 125), (x, y - 2), (x, y + 2))
