# New Document# Shadows of Brimstone HexCrawl Helper



Shadows of Brimstone is a cooperative, dungeon-crawl board game. You should check it out:

* [Shadows of Brimstone at Boardgame Geek]( https://boardgamegeek.com/boardgame/146791/shadows-brimstone-city-ancients)

The game primarily take place in underground 'mines' with each session loosely tied together to form a 'campaign'.

A fan, Sid Rain AKA paddirn on BGG, created created an expansion called "Hexcrawl".

* [Hexcrawl](https://boardgamegeek.com/thread/1239257/shadows-brimstone-hexcrawl)

It takes the core game and adds and "overland" aspect where your team (called a Posse) can leave the depths and continue the adventure overland. It also includes various story style campaigns.

With these new aspects come additional complexity. This application has been created to streamline some of that complexity.


# Application Features

## It's Alpha!
I know, practically everything on GitHub makes excuses for bugs or incomplete work. This is no different. In it's current form it's barely usable.

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

### Save and Load
It will save and load the game data. At this point this is just the generated towns.

### What is it good for?
It's actually a little useful even in it's current very raw form. I use it in our games to view the map (in color!) as well as the town attributes for each town we visit.

# Installation
The application should work for the major Operating Systems (WIndows, OS X, Linux).

As I'm writing this I realize I need to figure out a way for the application so get this stuff for you. Sorry.

## Python 3
[Install Python 3 for your system.](https://www.python.org/downloads/)

I'm using Python 3.6.3

## pygame
[Install pygame for your system.](http://www.pygame.org/wiki/GettingStarted#Pygame Installation)

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
(cmd) help

Documented commands (type help <topic>):
========================================
EOF  exit  help  jumpposse  load  newgame  quit  save  show
```

For each of the commands you can get help by typing `help <command>`


# References

## Redblob
[Red Blob Games](https://www.redblobgames.com/)

Red Blob Games was an amazing resource when trying to figure out how to write code for hexagon maps. The implementation guide provided the code present in the `redhex.py` module in this repository.

## Pygame
Pygame is a fun graphics library that made displaying the hexcrawl map fairly easy.

# sobapp
The inspiration for this application was the github project [sobapp](https://github.com/rbhaddon/sobapp). This project is not a direct fork of that project but seeing the start of something great there definitely got me thinking about creating a hexcrawl utility.
