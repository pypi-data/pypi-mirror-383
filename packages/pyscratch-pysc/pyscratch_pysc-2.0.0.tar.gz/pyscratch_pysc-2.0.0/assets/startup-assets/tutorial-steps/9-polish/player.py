import pyscratch as pysc
from pyscratch.sprite import create_shared_data_display_sprite
game = pysc.game
player1 = pysc.create_single_costume_sprite("assets/fish_brown_outline.png")
player2 = pysc.create_single_costume_sprite("assets/fish_orange_outline.png")
game['player1'] = player1
game['player2'] = player2

game['P1 HP'] = 10
game['P2 HP'] = 10

create_shared_data_display_sprite("P1 HP", position=(100, 100))
create_shared_data_display_sprite("P2 HP", position=(100, 200))

def move(): 
    player1.set_rotation_style_left_right()
    player2.set_rotation_style_left_right()
    while True:
        if pysc.is_key_pressed("d"): 
            player1.x += 4  
            player1.direction = 0

        if pysc.is_key_pressed("a"):  
            player1.x -= 4  
            player1.direction = 180

        if pysc.is_key_pressed("w"):  
            player1.y -= 4  
            
        if pysc.is_key_pressed("s"):  
            player1.y += 4  


        if pysc.is_key_pressed("right"): 
            player2.x += 4  
            player2.direction = 0

        if pysc.is_key_pressed("left"):  
            player2.x -= 4  
            player2.direction = 180

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
            if player1.scale_factor == player2.scale_factor:
                player1.hide()
                player2.hide()

            elif player1.scale_factor > player2.scale_factor: 
                player2.hide()
            else:
                player1.hide()

        yield 1/60  # must have an yield in a loop! 

# for the purpose of this tutorial, 
# `player1.when_game_start()` and `player2.when_game_start()` are almost the same. 
player2.when_game_start().add_handler(move2) 


def message_event(data):
    print("Received a message with data:", data)
player1.when_receive_message("message_topic1").add_handler(message_event)




def player1_skill(updown):

    game.broadcast_message("message_topic1", updown)
     
    if updown == 'up': 
        for i in range(20):
            player1.scale_by(1.025)
            yield 1/game.framerate

    if updown == 'down': 

        for i in range(20):
            player1.scale_by(1/1.025)
            yield 1/game.framerate


player1.when_key_pressed("space").add_handler(player1_skill) 



def player_hp_check():
    while True: 
        if game['P1 HP'] <= 0:
            player1.hide()

        if game['P2 HP'] <= 0:
            player2.hide()
        yield 1/game.framerate
game.when_game_start().add_handler(player_hp_check)
    
