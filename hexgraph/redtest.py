import sys
import redhex
import math


import pygame
from pygame.locals import *
import pygame_textinput

pygame.init()

SQRT_3 = 3**0.5
HEX_WIDTH = 36
HEX_HEIGHT = HEX_WIDTH * 2 / SQRT_3
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

hex_size = HEX_HEIGHT / 2


world_map = pygame.image.load("world_default_medium.jpg")
map_rect = world_map.get_rect()
map_size = map_rect.size

screen_size = map_rect.inflate(0, 100).size
screen = pygame.display.set_mode(screen_size)

map_rect.move_ip(0, 100)
print (map_rect)

menu_rect = Rect(0, 0, screen.get_width(), 100)
screen.fill(BLACK)
screen.blit(world_map, map_rect)

origin = redhex.Point(map_rect.x + HEX_WIDTH / 2, map_rect.y + HEX_HEIGHT / 2)
size = redhex.Point(hex_size, hex_size)
screen_layout = redhex.Layout(redhex.layout_pointy, size, origin)

map_height = 21
map_width = 28
hex_org = redhex.Hex(0, 0, 0)

#gf = pygame.font.Font('C:\WINDOWS\Fonts\ARIALN.TTF', 14)
gf = pygame.font.Font('C:/WINDOWS/Fonts/arial.TTF', 14)
gf.set_bold(1)


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
                            b.state = 1
                            self.state = b.extra
        self.render()
        return self.state

def draw_choices():
    pygame.draw.circle(screen, RED, (50, 50), 10, 0)

def draw_coord(hex_display, surf):
#        hex_d = redhex.Hex(q, r, 0)
    if hex_display == None:
        return
    (x, y) = redhex.hex_to_pixel(screen_layout, hex_display)
    (x, y) = (int(x), int(y))
    coord = "{},{}".format(hex_display.q, hex_display.r)
    coord_surf = gf.render(coord, 0, WHITE)
    (w, h) = coord_surf.get_size()
    x = x - w/2
    y = y - h/2
    surf.blit(coord_surf, (x, y))

#for r in range(map_height):
#    r_offset = math.floor(r/2)
#    for q in range(-r_offset, map_width - r_offset):
#        hex_d = redhex.Hex(q, r, 0)
#        (x, y) = redhex.hex_to_pixel(screen_layout, hex_d)
#        (x, y) = (int(x), int(y))
#        coord = "{},{}".format(q, r)
#        coord_surf = gf.render(coord, 0, WHITE)
#        (w, h) = coord_surf.get_size()
#        x = x - w/2
#        y = y - h/2
#        screen.blit(coord_surf, (x, y))
        #pygame.draw.circle(screen, BLACK, (x, y), 10, 0)


#for q in range(10):
#    for r in range(10):
#        hex_d = redhex.Hex(q, r, 0)
#        (x, y) = redhex.hex_to_pixel(screen_layout, hex_d)
#        (x, y) = (int(x), int(y))
#        pygame.draw.circle(screen, BLACK, (x, y), 10, 0)

def list_fonts():
    """List all fonts installed on the system.
  
    Returns a dictionary where the key is the font name and the value is the
    absolute path to the font file.
  
    """
  
    #pygame.font.init()
  
    d = {}
    fonts = pygame.font.get_fonts()
    for font in fonts:
        d[font] = pygame.font.match_font(font)
    return d

print( "Default: {}".format(pygame.font.get_default_font()))
for font, path in list_fonts().items():
        print ("{} - {}".format(font, path))

pygame.display.flip()


#textinput = pygame_textinput.TextInput()

# Initialise clock
clock = pygame.time.Clock()
mouse_hex = None
dm = DrawMenu(choices=[RED, BLUE, GREEN])
while 1:
    # Make sure game doesn't run at more than 60 frames per second
    clock.tick(60)
    events = pygame.event.get()
    screen.blit(world_map, map_rect)

    dm.update(events)
    screen.blit(dm.surface, menu_rect)

#    textinput.update(events)        
#    screen.blit(textinput.get_surface(), (10, 10))

    for event in events:
        
#        pygame.display.flip()
        
        if event.type == QUIT:
            sys.exit()

        elif event.type == MOUSEMOTION:
            if event.buttons:
                print("Buttons: {}".format(event.buttons))
                
                (x, y) = event.pos
                if map_rect.collidepoint(x, y):
                    click_pos = redhex.Point(x, y)
                    mouse_hex = redhex.pixel_to_hex(screen_layout, click_pos)
                    mouse_hex = redhex.hex_round(mouse_hex)
                
#                hex_line = redhex.hex_linedraw(hex_org, mouse_hex)
#                for painthex in hex_line:
#                    (x, y) = redhex.hex_to_pixel(screen_layout, painthex)
#                    (x, y) = (int(x), int(y))
#                    pygame.draw.circle(screen, BLACK, (x, y), 10, 0)
#                pygame.display.flip()
#            move_and_draw_all_game_objects()
    draw_coord(mouse_hex, screen)
    pygame.display.flip()