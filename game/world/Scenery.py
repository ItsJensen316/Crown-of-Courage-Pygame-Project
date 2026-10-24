"""Proportional, ground-aligned standalone forest decorations."""
from functools import lru_cache
from pathlib import Path

import pygame
from game.world.Object import objects
from game.world.Slopes import surface_y

SCENERY_IDS = frozenset((*range(366, 381), *range(388, 394)))


@lru_cache(maxsize=64)
def _scenery_frame(path, height):
    source_path = Path(path)
    if not source_path.is_file():
        source_path = next(p for p in source_path.parent.iterdir()
                           if p.name.lower() == source_path.name.lower())
    source = pygame.image.load(str(source_path)).convert_alpha()
    source = source.subsurface(source.get_bounding_rect()).copy()
    scale = height / source.get_height()
    return pygame.transform.scale(source, (max(1, round(source.get_width() * scale)), height))


class Scenery(objects):
    def __init__(self, x, y, path):
        super().__init__(x, y, 45, 45, [_scenery_frame(path, 30)], "")
        self.ground_offset = 0

    def place_on_ground(self, tiles):
        center = self.x + self.width / 2
        feet = self.y + self.height
        supports = [height for tile in tiles
                    if (height := surface_y(tile, center - 1, center + 1)) is not None
                    and feet - 6 <= height <= feet + 90]
        if supports:
            self.ground_offset = min(supports) - feet + 2

    def draw(self, screen):
        image = self.img_coll[0]
        screen.blit(image, image.get_rect(midbottom=(round(self.x + self.width / 2),
                    round(self.y + self.height + self.ground_offset))))
