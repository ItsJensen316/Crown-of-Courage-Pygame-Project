import pygame
from pygame.locals import *
import sys
pygame.init()
fps=120
fpsclock=pygame.time.Clock()
screen=pygame.display.set_mode((800,600))
pygame.display.set_caption("Keyboard_Input")
White=(255,255,255)
def movement():
    speed=0
    x=500
    y=560
    h=40
    w=40
    jump=0
    cool=50
    cool_down=False
    enemy_health=5
    cond=True
    while True:
        screen.fill(White)
        player=Rect(x, y, w, h)
        enemy=Rect(650, 560, 20, 100)
        if(enemy_health>0):
            pygame.draw.rect(screen, (0,255,0), enemy)
        pygame.draw.rect(screen, (255,0,0), player)
        collide = pygame.Rect.colliderect(player, enemy)
        if(collide==True and cool_down==False):
            enemy_health-=1
            cool=50
            cool_down=True
        if(cool_down==True):
            cool-=1
            if(cool<0 and collide==False):
                cool_down=False
        #print(enemy_health)
        ev=pygame.event.get()
        kinput = pygame.key.get_pressed()   
        if (kinput[pygame.K_RIGHT]):
            speed+=0.04
        else:
            for i in range(0,4):
                if(speed>0):
                    speed-=0.02
        if (kinput[pygame.K_LEFT]):
            speed-=0.04
        else:
            for i in range(0,4):
                if(speed<0):
                    speed+=0.02
        if(kinput[pygame.K_z]):
            if (kinput[pygame.K_RIGHT]):
                speed+=0.04
            if (kinput[pygame.K_LEFT]):
                speed-=0.04
            if(speed>3):
                speed=3
            elif(speed<-3):
                speed=-3
        else:
            if(speed>2):
                speed-=0.06
            elif(speed<-2):
                speed+=0.06
        if(kinput[pygame.K_x] and y>525 and cond==True):
            jump+=0.2
        else:
            if(y<560):
                jump-=0.15
            elif(y>560):
                jump=0
                y=560
            if(y<560):
                cond=False
            if(y==560):
                cond=True
            
        speed=float(format(speed,".2f"))
        #print(jump)
        x+=speed
        y-=jump
        for event in ev:
            if pygame.mouse.get_pressed()[0]:
                w=60
            else:
                w=40
        for event in ev:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
        pygame.display.update()
        print(fpsclock)
        fpsclock.tick()
movement()
