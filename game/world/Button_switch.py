"""Animated pressure plate; its collision sensor stays fixed at floor height."""

import math

import pygame


class Button:
    def __init__(self, x, y, w, h, img):
        self.x, self.y, self.width, self.height = x, y, w, h
        self.pressed = False
        self.lift_direction = -1
        self.img_coll = img
        self.press_amount = 0.0
        self.pulse = 0
        self.plate = img[0].subsurface(img[0].get_bounding_rect()).copy()

    def update(self, hero):
        target = 1.0 if self.pressed else 0.0
        self.press_amount += (target - self.press_amount) * 0.18
        if abs(target - self.press_amount) < 0.005:
            self.press_amount = target
        self.pulse = (self.pulse + 1) % 120

    def draw(self, screen):
        bottom = round(self.y + self.height)
        width = self.width
        height = max(7, self.plate.get_height() - round(5 * self.press_amount))
        top = bottom - height
        pygame.draw.rect(
            screen, (35, 37, 43), (round(self.x), bottom - 6, width, 6), border_radius=2
        )
        plate = pygame.transform.scale(self.plate, (width, height))
        screen.blit(plate, (round(self.x), top))
        # Amber idle indicator becomes a softly pulsing green when held down.
        color = (
            (96, 220 + int(25 * math.sin(self.pulse * 0.052)), 115)
            if self.pressed
            else (211, 153, 67)
        )
        pygame.draw.rect(
            screen, color, (round(self.x + 8), top + 3, width - 16, 3), border_radius=1
        )
        if self.pressed:
            pygame.draw.line(
                screen,
                (179, 255, 180),
                (round(self.x + 7), top),
                (round(self.x + width - 8), top),
                1,
            )
