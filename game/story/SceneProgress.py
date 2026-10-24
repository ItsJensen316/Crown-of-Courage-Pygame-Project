"""Scenes become replayable only after they have actually been entered."""

import json
from pathlib import Path

SAVE_PATH = Path(__file__).resolve().parents[2] / "saves/scene_progress.json"
SCENES = {"Level1/1-1": 1, "Level1/1-2": 2}


def visited_scenes():
    try:
        data = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
        return sorted(
            {n for n in data.get("visited", []) if type(n) is int and n in (1, 2)}
        )
    except (OSError, ValueError, TypeError, AttributeError):
        return []


def visit_scene(level_path):
    number = SCENES[level_path]
    visited = visited_scenes()
    if number in visited:
        return False
    visited.append(number)
    temporary = SAVE_PATH.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps({"visited": sorted(visited)}, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(SAVE_PATH)
    return True
