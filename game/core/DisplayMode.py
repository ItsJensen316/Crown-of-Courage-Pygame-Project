"""One scaled display for reliable fullscreen/windowed transitions."""

import pygame

LOGICAL_SIZE = (800, 600)
_fullscreen = None
_scaled = False


def set_fullscreen(enabled):
    global _fullscreen, _scaled
    enabled = bool(enabled)
    if not pygame.display.get_init():
        pygame.display.init()
    current = pygame.display.get_surface()
    dummy = pygame.display.get_driver() == "dummy"
    if current is not None and _fullscreen == enabled:
        return current
    # Never switch between software and scaled renderers on a live window.
    # Keeping SCALED in windowed mode also enables Windows fullscreen toggling.
    if current is not None and _fullscreen is not None and _scaled and not dummy:
        try:
            if not pygame.display.toggle_fullscreen():
                raise pygame.error("Fullscreen toggle unavailable")
            _fullscreen = enabled
            return pygame.display.get_surface()
        except pygame.error:
            pass
    flags = 0 if dummy else pygame.SCALED | (pygame.FULLSCREEN if enabled else 0)
    try:
        screen = pygame.display.set_mode(LOGICAL_SIZE, flags)
        _fullscreen = enabled
        _scaled = not dummy
    except pygame.error:
        screen = pygame.display.set_mode(LOGICAL_SIZE)
        _fullscreen = False
        _scaled = False
    return screen


def is_fullscreen():
    return bool(_fullscreen)


def initialize():
    from game.core.AppConfig import load_settings

    return set_fullscreen(load_settings()["fullscreen"])
