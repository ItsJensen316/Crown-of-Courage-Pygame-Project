import pygame
from game.core.helper import loadimages

pygame.init()
fps = 120
fpsclock = pygame.time.Clock()
screen = pygame.display.get_surface()
White = (255, 200, 100)
yscroll = 800
scroll = 1
canscroll = False
transparency = 0
Font = pygame.font.Font(None, 30)
mouse_pos = ()
index = 0
counter = 0
counter2 = 0
inventory_held = False
use_held = False
health_gain = {"Mushroom": 1, "Rations": 1, "Apple": 1, "Meat": 2, "Kit": 2}
select_outline = loadimages("assets/art/UI/Inventory_Selection.png", (45, 45))


def player_inventory(Inv, hero, Inv_dict, keys):
    global index, counter, counter2, inventory_held, use_held
    global yscroll
    global scroll
    global canscroll
    global transparency
    Player_Inv = hero.inventory
    Inv_length = len(Player_Inv)
    if canscroll:
        yscroll += 5 * scroll
        transparency += 10 * -scroll
    if transparency < 0:
        transparency = 0
    elif transparency > 255:
        transparency = 255
    if yscroll > 150:
        yscroll = 150
    elif yscroll < 20:
        yscroll = 20
    # The gameplay loop owns the event queue.
    kinput = pygame.key.get_pressed()
    inventory_down = kinput[keys["inventory"]]
    if inventory_down and not inventory_held:
        if yscroll == 20:
            scroll = 1
        elif yscroll == 150:
            scroll = -1
        canscroll = True

    inventory_held = inventory_down
    Inv.set_alpha(transparency)

    if transparency > 0:
        screen.blit(Inv, (0, yscroll))
    k = pygame.key.get_pressed()
    counter2 += 1
    # Consume only a healing item; keys cannot be eaten or lost via Use.
    use_down = k[keys["grab"]]
    if (
        use_down
        and not use_held
        and hero.current_health > 0
        and not getattr(hero, "interaction_used", False)
        and yscroll == 20
    ):
        counter2 = 0
        selected = index + 1
        if selected < len(Player_Inv):
            entry = Player_Inv[selected]
            gain = health_gain.get(entry["name"], 0)
            if gain and entry["quantity"] > 0 and hero.current_health < hero.max_health:
                hero.sounds[
                    "use_potion" if entry["name"] == "Kit" else "use_food"
                ].play()
                entry["quantity"] -= 1
                hero.current_health = min(hero.max_health, hero.current_health + gain)
    use_held = use_down
    if yscroll == 20:
        import game.ui.GameplayText as gameplay_text
        gameplay_text.prompt(
            "Arrows: select item | " + pygame.key.name(keys["grab"]).upper() + ": use"
        )
    for i in range(1, Inv_length):
        P = Player_Inv[i]
        Item_display = Inv_dict[P["name"]]
        Num = P["quantity"]
        Num = str(Num)
        Item_display.set_alpha(transparency)
        if transparency > 0:
            text = Font.render(Num, False, (255, 255, 255))
            text.set_alpha(transparency)
            screen.blit(Item_display, ((i + 2) * 50, (10 * 50) + yscroll))
            screen.blit(text, ((i + 2) * 50, (10 * 50) + yscroll + 25))
    if yscroll == 20:
        counter += 1
        if counter > 20:
            if k[pygame.K_RIGHT] and index < 9:
                counter = 0
                index += 1
            elif k[pygame.K_LEFT] and index > 0:
                counter = 0
                index -= 1
            else:
                counter += 30
        screen.blit(select_outline, ((index + 3) * 50 - 3, (10 * 50) - 3 + yscroll))


def reset_inventory_ui():
    """Close the panel and clear stale selection after a phase load/restart."""
    global yscroll, scroll, canscroll, transparency, index, counter, counter2, inventory_held, use_held
    yscroll = 150
    scroll = 1
    canscroll = False
    transparency = 0
    index = counter = counter2 = 0
    inventory_held = use_held = False


def is_open():
    return yscroll < 150 or (canscroll and scroll == -1)
