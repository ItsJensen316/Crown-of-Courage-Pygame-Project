"""Event-driven guide conversation with a bounded, wrapped dialogue panel."""

import json
import time

import game.ui.GameplayText as gameplay_text
import pygame


class GuideDialogue:
    TEXT_SPEED = 42.0

    def __init__(self, path="data/dialogue/wise_old_man.json"):
        with open(path, encoding="utf-8") as source:
            self.lines = json.load(source)["lines"]
        if not self.lines:
            raise ValueError("Guide dialogue must contain at least one line")
        self.active = False
        self.completed = False
        self.index = 0
        self.npc = None
        self._started = 0.0
        self.font = gameplay_text.face(20)
        self.heading = gameplay_text.face(24)
        self.small = gameplay_text.face(18)

    def visible_count(self):
        return min(
            len(self.lines[self.index]["text"]),
            int((time.perf_counter() - self._started) * self.TEXT_SPEED),
        )

    def update(self, hero, npcs):
        """The first approach is a story beat, even if the player jumps past."""
        if self.active or self.completed or not npcs:
            return
        npc = npcs[0]
        if hero.x + hero.width >= npc.x - 110:
            self.npc = npc
            self.active = True
            self.index = 0
            self._started = time.perf_counter()
            hero.char_speed = 0

    def handle_event(self, event, hero, npcs):
        if event.type != pygame.KEYDOWN:
            return False
        if self.active:
            if event.key == pygame.K_ESCAPE and self.completed:
                self.active = False
            elif event.key == pygame.K_RETURN:
                if self.visible_count() < len(self.lines[self.index]["text"]):
                    self._started = -1e9  # First press reveals the current line.
                elif self.index + 1 < len(self.lines):
                    self.index += 1
                    self._started = time.perf_counter()
                else:
                    self.completed = True
                    self.active = False
            return True
        if event.key == pygame.K_RETURN:
            self.npc = next((npc for npc in npcs if npc.can_talk(hero)), None)
            if self.npc is not None:
                self.active = True
                self.index = 0
                self._started = time.perf_counter()
                hero.char_speed = 0
                return True
        return False

    def wrapped(self, text, width):
        lines = []
        line = ""
        for word in text.split():
            candidate = (line + " " + word).strip()
            if line and self.font.size(candidate)[0] > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        return lines + ([line] if line else [])

    def draw(self, screen, hero, npcs):
        if not self.active:
            npc = next((npc for npc in npcs if npc.can_talk(hero)), None)
            if npc:
                text = (
                    "Enter: talk to the old man"
                    if not self.completed
                    else "Enter: speak again"
                )
                gameplay_text.prompt(text)
            return
        current = self.lines[self.index]
        line_count = len(self.wrapped(current["text"], screen.get_width() - 84))
        panel_height = max(150, 90 + line_count * 25)
        panel = pygame.Rect(
            22,
            screen.get_height() - panel_height - 20,
            screen.get_width() - 44,
            panel_height,
        )
        pygame.draw.rect(screen, (20, 26, 30), panel, border_radius=8)
        pygame.draw.rect(screen, (171, 151, 94), panel, 2, border_radius=8)
        current = self.lines[self.index]
        title = self.heading.render(current["speaker"], True, (233, 201, 117))
        screen.blit(
            title, title.get_rect(midtop=(screen.get_width() // 2, panel.y + 14))
        )
        # Wrap the FULL line first, so words don't jump between lines as typed.
        remaining = self.visible_count()
        for row, line in enumerate(self.wrapped(current["text"], panel.width - 40)):
            visible = line[: max(0, remaining)]
            remaining -= len(line) + 1
            rendered = self.font.render(visible, True, gameplay_text.COLOR)
            screen.blit(
                rendered,
                (
                    screen.get_width() // 2 - self.font.size(line)[0] // 2,
                    panel.y + 47 + row * 25,
                ),
            )
        hint = "Enter: reveal / continue" + (
            "    Esc: close"
            if self.completed
            else "    " + getattr(self, "encounter_hint", "A forest encounter")
        )
        rendered = self.small.render(hint, True, gameplay_text.COLOR)
        screen.blit(
            rendered,
            rendered.get_rect(midtop=(screen.get_width() // 2, panel.bottom - 26)),
        )
