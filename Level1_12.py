import pygame
import sys
from Conversation import *
from Game_Char_Copy import *
from Inventory import *
from UI import *
from Puzzle import *
from Old_man import *
import time
import json

pygame.init()
font = pygame.font.SysFont("notomono", 30)
bgmusic = pygame.mixer.music.load(f"Assets/{Level.level_path}/Music.mp3")
FONT_SIZE = 20


def load_conversation(file_name):
    msg = []
    with open(file_name) as file:
        for line in file:
            msg.append(line)
    return msg


### This covers the display of conversation text ####
def print_text(hero, text, pos, speaker):
    font = pygame.font.Font(None, FONT_SIZE)
    text_surface = font.render(
        text, True, (0, 0, 0)
    )  # Change to black (RGB values: 0, 0, 0)
    text_rect = text_surface.get_rect()
    padding = 10
    tail_offset = 20
    box_offset = 50

    if speaker == "player1":
        text_rect.topleft = (
            hero.x - tail_offset - text_rect.width,
            hero.y - text_rect.height - box_offset + 20,
        )
        tail_pos = (text_rect.right, text_rect.bottom)
        tail_end = (tail_pos[0] + tail_offset, tail_pos[1] + tail_offset)
    else:
        text_rect.topright = (
            hero.x + tail_offset + text_rect.width + 100,
            hero.y - text_rect.height - box_offset + 20,
        )
        tail_pos = (text_rect.left, text_rect.bottom)
        tail_end = (tail_pos[0] - tail_offset, tail_pos[1] + tail_offset)
    background_rect = text_rect.inflate(padding, padding)

    pygame.draw.rect(screen, (245, 245, 220), background_rect)
    screen.blit(text_surface, text_rect)
    pygame.draw.polygon(
        screen,
        (245, 245, 220),
        [
            (tail_pos[0], tail_pos[1] - 5),
            (tail_pos[0], tail_pos[1] + 5),
            (tail_end[0], tail_end[1]),
        ],
    )


#### Main Level Function ####
def level2(keys, settings):

    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(settings["volume"] / 100)
    clock = pygame.time.Clock()

    ##############HERO##############

    hero_Dim = (60, 90)
    hero = Players(0, 200, hero_Dim[0], hero_Dim[1], "Assets/Player", keys)

    ##############ENEMY##############


    for all in Level.Enemy:
        Level.Enemies_array.append(
            enemy(
                all["x"] - hero.current_checkpoint_x,
                all["y"] - hero.current_checkpoint_y,
                all["dimension"][0],
                all["dimension"][1],
                all["path"],
                keys,
                all["identity"],
            )
        )
        print(len(Level.Enemies_array))
        print(all["dimension"][0], all["dimension"][1])
    ##    enmy=enemy(Enmy[0]["x"],Enmy[0]["y"],90,90,Enmy[0]["path"],keys)

    byprod = {116: "", 117: "", 118: "", 119: "", 120: ""}
    for i in range(116, 121):
        a = loadimages(f"Assets/Level1/1-1/Extras/Tile_{i}.png", (45, 45))
        byprod[i] = a

    #################################

    ### Parameters for conversation ###
    msg = [
        {
            "i": 0,
            "msg": load_conversation("File1.txt"),
            "meet_status": False,
            "pos": Level.Old_man[0],
        }
    ]
    turn = ""
    conversation = ""
    current_character = 0
    last_update_time = time.time()
    text_speed = 0.05
    collision = False

    ### Function to check meet for conversation
    def check_meet():
        index = 0
        for all in msg:
            if pygame.Rect(hero.x, hero.y, hero.width, hero.height).colliderect(
                pygame.Rect(
                    all["pos"].x, all["pos"].y, all["pos"].width, all["pos"].height
                )
            ):
                return True, index
            index += 1
            return False, index

    ### Displaying all objects on the screen ###
    def draw(object):
        for all in object:
            # print(all)
            try:
                all.update(hero)

            except:
                all.update(Level.tiles, hero)

            ##            if abs(all.x-hero.x)<800:
            all.draw(screen)

    #############BACKGROUND#############

    def bg_scroll():
        # if hero.distance_after_cp<0:
        #     hero.distance_after_cp = 0
        if hero.screen_scroll_X:
            if not hero.slideableBlockCollision:
                hero.distance_after_cp += hero.char_speed
            elif not hero.rest_state:
                hero.distance_after_cp += 1 if hero.char_speed > 0 else 0
        for i in range(len(Level.bg_images)):
            if hero.screen_scroll_X:
                if not hero.slideableBlockCollision:
                    Level.bgx[i] -= hero.char_speed * speed_arr[i]
                elif not hero.rest_state:
                    Level.bgx[i] -= 1 if hero.char_speed > 0 else -1
            elif Level.bgx[i] > -100:
                Level.bgx[i] = -50
            if hero.screen_scroll_Y:
                Level.bgy[i] -= hero.y_scroll_speed * 0.5
            elif Level.bgy[i] > -50:
                Level.bgy[i] = -50
            if hero.current_health <= 0:
                Level.bgx[i] = -50 - hero.current_checkpoint_x * 0.5
                Level.bgy[i] = -50 - hero.current_checkpoint_y * 0.5

                # bg
                # if bgx[i] < -50 or bgx[i] < -50.6:
                #     bgx[i] += screen_scroll_speed
                Level.bgx[i] = -50

            # bgy[i] = -50 - hero.spawn_y * 0.5

    #############INVENTORY#############
    Inv = loadimages("Assets/Inventory.png", (800, 600)).convert_alpha()
    # To be used from json file
    data = {"Mushroom": 2, "Meat": 3, "Apple": 1, "Kit": 4}
    Inv_dict = {}
    for key, value in data.items():
        Inv_dict[key] = loadimages(f"Assets/Food/{value}.png", (40, 40)).convert_alpha()

    ###################################

    #############UI#############
    health = []
    for i in range(0, 13):
        bars = loadimages(f"Assets/UI/Healthbar/{i}.png", (200, 37))
        health.append(bars)

    ############################

    running = True
    down = False
    msg_delay_counter = 0
    lift_timer = 0
    lift_delay = 50
    # print(Level.tiles)
    while running:
        msg_delay_counter += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        kinput = pygame.key.get_pressed()
        if (
            kinput[pygame.K_RETURN]
            and not msg[index - 1]["meet_status"]
            and collision
            and msg_delay_counter > 30
        ):
            msg[index - 1]["i"] += 1
            turn = "player2" if turn == "player1" else "player1"
            current_character = 0
            msg_delay_counter = 0
        collision,index = check_meet()
        if msg[index-1]["i"] == len(msg[index-1]["msg"]) - 1:
            conversation = "finished"
            msg[index - 1]["meet_status"] = True

        mx, my = pygame.mouse.get_pos()
        bg_scroll()
        # Animalsw
        ##      hero.moved(tiles,ladder,food,bgx[0])
        screen.fill((20, 0, 60))
        for i, all in enumerate(Level.bg_images):
            try:
                if i == 1:
                    screen.blit(all, (Level.bgx[0], Level.bgy[0]))
                elif i == 0:
                    screen.blit(all, (Level.bgx[1], Level.bgy[1]))  # Background
            except:
                screen.blit(all, (Level.bgx[0], Level.bgy[0]))
        draw(Level.tiles)
        draw(Level.Slidables)
        draw(Level.Rest)
        draw(Level.CheckP)
        draw(Level.Ladder)
        draw(Level.Button)
        draw(Level.Pushables)
        draw(Level.Damage)
        draw(Level.Food)
        for i, all in enumerate(Level.Lift):
            if  not (145<all.lift_index<=151):
                Level.Lift[i].draw(screen)
            all.update(hero)

        
        lift_collide_list = [is_collide_single([Level.Lift[6]], hero), is_collide_single([Level.Lift[8]], hero),
                             is_collide_single([Level.Lift[11]], hero), is_collide_single([Level.Lift[12]], hero),
                             is_collide_single([Level.Lift[13]], hero), is_collide_single([Level.Lift[14]], hero)]
        lift_un_collide_list = [Level.Lift[0], Level.Lift[1],
                             Level.Lift[2], Level.Lift[3],
                             Level.Lift[4], Level.Lift[5],
                             Level.Lift[7], Level.Lift[9],
                             Level.Lift[10], Level.Lift[15]]
        # print(lift_collide_list)
        hero.inside_lift = any(lift_collide_list)   

              

        # print(Puzzle)
        draw(Level.Puzzle)
        Level.Old_man[0].draw(screen)
        Level.Old_man[0].update(hero)

        button_pressed,btn_index=is_collide(Level.Pushables,Level.Button[0])
        if ((not Level.Button[btn_index].pressed) or hero.inside_lift):
            for i, all in enumerate(Level.Lift):
                if (145<all.lift_index<=151):
                    Level.Lift[i].draw(screen)

        if button_pressed:
            hero.lift_movement_dir = Level.Button[btn_index].lift_direction
            Level.Button[btn_index].pressed=True
        else:
            Level.Button[btn_index].pressed=False
            hero.lift_movement_dir=0



        checkpoint_collision, index = is_collide(Level.CheckP, hero)
        if checkpoint_collision and not Level.CheckP[index].is_activated:
            # hero.current_checkpoint_x = max(hero.current_checkpoint_x, hero.distance_after_cp)
            hero.distance_after_cp = 0
            Level.CheckP[index].is_activated = True
            Level.level_metadata[Level.level_path]["tracker"]["level_checkpoints"][0][
                "inventory"
            ] = hero.inventory
            # print(Level.level_metadata)
            writeFile(Level.level_metadata, "level.json")
        # print(hero.current_checkpoint_x, hero.distance_after_cp, hero.realive)

        puzzle_collision, index = is_collide(Level.Puzzle, hero)
        if puzzle_collision and not Level.Puzzle[index].is_activated:
            running = puzzle11()
            # Level.Puzzle[index].is_activated = True
            if not running:
                break

        for all in Level.Enemies_array:
            if all.enemy_health <= 0:
                if all.can_append:
                    img = byprod[By_product[all.identity]]
                    Level.Food.append(
                        objects(
                            all.x,
                            all.y,
                            tiles_dimension[0],
                            tiles_dimension[1],
                            [img],
                            identity[By_product[all.identity]],
                        )
                    )
                    all.can_append = False

            if abs(all.x - hero.x) < 800:
                all.draw2(screen)
                if all.fight_range:
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
        hero.draw(screen)


        # lift closed portion after hero draw
        if (hero.inside_lift and Level.Button[0].pressed):
            # print(hero.inside_lift
            if lift_timer>=lift_delay:
              
                for i, all in enumerate(Level.Lift):
                    if (145<all.lift_index<=151):
                        Level.Lift[i].draw(screen)
                    all.lift_start=True    

            else:
                lift_timer += 1
           


        # print(Level.bgx[0], Level.bgy[0], -Level.x_limit[1], -Level.y_limit[1])

        ##        temp.talk(screen,hero,food)

        if conversation != "left" and not hero.realive:
            if hero.inside_lift and Level.Button[0].pressed and lift_timer>=lift_delay:
                hero.movement(Level.tiles + Level.Pushables + lift_un_collide_list, Level.Slidables)
            else:
                hero.movement(Level.tiles + Level.Pushables, Level.Slidables)  # 3562
            ##            enmy.enemy_movement(hero,tiles)
            for all in Level.Enemies_array:
                all.enemy_scroll(hero)
                if abs(all.x - hero.x) < 450:
                    all.enemy_movement(hero, Level.tiles)

        else:
            Level.Old_man[0].action = "Idle"
            hero.action = "Idle"
            
            hero.animation()
            ##            enmy.speed2=0
            hero.char_speed = 0
        # check for reac to check points

        if collision:
            conversation = "left"
            if turn == "":
                turn = "player1"
            if current_character < len(msg[index - 1]["msg"][msg[index - 1]["i"]]):
                if time.time() - last_update_time > text_speed:
                    current_character += 1
                    last_update_time = time.time()
            print_text(
                hero,
                msg[index - 1]["msg"][msg[index - 1]["i"]][:current_character],
                (msg[index - 1]["pos"].x, msg[index - 1]["pos"].y - 50),
                "player1" if turn == "player1" else "player2",
            )


        ##########Update Food##########

        hero.isFood, indx = is_collide(Level.Food, hero)
        if hero.isFood:
            text = font.render("Press G to pick up item", False, (255, 255, 255))
            screen.blit(text, (220, 10))
            if kinput[keys["grab"]]:
                available = False
                for all in hero.inventory:
                    if all["name"] == Level.Food[indx].identity:
                        hero.sounds["grab"].play()
                        all["quantity"] += 1
                        available = True

                if not available:
                    hero.inventory.append({"name": Level.Food[indx].identity, "quantity": 1})
                del Level.Food[indx]
        player_inventory(Inv, hero, Inv_dict, keys)
        for i, all in enumerate(hero.inventory):
            if all["quantity"] == 0:
                print(all["name"], all["quantity"])
                del hero.inventory[i]

        ##########Health##########
        healthbar(health, hero.current_health)
        # print(tiles[0].distance_covered, abs(hero.distance_after_cp))
        if hero.current_health <= 0 and hero.index == 10:
            screen.blit(death_screen, (0, 0))
            pygame.display.flip()
            time.sleep(1)
            hero.realive = True
            # print(hero.realive)
            hero.current_health = 2
            if hero.life == 0:
                running = False
        text = font.render(str(int(clock.get_fps())), 1, (255, 255, 255))
        screen.blit(text, (700, 0))
        ##        print((bgx[0]+50)/0.8)
        pygame.display.flip()

        clock.tick(120)  # limits FPS
    return

    pygame.quit()


##level1("")
