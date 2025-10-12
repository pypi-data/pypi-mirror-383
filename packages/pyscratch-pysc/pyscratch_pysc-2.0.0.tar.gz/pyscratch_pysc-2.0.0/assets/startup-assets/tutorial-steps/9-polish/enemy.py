import pyscratch as pysc
game = pysc.game


def spwan_enemy_blue(data): 
    enemy_blue = pysc.create_single_costume_sprite("assets/fish_blue_outline.png")

    enemy_blue.y = pysc.random_number(0, game.screen_height)
    enemy_blue.x = 0

    player1 = game['player1']
    player2 = game['player2']
    
    # a better way: break the loop when the sprite is removed
    #while not enemy_blue.removed: 
    while True:
        enemy_blue.x += 4

        if enemy_blue.is_touching(player1):
            enemy_blue.remove()
            player1.scale_by(1.1)

        if enemy_blue.is_touching(player2):
            enemy_blue.remove()
            player2.scale_by(1.1)

        yield 1/game.framerate  # must have an yield in a loop! 
    
game.when_receive_message("spawn_enemy_blue").add_handler(spwan_enemy_blue) 

def on_start():
    while True:
        game.broadcast_message("spawn_enemy_blue")
        yield 1

game.when_game_start().add_handler(on_start)



