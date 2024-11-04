import random
import pygame
from helper import *
from pygame.locals import *

pygame.init()
font = pygame.font.SysFont("notomono", 25)


def is_collide(tiles, player):
    index = 0
    for all in tiles:
        if pygame.Rect(player.x, player.y, player.width, player.height).colliderect(
            pygame.Rect(all.x, all.y, all.width, all.height)
        ):
            return True, index
        index += 1
    return False, index


def check_collide(tiles, player, check_point):
    x = player.x
    y = player.y
    dec = 0
    dec2 = 0

    if check_point == "left":
        x = player.x - 4
        dec = 15
        dec2 = 5
    elif check_point == "right":
        x = player.x + 4
        dec = 15
        dec2 = 5
    elif check_point == "up":
        y = player.y - 4
        dec = 5
    elif check_point == "down":
        y = player.y + 4
        dec = 5
    elif check_point == "fall":
        y = player.y + 4
        dec = 5
    elif check_point == "bottomright":
        x = player.x + 4
        dec = 10
        dec2 = 5
    elif check_point == "bottomleft":
        x = player.x - 4
        dec = 10
        dec2 = 5
    elif check_point == "slideable":
        for all in tiles:
            if pygame.Rect(
                player.x + 13, player.y + 85, player.width - 30, 5
            ).colliderect(pygame.Rect(all.x, all.y, all.width, 2)):
                return True
        return False
    elif check_point == "pushable":
        for all in tiles:
            if pygame.Rect(
                player.x + 13, player.y + 85, player.width - 30, 5
            ).colliderect(pygame.Rect(all.x, all.y, 45, 45)):
                return True
        return False
    for all in tiles:
        if pygame.Rect(
            x + 13, y + 2 + dec2, player.width - 30, player.height - dec
        ).colliderect(pygame.Rect(all.x, all.y, all.width, all.height)):
            return True
    if not check_point:
        for all in tiles:
            if pygame.Rect(x + 20, y, player.width * 0.3, player.height).colliderect(
                pygame.Rect(
                    all.x + (all.width // 2 - 0.15 * all.width),
                    all.y,
                    0.3 * all.width,
                    all.height,
                )
            ):
                return True

    return False


########################################
class Players:
    def __init__(self, x, y, w, h, path, keys):
        self.b1 = 0
        self.action = "Idle"
        self.spawn_x = 800
        self.spawn_y = 0
        self.life = 3
        self.path = path
        self.re_alive = False
        self.x = x
        self.y = y
        self.extra_dist_after_checkPoint = 0
        self.flip = 1
        self.G = 4
        self.max_force = 7
        self.char_speed = 0
        self.max_speed = 1
        self.gravity = 0
        self.force = 0
        self.max_jump_height = 250
        self.max_height_reach = False
        self.collide = False
        self.collide2 = False
        self.running_mode = False
        self.width = w
        self.height = h
        self.accleration = 0
        self.scroll_val = 0
        self.cond = True
        self.img_size = (w, h)
        self.img_coll = []
        self.index = 0
        self.animation_time = 16
        self.counter = 0
        self.jump_height = 0
        self.inc = 1
        self.speedY = 0
        self.inventory = [{"name": "", "quantity": 1000}]
        self.right = False
        self.left = False
        self.up = False
        self.down = False
        self.isLadder = False
        self.isFood = False
        self.climbing = False
        self.frame_num = 8
        self.rand = 1
        self.screen_scroll_X = False
        self.screen_scroll_Y = False
        self.ladder_collide = False
        self.boundary_collide_initial = (False, False)
        self.boundary_collide_final = (False, False)
        self.move_X = True
        self.move_Y = True
        self.current_health = 5
        self.fall = False
        self.rest_state = False
        self.slideableBlockCollision = False
        self.sounds = {
            "hurt": pygame.mixer.Sound("Music/Hero_hurt.mp3"),
            "hurt2": pygame.mixer.Sound("Music/Hero_hurt2.mp3"),
            "death": pygame.mixer.Sound("Music/Hero_death.mp3"),
            "sword": pygame.mixer.Sound("Music/Sword_1.mp3"),
            "sword2": pygame.mixer.Sound("Music/Sword_2.mp3"),
            "grab": pygame.mixer.Sound("Music/Grab.mp3"),
        }
        ##        for i in range(111, 131):
        ##            self.food.append(i)
        self.keys = keys

    ##    def boundary_collision(self): #To be done

    def animation(self):
        if self.index != len(self.img_coll) - 1:
            self.index += 1 if self.counter == self.animation_time else 0
            if self.counter >= self.animation_time:
                self.counter = 0
        else:
            if self.action == "Death":
                return
            self.rand = random.randint(1, 2)
            self.index = 0
        if self.action != "Idle":
            self.counter += self.inc
        else:
            self.counter += 1

    def movement(self, tiles, slidables, b1, end_pos, min_height):
        self.b1 = b1[0]
        self.right = check_collide(tiles, self, "right")
        self.left = check_collide(tiles, self, "left")
        self.up = check_collide(tiles, self, "up")
        self.down = check_collide(tiles, self, "down")
        self.fall = check_collide(tiles, self, "fall")
        self.bottomright = check_collide(tiles, self, "bottomright")
        self.bottomleft = check_collide(tiles, self, "bottomleft")
        self.ladder_collide = check_collide(Ladder, self, "")
        self.slideableBlockCollision = check_collide(slidables, self, "slideable")
        self.pushableBlockCollision = check_collide(pushables, self, "pushable")
        if self.slideableBlockCollision:
            self.down = True
        if self.pushableBlockCollision:
            self.right = True
            self.left = True
            self.down = True

        keys = pygame.key.get_pressed()
        if self.current_health <= 0:
            self.action = "Death"
            self.animation()
            self.img_size = (80, 90)
            ##            self.sounds["death"].play()
            return
        if not self.climbing:
            self.animation()
        if not self.ladder_collide:
            self.climbing = False
        if self.char_speed == 0 and not keys[self.keys["jump"]]:
            self.action = "Idle"

        ######Walk and Run######
        if keys[self.keys["sprint"]]:
            self.speed = 0.05
            self.max_speed = 3
            self.inc = 2
        else:
            self.speed = 0.03
            self.max_speed = 2
            self.inc = 1
        if keys[self.keys["right_move"]]:
            x = self.keys["jump"]
            if not keys[x]:
                self.action = "Run"
                if self.char_speed < -0.15:
                    self.action = "Drift"
                    self.inc = 1
            self.flip = 1
            self.char_speed += self.speed
        elif keys[self.keys["left_move"]]:
            if not keys[self.keys["jump"]]:
                self.action = "Run"
                if self.char_speed > 0.15:
                    self.action = "Drift"
                    self.inc = 1
            self.flip = -1
            self.char_speed -= self.speed
        else:
            for i in range(0, 4):
                if self.char_speed < 0:
                    self.char_speed += 0.01
                elif self.char_speed > 0:
                    self.char_speed -= 0.01

        ######Jump and Fall######
        if self.x < 0:
            self.x = 0
            self.char_speed = 0
        elif self.x > 745:
            self.x = 745
            self.char_speed = 0
        if self.char_speed > self.max_speed:
            self.char_speed = self.max_speed
        elif self.char_speed < -self.max_speed:
            self.char_speed = -self.max_speed
        if (
            keys[self.keys["jump"]]
            and self.jump_height < 24
            and not self.up
            and not self.ladder_collide
            and self.cond == True
        ):
            ##            print(self.ladder_collide)
            ##            self.action="Jump"
            self.gravity -= 0.4
            self.jump_height += 1
        elif self.down:
            self.cond = True
            self.jump_height = 0
            self.gravity = 0
        else:
            self.cond = False
        if not self.fall:
            self.action = "Jump"
            if self.gravity >= 0:
                self.action = "Fall"

        ######Attack######
        if keys[self.keys["attack"]]:
            self.action = "Attack"
            self.inc = 2
            if self.char_speed > 1 or self.char_speed < -1:
                self.action = "Dash_Attack"
            at = 4 if self.action == "Attack" else 1
            if self.index == at:
                self.sounds["sword2"].play()

        ######Ladder######
        if self.ladder_collide:
            self.climbing = True
            self.action = "Climb"
            self.gravity = 0
            acc = 1
            if keys[self.keys["sprint"]]:
                acc = 2
                self.inc = 2
            if (
                keys[self.keys["jump"]]
                or keys[self.keys["slide"]]
                or keys[self.keys["left_move"]]
                or keys[self.keys["right_move"]]
            ):
                self.animation()
            if keys[self.keys["jump"]]:
                self.gravity = -0.7 * acc
            elif keys[self.keys["slide"]]:
                self.gravity = 0.7 * acc
        elif not self.down:
            self.gravity += 0.15
        elif self.down and not keys[self.keys["jump"]]:
            self.gravity = 0
            self.jump_height = 0
        if (self.down and self.bottomright and self.bottomleft) or (
            self.down and self.ladder_collide
        ):
            self.y -= 1

        self.char_speed = float(format(self.char_speed, ".2f"))
        ##        if not self.down:
        if self.left:
            self.char_speed = 0.1
        if self.right:
            self.char_speed = -0.1
        if self.move_X == True:
            self.x += self.char_speed

        if self.up:
            self.cond = False
            self.gravity = 0.2
            self.gravity += 0.5
        if self.move_Y:
            self.y += self.gravity
        ##        print(self.char_speed)

        ##Grabbing##
        ##        if (keys[self.keys["grab"]] and self.isFood):

        # Screen Scroll X
        if self.x > 350:
            self.move_X = False
            self.screen_scroll_X = True
        if bgx[0] > -50:
            self.move_X = True
            self.screen_scroll_X = False
        if bgx[0] < -end_pos[0]:
            self.move_X = True
            self.screen_scroll_X = False
            if self.x < 350:
                self.x = 350
                self.move_X = False
                self.screen_scroll_X = True

        # Screen Scroll Y
        # if self.y > 350:
        #     self.move_Y = False
        #     self.screen_scroll_Y = True
        # if bgy[0] > -50:
        #     self.move_Y = True
        #     self.screen_scroll_Y = False
        # if bgy[0] < -end_pos[1]:
        #     self.move_Y = True
        #     self.screen_scroll_Y = False
        #     if self.y < 350:
        #         self.y = 350
        #         self.move_Y = False
        #         self.screen_scroll_Y = True

        if self.y > min_height:
            self.current_health = 0

    ##        print(b1x)

    def draw(self, screen):
        self.img_coll = loadimages2(self.path, self.action, self.img_size)
        try:
            if self.flip == 1:
                screen.blit(self.img_coll[self.index], (self.x, self.y))
            else:
                screen.blit(
                    pygame.transform.flip(self.img_coll[self.index], True, False),
                    (self.x, self.y),
                )
        except:
            self.index = 0


########################################


class enemy(Players):
    def __init__(self, x, y, w, h, path, keys, identity):
        super().__init__(x, y, w, h, path, keys)
        self.roaming_range = 1200
        self.initial_state = True
        self.final_state = False
        self.init_pos = (x, y)
        self.covered_range = 0
        self.delay_time = 80
        self.delay_count = 0
        self.fight_range = False
        self.radius = 200
        self.speed2 = 1
        self.attack_range = 0.7 * self.width
        self.distanceX = 0
        self.distanceY = 0
        ##        self.attack_gap = 70
        ##        self.attack_gap_count = 0
        self.left_collide = True
        self.right_collide = True
        self.player_counter = 0
        self.player_hit = False
        self.enemy_counter = 0
        self.enemy_hit = False
        self.enemy_health = 100
        self.damage_rate = 3
        self.hitted = False
        self.hit_counter = 500
        self.identity = identity
        self.can_append = True
        try:
            self.enemy_attack = loadimages2(self.path, "Attack", self.img_size)
        except:
            self.enemy_attack1 = loadimages2(self.path, "Attack1", self.img_size)
            self.enemy_attack2 = loadimages2(self.path, "Attack2", self.img_size)
        self.enemy_death = loadimages2(self.path, "Death", self.img_size)
        self.enemy_damage = loadimages2(self.path, "Damage", self.img_size)
        self.enemy_idle = loadimages2(self.path, "Idle", self.img_size)
        self.enemy_run = loadimages2(self.path, "Run", self.img_size)
        self.enemy_walk = loadimages2(self.path, "Walk", self.img_size)

    def health_bar(self):
        if self.enemy_health > 0:
            pygame.draw.rect(screen, (50, 50, 50), (self.x - 5, self.y - 20, 100, 10))
            pygame.draw.rect(
                screen,
                (255, 0, 0) if self.enemy_health < 40 else (0, 255, 0),
                (self.x - 5, self.y - 20, self.enemy_health, 10),
            )
            pygame.draw.rect(
                screen, (255, 255, 255), (self.x - 5, self.y - 20, 100, 10), 1
            )

    def draw2(self, screen):
        if self.action == "Attack":
            self.img_coll = self.enemy_attack
        elif self.action == "Attack1":
            self.img_coll = self.enemy_attack1
        elif self.action == "Attack2":
            self.img_coll = self.enemy_attack2
        elif self.action == "Death":
            self.img_coll = self.enemy_death
        elif self.action == "Damage":
            self.img_coll = self.enemy_damage
        elif self.action == "Run":
            self.img_coll = self.enemy_run
        elif self.action == "Walk":
            self.img_coll = self.enemy_walk
        else:
            self.img_coll = self.enemy_idle
        ##        self.img_coll = loadimages2(self.path, self.action, self.img_size )
        try:
            if self.flip == 1:
                screen.blit(self.img_coll[self.index], (self.x, self.y))
            else:
                screen.blit(
                    pygame.transform.flip(self.img_coll[self.index], True, False),
                    (self.x, self.y),
                )
        except:
            self.index = 0

    def draw_enemy(self, screen):
        pygame.draw.rect(
            screen, (255, 0, 0), (self.x, self.y, self.width, self.height), 1
        )

        pygame.draw.circle(
            screen,
            (255, 0, 0),
            (self.x + self.width / 2, self.y + self.height / 2),
            self.radius,
            1,
        )

    def check_hit(self, hero, enemy_rect):
        if pygame.Rect(hero.x, hero.y, hero.width, hero.height).colliderect(enemy_rect):
            return True
        return False

    def go_for_attack(self, hero):
        ##        self.draw_enemy(screen)
        self.distanceX = self.x + 10 - hero.x
        self.distanceY = self.y - hero.y
        if self.distanceX < 0:
            self.distanceX = -self.distanceX
        if self.distanceY < 0:
            self.distanceY = -self.distanceY

        if (
            self.distanceX > self.attack_range or self.distanceY > self.height
        ) and self.action != "Death":
            self.speed2 = 1.5

            if self.distanceX > self.width:
                if (self.x - hero.x) < 0:
                    self.flip = 1
                else:
                    self.flip = -1
            self.x += (
                self.speed2
                * self.flip
                * (not self.left_collide)
                * (not self.right_collide)
            )
            self.action = "Run"

            # self.y+=self.speed2 if (self.y-hero.y)<0 else -self.speed2
        elif self.action != "Death":
            if os.path.isfile(f"{self.path}/Attack{self.rand}/Attack{self.rand}_0.png"):
                self.action = f"Attack{self.rand}"
            ##                print("I")
            else:
                self.action = "Attack"
            disp = self.x + 30 + 5 if (self.x - hero.x) < 0 else self.x - 30 - 5
            ##            pygame.draw.rect(screen,(0,255,0),(disp,self.y,self.width,self.height))
            if self.check_hit(hero, pygame.Rect(disp, self.y, self.width, self.height)):
                #    hero.hero_health-=5
                self.player_counter += 1
                if self.player_counter > 60 and hero.current_health > 0:
                    hero.sounds["hurt"].play()
                    print("enemy hitted")
                    hero.current_health -= 1
                    self.player_counter = 0
        if self.action not in "Attack1Attack2":
            self.player_counter = 0

        if hero.action in "Dash_Attack":
            self.enemy_counter += 1
            at = 4 if hero.action == "Attack" else 1
            if self.distanceX < 80 and self.distanceY < 80 and hero.index == at:
                hero.sounds["sword"].play()
                self.hitted = True
                self.enemy_counter = 0
            else:
                self.hitted = False

    def enemy_scroll(self, hero):
        if hero.screen_scroll_X:
            self.x -= hero.char_speed
        if hero.screen_scroll_Y:
            self.y -= hero.gravity

    # hero to scroll back to the last check point
    # if hero.current_health <= 0:
    #     self.x = self.init_pos[0] - hero.spawn_x
    #     self.y = self.init_pos[1] - hero.spawn_y

    def enemy_movement(self, hero, tiles):
        self.health_bar()
        ##        print(hero.char_speed)

        if self.hitted:
            self.hit_counter = 0
            self.enemy_health -= self.damage_rate

        ##        print(self.left_collide, self.right_collide)
        self.right = check_collide(tiles, self, "right")
        self.left = check_collide(tiles, self, "left")
        self.up = check_collide(tiles, self, "up")
        self.down = check_collide(tiles, self, "down")
        self.bottomright = check_collide(tiles, self, "bottomright")
        self.bottomleft = check_collide(tiles, self, "bottomleft")
        self.y += self.G if not self.down else 0
        if self.down and (self.bottomright or self.bottomleft):
            self.y -= 1

        if self.right:
            self.x -= 1
            self.right_collide = True
            self.final_state = True
            self.initial_state = False
        elif self.left:
            self.x += 1
            self.left_collide = True
            self.initial_state = True
            self.final_state = False
        else:
            self.right_collide = False
            self.left_collide = False
        if not self.fight_range and self.action != "Death":
            if self.initial_state:
                self.flip = 1
                self.covered_range += 1
            if self.final_state:
                self.flip = -1
                self.covered_range -= 1

            self.x += (
                self.speed2
                * self.flip
                * (not self.left_collide)
                * (not self.right_collide)
            )

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
                    self.action = "Idle"
                else:
                    self.initial_state = False
                    self.final_state = False
                    self.delay_count += 1
                    self.action = "Idle"
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            (
                self.x - self.radius,
                self.y + 20,
                self.radius * 2 + self.width,
                self.radius * 2,
            ),
            1,
        )
        pygame.draw.rect(
            screen, (0, 255, 0), (hero.x, hero.y, hero.width, hero.height), 1
        )
        if pygame.Rect(
            self.x - self.radius,
            self.y + 20,
            self.radius * 2 + self.width,
            self.radius * 2,
        ).colliderect(pygame.Rect(hero.x, hero.y, hero.width, hero.height)):
            ##            pygame.draw.rect(screen,(0,255,0),(self.x , self.y , self.width , self.height ))
            ##            pygame.draw.rect(screen,(0,255,0),(hero.x, hero.y, hero.width, hero.height))

            self.fight_range = True
        else:
            self.speed2 = 0.5
            self.fight_range = False

        ##        if (self.distanceX<1):
        ##            self.action="Idle"
        if self.speed2 < 0.5:
            self.action = "Idle"
        elif self.speed2 == 0.5:
            self.action = "Walk"
        elif self.speed2 == 0.7:
            self.action = "Run"

        self.hit_counter += 1
        if self.hit_counter < 50:
            self.action = "Damage"

        if self.enemy_health <= 0:
            self.action = "Death"
        self.animation()

        # print(hero.collide)

        # print(self.x)
