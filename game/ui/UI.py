import pygame

pygame.init()
fps = 120
fpsclock = pygame.time.Clock()


class DynamicHealthBar:
    """Build the exact slot count from the original empty PNG's sections."""

    def __init__(self):
        self.empty = pygame.image.load("assets/art/UI/Healthbar/0.png").convert_alpha()
        self.cached = None
        self.surface = None
        self.font = pygame.font.SysFont("notomono", 20, bold=True)

    def draw(self, target, current, maximum):
        maximum = max(2, int(maximum))
        current = max(0, min(maximum, int(current)))
        if self.cached != (current, maximum):
            # First slot overlaps the heart. The middle is a clean repeatable
            # 18px segment; the final segment includes the original tapered cap.
            width = 69 + (maximum - 2) * 18 + 22
            image = pygame.Surface((width, 50), pygame.SRCALPHA)
            image.blit(self.empty, (0, 0), (0, 0, 69, 50))
            for i in range(maximum - 2):
                image.blit(self.empty, (69 + i * 18, 0), (69, 0, 18, 50))
            last = 69 + (maximum - 2) * 18
            image.blit(self.empty, (last, 0), (248, 0, 22, 50))
            for x in range(50, width):
                slot = 0 if x < 69 else min(maximum - 1, 1 + (x - 69) // 18)
                for y in range(50):
                    if image.get_at((x, y))[:3] == (255, 255, 255):
                        if slot < current:
                            stops = [
                                (255, 45, 35),
                                (255, 135, 15),
                                (255, 230, 30),
                                (45, 235, 55),
                            ]
                            position = slot / max(1, maximum - 1) * 3
                            index = min(2, int(position))
                            blend = position - index
                            base = tuple(
                                round(a + (b - a) * blend)
                                for a, b in zip(stops[index], stops[index + 1])
                            )
                            # One shared warm-to-green palette; a bright top edge
                            # retains the original pixel-art highlight.
                            color = (
                                tuple(min(255, c + 35) for c in base)
                                if y < 14
                                else base
                            )
                        else:
                            color = (255, 255, 255)
                        image.set_at((x, y), (*color, 255))
            self.surface = pygame.transform.scale(image, (round(width * 0.8), 40))
            self.number = self.font.render(
                f"{current}/{maximum}", True, (240, 255, 240)
            )
            self.cached = (current, maximum)
        target.blit(self.surface, (20, 20))
        label = self.number.get_rect(midleft=(28 + self.surface.get_width(), 40))
        pygame.draw.rect(target, (16, 25, 29), label.inflate(8, 6), border_radius=3)
        target.blit(self.number, label)
