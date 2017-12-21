import redhex
class Hex():

    def __init__(self):
        self.terrain = None
        self.town = None
        self.mine = None
        self.river = False
        self.rail = False
        self.road = False


class HexMap():

    def __init__(self):
        self.hexes = {}

    def get_hex(self, coord):
        return self.hexes.get(coord)

    def put_hex(self, coord, hex):
        self.hexes[coord] = hex

    #
    # Return a dictionary that can be json dumped
    #
    def to_saveable(self):
       
        tmap_save = []
        for hcoord, mhex in self.hexes.items():
            #
            #  Add the coordinates to the hex
            #  So it can be extracted during load
            #
            coord = (hcoord.q, hcoord.r, hcoord.s)
            mhex.save_coord = coord
            tmap_save.append(mhex.__dict__)

        return tmap_save


def Hex_factory_json(hex_json):
    thex = Hex()
    thex.terrain = hex_json['terrain']
    thex.rail = hex_json['rail']
    thex.river = hex_json['river']
    thex.road = hex_json['road']
    thex.town = hex_json['town']
    thex.mine = hex_json['mine']
    return thex

def HexMap_factory_json(map_json):
    load_map = HexMap()
    for h in map_json:
        thex = Hex_factory_json(h)
        (q, r, s) = h['save_coord']
        coord = redhex.Hex(q, r, s)
        load_map.put_hex(coord, thex)

    return load_map
