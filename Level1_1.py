import pygame
import sys
from Conversation import *
from Game_Char_Copy import *
from Inventory import *
from UI import *
import time
import json
pygame.init()
font = pygame.font.SysFont("notomono", 30)
bgmusic=pygame.mixer.music.load('Assets/{level_path}/Music.mp3')

FONT_SIZE = 20
def load_conversation(file_name): 
        msg = []
        with open(file_name) as file:
            for line in file:
                msg.append(line)
        return msg
    
def print_text(hero,text, speaker):
    font = pygame.font.Font(None, FONT_SIZE)
    text_surface = font.render(text, True, (0, 0, 0))  # Change to black (RGB values: 0, 0, 0)
    text_rect = text_surface.get_rect()
    padding = 10
    tail_offset = 20
    box_offset = 50

    if speaker == "player1":
        text_rect.topleft = (hero.x - tail_offset - text_rect.width, hero.y - text_rect.height - box_offset+20)
        tail_pos = (text_rect.right, text_rect.bottom)
        tail_end = (tail_pos[0] + tail_offset, tail_pos[1] + tail_offset)
    else:
         text_rect.topright = (hero.x + tail_offset + text_rect.width+100, hero.y - text_rect.height - box_offset+20)
         tail_pos = (text_rect.left, text_rect.bottom)
         tail_end = (tail_pos[0] - tail_offset, tail_pos[1] + tail_offset)
    background_rect = text_rect.inflate(padding, padding)
     
    pygame.draw.rect(screen, (245, 245, 220), background_rect)
    screen.blit(text_surface, text_rect)
    pygame.draw.polygon(screen, (245, 245, 220), [(tail_pos[0], tail_pos[1] - 5), 
                                         (tail_pos[0], tail_pos[1] + 5), 
                                         (tail_end[0], tail_end[1])])

def level1(keys,settings):
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(settings["volume"]/100)
    clock = pygame.time.Clock()
    
    
    # print(Enmy,others)
    
    ##############HERO##############
    hero_Dim=(60,90)
    hero=Players(0,450,hero_Dim[0],hero_Dim[1],"Assets/Player",keys)
    

    ##############ENEMY##############
    Enemies=[]
    for all in Enmy:
        Enemies.append(enemy(all["x"]-hero.spawn_x,all["y"]-hero.spawn_y,90,90,all["path"],keys,all["identity"]))
            
##    enmy=enemy(Enmy[0]["x"],Enmy[0]["y"],90,90,Enmy[0]["path"],keys)
    old_man=enemy(Enmy[0]["x"],Enmy[0]["y"],60,90,Enmy[0]["path"],keys,Enmy[0]["identity"])
    byprod={116:"",117:"",118:"",119:"",120:""}
    for i in range(116,121):
        a=loadimages(f"Assets/{level_path}/Extras/Tile_{i}.png",(45,45))
        byprod[i]=a
    #################################

    
    #parameters for conversatition
    msg = [{"i":0,"msg":load_conversation("File1.txt"),"meet_status":False,"pos":old_man}]
    turn = ""
    conversation = ""
    current_character = 0
    last_update_time = time.time()
    text_speed = 0.05
    collision=False

    def draw(object):
        for all in object:
            all.update(hero)
##            if abs(all.x-hero.x)<800:
            all.draw(screen)
     # function to check meet for conversatition
    def check_meet():
          
          index=0
          for all in msg:
            if pygame.Rect(hero.x, hero.y, hero.width, hero.height).colliderect(pygame.Rect(all["pos"].x, all["pos"].y, all["pos"].width, all["pos"].height)):
                return True,index
            index+=1
          return False,index

        
    #############BACKGROUND#############
    performance=True
    if performance:
        bgimg=loadimages(f"Assets/{level_path}/Tile_0.png",(8000,600)).convert()
    else:
        bgimg=loadimages(f"Assets/{level_path}/Tile_0.png",(8000,600))
    bgimg2=loadimages(f"Assets/{level_path}/Background2.png",(8000,600)).convert()
    death_screen=loadimages("Assets/Death_screen.png",(800,600))
    B1x=(-50-hero.spawn_x)*0.8
    B2x=(-50-hero.spawn_x)*0.5

    
    #############INVENTORY#############
    Inv=loadimages("Assets/Inventory.png",(800,600)).convert_alpha()
    #To be used from json file
    data={"Mushroom":2,"Meat":3,"Apple":1,"Kit":4}
    Inv_dict={}
    for key,value in data.items():
        Inv_dict[key]=loadimages(f'Assets/Food/{value}.png',(40,40)).convert_alpha()
              
    ###################################


        
    #############UI#############
    health=[]
    for i in range(0,13):
        bars=loadimages(f"Assets/UI/Healthbar/{i}.png",(200,37))
        health.append(bars)
        
    ############################

    running =True
    


    down=False
    msg_delay_counter=0
    while running:
        msg_delay_counter+=1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        kinput = pygame.key.get_pressed()     
        if kinput[pygame.K_RETURN] and not msg[index-1]["meet_status"] and collision and msg_delay_counter>30:
            msg[index-1]["i"] += 1
            turn = "player2" if turn == "player1" else "player1"
            current_character = 0
            msg_delay_counter=0

         
        collision,index = check_meet()
      
##        print(msg[index-1]["i"],len(msg[index-1]["msg"])-1)
        if msg[index-1]["i"] == len(msg[index-1]["msg"]) - 1:
           
            conversation = "finished"
            msg[index-1]["meet_status"]=True
          
        mx,my=pygame.mouse.get_pos()

        
        if hero.screen_scroll_X:
            B1x-=hero.char_speed*0.8
            B2x-=hero.char_speed*0.5
        elif B1x>-100:
            B1x=-50
            B2x=-50
        #Animalsw
##      hero.moved(tiles,ladder,food,B1x)
        screen.blit(bgimg2,(B2x,0))    #Background1
        screen.blit(bgimg,(B1x,0))   #Background2
        draw(tiles)
        draw(others)
        draw(CheckP)
        draw(ladder)   #Hero
        draw(food)
##        enmy.draw(screen)
##        enmy.draw_enemy(screen)
        old_man.draw(screen)
        for all in Enemies:
            if all.enemy_health<=0:
                if all.can_append:
                    img=byprod[By_product[all.identity]]
                    Food.append(objects(all.x,all.y,tiles_dimension[0],tiles_dimension[1],[img],identity[By_product[all.identity]]))
                    all.can_append=False
                
            if abs(all.x-hero.x)<800:
                all.draw2(screen)
                if all.fight_range:
                    all.go_for_attack(hero)
        if hero.action in "RunDrift":
            hero.img_size=(75,90)
        elif hero.action=="Attack" and 4<hero.index<8:
            hero.img_size=(105,90)
        elif hero.action=="Dash_Attack":
            if 1<hero.index<7:
                hero.img_size=(90,90)
            else:
                hero.img_size=(70,90)
        else:
            hero.img_size=(60,90)
        hero.draw(screen)
        
##        temp.talk(screen,hero,food)
            
        if conversation != "left":
            hero.movement(tiles,(B1x,0),(5672,0),600) #3562
##            enmy.enemy_movement(hero,tiles)
            for all in Enemies:
                all.enemy_movement(hero,tiles)
        
        else:
            old_man.action="Idle"
            hero.action="Idle"
            old_man.animation()
            hero.animation()
##            enmy.speed2=0
            hero.char_speed=0

        if collision:
            conversation = "left"
            if turn == "":
                turn = "player1"
            if current_character < len(msg[index-1]["msg"][msg[index-1]["i"]]):
                if time.time() - last_update_time > text_speed:
                    current_character += 1
                    last_update_time = time.time()
            print_text(hero,msg[index-1]["msg"][msg[index-1]["i"]][:current_character], "player1" if turn == "player1" else "player2")


        if hero.screen_scroll_X:
           old_man.x-=hero.char_speed
           
        
            
        ##########Update Food##########
           
        hero.isFood,indx=is_collide(Food,hero)
        if hero.isFood:
            text = font.render("Press G to pick up item", False, (255,255,255))
            screen.blit(text, (220,10))
            if kinput[keys["grab"]]:
                available=False
                for all in hero.inventory:
                    if all["name"]==Food[indx].identity:
                        hero.sounds["grab"].play()
                        all["quantity"]+=1
                        available=True
                        
                if not available:
                    hero.inventory.append({"name":Food[indx].identity,"quantity":1}) 
                del Food[indx]
        player_inventory(Inv,hero,Inv_dict,keys)
        for i,all in enumerate(hero.inventory):
            if(all["quantity"]==0):
                print(all["name"],all["quantity"])
                del hero.inventory[i]

        
        ##########Health##########
        
        healthbar(health,hero.current_health)
        if hero.current_health<=0 and hero.index==10:
            screen.blit(death_screen,(0,0))
            pygame.display.flip()
            time.sleep(1)
            hero.current_health=12
            if hero.life==0:
                running=False
        text = font.render(str(int(clock.get_fps())), 1, (255,255,255))
        screen.blit(text, (700,0))
##        print((B1x+50)/0.8)       
        pygame.display.flip()

        clock.tick(120)  # limits FPS
    return

    pygame.quit()
##level1("")
