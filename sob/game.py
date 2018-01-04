from .town import *
from .hexmap import *
import json


class Posse():
    #
    # Memers?
    # Current Job?
    # Current Mission?
    # notes?
    #

    def __init__(self, coord):
        #
        # where is the Posse?
        #
        self._loc = coord

    @property
    def location(self):
        return self._loc

class HexCrawl():

    def __init__(self):
        #
        #  Define the town map but
        #  wait until we know how things
        #  are going to be setup before
        #  populating.
        #
        self.game_state = None
        self.map_towns = None
        self.posse = None

        #
        # Load up the world map
        #
        self.world_map = self.load_map('world_map.json')

    @property
    def towns(self):
        return self.map_towns

    @property
    def started(self):
        if self.game_state != 'STARTED':
            return False
        return True
    #
    # Load the static map data
    #  - Terrian
    #  - Rail, River or Road hex
    #  - Town id
    #  - Mine id
    #
    def load_map(self, world_name):
        with open(world_name, 'r') as infile:
            load_data = json.load(infile)

        hexes = load_data['terrain_map']

        w_map = HexMap_factory_json(hexes)
#        w_map = HexMap()
#        for h in hexes:
#            thex = Hex_factory_json(h)
#            (q, r, s) = h['save_coord']
#            coord = redhex.Hex(q, r, s)
#            w_map.put_hex(coord, thex)

        return w_map

    def new_game(self):
        #
        # Start a new game
        # * Generate Towns
        # * Place Posse at a town (TODO)
        # * Start the day counter (TODO)
        #
        
        # Generate the towns
        self.map_towns = {}
        for tn_id, tn in TOWNS.items():
            self.map_towns[tn_id] = town_random_factory_2(tn_id, tn)

        #
        # Pick a random town for the Posse
        #
        roll = dice.roll('2d6')
        posse_start = self.map_towns[sum(roll)]
        self.posse = Posse(posse_start.coord)
        print("Posse starts at: {}".format(posse_start.name))
        #
        # Mark the game as started
        #
        self.game_state = 'STARTED'            

    def load_game(self, load_name):
        with open(load_name, 'r') as infile:
            load_data = json.load(infile)

        towns = load_data['towns']
        load_towns = {}
        for tn in towns:
            tn_obj = town_json_factory(tn)
            load_towns[tn_obj.id] = tn_obj

        self.map_towns = load_towns
        self.game_state = 'STARTED'

    def save_game(self, save_name):
        towns_save = []
        save_data = {'towns' : towns_save}
        for tn in self.map_towns.values():
            print(tn.id)
            towns_save.append(tn.__dict__)

        with open(save_name, 'w') as outfile:
            json.dump(save_data, outfile, sort_keys=True, indent=4)

        