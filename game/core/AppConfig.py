"""Shared persisted menu settings and validated gameplay bindings."""

import json
from pathlib import Path

import pygame

DEFAULT_SETTINGS = {
    "volume": 70,
    "music_volume": 70,
    "effects_volume": 70,
    "low_graphics": False,
    "show_fps": False,
    "fullscreen": True,
}
DEFAULT_CONTROLS = {
    "jump": "w",
    "left_move": "a",
    "right_move": "d",
    "attack": "space",
    "inventory": "q",
    "grab": "e",
    "sprint": "left shift",
    "slide": "s",
}
LABELS = {
    "jump": "Jump / climb up",
    "left_move": "Move left",
    "right_move": "Move right",
    "attack": "Attack",
    "inventory": "Inventory",
    "grab": "Grab / Use",
    "sprint": "Sprint",
    "slide": "Climb down / slide",
}


def read_json(path, default):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except (OSError, ValueError):
        return default.copy()


def load_settings():
    data = {**DEFAULT_SETTINGS, **read_json("saves/setting.json", {})}
    for key in ("volume", "music_volume", "effects_volume"):
        data[key] = max(0, min(100, int(data[key])))
    return data


def audio_volume(data, category):
    return data["volume"] * data.get(category + "_volume", 100) / 10000


def apply_audio_settings(data):
    if pygame.mixer.get_init():
        from game.audio.SoundEffects import set_volume

        pygame.mixer.music.set_volume(audio_volume(data, "music"))
        set_volume(audio_volume(data, "effects"))


def save_settings(data):
    Path("saves/setting.json").write_text(json.dumps(data, indent=2) + "\n")
    apply_audio_settings(data)


def load_controls():
    data = read_json("saves/control_key.json", DEFAULT_CONTROLS)
    result = {}
    for action, default in DEFAULT_CONTROLS.items():
        name = data.get(action, default)
        try:
            pygame.key.key_code(name)
        except (ValueError, TypeError):
            name = default
        result[action] = name
    return result


def gameplay_keys():
    return {
        action: pygame.key.key_code(name) for action, name in load_controls().items()
    }


def save_controls(data):
    Path("saves/control_key.json").write_text(json.dumps(data, indent=2) + "\n")


def rebind(data, action, key):
    if key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_UNKNOWN):
        return False
    name = pygame.key.name(key)
    if not name:
        return False
    previous = data[action]
    for other, value in data.items():
        if other != action and value == name:
            data[other] = previous
    data[action] = name
    save_controls(data)
    return True
