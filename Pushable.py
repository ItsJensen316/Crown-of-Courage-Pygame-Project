import pygame
def check_collide(tiles, player, check_pofloat):
    x = player.x
    y = player.y
    if check_pofloat == "left":
        x = x-4
    
    elif check_pofloat == "right":
     
        x = x+4
       
    elif check_pofloat == "up": 

        y = player.y - 4

    elif check_pofloat == "down":
        y = player.y + 4
    for all in tiles:
        if pygame.Rect(x+13, y, player.width-30, player.height-5).colliderect(
            pygame.Rect(all.x, all.y, all.width, all.height)
        ):
            return True


class pushableObject:
    def __init__(self,x,y,w,h,img):
        self.x=x
        self.y=y
        self.width=w
        self.gravity=1
        self.height=h
        self.speed=0
        self.img=img
        
    def draw(self,screen):
        pygame.draw.rect(screen,(255,255,255),(self.x,self.y,self.width,self.height))
    def update(self,tiles,hero):
        if (hero.screen_scroll_X and not hero.slideableBlockCollision) :
           self.x-=hero.char_speed
        if hero.screen_scroll_Y and not hero.slideableBlockCollision:
            self.y-=hero.gravity
        elif(hero.slideableBlockCollision):

            if not hero.rest_state:
                  self.x-=1 if hero.char_speed>0 else -1


        self.down=check_collide(tiles,self,"down")
        self.right=check_collide(tiles,self,"right")
        self.left=check_collide(tiles,self,"left")
        self.up=check_collide(tiles,self,"up")
   


        if not self.down:
            self.y+=self.gravity
            
        if check_collide([self],hero,"right"):
            if self.speed<0.8:
                self.speed+=0.1 if not self.right else 0
                
                self.speed=float(format(self.speed,".1f"))
        elif check_collide([self],hero,"left"):
            if self.speed>-0.8:
                self.speed+=-0.1 if not self.left else 0
                self.speed=float(format(self.speed,".1f"))
        else:
            if self.speed<0:
                self.speed+=0.1
                self.speed=float(format(self.speed,".1f"))
            elif self.speed>0:
                self.speed-=0.1
                self.speed=float(format(self.speed,".1f"))
            else:
                self.speed=0
        # print(self.speed)                
        self.x+=self.speed
