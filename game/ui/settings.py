"""Compact, event-driven settings; changes persist without per-frame disk writes."""

import game.audio.MusicPlayer as music
import pygame
from game.core.AppConfig import (
    DEFAULT_CONTROLS,
    DEFAULT_SETTINGS,
    LABELS,
    apply_audio_settings,
    load_controls,
    load_settings,
    rebind,
    save_controls,
    save_settings,
)
from game.core.DisplayMode import is_fullscreen, set_fullscreen
from game.core.helper import screen
from game.story.SceneProgress import reset_progress as reset_scenes
from game.story.StoryProgress import reset_progress as reset_story
from game.ui.MenuUI import GOLD, MUTED, PANEL, TEXT, button, header, label


def _confirm_progress_reset():
    snapshot = screen.copy()
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((5, 10, 16, 190))
    clock = pygame.time.Clock()
    selected = 1
    choices = [pygame.Rect(170, 350, 210, 48), pygame.Rect(420, 350, 210, 48)]
    while True:
        for event in pygame.event.get():
            if music.handle_event(event):
                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_TAB):
                    selected = 1 - selected
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return selected == 0
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(choices):
                    if rect.collidepoint(event.pos):
                        return i == 0
        screen.blit(snapshot, (0, 0))
        screen.blit(shade, (0, 0))
        panel = pygame.Rect(90, 170, 620, 260)
        pygame.draw.rect(screen, PANEL, panel, border_radius=12)
        pygame.draw.rect(screen, GOLD, panel, 2, border_radius=12)
        label(screen, "Reset progress?", (400, 209), 32, GOLD, True)
        label(screen, "Scene unlocks and story journal pages will be cleared.",
              (400, 257), 23, TEXT, True)
        label(screen, "This cannot be undone. You will return to the main menu.",
              (400, 286), 21, TEXT, True)
        label(screen, "Your settings and controls will be kept.",
              (400, 315), 21, MUTED, True)
        for i, (rect, name) in enumerate(zip(choices, ("Reset progress", "Cancel"))):
            button(screen, rect, name,
                   selected == i or rect.collidepoint(pygame.mouse.get_pos()))
        pygame.display.flip()
        clock.tick(60)


def setting():
    data = load_settings()
    controls = load_controls()
    clock = pygame.time.Clock()
    pending = None
    dragging = None
    message = "Changes save automatically."
    actions = list(DEFAULT_CONTROLS)
    key_rects = {
        action: pygame.Rect(224 + (i // 4) * 366, 363 + (i % 4) * 44, 142, 34)
        for i, action in enumerate(actions)
    }
    volume_labels = {"volume": "Main", "music_volume": "Music", "effects_volume": "Others"}
    tracks = {
        key: pygame.Rect(350, 118 + i * 30, 300, 14)
        for i, key in enumerate(volume_labels)
    }
    low = pygame.Rect(300, 223, 58, 28)
    fps = pygame.Rect(666, 223, 58, 28)
    fullscreen = pygame.Rect(666, 268, 58, 28)
    reset = pygame.Rect(592, 545, 172, 36)
    reset_progress = pygame.Rect(40, 545, 180, 36)

    def volume(key, x):
        track = tracks[key]
        data[key] = round(max(0, min(1, (x - track.left) / track.width)) * 100)
        apply_audio_settings(data)

    while True:
        back = header(screen, "Settings", "Tune the journey to your play style.")
        for event in pygame.event.get():
            if music.handle_event(event):
                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if pending:
                    if event.key == pygame.K_ESCAPE:
                        pending = None
                        message = "Key change cancelled."
                    elif rebind(controls, pending, event.key):
                        pending = None
                        message = (
                            "Control saved. Existing bindings are swapped if needed."
                        )
                    else:
                        message = "Enter and Escape are reserved for menus."
                    continue
                if event.key == pygame.K_ESCAPE:
                    save_settings(data)
                    return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back.collidepoint(event.pos):
                    save_settings(data)
                    return
                if pending:
                    continue
                selected_track = next(
                    (key for key, track in tracks.items()
                     if track.inflate(20, 10).collidepoint(event.pos)),
                    None,
                )
                if selected_track is not None:
                    dragging = selected_track
                    volume(dragging, event.pos[0])
                elif low.collidepoint(event.pos):
                    data["low_graphics"] = not data["low_graphics"]
                    save_settings(data)
                elif fps.collidepoint(event.pos):
                    data["show_fps"] = not data["show_fps"]
                    save_settings(data)
                elif fullscreen.collidepoint(event.pos):
                    set_fullscreen(not data["fullscreen"])
                    data["fullscreen"] = is_fullscreen()
                    save_settings(data)
                elif reset_progress.collidepoint(event.pos):
                    if _confirm_progress_reset():
                        try:
                            save_settings(data)
                            reset_scenes()
                            reset_story()
                        except OSError:
                            message = "Could not reset progress. Please try again."
                        else:
                            return "progress_reset"
                elif reset.collidepoint(event.pos):
                    data = DEFAULT_SETTINGS.copy()
                    controls = DEFAULT_CONTROLS.copy()
                    set_fullscreen(data["fullscreen"])
                    data["fullscreen"] = is_fullscreen()
                    save_settings(data)
                    save_controls(controls)
                    message = "Default settings and controls restored."
                else:
                    for action, rect in key_rects.items():
                        if rect.collidepoint(event.pos):
                            pending = action
                            message = "Press a new key. Escape cancels."
                            break
            if event.type == pygame.MOUSEMOTION and dragging:
                volume(dragging, event.pos[0])
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging:
                dragging = None
                save_settings(data)
        pygame.draw.rect(screen, PANEL, (36, 107, 728, 98), border_radius=10)
        for key, track in tracks.items():
            label(screen, volume_labels[key], (62, track.y - 4), 24, GOLD)
            pygame.draw.line(screen, (64, 81, 76), track.midleft, track.midright, 6)
            x = round(track.left + track.width * data[key] / 100)
            pygame.draw.line(screen, GOLD, track.midleft, (x, track.centery), 6)
            pygame.draw.circle(screen, TEXT, (x, track.centery), 8)
            label(screen, str(data[key]) + "%", (710, track.centery), 21, MUTED, True)
        pygame.draw.rect(screen, PANEL, (36, 207, 728, 108), border_radius=10)
        label(screen, "Low graphics", (62, 228), 25)
        label(screen, "Show FPS", (430, 228), 25)
        for rect, value in [
            (low, data["low_graphics"]),
            (fps, data["show_fps"]),
            (fullscreen, data["fullscreen"]),
        ]:
            pygame.draw.rect(
                screen,
                (104, 139, 83) if value else (65, 77, 76),
                rect,
                border_radius=14,
            )
            pygame.draw.circle(
                screen,
                TEXT,
                (rect.right - 14 if value else rect.left + 14, rect.centery),
                10,
            )
        label(screen, "Low graphics hides backgrounds.", (62, 278), 19, MUTED)
        label(screen, "Fullscreen", (430, 278), 25)
        label(screen, "Controls", (44, 329), 28, GOLD)
        for i, action in enumerate(actions):
            rect = key_rects[action]
            left = 62 + (i // 4) * 366
            label(screen, LABELS[action], (left, rect.y + 7), 22)
            name = (
                "Press a key..."
                if pending == action
                else controls[action]
                .replace("left ", "L ")
                .replace("right ", "R ")
                .title()
            )
            button(
                screen,
                rect,
                name,
                pending == action or rect.collidepoint(pygame.mouse.get_pos()),
            )
        button(
            screen,
            reset,
            "Restore defaults",
            reset.collidepoint(pygame.mouse.get_pos()),
        )
        button(screen, reset_progress, "Reset progress",
               reset_progress.collidepoint(pygame.mouse.get_pos()))
        label(screen, message, (40, 584), 17, MUTED)
        pygame.display.flip()
        clock.tick(60)
