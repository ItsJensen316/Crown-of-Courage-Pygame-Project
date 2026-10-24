"""Committed sword swings and release timing measured from actual damage."""

import pygame

CRITICAL_WINDOW_MS = 90
CRITICAL_COOLDOWN_MS = 300
MINIMUM_HOLD_MS = 190
NORMAL_DAMAGE_TICKS = 8


def attack_input(hero, pressed):
    now = pygame.time.get_ticks()
    was_pressed = getattr(hero, "_attack_down", False)
    hero._attack_released = was_pressed and not pressed
    if pressed and not was_pressed:
        hero._attack_pressed_at = now
        if not getattr(hero, "_sword_in_progress", False):
            hero._sword_cycle = getattr(hero, "_sword_cycle", 0) + 1
            hero._sword_in_progress = True
            hero._sword_action = None
            hero.index = hero.counter = 0
            hero.inc = 2
            hero._swing_sound_played = False
    hero._attack_down = pressed


def next_swing(hero):
    if hero._attack_down:
        hero._sword_cycle = getattr(hero, "_sword_cycle", 0) + 1
        hero._sword_action = None
    else:
        hero._sword_in_progress = False


def sword_damage(enemy, hero):
    """Normal damage occurs at contact; a qualified later release adds its bonus."""
    now = pygame.time.get_ticks()
    cycle = getattr(hero, "_sword_cycle", 0)
    active = hero.action in ("Attack", "Dash_Attack")
    contact_frame = 4 if hero.action == "Attack" else 1
    in_range = abs(enemy.x + 10 - hero.x) < 80 and abs(enemy.y - hero.y) < 80
    if (
        active
        and hero.index == contact_frame
        and in_range
        and getattr(enemy, "_sword_hit_cycle", None) != cycle
        and hero.current_health > 0
        and enemy.enemy_health > 0
    ):
        damage = (
            enemy.damage_rate * NORMAL_DAMAGE_TICKS * getattr(hero, "attack_power", 1.0)
        )
        # Eligibility is captured BEFORE release. Taps and late re-presses cannot
        # retroactively turn their normal strike into a critical.
        eligible = (
            getattr(hero, "_attack_down", False)
            and now - getattr(hero, "_attack_pressed_at", now) >= MINIMUM_HOLD_MS
        )
        enemy._sword_contact = (cycle, now, damage, eligible)
        enemy._sword_hit_cycle = cycle
        return damage, False
    contact = getattr(enemy, "_sword_contact", None)
    if contact is None:
        return 0, False
    hit_cycle, damaged_at, damage, eligible = contact
    elapsed = now - damaged_at
    if hit_cycle != cycle or elapsed > CRITICAL_WINDOW_MS or enemy.enemy_health <= 0:
        enemy._sword_contact = None
        return 0, False
    if getattr(hero, "_attack_released", False):
        enemy._sword_contact = None
        if (
            eligible
            and 0 < elapsed <= CRITICAL_WINDOW_MS
            and in_range
            and hero.current_health > 0
            and now >= getattr(hero, "_critical_ready_at", 0)
        ):
            hero._critical_ready_at = now + CRITICAL_COOLDOWN_MS
            return damage, True  # Initial damage + this bonus = one 2x strike.
    return 0, False
