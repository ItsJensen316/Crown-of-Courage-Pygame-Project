"""Tower mosaic: responsive board, separate piece tray, and precise snapping."""

import random
import sys

import game.ui.GameplayText as gameplay_text
import game.audio.MusicPlayer as music
import pygame
from game.core.helper import loadimages


def puzzle_layout(size):
    width, height = size
    cell = max(32, min(int(width * 0.108), int((height - 215) / 3)))
    side = cell * 3
    return (
        cell,
        pygame.Rect(int(width * 0.07), 145, side, side),
        pygame.Rect(width - int(width * 0.07) - side, 145, side, side),
    )


def puzzle11():
    screen = pygame.display.get_surface()
    cell, board, tray = puzzle_layout(screen.get_size())
    images = [loadimages(f"assets/puzzles/Gate_Puzzle/{i}.png", (cell, cell)) for i in range(9)]
    backdrop = screen.copy()
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((8, 15, 20, 235))
    title = gameplay_text.face(28)
    font = gameplay_text.face(20)
    small = gameplay_text.face(18)
    slots = [
        pygame.Rect(board.x + i % 3 * cell, board.y + i // 3 * cell, cell, cell)
        for i in range(9)
    ]
    homes = [
        pygame.Rect(tray.x + i % 3 * cell, tray.y + i // 3 * cell, cell, cell).inflate(
            -6, -6
        )
        for i in range(9)
    ]
    order = list(range(9))
    random.shuffle(order)
    rects = [pygame.Rect(0, 0, cell, cell) for _ in range(9)]
    for i, home in zip(order, homes):
        rects[i].center = home.center
    placed = [-1] * 9
    dragging = None
    offset = (0, 0)
    clock = pygame.time.Clock()
    reset = pygame.Rect(tray.x, board.bottom + 28, 135, 36)
    close = pygame.Rect(tray.right - 105, board.bottom + 28, 105, 36)

    def label(text, pos, color=(231, 229, 210), face=font):
        rendered = face.render(text, True, color)
        if pos[1] in (34, 80, screen.get_height() - 44):
            screen.blit(
                rendered, rendered.get_rect(midtop=(screen.get_width() // 2, pos[1]))
            )
        else:
            screen.blit(rendered, pos)

    while True:
        for event in pygame.event.get():
            if music.handle_event(event):
                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if close.collidepoint(event.pos):
                    return False
                if reset.collidepoint(event.pos):
                    placed[:] = [-1] * 9
                    for i, home in zip(order, homes):
                        rects[i].center = home.center
                    dragging = None
                    continue
                for i in reversed(range(9)):
                    if rects[i].collidepoint(event.pos):
                        dragging = i
                        placed[i] = -1
                        offset = (rects[i].x - event.pos[0], rects[i].y - event.pos[1])
                        break
            if event.type == pygame.MOUSEMOTION and dragging is not None:
                rects[dragging].topleft = (
                    event.pos[0] + offset[0],
                    event.pos[1] + offset[1],
                )
                rects[dragging].clamp_ip(screen.get_rect())
            if (
                event.type == pygame.MOUSEBUTTONUP
                and event.button == 1
                and dragging is not None
            ):
                i = dragging
                rects[i].topleft = (event.pos[0] + offset[0], event.pos[1] + offset[1])
                target = next(
                    (
                        j
                        for j, slot in enumerate(slots)
                        if slot.collidepoint(rects[i].center)
                    ),
                    None,
                )
                if target is not None and target not in placed:
                    rects[i].center = slots[target].center
                    placed[i] = target
                else:
                    rects[i].center = homes[order.index(i)].center
                dragging = None

        screen.blit(backdrop, (0, 0))
        screen.blit(shade, (0, 0))
        label("THE FOREST GATE", (board.x, 34), (233, 201, 117), title)
        label(
            "Restore the mosaic to open the way to the abandoned castle.", (board.x, 80)
        )
        label("GATE MOSAIC", (board.x, 116), face=small)
        label("PIECES", (tray.x, 116), face=small)
        for panel in (board, tray):
            pygame.draw.rect(
                screen, (23, 37, 42), panel.inflate(16, 16), border_radius=8
            )
            pygame.draw.rect(
                screen, (145, 129, 83), panel.inflate(16, 16), 2, border_radius=8
            )
        for j, slot in enumerate(slots):
            pygame.draw.rect(screen, (64, 80, 80), slot, 1)
            if dragging is not None and slot.collidepoint(rects[dragging].center):
                pygame.draw.rect(
                    screen,
                    (196, 165, 90) if j not in placed else (161, 85, 72),
                    slot,
                    3,
                )
        for home in homes:
            pygame.draw.rect(screen, (40, 55, 59), home, border_radius=4)
        for i in range(9):
            if i == dragging:
                continue
            screen.blit(images[i], rects[i])
            pygame.draw.rect(screen, (112, 121, 110), rects[i], 1)
        if dragging is not None:
            screen.blit(images[dragging], rects[dragging])
            pygame.draw.rect(screen, (233, 201, 117), rects[dragging], 2)
        correct = sum(i == slot for i, slot in enumerate(placed))
        label(f"Aligned: {correct} / 9", (board.x, board.bottom + 34), (233, 201, 117))
        for button, text in ((reset, "Reset pieces"), (close, "Return")):
            pygame.draw.rect(screen, (44, 61, 64), button, border_radius=5)
            screen.blit(
                font.render(text, True, (231, 229, 210)), (button.x + 10, button.y + 8)
            )
        label(
            "Drag a piece into a square. Lift any placed piece to move it.",
            (board.x, screen.get_height() - 44),
            face=small,
        )
        pygame.display.flip()
        if correct == 9:
            return True
        clock.tick(60)
