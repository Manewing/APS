# Some globals
import numpy as np
import pygame

SMALL_FONT  = None
BIG_FONT    = None

def init():
    pygame.init()
    global SMALL_FONT, BIG_FONT
    # got some issues with SysFont ...
    #SMALL_FONT = pygame.font.SysFont('Times New Roman', 11)
    #BIG_FONT   = pygame.font.SysFont('Times New Roman', 25)
    SMALL_FONT = pygame.font.SysFont(None, 15)
    BIG_FONT   = pygame.font.SysFont(None, 25)

def rnd(x):
    return np.random.uniform(0, x) + ENV_OFF

def write_screen(screen, text, pos, color, font):
    screen.blit(font.render(text, True, color), pos)

RED         = (255,  75,   0, 0)
GREEN       = (100, 255,   0, 0)
BLUE        = (  0,  75, 255, 0)
YELLOW      = (255, 255,   0, 0)
BLACK       = (  0,   0,   0, 0)
WHITE       = (255, 255, 255, 0)

ENV_OFF     = 100
DELAY       = 45

init()
