"""An illustrated journal showing only chapters discovered through play."""

import game.audio.MusicPlayer as music
import pygame
from game.core.helper import screen
from game.ui.MenuUI import GOLD, MUTED, PANEL, button, header, label, text_font
from game.story.StoryArt import illustration
from game.story.StoryProgress import PAGES, draw_notification, unlocked_pages


def wrap(text, font, width):
    rows = []
    line = ""
    for word in text.split():
        candidate = (line + " " + word).strip()
        if line and font.size(candidate)[0] > width:
            rows.append(line)
            line = word
        else:
            line = candidate
    return rows + ([line] if line else [])


def StoryBook(initial_page=None):
    pages = unlocked_pages()
    selected = pages.index(initial_page) if initial_page in pages else 0
    clock = pygame.time.Clock()
    while True:
        back = header(screen, "Story Journal", f"{len(pages)} of 4 pages discovered")
        previous = pygame.Rect(36, 531, 125, 42)
        following = pygame.Rect(639, 531, 125, 42)
        for event in pygame.event.get():
            if music.handle_event(event):
                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    return
                if pages and event.key == pygame.K_LEFT:
                    selected = max(0, selected - 1)
                if pages and event.key == pygame.K_RIGHT:
                    selected = min(len(pages) - 1, selected + 1)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    return
                if pages and previous.collidepoint(event.pos):
                    selected = max(0, selected - 1)
                if pages and following.collidepoint(event.pos):
                    selected = min(len(pages) - 1, selected + 1)
        if not pages:
            pygame.draw.rect(screen, PANEL, (80, 155, 640, 300), border_radius=12)
            label(screen, "Your journal is empty.", (400, 265), 34, GOLD, True)
            label(screen, "Begin your journey with Play.", (400, 314), 25, MUTED, True)
        else:
            number = pages[selected]
            title, text = PAGES[number]
            pygame.draw.rect(screen, PANEL, (28, 105, 744, 412), border_radius=10)
            art = illustration(number)
            width = round(art.get_width() * 240 / art.get_height())
            screen.blit(
                pygame.transform.scale(art, (width, 240)), ((800 - width) // 2, 115)
            )
            label(screen, f"{number}. {title}", (400, 377), 28, GOLD, True)
            for i, line in enumerate(wrap(text, text_font(23), 680)):
                label(screen, line, (400, 407 + i * 23), 23, center=True)
            if selected > 0:
                button(
                    screen,
                    previous,
                    "< Previous",
                    previous.collidepoint(pygame.mouse.get_pos()),
                )
            if selected < len(pages) - 1:
                button(
                    screen,
                    following,
                    "Next >",
                    following.collidepoint(pygame.mouse.get_pos()),
                )
        label(
            screen,
            "Arrow keys: turn page   |   Enter / Esc: return",
            (400, 554),
            20,
            MUTED,
            True,
        )
        draw_notification(screen, top=120)
        pygame.display.flip()
        clock.tick(60)
