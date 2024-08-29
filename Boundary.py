class Boundary:
    def __init__(self, initial, final):


    def update(self,hero):
        if hero.screen_scroll_X:
            if not hero.slideableBlockCollision:
                self.x-=hero.char_speed
            elif not hero.rest_state:
                self.x-=1 if hero.char_speed>0 else -1
        if hero.screen_scroll_Y:
            self.y-=hero.gravity
        if hero.current_health<=0:
            self.x=self.x_copy-hero.spawn_x
            self.y=self.y_copy-hero.spawn_y
        
