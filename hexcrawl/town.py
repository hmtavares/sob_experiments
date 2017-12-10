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
#import dice



class Town():

    TOWN_NAMES = [
        "Brimstone",
        "Masthead",
        "Fort Burk",
        "West Witold",
        "Hill Town",
        "Serafin",
        "Fringe",
        "Wood's End",
        "Larberg's Landing",
        "Stone's Crossing",
        "Lestina",
        "Last Chance",
        "Fort Lopez",
        "Adlerville",
        "Flamme's Folly",
        "Fort Landy",
        "Conradt's Claim",
        "Wilshin's Lodge",
        "Seto's Mill",
        "San Miguel Mission",
    ]

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
    def __init__(self, size, town_type, trait, locations):

        #TODO: Add validation
        self.size = size
        self.type = town_type
        self.trait = trait
        self.locations = locations



