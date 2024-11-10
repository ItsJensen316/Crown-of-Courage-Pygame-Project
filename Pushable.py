import pygame


def check_collide(tiles, player, check_point):
    x = player.x
    y = player.y
    dec = 0
    dec2 = 0

    if check_point == "left":
        x = player.x - 15
        dec = 15
        dec2 = 5
    elif check_point == "right":
        x = player.x + 20
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
    # elif check_point == "bottomright":
    #     x = player.x + 4
    #     dec = 10
    #     dec2 = 5
    # elif check_point == "bottomleft":
    #     x = player.x - 4
    #     dec = 10
    #     dec2 = 5

    for all in tiles:
        if pygame.Rect(
            x + 13, y + 2 + dec2, player.width - 30, player.height - dec
        ).colliderect(pygame.Rect(all.x, all.y, all.width, all.height)):
            return True

    return False


class pushableObject:
    def __init__(self, x, y, w, h, img):
        self.x = x
        self.y = y
        self.width = w
        self.gravity = 1
        self.height = h
        self.speed = 0
        self.friction = 0.2
        self.img = img
        self.acc = 2

    def draw(self, screen):
        pygame.draw.rect(
            screen, (255, 255, 255), (self.x, self.y, self.width, self.height)
        )

    def update(self, tiles, hero):
        if hero.screen_scroll_X and not hero.rest_state:
            self.x -= hero.char_speed
        if hero.screen_scroll_Y:
            self.y -= hero.y_scroll_speed
        # elif hero.slideableBlockCollision:

        #     if not hero.rest_state and hero.screen_scroll_X:
        #         self.x -= 1 if hero.char_speed > 0 else -1

        self.down = check_collide(tiles, self, "down")
        self.right = check_collide(tiles, self, "right")
        self.left = check_collide(tiles, self, "left")
        self.up = check_collide(tiles, self, "up")
        # print(self.left, self.right)

        if not self.down:
            self.y += self.gravity
        if not (self.right or self.left):

            if check_collide([self], hero, "right"):
                self.speed = self.acc - self.friction

            elif check_collide([self], hero, "left"):
                self.speed = -self.acc + self.friction

            else:
                # logic to apply momentum in object
                if self.speed < 0:
                    self.speed += 0.1
                    self.speed = float(format(self.speed, ".1f"))
                elif self.speed > 0:
                    self.speed -= 0.1
                    self.speed = float(format(self.speed, ".1f"))
                else:
                    self.speed = 0
        else:
            self.speed = 0
        self.x += self.speed
