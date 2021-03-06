import sys
import redhex
import math


import pygame
from pygame.locals import *
#import pygame_textinput
from sob.hexmap import HexMap
from sob.hexmap import Hex as SobHex

import json

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
#screen.fill(BLACK)
#screen.blit(world_map, map_rect)

origin = redhex.Point(map_rect.x + HEX_WIDTH / 2, map_rect.y + HEX_HEIGHT / 2)
size = redhex.Point(hex_size, hex_size)
screen_layout = redhex.Layout(redhex.layout_pointy, size, origin)

map_height = 21
map_width = 28
hex_org = redhex.Hex(0, 0, 0)

gf = pygame.font.SysFont("Arial", 14)
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


def save_map(tmap):
       
    tmap_save = []
    save_data = {'terrain_map' : tmap_save}
    for hcoord, mhex in tmap.hexes.items():
        coord = (hcoord.q, hcoord.r, hcoord.s)
        mhex.save_coord = coord
        tmap_save.append(mhex.__dict__)

    with open('terrain_map_save.json', 'w') as outfile:
        json.dump(save_data, outfile, sort_keys=True, indent=4)


def terrain_hex_json_factory(hex_json):
    thex = SobHex()
    print (hex_json)
    thex.terrain = hex_json['terrain']
    thex.rail = hex_json['rail']
    thex.river = hex_json['river']
    thex.road = hex_json['road']
    thex.town = hex_json['town']
    thex.mine = hex_json['mine']

    return thex

def load_map():
    with open('terrain_map_save.json', 'r') as infile:
        load_data = json.load(infile)
    print(load_data)
    hexes = load_data['terrain_map']
    load_map = HexMap()
    for h in hexes:
        thex = terrain_hex_json_factory(h)
        (q, r, s) = h['save_coord']
        coord = redhex.Hex(q, r, s)
        load_map.put_hex(coord, thex)

    return load_map


print( "Default: {}".format(pygame.font.get_default_font()))
for font, path in list_fonts().items():
        print ("{} - {}".format(font, path))

#pygame.display.flip()


#textinput = pygame_textinput.TextInput()

# Initialise clock
clock = pygame.time.Clock()

#Setup the map
land_map = HexMap()


mouse_hex = None
color_to_terrain = {
    GREEN : 1,
    BLUE : 2,
    RED : 3
}
terrain_to_color = {v: k for k, v in color_to_terrain.items()}

dm = DrawMenu(choices=[RED, BLUE, GREEN])
oldstate = None
while 1:
    # Make sure game doesn't run at more than 60 frames per second
    clock.tick(60)
    events = pygame.event.get()
    screen.blit(world_map, map_rect)

    state = dm.update(events)
    if state != oldstate:
        print (state)
        oldstate = state
    screen.blit(dm.surface, menu_rect)

#    textinput.update(events)        
#    screen.blit(textinput.get_surface(), (10, 10))

    for event in events:
        
#        pygame.display.flip()
        
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN:
            print (event)
            if event.key == K_s:
                save_map(land_map)
            if event.key == K_l:
                land_map = load_map()
        elif event.type == MOUSEBUTTONDOWN:
            (x, y) = event.pos
            if map_rect.collidepoint(x, y):
                click_pos = redhex.Point(x, y)
                mouse_hex = redhex.pixel_to_hex(screen_layout, click_pos)
                mouse_hex = redhex.hex_round(mouse_hex)
                map_hex = SobHex()
                print (state)
                if state:
                    #
                    #  Save the terrain selection to the hex
                    #
                    map_hex.terrain = color_to_terrain[state]
                    land_map.put_hex(mouse_hex, map_hex)
                    print ("added")
                else:
                    #
                    #  Print the hex
                    #
                    thex = land_map.hexes.get(mouse_hex)
                    if thex:
                        print(thex.__dict__)
                    else:
                        print("No Hex")

        elif event.type == MOUSEMOTION:
            if event.buttons:
                #print("Buttons: {}".format(event.buttons))
                
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
    for coord, mhex in land_map.hexes.items():
        (x, y) = redhex.hex_to_pixel(screen_layout, coord)
        (x, y) = (int(x), int(y))
        #print ("yep {}".format(mhex.__dict__))
        hcolor = terrain_to_color[mhex.terrain]
        pygame.draw.circle(screen, hcolor, (x, y), 10, 0)
        #print ('{} - {}'.format(coord, mhex.__dict__))
    pygame.display.flip()