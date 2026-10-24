"""Cached sound effects and independent combat feedback channels."""

from functools import lru_cache
from pathlib import Path

import pygame

_sounds = []
_volume = None


def set_volume(volume):
    global _volume
    _volume = volume
    for sound in _sounds:
        sound.set_volume(volume)


@lru_cache(maxsize=24)
def load_effect(path, fallback=None):
    if Path(path).is_file():
        sound = pygame.mixer.Sound(path)
    elif fallback and Path(fallback).is_file():
        sound = pygame.mixer.Sound(fallback)
    else:
        sound = pygame.mixer.Sound(buffer=b"\0" * 2048)
    if _volume is None:
        from game.core.AppConfig import audio_volume, load_settings

        set_volume(audio_volume(load_settings(), "effects"))
    sound.set_volume(_volume)
    _sounds.append(sound)
    return sound


def play_effect(sound, category):
    """Keep combat feedback audible independently of general world effects."""
    pygame.mixer.set_num_channels(max(32, pygame.mixer.get_num_channels()))
    pygame.mixer.set_reserved(3)
    channel = pygame.mixer.Channel({"hurt": 0, "swing": 1, "hit": 2}[category])
    channel.play(sound)
    return channel
