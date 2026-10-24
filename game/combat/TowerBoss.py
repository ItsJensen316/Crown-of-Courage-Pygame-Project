"""The tower keeper's dormant introduction, arena framing and reward."""

import time
from types import SimpleNamespace

import game.audio.MusicPlayer as music
import pygame
from game.story.Dialogue import GuideDialogue
from game.actors.Game_Char_Copy import enemy
from game.items.ItemSprites import Collectible
from game.world.Slopes import surface_y
from game.story.StoryProgress import unlock as unlock_story


class TowerKeeper(enemy):
    MAX_HEALTH = 500

    def __init__(self, *args):
        super().__init__(*args)
        self._load_proportional_frames()
        self.max_enemy_health = self.MAX_HEALTH
        self.enemy_health = self.max_enemy_health
        self.awake = False
        self.potion_dropped = False
        self.death_ready = False

    def _load_proportional_frames(self):
        """Use one uniform pixel scale, with a shared centre and foot baseline."""
        sources = {}
        for action in (
            "Attack",
            "Attack1",
            "Attack2",
            "Idle",
            "Run",
            "Walk",
            "Damage",
            "Death",
        ):
            attribute = "enemy_" + action.lower()
            if not hasattr(self, attribute):
                continue
            sources[attribute] = [
                pygame.image.load(
                    f"{self.path}/{action}/{action}_{i}.png"
                ).convert_alpha()
                for i in range(len(getattr(self, attribute)))
            ]
        # Scale every action together rather than resizing each frame to a
        # square (or changing the character's scale between animations).
        scale = min(
            self.width
            / max(f.get_width() for frames in sources.values() for f in frames),
            self.height
            / max(f.get_height() for frames in sources.values() for f in frames),
        )
        for attribute, frames in sources.items():
            result = []
            for source in frames:
                size = (
                    max(1, round(source.get_width() * scale)),
                    max(1, round(source.get_height() * scale)),
                )
                frame = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                frame.blit(
                    pygame.transform.scale(source, size),
                    ((self.width - size[0]) // 2, self.height - size[1]),
                )
                result.append(frame)
            setattr(self, attribute, result)

    def go_for_attack(self, hero):
        if self.awake and self.enemy_health > 0:
            super().go_for_attack(hero)

    def enemy_movement(self, hero, tiles):
        if self.enemy_health <= 0 and not self.death_ready:
            return
        if self.awake:
            super().enemy_movement(hero, tiles)
            if self.enemy_health <= 0 and not self.death_ready:
                self.action = "Damage"
                self.index = self.counter = 0
                self.hitted = False
            # Once challenged, the keeper stays engaged throughout the room.
            self.fight_range = self.enemy_health > 0 and hero.current_health > 0
            return
        self.fight_range = False
        self.hitted = False
        self.action = "Idle"
        self.gravity = min(5, self.gravity + 0.2)
        self._move_vertical(tiles, [])
        self.animation()

    def draw2(self, screen):
        if self.enemy_health <= 0 and not self.death_ready:
            self.action = "Damage"
        super().draw2(screen)


class KeeperEncounter(GuideDialogue):
    def __init__(self, boss, camera, level):
        super().__init__("data/dialogue/tower_keeper.json")
        self.boss, self.camera, self.level = boss, camera, level
        self.triggered = False
        self.farewell_started = False
        self.encounter_hint = "The tower keeper"
        # Fixed world framing: ceiling at row 16, floor along the bottom,
        # keeper to the left, framing the keeper within the chamber.
        self.frame = (max(0, boss.x - 200), max(0, boss.y - 360))
        # The editor marker uses a normal tile origin, but this actor is 150px
        # tall. Seat his feet on the mound instead of spawning through its cap.
        feet = boss.y + boss.height
        supports = [
            surface_y(t, boss.x + 13, boss.x + boss.width - 17) for t in level.tiles
        ]
        supports = [
            top for top in supports if top is not None and feet - 45 <= top <= feet + 45
        ]
        if supports:
            boss.y = min(supports) - boss.height
        candidates = [
            ladder
            for ladder in getattr(level, "Ladder", [])
            if boss.x - 250 <= ladder.x <= boss.x + 600
            and boss.y + boss.height <= ladder.y <= boss.y + boss.height + 135
        ]
        self._exit_ladders = [
            ladder
            for ladder in candidates
            if not any(
                other.x == ladder.x and other.y < ladder.y for other in candidates
            )
        ]

    @property
    def blocked_ladders(self):
        if not self.triggered or self.boss.death_ready:
            return []
        return self._exit_ladders

    @property
    def barriers(self):
        return [
            SimpleNamespace(x=ladder.x, y=ladder.y, width=ladder.width, height=10)
            for ladder in self.blocked_ladders
        ]

    def draw_gates(self, screen):
        for gate in self.barriers:
            rect = pygame.Rect(round(gate.x), round(gate.y), gate.width, gate.height)
            pygame.draw.rect(screen, (51, 40, 45), rect)
            pygame.draw.rect(screen, (185, 139, 85), rect, 2)
            for x in range(rect.left + 5, rect.right, 9):
                pygame.draw.line(
                    screen, (114, 88, 70), (x, rect.top + 2), (x, rect.bottom - 2), 3
                )

    def update(self, hero, npcs):
        boss = self.boss
        if boss.enemy_health <= boss.max_enemy_health / 2 and not boss.potion_dropped:
            boss.potion_dropped = True
            x = boss.x + (boss.width - 45) / 2
            surfaces = [surface_y(t, x + 8, x + 37) for t in self.level.tiles]
            floors = [
                top
                for top in surfaces
                if top is not None and top >= boss.y + boss.height - 10
            ]
            floor = min(floors, default=boss.y + boss.height)
            self.level.Food.append(Collectible(x, floor - 45, 120))
        if boss.enemy_health <= 0:
            if not self.farewell_started:
                self.farewell_started = True
                music.start("Level1/1-2")
                self.lines = [
                    {
                        "speaker": "Tower Keeper",
                        "text": "Forgive me, Princess. Take the elevator to leave this tower. May you find your brother... good luck.",
                    }
                ]
                self.active, self.completed = True, False
                self.index = 0
                self._started = time.perf_counter()
                self.camera.locked_position = self.frame
                boss.fight_range = boss.hitted = False
                boss.action = "Damage"
                boss.index = boss.counter = 0
                hero.char_speed = hero.gravity = 0
                hero._grabbed_box = None
            if boss.death_ready:
                self.camera.locked_position = None
            return
        if not self.triggered and hero.current_health > 0:
            dx = hero.x + hero.width / 2 - (boss.x + boss.width / 2)
            dy = hero.y + hero.height / 2 - (boss.y + boss.height / 2)
            if abs(dx) <= 280 and abs(dy) <= 210:
                self.triggered = True
                music.start("boss")
                self.active = True
                self.index = 0
                self._started = time.perf_counter()
                self.camera.locked_position = self.frame
                hero.char_speed = hero.gravity = 0
                hero._grabbed_box = None
        if self.triggered and self.completed and not boss.awake:
            boss.awake = True

    def handle_event(self, event, hero, npcs):
        # One forced introduction; the keeper cannot be talked to during combat.
        handled = super().handle_event(event, hero, []) if self.active else False
        if self.farewell_started and self.completed and not self.boss.death_ready:
            unlock_story(3)
            self.boss.death_ready = True
            self.boss.action = "Death"
            self.boss.index = self.boss.counter = 0
            self.camera.locked_position = None
        return handled

    def draw(self, screen, hero, npcs):
        super().draw(screen, hero, [])
