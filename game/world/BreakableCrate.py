"""Wooden crates break into their own sprite fragments and roll loot once."""

import random

import pygame
from game.items.ItemSprites import Collectible
from game.world.Object import objects


class BreakableCrate(objects):
    DROP_CHANCE = 0.28
    BREAK_FRAMES = 42

    def __init__(self, x, y, w, h, img, tile_id, food):
        super().__init__(x, y, w, h, img, "")
        self.tile_id = tile_id
        self.food = food
        self.broken = False
        self.finished = False
        self.age = 0
        self.fragments = []

    def update(self, hero):
        if self.broken:
            self.age += 1
            self.finished = self.age >= self.BREAK_FRAMES
            return
        if getattr(hero, "current_health", 0) <= 0:
            return
        attack = getattr(hero, "action", "")
        strike = (attack == "Attack" and hero.index == 4) or (
            attack == "Dash_Attack" and hero.index in (1, 2)
        )
        if not strike:
            return
        center = hero.x + hero.width / 2
        reach = pygame.Rect(
            round(center if hero.flip == 1 else center - 65),
            round(hero.y + 12),
            65,
            hero.height - 17,
        )
        if reach.colliderect(pygame.Rect(self.x, self.y, self.width, self.height)):
            self.break_open(hero)

    def break_open(self, hero):
        if self.broken:
            return
        self.broken = True
        source = self.img_coll[0]
        for row in range(2):
            for column in range(3):
                left = column * source.get_width() // 3
                top = row * source.get_height() // 2
                right = (column + 1) * source.get_width() // 3
                bottom = (row + 1) * source.get_height() // 2
                fragment = source.subsurface(
                    (left, top, right - left, bottom - top)
                ).copy()
                self.fragments.append(
                    (
                        fragment,
                        left,
                        top,
                        (column - 1) * 1.1 + hero.flip * 0.35,
                        -1.5 - row * 0.4,
                        random.uniform(-6, 6),
                    )
                )
        hero.sounds["sword"].play()
        if random.random() < self.DROP_CHANCE:
            kind = random.choice(("mushroom", "ration", "apple"))
            tile = (
                random.choice((111, 112, 113, 114, 115))
                if kind == "mushroom"
                else 117 if kind == "ration" else 121
            )
            self.food.append(Collectible(self.x, self.y + self.height - 45, tile))

    def draw(self, screen):
        if not self.broken:
            screen.blit(self.img_coll[0], (round(self.x), round(self.y)))
            return
        if self.finished:
            return
        for image, x, y, vx, vy, spin in self.fragments:
            frame = pygame.transform.rotate(image, spin * self.age)
            frame.set_alpha(round(255 * (1 - self.age / self.BREAK_FRAMES)))
            center = (
                round(self.x + x + image.get_width() / 2 + vx * self.age),
                round(
                    self.y
                    + y
                    + image.get_height() / 2
                    + vy * self.age
                    + 0.045 * self.age**2
                ),
            )
            screen.blit(frame, frame.get_rect(center=center))
