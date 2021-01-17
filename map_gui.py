#
#
#

# import sys
import logging

import redhex
import map_display
# import math
# import pygame
# from pygame.locals import *
# #import pygame_textinput
# from sob.hexmap import HexMap
# from sob.hexmap import Hex as SobHex
# import time

import pygame
import pygame_gui

SQRT_3 = 3**0.5
HEX_WIDTH = 36
HEX_HEIGHT = HEX_WIDTH * 2 / SQRT_3
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


#================= Artifacts ==================

#
# TODO: Put artifacts in a separate file
#
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


class RectMarker(object):
    def __init__(self, rect):
        self.rect = rect


    def render(self, screen, screen_layout):

        pygame.draw.rect(screen, (0,0,255), self.rect)



#
# Collect a line of text
#
class TextLineDialog(pygame_gui.elements.UIWindow):
    def __init__(self, dialog_rect, title, label_text, id, ui_manager):
        super().__init__(dialog_rect, ui_manager,
                     window_display_title=title,
                     object_id=id,
                     resizable=False)

        self.log = logging.getLogger()

        label_rect = pygame.Rect(0,0,100, 20)
        text_rect = label_rect.move(label_rect.width+10,0)

        text_rect.width = dialog_rect.width - text_rect.left - 50

        pygame_gui.elements.UILabel(
            label_rect,
            label_text,
            manager=self.ui_manager,
            container=self)

        self.text_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=text_rect,
            manager = self.ui_manager,
            container=self)
        self.text_entry.focus()

        #
        # TODO OK and Cancel buttons
        #

        self.canceled = False
        self.completed = False
        self.text = None

    def process_events(self, event):
        if event.type == pygame.USEREVENT:
            if (event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
                event.ui_element == self.text_entry):
                print(event.text)
                self.completed = True
                self.text = event.text
                self.kill()

            if event.user_type == pygame_gui.UI_WINDOW_CLOSE:
                self.canceled = True
            #
            # TODO Deal with OK and Cancel buttons
            #

            # if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            #     print(event)
            #     print(event.ui_element)
            #     if event.ui_element == self.game_button:
            #         self.move_posse = True

            #     if event.ui_element == self.posse_button:
            #         self.move_posse = True

class GameGui():

    def __init__(self):
        self.running = True
        self.move_posse = False

        self.log = logging.getLogger()

        pygame.init()
        pygame.display.set_caption("HexCrawl")

        #
        # Map of artifacts to render
        #
        self.artifacts = {}

        self.world_map = pygame.image.load("world_default_medium.jpg")
        self.map_rect = self.world_map.get_rect()

        hex_size = HEX_HEIGHT / 2

        menu_height = 100

        screen_size = self.map_rect.inflate(0, menu_height).size
        self.screen = pygame.display.set_mode(screen_size,)
        
        self.background_surface = None
        
        self.map_rect.move_ip(0, menu_height)
        self.menu_rect = pygame.Rect(0, 0, self.screen.get_width(), menu_height)

        origin = redhex.Point(self.map_rect.x + HEX_WIDTH / 2,
                              self.map_rect.y + HEX_HEIGHT / 2)
        size = redhex.Point(hex_size, hex_size)
        self.screen_layout = redhex.Layout(redhex.layout_pointy, size, origin)

        print(self.screen.get_size())
        # self.ui_manager = pygame_gui.UIManager(self.screen.get_size(),
        #                             pygame_gui.PackageResource(package='data.themes',
        #                                             resource='theme_2.json'))
        self.ui_manager = pygame_gui.UIManager(self.screen.get_size())

        self.ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 10, 'style': 'bold'},
                                       {'name': 'fira_code', 'point_size': 10, 'style': 'regular'},
                                       {'name': 'fira_code', 'point_size': 10, 'style': 'italic'},
                                       {'name': 'fira_code', 'point_size': 14, 'style': 'italic'},
                                       {'name': 'fira_code', 'point_size': 14, 'style': 'bold'}
                                       ])
        #Setup font
        # self.font = pygame.font.SysFont("Arial", 14)
        # self.font.set_bold(1)

        self.recreate_ui()

        #
        # Init the clock
        #
        self.clock = pygame.time.Clock()

    def recreate_ui(self):
        self.ui_manager.set_window_resolution(self.screen.get_size())
        self.ui_manager.clear_and_reset()

        self.background_surface = pygame.Surface(self.screen.get_size())
        self.background_surface.blit(self.world_map, self.map_rect)

        #
        # A panel to house all the game option buttons.
        #
        self.menu_panel = pygame_gui.elements.UIPanel(
            self.menu_rect, 0, self.ui_manager)

        button_width = 100
        button_height = 40
        button_x_border = 30
        button_y_border = 20
        button_x_space = 20
        button_y_space = 20

        button_rect = pygame.Rect(0, 0, button_width, button_height)

        button_x = button_x_border
        button_y = button_y_border

        draw_rect = button_rect.move(button_x_border, button_y_border)
        self.game_button = pygame_gui.elements.UIButton(
            draw_rect,
            'New Game',
            self.ui_manager,
            container=self.menu_panel)

        draw_rect = draw_rect.move(button_x_space + button_width, 0)
        self.posse_button = pygame_gui.elements.UIButton(
            draw_rect,
            'Posse',
            self.ui_manager,
            container=self.menu_panel)

        draw_rect = draw_rect.move(button_x_space + button_width, 0)
        self.save_button = pygame_gui.elements.UIButton(
            draw_rect,
            'Save',
            self.ui_manager,
            container=self.menu_panel)

        draw_rect = draw_rect.move(button_x_space + button_width, 0)
        self.load_button = pygame_gui.elements.UIButton(
            draw_rect,
            'Load',
            self.ui_manager,
            container=self.menu_panel)




    def process_events(self, event):
        self.ui_manager.process_events(event)



    def get_posse_name_dialog(self):
        return TextLineDialog(pygame.Rect(((100,100),(300,300))),
                              'Posse Name',
                              'Posse Name:',
                              '#new_game_dialog',
                              self.ui_manager)

    def add_artifact(self, art_id, artifact):
        self.artifacts[art_id] = artifact

    def get_artifact(self, art_id):
        return self.artifacts[art_id]

    def remove_artifact(self, art_id):
        return self.artifacts.pop(art_id)

    # def get_click(self):
    #     while 1:
    #         # Make sure game doesn't run at more than 60 frames per second
    #         self.clock.tick(60)
    #         events = pygame.event.get()
    #         self.screen.blit(self.world_map, self.map_rect)

    #         for event in events:
    #             if event.type == QUIT:
    #                 sys.exit()
    #             if event.type == KEYDOWN:
    #                 print (event)
    #                 if (event.key == K_q or
    #                     event.key == K_ESCAPE):
    #                     return None

    #             if event.type == MOUSEBUTTONDOWN:
    #                 (x, y) = event.pos
    #                 if self.map_rect.collidepoint(x, y):
    #                     click_pos = redhex.Point(x, y)
    #                     mouse_hex = redhex.pixel_to_hex(self.screen_layout, click_pos)
    #                     mouse_hex = redhex.hex_round(mouse_hex)
                        
    #                     return mouse_hex

    #         for art in self.artifacts.values():
    #             art.render(self.screen, self.screen_layout)

    #         pygame.display.flip()


    # def event_update(self):
    #     start = time.time()
    #     while 1:
    #         end = time.time()
    #         if end-start > 1:
    #             return
    #         # Make sure game doesn't run at more than 60 frames per second
    #         self.clock.tick(60)
    #         events = pygame.event.get()
    #         self.screen.blit(self.world_map, self.map_rect)

    #         for event in events:
    #         #     if event.type == QUIT:
    #         #         sys.exit()
    #         #     if event.type == KEYDOWN:
    #         #         print (event)
    #         #         if (event.key == K_q or
    #         #             event.key == K_ESCAPE):
    #         #             return

    #             if event.type == MOUSEBUTTONDOWN:
    #                 (x, y) = event.pos
    #                 if self.map_rect.collidepoint(x, y):
    #                     click_pos = redhex.Point(x, y)
    #                     mouse_hex = redhex.pixel_to_hex(self.screen_layout, click_pos)
    #                     mouse_hex = redhex.hex_round(mouse_hex)
                        
    #                     return mouse_hex

    #         #     elif event.type == MOUSEMOTION:
    #         #         if event.buttons:
    #         #             #print("Buttons: {}".format(event.buttons))
                        
    #         #             (x, y) = event.pos
    #         #             if self.map_rect.collidepoint(x, y):
    #         #                 click_pos = redhex.Point(x, y)
    #         #                 mouse_hex = redhex.pixel_to_hex(self.screen_layout, click_pos)
    #         #                 mouse_hex = redhex.hex_round(mouse_hex)
                        
    #         # # for coord, mhex in land_map.hexes.items():
    #         # #     (x, y) = redhex.hex_to_pixel(screen_layout, coord)
    #         # #     (x, y) = (int(x), int(y))
    #         # #     #print ("yep {}".format(mhex.__dict__))
    #         # #     hcolor = terrain_to_color[mhex.terrain]
    #         # #     pygame.draw.circle(screen, hcolor, (x, y), 10, 0)
    #         # #     #print ('{} - {}'.format(coord, mhex.__dict__))
    #         # pygame.draw.circle(self.screen, GREEN, (px, py), int(HEX_WIDTH / 2), 3)

    #         for art in self.artifacts.values():
    #             art.render(self.screen, self.screen_layout)

    #         pygame.display.flip()


    # def circle_hex(self, coord):
    #     print(coord)
    #     hex_display = redhex.Hex(q=coord[0], r=coord[1], s=coord[2])
    #     (x, y) = redhex.hex_to_pixel(self.screen_layout, hex_display)
    #     (px, py) = (int(x), int(y))

    #     print ("{}, {}, {}".format(px, py, int(HEX_WIDTH / 2)))
    #     start = time.time()
    #     while 1:
            
            
    #         end = time.time()
    #         if end-start > 1:
    #             return
    #         # Make sure game doesn't run at more than 60 frames per second
    #         self.clock.tick(60)
    #         events = pygame.event.get()
    #         self.screen.blit(self.world_map, self.map_rect)

    #         for event in events:
    #             if event.type == QUIT:
    #                 sys.exit()
    #             if event.type == KEYDOWN:
    #                 print (event)
    #                 if (event.key == K_q or
    #                     event.key == K_ESCAPE):
    #                     return

    #             elif event.type == MOUSEBUTTONDOWN:
    #                 (x, y) = event.pos
    #                 if self.map_rect.collidepoint(x, y):
    #                     click_pos = redhex.Point(x, y)
    #                     mouse_hex = redhex.pixel_to_hex(self.screen_layout, click_pos)
    #                     mouse_hex = redhex.hex_round(mouse_hex)
    #                     map_hex = SobHex()

    #             elif event.type == MOUSEMOTION:
    #                 if event.buttons:
    #                     #print("Buttons: {}".format(event.buttons))
                        
    #                     (x, y) = event.pos
    #                     if self.map_rect.collidepoint(x, y):
    #                         click_pos = redhex.Point(x, y)
    #                         mouse_hex = redhex.pixel_to_hex(self.screen_layout, click_pos)
    #                         mouse_hex = redhex.hex_round(mouse_hex)
                        
    #         # for coord, mhex in land_map.hexes.items():
    #         #     (x, y) = redhex.hex_to_pixel(screen_layout, coord)
    #         #     (x, y) = (int(x), int(y))
    #         #     #print ("yep {}".format(mhex.__dict__))
    #         #     hcolor = terrain_to_color[mhex.terrain]
    #         #     pygame.draw.circle(screen, hcolor, (x, y), 10, 0)
    #         #     #print ('{} - {}'.format(coord, mhex.__dict__))
    #         pygame.draw.circle(self.screen, GREEN, (px, py), int(HEX_WIDTH / 2), 3)

    #         pygame.display.flip()

    # def draw_coord(self, hex_display):
    #     if hex_display == None:
    #         return
    #     (x, y) = redhex.hex_to_pixel(self.screen_layout, hex_display)
    #     (x, y) = (int(x), int(y))
    #     coord = "{},{}".format(hex_display.q, hex_display.r)
    #     coord_surf = self.font.render(coord, 0, WHITE)
    #     #
    #     # Center the text in the hex
    #     #
    #     (w, h) = coord_surf.get_size()
    #     x = x - w/2
    #     y = y - h/2
    #     self.screen.blit(coord_surf, (x, y))

    # def update(self):
    #     self.screen.blit(self.world_map, self.map_rect)
    #     pygame.display.flip()

    def run(self):
        while self.running:
            time_delta = self.clock.tick() / 1000.0
            # self.time_delta_stack.append(time_delta)
            # if len(self.time_delta_stack) > 2000:
            #     self.time_delta_stack.popleft()

            # check for input
            self.process_events()

            # respond to input
            self.ui_manager.update(time_delta)

            # if len(self.time_delta_stack) == 2000:
            #     self.fps_counter.set_text(
            #         f'FPS: {min(999.0, 1.0/max(sum(self.time_delta_stack)/2000.0, 0.0000001)):.2f}')
            #     self.frame_timer.set_text(f'frame_time: {sum(self.time_delta_stack)/2000.0:.4f}')

            # draw graphics
            self.screen.blit(self.background_surface, (0, 0))
            for art in self.artifacts.values():
                art.render(self.screen, self.screen_layout)

            self.ui_manager.draw_ui(self.screen)

            pygame.display.update()