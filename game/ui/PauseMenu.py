"""Modal pause overlay: gameplay stays frozen until resume or confirmed exit."""

import game.audio.MusicPlayer as music
import pygame
from game.ui.GameplayText import BACKGROUND, BORDER, COLOR, face
from game.ui.settings import setting


def _text(screen, message, center, size=24, color=COLOR):
    art = face(size).render(message, True, color)
    screen.blit(art, art.get_rect(center=center))


def pause_menu(screen):
    snapshot = screen.copy()
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((5, 10, 16, 185))
    clock = pygame.time.Clock()
    selected = 2  # Enter resumes by default.
    confirming = False
    confirm_selected = 1  # Leaving requires an explicit choice.
    pygame.mixer.pause()
    try:
        while True:
            w, h = screen.get_size()
            cx, cy = w // 2, h // 2
            panel = pygame.Rect(cx - 260, cy - 190, 520, 380)
            choices = [
                pygame.Rect(cx - 175, cy - 72 + i * 78, 350, 58) for i in range(3)
            ]
            confirm = [
                pygame.Rect(cx - 222, cy + 62, 210, 54),
                pygame.Rect(cx + 12, cy + 62, 210, 54),
            ]
            action = None
            for event in pygame.event.get():
                if music.handle_event(event):
                    continue
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if confirming:
                            confirming = False
                        else:
                            return "resume"
                    elif event.key in (
                        pygame.K_UP,
                        pygame.K_DOWN,
                        pygame.K_TAB,
                        pygame.K_LEFT,
                        pygame.K_RIGHT,
                    ):
                        if confirming:
                            confirm_selected = 1 - confirm_selected
                        else:
                            selected = (
                                selected
                                + (
                                    -1
                                    if event.key in (pygame.K_UP, pygame.K_LEFT)
                                    else 1
                                )
                            ) % 3
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        action = (
                            ("leave" if confirm_selected == 0 else "cancel")
                            if confirming
                            else ("main", "settings", "resume")[selected]
                        )
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    rects = confirm if confirming else choices
                    for i, rect in enumerate(rects):
                        if rect.collidepoint(event.pos):
                            action = (
                                ("leave", "cancel")[i]
                                if confirming
                                else ("main", "settings", "resume")[i]
                            )
                            break
            if action == "leave":
                return "main_menu"
            if action == "cancel":
                confirming = False
            if action == "main":
                confirming = True
                confirm_selected = 1
            if action == "resume":
                return "resume"
            if action == "settings":
                if setting() == "progress_reset":
                    return "main_menu"
            screen.blit(snapshot, (0, 0))
            screen.blit(shade, (0, 0))
            pygame.draw.rect(screen, BACKGROUND, panel, border_radius=12)
            pygame.draw.rect(screen, BORDER, panel, 2, border_radius=12)
            _text(
                screen,
                "Return to Main Menu?" if confirming else "Paused",
                (cx, cy - 137),
                28,
            )
            if confirming:
                _text(screen, "Progress in the current scene", (cx, cy - 48), 21)
                _text(screen, "will be reset.", (cx, cy - 17), 21)
                names = ("Main Menu", "Cancel")
                rects = confirm
                focus = confirm_selected
            else:
                names = ("Main Menu", "Settings", "Resume")
                rects = choices
                focus = selected
            mouse = pygame.mouse.get_pos()
            for i, (name, rect) in enumerate(zip(names, rects)):
                active = i == focus or rect.collidepoint(mouse)
                pygame.draw.rect(
                    screen,
                    (68, 62, 42) if active else (31, 40, 43),
                    rect,
                    border_radius=8,
                )
                pygame.draw.rect(
                    screen, COLOR if active else BORDER, rect, 2, border_radius=8
                )
                _text(screen, name, rect.center)
            if not confirming:
                _text(screen, "Esc: resume", (cx, cy + 166), 18, (174, 183, 176))
            pygame.display.flip()
            clock.tick(60)
    finally:
        if pygame.mixer.get_init():
            pygame.mixer.unpause()
