import sys
import redhex
import math
import pygame
from pygame.locals import *
#import pygame_textinput
from sob.hexmap import HexMap
from sob.hexmap import Hex as SobHex


SQRT_3 = 3**0.5
HEX_WIDTH = 36
HEX_HEIGHT = HEX_WIDTH * 2 / SQRT_3
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Button:
    def __init__(self, name=None, button_rect=None, extra=None):
        self.name = name
        self.rect = button_rect
        self.extra = extra
        self.state = False
        self.focus = False

class DrawMenu:

    def __init__(self, button_size = (50, 50), choices = []):
        self.choices = choices
        self.button_rect = Rect((0, 0), button_size)
        self.space = button_size[0]
        self.state = None
        
        self.build()

    def build(self):
        num_choices = len(self.choices)
        width = self.button_rect.w * num_choices + self.space * (num_choices - 1)
        height = self.button_rect.h
        self.surface = pygame.Surface((width, height))

        b_rect = self.button_rect.copy()
        buttons = []
        for choice in self.choices:
            b = Button(button_rect=b_rect, extra=choice)
            b_rect = b_rect.move(b_rect.w + self.space, 0)
            buttons.append(b)
        self.buttons = buttons

    def render(self):

        self.surface.fill(BLACK)
        for b in self.buttons:
            pygame.draw.circle(self.surface, b.extra, b.rect.center, int(b.rect.w/2))
            if b.state == 1:
                pygame.draw.circle(self.surface, BLACK, b.rect.center, int(b.rect.w/4))
            if b.focus == 1:
                pygame.draw.rect(self.surface, b.extra, b.rect)

    def update(self, events):
        for event in events:
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    (x, y) = event.pos
                    for b in self.buttons:
                        if b.rect.collidepoint(x, y):
                            for b2 in self.buttons:
                                b2.state = 0
                            if b.extra != self.state:
                                #
                                # Change the state to this button
                                #
                                b.state = 1
                                self.state = b.extra
                            else:
                                #
                                # Selecting an active button.
                                # Clear the state of this button
                                #
                                self.state = None
        self.render()
        return self.state




class MapDisplay():
    def __init__(self):
        pygame.init()

        self.world_map = pygame.image.load("world_default_medium.jpg")
        self.map_rect = self.world_map.get_rect()

        hex_size = HEX_HEIGHT / 2

        screen_size = self.map_rect.inflate(0, 100).size
        self.screen = pygame.display.set_mode(screen_size)

        self.map_rect.move_ip(0, 100)

        self.menu_rect = Rect(0, 0, self.screen.get_width(), 100)

        origin = redhex.Point(self.map_rect.x + HEX_WIDTH / 2,
                              self.map_rect.y + HEX_HEIGHT / 2)
        size = redhex.Point(hex_size, hex_size)
        self.screen_layout = redhex.Layout(redhex.layout_pointy, size, origin)

        #Setup font
        self.font = pygame.font.Font('C:/WINDOWS/Fonts/arial.TTF', 14)
        self.font.set_bold(1)

        #
        # Init the clock
        #
        clock = pygame.time.Clock()

    def draw_coord(self, hex_display):
        if hex_display == None:
            return
        (x, y) = redhex.hex_to_pixel(self.screen_layout, hex_display)
        (x, y) = (int(x), int(y))
        coord = "{},{}".format(hex_display.q, hex_display.r)
        coord_surf = self.font.render(coord, 0, WHITE)
        #
        # Center the text in the hex
        #
        (w, h) = coord_surf.get_size()
        x = x - w/2
        y = y - h/2
        self.screen.blit(coord_surf, (x, y))

    def update(self):
        self.screen.blit(self.world_map, self.map_rect)
        pygame.display.flip()

