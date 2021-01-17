#!/usr/bin/env python
"""A UI session for a game of Deduce or DIe
"""
import sys
import datetime
import logging
import logging.handlers
import random
import copy
import argparse
import cmd
import os

from pathlib import Path

import dice
import sob.town as town
from sob.town import Town
#from dod_game import *
import json
#import map_display

import pygame
import pygame_gui

import redhex

import map_gui
from sob.game import HexCrawl

# Test Hexcrawl module components
DEFAULT_LOG_DIR = 'logs'
DEFAULT_LOGFILE = 'hexgame'
DEFAULT_LOG_LEVEL = 'INFO'

DEFAULT_SAVE_DIR = 'saves'


def setup_logging(log_level, log_file, conslog):

    global log
    global root_logger
    global console_handler

    levels = {'ERROR'   :logging.ERROR,
              'WARNING' :logging.WARNING,
              'INFO'    :logging.INFO,
              'DEBUG'   :logging.DEBUG}

    log_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(module)s.%(name)s.%(funcName)s] %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(levels[log_level])

    log_dir, log_filename = os.path.split(log_file)

    if not os.path.dirname(log_dir):
        #
        # If no directory in the filename then us the directory
        # indicated by the environment or default directory.
        #
        log_dir = os.getenv('PY_UTIL_LOG_DIR', DEFAULT_LOG_DIR)
        log_file = os.path.join(log_dir, log_filename + '.log')

    #
    # Check that the log directory exists
    #
    if log_dir and not os.path.exists(log_dir):
        #
        #  It doesn't.
        #  Create the directory
        #
        os.makedirs(log_dir)

    file_handler = logging.handlers.RotatingFileHandler(log_file, backupCount = 3)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    if os.path.isfile(log_file):
        #
        # Roll the old log
        #
        root_logger.info('------------- Close Log -------------')
        file_handler.doRollover()

    if conslog:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)

    log = logging.getLogger()
    return log_file

class HexcrawlController():
    def __init__(self, game, gui, default_save_dir):
        self.game = game
        self.gui = gui
        self.default_save_dir = default_save_dir

        self.running = True
        self.log = logging.getLogger()
        self.process_events_fn = self.state_main_menu

        save_path = Path(self.default_save_dir)
        
        if not save_path.exists():
            self.log.info("Creating save directory: ./{}".format(save_path))
            os.mkdir(save_path)

    def process_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            #
            # Let the underlying base GUI get some work done
            #
            self.gui.process_events(event)

            #
            # The current state processes the event.
            #
            self.process_events_fn(event)

    def state_get_posse_location(self, event):

        finished = False;

        #
        # Escape or Q will cancel the posse move
        #
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_q or
                event.key == pygame.K_ESCAPE):
                self.log.info("canceled-ESC: {}".format(event))
                finished = True;
                self.confirm_posse_loc.kill()


        if event.type == pygame.USEREVENT:
            #
            # Dialog confirmed.
            # Ignore it if a location hasn't been selected yet.
            #
            if event.user_type == pygame_gui.UI_CONFIRMATION_DIALOG_CONFIRMED: 

                try:
                    posse_art = self.gui.get_artifact('posse_target')
                    coord = posse_art.coord
                    desthex = redhex.Hex(q=coord[0], r=coord[1], s=coord[2])
                    self.game.posse.location = desthex
                    self.gui.get_artifact('posse').set_coord(desthex)
                    #self.display.event_update()
                    # self.gui.remove_artifact('posse_target')
                    self.log.info("Posse location set: {} [{}]".format(
                                self.game.location_string(desthex), desthex))
                except KeyError as e:
                    #
                    #  No location was selected.
                    #
                    None

            if event.user_type == pygame_gui.UI_WINDOW_CLOSE:
                self.log.info("canceled-CLOSE: {}".format(event))
                finished = True;

        if event.type == pygame.MOUSEBUTTONDOWN:
            (x, y) = event.pos
            #
            # check that the click was on the map and not in the confirmation dialog
            #
            if (self.gui.map_rect.collidepoint(x, y) and
                not self.confirm_posse_loc.check_clicked_inside_or_blocking(event)):

                click_pos = redhex.Point(x, y)
                mouse_hex = redhex.pixel_to_hex(self.gui.screen_layout, click_pos)
                mouse_hex = redhex.hex_round(mouse_hex)
                
                #
                # Add a marker for where the posse will end up.
                # TODO: Make this a different color from the current posse location
                #
                self.gui.add_artifact('posse_target', map_gui.PosseMarker(mouse_hex))

                self.log.info("Posse location: {} [{}]".format(
                    self.game.location_string(mouse_hex), mouse_hex))

        if finished:
            #
            # Clear out the selection indicator if a hex was selected
            #
            try:
                self.gui.remove_artifact('posse_target')
            except KeyError as e:
                #
                # Expected if no map hex was selected.
                #
                None
            #
            # Return to processing the main menu.
            #
            self.process_events_fn = self.state_main_menu
            self.confirm_posse_loc = None


    def state_create_game(self, event):

        #
        # The Dialog box will handle all the GUI events.
        # The state of the dialog box will tell us if we're done.
        #
        self.new_game_dialog.process_events(event)
        if self.new_game_dialog.canceled:
            #
            # Dialog canceled. Do not create a game.
            # Return to processing the main menu.
            #
            self.process_events_fn = self.state_main_menu
        elif self.new_game_dialog.completed:
            #
            # Create the new game
            #
            posse_name = self.new_game_dialog.text.strip()
            self.log.info("Creating a new game for posse: '{}', '{}'".format(self.new_game_dialog.text, posse_name))
            self.game.new_game(posse_name)

            #
            # Create a posse marker
            #
            self.gui.add_artifact('posse',
                map_gui.PosseMarker(self.game.posse.location))

            #
            # Return to processing the main menu.
            #
            self.process_events_fn = self.state_main_menu
            self.new_game_dialog = None

    def state_save_file(self, event):
        finished = False
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                self.log.info("Saving game to: {}".format(event.text))
                self.game.save_game(event.text)
                finished = True
        
            if event.user_type == pygame_gui.UI_WINDOW_CLOSE:
                self.log.info("Save Canceled")
                finished = True

        if finished:
            #
            # Return to processing the main menu.
            #
            self.process_events_fn = self.state_main_menu

    def state_load_file(self, event):
        finished = False
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_FILE_DIALOG_PATH_PICKED:
                self.log.info("Loading game from: {}".format(event.text))
                self.game.load_game(event.text)

                #
                # Create a new posse marker
                #
                self.gui.add_artifact('posse',
                map_gui.PosseMarker(self.game.posse.location))

                finished = True
            
            if event.user_type == pygame_gui.UI_WINDOW_CLOSE:
                self.log.info("Load Canceled")
                finished = True

        if finished:
            #
            # Return to processing the main menu.
            #
            self.process_events_fn = self.state_main_menu


    def state_main_menu(self, event):

        #
        #  Process events for the main button panel
        #
        if event.type == pygame.USEREVENT:

            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:

                if event.ui_element == self.gui.game_button:
                    #
                    # Get the posse name and create a new game.
                    #
                    self.new_game_dialog = game_display.get_posse_name_dialog()

                    #
                    # The posse dialog is modal so disable everything else.
                    # Do this by changing the controller state to only deal
                    # with the game creation events.
                    #
                    self.process_events_fn = self.state_create_game

                    self.log.info("New Game")

                if event.ui_element == self.gui.posse_button:

                    if not self.game.started:
                        message_rect = pygame.Rect(-1,-1,-1,-1)
                        pygame_gui.windows.UIMessageWindow(message_rect,"No game has been started",self.gui.ui_manager)

                    else:
                        message_rect = pygame.Rect(-1,-1,-1,-1)
                        self.confirm_posse_loc = pygame_gui.windows.UIConfirmationDialog(message_rect,self.gui.ui_manager,"Select the new Posse location on the map")
                        self.confirm_posse_loc.set_blocking(False)
#                        print(self.confirm_posse_loc.__dict__)

                        self.process_events_fn = self.state_get_posse_location

                if event.ui_element == self.gui.save_button:
                    if not self.game.started:
                        message_rect = pygame.Rect(-1,-1,-1,-1)
                        pygame_gui.windows.UIMessageWindow(message_rect,"No game has been started",self.gui.ui_manager)
                    else:
                        self.file_dialog = pygame_gui.windows.UIFileDialog(pygame.Rect(160, 50, 440, 500),
                                                        self.gui.ui_manager,
                                                        window_title='Save Game...',
                                                        initial_file_path=self.default_save_dir)
                                                        #allow_existing_files_only=True)

                        self.process_events_fn = self.state_save_file

                if event.ui_element == self.gui.load_button:

                    if self.game.started:
                        message_rect = pygame.Rect(0,0,250,250)
                        pygame_gui.windows.UIMessageWindow(message_rect,"A game is in progress. </b>Restart the application to load a game",self.gui.ui_manager)

                    else:
                        self.file_dialog = pygame_gui.windows.UIFileDialog(pygame.Rect(160, 50, 440, 500),
                                                        self.gui.ui_manager,
                                                        window_title='Load Game...',
                                                        initial_file_path=self.default_save_dir,
                                                        allow_existing_files_only=True)

                        self.process_events_fn = self.state_load_file

    def run(self):
        while self.running:
            time_delta = self.gui.clock.tick() / 1000.0

            #
            # check for input
            #
            self.process_events()

            #
            # respond to input
            #
            self.gui.ui_manager.update(time_delta)

            #
            # draw the map and artifacts.
            #
            self.gui.screen.blit(self.gui.background_surface, (0, 0))
            for art in self.gui.artifacts.values():
                art.render(self.gui.screen, self.gui.screen_layout)

            #
            # Draw the button panel.
            #
            self.gui.ui_manager.draw_ui(self.gui.screen)

            pygame.display.update()

#
# main
#
parser = argparse.ArgumentParser(description='Track a Hexcrawl game session')

parser.add_argument('--logfile', dest='log_file', default=DEFAULT_LOGFILE,
                        help='The path and name of the log file. Default={}_<timestamp>.log'.format(DEFAULT_LOGFILE))
parser.add_argument('--level', dest='log_level', default=DEFAULT_LOG_LEVEL,
                        help='Set the log level for the application log. ' \
                             '[ERROR, WARN, INFO, DEBUG] Default={}'.format(DEFAULT_LOG_LEVEL))
#parser.add_argument( 'num_players', help='Number of players (3-6)')


args = parser.parse_args()

time_now = datetime.datetime.now()
#
# TODO make logging to the console false by default. Add a command line option to turn it on.
#
full_log_file = setup_logging(args.log_level, args.log_file, True)


log.info("Game Start")

#
# Create game
#
game = HexCrawl()

#
#  Setup and display the map
#
game_display  = map_gui.GameGui()
game_controller = HexcrawlController(game, game_display, DEFAULT_SAVE_DIR)
game_controller.run()
