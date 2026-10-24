import time
from copy import deepcopy

import game.ui.GameplayText as gameplay_text
import game.items.Inventory as inventory_ui
import game.audio.MusicPlayer as music
import pygame
from game.core.AppConfig import apply_audio_settings, gameplay_keys, load_settings
from game.world.Camera import Camera
from game.world.CollisionGrid import CollisionGrid
from game.ui.DeathScreen import show_death
from game.story.Dialogue import GuideDialogue
from game.actors.Game_Char_Copy import Players, enemy, is_collide
from game.core.helper import (
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    By_product,
    Level,
    load_backgrounds,
    loadimages,
    readFile,
    screen,
    start_level,
)
from game.items.Inventory import player_inventory
from game.items.ItemSprites import DISPLAY_NAMES, INVENTORY_TILES, Collectible, item_icon, key_icon
from game.ui.PauseMenu import pause_menu
from game.world.Pushable import pushableObject
from game.story.Puzzle import puzzle11
from game.story.SceneProgress import visit_scene
from game.items.SpecialItems import SpecialItems
from game.story.StoryProgress import draw_notification
from game.story.StoryProgress import unlock as unlock_story
from game.combat.TowerBoss import KeeperEncounter, TowerKeeper
from game.world.TowerMechanics import (
    HazardDamage,
    TowerElevator,
    configure_platforms,
    show_demo_end,
    show_loading,
)
from game.ui.UI import DynamicHealthBar

pygame.init()
font = pygame.font.SysFont("notomono", 30)


def _play_phase(keys, settings, level_path="Level1/1-1", player_state=None):
    loading_started = pygame.time.get_ticks()
    if level_path == "Level1/1-2":
        show_loading()
    start_level(level_path, backgrounds=not settings.get("low_graphics", False))
    inventory_ui.reset_inventory_ui()
    scene_title = (
        "Scene 1 — The Forest"
        if level_path == "Level1/1-1"
        else "Scene 2 — Inside the Tower"
    )
    pygame.display.set_caption("Crown of Courage — " + scene_title)
    music.start(level_path, settings["volume"])
    clock = pygame.time.Clock()

    hero_Dim = (60, 90)
    spawn = Level.hero_pos or ((1, 10) if level_path == "Level1/1-1" else (1, 6))
    hero = Players(
        spawn[0] * 45, spawn[1] * 45, hero_Dim[0], hero_Dim[1], "assets/art/Player", keys
    )
    if player_state:
        hero.inventory = deepcopy(player_state["inventory"])
        hero.max_health = player_state.get("max_health", 6)
        hero.attack_power = player_state.get("attack_power", 1.0)
        hero.keys_count = player_state.get("keys_count", 0)
        hero.current_health = min(hero.max_health, player_state["health"])
        hero.life = player_state["life"]
    visit_scene(level_path)
    apply_audio_settings(settings)

    camera = Camera(Level)
    collision_grid = CollisionGrid(Level.tiles, camera)
    if camera.goal_rect is not None:
        # Keep the map intact, but retire its old mid-level puzzle marker.
        Level.Puzzle.clear()

    course_rules = readFile("data/config/course_design.json").get(level_path, {})
    configure_platforms(Level, course_rules)
    hazards = HazardDamage()
    elevator = TowerElevator(Level.Lift, course_rules)
    patrols = course_rules.get("enemy_patrol_steps", {})
    for entry in Level.Enemy:
        foe_type = (
            TowerKeeper
            if level_path == "Level1/1-2" and entry["identity"] == "Orc_Shaman"
            else enemy
        )
        foe = foe_type(
            entry["x"] - hero.current_checkpoint_x,
            entry["y"] - hero.current_checkpoint_y,
            entry["dimension"][0],
            entry["dimension"][1],
            entry["path"],
            keys,
            entry["identity"],
        )
        foe.roaming_range = patrols.get(str(round(entry["x"] / 45)), foe.roaming_range)
        Level.Enemies_array.append(foe)

    keeper = next(
        (foe for foe in Level.Enemies_array if isinstance(foe, TowerKeeper)), None
    )
    dialogue = KeeperEncounter(keeper, camera, Level) if keeper else GuideDialogue()
    story_npcs = Level.Old_man if level_path == "Level1/1-1" else []

    def draw(object):
        for all in object:

            if not dialogue.active:
                if isinstance(all, pushableObject):
                    all.update(collision_grid.near(all, margin=32), hero)
                else:
                    all.update(hero)

            if (
                all.x + all.width >= -60
                and all.x <= SCREEN_WIDTH + 60
                and all.y + all.height >= -60
                and all.y <= SCREEN_HEIGHT + 60
            ):
                if getattr(all, "tile_id", None) in (173, 174):
                    special_items.draw_chest(screen, all)
                else:
                    all.draw(screen)

    Inv = loadimages("assets/art/Inventory.png", (800, 600)).convert_alpha()
    Inv_dict = {
        name: item_icon(tile_id, 32).copy() for name, tile_id in INVENTORY_TILES.items()
    }

    Inv_dict["Key"] = key_icon(32)

    health = DynamicHealthBar()
    special_items = SpecialItems(Level)

    if level_path == "Level1/1-2":
        while pygame.time.get_ticks() - loading_started < 450:
            pygame.event.pump()
            clock.tick(60)
    running = True
    puzzle_cooldown = 0

    while running:
        gameplay_text.begin()
        dialogue.update(hero, story_npcs)
        if not dialogue.active or camera.locked_position is not None:
            camera.follow(hero, Level)
        puzzle_cooldown = max(0, puzzle_cooldown - 1)
        for event in pygame.event.get():
            if music.handle_event(event):
                continue
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_started = time.perf_counter()
                if pause_menu(screen) == "main_menu":
                    music.stop()
                    return {"main_menu": True}
                if dialogue.active:
                    dialogue._started += time.perf_counter() - pause_started
                camera._follow_time = time.perf_counter()
                settings.clear()
                settings.update(load_settings())
                keys.clear()
                keys.update(gameplay_keys())
                if not settings.get("low_graphics", False) and not Level.bg_images:
                    Level.bg_images = load_backgrounds("assets/art/Backgrounds")
                apply_audio_settings(settings)
                continue
            if dialogue.handle_event(event, hero, story_npcs):
                if story_npcs and dialogue.completed:
                    unlock_story(2)
                continue

        if settings.get("low_graphics", False):
            screen.fill((16, 24, 24) if level_path == "Level1/1-1" else (26, 26, 36))
        else:
            camera.draw_backgrounds(screen, Level)
        camera.draw_terrain(screen)
        if keeper:
            dialogue.draw_gates(screen)
        draw(Level.Slidables)
        draw(Level.Rest)
        draw(Level.CheckP)
        draw(Level.Ladder)
        draw(Level.Pushables)
        draw(Level.Damage)
        if not dialogue.active:
            elevator.update(hero, Level.Button, Level.Pushables)
        for marker in Level.Button:
            if getattr(marker, "is_tower_lock", False):
                marker.unlocked = camera.goal_solved
                if (
                    not dialogue.active
                    and not marker.unlocked
                    and abs(hero.x + hero.width / 2 - marker.x - marker.width / 2) < 180
                    and abs(hero.y - marker.y) < 120
                ):
                    gameplay_text.prompt("Tower locked — solve the entrance puzzle")
        draw(Level.Button)
        elevator.draw_back(screen, camera.y)
        draw(Level.Puzzle)
        for old_man in Level.Old_man:
            old_man.update(hero)
            old_man.draw(screen)

        checkpoint_collision, index = is_collide(Level.CheckP, hero)
        if (
            not dialogue.active
            and checkpoint_collision
            and not Level.CheckP[index].is_activated
        ):

            hero.distance_after_cp = 0
            Level.CheckP[index].is_activated = True

        # At the tower, open once per contact. Cancelling requires leaving
        # the doorway and touching it again; a solved puzzle stays solved.
        if hero.current_health > 0 and not dialogue.active and camera.enter_goal(hero):
            camera.goal_solved = puzzle11()
            if camera.goal_solved:
                show_loading()
                music.stop()
                return {
                    "next_phase": "Level1/1-2",
                    "inventory": deepcopy(hero.inventory),
                    "health": hero.current_health,
                    "max_health": hero.max_health,
                    "attack_power": hero.attack_power,
                    "keys_count": hero.keys_count,
                    "life": hero.life,
                }
            pygame.display.set_caption("Crown of Courage — " + scene_title)
            clock.tick(120)
        elif not dialogue.active and camera.goal_rect is None:
            puzzle_collision, index = is_collide(Level.Puzzle, hero)
            if (
                puzzle_collision
                and not Level.Puzzle[index].is_activated
                and not puzzle_cooldown
            ):
                Level.Puzzle[index].is_activated = puzzle11()
                puzzle_cooldown = 120

        for all in Level.Enemies_array:
            if all.enemy_health <= 0 and getattr(all, "death_ready", True):
                if all.can_append:
                    Level.Food.append(
                        Collectible(
                            all.x + (all.width - 45) / 2,
                            all.y + all.height - 45,
                            By_product[all.identity],
                        )
                    )
                    all.can_append = False

            if -all.width <= all.x <= screen.get_width() or abs(all.x - hero.x) < 800:
                all.draw2(screen)
                if all.fight_range and not dialogue.active:
                    all.go_for_attack(hero)
        if hero.action in "RunDrift":
            hero.img_size = (75, 90)
        elif hero.action == "Attack" and 4 < hero.index < 8:
            hero.img_size = (105, 90)
        elif hero.action == "Dash_Attack":
            if 1 < hero.index < 7:
                hero.img_size = (90, 90)
            else:
                hero.img_size = (70, 90)
        else:
            hero.img_size = (60, 90)
        draw(Level.Boxes)
        Level.Boxes[:] = [
            box for box in Level.Boxes if not getattr(box, "finished", False)
        ]
        death_backdrop = None
        if (
            hero.current_health <= 1
            or hero.y + camera.y + hero.height >= camera.bounds.bottom - 30
        ):
            death_backdrop = screen.copy()
        hero.draw(screen)
        elevator.draw_doors(screen)

        if not dialogue.active and not hero.realive and not elevator.locked:
            arena_barriers = dialogue.barriers if keeper else []
            hero.blocked_ladders = dialogue.blocked_ladders if keeper else []
            hero.movement(
                collision_grid.near(hero)
                + Level.Pushables
                + elevator.floors
                + elevator.barriers
                + arena_barriers,
                Level.Slidables,
            )
            for block in Level.Pushables:
                block.finish_drag(hero)
            hazards.update(hero, Level.Damage)
            hazards.update_enemies(Level.Enemies_array, Level.Damage)
            for all in Level.Enemies_array:
                if -all.width <= all.x <= screen.get_width() or abs(all.x - hero.x) < 450:
                    all.enemy_movement(
                        hero,
                        collision_grid.near(all, margin=max(24, all.width))
                        + arena_barriers,
                    )

        else:
            for old_man in Level.Old_man:
                old_man.action = "Idle"
            hero.action = "Idle"

            hero.animation()

            hero.char_speed = 0
            if dialogue.active and not elevator.locked:
                hero.passive_fall(
                    collision_grid.near(hero)
                    + Level.Pushables
                    + elevator.floors
                    + elevator.barriers
                    + (dialogue.barriers if keeper else []),
                    Level.Slidables,
                )
        if elevator.reached_exit(hero):
            unlock_story(4)
            music.stop()
            show_demo_end(hero)
            return {"demo_complete": True}
        # Pickups are the final world layer, above actors and scenery.
        # Inventory, dialogue, and the HUD are drawn afterward.
        special_items.draw_glows(screen)
        draw(Level.Inventory)
        draw(Level.Food)
        hero.interaction_used = False
        special_items.update(
            screen,
            hero,
            keys,
            enabled=not dialogue.active
            and not elevator.locked
            and not inventory_ui.is_open(),
        )

        hero.isFood, indx = is_collide(Level.Food, hero)
        if (
            hero.isFood
            and not dialogue.active
            and not elevator.locked
            and not inventory_ui.is_open()
        ):
            label = DISPLAY_NAMES.get(Level.Food[indx].identity, "item")
            button = pygame.key.name(keys["grab"]).upper()
            gameplay_text.prompt(f"Press {button} to collect {label}")
            if special_items.interact_pressed and not hero.interaction_used:
                hero.interaction_used = True
                hero.sounds["grab"].play()
                available = False
                for all in hero.inventory:
                    if all["name"] == Level.Food[indx].identity:
                        all["quantity"] += 1
                        available = True

                if not available:
                    hero.inventory.append(
                        {"name": Level.Food[indx].identity, "quantity": 1}
                    )
                del Level.Food[indx]
        if not dialogue.active:
            player_inventory(Inv, hero, Inv_dict, keys)
        for i, all in enumerate(hero.inventory):
            if all["quantity"] == 0:
                del hero.inventory[i]

        fell_into_pit = hero.y + camera.y >= camera.bounds.bottom
        if fell_into_pit or hero.current_health <= 0:
            hero.current_health = 0
            show_death(
                screen,
                hero,
                death_backdrop if death_backdrop is not None else screen.copy(),
                pit=fell_into_pit,
                tiles=Level.tiles
                + Level.Pushables
                + elevator.floors
                + elevator.barriers
                + (dialogue.barriers if keeper else []),
                slidables=Level.Slidables,
            )
            return {"restart_phase": True}
        health.draw(screen, hero.current_health, hero.max_health)
        hazards.draw(screen)
        elevator.draw_status(screen, hero)
        for foe in Level.Enemies_array:
            foe.draw_critical_text(screen)
        dialogue.draw(screen, hero, story_npcs)
        if settings.get("show_fps", False):
            text = font.render(
                str(int(clock.get_fps())) + " FPS", True, (231, 234, 222)
            )
            screen.blit(text, text.get_rect(topright=(screen.get_width() - 20, 12)))
        gameplay_text.draw(screen)
        draw_notification(screen)

        pygame.display.flip()

        clock.tick(120)  # limits FPS
    music.stop()
    return


def run_phase(keys, settings, level_path="Level1/1-1", player_state=None):
    """Restart a fallen phase with fresh actors, pickups, inventory, and camera."""
    while True:
        result = _play_phase(keys, settings, level_path, player_state)
        if result and result.get("restart_phase"):
            player_state = None
            continue
        return result


def level2(keys, settings, player_state=None):
    """Start Scene 2 inside the abandoned tower."""
    return run_phase(keys, settings, "Level1/1-2", player_state)
