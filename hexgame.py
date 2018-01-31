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
