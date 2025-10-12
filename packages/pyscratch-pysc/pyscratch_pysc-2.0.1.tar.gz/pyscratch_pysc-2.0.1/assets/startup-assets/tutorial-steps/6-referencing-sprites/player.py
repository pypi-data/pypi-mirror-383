import pyscratch as pysc
game = pysc.game
player1 = pysc.create_single_costume_sprite("assets/fish_brown_outline.png")
player2 = pysc.create_single_costume_sprite("assets/fish_orange_outline.png")
game['player1'] = player1

def move(): 
    while True:
        if pysc.is_key_pressed("d"): 
            player1.x += 4  

        if pysc.is_key_pressed("a"):  
            player1.x -= 4  

        if pysc.is_key_pressed("w"):  
            player1.y -= 4  
            
        if pysc.is_key_pressed("s"):  
            player1.y += 4  

        if pysc.is_key_pressed("right"): 
            player2.x += 4  

        if pysc.is_key_pressed("left"):  
            player2.x -= 4  

        if pysc.is_key_pressed("up"):  
            player2.y -= 4  
            
        if pysc.is_key_pressed("down"):  
            player2.y += 4  

        yield 1/60  # must have an yield in a loop! 

# for the purpose of this tutorial, 
# `player1.when_game_start()` and `player2.when_game_start()` are almost the same. 
game_start = player2.when_game_start()  
game_start.add_handler(move) 




def move2(): 
    player1.x = 200
    player1.y = 400
    
    player2.x = 400
    player2.y = 200
    
    while True:
        if player1.is_touching(player2):
            player1.hide()
            player2.hide()

        yield 1/60  # must have an yield in a loop! 

# for the purpose of this tutorial, 
# `player1.when_game_start()` and `player2.when_game_start()` are almost the same. 
player2.when_game_start().add_handler(move2) 