import pyscratch as pysc
game = pysc.game


def spwan_enemy_red(data): 
    enemy_red = pysc.create_single_costume_sprite("assets/fish_red_outline.png")

    enemy_red.y = pysc.random_number(0, game.screen_height)
    enemy_red.x = 0

    player1 = game['player1']
    player2 = game['player2']
    
    # a better way: break the loop when the sprite is removed
    #while not enemy_blue.removed: 
    while True:
        enemy_red.x += 4

        if enemy_red.is_touching(player1):
            enemy_red.remove()
            game['P1 HP'] -= 1

        if enemy_red.is_touching(player2):
            enemy_red.remove()
            game['P2 HP'] -= 1

        yield 1/game.framerate  # must have an yield in a loop! 
    
game.when_receive_message("spwan_enemy_red").add_handler(spwan_enemy_red) 

def on_start():
    yield .5
    while True:
        game.broadcast_message("spwan_enemy_red")
        yield 1

game.when_game_start().add_handler(on_start)



