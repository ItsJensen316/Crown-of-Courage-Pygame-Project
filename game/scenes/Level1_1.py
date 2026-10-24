"""Scene 1: forest, guide, and tower picture puzzle."""

from game.scenes.Level1_12 import level2, run_phase


def level1(keys, settings):
    result = run_phase(keys, settings, "Level1/1-1")
    if result and result.get("next_phase") == "Level1/1-2":
        return level2(keys, settings, player_state=result)
    return result
