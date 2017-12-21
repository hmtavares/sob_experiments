#!/usr/bin/env python
"""Towns and town generation
"""
import datetime
import logging
import random
import copy


#import enum
#from random import choice

#import charts
import dice

#
#  Lookup towns by die roll.
#  Note that these rolls also work as
#  an 'id' for the town
#
TOWNS = {
        2  : ("Masthead", (11, 1)),
        3  : ("Fort Burk", (11, 4)),
        4  : ("West Witold", (-4,9)),
        5  : ("Hill Town", (1, 6)),
        6  : ("Serafin", (7, 7)),
        7  : ("Fringe", (10, 6)),
        8  : ("Wood's End", (-8, 17)),
        9  : ("Larberg's Landing", (-4, 20)),
        10 : ("Stone's Crossing", (-1, 18)),
        11 : ("Lestina", (0, 14)),
        12 : ("Last Chance", (15, 1)),
        13 : ("Fort Lopez", (10, 8)),
        14 : ("Adlerville", (6, 14)),
        15 : ("Flamme's Folly", (14, 7)),
        16 : ("Fort Landy", (12, 11)),
        17 : ("Conradt's Claim - fort", (17, 9)),
        18 : ("Wilshin's Lodge", (13, 14)),
        19 : ("Seto's Mill", (19, 3)),
        20 : ("San Miguel Mission", (19, 10)),
    }

MINES = {
        4  : ("The Badlands", (1, 2)),
        5  : ("Gregor’s Gulch", (7, 0)),
        6  : ("Mt. La Terra", (5, 6)),
        7  : ("Hell Mouth", (19, 0)),
        8  : ("Glory’s Anthem", (26, 1)),
        9  : ("Cake’s Cave", (-1, 10)),
        10 : ("Clayton Ravine", (-4, 17)),
        11 : ("Mt. La Pointe", (5, 11)),
        12 : ("Ranae Pointe", (2, 20)),
        13 : ("The Tombs", (8, 20)),
        14 : ("Arzhakov’s Gate", (8, 17)),
        15 : ("Phillip’s Hill", (10, 13)),
        16 : ("Scrogg’s Bog", (18, 17)),
        17 : ("Old Ed’s Mine", (18, 12)),
        18 : ("Conradt’s Claim", (18, 8)),
        19 : ("Sierra Magallanes", (24, 5)),
        20 : ("Ruins of Brimstone", (18, 4)),
    }

def town_json_factory(town_json):
    return Town(
        town_json['name'],
        town_json['coord'],
        town_json['type'],
        town_json['trait'],
        town_json['locations'])


def town_random_factory(tn_id, name, coord):
        """Create a random town

        Args:
            name - The name of the town
            coord - the q,r coordinates of the town
        """

        #
        # Town Size and how many buildings
        #
        town_size, size_low, size_high  = random.choice(TOWN_SIZES)

        num_buildings = random.randint(size_low, size_high)

        #
        #  Generate town kind
        #
        roll = dice.roll('2d6')
        town_type = TOWN_TYPES[sum(roll)]

        #
        # Generate Town Trait
        #
        roll = dice.roll('2d6')
        trait_roll = roll[0] * 10 + roll[1]
        town_trait = trait_roll

        #
        # Generate buildings
        #
        # Copy the building list
        draw_buildings = TOWN_BUILDINGS[:]

        random.shuffle(draw_buildings)

        town_buildings = []
        for i in range(num_buildings):
            town_buildings.append(draw_buildings.pop())

        return Town(tn_id, name, coord, town_type, town_trait, town_buildings)

TOWN_SIZES = [
        ("Small", 1, 4),
        ("Small", 1, 4),
        ("Small", 1, 4),
        ("Small", 1, 4),
        ("Medium", 5, 6),
        ("Medium", 5, 6),
        ("Large", 7, 8),
        ("Large", 7, 8)
    ]

TOWN_TYPES = {
    2: 'Town Ruins',
    3: 'Haunted Town',
    4: 'Plague Town',
    5: 'Rail Town',
    6: 'Standard Frontier Town',
    7: 'Standard Frontier Town',
    8: 'Standard Frontier Town',
    9: 'Mining Town',
    10: 'River Town',
    11: 'Mutant Town',
    12: 'Outlaw Town',
}

TOWN_BUILDINGS = [
    "General Store",
    "Frontier Outpost",
    "Church",
    "Doc’s Office",
    "Saloon",
    "Blacksmith",
    "Sheriff’s Office",
    "Gambling Hall",
    "Street Market",
    "Smuggler’s Den",
    "Mutant Quarter",
    "Indian Trading Post",
]

TOWN_TRAITS = {
    11: {
        "name": "Dry",
        "description": "This Town has declared alcohol to be a vile sin and forbids the purchase of or the imbibing of any alcoholic demon drink. Heroes may not purchase any alcoholic Side Bag Tokens here but may attempt to sell them at the Camp Site for twice the price. When attempting to sell, roll a D6. On a 1 or 2, the sale is discovered and the Heroes must end their Town Stay and cannot enter Town for a week."
    },
    12: {
        "name": "Dark Secret",
        "description": ""
    },
    13: {
        "name": "No Stones Allowed",
        "description": ""
    },
    14: {
        "name": "Dark Stone Infused",
        "description": ""
    },
    15: {
        "name": "Shortages",
        "description": ""
    },
    16: {
        "name": "Obligation",
        "description": ""
    },
    21: {
        "name": "Degenerate",
        "description": ""
    },
    22: {
        "name": "Bad Water",
        "description": ""
    },
    23: {
        "name": "Inbred",
        "description": ""
    },
    24: {
        "name": "Xenophobic",
        "description": ""
    },
    25: {
        "name": "Unstable Gate",
        "description": ""
    },
    26: {
        "name": "Foreigners",
        "description": ""
    },
    31: {
        "name": "Heathens",
        "description": ""
    },
    32: {
        "name": "Cannibals",
        "description": ""
    },
    33: {
        "name": "Religious Cult",
        "description": ""
    },
    34: {
        "name": "Boring",
        "description": ""
    },
    35: {
        "name": "Bartering",
        "description": ""
    },
    36: {
        "name": "Corrupt",
        "description": ""
    },
    41: {
        "name": "Thieving",
        "description": ""
    },
    42: {
        "name": "Slavers",
        "description": ""
    },
    43: {
        "name": "Amazonian",
        "description": ""
    },
    44: {
        "name": "Peaceful",
        "description": ""
    },
    45: {
        "name": "Addicted",
        "description": ""
    },
    46: {
        "name": "Nightmares",
        "description": ""
    },
    51: {
        "name": "Artifact Decay",
        "description": ""
    },
    52: {
        "name": "Bad Luck",
        "description": ""
    },
    53: {
        "name": "Black Market",
        "description": ""
    },
    54: {
        "name": "Jovial",
        "description": ""
    },
    55: {
        "name": "Constructive",
        "description": ""
    },
    56: {
        "name": "Cattle Yard",
        "description": ""
    },
    61: {
        "name": "Law Abiding",
        "description": ""
    },
    62: {
        "name": "Fancy House",
        "description": ""
    },
    63: {
        "name": "Unstable Economy",
        "description": ""
    },
    64: {
        "name": "Dimensional Paradox",
        "description": ""
    },
    65: {
        "name": "Well-Defended",
        "description": ""
    },
    66: {
        "name": "Unique Location",
        "description": ""
    }
}

class Town():

    def __init__(self, tn_id, name, coord, town_type, trait, locations):

        #TODO: Add validation
        #
        # I don't like storing the id in the Town
        # but it's too useful when saving
        #
        self.id = tn_id
        self.name = name
        self.type = town_type
        self.trait = trait
        self.locations = locations
        self.coord = coord

    def get_size(self):
        num_buildings = len(self.locations)

        if num_buildings < 1:
            return "Ruins"
        if num_buildings >= 1 and num_buildings <= 4:
            return "Small"
        if num_buildings >= 5 and num_buildings <= 6:
            return "Medium"
        if num_buildings >= 7 and num_buildings <= 8:
            return "Large"
        raise Exception("Invalid town size: {}".format(num_buildings))


    def __str__(self):
                return '''
Town: {} - {}
 Size: {}
 Kind: {}
 Trait: {}
 Buildings ({}):'''.format(self.name, self.coord,
                           self.get_size(), 
                           self.type,
                           TOWN_TRAITS[self.trait]['name'],
                           self.locations)