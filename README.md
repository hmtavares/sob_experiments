# Shadows of Brimstone HexCrawl Helper



Shadows of Brimstone is a cooperative, dungeon-crawl board game. You should check it out:

* [Shadows of Brimstone at Boardgame Geek]( https://boardgamegeek.com/boardgame/146791/shadows-brimstone-city-ancients)

The game primarily takes place in underground 'mines' with each session loosely tied together to form a 'campaign'.

A fan, Sid Rain AKA paddirn on BGG, created an expansion called "Hexcrawl".

* [Hexcrawl](https://boardgamegeek.com/thread/1239257/shadows-brimstone-hexcrawl)

It takes the core game and adds and "overland" aspect where your team (called a Posse) can leave the depths and continue the adventure overland. It also includes various story style campaigns.

With these new aspects come additional complexity. This application has been created to streamline some of that complexity.


# Application Features

## It's Alpha!
I know, practically everything on GitHub makes excuses for bugs or incomplete work. This is no different. In it's current form it's barely usable.

One big issue right now is the map graphic. It doesn't respond to mouse clicks or anything else unless a game function is activated that requires it (selecting a hex on the map). This is likely to be an issue for a while until I can figure out what GUI utility to use. Currently it uses a simple drawing/rendering utility that doesn't have built in GUI functions.

## What does it do?
### Display the Hexcrawl map.
The application will display a window with the Hexcrawl map. It will also indicate where your Posse is located.

### Generate Towns
The application will generate all the core and hexcrawl attributes for each town
* Buildings
* Town type
* Hexcrawl trait
* Hexcrawl Job

### Display Towns
The attributes of each town can be displayed as text.

### Track Your Posse
Basic Posse tracking functionality 
* Posse location (displayed on map)
* Current job and job location
* Current mission and mission location

### Convenience functions
Drawing from the two most shuffled decks
* Loot deck draws
* Scavenge deck draws

### Save and Load
It will save and load the game data. At this point this is just the generated towns and Posse data

### What is it good for?
It's actually a little useful even in it's current very raw form. I use it in our games to view the map (in color!) as well as the town attributes for each town we visit.

# Installation
The application should work for the major Operating Systems (Windows, OS X, Linux).

As I'm writing this I realize I need to figure out a way for the application to get this stuff for you. Sorry.

## Python 3
[Install Python 3 for your system.](https://www.python.org/downloads/)

I'm using Python 3.6.3

## pygame
[Install pygame for your system.](http://www.pygame.org/wiki/GettingStarted#Pygame)

I'm using pygame 1.9.3

## python dice package
Install the python 'dice' package

`pip install dice`

# Run hexgame.py

python hexgame.py

The hexcrawl map should be displayed.
On the command line where you started hexgame.py you'll be presented with a very plain command prompt:

(Cmd)

## Commands
You can show all the commands by typing

``` 
(Cmd) help

Documented commands (type help <topic>):
========================================
EOF   help  jumpposse  loot     newgame  save      show
exit  job   load       mission  quit     scavenge
```

For each of the commands you can get help by typing `help <command>`


### newgame
Create a new Hexcrawl game session

        newgame {Posse name}
        Parameters:
            Posse name: [optional] The name of the Posse for the game

        Create all town locations.
        Randomly place the Posse

        If there is an existing game session it will be replaced with
        the new session. Save before running this command.


### show {town, posse}

#### show town <town>
        Parameters: town - Town name or id

        Print the details of the town named in the command.

        * Name / location
        * Size
        * Kind of town
        * Hexcrawl trait
        * List of buildings

        The jobs are not shown as you may not be looking at the job board.

        Note: The entire name does not need to be typed in.
              e.g. 'show Fri' will show Fringe.
              Multiple matches will show all matches.
              e.g. 'show Fort' will show Fort Burke, Fort Lopez
              and Fort Landy

#### show posse
        Parameters: None

        Print the details of the Posse

### job {show, set, refresh}

#### job show <town>
        Parameters: town - Town name or id

        Print the Jobs at that town

#### job set <job id>
        Parameters: job id: The 'roll' from the job chart for the job

        Make that job the current posse job

        The map graphic will be activated and the destination
        for the job can be set. The ESC key will cancel
        the map action and save the mission with no location.

#### job refresh <town>
        Parameters: town - Town name or id

        Generate a new set of jobs for the town. May result in a Mandatory job.

### mission
Set a mission for the Posse

        Pararmeters:
            line - The text description for the mission

        The map graphic will be activated and the destination
        for the mission can be set. The ESC key will cancel
        the map action and save the mission with no location.


### jumpposse

        The map graphic will be activated and the destination
        for the posse can be set. The ESC key will cancel
        the map action and save the mission with no location.


### save <filename>

    Save the hexcrawl session data to the file given

### load <filename>

    Load the hexcrawl session data from the file given.

### loot <heros> <cards>

    Draw the number of loot cards indicated for the number of heros indicated.

### scavenge <cards>
    Draw the number of scavenge cards indicated.

### quit
    End the hexcrawl session.    

# Game Walkthrough
The following is a quick step by step example on how you might use this utility:

## Start a new game.
Run the application
```
python hexgame.py
```
Use the ```newgame``` command to start a new Hexcrawl session. This results in the towns being generated and our posse being placed at a random town. In this case "Hill Town"

```
(Cmd) newgame
Posse starts at: Hill Town
```


## Do a mission
Using whatever Hexcrawl campaign you're playing figure out what your next mission is. So if you were doing the 'Form and Void' short story campaign your first mission would be "For a Few Darkstone More" at the closest mine. That would either be Mt. La Terra or Cake's Cave. We choose Cake's Cave.

We use the mission command to set the posse mission.

```
(Cmd) mission For a Few Darkstone More
Select the mission location on the map
Hex(q=-1, r=10, s=-9)
Mission location set: Cake’s Cave [Hex(q=-1, r=10, s=-9)]
```
We can show the posse to see that it now has a mission

```
(Cmd) show posse

Posse:
 Name:
 location: Hill Town Hex(q=1, r=6, s=-7)

 Mission: Cake’s Cave Hex(q=-1, r=10, s=-9)
   For a Few Darkstone More
 Job:  None
   [None]
```

We use the Hexcrawl rules to move to the mine and start the mission. I typically don't bother to move the posse in the application during these movements as they go pretty quick. In the future the application map will calculate movement points and using the map to move will be more usefull

Once we're in the mine we will be drawing scavenge cards and loot cards. You can use the application to speed these processes up a bit if you like:

If we have 4 heros and finish a combat that lets everyone draw 2 loot cards we would do the following:

```
(Cmd) loot 4 2
Member 1:
  XP   Reward   Description
  ---  ------   -----------
   20     100   Sack of Gold Dust - 100 Gold
   20     100   Blood Money - 1d6 x 25 Gold
Member 2:
  XP   Reward   Description
  ---  ------   -----------
   20     150   Gold Nuggets - 1d6 x 50 Gold
   20      --   What's this! Draw an Artifact card
Member 3:
  XP   Reward   Description
  ---  ------   -----------
   20     250   Gold Bars - 250 Gold
   20      --   This should come in handy. Draw a Gear card
Member 4:
  XP   Reward   Description
  ---  ------   -----------
   20      25   Coins - 25 gold
   20       1   Dark Stone Shard - 1 Dark Stone
```

You can see this quickly gets the loot card business done. Note that the 'Reward' column has the random results already generated. You can use these during your game or roll them up yourself if you like.

The same is true when scavenging:

```
(Cmd) scavenge 2
  XP   Reward   Description
  ---  ------   -----------
   10      --   Nothing here
   10      --   3 Horror hits. Two sanity damage per hit
```

Note that these are not remembered by the game session. They are only for convenience and are optional.   

## Head to town
With our mission complete we'll head back to town to do some town business. First order is figure out what jobs are available

```
(Cmd) job show Hill
Town Jobs:
  [2] Inexplicable Murder
  [89] The Hunt
  [53] Prairie Banshees
```

No mandatory job (whew) and we see the 3 job options available. We pick "Inexplicable Murder". This requires a random town and we roll one up - Fringe.

We use the 'job set' command to set the job on the posse. We use the job id "2" to indicate the job. This will also activate the hexcrawl map graphic for us to click on the target town, Fringe

```
(Cmd) job set 2
Select the job location on the map
Job location set: Fringe [Hex(q=10, r=6, s=-16)]
```

We also want to clear our mission since we completed it. We do that by using the mission command with no text and just hit the escape key on the map:

```
(Cmd) mission
Select the mission location on the map
<Event(2-KeyDown {'unicode': '\x1b', 'key': 27, 'mod': 0, 'scancode': 1})>
No location selected
```

oops. A little bit of ugly debug text remains for future clean up.

We can show the current state of the posse:

```
(Cmd) show posse

Posse:
 Name:
 location: Hill Town Hex(q=1, r=6, s=-7)

 Mission:  None

 Job: Fringe Hex(q=10, r=6, s=-16)
   [2] Inexplicable Murder
```


Once we finish in town that will be it for this session (time for dinner!) so we'll save to file. This will remember where we ended up and what our job is for next time.

```(Cmd) save awesome_team.save```

Next time we play we'll load the awesome_team.save file and be ready to go!




# References

## Redblob
[Red Blob Games](https://www.redblobgames.com/)

Red Blob Games was an amazing resource when trying to figure out how to write code for hexagon maps. The implementation guide provided the code present in the `redhex.py` module in this repository.

## Pygame
Pygame is a fun graphics library that made displaying the hexcrawl map fairly easy.

# sobapp
The inspiration for this application was the github project [sobapp](https://github.com/rbhaddon/sobapp). This project is not a direct fork of that project but seeing the start of something great there definitely got me thinking about creating a hexcrawl utility.
