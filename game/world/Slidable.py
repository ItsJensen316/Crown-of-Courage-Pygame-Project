"""Moving platforms with fixed endpoint pauses and exact rider displacement."""


class slideBlock:
    def __init__(self, x, y, w, h, img):
        self.x, self.y, self.width, self.height = x, y, w, h
        self.img = img
        self.speed = 1.0
        self.roaming_range = 270
        self.covered_range = 0.0
        self.dir = 1
        self.initial_state, self.final_state = True, False
        self.delay_time = 60
        self.delay_count = 0
        self.index = 0
        self.delta_x = 0

    def draw(self, screen):
        screen.blit(self.img[0], (round(self.x), round(self.y)))

    def update(self, hero):
        feet = hero.y + hero.height
        riding = (
            abs(feet - self.y) <= 6
            and hero.gravity >= 0
            and hero.x + hero.width - 17 > self.x
            and hero.x + 13 < self.x + self.width
        )
        self.delta_x = 0.0
        if self.delay_count:
            self.delay_count -= 1
        else:
            # Ease near each end without a random multi-second wait.
            edge = min(self.covered_range, self.roaming_range - self.covered_range)
            amount = self.speed * max(0.25, min(1.0, (edge + 4) / 30))
            next_pos = max(
                0, min(self.roaming_range, self.covered_range + amount * self.dir)
            )
            self.delta_x = next_pos - self.covered_range
            self.covered_range = next_pos
            self.x += self.delta_x
            if next_pos in (0, self.roaming_range):
                self.dir *= -1
                self.delay_count = self.delay_time
        self.initial_state = self.delta_x > 0
        self.final_state = self.delta_x < 0
        if riding:
            hero.x += self.delta_x
