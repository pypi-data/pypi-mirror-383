import pyscratch as pysc
from pyscratch import game
import pygame


# create the variable
game['Score'] = 0

# for the display of the variable - v1.0.5, default font
score_display = pysc.create_shared_data_display_sprite("Score")
score_display.set_draggable(True) # optional


# the sprite
player = pysc.create_single_costume_sprite("assets/fish_brown_outline.png")
player.set_draggable(True)


def add_score():
    game['Score'] += 1 

player.when_this_sprite_clicked().add_handler(add_score) 

def scale(): 

    for i in range(20):
        player.scale_by(1.025)
        yield 0.03 

    for i in range(20):
        player.scale_by(1/1.025)
        yield 0.03 

player.when_this_sprite_clicked().add_handler(scale) 


# Remember: The function is the stack of scratch blocks without the event block at the top
def move(): 
    while True: # the forever loop 
        if pysc.is_key_pressed("d"): 
            player.x += 4  

        if pysc.is_key_pressed("a"):  
            player.x -= 4  

        if pysc.is_key_pressed("w"):  
            player.y -= 4  
            
        if pysc.is_key_pressed("s"):  
            player.y += 4  

        yield 1/60  # must have an yield in a loop! 

# Attach the function to the event
game_start = player.when_game_start() 
game_start.add_handler(move) 

# Or just in one line
#player.when_game_start().add_handler(move) 
