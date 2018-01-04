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
import dice
import sob.town as town
from sob.town import Town
#from dod_game import *
import json
import map_display
from sob.game import HexCrawl

# Test Hexcrawl module components

DEFAULT_LOGFILE = 'hexgame'
DEFAULT_LOG_LEVEL = 'INFO'

def setup_logging(time_now, log_level, log_path, log_filename):

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

    log_file = log_path + '/' + log_filename + '_' + timestamp_now + '.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    log = logging.getLogger()
    return log_file

parser = argparse.ArgumentParser(description='Play a practice session of Deduce or Die')

parser.add_argument('--logfile', dest='log_file', default=DEFAULT_LOGFILE,
                        help='The name of the log file. Default={}_<timestamp>.log'.format(DEFAULT_LOGFILE))
parser.add_argument('--level', dest='log_level', default=DEFAULT_LOG_LEVEL,
                        help='Set the log level for the application log. ' \
                             '[ERROR, WARN, INFO, DEBUG] Default={}'.format(DEFAULT_LOG_LEVEL))
#parser.add_argument( 'num_players', help='Number of players (3-6)')


args = parser.parse_args()

time_now = datetime.datetime.now()
full_log_file = setup_logging(time_now, args.log_level, 'logs', args.log_file)


log.info("Game Start")

class HexcrawlCommands(cmd.Cmd):
    """Command processor for Deduce or Die"""

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
        desthex = self.display.get_click()
        self.posse._loc = desthex
        self.display.event_update()

    def do_show(self, line):
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
        parms = line.split()
        if len(parms) != 1:
            print("Invalid filename")
            return
        self.game.save_game(line)

    def do_load(self, line):
        parms = line.split()
        if len(parms) != 1:
            print("Invalid filename")
            return
        
        self.game.load_game(line)

    def do_EOF(self, line):
        return True

    def do_quit(self, line):
        return True

    def do_exit(self, line):
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
