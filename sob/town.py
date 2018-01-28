#!/usr/bin/env python
"""Towns and town generation
"""
import datetime
import logging
import random
import copy
import dice

#
#  Lookup towns by die roll.
#  Note that these rolls also work as
#  an 'id' for the town
#
TOWNS = {
        2  : {'name':"Masthead",
              'coord': (11, 1),
              'disallowed': ['Mining', 'River', 'Rail']},
        3  : {'name':"Fort Burk",
              'coord': (11, 4),
              'disallowed': ['Mining', 'River', 'Rail']},
        4  : {'name':"West Witold",
              'coord': (-4, 9),
              'disallowed': ['River', 'Rail']},
        5  : {'name':"Hill Town",
              'coord': (1, 6),
              'disallowed': ['Rail']},
        6  : {'name':"Serafin",
              'coord': (7, 7),
              'disallowed': ['River']},
        7  :  {'name':"Fringe",
              'coord': (10, 6),
              'disallowed': ['River', 'Mine']},
        8  : {'name':"Wood's End",
              'coord': (-8, 17),
              'disallowed': ['River']},
        9  : {'name':"Larberg's Landing",
              'coord': (-4, 20),
              'disallowed': ['Rail']},
        10 : {'name':"Stone's Crossing",
              'coord': (-1, 18),
              'disallowed': ['River']},
        11 : {'name':"Lestina",
              'coord': (0, 14),
              'disallowed': ['River']},
        12 : {'name':"Last Chance",
              'coord': (15, 1),
              'disallowed': ['River']},
        13 : {'name':"Fort Lopez",
              'coord': (10, 8),
              'disallowed': ['River']},
        14 : {'name':"Adlerville",
              'coord': (6, 14),
              'disallowed': ['River', 'Rail']},
        15 : {'name':"Flamme's Folly",
              'coord':  (14, 7),
              'disallowed': ['River', 'Rail']},
        16 : {'name':"Fort Landy",
              'coord': (12, 11),
              'disallowed': ['River', 'Rail']},
        17 : {'name':"Conradt's Claim",
              'coord': (17, 9),
              'disallowed': ['Rail']},
        18 : {'name':"Wilshin's Lodge",
              'coord': (13, 14),
              'disallowed': ['Rail']},
        19 : {'name':"Seto's Mill",
              'coord': (19, 3),
              'disallowed': ['Rail']},
        20 : {'name':"San Miguel Mission",
              'coord': (19, 10),
              'disallowed': ['Rail']},
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

#def __init__(self, tn_id, name, coord, town_type, trait, locations):

def town_json_factory(town_json):
    return Town(
        town_json['id'],
        town_json['name'],
        town_json['coord'],
        town_json['type'],
        town_json['trait_id'],
        town_json['job'],
        town_json['locations'])






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
    2: 'Ruins',
    3: 'Haunted',
    4: 'Plague',
    5: 'Rail',
    6: 'Standard Frontier',
    7: 'Standard Frontier',
    8: 'Standard Frontier',
    9: 'Mining',
    10: 'River',
    11: 'Mutant',
    12: 'Outlaw',
}


TOWN_TYPE_BLDGS = {
    'Mutant': {'include': ["Mutant Quarter"],
               'exclude': ["Frontier Outpost"]},
    'Mining': {'include': ["General Store"],
               'exclude': []},
    'Outlaw': {'include': ["Smuggler’s Den"],
               'exclude': ["Sheriff’s Office"]},
    'Plague': {'include': ["Doc’s Office", "Church"],
               'exclude': ["Sheriff’s Office"]},
    'River':  {'include': ["Street Market"],
               'exclude': []}
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
        "description": "",
        "disallowed" : ['Mining']
    },
    14: {
        "name": "Dark Stone Infused",
        "description": ""
    },
    15: {
        "name": "Shortages",
        "description": "",
        "disallowed" : ['Mining', 'Rail']
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
        "description": "",
        "disallowed" : ['Mutant'],
        "exclude_bldg": ['Mutant Quarter']
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
        "description": "",
        "disallowed" : ['Plague'],
        "exclude_bldg": ['Church']
    },
    32: {
        "name": "Cannibals",
        "description": ""
    },
    33: {
        "name": "Religious Cult",
        "description": "",
        "include_bldg": ['Church']
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
        "description": "",
        "disallowed" : ['Outlaw'],
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
        "description": "",
        "disallowed" : ['Outlaw'],
        "exclude_bldg": ["Smuggler's Den"]
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

    def __init__(self, tn_id, name, coord, town_type, trait_id, job, locations):

        #TODO: Add validation
        #
        # I don't like storing the id in the Town
        # but it's too useful when saving
        #
        self.id = tn_id
        self.name = name
        self.type = town_type
        self.trait_id = trait_id
        #
        # Quickly validate the trait_id
        #
        trait_test = self.trait

        self.job = job

        self.locations = locations
        self.coord = coord

    @property
    def trait(self):
        return TOWN_TRAITS[self.trait_id]

    @property
    def size(self):
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


    def update_jobs(self, jobs, job_mandatory):
        """Generate a new set of jobs for the town.
           This is used to refresh the jobs at a town.

           Args:
            jobs - The collection of mandatory and non-mandatory jobs
            job_mandatory - The % chance that a town will have a mandatory
                            job. 0% indicates that the method defind in the
                            Hexcrawl document should be used (roll +/- 1)
        """
        self.job = Town.generate_jobs(jobs, job_mandatory)

    def random_factory(tn_id, jobs, job_mandatory, allow_ruins = False):
        """Create a random town

        Args:
            tn_id - The id of the town on the hexcrawl map
            jobs - The collection of mandatory and non-mandatory jobs
            allow_ruins - True if a town can be generated as
                          type 'Ruins'
            job_mandatory - The % chance that a town will have a mandatory
                            job. 0% indicates that the method defind in the
                            Hexcrawl document should be used (roll +/- 1)
        """

        tn = TOWNS[tn_id]
        if not allow_ruins:
            #
            # Ruins are not allowed for this town so
            # add Ruins to the disallowed type list
            #
            tn['disallowed'].append("Ruins")
        #
        # Town Size and how many buildings
        #
        town_size, size_low, size_high  = random.choice(TOWN_SIZES)

        num_buildings = random.randint(size_low, size_high)

        #
        #  Generate town kind.
        #  Keep trying until a valid type is generated
        # 
        while(True):
            roll = dice.roll('2d6')
            town_type = TOWN_TYPES[sum(roll)]
            if town_type not in tn['disallowed']:
                break

        #
        # Generate Town Trait
        # Keep trying until a valid trait is generated
        #
        while(True):
            roll = dice.roll('2d6')
            trait_roll = roll[0] * 10 + roll[1]
            town_trait = TOWN_TRAITS[trait_roll]

            #
            # Check for special trait considerations
            #
            disallowed = town_trait.get('disallowed')
            if not disallowed:
                #
                # No special considerations.
                # Keep the trait
                #
                break
            if town_type not in disallowed:
                #
                # No special consideration violations
                # Keep the trait.
                #
                break
        #
        # Generate buildings
        #
        # Copy the building list so we can 'draw' from it
        # without modifying the reference list.
        draw_buildings = TOWN_BUILDINGS[:]
        town_buildings = []

        #
        # Check if the town has special building considerations
        #
        special_tn = TOWN_TYPE_BLDGS.get(town_type)
        if special_tn:
            #
            # Get manditory buildings then remove
            # them from the available buildings
            #
            for bldg in special_tn['include']:
                draw_buildings.remove(bldg)
                town_buildings.append(bldg)
                num_buildings -= 1

            #
            # Get excluded buildings and take them out of the
            # available buildings                
            #
            for bldg in special_tn['exclude']:
                draw_buildings.remove(bldg)

        #
        # Randomize the remaining buildings
        # and draw enough to fill the town
        #                
        random.shuffle(draw_buildings)
        for i in range(num_buildings):
            town_buildings.append(draw_buildings.pop())


        #
        # Roll for the town job
        #
        # TODO: Create a seperate "Manditory" roll to
        #       check if the town has a manditory job
        #
        town_job = Town.generate_jobs(jobs, job_mandatory)

        #
        # Fix town coordinates to be normalized 3-tuple coordinates
        # 
        (q, r) = tn['coord']
        coord = (q, r, 0 - (q + r))
        return Town(tn_id, tn['name'], coord, town_type, trait_roll,
                    town_job, town_buildings)


    def generate_jobs(jobs, mandatory):
        """Create a set of random jobs

        Return a single mandatory job
        or
        Return 3 non-mandatory jobs

        Args:
            jobs - The collection of mandatory and non-mandatory jobs
            job_mandatory - The % chance that a town will have a mandatory
                            job. 0% indicates that the method defind in the
                            Hexcrawl document should be used (roll +/- 1)
        """
        town_jobs = []
        roll = dice.roll('1d100')
        if roll[0] <= mandatory:
            #
            # Generate a single mandatory job
            #
            random.shuffle(jobs['mandatory'])
            town_jobs = [jobs['mandatory'][0]]
        else:            
            #
            # Generate 3 different jobs
            #
            random.shuffle(jobs['normal'])
            town_jobs = [jobs['normal'][0],
                         jobs['normal'][1],
                         jobs['normal'][2]]

        return town_jobs

    def __str__(self):
        town_str = '''
Town:   {} - {}
  Size:  {}
  Kind:  {}
  Trait: [{}]{}
  Buildings:
'''.format(self.name, self.coord,
                     self.size, 
                     self.type,
                     self.trait_id, self.trait['name'])


        for loc in self.locations:
            town_str += "    {}\n".format(loc)

        return town_str
