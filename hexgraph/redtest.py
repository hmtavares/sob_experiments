import sys
import redhex
import math


import pygame
from pygame.locals import *


pygame.init()

SQRT_3 = 3**0.5
HEX_WIDTH = 36
HEX_HEIGHT = HEX_WIDTH * 2 / SQRT_3
BLACK = (0, 0, 0)

hex_size = HEX_HEIGHT / 2


ball = pygame.image.load("world_default_medium.jpg")
ballrect = ball.get_rect()
ballsize = ballrect.size
screen = pygame.display.set_mode(ballsize)
screen.fill(BLACK)
screen.blit(ball, ballrect)

origin = redhex.Point(HEX_WIDTH / 2, HEX_HEIGHT / 2)
size = redhex.Point(hex_size, hex_size)
screen_layout = redhex.Layout(redhex.layout_pointy, size, origin)

map_height = 21
map_width = 28
hex_org = redhex.Hex(0, 0, 0)

#for r in range(map_height):
#    r_offset = math.floor(r/2)
#    for q in range(-r_offset, map_width - r_offset):
#        hex_d = redhex.Hex(q, r, 0)
#        (x, y) = redhex.hex_to_pixel(screen_layout, hex_d)
#        (x, y) = (int(x), int(y))
#        pygame.draw.circle(screen, BLACK, (x, y), 10, 0)


#for q in range(10):
#    for r in range(10):
#        hex_d = redhex.Hex(q, r, 0)
#        (x, y) = redhex.hex_to_pixel(screen_layout, hex_d)
#        (x, y) = (int(x), int(y))
#        pygame.draw.circle(screen, BLACK, (x, y), 10, 0)


pygame.display.flip()

# Initialise clock
clock = pygame.time.Clock()

while 1:
    # Make sure game doesn't run at more than 60 frames per second
    clock.tick(60)

    for event in pygame.event.get():
        
        if event.type in (pygame.QUIT, pygame.KEYDOWN):
            sys.exit()
        elif event.type == MOUSEMOTION:
#            if event.button == 1:
            screen.blit(ball, ballrect)
            (x, y) = event.pos
            click_pos = redhex.Point(x, y)
            mouse_hex = redhex.pixel_to_hex(screen_layout, click_pos)
            mouse_hex = redhex.hex_round(mouse_hex)
            hex_line = redhex.hex_linedraw(hex_org, mouse_hex)
            for painthex in hex_line:
                (x, y) = redhex.hex_to_pixel(screen_layout, painthex)
                (x, y) = (int(x), int(y))
                pygame.draw.circle(screen, BLACK, (x, y), 10, 0)
            pygame.display.flip()
#            move_and_draw_all_game_objects()

