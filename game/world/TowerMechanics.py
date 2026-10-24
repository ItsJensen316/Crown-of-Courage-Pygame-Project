"""Tower hazards, platform lanes, and the block-powered elevator."""

from types import SimpleNamespace

import game.ui.GameplayText as gameplay_text
import game.audio.MusicPlayer as music
import pygame
from game.story.StoryProgress import draw_notification


def actor_rect(actor):
    return pygame.Rect(
        round(actor.x + 13), round(actor.y + 3), actor.width - 30, actor.height - 3
    )


def hazard_rect(hazard):
    spike = getattr(hazard, "tile_id", 202) == 201
    return pygame.Rect(
        hazard.x + 5,
        hazard.y + (30 if spike else 7),
        hazard.width - 10,
        16 if spike else hazard.height - 7,
    )


def configure_platforms(level, rules):
    for platform in level.Slidables:
        # A wider deck is easier to read and board; lanes end before solid walls.
        old = platform.width
        platform.width = 90
        platform.img = [
            pygame.transform.scale(img, (90, platform.height)) for img in platform.img
        ]
        blockers = [
            t
            for t in level.tiles
            if t.y < platform.y + platform.height - 3
            and t.y + t.height > platform.y + 3
        ]
        right = min(
            (t.x for t in blockers if t.x >= platform.x + old), default=platform.x + 450
        )
        left = max(
            (t.x + t.width for t in blockers if t.x + t.width <= platform.x), default=0
        )
        maximum = rules.get("platform_travel_tiles", 7) * 45
        if right - platform.x - platform.width >= 90:
            platform.roaming_range = min(
                maximum, right - platform.x - platform.width - 2
            )
        else:
            # Start at the far end of a leftward lane, retaining the CSV spawn.
            travel = max(0, min(maximum, platform.x - left - 2))
            platform.covered_range = travel
            platform.roaming_range = travel
            platform.dir = -1
        platform.speed = rules.get("platform_speed", 1.0)


class HazardDamage:
    def __init__(self):
        self.cooldown = 0
        self.flash = 0

    def update(self, hero, hazards):
        self.cooldown = max(0, self.cooldown - 1)
        self.flash = max(0, self.flash - 1)
        if self.cooldown or hero.current_health <= 0:
            return False
        body = actor_rect(hero)
        for hazard in hazards:
            # Spikes occupy the floor edge, flames their visible central area.
            box = hazard_rect(hazard)
            if body.colliderect(box):
                hero.current_health = max(0, hero.current_health - 1)
                hero.play_hurt_sound()
                if hero.current_health == 0:
                    hero.index = hero.counter = 0
                self.cooldown, self.flash = 120, 18
                return True
        return False

    def update_enemies(self, enemies, hazards):
        """Ten HP per second of exposure, with one timer per enemy (120 FPS)."""
        for enemy in enemies:
            cooldown = max(0, getattr(enemy, "_hazard_cooldown", 0) - 1)
            enemy._hazard_cooldown = cooldown
            if cooldown or enemy.enemy_health <= 0 or not getattr(enemy, "awake", True):
                continue
            if any(
                actor_rect(enemy).colliderect(hazard_rect(hazard)) for hazard in hazards
            ):
                enemy.enemy_health = max(0, enemy.enemy_health - 10)
                enemy.hit_counter = 0
                enemy._hurt_flash_until = pygame.time.get_ticks() + 160
                enemy._hazard_cooldown = 120

    def draw(self, screen):
        if self.flash:
            pygame.draw.rect(screen, (210, 62, 43), screen.get_rect(), 5)


class TowerElevator:
    def __init__(self, parts, rules):
        self.parts = parts
        self.floor_parts = [p for p in parts if p.lift_index in (161, 156, 157, 162)]
        floor = min((p.y + p.height - 5 for p in self.floor_parts), default=0)
        self.travel = max(0, floor - rules.get("elevator_exit_floor_row", 5) * 45)
        self.speed = rules.get("elevator_speed", 4.5)
        self.offset = 0.0
        self.state = "waiting"
        self.door_open = 0.0
        self.blocks = []
        self.buttons = []
        self.enabled = self.moving = self.started = self.locked = self.at_top = False

    @property
    def floors(self):
        return [
            SimpleNamespace(x=p.x, y=p.y + p.height - 5, width=p.width, height=5)
            for p in self.floor_parts
        ]

    @property
    def barriers(self):
        # A shut or partly opened doorway cannot be walked through.
        panels = [p for p in self.parts if 152 <= p.lift_index <= 157]
        if not panels or self.state != "waiting" or self.door_open == 1:
            return []
        return [
            SimpleNamespace(
                x=min(p.x for p in panels),
                y=min(p.y for p in panels),
                width=90,
                height=135,
            )
        ]

    def update(self, hero, buttons, blocks):
        self.enabled = False
        # Part 1's puzzle lock shares the button group, but has no elevator.
        if not self.parts or not self.floor_parts:
            self.buttons = []
            self.blocks = []
            return
        self.buttons = buttons
        for button in buttons:
            button.pressed = any(
                button.x + 5 <= block.x + block.width / 2 <= button.x + button.width - 5
                and abs(block.y + block.height - (button.y + button.height)) <= 6
                for block in blocks
            )
            hero_on_plate = (
                hero.x + hero.width - 17 > button.x + 5
                and hero.x + 13 < button.x + button.width - 5
                and abs(hero.y + hero.height - (button.y + button.height)) <= 6
                and getattr(hero, "gravity", 0) >= 0
            )
            button.pressed = button.pressed or hero_on_plate
            self.enabled |= button.pressed
        if not self.parts or not self.floor_parts:
            return
        left = min(p.x for p in self.parts)
        right = max(p.x + p.width for p in self.parts)
        floor = self.floors[0].y
        inside = (
            hero.x + hero.width / 2 > left + 30
            and hero.x + hero.width / 2 < right - 30
            and abs(hero.y + hero.height - floor) <= 8
        )
        self.blocks = blocks
        if self.state == "waiting" and self.enabled and inside and self.door_open >= 1:
            self.state = "closing"
            self.started = True
        self.locked = self.state in ("closing", "ascending", "opening")
        self.moving = False
        if self.locked:
            hero.x = (left + right - hero.width) / 2
            hero.char_speed = hero.gravity = 0
            hero.climbing = False
        target_open = (
            self.state in ("opening", "arrived")
            or self.state == "waiting"
            and self.enabled
        )
        self.door_open = (
            min(1.0, self.door_open + 1 / 36)
            if target_open
            else max(0.0, self.door_open - 1 / 36)
        )
        if self.door_open > 1 - 1e-6:
            self.door_open = 1.0
        if self.door_open < 1e-6:
            self.door_open = 0.0
        if self.state == "closing" and self.door_open == 0:
            self.state = "ascending"
        if self.state == "ascending" and self.enabled:
            next_offset = max(-self.travel, self.offset - self.speed)
            dy = next_offset - self.offset
            self.offset = next_offset
            for part in self.parts:
                part.y += dy
            self.moving = bool(dy)
            if self.offset <= -self.travel:
                self.at_top = True
                self.state = "opening"
        if self.locked:
            hero.y = self.floors[0].y - hero.height
        if self.state == "opening" and self.door_open == 1:
            self.state = "arrived"
            self.locked = False

    def draw_back(self, screen, camera_y):
        if not self.parts:
            return
        center = (
            min(p.x for p in self.parts) + max(p.x + p.width for p in self.parts)
        ) / 2
        roof = min(p.y for p in self.parts)
        # Links are anchored to the shaft, so camera movement cannot make them swim.
        y = round(-camera_y) % 14 - 14
        while y < min(screen.get_height(), roof + 12):
            width = 10 if (round((y + camera_y) / 14) % 2) == 0 else 6
            link = pygame.Rect(round(center - width / 2), y, width, 17)
            pygame.draw.ellipse(screen, (23, 25, 32), link, 3)
            pygame.draw.ellipse(screen, (144, 151, 157), link.inflate(-3, -3), 1)
            y += 14
        for part in self.parts:
            # The wooden-door sprite is the open cabin; the grille is its closed state.
            if not 146 <= part.lift_index <= 151:
                part.draw(screen)

    def draw_doors(self, screen):
        # Use the original Lift1 grille in front of the rider when closed.
        # Lift2 remains behind the rider as the open-cabin artwork.
        opacity = round(255 * (1 - self.door_open))
        if not opacity:
            return
        for part in self.parts:
            if 146 <= part.lift_index <= 151:
                frame = part.img_coll[0]
                if opacity < 255:
                    frame = frame.copy()
                    frame.set_alpha(opacity)
                screen.blit(frame, (round(part.x), round(part.y)))

    def exit_rect(self):
        if not self.parts or not self.floors:
            return pygame.Rect(0, 0, 0, 0)
        right = max(p.x + p.width for p in self.parts)
        return pygame.Rect(round(right + 8), round(self.floors[0].y - 130), 135, 140)

    def reached_exit(self, hero):
        return self.state == "arrived" and self.exit_rect().colliderect(
            actor_rect(hero)
        )

    def draw_status(self, screen, hero):
        if not self.parts or not self.floor_parts:
            return
        if self.state == "arrived":
            gameplay_text.prompt("Exit the tower to continue")
            return
        if self.locked:
            gameplay_text.prompt(
                "Lift doors closing..."
                if self.state == "closing"
                else "Ascending to the tower exit..."
            )
            return
        # Instructions belong to the stationary switch, never to the box.
        if not any(
            (hero.x + hero.width / 2 - b.x - b.width / 2) ** 2
            + (hero.y + hero.height / 2 - b.y - b.height / 2) ** 2
            <= (5 * 45) ** 2
            for b in self.buttons
        ):
            return
        gameplay_text.prompt(
            "Push the box onto this switch to keep the lift activated"
            if self.enabled
            else "Push the box onto this switch to activate the lift"
        )


def show_demo_end(hero):
    """Show the outdoor epilogue and return to the main menu."""
    screen = pygame.display.get_surface()
    background = pygame.Surface(screen.get_size())
    background.fill((92, 151, 175))
    for name in ("L11B1.png", "L11B2.png"):
        source = pygame.image.load(
            "assets/art/Backgrounds/Level1/1-1/" + name
        ).convert_alpha()
        crop = source.subsurface(
            (0, 0, min(800, source.get_width()), min(600, source.get_height()))
        )
        background.blit(pygame.transform.scale(crop, screen.get_size()), (0, 0))
    title = gameplay_text.face(28)
    text = gameplay_text.face(20)
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if music.handle_event(event):
                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_RETURN,
                pygame.K_ESCAPE,
            ):
                return
        screen.blit(background, (0, 0))
        pygame.draw.rect(screen, (53, 65, 39), (0, 480, 800, 120))
        pygame.draw.rect(screen, (95, 123, 58), (0, 480, 800, 10))
        # The princess has emerged from the stone doorway into the forest.
        pygame.draw.rect(screen, (48, 44, 53), (0, 240, 160, 240))
        pygame.draw.rect(screen, (20, 24, 28), (65, 330, 95, 150))
        if hero.img_coll:
            frame = hero.img_coll[min(hero.index, len(hero.img_coll) - 1)]
            screen.blit(frame, (380, 480 - frame.get_height()))
        panel = pygame.Rect(40, 60, screen.get_width() - 80, 160)
        pygame.draw.rect(screen, (19, 28, 30), panel, border_radius=10)
        for face, line, y, color in [
            (title, "Beyond the abandoned tower", 82, (237, 207, 133)),
            (
                text,
                "The princess steps outside. Her search continues...",
                137,
                (237, 239, 225),
            ),
            (text, "End of demo  |  Enter / Esc: return to menu", 181, (176, 195, 180)),
        ]:
            rendered = face.render(line, True, color)
            screen.blit(
                rendered, rendered.get_rect(midtop=(screen.get_width() // 2, y))
            )
        draw_notification(screen, top=245)
        pygame.display.flip()
        clock.tick(60)


def show_loading():
    """Flip before any blocking phase-two asset work begins."""
    screen = pygame.display.get_surface()
    screen.fill((15, 18, 26))
    title = gameplay_text.face(28).render("Loading...", True, (233, 201, 117))
    subtitle = gameplay_text.face(20).render(
        "Entering the tower", True, (195, 201, 203)
    )
    screen.blit(
        title,
        title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 15)),
    )
    screen.blit(
        subtitle,
        subtitle.get_rect(
            center=(screen.get_width() // 2, screen.get_height() // 2 + 28)
        ),
    )
    pygame.display.flip()
    pygame.event.pump()
