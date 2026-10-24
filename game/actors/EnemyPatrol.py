"""Patrol-only ledge awareness; combat pursuit is intentionally unrestricted."""

import math

from game.world.Slopes import surface_y


def ground_ahead(actor, tiles, direction):
    """Trace connected floor from a supporting foot to just beyond the stance.

    Comparing the far foot directly to body height fails on downhill ramps:
    the two feet may span more than a tile of vertical drop. Small connected
    surface steps distinguish that continuous incline from a real ledge.
    """
    left, right = actor.x + 13, actor.x + actor.width - 17
    feet = actor.y + actor.height
    supports = []
    for tile in tiles:
        ground = surface_y(tile, left, right)
        if ground is None or abs(ground - feet) > 9:
            continue
        start, end = max(left, tile.x), min(right, tile.x + tile.width)
        slope = getattr(tile, "slope", 0)
        if slope == 1:
            anchor = end - 1e-4
        elif slope == -1:
            anchor = start + 1e-4
        else:
            anchor = end - 1e-4 if direction > 0 else start + 1e-4
        supports.append((abs(ground - feet), -anchor * direction, anchor, ground))
    if not supports:
        return False
    _, _, anchor, height = min(supports)
    target = (right + 5) if direction > 0 else (left - 5)
    steps = max(1, math.ceil(abs(target - anchor) / 3))
    distance = abs(target - anchor) / steps
    for i in range(1, steps + 1):
        x = anchor + (target - anchor) * i / steps
        candidates = []
        for tile in tiles:
            ground = surface_y(tile, x - 0.001, x + 0.001)
            if ground is not None and abs(ground - height) <= distance + 2:
                candidates.append(ground)
        if not candidates:
            return False
        height = min(candidates, key=lambda ground: abs(ground - height))
    return True
