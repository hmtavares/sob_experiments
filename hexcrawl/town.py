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

#("Brimstone" (19, 4)),

TOWNS = [
        ("Masthead", (11, 1)),
        ("Fort Burk", (11, 4)),
        ("West Witold", (-4,9)),
        ("Hill Town", (1, 6)),
        ("Serafin", (7, 7)),
        ("Fringe", (10, 6)),
        ("Wood's End", (-8, 17)),
        ("Larberg's Landing", (-4, 20)),
        ("Stone's Crossing", (-1, 18)),
        ("Lestina", (0, 14)),
        ("Last Chance", (15, 1)),
        ("Fort Lopez", (10, 8)),
        ("Adlerville", (6, 14)),
        ("Flamme's Folly", (14, 7)),
        ("Fort Landy", (12, 11)),
        ("Conradt's Claim - fort", (17, 9)),
        ("Wilshin's Lodge", (13, 14)),
        ("Seto's Mill", (19, 3)),
        ("San Miguel Mission", (19, 10)),
    ]

def town_factory(name, coord):
        """Create a random town

        Args:
            name - The name of the town
            coord - the q,r coordinates of the town
        """

        #
        # Town Size and how many buildings
        #
        town_size, size_low, size_high  = random.choice(Town.TOWN_SIZES)

        num_buildings = random.randint(size_low, size_high)

        #
        #  Generate town kind
        #
        roll = dice.roll('2d6')
        town_type = Town.TOWN_TYPES[sum(roll)]

        #
        # Generate Town Trait
        #
        roll = dice.roll('2d6')
        trait_roll = roll[0] * 10 + roll[1]
        town_trait = Town.TOWN_TRAITS[trait_roll]
        #print ("trait({}) - {}".format(trait_roll, town_trait['name']))

        #
        # Generate buildings
        #
        # Copy the building list
        draw_buildings = Town.TOWN_BUILDINGS[:]

        random.shuffle(draw_buildings)

        town_buildings = []
        for i in range(num_buildings):
            town_buildings.append(draw_buildings.pop())

        return Town(name, coord, town_type, town_trait, town_buildings)

class Town():

    

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
    def __init__(self, name, coord, town_type, trait, locations):

        #TODO: Add validation
        self.name = name
        self.type = town_type
        self.trait = trait
        self.locations = locations
        self.coord = coord

    def get_size():
        num_buildings = len(locations)

        if num_buildings < 1:
            return "Ruins"
        if num_buildings >= 1 and num_buildings <= 4:
            return "Small"
        if num_buildings >= 5 and num_buildings <= 6:
            return "Medium"
        if num_buildings >= 7 and num_buildings <= 8:
            return "Large"
        raise Exception("Invalid town size: {}".format(num_buildings))


