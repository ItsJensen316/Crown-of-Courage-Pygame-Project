import pygame,sys
from helper import *

def loadimages():
    images=[]
    for i in range(0,17):
        image=pygame.image.load(f'Book\{i}.png')
        images.append(image)
    return images

def animate(speed,direction,image,i1,i2):
    for i in range(i1,i2,direction):
        for j in range(0,speed):
            screen.blit(image[14],(0,0))
            screen.blit(image[15],(0,0))
            screen.blit(image[i],(0,0))
            pygame.display.update()

def StoryBook():
    story=True
    while story:
        i=loadimages()
        mx,my=pygame.mouse.get_pos()
        #print(mx,my)
        ev=pygame.event.get()
        screen.blit(i[14],(0,0))
        speed=4
        if(785>mx>750 and 315>my>275):
            screen.blit(i[13],(0,0))
            for event in ev:
                if event.type == pygame.MOUSEBUTTONUP:
                    animate(speed,-1,i,10,0)
        elif(50>mx>15 and 315>my>275):
            screen.blit(i[12],(0,0))
            for event in ev:
                if event.type == pygame.MOUSEBUTTONUP:
                    animate(speed,1,i,1,11)
        else:
            screen.blit(i[0],(0,0))
        
        if(80>mx>10 and 50>my>8):
            screen.blit(i[16],(0,0))
            if pygame.mouse.get_pressed()[0]:
                story=False
        else:
            screen.blit(i[15],(0,0))
        pygame.display.flip()
        for event in ev:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
