#!/usr/bin/env python
"""A UI session for a game of Deduce or DIe
"""
import datetime
import logging
import random
import copy
import argparse
import cmd
import dice
import sob.town as town
from sob.town import Town
from sob.town import TOWNS
from sob.town import MINES
from sob.hexmap import HexMap
from sob.hexmap import Hex as SobHex
import redhex
import json


# Test Hexcrawl module components

DEFAULT_LOGFILE = 'mapmerge'
DEFAULT_LOG_LEVEL = 'INFO'
def terrain_hex_json_factory(hex_json):
    thex = SobHex()
    thex.terrain = hex_json['terrain']
    thex.rail = hex_json['rail']
    thex.river = hex_json['river']
    thex.road = hex_json['road']
    thex.town = hex_json['town']
    thex.mine = hex_json['mine']
    return thex

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
full_log_file = setup_logging(time_now, args.log_level, '.', args.log_file)


log.info("Session Start")

class HexcrawlCommands(cmd.Cmd):
    """Command processor for Deduce or Die"""

    def __init__(self):
        """Create a command processor for testing Hexcrawl


        Args: None

        Returns:
            An initilized command processor for Hexcrawl

        Raises: None

        """

        self.map_towns = [];
        self.log = logging.getLogger(self.__class__.__name__)

        cmd.Cmd.__init__(self)
#        self.dod = DodSession(num_players)
#        least_msg = ""   
#        for h in self.dod.hands:
#            least_msg += "Player {} least suit: {}\n".format(h.player, h.least)
#        self.intro = '''
#Exposed: {}
#{}
#Your hand: {}
#'''.format(self.dod.exposed, least_msg, self.dod.hands[0])

#        self.question_cards = self.dod.draw_questions()
#        self.prompt = str(self.dod.question_cards) + ':'
#        self.questions = []

#    doc_header = 'doc_header'
#    misc_header = 'misc_header'
#    undoc_header = 'undoc_header'
    
#    ruler = '-'

    #
    # Validate the ask command line
    # * There must be at least 3 parameters
    # * start and end must be integers
    # * Return the parsed parameters: player, start, end, suit
    #
    def __ask_validate(self, parms):
        parm_len = len(parms)
        if parm_len < 3:
            raise DodException("Not enough parameters")
        if parm_len > 4:
            print ("ignoring extra parameters")
        
        (player, start, end) = parms[:3]
        try:
            player = int(player)
            start = int(start)
            end = int(end)
        except ValueError:
            raise DodException("Non-numeric value for player, start or end")

        suit = None
        if parm_len >= 4:
            suit = parms[3]

        return (player, start, end, suit)

    def do_town(self, line):
        """Create a random town

        Args:
            line: The string that contains the paramaters after "town".
                  This should be empty and is ignored.
        """

        #
        # Town Size and how many buildings
        #
        town_size, size_low, size_high  = random.choice(town.TOWN_SIZES)

        num_buildings = random.randint(size_low, size_high)

        #
        #  Generate town kind
        #
        roll = dice.roll('2d6')
        town_type = town.TOWN_TYPES[sum(roll)]

        #
        # Generate Town Trait
        #
        roll = dice.roll('2d6')
        trait_roll = roll[0] * 10 + roll[1]
        town_trait = town.TOWN_TRAITS[trait_roll]
        print ("trait({}) - {}".format(trait_roll, town_trait['name']))

        #
        # Generate buildings
        #
        # Copy the building list
        draw_buildings = town.TOWN_BUILDINGS[:]

        random.shuffle(draw_buildings)

        town_buildings = []
        for i in range(num_buildings):
            town_buildings.append(draw_buildings.pop())



        print ('''
Town: 
 Size: {}
 Kind: {}
 Trait: {}
 Buildings ({}):'''.format(town_size, town_type, town_trait['name'], num_buildings))

        for bld in town_buildings:
            print ("  {}".format(bld))
            
#        my_town = Town("this", "that", "other", ['stuff'])

    def do_map(self, line):
        self.map_towns = []
        for tn in town.TOWNS:
            self.map_towns.append(town.town_factory(tn[0], tn[1]))

    def do_showtowns(self, line):
        for tn in self.map_towns:
            print ("{} - {} - {}".format(tn.name, tn.coord, tn.type))

    def do_show(self, line):
        for tn in self.map_towns:
            if line in tn.name:
                print (tn)

    def do_save(self, line):
       
        towns_save = []
        save_data = {'towns' : towns_save}
        for tn in self.map_towns:
            towns_save.append(tn.__dict__)


        with open('hexcrawl_save.json', 'w') as outfile:
            json.dump(save_data, outfile, sort_keys=True, indent=4)

    def do_load(self, line):
        with open('hexcrawl_save.json', 'r') as infile:
            load_data = json.load(infile)

        towns = load_data['towns']
        load_towns = []
        for tn in towns:
            load_towns.append(town.town_json_factory(tn))

        self.map_towns = load_towns

    def save_map(self, tmap):
       
        tmap_save = []
        save_data = {'terrain_map' : tmap_save}
        for hcoord, mhex in tmap.hexes.items():
            print ('{} - {}'.format(hcoord, mhex))
            coord = (hcoord.q, hcoord.r, hcoord.s)
            mhex.save_coord = coord
            tmap_save.append(mhex.__dict__)

        with open('combined_map_save.json', 'w') as outfile:
            json.dump(save_data, outfile, sort_keys=True, indent=4)


    def do_load_map(self, line):
        log.info('Loading difficult terrain')

        load_map = HexMap()

        with open('terrain_difficult.json', 'r') as infile:
            load_data = json.load(infile)

        hexes = load_data['terrain_map']
        for h in hexes:
            (q, r, s) = h['save_coord']
            coord = redhex.Hex(q, r, s)

            thex = load_map.get_hex(coord)
            if thex == None:
                thex = terrain_hex_json_factory(h)
            
            load_map.put_hex(coord, thex)


        with open('terrain_river.json', 'r') as infile:
            load_data = json.load(infile)

        hexes = load_data['terrain_map']
        for h in hexes:
            (q, r, s) = h['save_coord']
            coord = redhex.Hex(q, r, s)

            thex = load_map.get_hex(coord)
            if thex == None:
                thex = terrain_hex_json_factory(h)
            else:
                thex.river = True
                thex.terrain = 3
            
            load_map.put_hex(coord, thex)

        with open('terrain_rail.json', 'r') as infile:
            load_data = json.load(infile)

        hexes = load_data['terrain_map']
        for h in hexes:
            (q, r, s) = h['save_coord']
            coord = redhex.Hex(q, r, s)

            thex = load_map.get_hex(coord)
            if thex == None:
                thex = terrain_hex_json_factory(h)
            else:
                thex.rail = True
                thex.terrain = 1
            
            load_map.put_hex(coord, thex)

        with open('terrain_road.json', 'r') as infile:
            load_data = json.load(infile)

        hexes = load_data['terrain_map']
        for h in hexes:
            (q, r, s) = h['save_coord']
            coord = redhex.Hex(q, r, s)

            thex = load_map.get_hex(coord)
            if thex == None:
                thex = terrain_hex_json_factory(h)
            else:
                thex.road = True
                thex.terrain = 1
            
            load_map.put_hex(coord, thex)

        for tn_id, tn in TOWNS.items():
            (q, r) = tn[1]
            s = -(r + q)
            if (q + r + s):
                raise Exception("WTF math")
            coord = redhex.Hex(q, r, s)

            thex = load_map.get_hex(coord)
            if thex == None:
                thex = SobHex()
            
            thex.town = tn_id
            thex.terrain = 1
            
            load_map.put_hex(coord, thex)

        for mine_id, mine in MINES.items():
            (q, r) = mine[1]
            s = -(r + q)
            if (q + r + s):
                raise Exception("WTF math")
            coord = redhex.Hex(q, r, s)

            thex = load_map.get_hex(coord)
            if thex == None:
                thex = SobHex()

            thex.mine = mine_id
            thex.terrain = 3
            
            load_map.put_hex(coord, thex)

        self.save_map(load_map)

    def do_stats(self, line):
        sizes = {}
        types = {}
        traits = {}
        for tn in self.map_towns:
            tsize = tn.get_size()
            if sizes.get(tsize) is None:
                sizes[tsize] = 1
            else:
                sizes[tsize] += 1

            if types.get(tn.type) is None:
                types[tn.type] = 1
            else:
                types[tn.type] += 1


        print('''
Small:  {}
Medium: {}
Large:  {}'''.format(sizes['Small'], sizes['Medium'], sizes['Large']))

        frontier = types.get('Standard Frontier Town')
        ruins = types.get('Town Ruins')
        haunted = types.get('Haunted Town')
        plague = types.get('Plague Town')
        rail = types.get('Rail Town')
        mining = types.get('Mining Town')
        river = types.get('River Town')
        mutant = types.get('Mutant Town')
        outlaw = types.get('Outlaw Town')

        if frontier is None: frontier = 0
        if ruins is None: ruins = 0
        if haunted is None: haunted = 0
        if plague is None: plague = 0
        if rail is None: rail = 0
        if mining is None: mining = 0
        if river is None: river = 0
        if mutant is None: mutant = 0
        if outlaw is None: outlaw = 0



        print('''
Frontier: {}
Ruins:    {}
Haunted:  {}
Plague:   {}
Rail:     {}
Mining:   {}
River:    {}
Mutant:   {}
Outlaw:   {}'''.format( frontier,
                        ruins,
                        haunted,
                        plague,
                        rail,
                        mining,
                        river,
                        mutant,
                        outlaw))


    def do_quit(self, line):
        return True

    def do_EOF(self, line):
        return True

HexcrawlCommands().cmdloop()
