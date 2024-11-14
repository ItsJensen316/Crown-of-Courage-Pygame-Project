class Button:
    def __init__(self, x, y, w, h, img):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.distance_covered = 0
        self.pressed = False
        self.lift_direction = -1
        self.img_coll = img

    def update(self, hero):
        if hero.screen_scroll_X:
            if not hero.slideableBlockCollision:
                self.x -= hero.char_speed
            elif not hero.rest_state:
                self.x -= 1 if hero.char_speed > 0 else -1
        if hero.screen_scroll_Y:
            self.y -= hero.y_scroll_speed
        if hero.realive:
            if self.distance_covered < abs(hero.distance_after_cp):
                hero.y = 100
                if hero.distance_after_cp < 0:
                    self.x -= 1
                else:
                    self.x += 1
                # self.y+1
                self.distance_covered += 1
            else:
                hero.realive = False
                self.distance_covered = 0

    def animation(self):
        if self.index < len(self.img_coll):
            self.index += 1 if self.counter == self.animation_time else 0
            if self.counter >= self.animation_time:
                self.counter = 0
        else:
            self.index = 0
        self.counter += 1

    def draw(self, screen):
        if self.pressed:
            screen.blit(self.img_coll[0], (self.x, self.y+5))
        else:
            screen.blit(self.img_coll[0], (self.x, self.y))

