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

    def __init__(self, coord, game,
                 name = None,
                 mission_loc = None,
                 mission = None,
                 job_loc = None,
                 job_id = None):
        #
        # where is the Posse?
        #
        self._loc = coord
        self.name = name
        # The hexcrawl game that owns this posse
        self.game = game

        self.mission_loc = mission_loc
        self.mission_text = mission

        self.job_loc = None
        self.job_id = job_id
        if self.job_id:
            self.job_id = int(job_id)
            self.job_loc = job_loc


    @property
    def location(self):
        return self._loc

    @location.setter
    def location(self, loc):
        self._loc = loc

    def json_factory(posse_json, game):
        (q, r, s) = posse_json['_loc']
        (x, y, z) = posse_json['job_loc']
        return Posse(
            (q, r, s),
            game,
            posse_json['name'],
            posse_json['mission_loc'],
            posse_json['mission_text'],
            (x, y, z),
            posse_json['job_id'])

    def __str__(self):
        hex = self.game.world_map.get_hex(self.location)
        loc_string = ""
        if hex.town:
            loc_string = TOWNS[hex.town]['name']
        elif hex.mine:
            loc_string = MINES[hex.mine][0]

        hex = self.game.world_map.get_hex(self.mission_loc)
        mission_loc_string = ""
        if(hex):
            if hex.town:
                mission_loc_string = TOWNS[hex.town]['name']
            elif hex.mine:
                mission_loc_string = MINES[hex.mine][0]

        hex = self.game.world_map.get_hex(self.job_loc)
        job_loc_string = ""
        if(hex):
            if hex.town:
                job_loc_string = TOWNS[hex.town]['name']
            elif hex.mine:
                job_loc_string = MINES[hex.mine][0]

        return '''
Posse:
 Name:  {}
 location: {} {}

 Mission: {} {}
   {}
 Job: {} {}
   {}'''.format(self.name,
                 loc_string, self.location,
                 mission_loc_string, self.mission_loc, 
                 self.mission_text,
                 job_loc_string, self.job_loc,
                 self.job_id)


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

    def new_game(self, posse_name = None):
        #
        # Start a new game
        # * Generate Towns
        # * Place Posse at a town (TODO)
        # * Start the day counter (TODO)
        #
        
        # Generate the towns
        self.map_towns = {}
        for tn_id in TOWNS:
            self.map_towns[tn_id] = town_random_factory_2(tn_id)

        #
        # Pick a random town for the Posse
        #
        roll = dice.roll('2d6')
        posse_start = self.map_towns[sum(roll)]
        self.posse = Posse(posse_start.coord, self, posse_name)
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

        posse = load_data['posse']

        self.posse = Posse.json_factory(posse, self)

        self.game_state = 'STARTED'

    def save_game(self, save_name):
        
        #
        # Save the Town data
        #
        towns_save = []
        save_data = {'towns' : towns_save}
        for tn in self.map_towns.values():
            towns_save.append(tn.__dict__)

        #
        # Save the Posse data
        #
        posse_dict = self.posse.__dict__
        #
        # Forget the game instance since it can't be saved
        #
        posse_dict.pop('game')
        save_data['posse'] = self.posse.__dict__

        with open(save_name, 'w') as outfile:
            json.dump(save_data, outfile, sort_keys=True, indent=4)

        #
        # Put the game reference back on the posse
        #
        posse_dict['game'] = self




        