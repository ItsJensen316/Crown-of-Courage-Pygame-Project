"""Forest 45-degree ramp geometry. Tile 47 rises right; 48 rises left."""


def surface_y(tile, left, right):
    """Highest supporting point under the actor's inset footprint."""
    start = max(left, tile.x)
    end = min(right, tile.x + tile.width)
    if end <= start:
        return None
    direction = getattr(tile, "slope", 0)
    if direction == 1:
        return tile.y + tile.height - (end - tile.x) * tile.height / tile.width
    if direction == -1:
        return tile.y + (start - tile.x) * tile.height / tile.width
    return tile.y
