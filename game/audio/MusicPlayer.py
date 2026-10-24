"""Ordered, streaming playlists shared across game and modal menu screens."""

from pathlib import Path

import pygame

MUSIC_END = pygame.USEREVENT + 27
_context = None
_tracks = []
_index = 0


def tracks_for(context):
    if context == "menu":
        return [str(p) for i in (1, 2) if (p := Path(f"assets/audio/Music{i}.mp3")).is_file()]
    if context == "boss":
        boss = Path("assets/audio/Boss/Music.mp3")
        return [str(boss)] if boss.is_file() else tracks_for("Level1/1-2")
    folder = Path("assets/audio") / context
    numbered = [str(p) for i in (1, 2) if (p := folder / f"Music{i}.mp3").is_file()]
    if context == "Level1/1-2" and numbered:
        return numbered
    legacy = folder / "Music.mp3"
    return [str(legacy)] if legacy.is_file() else []


def stop():
    global _context, _tracks, _index
    _context = None
    _tracks = []
    _index = 0
    if pygame.mixer.get_init():
        pygame.mixer.music.set_endevent()
        pygame.mixer.music.stop()
    if pygame.display.get_init():
        pygame.event.clear(MUSIC_END)


def start(context, volume=None):
    global _context, _tracks, _index
    if _context == context and volume is None:
        return
    from game.core.AppConfig import audio_volume, load_settings

    settings = load_settings()
    if volume is not None:
        settings["volume"] = volume
    volume = audio_volume(settings, "music")
    if _context == context:
        pygame.mixer.music.set_volume(volume)
        return
    stop()
    _context = context
    _tracks = tracks_for(context)
    _index = 0
    if not _tracks:
        return
    pygame.mixer.music.load(_tracks[0])
    pygame.mixer.music.set_volume(volume)
    if len(_tracks) == 1:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.set_endevent(MUSIC_END)
        pygame.mixer.music.play()
        pygame.mixer.music.queue(_tracks[1])


def handle_event(event):
    global _index
    if event.type != MUSIC_END:
        return False
    if len(_tracks) > 1:
        _index = (_index + 1) % len(_tracks)
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.queue(_tracks[(_index + 1) % len(_tracks)])
        else:
            # Recover if two very short tracks ended while loading a screen.
            volume = pygame.mixer.music.get_volume()
            pygame.mixer.music.load(_tracks[_index])
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play()
            pygame.mixer.music.queue(_tracks[(_index + 1) % len(_tracks)])
    return True
