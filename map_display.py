import sys
import redhex
import math
import pygame
from pygame.locals import *
#import pygame_textinput
from sob.hexmap import HexMap
from sob.hexmap import Hex as SobHex
import time


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


class PosseMarker(object):
    def __init__(self, coord):
        self.set_coord(coord)


    def set_coord(self, coord):
        self._loc = redhex.Hex(q=coord[0], r=coord[1], s=coord[2])


    @property
    def coord(self):
        return (self._loc.q, self._loc.r, self._loc.s)

    @coord.setter
    def coord(self, coord):
        # TODO doesn't work. Why?
        self.set_coord(coord)


    def render(self, screen, screen_layout):
        (x, y) = redhex.hex_to_pixel(screen_layout, self._loc)
        (px, py) = (int(x), int(y))
        pygame.draw.circle(screen, GREEN, (px, py), int(HEX_WIDTH / 2), 3)





class MapDisplay():
    def __init__(self):
        pygame.init()

        #
        # List of artifacts to render
        #
        self.artifacts = []

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
        self.font = pygame.font.SysFont("Arial", 14)
        self.font.set_bold(1)

        #
        # Init the clock
        #
        self.clock = pygame.time.Clock()

    def add_artifact(self, artifact):
        self.artifacts.append(artifact)


    def get_click(self):
        while 1:
            # Make sure game doesn't run at more than 60 frames per second
            self.clock.tick(60)
            events = pygame.event.get()
            self.screen.blit(self.world_map, self.map_rect)

            for event in events:
                if event.type == QUIT:
                    sys.exit()
                if event.type == KEYDOWN:
                    print (event)
                    if (event.key == K_q or
                        event.key == K_ESCAPE):
                        return None

                if event.type == MOUSEBUTTONDOWN:
                    (x, y) = event.pos
                    if self.map_rect.collidepoint(x, y):
                        click_pos = redhex.Point(x, y)
                        mouse_hex = redhex.pixel_to_hex(self.screen_layout, click_pos)
                        mouse_hex = redhex.hex_round(mouse_hex)
                        
                        return mouse_hex

            for art in self.artifacts:
                art.render(self.screen, self.screen_layout)

            pygame.display.flip()


    def event_update(self):
        start = time.time()
        while 1:
            end = time.time()
            if end-start > 1:
                return
            # Make sure game doesn't run at more than 60 frames per second
            self.clock.tick(60)
            events = pygame.event.get()
            self.screen.blit(self.world_map, self.map_rect)

            for event in events:
            #     if event.type == QUIT:
            #         sys.exit()
            #     if event.type == KEYDOWN:
            #         print (event)
            #         if (event.key == K_q or
            #             event.key == K_ESCAPE):
            #             return

                if event.type == MOUSEBUTTONDOWN:
                    (x, y) = event.pos
                    if self.map_rect.collidepoint(x, y):
                        click_pos = redhex.Point(x, y)
                        mouse_hex = redhex.pixel_to_hex(self.screen_layout, click_pos)
                        mouse_hex = redhex.hex_round(mouse_hex)
                        
                        return mouse_hex

            #     elif event.type == MOUSEMOTION:
            #         if event.buttons:
            #             #print("Buttons: {}".format(event.buttons))
                        
            #             (x, y) = event.pos
            #             if self.map_rect.collidepoint(x, y):
            #                 click_pos = redhex.Point(x, y)
            #                 mouse_hex = redhex.pixel_to_hex(self.screen_layout, click_pos)
            #                 mouse_hex = redhex.hex_round(mouse_hex)
                        
            # # for coord, mhex in land_map.hexes.items():
            # #     (x, y) = redhex.hex_to_pixel(screen_layout, coord)
            # #     (x, y) = (int(x), int(y))
            # #     #print ("yep {}".format(mhex.__dict__))
            # #     hcolor = terrain_to_color[mhex.terrain]
            # #     pygame.draw.circle(screen, hcolor, (x, y), 10, 0)
            # #     #print ('{} - {}'.format(coord, mhex.__dict__))
            # pygame.draw.circle(self.screen, GREEN, (px, py), int(HEX_WIDTH / 2), 3)

            for art in self.artifacts:
                art.render(self.screen, self.screen_layout)

            pygame.display.flip()


    def circle_hex(self, coord):
        print(coord)
        hex_display = redhex.Hex(q=coord[0], r=coord[1], s=coord[2])
        (x, y) = redhex.hex_to_pixel(self.screen_layout, hex_display)
        (px, py) = (int(x), int(y))

        print ("{}, {}, {}".format(px, py, int(HEX_WIDTH / 2)))
        start = time.time()
        while 1:
            
            
            end = time.time()
            if end-start > 1:
                return
            # Make sure game doesn't run at more than 60 frames per second
            self.clock.tick(60)
            events = pygame.event.get()
            self.screen.blit(self.world_map, self.map_rect)

            for event in events:
                if event.type == QUIT:
                    sys.exit()
                if event.type == KEYDOWN:
                    print (event)
                    if (event.key == K_q or
                        event.key == K_ESCAPE):
                        return

                elif event.type == MOUSEBUTTONDOWN:
                    (x, y) = event.pos
                    if self.map_rect.collidepoint(x, y):
                        click_pos = redhex.Point(x, y)
                        mouse_hex = redhex.pixel_to_hex(self.screen_layout, click_pos)
                        mouse_hex = redhex.hex_round(mouse_hex)
                        map_hex = SobHex()

                elif event.type == MOUSEMOTION:
                    if event.buttons:
                        #print("Buttons: {}".format(event.buttons))
                        
                        (x, y) = event.pos
                        if self.map_rect.collidepoint(x, y):
                            click_pos = redhex.Point(x, y)
                            mouse_hex = redhex.pixel_to_hex(self.screen_layout, click_pos)
                            mouse_hex = redhex.hex_round(mouse_hex)
                        
            # for coord, mhex in land_map.hexes.items():
            #     (x, y) = redhex.hex_to_pixel(screen_layout, coord)
            #     (x, y) = (int(x), int(y))
            #     #print ("yep {}".format(mhex.__dict__))
            #     hcolor = terrain_to_color[mhex.terrain]
            #     pygame.draw.circle(screen, hcolor, (x, y), 10, 0)
            #     #print ('{} - {}'.format(coord, mhex.__dict__))
            pygame.draw.circle(self.screen, GREEN, (px, py), int(HEX_WIDTH / 2), 3)

            pygame.display.flip()

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

