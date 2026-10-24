# Crown of Courage: A Princess's Quest

A pixel-art action platformer about a princess searching for her captured brother. Explore a dangerous forest, uncover the secrets of an abandoned tower, and keep moving toward the unknown.

Built with **Python and Pygame**. The initial demo includes two connected scenes.

## Gameplay

![Gameplay montage](docs/media/gameplay-preview.gif)

[Watch the short gameplay montage](https://github.com/user-attachments/assets/a705e4c6-acfb-444d-aae9-0528dff1b600)

| Forest exploration | Inside the tower |
| --- | --- |
| ![Exploring the forest](docs/media/forest.png) | ![Moving platforms inside the tower](docs/media/platforms.png) |

## Features

- Exploration, platforming, and environmental puzzles.
- Sword combat, running attacks, and timed critical hits.
- Enemies and a **boss fight**.
- Collectibles, upgrades, inventory, and an illustrated story journal.
- Fullscreen, remappable controls, saved discoveries, and a pause menu.

## Play on Windows

[**Download the Windows demo installer — v1.0.0**](https://github.com/ItsJensen316/Crown-of-Courage-Pygame-Project/releases/download/v1.0.0/Crown-of-Courage-Setup-1.0.0.exe)

Run the installer, then launch **Crown of Courage** from the Start Menu or desktop shortcut. **Python is not required.**

## Run from source

Requires **Python 3.10+**.

```bash
python -m pip install -r requirements.txt
python main.py
```

Windows users can also launch through `Run_Game.bat` after installing the requirements.

## Controls

| Action | Default control |
| --- | --- |
| Move / jump / climb | **A / D**, **W / S** |
| Sprint / grip a box | **Shift** |
| Attack | **Space** |
| Collect / interact / use | **E** |
| Inventory / select item | **Q**, **Left / Right arrows** |
| Dialogue / pause | **Enter**, **Escape** |

For a critical hit, hold through the swing, let the sword connect, then release promptly. Gameplay bindings can be changed in Settings.

## Progress and settings

Scene discoveries, journal pages, settings, and controls are saved in `%LOCALAPPDATA%\Crown of Courage\saves\` on Windows. There is no mid-scene save/resume.

Use **Settings → Reset progress** to clear discoveries while keeping your preferences. **Restore defaults** resets settings and controls separately. Volume sliders control Main, Music, and Others (sound effects).

## Created together

**[Jensen Jose](https://github.com/ItsJensen316)** and **[Roshan Kumar Patel](https://github.com/doTryCatch)** developed the idea and built the game together, sharing ideas, design decisions, and implementation.

## More

- [Game guide and architecture](docs/GAME_GUIDE.md) — detailed mechanics, progression, architecture, and spoilers.
- [Credits](CREDITS.md) — artwork, animation, and sound-effect sources.
