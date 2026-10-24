"""Permanent story discoveries, independent of phase deaths and inventory."""

import json
import time
from game.core.SavePaths import SAVE_DIR

SAVE_PATH = SAVE_DIR / "story_progress.json"
_notices = []
_notice_until = 0.0
PAGES = {
    1: (
        "A sister's promise",
        "An enemy king has captured the princess's brother. Leaving the safety of her kingdom behind, she enters the forest to follow his captors. Whatever lies ahead, she has promised to bring him home.",
    ),
    2: (
        "The forest guide",
        "Through the forest's winding paths and hostile creatures, the princess reaches a wise old man beside his hut. He saw soldiers travelling toward the abandoned castle. He directs her east, to a sealed tower entrance: solve its picture puzzle to find the way inside.",
    ),
    3: (
        "The tower keeper",
        "Moving platforms, treacherous slopes and puzzling passages test the princess inside the abandoned tower. Its hostile keeper bars her path, but she defeats him in battle. Regretting his stand, he asks forgiveness and tells her to take the elevator out of the tower.",
    ),
    4: (
        "Beyond the tower",
        "The princess powers the elevator and rides to the tower's summit. At last she steps into the open air. The forest and the abandoned tower are behind her, but her brother is still waiting. With renewed courage, she follows the trail toward the enemy king.",
    ),
}


def unlocked_pages():
    try:
        data = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
        return sorted(
            {n for n in data.get("unlocked", []) if type(n) is int and n in PAGES}
        )
    except (OSError, ValueError, TypeError, AttributeError):
        return []


def unlock(page):
    """Return True only for a new discovery, so introductions never repeat."""
    pages = unlocked_pages()
    if page not in PAGES or page in pages:
        return False
    pages.append(page)
    temporary = SAVE_PATH.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps({"unlocked": sorted(pages)}, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(SAVE_PATH)
    _notices.append(page)
    return True


def draw_notification(screen, top=76):
    """Start each brief notice when a screen can actually display it."""
    global _notice_until
    now = time.perf_counter()
    if now >= _notice_until:
        if not _notices:
            return
        _notices.pop(0)
        _notice_until = now + 4.0
    import pygame
    from game.ui.GameplayText import BACKGROUND, BORDER, COLOR, face

    message = "New page added to your journal — find it under Story."
    font = face(18)
    art = font.render(message, True, COLOR)
    panel = pygame.Rect(0, top, art.get_width() + 28, 40)
    panel.centerx = screen.get_width() // 2
    pygame.draw.rect(screen, BACKGROUND, panel, border_radius=7)
    pygame.draw.rect(screen, BORDER, panel, 2, border_radius=7)
    screen.blit(art, art.get_rect(center=panel.center))
