class Players:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.gravity = 2
        self.force = 3
        self.max_jump_height = 250
        self.max_height_reach = False
        self.collide = False
        self.running_mode=False
        self.width=30
        self.height=30
        self.img_size=(40,40)
        self.img_coll=[]
        self.index=0
        self.animation_time=50
        self.counter=0
        for i in range(5):
            self.img=pygame.transform.scale(pygame.image.load(f"./player/{i}.png"),self.img_size)
            self.img_coll.append(self.img)
    def animation(self):
        if self.index!=len(self.img_coll)-1:
            self.index+=1 if self.counter==self.animation_time else 0
            if self.counter==self.animation_time:
                self.counter=0   
            
        else:
            self.index=0    
        self.counter+=1  

    def move(self, keys):
        #write your movement code here
        self.running_mode=keys[pygame.K_LSHIFT]*keys[pygame.K_d]
        if self.y < SCREEN_HEIGHT - 100:
            self.collide = False
            if self.max_height_reach:
                self.gravity = 0.1
        else:
            self.collide = True
            self.force = 2.7
            self.max_height_reach = False

        self.gravity = 0 if self.collide else 0.4
        self.y += self.gravity
        
        if keys[pygame.K_w] and not self.max_height_reach:
            self.force -= self.force * 0.01
            if self.force <= 0:
                self.max_height_reach = True
            self.y -= self.force if self.force > 0 else 0

        self.x += (keys[pygame.K_d] - keys[pygame.K_a]) * 0.7 if not self.running_mode else 1.5        

    def draw(self, screen):
        screen.blit(self.img_coll[self.index],(self.x,self.y))
        self.animation()
