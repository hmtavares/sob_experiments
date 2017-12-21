from .town import *
from .hexmap import *
import json

class HexCrawl():

    def __init__(self):
        #
        #  Define the town map but
        #  wait until we know how things
        #  are going to be setup before
        #  populating.
        #
        self.map_towns = None

        #
        # Load up the world map
        #
        self.world_map = self.load_map('world_map.json')


    def get_towns(self):
        return self.map_towns

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
        # Generate the towns
        self.map_towns = {}
        for tn_id, tn in TOWNS.items():
            self.map_towns[tn_id] = town_random_factory(tn_id, tn[0], tn[1])

