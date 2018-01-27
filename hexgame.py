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
        self.setup_parsers()

        cmd.Cmd.__init__(self)


    def setup_parsers(self):
        #
        # Show parser
        #
        # show [town, posse]
        self.show_parser = argparse.ArgumentParser(description='Show game element details')
        subparsers = self.show_parser.add_subparsers(help='Show towns or posse')

        #        
        # show town <town name/id>
        #
        town_parser = subparsers.add_parser("town")
        town_parser.set_defaults(func=self.show_town)
        #
        # show posse
        #
        posse_parser = subparsers.add_parser("posse")
        posse_parser.set_defaults(func=self.show_posse)

        town_parser.add_argument('name',
                        help='The name of the town to show.')

        #
        # Loot Parser
        #
        self.loot_parser = argparse.ArgumentParser(description='Draw loot after a fight')        
        self.loot_parser.add_argument('members', type=int, help='Number of members in posse')
        self.loot_parser.add_argument('cards', type=int, help='Number of cards to draw for each member')

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

        TODO: Allow and escape key to return to the CLI without moving
              the Posse
        TODO: Allow a mine name, town name or coordinate to be provided
              on the command line
        """
        desthex = self.display.get_click()
        #
        # If we got a destination set it.
        # Otherwise leave the Posse where it is.
        #
        if desthex:
            self.game.posse.location = desthex
            self.display.get_artifact('posse').set_coord(desthex)
            self.display.event_update()

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
        tn_name = town_args.name

        towns = self.game.towns
        try:
            tn_id = int(tn_name)
            tn = towns[tn_id]
            print (tn)
        except ValueError:
            for tn in towns.values():
                if tn_name in tn.name:
                    print(tn)
                    break

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

        mission_hex = self.display.get_click()
        #
        # If we got a hex set it.
        # Otherwise no location
        #
        self.game.posse.mission_loc = None
        if mission_hex:
            self.game.posse.mission_loc = mission_hex

    def do_job(self, line):
        """Set a job for the Posse

        Pararmeters:
            line - The Job ID (roll) from the job table

        The map graphic will be activated and the destination
        for the job can be set. The ESC key will cancel
        the map action and save the job with no location.
        """
        try:
            self.game.posse.job_id = int(line)
        except ValueError:
            print("Job key must be an integer")
            return


        job_hex = self.display.get_click()
        #
        # If we got a hex set it.
        # Otherwise no location
        #
        self.game.posse.job_loc = None
        if job_hex:
            self.game.posse.job_loc = job_hex

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
