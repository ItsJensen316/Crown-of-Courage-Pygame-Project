import pygame
import random
class slideBlock:
    def __init__(self, x, y, w, h, img):
        self.img=img
        self.x=x
        self.y=y
        self.width=w
        self.height=h
        self.roaming_range = 400
        self.initial_state = True
        self.final_state = False
        self.covered_range = 0
        self.delay_time = 80
        self.delay_count = 0
        self.speed2 = 1
        self.left_collide = True
        self.right_collide = True
        self.index=-1

    def draw(self, screen):
        if self.index!=len(self.img)-1:
            self.index+=1
        screen.blit(self.img[self.index],(self.x,self.y))
##        pygame.draw.rect(screen,(255,255,255),(self.x,self.y,self.width,self.height))

    def update(self, hero):
        key=pygame.key.get_pressed()
        if (hero.screen_scroll_X and not hero.slideableBlockCollision) :
           self.x-=hero.char_speed
        if hero.screen_scroll_Y and not hero.slideableBlockCollision:
            self.y-=hero.y_scroll_speed

        if self.initial_state:
                self.covered_range += 1
        if self.final_state:
                self.covered_range -= 1
        if not hero.slideableBlockCollision:
            self.x +=(self.initial_state-self.final_state)
        elif not hero.screen_scroll_X:
            self.x +=(self.initial_state-self.final_state)
            
        if hero.slideableBlockCollision:
            hero.action="Idle"
            hero.char_speed=(self.initial_state-self.final_state)
            if not self.initial_state and not self.final_state:
                hero.rest_state=True
            else:
                hero.rest_state=False  

                

        if self.covered_range >= self.roaming_range:
                if self.delay_count == self.delay_time:
                    self.final_state = True
                    self.initial_state = False
                    self.delay_count = 0
                    self.delay_time = random.randint(200, 500)
                else:
                    self.final_state = False
                    self.initial_state = False
                    self.delay_count += 1

        if self.covered_range <= 0:
                if self.delay_count == self.delay_time:
                    self.final_state = False
                    self.initial_state = True
                    self.delay_count = 0
                    self.delay_time = random.randint(200, 500)
                   
                else:
                    self.initial_state = False
                    self.final_state = False
                    self.delay_count += 1
