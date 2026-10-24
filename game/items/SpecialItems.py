"""Health/power upgrades, consumable keys, and single-use healing chests."""

import math

import game.ui.GameplayText as gameplay_text
import pygame
from game.items.ItemSprites import key_icon


class SpecialItems:
    def __init__(self, level):
        self.level = level
        self.font = pygame.font.SysFont("notomono", 20)
        self.message = ""
        self.until = 0
        self.grab_held = False
        # Cached additive halos keep the effect inexpensive while it pulses.
        self.glows = []
        for strength in range(8):
            halo = pygame.Surface((120, 120))
            for radius in range(56, 0, -2):
                power = (1 - radius / 58) ** 2 * (0.65 + strength / 14)
                color = (int(30 * power), int(145 * power), int(65 * power))
                pygame.draw.circle(halo, color, (60, 60), radius)
            self.glows.append(halo)
        self.power_glows = []
        for strength in range(8):
            halo = pygame.Surface((120, 120))
            for radius in range(56, 0, -2):
                power = (1 - radius / 58) ** 2 * (0.65 + strength / 14)
                pygame.draw.circle(
                    halo,
                    (int(120 * power), int(35 * power), int(180 * power)),
                    (60, 60),
                    radius,
                )
            self.power_glows.append(halo)
        self.key_held = False
        self.synced = False
        self.gold_glows = []
        for green in self.glows:
            gold = green.copy()
            # Construct a gold halo with the same cached radial falloff.
            for x in range(120):
                for y in range(120):
                    value = green.get_at((x, y)).g
                    gold.set_at(
                        (x, y),
                        (
                            min(255, int(value * 1.5)),
                            int(value * 0.85),
                            int(value * 0.12),
                        ),
                    )
            self.gold_glows.append(gold)
        for item in level.Inventory:
            if getattr(item, "tile_id", None) == 184:
                icon = pygame.Surface((45, 45), pygame.SRCALPHA)
                icon.blit(key_icon(36), (4, 4))
                item.img_coll = [icon]
        self.chest_frames = {}
        for tile in (173, 174):
            original = pygame.image.load(
                f"assets/art/Level1/1-2/Extras/tile_{tile}.png"
            ).convert_alpha()
            original = original.subsurface(original.get_bounding_rect()).copy()
            height = round(original.get_height() * 72 / original.get_width())
            self.chest_frames[tile] = []
            for stretch in (-2, -1, 0, 1, 2):
                self.chest_frames[tile].append(
                    pygame.transform.scale(original, (72, height + stretch))
                )
        for chest in level.Boxes:
            if getattr(chest, "tile_id", None) not in (173, 174):
                continue
            chest.width = 72
            # Snap the visible base to the nearest floor under this map marker.
            supports = [
                tile.y
                for tile in getattr(level, "tiles", [])
                if tile.x < chest.x + 72
                and tile.x + tile.width > chest.x
                and chest.y + chest.height - 1 <= tile.y <= chest.y + chest.height + 135
            ]
            if supports:
                chest.y = min(supports) - chest.height
                chest.y_copy = chest.y
        self.open_image = pygame.transform.scale(
            pygame.image.load("assets/art/Level1/1-2/Extras/tile_174.png").convert_alpha(),
            (45, 45),
        )

    def notify(self, message):
        self.message = message
        self.until = pygame.time.get_ticks() + 3000

    def update(self, screen, hero, keys, enabled=True):
        held = pygame.key.get_pressed()[keys["grab"]]
        pressed = held and not self.grab_held
        self.grab_held = held
        self.interact_pressed = pressed
        hero.key_prompt_active = False
        if not self.synced:
            self.set_keys(hero, hero.keys_count)
            self.synced = True
        body = pygame.Rect(hero.x, hero.y, hero.width, hero.height)
        prompt = ""
        if enabled and hero.current_health > 0:
            for item in self.level.Inventory[:]:
                tile = getattr(item, "tile_id", None)
                if tile not in (181, 182, 183, 184) or not body.colliderect(
                    pygame.Rect(item.x, item.y, item.width, item.height)
                ):
                    continue
                prompt = (
                    "Press "
                    + pygame.key.name(keys["grab"]).upper()
                    + " to collect "
                    + ("a key" if tile == 184 else "Special Potion")
                )
                if not pressed or getattr(hero, "interaction_used", False):
                    continue
                if tile == 184:
                    self.set_keys(hero, hero.keys_count + 1)
                    self.notify("Key collected")
                elif tile == 182:
                    hero.attack_power = getattr(hero, "attack_power", 1.0) + 0.25
                    self.notify("Special Potion collected — attack power +25%")
                else:
                    hero.max_health += 1
                    self.notify(
                        "Special Potion collected — additional health slot unlocked"
                    )
                hero.interaction_used = True
                hero.sounds["grab"].play()
                self.level.Inventory.remove(item)
                break
            for chest in self.level.Boxes:
                if getattr(chest, "tile_id", None) != 173:
                    continue
                area = pygame.Rect(chest.x, chest.y, chest.width, chest.height).inflate(
                    60, 30
                )
                if not body.colliderect(area):
                    continue
                prompt = (
                    "Press "
                    + pygame.key.name(keys["grab"]).upper()
                    + " to unlock chest"
                    if hero.keys_count
                    else "A key is needed to open this chest"
                )
                if pressed and not getattr(hero, "interaction_used", False):
                    hero.interaction_used = True
                    if hero.keys_count:
                        self.set_keys(hero, hero.keys_count - 1)
                        chest.opened_at = pygame.time.get_ticks()
                        chest.tile_id = 174
                        chest.img_coll = [self.open_image]
                        chest.index = 0
                        hero.current_health = hero.max_health
                        self.notify("Replenished full health")
                        hero.sounds["grab"].play()
                        prompt = ""
                        break
                    self.notify("A key is needed to open this chest")
        # Messages sit below the HUD, away from food interaction prompts.
        message = self.message if pygame.time.get_ticks() < self.until else prompt
        if message:
            gameplay_text.prompt(message)
        if hero.keys_count:
            text = self.font.render(f"Keys: {hero.keys_count}", True, (255, 225, 130))
            screen.blit(text, (20, 100))

    def draw_glows(self, screen):
        now = pygame.time.get_ticks() / 1000
        for item in self.level.Inventory + self.level.Food:
            if getattr(item, "tile_id", None) not in (119, 120, 181, 182, 183, 184):
                continue
            if not (
                -80 < item.x < screen.get_width() + 80
                and -80 < item.y < screen.get_height() + 80
            ):
                continue
            phase = now * 3 + getattr(item, "x_copy", 0) * 0.03
            pulse = int((math.sin(phase) + 1) * 3.5)
            center = (round(item.x + item.width / 2), round(item.y + item.height / 2))
            gold = getattr(item, "tile_id", None) == 184
            halo = (
                self.gold_glows
                if gold
                else (
                    self.power_glows
                    if getattr(item, "tile_id", None) == 182
                    else self.glows
                )
            )[pulse]
            screen.blit(
                halo, halo.get_rect(center=center), special_flags=pygame.BLEND_RGB_ADD
            )
            for i in range(3):
                angle = now * (0.8 + i * 0.2) + i * math.tau / 3
                x = round(center[0] + math.cos(angle) * 26)
                y = round(center[1] + math.sin(angle) * 23)
                pygame.draw.circle(
                    screen,
                    (
                        (255, 215, 65)
                        if gold
                        else (
                            (225, 125, 255)
                            if getattr(item, "tile_id", None) == 182
                            else (125, 255, 95)
                        )
                    ),
                    (x, y),
                    2,
                )

    @staticmethod
    def set_keys(hero, count):
        hero.keys_count = max(0, count)
        hero.inventory[:] = [
            entry for entry in hero.inventory if entry["name"] != "Key"
        ]
        if hero.keys_count:
            hero.inventory.append({"name": "Key", "quantity": hero.keys_count})

    def draw_chest(self, screen, chest):
        now = pygame.time.get_ticks()
        tile = chest.tile_id
        # Gentle idle breathing, followed by a quick opening squash/stretch.
        age = now - getattr(chest, "opened_at", -10000)
        frame = (
            min(4, int(age / 60))
            if tile == 174 and age < 300
            else round(2 + math.sin(now / 450) * 1)
        )
        image = self.chest_frames[tile][frame]
        screen.blit(
            image,
            (
                round(chest.x + (chest.width - 72) / 2),
                round(chest.y + chest.height - image.get_height()),
            ),
        )
