"""Bounded camera shared by terrain, actors, and background layers.

Existing physics uses screen-space positions. The camera translates every world
object by the same delta once per frame, so collision code can remain unchanged.
Background positions are derived from the absolute camera position, never used
as world bounds.
"""

import math
import os
import time

import pygame


class Camera:
    # BACKGROUND SPEED SETTINGS: draw back-to-front, by image filename.
    # 0.0 = fixed scenery; 1.0 = terrain speed. Smaller = farther away.
    # x_speed controls horizontal parallax; y_speed controls vertical parallax.
    BACKGROUND_LAYERS = {
        "L11B1.png": {"x_speed": 0.08, "y_speed": 0.06},  # distant forest / sky
        "L11B2.png": {"x_speed": 0.22, "y_speed": 0.16},  # nearby trees
        "L12B1.png": {"x_speed": 0.12, "y_speed": 0.08},  # second phase
    }
    DEFAULT_BACKGROUND = {"x_speed": 0.12, "y_speed": 0.08}
    # Vertical camera: ordinary jumps remain inside this screen-space band.
    VERTICAL_TOP = 110
    VERTICAL_BOTTOM = 450
    VERTICAL_RESPONSE = 10.0  # smaller = softer tracking; larger = quicker

    GROUPS = (
        "tiles",
        "Slidables",
        "Rest",
        "CheckP",
        "Ladder",
        "Button",
        "Pushables",
        "Damage",
        "Food",
        "Lift",
        "Puzzle",
        "Old_man",
        "Door",
        "Boxes",
        "Inventory",
        "Danger",
        "Floor",
        "Enemies_array",
    )

    def __init__(self, level, viewport=(800, 600)):
        self.width, self.height = viewport
        self.x = self.y = 0.0
        self.locked_position = None
        self._follow_time = None
        self._vertical_target = None
        # Match helper.load_backgrounds' metadata order and missing-file filter.
        self._background_names = [
            name
            for name in level.bg_data
            if os.path.isfile(f"assets/art/Backgrounds/{level.level_path}/{name}")
        ]
        rows = level.tiles_arr
        world_width = max(map(len, rows)) * 45
        world_height = len(rows) * 45
        # Level 1's final continuous ground row ends at y=630. The empty
        # editor rows below it must not become visible camera space.
        bottom = 630 if level.level_path == "Level1/1-1" else world_height
        self.bounds = pygame.Rect(0, 0, world_width, bottom)
        # Bake static collision terrain at exact tile-grid coordinates.
        # One rounded render origin prevents floating-point tile-edge seams.
        self._terrain = pygame.Surface((world_width, world_height), pygame.SRCALPHA)
        for tile in level.tiles:
            self._terrain.blit(tile.img_coll[0], (round(tile.x), round(tile.y)))
        self.max_x = max(0, self.bounds.right - self.width)
        self.max_y = max(0, self.bounds.bottom - self.height)
        self.goal_rect = None
        self.goal_solved = False
        self.goal_was_touching = False
        if level.level_path == "Level1/1-1":
            # Tiles 345..365 make up the original tower. Use their actual
            # positions rather than a trigger near column 28 in the old map.
            tower = [
                (column * 45, row * 45)
                for row, cells in enumerate(rows)
                for column, value in enumerate(cells)
                if 345 <= int(value) <= 365
            ]
            if tower:
                left = min(x for x, y in tower)
                right = max(x for x, y in tower) + 45
                entrance_bottom = max(y for x, y in tower) + 45
                self.goal_rect = pygame.Rect(
                    left, entrance_bottom - 90, right - left, 90
                )
                # Show the entire tower and stop at the map's right edge.
                self.max_x = max(0, right - self.width)

    def objects(self, level):
        seen = set()
        for name in self.GROUPS:
            for obj in getattr(level, name, ()):
                if id(obj) not in seen:
                    seen.add(id(obj))
                    yield obj

    def follow(self, hero, level, dt=None):
        world_x, world_y = hero.x + self.x, hero.y + self.y
        now = time.perf_counter()
        if self.locked_position is not None:
            new_x = min(self.max_x, max(0, self.locked_position[0]))
            new_y = min(self.max_y, max(0, self.locked_position[1]))
            self._vertical_target = new_y
        else:
            new_x = min(self.max_x, max(0, world_x - 350))
            now = time.perf_counter()
            if self._vertical_target is None:
                # Place the camera before the first frame, without easing in from
                # outside the level. Subsequent movement is always smoothed.
                self._vertical_target = min(
                    self.max_y, max(0, world_y + hero.height - self.VERTICAL_BOTTOM)
                )
                new_y = self._vertical_target
            else:
                # A dead zone avoids following every jump or landing correction.
                # Track the target, not the lagging camera, to avoid feedback drift.
                if world_y < self._vertical_target + self.VERTICAL_TOP:
                    self._vertical_target = world_y - self.VERTICAL_TOP
                elif (
                    world_y + hero.height > self._vertical_target + self.VERTICAL_BOTTOM
                ):
                    self._vertical_target = world_y + hero.height - self.VERTICAL_BOTTOM
                self._vertical_target = min(self.max_y, max(0, self._vertical_target))
                elapsed = now - self._follow_time if dt is None else dt
                elapsed = min(0.05, max(0.0, elapsed))
                blend = 1.0 - math.exp(-self.VERTICAL_RESPONSE * elapsed)
                new_y = self.y + (self._vertical_target - self.y) * blend
                new_y = min(self.max_y, max(0, new_y))
        self._follow_time = now
        dx, dy = new_x - self.x, new_y - self.y
        if dx or dy:
            for obj in self.objects(level):
                obj.x -= dx
                obj.y -= dy
            hero.x -= dx
            hero.y -= dy
            hero.distance_after_cp += dx
        self.x, self.y = new_x, new_y
        # Disable every old object-specific camera offset. Physics and moving
        # platforms still update normally; only this class translates the view.
        hero.screen_scroll_X = hero.screen_scroll_Y = False
        hero.move_X = hero.move_Y = True

    def draw_backgrounds(self, screen, level, dt=None):
        """Use the same eased vertical camera as the character and terrain.

        Each background still has its own parallax speed, but no second
        smoothing filter that could lag behind a jump or landing.
        """
        screen.fill((12, 22, 18))
        for i, background in enumerate(level.bg_images):
            name = self._background_names[i] if i < len(self._background_names) else ""
            layer = self.BACKGROUND_LAYERS.get(name, self.DEFAULT_BACKGROUND)
            max_x = max(0, background.get_width() - screen.get_width())
            max_y = max(0, background.get_height() - screen.get_height())
            x = -min(max_x, max(0, self.x * layer["x_speed"]))
            # Bottom-anchor the layers; preserve their ground alignment and
            # leave enough overscan above them for gentle upward parallax.
            y = -max_y + (self.max_y - self.y) * layer["y_speed"]
            y = min(0.0, max(-max_y, y))
            level.bgx[i], level.bgy[i] = x, y
            screen.blit(
                background,
                (0, 0),
                pygame.Rect(
                    -round(x), -round(y), screen.get_width(), screen.get_height()
                ),
            )

    def draw_terrain(self, screen):
        screen.blit(
            self._terrain,
            (0, 0),
            pygame.Rect(round(self.x), round(self.y), self.width, self.height),
        )

    def touching_goal(self, hero):
        if self.goal_rect is None:
            return False
        body = pygame.Rect(
            round(hero.x + self.x), round(hero.y + self.y), hero.width, hero.height
        )
        return body.colliderect(self.goal_rect)

    def enter_goal(self, hero):
        touching = self.touching_goal(hero)
        entered = touching and not self.goal_was_touching and not self.goal_solved
        self.goal_was_touching = touching
        return entered
