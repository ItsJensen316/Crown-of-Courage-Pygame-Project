from helper import*
pygame.display.set_caption("Level Selector")
def loadimages():
    images=[]
    for i in range(0,15):
        image=pygame.image.load(f'Levels\{i}.png')
        images.append(image)
    return images

def unlockimage(u,image):
    for i in range(0,6):
        if(u==i):
            screen.blit(image[i+8],(0,0))
    
def Levels():
    level=True
    while level:
        i=loadimages()
        #Loading images
        ev=pygame.event.get()
        mx,my=pygame.mouse.get_pos()
        level=open("unlock.txt","r")
        unlock=level.read()
        unlock=int(unlock)
        unlockimage(unlock,i)
        if(80>mx>9 and 590>my>550):
            screen.blit(i[7], (0,0))
            if pygame.mouse.get_pressed()[0]:
                level=False
        else:
            screen.blit(i[6], (0,0))
        if(244>mx>78 and 216>my>44 and unlock>0):
            screen.blit(i[1], (0,0))
        if(483>mx>317 and 216>my>44 and unlock>1):
            screen.blit(i[2], (0,0))
        if(722>mx>556 and 216>my>44 and unlock>2):
            screen.blit(i[3], (0,0))
        if(349>mx>185 and 500>my>326 and unlock>3):
            screen.blit(i[4], (0,0))
        if(619>mx>453 and 500>my>326 and unlock>4):
            screen.blit(i[5], (0,0))
        pygame.display.flip()
        for event in ev:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
