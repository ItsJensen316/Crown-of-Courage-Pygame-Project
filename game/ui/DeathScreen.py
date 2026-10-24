"""A death sequence with passive falling, followed by an explicit retry prompt."""

import time

import game.audio.MusicPlayer as music
import pygame
from game.ui.GameplayText import face


def show_death(screen, hero, backdrop, pit=False, tiles=(), slidables=()):
    music.stop()
    pygame.mixer.stop()
    hero.action = "Death"
    hero.index = hero.counter = 0
    frames = hero.death_frames()
    channel = hero.sounds["death"].play()
    sound_length = hero.sounds["death"].get_length()
    started = time.perf_counter()
    clock = pygame.time.Clock()
    pygame.event.clear((pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.JOYBUTTONDOWN))
    while True:
        elapsed = time.perf_counter() - started
        hero.passive_fall(tiles, slidables)
        hero.index = min(len(frames) - 1, int(elapsed / (17 / 120)))
        animation_done = pit or hero.index == len(frames) - 1
        ready = (
            animation_done
            and elapsed >= sound_length
            and (channel is None or not channel.get_busy())
        )
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if ready and event.type in (
                pygame.KEYDOWN,
                pygame.MOUSEBUTTONDOWN,
                pygame.JOYBUTTONDOWN,
            ):
                return
        screen.blit(backdrop, (0, 0))
        if not pit:
            hero.draw(screen)
        veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        veil.fill((12, 11, 19, min(215, round(65 + elapsed * 85))))
        screen.blit(veil, (0, 0))
        if animation_done:
            cx, cy = screen.get_width() // 2, screen.get_height() // 2
            panel = pygame.Rect(cx - 280, cy - 105, 560, 225)
            pygame.draw.rect(screen, (22, 22, 31), panel, border_radius=12)
            pygame.draw.rect(screen, (128, 91, 70), panel, 2, border_radius=12)
            title = face(54).render("YOU DIED", True, (235, 111, 91))
            screen.blit(title, title.get_rect(center=(cx, cy - 38)))
            pygame.draw.line(
                screen, (160, 119, 78), (cx - 120, cy + 8), (cx + 120, cy + 8), 2
            )
            if ready:
                text = face(20).render(
                    "Press any key or click to continue", True, (255, 240, 185)
                )
                screen.blit(text, text.get_rect(center=(cx, cy + 48)))
            text = face(17).render(
                "Restart from the beginning of this scene.", True, (171, 178, 180)
            )
            screen.blit(text, text.get_rect(center=(cx, cy + 88)))
        pygame.display.flip()
        clock.tick(120)
