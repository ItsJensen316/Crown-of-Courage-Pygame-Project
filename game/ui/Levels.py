"""Scene replay cards reveal artwork only after the scene has been visited."""

import game.audio.MusicPlayer as music
import pygame
from game.core.AppConfig import gameplay_keys, load_settings
from game.core.helper import screen
from game.ui.MenuUI import GOLD, MUTED, button, header, label, thumbnail
from game.story.SceneProgress import visited_scenes


def Levels():
    from game.scenes.Level1_1 import level1
    from game.scenes.Level1_12 import level2

    clock = pygame.time.Clock()
    selected = 0
    cards = [pygame.Rect(48, 132, 340, 366), pygame.Rect(412, 132, 340, 366)]
    subtitles = ["The Forest", "Inside the Tower"]
    while True:
        music.start("menu")
        visited = visited_scenes()
        back = header(
            screen,
            "Choose a scene",
            "Visit a scene during your journey to unlock it here.",
        )
        for event in pygame.event.get():
            if music.handle_event(event):
                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_TAB):
                    selected = 1 - selected
                if event.key == pygame.K_RETURN and selected + 1 in visited:
                    result = (level1 if selected == 0 else level2)(
                        gameplay_keys(), load_settings()
                    )
                    if result and result.get("main_menu"):
                        return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    return
                for i, card in enumerate(cards):
                    if card.collidepoint(event.pos):
                        selected = i
                        if i + 1 in visited:
                            result = (level1 if i == 0 else level2)(
                                gameplay_keys(), load_settings()
                            )
                            if result and result.get("main_menu"):
                                return
                        break
        visited = visited_scenes()
        for i, card in enumerate(cards):
            unlocked = i + 1 in visited
            active = unlocked and (
                selected == i or card.collidepoint(pygame.mouse.get_pos())
            )
            button(screen, card, "", active)
            if not unlocked:
                pygame.draw.rect(screen, (28, 31, 34), card, border_radius=10)
                pygame.draw.rect(screen, (63, 68, 70), card, 2, border_radius=10)
            picture = pygame.Rect(card.x + 8, card.y + 8, 324, 242)
            if unlocked:
                screen.blit(thumbnail(i == 1), picture)
            else:
                pygame.draw.rect(screen, (35, 39, 42), picture, border_radius=6)
                cx, cy = picture.center
                pygame.draw.arc(
                    screen, (105, 111, 111), (cx - 17, cy - 30, 34, 38), 0, 3.15, 5
                )
                pygame.draw.rect(
                    screen, (105, 111, 111), (cx - 24, cy - 10, 48, 38), border_radius=5
                )
                pygame.draw.circle(screen, (35, 39, 42), (cx, cy + 4), 5)
                pygame.draw.line(screen, (35, 39, 42), (cx, cy + 6), (cx, cy + 16), 4)
            label(
                screen,
                f"Scene {i+1}",
                (card.centerx, card.y + 276),
                30,
                GOLD if unlocked else MUTED,
                True,
            )
            label(
                screen,
                subtitles[i] if unlocked else "Not visited",
                (card.centerx, card.y + 307),
                23,
                MUTED,
                True,
            )
            label(
                screen,
                "Enter / Click to play" if unlocked else "Locked",
                (card.centerx, card.bottom - 24),
                21,
                MUTED if not unlocked else GOLD,
                True,
            )
        label(
            screen,
            "Begin with Play. Discovered scenes stay unlocked.",
            (400, 553),
            21,
            MUTED,
            True,
        )
        pygame.display.flip()
        clock.tick(60)
