import pygame
from pygame.locals import *
from helper import *
import sys
pygame.init()
fps=120
fpsclock=pygame.time.Clock()
screen=pygame.display.set_mode((800,600))
pygame.display.set_caption("Keyboard_Input")
White=(255,200,100)
yscroll=800
scroll=1
canscroll=False
transparency=0
Font = pygame.font.Font(None, 30)
mouse_pos=()
index=0
counter=0
counter2=0
health_gain={"Mushroom":1,"Apple":2,"Meat":3,"Kit":4}
select_outline=loadimages("Assets/UI/Inventory_Selection.png",(45,45))
def player_inventory(Inv,hero,Inv_dict,keys):
    global index, counter, counter2
    global yscroll
    global scroll
    global canscroll
    global transparency
    Player_Inv=hero.inventory
    Inv_length=len(Player_Inv)
    if canscroll==True:
        yscroll+=5*scroll
        transparency+=10*-scroll
    if(transparency<0):
        transparency=0
    elif(transparency>255):
        transparency=255
    if(yscroll>150):
        yscroll=150
    elif(yscroll<20):
        yscroll=20
    ev=pygame.event.get()
    kinput = pygame.key.get_pressed()
    if kinput[keys["inventory"]]:
        if(yscroll==20):
            scroll=1
        elif(yscroll==150):
            scroll=-1
        canscroll=True
        
    Inv.set_alpha(transparency)
##    Key=loadimages("Assets/Key.png",(40,40)).convert_alpha()
##    Key.set_alpha(transparency)
    screen.blit(Inv,(0,yscroll))
    k = pygame.key.get_pressed()
    counter2+=1
    for i in range(1,Inv_length):
        P=Player_Inv[i]
        Item_display=Inv_dict[P['name']]
        if k[pygame.K_u] and counter2>20:
            counter2=0
            try:
                if hero.current_health<12:
                    Player_Inv[index+1]["quantity"]-=1
                    hero.current_health+=health_gain[Player_Inv[index+1]['name']]
            except:
                pass
            if hero.current_health>12:
                hero.current_health=12
        
        Num=P['quantity']
        Num=str(Num)
        Item_display.set_alpha(transparency)
        text = Font.render(Num, False, (255,255,255))
        screen.blit(Item_display,((i+2)*50,(10*50)+yscroll))
        screen.blit(text, ((i+2)*50,(10*50)+yscroll+25))
    if yscroll==20:
        counter+=1
        if counter>20:
            if k[pygame.K_RIGHT] and index<9:
                counter=0
                index+=1
            elif k[pygame.K_LEFT] and index>0:
                counter=0
                index-=1
            else:
                counter+=30
        screen.blit(select_outline,((index+3)*50-3,(10*50)-3+yscroll))    
##        pygame.draw.rect(screen,(255,255,255),((index+3)*50-3,(10*50)-3+yscroll,45,45),2)
        
        
