import pygame
import sys
from Conversation import *
from Game_Char_Copy import *
from Inventory import *
from UI import *
import time
pygame.init()

def level1(key_map):
    clock = pygame.time.Clock()
    
    hero_pos,tiles_arr,tiles,ladder,food,door,lift,boxes,inventory,others,Enmy=loadimages1('Assets/Level1/1-1')
    
    # print(Enmy,others)

    enmy=enemy(Enmy[0]["x"],Enmy[0]["y"],90,90,Enmy[0]["path"]) 
    


    def draw(object):
        for all in object:
            all.update(hero)
            all.draw(screen)
        
    ##background images setup
    bgimg=loadimages("Assets/Level1/1-1/Tile_0.png",(8000,600))
    bgimg2=loadimages("Assets/Level1/1-1/Background2.png",(8000,600))
    death_screen=loadimages("Assets/Death_screen.png",(800,600))

    
    #############INVENTORY#############
    Inv=loadimages("Assets/Inventory.png",(800,600)).convert_alpha()
    Inv_items=[]
    Inv_length=3
    for i in range(140,140+Inv_length):
        item=loadimages(f'Assets/Food/{i}.png',(40,40)).convert_alpha()
        Inv_items.append(item)

    #############UI#############
    health=[]
    for i in range(0,13):
        bars=loadimages(f"Assets/UI/Healthbar/{i}.png",(200,37))
        health.append(bars)
    


        
    B1x=-50
    B2x=-50
    hero_Dim=(60,90)

    running =True

    hero=Players(0,450,hero_Dim[0],hero_Dim[1],"Assets/Player")
    
    temp=conversation("File1.txt")


    down=False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        mx,my=pygame.mouse.get_pos()

        
        if hero.screen_scroll:
            B1x-=hero.char_speed*0.5
            B2x-=hero.char_speed*0.8
        elif B1x>-100:
            B1x=-50
            B2x=-50
        #Animalsw
##      hero.moved(tiles,ladder,food,B1x)
        screen.blit(bgimg2,(B1x,0))    #Background1
        screen.blit(bgimg,(B2x,0))   #Background2
        draw(tiles)
        draw(others)
    
        draw(ladder)   #Hero
        draw(food)
        enmy.draw(screen)
        enmy.draw_enemy(screen)
        hero.draw(screen)
##        temp.talk(screen,hero,food)
        if enmy.fight_range:
            enmy.go_for_attack(hero)
        enmy.enemy_movement(hero,tiles)
        hero.movement(tiles,B1x,3562,600)
        
        hero.isFood=check_collide(Food,hero,"") 
        if(hero.isFood):
            text = font.render("Press G to pick up item", False, (255,255,255))
            screen.blit(text, (200,10))
        player_inventory(Inv,Inv_items,Inv_length)
        healthbar(health,hero.current_health)
        if hero.current_health==0:
            screen.blit(death_screen,(0,0))
            pygame.display.flip()
            time.sleep(3)
            running=False
        pygame.display.flip()

        clock.tick(165)  # limits FPS to 60
    return

    pygame.quit()
##while True:
##    level1()
