#!/usr/bin/env python
"""A UI session for a game of Deduce or DIe
"""
import sys
import datetime
import logging
import random
import copy
import argparse
import cmd
import os
import dice
import sob.town as town
from sob.town import Town
#from dod_game import *
import json
import map_display
from sob.game import HexCrawl

# Test Hexcrawl module components

DEFAULT_LOGFILE = 'logs/hexgame'
DEFAULT_LOG_LEVEL = 'INFO'

def setup_logging(time_now, log_level, log_file):

    global log
    global root_logger
    global console_handler

    timestamp_now = time_now.strftime('%Y%m%d_%H%M%S')

    levels = {'ERROR'   :logging.ERROR,
              'WARNING' :logging.WARNING,
              'INFO'    :logging.INFO,
              'DEBUG'   :logging.DEBUG}

    log_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(module)s.%(name)s.%(funcName)s] %(message)s')
    root_logger = logging.getLogger()
    root_logger.setLevel(levels[log_level])

    log_path, log_filename = os.path.split(log_file)
    log_filename = log_filename + '_' + timestamp_now + '.log'
    #
    # Check for an actual log filename
    #
    if not log_filename:
        raise ValueError("Log file path must include a filename")

    #
    # Check that the log directory exists
    #
    if log_path and not os.path.exists(log_path):
        #
        #  It doesn't.
        #  Create the directory
        #
        os.makedirs(log_path)
    
    log_file = os.path.join(log_path, log_filename)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    log = logging.getLogger()
    return log_file

parser = argparse.ArgumentParser(description='Track a Hexcrawl game session')

parser.add_argument('--logfile', dest='log_file', default=DEFAULT_LOGFILE,
                        help='The path and name of the log file. Default={}_<timestamp>.log'.format(DEFAULT_LOGFILE))
parser.add_argument('--level', dest='log_level', default=DEFAULT_LOG_LEVEL,
                        help='Set the log level for the application log. ' \
                             '[ERROR, WARN, INFO, DEBUG] Default={}'.format(DEFAULT_LOG_LEVEL))
#parser.add_argument( 'num_players', help='Number of players (3-6)')


args = parser.parse_args()

time_now = datetime.datetime.now()
full_log_file = setup_logging(time_now, args.log_level, args.log_file)


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

        cmd.Cmd.__init__(self)

    def do_newgame(self, line):
        """Create a new Hexcrawl game session

        newgame <cr>
        Parameters: None
        
        Create all town locations.
        Randomly place the Posse

        If there is an existing game session it will be replaced with
        the new session. Save before running this command.
        """
        self.game.new_game()
        if not self.posse:
            #
            # Create a posse marker the old posse from the display
            #
            self.posse = map_display.PosseMarker(self.game.posse.location)
            self.display.add_artifact(self.posse)

        else:
            #
            # Move the posse marker
            #
            loc = self.game.posse.location
            self.posse.set_coord(loc)

        print (self.posse.__dict__)
        self.display.event_update()

    def do_jumpposse(self, line):
        """Place the Posse at a new location

        jumpposse <cr>
        Parameters: None
        
        Control moves to the GUI map display. When a hex is clicked
        the posse will be moved to that hex.

        Note that the CLI will not respond until a hex has been clicked.

        TODO: Allow and escape key to return to the CLI without moving
              the Posse
        TODO: Allow a mine name, town name or coordinate to be provided
              on the command line
        """
        desthex = self.display.get_click()
        self.posse._loc = desthex
        self.display.event_update()

    def do_show(self, line):
        """Show the details of a town

        show <town name> <cr>
        Parameters: Town name
        
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

        TODO: Improve formatting
        TODO: Add Job if one has been rolled.
        TODO: Optionally hide towns that have not been visited
        TODO: Show "last known" town stats and don't show any changes
              i.e. destroyed buildings, until the town is visited
        """
        if not self.game.started:
            print ("Start or load a game")
            return
        if not line:
            print ("ID or town name required")
            return
        towns = self.game.towns
        try:
            tn_id = int(line)
            tn = towns[tn_id]
            print (tn)
        except ValueError:
            for tn in towns.values():
                if line in tn.name:
                    print(tn)
                    break

    def do_save(self, line):
        """Save the current Hexcrawl game session data

        save <filename> <cr>
        Parameters:
        filename - A filname to use when saving the data.
        
        Saves all town locations.
        [TODO] Saves Posse location.

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
        
        self.game.load_game(line)

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
        Parameters: None

        If there is an existing game session it is lost.
        Save before running this command.
        """
        return True


#
# Create game
#
game = HexCrawl()

#
#  Setup and display the map
#
display  = map_display.MapDisplay()
display.update()


#
# Start the CLI
#  pygame won't be happy about not getting
#  any CPU as the cmdloop waits for input.
#  We'll live with it for now.
#
HexcrawlCommands(game, display).cmdloop()
