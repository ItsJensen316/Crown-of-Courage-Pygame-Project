import pygame
import time

def load_conversation(file_name): 
    msg = []
    with open(file_name) as file:
        for line in file:
            msg.append(line)  
    return msg

def print_text(screen, text, pos, speaker):
    font = pygame.font.Font(None, FONT_SIZE)
    text_surface = font.render(text, True, (0, 0, 0))  # Change to black (RGB values: 0, 0, 0)
    text_rect = text_surface.get_rect()

    padding = 10
    tail_offset = 20
    box_offset = 0

    if speaker == "player1":
        text_rect.topleft = (pos[0] - tail_offset - text_rect.width, pos[1] - text_rect.height - box_offset)
        tail_pos = (text_rect.right, text_rect.bottom)
        tail_end = (tail_pos[0] + tail_offset, tail_pos[1] + tail_offset)
    else:
        text_rect.topright = (pos[0] + tail_offset + text_rect.width, pos[1] - text_rect.height - box_offset)
        tail_pos = (text_rect.left, text_rect.bottom)
        tail_end = (tail_pos[0] - tail_offset, tail_pos[1] + tail_offset)

    background_rect = text_rect.inflate(padding, padding)
    
    pygame.draw.rect(screen, (245, 245, 220), background_rect)
    screen.blit(text_surface, text_rect)

    pygame.draw.polygon(screen, (245, 245, 220), [(tail_pos[0], tail_pos[1] - 5), 
                                          (tail_pos[0], tail_pos[1] + 5), 
                                          (tail_end[0], tail_end[1])])

##class Player:
##    def _init_(self, x, y):
##        self.x = x
##        self.y = y
##        self.gravity = 2
##        self.force = 3
##        self.max_jump_height = 250
##        self.max_height_reach = False
##        self.collide = False
##        self.running_mode = False
##        self.width = 30
##        self.height = 30
##
##    def move(self, keys):
##        self.running_mode = keys[pygame.K_LSHIFT] * keys[pygame.K_d]
##        if self.y < SCREEN_HEIGHT - 100:
##            self.collide = False
##            if self.max_height_reach:
##                self.gravity = 0.1
##        else:
##            self.collide = True
##            self.force = 2.7
##            self.max_height_reach = False
##
##        self.gravity = 0 if self.collide else 0.4
##        self.y += self.gravity
##        
##        if keys[pygame.K_w] and not self.max_height_reach:
##            self.force -= self.force * 0.01
##            if self.force <= 0:
##                self.max_height_reach = True
##            self.y -= self.force if self.force > 0 else 0
##
##        self.x += (keys[pygame.K_d] - keys[pygame.K_a]) * 0.7 if not self.running_mode else 1.5
##
##    def draw(self, screen):
##        pygame.draw.rect(screen, (100, 100, 100), (self.x, self.y, self.width, self.height))

pygame.init()
FONT_SIZE = 20

class conversation:
    def __init__(self,file):
        self.file=file
        self.index=0
        self.speak = False
    def talk(self,screen,player1,player3):
        player2=player3[0]
        msg = load_conversation(self.file)
        turn = ""
        conversation = ""
        current_character = 0
        last_update_time = time.time()
        text_speed = 0.05  # Adjust the speed here (in seconds)
        collision = pygame.Rect(player1.x, player1.y, player1.width, player1.height).colliderect(
                pygame.Rect(player2.x, player2.y, player2.width, player2.height)
            )
        if collision==True:
            self.speak=True
        while self.speak:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.index != len(msg):
                        self.index += 1
                        turn = "player2" if turn == "player1" else "player1"
                        current_character = 0
 

            if self.index == len(msg):
                self.speak=False
                

            keys = pygame.key.get_pressed()

           
            player1.draw(screen)
            player2.draw(screen)
            
            if collision and self.speak:
                if turn == "":
                    turn = "player1"
                if current_character < len(msg[self.index]):
                    if time.time() - last_update_time > text_speed:
                        current_character += 1
                        last_update_time = time.time()
                print_text(screen, msg[self.index][:current_character],
                           (player1.x, player1.y-20) if turn == "player1" else (player2.x+30, player2.y-20),
                           "player1" if turn == "player1" else "player2")
                pygame.display.update()
            else:
                print_text(screen, msg[self.index-1],
                           (player1.x, player1.y-20) if turn == "player1" else (player2.x+30, player2.y-20),
                           "player1" if turn == "player1" else "player2")
            

