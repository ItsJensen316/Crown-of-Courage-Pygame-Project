"""Push blocks with slope-aware support and cached, terrain-aligned artwork."""

import math

import pygame
from game.world.Slopes import surface_y


class pushableObject:
    def __init__(self, x, y, w, h, img):
        self.x, self.y, self.width, self.height = x, y, w, h
        self.img = img
        self.gravity = 0.0
        self.speed = 0.0
        self.angle = 0.0
        self._frames = {}
        self._support = None
        self._grab_side = 0
        self._before_step = None

    def draw(self, screen):
        angle = round(self.angle)
        if angle not in self._frames:
            self._frames[angle] = pygame.transform.rotate(self.img[0], angle)
        frame = self._frames[angle]
        center_y = self.y + self.height / 2
        if self._support is not None:
            # Keep the rotated bottom face on the inclined plane. The logical
            # rectangle remains upright for the hero's existing push collision.
            tile = self._support
            direction = getattr(tile, "slope", 0)
            if direction:
                cx = self.x + self.width / 2
                plane = (
                    tile.y + tile.height - (cx - tile.x) * tile.height / tile.width
                    if direction == 1
                    else tile.y + (cx - tile.x) * tile.height / tile.width
                )
                center_y = plane - self.height / (
                    2 * math.cos(math.radians(self.angle))
                )
        screen.blit(
            frame,
            frame.get_rect(center=(round(self.x + self.width / 2), round(center_y))),
        )

    def _surfaces(self, tiles, x):
        for tile in tiles:
            top = surface_y(tile, x + 2, x + self.width - 2)
            if top is not None:
                yield top, tile

    def update(self, tiles, hero):
        held = pygame.key.get_pressed()
        feet = self.y + self.height
        supports = [
            (top, tile)
            for top, tile in self._surfaces(tiles, self.x)
            if abs(feet - top) <= 3
        ]
        grounded = bool(supports) and self.gravity >= 0
        vertical = (
            hero.y + hero.height > self.y + 5 and hero.y < self.y + self.height - 5
        )
        push_right = (
            held[hero.keys["right_move"]]
            and abs(hero.x + hero.width - 17 - self.x) <= 12
        )
        push_left = (
            held[hero.keys["left_move"]]
            and abs(hero.x + 13 - self.x - self.width) <= 12
        )
        shift = held[pygame.K_LSHIFT] or held[pygame.K_RSHIFT]
        jumping = "jump" in hero.keys and held[hero.keys["jump"]]
        touching_left = abs(hero.x + hero.width - 17 - self.x) <= 12
        touching_right = abs(hero.x + 13 - self.x - self.width) <= 12
        owner = getattr(hero, "_grabbed_box", None)
        grabbing = (
            shift
            and not jumping
            and vertical
            and getattr(hero, "current_health", 1) > 0
            and getattr(hero, "gravity", 0) >= 0
            and (touching_left or touching_right)
            and owner in (None, self)
        )
        self._before_step = None
        if grabbing:
            hero._grabbed_box = self
            if owner is not self:
                self._grab_side = 1 if touching_left else -1
            hero.flip = self._grab_side
            direction = int(held[hero.keys["right_move"]]) - int(
                held[hero.keys["left_move"]]
            )
            self.speed = 1.8 * direction
            self._before_step = (self.x, self.y, hero.x)
        else:
            if owner is self:
                hero._grabbed_box = None
            self.speed = (
                (1.8 if push_right else -1.8 if push_left else 0) if vertical else 0
            )
        next_x = self.x + self.speed
        box = pygame.Rect(next_x, self.y + 2, self.width, self.height - 4)
        for tile in tiles:
            if getattr(tile, "one_way", False):
                continue
            if getattr(tile, "slope", 0):
                top = surface_y(tile, next_x + 2, next_x + self.width - 2)
                # Reachable incline is a floor, not a rectangular wall.
                if top is None or feet <= top + abs(self.speed) + 3:
                    continue
            elif grounded and tile.y >= feet - abs(self.speed) - 3:
                continue
            if box.colliderect(pygame.Rect(tile.x, tile.y, tile.width, tile.height)):
                if self.speed > 0:
                    next_x = min(next_x, tile.x - self.width)
                elif self.speed < 0:
                    next_x = max(next_x, tile.x + tile.width)
        self.x = next_x
        if grabbing:
            # Share the actual displacement, including a stop against a wall.
            self.speed = self.x - self._before_step[0]
        self.gravity = min(5, self.gravity + 0.2)
        next_feet = feet + self.gravity
        allowance = abs(self.speed) + 3 if grounded else 2
        surfaces = [
            (top, tile)
            for top, tile in self._surfaces(tiles, self.x)
            if feet <= top + allowance
            and next_feet + (allowance if grounded else 0) >= top
        ]
        self._support = None
        if surfaces:
            highest = min(top for top, _ in surfaces)
            # At a crest the ramp and plateau share a height. Prefer the flat
            # contact immediately, regardless of terrain/map iteration order.
            flat = [
                (top, tile)
                for top, tile in surfaces
                if not getattr(tile, "slope", 0) and top <= highest + 2
            ]
            next_feet, self._support = min(flat or surfaces, key=lambda item: item[0])
            self.gravity = 0
        self.y = next_feet - self.height
        target = 0.0
        if self._support is not None:
            target = math.degrees(
                math.atan2(
                    getattr(self._support, "slope", 0) * self._support.height,
                    self._support.width,
                )
            )
        if self._support is not None and not getattr(self._support, "slope", 0):
            self.angle = 0.0
        else:
            self.angle += max(-6, min(6, target - self.angle))

    def finish_drag(self, hero):
        """Keep contact when terrain stops the hero during a pull."""
        if getattr(hero, "_grabbed_box", None) is not self or self._before_step is None:
            return
        old_x, old_y, hero_x = self._before_step
        hero_dx = hero.x - hero_x
        box_dx = self.x - old_x
        if abs(hero_dx) < abs(box_dx) - 0.001:
            fraction = max(0, min(1, hero_dx / box_dx)) if box_dx else 0
            self.x = old_x + box_dx * fraction
            self.y = old_y + (self.y - old_y) * fraction
        hero.flip = self._grab_side
