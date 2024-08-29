import pygame
from pygame.locals import *
from helper import *
import sys
pygame.init()
fps=120
fpsclock=pygame.time.Clock()
screen=pygame.display.set_mode((800,600))
def healthbar(health,curr_health):
    screen.blit(health[curr_health],(20,20))
    pygame.display.update()
    fpsclock.tick(fps)
