import pygame
import sys,csv

clock = pygame.time.Clock()
screen=pygame.display.set_mode((800,600))
tiles_arr=[]
tiles_dimension=(45,45)
img_arr=[]
displaceX=0
displaceY=0
bg=pygame.image.load("Assets/Level1/1-2/Background.png")
bg2=pygame.image.load("Assets/Level1/1-2/Background2.png")
bg=pygame.transform.scale(bg,(5600,2400))
bg2=pygame.transform.scale(bg2,(800,600))
for i in range(1,450):
    try:
        if(i<=100):
            img=pygame.image.load(f"Assets/Level1/1-2/tile_{i}.png")
        else:
            img=pygame.image.load(f"Assets/Level1/1-2/Extras/tile_{i}.png")
    except:
        img=pygame.image.load("Assets/Empty.png")
    img=pygame.transform.scale(img,tiles_dimension)
    img_arr.append(img)
    
# Python code to illustrate with()
with open("level12.csv") as file: 
    data = csv.reader(file)
    for all in data:
##        for i in range(len(all)):
##            for key,value in dict.items():
##                if(key==all[i]):
##                    all[i]=value
        tiles_arr.append(all)
##with open("level12-Copy.csv", 'w', newline='') as file:  
##    writer = csv.writer(file)
##    writer.writerows(tiles_arr)
tiles_arr[0][0]='50'
running =True
for i in range(len(tiles_arr)):
    for j in range(len(tiles_arr[0])):
        #print(tiles_arr[i][j])
        if(tiles_arr[i][j])=='1':
            print("1")
color=(21,19,39)

while running:
    
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    kinput = pygame.key.get_pressed()
    displaceX+=(kinput[pygame.K_d]-kinput[pygame.K_a])*10
    displaceY+=(kinput[pygame.K_w]-kinput[pygame.K_s])*10
    screen.blit(bg2,(0,0))  #Background color
    screen.blit(bg,(-displaceX*0.9,displaceY*0.9))  #Background texture

    # fill the screen with a color to wipe away anything from last frame
    
    for i in range(len(tiles_arr)):
        for j in range(len(tiles_arr[0])):
            #print(tiles_arr[i][j])
            if tiles_arr[i][j]!='-1':
                screen.blit(img_arr[int(tiles_arr[i][j])-1],(tiles_dimension[0]*j-displaceX,tiles_dimension[1]*i+displaceY))
                           
    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
    
