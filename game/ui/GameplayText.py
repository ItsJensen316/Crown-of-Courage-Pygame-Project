"""Shared, responsive styling and layout for gameplay messages."""

from functools import lru_cache

import pygame

COLOR = (255, 240, 185)
BACKGROUND = (22, 27, 32)
BORDER = (126, 108, 69)
_pending = []


@lru_cache(maxsize=12)
def face(size=20):
    return pygame.font.SysFont("notomono", size)


def begin():
    _pending.clear()


def prompt(message):
    if message and message not in _pending:
        _pending.append(message)


def wrapped(message, font, width):
    lines = []
    line = ""
    for word in message.split():
        # Also handle unusually narrow windows or long unbroken labels.
        for char in (" " if line else "") + word:
            if line and font.size(line + char)[0] > width:
                lines.append(line.rstrip())
                line = ""
            line += char
    if line.strip():
        lines.append(line.strip())
    return lines


def draw(screen):
    width, height = screen.get_size()
    font = face(20 if width >= 480 else 17)
    max_width = max(20, min(720, width - 48))
    y = max(72, round(height * 0.14))
    boxes = []
    for message in _pending:
        lines = wrapped(message, font, max_width)
        surfaces = [font.render(line, True, COLOR) for line in lines]
        if not surfaces:
            continue
        box = pygame.Rect(
            0,
            y,
            max(s.get_width() for s in surfaces) + 24,
            len(surfaces) * (font.get_linesize() + 2) + 16,
        )
        box.centerx = width // 2
        pygame.draw.rect(screen, BACKGROUND, box, border_radius=6)
        pygame.draw.rect(screen, BORDER, box, 1, border_radius=6)
        for i, surface in enumerate(surfaces):
            screen.blit(
                surface,
                surface.get_rect(
                    midtop=(width // 2, y + 8 + i * (font.get_linesize() + 2))
                ),
            )
        boxes.append(box)
        y = box.bottom + 8
    return boxes
