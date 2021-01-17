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

DEFAULT_LOGFILE = 'logs/hexgame'
DEFAULT_LOG_LEVEL = 'INFO'

DEFAULT_SAVE_DIR = 'saves'


def setup_logging(log_level, log_filename, conslog):

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

    if os.path.dirname(log_filename):
        #
        # If the log_filename provides a path, use that
        #
        
        log_file = log_filename + '.log'
    else:
        #
        # If no directory in the filename then us the directory
        # indicated by the environment or default directory.
        #

        log_dir = os.getenv('PY_UTIL_LOG_DIR', DEFAULT_LOGFILE)
        log_file = os.path.join(log_dir, log_filename + '.log')

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


# def setup_logging(time_now, log_level, log_file):

#     global log
#     global root_logger
#     global console_handler

#     timestamp_now = time_now.strftime('%Y%m%d_%H%M%S')

#     levels = {'ERROR'   :logging.ERROR,
#               'WARNING' :logging.WARNING,
#               'INFO'    :logging.INFO,
#               'DEBUG'   :logging.DEBUG}

#     log_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(module)s.%(name)s.%(funcName)s] %(message)s')
#     root_logger = logging.getLogger()
#     root_logger.setLevel(levels[log_level])

#     log_path, log_filename = os.path.split(log_file)
#     log_filename = log_filename + '_' + timestamp_now + '.log'
#     #
#     # Check for an actual log filename
#     #
#     if not log_filename:
#         raise ValueError("Log file path must include a filename")

#     #
#     # Check that the log directory exists
#     #
#     if log_path and not os.path.exists(log_path):
#         #
#         #  It doesn't.
#         #  Create the directory
#         #
#         os.makedirs(log_path)
    
#     log_file = os.path.join(log_path, log_filename)
#     file_handler = logging.FileHandler(log_file)
#     file_handler.setFormatter(log_formatter)
#     root_logger.addHandler(file_handler)

#     log = logging.getLogger()
#     return log_file

parser = argparse.ArgumentParser(description='Track a Hexcrawl game session')

parser.add_argument('--logfile', dest='log_file', default=DEFAULT_LOGFILE,
                        help='The path and name of the log file. Default={}_<timestamp>.log'.format(DEFAULT_LOGFILE))
parser.add_argument('--level', dest='log_level', default=DEFAULT_LOG_LEVEL,
                        help='Set the log level for the application log. ' \
                             '[ERROR, WARN, INFO, DEBUG] Default={}'.format(DEFAULT_LOG_LEVEL))
#parser.add_argument( 'num_players', help='Number of players (3-6)')


args = parser.parse_args()

time_now = datetime.datetime.now()
full_log_file = setup_logging(args.log_level, args.log_file, True)


log.info("Game Start")

class HexcrawlCommands(cmd.Cmd):
    """Command processor for Shadows of Brimstone Hexcrawl"""

    def __init__(self, game, the_map):
        """Create a command processor for testing Hexcrawl


        Args: None

        Returns:
            An initilized command processor for Hexcrawl

        Raises: None

        """
        self.log = logging.getLogger(self.__class__.__name__)

        self.game = game
        self.display = the_map
        self.posse = None
        self.setup_parsers()

        cmd.Cmd.__init__(self)


    def setup_parsers(self):
        #
        # Show parser
        #
        # show [town, posse]
        self.show_parser = argparse.ArgumentParser(description='Show game element details',
                                                   prog='show')
        subparsers = self.show_parser.add_subparsers(dest='command')
        subparsers.required = True

        #        
        # show town <town name/id>
        #
        town_parser = subparsers.add_parser("town", help='Show the details for the specified town')
        town_parser.set_defaults(func=self.show_town)
        town_parser.add_argument('name', help='The name of the town to show.')

        #
        # show posse
        #
        posse_parser = subparsers.add_parser("posse", help='show the Posse details')
        posse_parser.set_defaults(func=self.show_posse)

        #
        # Job parser
        #
        # job {show, set, refresh}
        self.job_parser = argparse.ArgumentParser(description='Job operations',
                                                  prog='job')
        subparsers = self.job_parser.add_subparsers(dest = 'command')
        subparsers.required = True
        #        
        # job show <town name/id>
        #
        job_parser = subparsers.add_parser("show", help="Show the jobs for a town")
        job_parser.set_defaults(func=self.show_jobs)

        job_parser.add_argument('name',
                        help='The town to show jobs for.')

        #        
        # job set <none>
        #
        job_parser = subparsers.add_parser("set", help="Set the job for the posse")
        job_parser.set_defaults(func=self.set_job)

        job_parser.add_argument('id',
                        help='The ID of the job to add to the Posse.')

        #        
        # job refresh <town name/id>
        #
        job_parser = subparsers.add_parser("refresh", help="Refresh the jobs at a town")
        job_parser.set_defaults(func=self.refresh_jobs)

        job_parser.add_argument('-s', dest = 'show', action='store_true',
                        help='Show the jobs after refresh')
        job_parser.add_argument('name',
                        help='The town refresh')


        #
        # Loot Parser
        #
        self.loot_parser = argparse.ArgumentParser(description='Draw loot after a fight')        
        self.loot_parser.add_argument('members', type=int, help='Number of members in posse')
        self.loot_parser.add_argument('cards', type=int, help='Number of cards to draw for each member')

        #
        # Scavenge Parser
        #
        self.scavenge_parser = argparse.ArgumentParser(description='Draw scavenge cards')        
        self.scavenge_parser.add_argument('cards', type=int, help='Number of cards to draw')


    def do_newgame(self, line):
        """Create a new Hexcrawl game session

        newgame {Posse name}<cr>
        Parameters: 
            Posse name: [optional] The name of the Posse for the game
        
        Create all town locations.
        Randomly place the Posse

        If there is an existing game session it will be replaced with
        the new session. Save before running this command.
        """
        posse_name = line.strip()
        self.game.new_game(posse_name)
        #
        # Create a posse marker
        #
        self.display.add_artifact('posse',
            map_display.PosseMarker(self.game.posse.location))

        self.display.event_update()

    def do_jumpposse(self, line):
        """Place the Posse at a new location

        jumpposse <cr>
        Parameters: None
        
        Control moves to the GUI map display. When a hex is clicked
        the posse will be moved to that hex.

        Note that the CLI will not respond until a hex has been clicked.

        TODO: Allow a mine name, town name or coordinate to be provided
              on the command line
        """

        if not self.game.started:
            message_rect = pygame.Rect(0,0,200,200)
            pygame_gui.windows.UIMessageWindow(message_rect,"Just a message",self.gui.ui_manager)
            print ("Start or load a game")
            return

        print("Select the new Posse location on the map")
        desthex = self.display.get_click()
        #
        # If we got a destination set it.
        # Otherwise leave the Posse where it is.
        #
        if desthex:
            self.game.posse.location = desthex
            self.display.get_artifact('posse').set_coord(desthex)
            self.display.event_update()
            print("Posse location set: {} [{}]".format(
                self.game.location_string(desthex), desthex))
        else:
            print("No location selected")

    def do_show(self, line):
        """Show details of a game element

        show [town, posse]

        show town <town> <cr>
        Parameters: town - Town name or id
        
        Print the details of the town named in the command.

        * Name / location
        * Size
        * Kind of town
        * Hexcrawl trait
        * List of buildings

        Note: The entire name does not need to be typed in.
              e.g. 'show Fri' will show Fringe.
              Multiple matches will show all matches.
              e.g. 'show Fort' will show Fort Burke, Fort Lopez
              and Fort Landy

        show posse
        Parameters: None

        Print the details of the Posse

        """
        if not self.game.started:
            print ("Start or load a game")
            return

        try:
            show_args = self.show_parser.parse_args(line.split())
        except SystemExit as e:
            #
            # Gross but it's the only way to prevent
            # a command error from dumping out of the
            # entire application.
            #
            return

        show_args.func(show_args)


    def show_town(self, town_args):
        """Show the details of a town
        Parameters:
            town_args - The parse_arg argument object

        This is used by the do_show() parser
        """
        try:
            town = self.args_to_town(town_args)
        except ValueError as e:
            print (e)
            return

        print(town)            

    def show_posse(self, posse_args):
        """Show the details of a posse
        Parameters:
            town_args - The parse_arg argument object

        This is used by the do_show() parser
        """

        print(self.game.posse)

    def do_mission(self, line):
        """Set a mission for the Posse

        Pararmeters:
            line - The text description for the mission

        The map graphic will be activated and the destination
        for the mission can be set. The ESC key will cancel
        the map action and save the mission with no location.
        """
        self.game.posse.mission_text = line

        print("Select the mission location on the map")
        mission_hex = self.display.get_click()
        #
        # If we got a hex set it.
        # Otherwise no location
        #
        self.game.posse.mission_loc = None
        if mission_hex:
            self.game.posse.mission_loc = mission_hex
            print(mission_hex)
            print("Mission location set: {} [{}]".format(
                self.game.location_string(mission_hex), mission_hex))
        else:
            print("No location selected")


    def do_job(self, line):
        """Job operations

        show [show, set, refresh]

        job show <town>
        Parameters: town - Town name or id
        
        Print the Jobs at that town

        job set <job id>
        Parameters: job id: The 'roll' from the job chart for the job

        Make that job thte current posse job

        job refresh <town>
        Parameters: town - Town name or id

        Generate a new set of jobs for the town. May result in a Mandatory job.

        Note: The entire name does not need to be typed in for a town.
              e.g. 'jow show Fri' will show Fringe.

              Multiple matches will show all matches.
              e.g. 'job show Fort' will show Fort Burke, Fort Lopez
              and Fort Landy

              The command line does not support spaces in names so just use
              a unique portion for multi-word names
              e.g. 'job show Fort Burk' will result in an error use
                   'job show Burk' instead.

        """
        if not self.game.started:
            print ("Start or load a game")
            return

        try:
            job_args = self.job_parser.parse_args(line.split())
        except SystemExit as e:
            #
            # Gross but it's the only way to prevent
            # a command error from dumping out of the
            # entire application.
            #
            return

        job_args.func(job_args)


    def set_job(self, job_args):
        """Set a job for the Posse
        Parameters:
            job_args - The parse_arg argument object

        The map graphic will be activated and the destination
        for the job can be set. The ESC key will cancel
        the map action and save the job with no location.
        """
        job_id = job_args.id
        try:
            self.game.posse.job_id = int(job_id)
        except ValueError:
            print("Job key must be an integer")
            return

        print("Select the job location on the map")
        job_hex = self.display.get_click()
        #
        # If we got a hex set it.
        # Otherwise no location
        #
        self.game.posse.job_loc = None
        if job_hex:
            self.game.posse.job_loc = job_hex
            print("Job location set: {} [{}]".format(
                self.game.location_string(job_hex), job_hex))
        else:
            print("No location selected")


    def show_jobs(self, job_args):
        """Show the jobs in a town
        Parameters:
            job_args - The parse_arg argument object

        This is used by the do_show() parser
        """
        try:
            town = self.args_to_town(job_args)
        except ValueError as e:
            print (e.message)
            return

        self.print_jobs(town)

    def print_jobs(self, town):
        """Print the jobs for a town

        """
        if len(town.job) == 1:
            #
            # Single mandatory job
            #
            job_str = '''
MANDATORY JOB:
  [{}] {}'''.format(town.job[0]['id'], town.job[0]['title'])
        else:
            #
            # 3 Optional jobs
            #
            job_str = "Town Jobs:\n"
            for job in town.job:
                job_str += "  [{}] {}\n".format(job['id'], job['title'])

        print(job_str)



    def args_to_town(self, town_name_args):
        """Given parser args with a town id or name in 'name'
           Get the town or raise a ValueError
        """
        tn_name = town_name_args.name

        towns = self.game.towns
        town = None
        try:
            tn_id = int(tn_name)
            town = towns[tn_id]
        except ValueError:
            #
            # The arg wasn't a number
            # Try it as a name
            #
            for tn in towns.values():
                if tn_name in tn.name:
                    town = tn
                    break
        except KeyError:
            #
            # The arg was a number but
            # not a valid town key.
            #
            # We'll handle the error later
            # in the function
            #
            pass


        if not town:
            raise ValueError("Unknown Town -  {}".format(tn_name))
        
        return town



    def refresh_jobs(self, job_args):
        """Refresh the jobs in a town
        Parameters:
            job_args - The parse_arg argument object

        Used to reset the jobs in a town when re-visiting
        """
        try:
            town = self.args_to_town(job_args)
        except ValueError as e:
            print (e.message)
            return

        town.update_jobs(self.game.jobs, self.game.mandatory_jobs)

    def do_loot(self, line):
        """Draw Loot cards for the Posse

        loot ...
        
        Draw the specified number of loot cards for the
           specified Posse members
        """

        try:
            loot_args = self.loot_parser.parse_args(line.split())
        except SystemExit as e:
            #
            # Gross but it's the only way to prevent
            # a command error from dumping out of the
            # entire application.
            #
            return


        deck = self.game.loot

        draws = []
        for member in range(loot_args.members):
            print ("Member {}:".format(member+1))
            print ("  XP   Reward   Description")
            print ("  ---  ------   -----------")

            for card in range(loot_args.cards):
                loot = deck.draw()[0]
                mult = dice.roll(loot['die'])[0] if loot['die'] else 1
                value = loot['unit_mult'] * mult if loot['unit_mult'] else '--'

                print ("  {:>3}  {:>6}   {}".
                    format(loot['xp'], value, loot['text']))

                draws.append(loot)

        #
        # Discard the cards drawn
        #
        deck.discard(draws)

        #
        # Shuffle the discards back into the deck
        # for the next loot draw
        #
        deck.reset()

    def do_scavenge(self, line):
        """Draw Scavenge cards when searching

        scavenge x

        Draw (x) scavenge cards
        """

        try:
            scavenge_args = self.scavenge_parser.parse_args(line.split())
        except SystemExit as e:
            #
            # Gross but it's the only way to prevent
            # a command error from dumping out of the
            # entire application.
            #
            return


        deck = self.game.scavenge

        draws = []
        print ("  XP   Reward   Description")
        print ("  ---  ------   -----------")

        draws = deck.draw(scavenge_args.cards)
        for card in draws:

            value = card['value'] if card['value'] else '--'
            card_text = card['text']

            if card['text'] == 'Something Shiny':
                #
                # The one special case
                # GEnerate the specific something
                #
                random.shuffle(card['something'])
                card_text = "Something Shiny - {}".format(card['something'][0])

            print ("  {:>3}  {:>6}   {}".
                format(card['xp'], value, card_text))

        #
        # Discard the cards drawn
        #
        deck.discard(draws)

        #
        # Shuffle the discards back into the deck
        # for the next loot draw
        #
        deck.reset()        

    def do_save(self, line):
        """Save the current Hexcrawl game session data

        save <filename> <cr>
        Parameters:
        filename - A filname to use when saving the data.
        
        Saves all town locations.
        Saves Posse data.

        """
        parms = line.split()
        if len(parms) != 1:
            print("Invalid filename")
            return
        self.game.save_game(line)

    def do_load(self, line):
        """Load Hexcrawl game session data

        load <filename> <cr>
        Parameters:
        filename - A filname to use when loading the data.

        Loads all town locations.
        [TODO] Loads Posse location.

        If there is an existing game session it will be replaced with
        the loaded session. Save before running this command.
        """
        parms = line.split()
        if len(parms) != 1:
            print("Invalid filename")
            return
        
        try:
            self.game.load_game(line)
        except FileNotFoundError:
            print("Could not find the file")
            return

        #
        # Create a new posse marker
        #
        self.display.add_artifact('posse',
            map_display.PosseMarker(self.game.posse.location))

        self.display.event_update()


    def do_EOF(self, line):
        """Exits the program

        <ctrl>-z <cr>
        Parameters: None

        If there is an existing game session it is lost.
        Save before running this command.
        """
        return True

    def do_quit(self, line):
        """Exits the program

        quit <cr>
        Parameters: None

        If there is an existing game session it is lost.
        Save before running this command.
        """
        return True

    def do_exit(self, line):
        """Exits the program

        exit <cr>
        Parameters: None(q, r, s) 

        If there is an existing game session it is lost.
        Save before running this command.
        """
        return True



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

    #         if event.type == pygame.MOUSEMOTION:
    #             if self.move_posse:
    #                 (x, y) = event.pos
    #                 if self.map_rect.collidepoint(x, y):
    #                     click_pos = redhex.Point(x, y)
    #                     mouse_hex = redhex.pixel_to_hex(self.screen_layout, click_pos)
    #                     mouse_hex = redhex.hex_round(mouse_hex)
    #                     (px, py) = redhex.hex_to_pixel(self.screen_layout, mouse_hex)
    #                     (px, py) = (int(px), int(py))
    # #                    print(mouse_hex)
    #                     #pygame.draw.circle(self.screen, GREEN, (px, py), int(HEX_WIDTH / 2), 3)
    # #                    pygame.display.flip()
    #                     self.add_artifact('posse',
    #                         map_display.PosseMarker(mouse_hex))

            # if event.type == pygame.MOUSEBUTTONDOWN:
            #     if event.button == 1:
            #         if self.move_posse:
            #             (x, y) = event.pos
            #             if self.map_rect.collidepoint(x, y):
            #                 #
            #                 # A hex was selected. Leave the posse marker and
            #                 # get out of move_posse state
            #                 #
            #                 self.move_posse = False

            self.gui.process_events(event)


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
                #
                self.gui.add_artifact('posse_target', map_gui.PosseMarker(mouse_hex))

                self.log.info("Posse location: {} [{}]".format(
                    self.game.location_string(mouse_hex), mouse_hex))

                # self.new_game_dialog = None


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

        # if event.type == pygame.KEYDOWN and event.key == pygame.K_d:
        #     self.debug_mode = False if self.debug_mode else True
        #     self.ui_manager.set_visual_debug_mode(self.debug_mode)

        # if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
        #     print("self.ui_manager.focused_set:", self.ui_manager.focused_set)

        if event.type == pygame.USEREVENT:
        #     if (event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED and
        #             event.ui_object_id == '#main_text_entry'):
        #         print(event.text)

        #     if event.user_type == pygame_gui.UI_TEXT_BOX_LINK_CLICKED:
        #         if event.link_target == 'test':
        #             print("clicked test link")
        #         elif event.link_target == 'actually_link':
        #             print("clicked actually link")

            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:

                if event.ui_element == self.gui.game_button:
                    #
                    # Get the posse name and create a new game.
                    #
                    self.new_game_dialog = game_display.get_posse_name_dialog()

                    #
                    # The posse dialog is modal so disable everything else.
                    #
                    # self.gui.menu_panel.disable()

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



        #         if event.ui_element == self.test_button:
        #             self.test_button.set_text(random.choice(['', 'Hover me!',
        #                                                      'Click this.',
        #                                                      'A Button']))
        #             self.create_message_window()

        #         if event.ui_element == self.test_button_3:
        #             ScalingWindow(pygame.Rect((50, 50), (224, 224)), self.ui_manager)
        #         if event.ui_element == self.test_button_2:
        #             EverythingWindow(pygame.Rect((10, 10), (640, 480)), self.ui_manager)

        #         if event.ui_element == self.disable_toggle:
        #             if self.all_enabled:
        #                 self.disable_toggle.set_text('Enable')
        #                 self.all_enabled = False
        #                 self.ui_manager.root_container.disable()
        #                 self.disable_toggle.enable()
        #             else:
        #                 self.disable_toggle.set_text('Disable')
        #                 self.all_enabled = True
        #                 self.ui_manager.root_container.enable()

        #         if event.ui_element == self.hide_toggle:
        #             if self.all_shown:
        #                 self.hide_toggle.set_text('Show')
        #                 self.all_shown = False
        #                 self.ui_manager.root_container.hide()
        #                 self.hide_toggle.show()
        #             else:
        #                 self.hide_toggle.set_text('Hide')
        #                 self.all_shown = True
        #                 self.ui_manager.root_container.show()

        #     if (event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED
        #             and event.ui_element == self.test_drop_down):
        #         self.check_resolution_changed()

    def run(self):
        while self.running:
            time_delta = self.gui.clock.tick() / 1000.0
            # self.time_delta_stack.append(time_delta)
            # if len(self.time_delta_stack) > 2000:
            #     self.time_delta_stack.popleft()

            # check for input
            self.process_events()

            # respond to input
            self.gui.ui_manager.update(time_delta)

            # if len(self.time_delta_stack) == 2000:
            #     self.fps_counter.set_text(
            #         f'FPS: {min(999.0, 1.0/max(sum(self.time_delta_stack)/2000.0, 0.0000001)):.2f}')
            #     self.frame_timer.set_text(f'frame_time: {sum(self.time_delta_stack)/2000.0:.4f}')

            # draw graphics
            self.gui.screen.blit(self.gui.background_surface, (0, 0))
            for art in self.gui.artifacts.values():
                art.render(self.gui.screen, self.gui.screen_layout)

            self.gui.ui_manager.draw_ui(self.gui.screen)

            pygame.display.update()
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
#display.update()


#
# Start the CLI
#  pygame won't be happy about not getting
#  any CPU as the cmdloop waits for input.
#  We'll live with it for now.
#
#HexcrawlCommands(game, display).cmdloop()
