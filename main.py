"""Launch Crown of Courage and its main menu."""

import os
from pathlib import Path

import pygame


def start_journey():
    from game.core.AppConfig import gameplay_keys, load_settings
    from game.scenes.Level1_1 import level1
    from game.story.Story import StoryBook
    from game.story.StoryProgress import unlock

    if unlock(1):
        StoryBook(initial_page=1)
    return level1(gameplay_keys(), load_settings())


def home_page():
    import game.audio.MusicPlayer as music
    from game.core.helper import screen
    from game.ui.Levels import Levels
    from game.ui.MenuUI import GOLD, MUTED, button, home_art, icon, label
    from game.ui.settings import setting
    from game.story.Story import StoryBook
    from game.story.StoryProgress import draw_notification

    clock = pygame.time.Clock()
    selected = 0
    rects = [pygame.Rect(200, 315, 400, 85)] + [
        pygame.Rect(x - 58, 450, 116, 96) for x in (250, 400, 550)
    ]
    actions = [start_journey, setting, Levels, StoryBook]
    names = ["PLAY", "Settings", "Levels", "Story"]
    while True:
        music.start("menu")
        pygame.display.set_caption("Crown of Courage: A Princess's Quest")
        close = pygame.Rect(screen.get_width() - 54, 14, 40, 40)
        for event in pygame.event.get():
            if music.handle_event(event):
                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_TAB):
                    selected = (selected + 1) % 4
                elif event.key in (pygame.K_LEFT, pygame.K_UP):
                    selected = (selected - 1) % 4
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    actions[selected]()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if close.collidepoint(event.pos):
                    pygame.quit()
                    raise SystemExit
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        selected = i
                        actions[i]()
                        break
        screen.blit(home_art(), (0, 0))
        label(screen, "Crown of Courage:", (400, 29), 44, GOLD, True)
        label(screen, "A Princess's Quest", (400, 64), 33, GOLD, True)
        label(
            screen, "Through the forest. Beyond the tower.", (400, 94), 23, MUTED, True
        )
        mouse = pygame.mouse.get_pos()
        pygame.draw.rect(
            screen,
            (111, 46, 46) if close.collidepoint(mouse) else (26, 37, 38),
            close,
            border_radius=7,
        )
        pygame.draw.rect(screen, GOLD, close, 1, border_radius=7)
        pygame.draw.line(
            screen,
            GOLD,
            (close.x + 12, close.y + 12),
            (close.right - 12, close.bottom - 12),
            3,
        )
        pygame.draw.line(
            screen,
            GOLD,
            (close.right - 12, close.y + 12),
            (close.x + 12, close.bottom - 12),
            3,
        )
        button(
            screen,
            rects[0],
            "PLAY",
            selected == 0 or rects[0].collidepoint(mouse),
            True,
        )
        for i, kind in enumerate(["settings", "levels", "story"], 1):
            rect = rects[i]
            active = selected == i or rect.collidepoint(mouse)
            button(screen, rect, "", active)
            icon(screen, kind, (rect.centerx, rect.y + 35))
            label(
                screen,
                names[i],
                (rect.centerx, rect.bottom - 20),
                23,
                GOLD if active else (231, 234, 222),
                True,
            )
        label(
            screen,
            "A sister's promise. A journey into the unknown.",
            (400, 580),
            20,
            MUTED,
            True,
        )
        draw_notification(screen, top=110)
        pygame.display.flip()
        clock.tick(60)


def main():
    os.chdir(Path(__file__).resolve().parent)
    pygame.init()
    pygame.display.set_icon(pygame.image.load("assets/art/icon.png"))
    try:
        home_page()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
