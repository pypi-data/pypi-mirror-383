import pyscratch as pysc

player1 = pysc.create_single_costume_sprite("assets/fish_brown_outline.png")
player2 = pysc.create_single_costume_sprite("assets/fish_orange_outline.png")

def move(): 
    while True:
        if pysc.is_key_pressed("d"):  
            player1.x += 4   

        if pysc.is_key_pressed("right"):  
            player2.x += 4   

        yield 1/60  # must have an yield in a loop! 

# for the purpose of this tutorial, 
# `player1.when_game_start()` and `player2.when_game_start()` are almost the same. 
game_start = player2.when_game_start()  
game_start.add_handler(move) 

