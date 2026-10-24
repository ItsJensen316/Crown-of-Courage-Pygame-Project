import os
import random
from functools import lru_cache

import pygame
from game.actors.EnemyPatrol import ground_ahead
from game.ui.GameplayText import face
from game.core.helper import Level, find_file_length, loadimages2, screen
from game.world.Slopes import surface_y
from game.audio.SoundEffects import load_effect, play_effect
from game.combat.SwordCombat import attack_input, next_swing, sword_damage

pygame.init()


def is_collide(tiles, player):
    index = 0
    for all in tiles:
        if pygame.Rect(player.x, player.y, player.width, player.height).colliderect(
            pygame.Rect(all.x, all.y, all.width, all.height)
        ):
            return True, index
        index += 1
    return False, 0


def check_collide(tiles, player, check_point):
    x = player.x
    y = player.y
    dec = 0
    dec2 = 0

    if check_point == "left":
        x = player.x - 4
        dec = 15
        dec2 = 5
    elif check_point == "right":
        x = player.x + 4
        dec = 15
        dec2 = 5
    elif check_point == "up":
        y = player.y - 4
        dec = 5
    elif check_point == "down":
        y = player.y + 4
        dec = 5
    elif check_point == "fall":
        y = player.y + 4
        dec = 5
    elif check_point == "bottomright":
        x = player.x + 4
        dec = 10
        dec2 = 5
    elif check_point == "bottomleft":
        x = player.x - 4
        dec = 10
        dec2 = 5
    elif check_point == "slideable":
        indx = 0
        for Index, all in enumerate(tiles):
            ground = surface_y(all, player.x + 13, player.x + player.width - 17)
            if ground is not None and abs(player.y + player.height - ground) <= 1:
                return True, indx
            indx += 1
        return False, indx

    probe = pygame.Rect(x + 13, y + 2 + dec2, player.width - 30, player.height - dec)
    for all in tiles:
        slope = getattr(all, "slope", 0)
        if slope:
            ground = surface_y(all, player.x + 13, player.x + player.width - 17)
            if check_point in ("down", "fall"):
                if (
                    ground is not None
                    and getattr(player, "gravity", 0) >= 0
                    and abs(player.y + player.height - ground) <= 6
                ):
                    return True
                continue
            if check_point == "up":
                if player.y + 2 < all.y + all.height - 5:
                    continue
            elif check_point == "right":
                if not (slope == -1 and player.x + player.width - 17 <= all.x + 4):
                    continue
            elif check_point == "left":
                if not (slope == 1 and player.x + 13 >= all.x + all.width - 4):
                    continue
            else:
                continue
        if getattr(all, "one_way", False):
            if (
                check_point not in ("down", "fall")
                or getattr(player, "gravity", 0) < 0
                or player.y + player.height > all.y + 6
            ):
                continue
        if probe.colliderect(pygame.Rect(all.x, all.y, all.width, all.height)):
            return True
    if not check_point:
        probe = pygame.Rect(x + 20, y, player.width * 0.3, player.height)
        for all in tiles:
            if probe.colliderect(
                pygame.Rect(
                    all.x + (all.width // 2 - 0.15 * all.width),
                    all.y,
                    0.3 * all.width,
                    all.height,
                )
            ):
                return True

    return False


class Players:
    def __init__(self, x, y, w, h, path, keys):
        self.action = "Idle"
        self.current_checkpoint_x = 0
        self.current_checkpoint_y = 0
        self.distance_after_cp = 0
        self.life = 3
        self.realive = False
        self.path = path
        self.re_alive = False
        self.x = x
        self.y = y
        self.extra_dist_after_checkPoint = 0
        self.flip = 1
        self.G = 4
        self.char_speed = 0
        self.max_speed = 1
        self.gravity = 0
        self.max_jump_height = 250
        self.max_height_reach = False
        self.collide = False
        self.collide2 = False
        self.running_mode = False
        self.width = w
        self.height = h
        self.cond = True
        self.img_size = (w, h)
        self.img_coll = []
        self.index = 0
        self.animation_time = 16
        self.counter = 0
        self.jump_height = 0
        self.inc = 1
        self.speedY = 0
        self.inventory = [{"name": "", "quantity": 1000}]
        self.right = False
        self.left = False
        self.up = False
        self.down = False
        self.isLadder = False
        self.isFood = False
        self.climbing = False
        self.frame_num = 8
        self.rand = 1
        self.y_scroll_limit = 200
        self.y_scroll_speed = 5
        self.y_rate = 1
        self.screen_scroll_X = False
        self.screen_scroll_Y = False
        self.ladder_collide = False
        self.move_X = True
        self.move_Y = True
        self.attack_power = 1.0
        self.max_health = 6
        self.keys_count = 0
        self.current_health = self.max_health
        self.fall = False
        self.rest_state = False
        self.slideableBlockCollision = False
        self.restriction = False
        self.lift_movement_dir = 0
        self.inside_lift = False

        self.sounds = {
            "hurt": load_effect("assets/audio/Hero_hurt_1.mp3"),
            "hurt2": load_effect("assets/audio/Hero_hurt_2.mp3"),
            "jump": load_effect("assets/audio/Jump_1.mp3"),
            "jump2": load_effect("assets/audio/Jump_2.mp3"),
            "use_potion": load_effect("assets/audio/Use_1.mp3"),
            "use_food": load_effect("assets/audio/Use_2.mp3"),
            "death": load_effect("assets/audio/Hero_death.mp3"),
            "sword": load_effect("assets/audio/Sword_1.mp3"),
            "sword2": load_effect("assets/audio/Sword_2.mp3"),
            "grab": load_effect("assets/audio/Grab.mp3"),
        }

        self.keys = keys

    def play_hurt_sound(self):
        self._hurt_flash_until = pygame.time.get_ticks() + 160
        play_effect(random.choice((self.sounds["hurt"], self.sounds["hurt2"])), "hurt")

    def animation(self):
        if self.index != len(self.img_coll) - 1:
            self.index += 1 if self.counter == self.animation_time else 0
            if self.counter >= self.animation_time:
                self.counter = 0
        else:
            if self.action == "Death":
                return
            self.rand = random.randint(1, 2)
            self.index = 0
        if self.action != "Idle":
            self.counter += self.inc
        else:
            self.counter += 1

    def movement(self, tiles, slidables):

        self.right = check_collide(tiles, self, "right")
        self.left = check_collide(tiles, self, "left")
        self.up = check_collide(tiles, self, "up")
        self.down = check_collide(tiles, self, "down")
        self.fall = check_collide(tiles, self, "fall")
        self.bottomright = check_collide(tiles, self, "bottomright")
        self.bottomleft = check_collide(tiles, self, "bottomleft")
        self.ladder_collide = check_collide(
            [
                ladder
                for ladder in Level.Ladder
                if not any(
                    ladder is blocked
                    for blocked in getattr(self, "blocked_ladders", ())
                )
            ],
            self,
            "",
        )
        self.slideableBlockCollision, index = check_collide(
            slidables, self, "slideable"
        )
        if self.gravity >= 0 and self.slideableBlockCollision:
            self.down = self.fall = True

        keys = pygame.key.get_pressed()
        if self.current_health <= 0:
            self.action = "Death"
            self.animation()
            self.img_size = (80, 90)

            return
        attack_input(self, bool(keys[self.keys["attack"]]))
        previous_index = self.index
        previous_action = self.action
        self.animation_time = (
            24 if getattr(self, "_grabbed_box", None) is not None else 16
        )
        if not self.climbing:
            self.animation()
        if (
            getattr(self, "_sword_in_progress", False)
            and previous_action in ("Attack", "Dash_Attack")
            and self.index < previous_index
        ):
            next_swing(self)
        if not self.ladder_collide:
            self.climbing = False
        if self.char_speed == 0 and not keys[self.keys["jump"]]:
            self.action = "Idle"

        if keys[self.keys["sprint"]]:
            self.speed = 0.05
            self.max_speed = 3
            self.inc = 2
        else:
            self.speed = 0.03
            self.max_speed = 2
            self.inc = 1
        if keys[self.keys["right_move"]]:
            x = self.keys["jump"]
            if not keys[x]:
                self.action = "Run"
                if self.char_speed < -0.15:
                    self.action = "Drift"
                    self.inc = 1
            self.flip = 1
            self.char_speed += self.speed
        elif keys[self.keys["left_move"]]:
            if not keys[self.keys["jump"]]:
                self.action = "Run"
                if self.char_speed > 0.15:
                    self.action = "Drift"
                    self.inc = 1
            self.flip = -1
            self.char_speed -= self.speed
        else:
            for i in range(0, 4):
                if self.char_speed < 0:
                    self.char_speed += 0.01
                elif self.char_speed > 0:
                    self.char_speed -= 0.01

        if self.x < 0:
            self.x = 0
            self.char_speed = 0
        elif self.x > 745:
            self.x = 745
            self.char_speed = 0
        if self.char_speed > self.max_speed:
            self.char_speed = self.max_speed
        elif self.char_speed < -self.max_speed:
            self.char_speed = -self.max_speed
        if (
            keys[self.keys["jump"]]
            and self.jump_height < 24
            and not self.up
            and not self.ladder_collide
            and self.cond
        ):

            if self.jump_height == 0:
                random.choice((self.sounds["jump"], self.sounds["jump2"])).play()
            self.gravity -= 0.4
            self.jump_height += 1
        elif self.down:
            self.cond = True
            self.jump_height = 0
            self.gravity = 0
        else:
            self.cond = False
        if not self.fall:
            self.action = "Jump"
            if self.gravity >= 0:
                self.action = "Fall"

        if getattr(self, "_sword_in_progress", False):
            if self._sword_action is None:
                self._sword_action = (
                    "Dash_Attack" if abs(self.char_speed) > 1 else "Attack"
                )
            self.action = self._sword_action
            self.inc = 2
            at = 4 if self.action == "Attack" else 1
            on_swing_frame = self.index == at
            if on_swing_frame and not getattr(self, "_swing_sound_played", False):
                play_effect(self.sounds["sword2"], "swing")
            self._swing_sound_played = on_swing_frame
        else:
            self._swing_sound_played = False

        if self.ladder_collide:
            self._sword_in_progress = False
            self.climbing = True
            self.action = "Climb"
            self.gravity = 0
            acc = 1
            if keys[self.keys["sprint"]]:
                acc = 2
                self.inc = 2
            if (
                keys[self.keys["jump"]]
                or keys[self.keys["slide"]]
                or keys[self.keys["left_move"]]
                or keys[self.keys["right_move"]]
            ):
                self.animation()
            if keys[self.keys["jump"]]:
                self.gravity = -0.7 * acc
            elif keys[self.keys["slide"]]:
                self.gravity = 0.7 * acc
        elif not self.down:
            self.gravity += 0.15
        elif self.down and not keys[self.keys["jump"]]:
            self.gravity = 0
            self.jump_height = 0
        grabbed_box = getattr(self, "_grabbed_box", None)
        if grabbed_box is not None:
            self._sword_in_progress = False
            # Shift on a contacted box overrides sprint and drift. Facing stays
            # toward the box even when walking backwards to pull it.
            self.char_speed = grabbed_box.speed
            self.flip = grabbed_box._grab_side
            self.action = "Run" if self.char_speed else "Idle"
            self.inc = 1
        self.char_speed = float(format(self.char_speed, ".2f"))

        # Resolve against wall faces instead of nudging into them each frame.
        if self.move_X:
            self._move_horizontal(tiles, self.char_speed)
        self.rest_state = False
        if self.up:
            self.cond = False
            self.gravity = 0.2
            self.gravity += 0.5
        if self.move_Y:
            if self.gravity > 5:
                self.gravity = 5
            self._move_vertical(tiles, slidables)

        # Camera.follow handles viewport translation centrally.
        self.move_X = self.move_Y = True
        self.screen_scroll_X = self.screen_scroll_Y = False

    def _move_horizontal(self, tiles, dx):
        left, right = self.x + 13, self.x + self.width - 17
        top, bottom = self.y + 7, self.y + self.height - 5
        walls = [
            obj
            for obj in tiles
            if not getattr(obj, "one_way", False)
            and top < obj.y + obj.height
            and bottom > obj.y
            and (
                not getattr(obj, "slope", 0)
                or (dx > 0 and obj.slope == -1)
                or (dx < 0 and obj.slope == 1)
            )
        ]
        next_x = self.x + dx
        if dx > 0:
            faces = [
                obj.x for obj in walls if right <= obj.x + 1e-6 and right + dx >= obj.x
            ]
            if faces:
                next_x = min(next_x, min(faces) - (self.width - 17))
                self.char_speed = 0
                self.right = True
        elif dx < 0:
            faces = [
                obj.x + obj.width
                for obj in walls
                if left >= obj.x + obj.width - 1e-6 and left + dx <= obj.x + obj.width
            ]
            if faces:
                next_x = max(next_x, max(faces) - 13)
                self.char_speed = 0
                self.left = True
        self.x = next_x
        # Recover small overlaps when entering a ladder beside a wall. A narrow
        # shaft must not accumulate horizontal drift while climbing down.
        if self.climbing:
            for obj in walls:
                left, right = self.x + 13, self.x + self.width - 17
                if left < obj.x + obj.width and right > obj.x:
                    corrections = (obj.x - right, obj.x + obj.width - left)
                    self.x += min(corrections, key=abs)
                    self.char_speed = 0

    def passive_fall(self, tiles, slidables=()):
        """Scripted scenes disable input, but never suspend downward physics."""
        self.char_speed = 0
        self.climbing = False
        self.gravity = min(5, max(0, self.gravity) + 0.15)
        self.down = self.fall = False
        self._move_vertical(tiles, slidables)

    def _move_vertical(self, tiles, slidables):
        """Resolve vertical movement against surfaces instead of nudging up 5px.

        Keep the existing acceleration/jump settings, but stop exactly at a
        floor or ceiling. This prevents landing and grounded-position bouncing.
        """
        old_y = self.y
        next_y = old_y + self.gravity
        left, right = self.x + 13, self.x + self.width - 17
        if self.gravity >= 0:
            surfaces = []
            for obj in (*tiles, *slidables):
                ground = surface_y(obj, left, right)
                if ground is None:
                    continue
                # A grounded actor follows the ramp down within one step;
                # airborne actors must actually cross its diagonal surface.
                follow = bool(
                    self.down
                    and (getattr(obj, "slope", 0) or getattr(self, "_on_slope", False))
                )
                if (
                    old_y + self.height <= ground + 6
                    and next_y + self.height >= ground - (6 if follow else 1e-7)
                ):
                    surfaces.append(ground)
            if surfaces:
                ground = min(surfaces)
                next_y = ground - self.height
                self._on_slope = any(
                    getattr(obj, "slope", 0)
                    and (height := surface_y(obj, left, right)) is not None
                    and abs(height - ground) < 1e-6
                    for obj in tiles
                )
                self.gravity = 0
                self.down = self.fall = True
                self.cond = True
                self.jump_height = 0
        else:
            ceilings = [
                obj.y + obj.height
                for obj in tiles
                if not getattr(obj, "one_way", False)
                and left < obj.x + obj.width
                and right > obj.x
                and old_y + 2 >= obj.y + obj.height - 1
                and next_y + 2 <= obj.y + obj.height
            ]
            if ceilings:
                next_y = max(ceilings) - 2
                self.gravity = 0
                self.cond = False
        self.y = next_y

    def death_frames(self):
        if not hasattr(self, "_death_frames"):
            self._death_frames = []
            scale = (
                self.height / 33
            )  # Original hero idle/death frames share a 33px baseline.
            for i in range(find_file_length(f"{self.path}/Death")):
                source = pygame.image.load(
                    f"{self.path}/Death/Death_{i}.png"
                ).convert_alpha()
                self._death_frames.append(
                    pygame.transform.scale(
                        source,
                        (
                            round(source.get_width() * scale),
                            round(source.get_height() * scale),
                        ),
                    )
                )
        return self._death_frames

    def _damage_frame(self, frame):
        if pygame.time.get_ticks() >= getattr(self, "_hurt_flash_until", 0):
            return frame
        # Tint only opaque sprite pixels; never modify shared animation frames.
        tinted = frame.copy()
        flash = pygame.mask.from_surface(frame).to_surface(
            setcolor=(255, 145, 145, 150), unsetcolor=(0, 0, 0, 0)
        )
        tinted.blit(flash, (0, 0))
        return tinted

    def draw(self, screen):
        if self.action == "Death":
            self.img_coll = self.death_frames()
            frame = self.img_coll[min(self.index, len(self.img_coll) - 1)]
            if self.flip != 1:
                frame = pygame.transform.flip(frame, True, False)
            frame = self._damage_frame(frame)
            screen.blit(
                frame,
                frame.get_rect(
                    midbottom=(
                        round(self.x + self.width / 2),
                        round(self.y + self.height),
                    )
                ),
            )
            return
        self.img_coll = loadimages2(self.path, self.action, self.img_size)
        if not 0 <= self.index < len(self.img_coll):
            self.index = 0
        index = self.index
        if (
            self.action == "Run"
            and getattr(self, "_grabbed_box", None) is not None
            and self.char_speed * self.flip < 0
        ):
            # Backward steps while pulling, with the torso still facing the box.
            index = (-index) % len(self.img_coll)
        frame = self._damage_frame(self.img_coll[index])
        x = self.x
        if self.flip != 1:
            frame = pygame.transform.flip(frame, True, False)
            # Mirror around the hero's body, not the wider attack canvas.
            x += self.width - frame.get_width()
        screen.blit(frame, (x, self.y))


@lru_cache(maxsize=16)
def _enemy_animation_frames(path, height):
    """Keep one pixel scale across an enemy's differently sized frames."""
    originals = {}
    for action in ("Attack", "Attack1", "Attack2", "Damage", "Death", "Idle", "Run", "Walk"):
        if not os.path.isdir(f"{path}/{action}"):
            continue
        originals[action] = [
            pygame.image.load(f"{path}/{action}/{action}_{i}.png").convert_alpha()
            for i in range(find_file_length(f"{path}/{action}"))
        ]
    scale = height / max(frame.get_height() for frame in originals["Idle"])
    return {
        "enemy_" + action.lower(): [
            pygame.transform.scale(
                frame,
                (
                    max(1, round(frame.get_width() * scale)),
                    max(1, round(frame.get_height() * scale)),
                ),
            )
            for frame in frames
        ]
        for action, frames in originals.items()
    }


class enemy(Players):
    def __init__(self, x, y, w, h, path, keys, identity):
        super().__init__(x, y, w, h, path, keys)
        self.roaming_range = 1200
        self.initial_state = True
        self.final_state = False
        self.init_pos = (x, y)
        self.covered_range = 0
        self.delay_time = 80
        self.delay_count = 0
        self.fight_range = False
        self.radius = 200
        self.speed2 = 1
        self.attack_range = 0.7 * self.width
        self.distanceX = 0
        self.distanceY = 0

        self.left_collide = True
        self.right_collide = True
        self.player_counter = 0
        self.player_hit = False
        self.enemy_counter = 0
        self.enemy_hit = False
        self.enemy_health = 100
        self.damage_rate = 3
        self.hitted = False
        self.hit_counter = 500
        self.identity = identity
        self.can_append = True
        try:
            self.enemy_attack = loadimages2(self.path, "Attack", self.img_size)
        except (FileNotFoundError, pygame.error):
            self.enemy_attack1 = loadimages2(self.path, "Attack1", self.img_size)
            self.enemy_attack2 = loadimages2(self.path, "Attack2", self.img_size)
        self.enemy_death = loadimages2(self.path, "Death", self.img_size)
        self.enemy_damage = loadimages2(self.path, "Damage", self.img_size)
        self.enemy_idle = loadimages2(self.path, "Idle", self.img_size)
        self.enemy_run = loadimages2(self.path, "Run", self.img_size)
        self.enemy_walk = loadimages2(self.path, "Walk", self.img_size)
        for attribute, frames in _enemy_animation_frames(self.path, self.height).items():
            setattr(self, attribute, frames)

    def health_bar(self):
        if self.enemy_health > 0:
            ratio = max(
                0, min(1, self.enemy_health / getattr(self, "max_enemy_health", 100))
            )
            pygame.draw.rect(screen, (50, 50, 50), (self.x - 5, self.y - 20, 100, 10))
            pygame.draw.rect(
                screen,
                (255, 0, 0) if ratio < 0.4 else (0, 255, 0),
                (self.x - 5, self.y - 20, round(100 * ratio), 10),
            )
            pygame.draw.rect(
                screen, (255, 255, 255), (self.x - 5, self.y - 20, 100, 10), 1
            )

    def draw2(self, screen):
        if self.action == "Attack":
            self.img_coll = self.enemy_attack
        elif self.action == "Attack1":
            self.img_coll = self.enemy_attack1
        elif self.action == "Attack2":
            self.img_coll = self.enemy_attack2
        elif self.action == "Death":
            self.img_coll = self.enemy_death
        elif self.action == "Damage":
            self.img_coll = self.enemy_damage
        elif self.action == "Run":
            self.img_coll = self.enemy_run
        elif self.action == "Walk":
            self.img_coll = self.enemy_walk
        else:
            self.img_coll = self.enemy_idle

        if not 0 <= self.index < len(self.img_coll):
            self.index = 0
        frame = self._damage_frame(self.img_coll[self.index])
        if self.flip != 1:
            frame = pygame.transform.flip(frame, True, False)
        screen.blit(
            frame,
            frame.get_rect(
                midbottom=(
                    round(self.x + self.width / 2),
                    round(self.y + self.height),
                )
            ),
        )

    def check_hit(self, hero, enemy_rect):
        if pygame.Rect(hero.x, hero.y, hero.width, hero.height).colliderect(enemy_rect):
            return True
        return False

    def go_for_attack(self, hero):

        self.distanceX = self.x + 10 - hero.x
        self.distanceY = self.y - hero.y
        if self.distanceX < 0:
            self.distanceX = -self.distanceX
        if self.distanceY < 0:
            self.distanceY = -self.distanceY

        if (
            self.distanceX > self.attack_range or self.distanceY > self.height
        ) and self.action != "Death":
            self.speed2 = 1.5

            if self.distanceX > self.width:
                if (self.x - hero.x) < 0:
                    self.flip = 1
                else:
                    self.flip = -1
            self.x += (
                self.speed2
                * self.flip
                * (not self.left_collide)
                * (not self.right_collide)
            )
            self.action = "Run"

        elif self.action != "Death":
            if os.path.isfile(f"{self.path}/Attack{self.rand}/Attack{self.rand}_0.png"):
                self.action = f"Attack{self.rand}"

            else:
                self.action = "Attack"
            disp = self.x + 30 + 5 if (self.x - hero.x) < 0 else self.x - 30 - 5

            if self.check_hit(hero, pygame.Rect(disp, self.y, self.width, self.height)):

                self.player_counter += 1
                if self.player_counter > 60 and hero.current_health > 0:
                    hero.play_hurt_sound()
                    hero.current_health -= 1
                    self.player_counter = 0
        if self.action not in "Attack1Attack2":
            self.player_counter = 0

    def draw_critical_text(self, screen):
        started = getattr(self, "_critical_started", None)
        if started is None or not pygame.Rect(
            self.x, self.y, self.width, self.height
        ).colliderect(screen.get_rect()):
            return
        progress = (pygame.time.get_ticks() - started) / 650
        if not 0 <= progress < 1:
            return
        text = face(18).render("Critical hit!", True, (255, 194, 104))
        shadow = face(18).render("Critical hit!", True, (45, 20, 25))
        alpha = round(255 * min(1, (1 - progress) * 2))
        text.set_alpha(alpha)
        shadow.set_alpha(alpha)
        rect = text.get_rect(
            midbottom=(
                round(self.x + self.width / 2),
                round(self.y - 8 - 26 * progress),
            )
        )
        rect.clamp_ip(screen.get_rect().inflate(-8, -8))
        screen.blit(shadow, rect.move(1, 2))
        screen.blit(text, rect)

    def enemy_movement(self, hero, tiles):
        self.health_bar()
        damage, critical = sword_damage(self, hero)
        self.hitted = bool(damage)
        if damage:
            self.hit_counter = 0
            self.enemy_health = max(0, self.enemy_health - damage)
            play_effect(hero.sounds["sword"], "hit")
        if critical:
            self._critical_started = pygame.time.get_ticks()

        self.right = check_collide(tiles, self, "right")
        self.left = check_collide(tiles, self, "left")
        self.up = check_collide(tiles, self, "up")
        self.down = check_collide(tiles, self, "down")
        self.bottomright = check_collide(tiles, self, "bottomright")
        self.bottomleft = check_collide(tiles, self, "bottomleft")
        near_slope = any(
            getattr(tile, "slope", 0)
            and self.x + self.width > tile.x - 6
            and self.x < tile.x + tile.width + 6
            and self.y + self.height >= tile.y - 10
            and self.y < tile.y + tile.height
            for tile in tiles
        )
        if not near_slope:
            self.y += self.G if not self.down else 0
            if self.down and (self.bottomright or self.bottomleft):
                self.y -= 1

        if self.right:
            self.x -= 1
            self.right_collide = True
            self.final_state = True
            self.initial_state = False
        elif self.left:
            self.x += 1
            self.left_collide = True
            self.initial_state = True
            self.final_state = False
        else:
            self.right_collide = False
            self.left_collide = False
        if not self.fight_range and self.action != "Death":
            if self.initial_state:
                self.flip = 1
            if self.final_state:
                self.flip = -1
            step = (
                self.speed2
                * self.flip
                * (not self.left_collide)
                * (not self.right_collide)
            )
            if step and self.down and not ground_ahead(self, tiles, self.flip):
                # Reverse patrol before the leading foot crosses a drop. Chase
                # movement lives in go_for_attack and bypasses this guard.
                self.flip *= -1
                self.initial_state = self.flip > 0
                self.final_state = self.flip < 0
                self.delay_count = 0
                step = 0
            self.x += step
            if step:
                self.covered_range += self.flip

            if self.covered_range >= self.roaming_range:
                if self.delay_count == self.delay_time:
                    self.final_state = True
                    self.initial_state = False
                    self.delay_count = 0
                    self.delay_time = random.randint(200, 500)
                else:
                    self.final_state = False
                    self.initial_state = False
                    self.delay_count += 1

            if self.covered_range <= 0:
                if self.delay_count == self.delay_time:
                    self.final_state = False
                    self.initial_state = True
                    self.delay_count = 0
                    self.delay_time = random.randint(200, 500)
                    self.action = "Idle"
                else:
                    self.initial_state = False
                    self.final_state = False
                    self.delay_count += 1
                    self.action = "Idle"
        if near_slope:
            self.gravity = 0 if self.down else self.G
            self._move_vertical(tiles, [])
        if pygame.Rect(
            self.x - self.radius,
            self.y + 20,
            self.radius * 2 + self.width,
            self.radius * 2,
        ).colliderect(pygame.Rect(hero.x, hero.y, hero.width, hero.height)):

            self.fight_range = True
        else:
            self.speed2 = 0.5
            self.fight_range = False

        if self.speed2 < 0.5:
            self.action = "Idle"
        elif self.speed2 == 0.5:
            self.action = "Walk"
        elif self.speed2 == 0.7:
            self.action = "Run"

        self.hit_counter += 1
        if self.hit_counter < 50:
            self.action = "Damage"

        if self.enemy_health <= 0:
            self.action = "Death"
        self.animation()
