"""Static terrain broad phase in world coordinates; exact checks stay unchanged."""

import math


class CollisionGrid:
    CELL_SIZE = 90

    def __init__(self, tiles, camera):
        self.tiles = tiles
        self.camera = camera
        self.cells = {}
        for index, tile in enumerate(tiles):
            # Build once before the first camera translation.
            for key in self._cells(tile.x, tile.y, tile.width, tile.height):
                self.cells.setdefault(key, []).append(index)

    def _cells(self, x, y, width, height):
        left, top = math.floor(x / self.CELL_SIZE), math.floor(y / self.CELL_SIZE)
        right = math.floor((x + width) / self.CELL_SIZE)
        bottom = math.floor((y + height) / self.CELL_SIZE)
        for row in range(top, bottom + 1):
            for column in range(left, right + 1):
                yield column, row

    def near(self, actor, margin=24):
        x = actor.x + self.camera.x - margin
        y = actor.y + self.camera.y - margin
        found = set()
        for cell in self._cells(
            x, y, actor.width + margin * 2, actor.height + margin * 2
        ):
            found.update(self.cells.get(cell, ()))
        # Preserve original map order for the existing narrow-phase checks.
        return [self.tiles[index] for index in sorted(found)]
