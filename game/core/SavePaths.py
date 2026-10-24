"""Writable per-user save storage, independent of the installation folder."""

import os
import sys
from pathlib import Path


def save_directory():
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share")
    directory = base / "Crown of Courage" / "saves"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


SAVE_DIR = save_directory()
