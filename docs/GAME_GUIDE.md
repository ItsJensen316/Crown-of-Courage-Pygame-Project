# Game Guide and Architecture

**Spoiler warning:** this guide explains the full demo progression, encounter outcomes, puzzle completion, and ending.

[Back to the README](../README.md).

A story-driven 2D action platformer built with **Python and Pygame**. A princess leaves her kingdom to rescue her brother from an enemy king, following his captors through a hostile forest and an abandoned tower.

The initial demo contains **two connected scenes in Level 1** and ends when the princess escapes the tower. Her search continues beyond the demo.

## Features

- Side-scrolling exploration with parallax backgrounds, slopes, ladders, moving platforms, and pushable boxes.
- Normal and running sword attacks, timed-release critical hits, and floating combat feedback.
- Patrolling enemies, a 500-HP tower keeper, and thorns and fire that damage both the princess and enemies.
- A nine-piece picture puzzle guarding the tower entrance.
- Food, healing potions, health-capacity and attack-power upgrades, keys, and healing chests.
- Breakable wooden crates with fragment animations and a 15% chance to drop food.
- NPC dialogue, a boss introduction and farewell, and an outdoor epilogue.
- Four illustrated journal pages and scene-replay cards unlocked through exploration.
- Fullscreen and windowed modes, remappable gameplay controls, master volume, low graphics, and an optional FPS counter.
- A pause menu with Resume, Settings, and confirmation before returning to Main Menu.
- Ordered music playlists, a dedicated boss track, and overlapping combat sound effects.

## Run from source

Requires **Python 3.10 or newer** and **Pygame 2.6.1**.

From the project folder:

```bash
python -m pip install -r requirements.txt
python main.py
```

On Windows, `Run_Game.bat` launches the game after dependencies are installed. Keep the media folders and map files alongside the Python modules.

## Controls

Gameplay bindings can be changed in **Settings**.

| Action | Default input |
| --- | --- |
| Move left / right | **A / D** |
| Jump / climb up | **W** |
| Climb down | **S** |
| Sprint / climb faster | **Left Shift** with movement |
| Push a movable box | Walk against it with **A / D** |
| Grip and push / pull a box | Hold **Shift + A / D** while touching its side |
| Attack | **Space** |
| Running attack | **Space** while moving at speed |
| Collect / interact / use selected inventory item | **G** |
| Open / close inventory | **E** |
| Select inventory item | **Left / Right arrow** |
| Talk / advance dialogue | **Enter** |
| Pause / resume | **Escape** |
| Move picture-puzzle pieces | Drag with the **left mouse button** |

Box gripping accepts either Shift key. Inventory selection, dialogue, and menu navigation use fixed keys. The **Climb down / slide** binding controls ladder descent in this demo.

Menus support mouse input. The main menu also supports arrows, Tab, and Enter or Space. Its top-right **X** closes the game. Fullscreen is enabled by default; Settings can toggle it while preserving the 800 × 600 game view.

## Attacks and critical-hit timing

A tap starts a complete normal sword swing. Holding attack repeats swings. Moving quickly when a swing begins selects the running attack.

To perform a critical:

1. **Hold through the windup**, continuously for at least **190 ms before contact**.
2. **Let the sword damage the enemy.** Normal damage happens immediately on contact.
3. **Release within 90 ms after that damage.** A valid release adds an equal damage bonus and displays a floating **“Critical hit!”** message.

| Combat value | Base value |
| --- | --- |
| Normal strike | **24 damage** |
| Critical strike | **48 total damage** |
| Minimum hold before contact | **190 ms** |
| Release window after contact | **90 ms** |
| Successful-critical cooldown | **300 ms** |

Each swing applies its normal damage to an enemy once. Quick taps, releases before contact, and late releases do not qualify for the bonus. The enemy must still be alive and in range when the release is checked. Tapping again during a committed swing cannot skip its windup.

Power potions increase normal and critical damage. Attacking provides no invulnerability, so spacing and choosing when to strike remain important. Timing constants are defined in `game/combat/SwordCombat.py`.

## Story and progression

### Scene 1 — The Forest

**Play** starts a fresh journey. The first playthrough presents the opening journal page before entering the forest.

Explore its platforms and hazards, gather supplies, and talk to the old man beside his hut. He points the princess toward the abandoned castle and explains the sealed tower entrance. Reassemble the nine-piece picture at the entrance to continue into Scene 2.

When transitioning directly into Scene 2, current health, maximum health, attack power, keys, and inventory carry over.

### Scene 2 — Inside the Tower

Navigate ladders, moving platforms, slopes, flames, and thorns. The keeper confronts the princess in a sealed arena. His music starts with his opening dialogue; the ladder escape stays blocked until his farewell ends.

The keeper has **500 HP** and drops a healing potion at half health. After defeat, he regrets his actions and directs the princess to the elevator. Move the box onto the pressure switch to keep the lift powered, ride it upward, and step outside to finish the demo.

### Scene selection and Story Journal

Both scene cards start locked, greyed out, and without pictures. Visiting a scene unlocks its card for replay. Replaying starts that scene with fresh gameplay state.

The journal begins empty and gains four illustrated pages:

| Page | Unlock | Illustration |
| --- | --- | --- |
| A sister's promise | First Play | The princess in the forest |
| The forest guide | Finish the old man's conversation | The princess, old man, hut, and well |
| The tower keeper | Finish the defeated keeper's farewell | The battle in the tower chamber |
| Beyond the tower | Leave after the elevator ride | The elevator and the world outside |

A brief notification announces each new page. Journal pages and visited scenes remain unlocked after deaths, replays, and restarts.

## Items and survival

Press **G** near a collectible to pick it up. Food and healing potions enter the inventory. Open it with **E**, choose an item with the arrows, and press **G** to consume it. Consumables are used only when they can restore missing health.

| Item | Effect |
| --- | --- |
| Mushroom, rations, apple | Restore **1 health slot** |
| Meat | Restore **2 health slots** |
| Healing potion | Restore **2 health slots** |
| Health-capacity Special Potion | Add **1 maximum-health slot**, without healing current damage |
| Attack-power Special Potion | Add **25% of base attack power** per pickup |
| Key | Unlock one healing chest |
| Healing chest | Consume one key and restore full health |

The princess begins with **6 health slots**. Special Potions require manual collection and take effect immediately. Upgrades carry into the next scene during a continuous journey and reset when starting or retrying a scene.

Wooden crates break when struck and each has a **15% chance** to drop a mushroom, ration, or apple. Defeated enemies also drop supplies. Drops require manual collection.

Thorns and fire deal gradual damage. Enemies lose **10 HP per hazard tick**, approximately once per second at the target frame rate. Overlapping hazard tiles do not multiply the tick. Damage flashes and combat effects indicate hits.

## Pause, death, and local progress

**Escape** pauses gameplay. Settings can be opened while paused. Main Menu requires confirmation because progress in the current scene will reset. Music continues through pause, Settings, and the picture puzzle.

Combat and pit deaths play the full death sound before accepting a fresh key or click to retry. The **YOU DIED** screen does not restart automatically. Retrying rebuilds the scene with fresh health, enemies, pickups, and inventory, including resetting carried upgrades and supplies.

There is **no mid-scene save/resume**. Discoveries and preferences are saved in automatically created files in `saves/`:

| File | Saved information |
| --- | --- |
| `saves/scene_progress.json` | Visited scenes available for replay |
| `saves/story_progress.json` | Unlocked journal pages |
| `saves/setting.json` | Volume, fullscreen, low graphics, and FPS preferences |
| `saves/control_key.json` | Custom gameplay bindings |

These files are excluded from Git. Removing the progress files resets discovery; removing preference files restores defaults.

## Audio

| Context | Playback |
| --- | --- |
| Main menu | `assets/audio/Music1.mp3` → `assets/audio/Music2.mp3` → repeat |
| Forest | `assets/audio/Level1/1-1/Music.mp3`, looping |
| Tower | `assets/audio/Level1/1-2/Music1.mp3` → `Music2.mp3` → repeat |
| Keeper introduction and battle | `assets/audio/Boss/Music.mp3`, looping |

The tower playlist resumes on the keeper's defeat. Death stops background music so its sound can finish.

Effects in `assets/audio/` include random hurt and jump variants, potion and food-use sounds, sword swings and impacts, pickups, and death. Damage, swings, and impacts use independent channels so they can overlap.

## Project structure

| Files | Responsibility |
| --- | --- |
| `main.py`, `game/ui/MenuUI.py`, `game/ui/Levels.py`, `game/ui/settings.py`, `game/ui/PauseMenu.py` | Entry point, menus, scene selection, and preferences |
| `game/scenes/Level1_1.py`, `game/scenes/Level1_12.py` | Scene entry points, transitions, and shared gameplay loop |
| `game/actors/Game_Char_Copy.py`, `game/combat/SwordCombat.py`, `game/actors/EnemyPatrol.py`, `game/combat/TowerBoss.py` | Characters, combat, enemy behavior, and boss encounter |
| `game/world/Camera.py`, `game/world/CollisionGrid.py`, `game/world/Slopes.py` | Camera tracking, collision lookup, and terrain geometry |
| `game/world/TowerMechanics.py`, `game/world/Pushable.py`, `game/world/Slidable.py`, `game/world/Lift.py`, `game/world/Button_switch.py` | Hazards, platforms, boxes, elevator, and switches |
| `game/items/Inventory.py`, `game/items/ItemSprites.py`, `game/items/SpecialItems.py`, `game/world/BreakableCrate.py`, `game/ui/UI.py` | Inventory, collectibles, upgrades, crates, and health display |
| `game/story/Dialogue.py`, `game/actors/Old_man.py`, `game/story/Story.py`, `game/story/StoryArt.py` | Conversations and illustrated journal |
| `game/story/SceneProgress.py`, `game/story/StoryProgress.py`, `game/core/AppConfig.py` | Discoveries and settings persistence |
| `game/audio/MusicPlayer.py`, `game/audio/SoundEffects.py`, `game/ui/DeathScreen.py`, `game/core/DisplayMode.py` | Audio, death flow, and display modes |
| `game/core/helper.py`, `game/core/Level_manager.py`, `game/world/Object.py`, `game/world/TowerLock.py`, `game/world/WallLamp.py`, `game/ui/GameplayText.py` | Loading, shared world objects, and gameplay presentation |
| `data/maps/Level11.csv`, `data/maps/Level12.csv` | Scene maps |
| `data/config/level.json`, `data/config/course_design.json`, `data/dialogue/` | Scene metadata, mechanic parameters, and dialogue content |
| `assets/art/`, `assets/puzzles/Gate_Puzzle/`, `assets/audio/` | Artwork, puzzle pieces, and audio |

Concept and development by **[Jensen Jose](https://github.com/ItsJensen316)** and **[doTryCatch](https://github.com/doTryCatch)**.

Asset attributions: [Credits](../CREDITS.md).

## Architecture and physics

### Scene loop

`main.py` opens the menu. `Level1_1.level1()` starts the forest through the shared `run_phase()` loop in `game/scenes/Level1_12.py`. A successful entrance puzzle returns a state dictionary; the wrapper passes it into Scene 2. A death returns a retry flag, rebuilding the same scene with fresh player state. The two scenes share loading, rendering, collision, inventory, dialogue, hazards, and UI code.

Maps are CSV grids using 45-pixel cells. `helper.start_level()` rebuilds the shared `Level` object from the map and metadata. Tile ranges select terrain, ladders, collectibles, actors, platforms, and mechanisms. `data/config/level.json` and `data/config/course_design.json` are static configuration; discoveries and preferences use separate local save files.

### Coordinates and camera

Actors and world objects retain screen-space coordinates. `Camera.follow()` maintains the camera's world offset and translates every world object by the same delta once per frame. Adding that offset recovers world coordinates. `CollisionGrid` indexes static terrain in world space and returns nearby candidates for exact collision checks.

Terrain is baked into a surface at scene load. The camera draws a viewport from that surface, while animated actors and objects are drawn separately. Background layers use independent parallax rates. A vertical dead zone and exponential easing keep ordinary jumps from moving the entire view abruptly.

### Movement and collision

Horizontal motion accelerates toward walk or sprint speed and slows after release. The grounded jump applies a short upward acceleration while the jump button remains held; gravity then pulls the princess down. Most gameplay simulation targets 120 updates per second. Movement, animation counters, and hazard tick cooldowns are largely frame-based; critical input windows and sound completion use elapsed time.

Horizontal collision resolves against wall faces. Vertical collision detects crossings of floors or ceilings and snaps to the contact surface. `Slopes.surface_y()` calculates the support height over a diagonal ramp. One-way platforms permit passage from below and support descending actors from above. Moving platforms apply their displacement to a rider standing on their deck, maintaining grounded animation state.

Ladders replace normal falling with controlled vertical movement. Dialogue and death disable normal control but continue passive downward collision resolution. The elevator explicitly positions its rider while its closing, ascending, and opening sequence runs.

### Boxes, switches, and encounter boundaries

Pushable boxes check adjacent terrain and resolve gravity and slope support. Gripping a contacted box binds the princess's movement and facing to it; pulling reuses backward walking frames. A pressure switch detects a supported hero or box. Leaving a box on the switch keeps the elevator enabled during the ride.

The keeper encounter owns its introduction, camera framing, arena barriers, half-health reward, farewell, and journal unlock. Ladder access is blocked while the encounter is active, then restored after the farewell. The elevator exit triggers the final journal page and epilogue.

### Combat and presentation

`game/combat/SwordCombat.py` tracks committed swing cycles. A target receives normal damage once per cycle at its contact animation frame. Eligibility for a critical is captured at that contact: a sufficiently long continuous hold followed by a valid release adds one equal bonus. The cooldown prevents immediate repeated criticals. This replaces the earlier lingering-hit behavior; the critical popup reports a confirmed bonus.

The player's logical body stays fixed when a wider attack frame is mirrored. Death frames use a common scale and foot anchor. Damage tints are applied to copies of animation surfaces so cached source frames remain unchanged.

`MusicPlayer` streams and queues ordered tracks through a shared end event, including during modal screens. `SoundEffects` caches effects and reserves separate channels for hurt, swing, and impact feedback. The death screen stops other playback, runs falling and animation, then waits for the sound and a fresh retry input.

### Persistence and scope

Scene and journal JSON files record discoveries, not a complete world snapshot. Settings and remapped controls are also local. Collectibles, enemy state, puzzle state, upgrades, and inventory are session state and reset on retry. The demo currently contains one level with two scenes; it does not implement a later level or a complete campaign.
