import pyscratch as pysc
game = pysc.game

spawn_button = pysc.create_single_costume_sprite("assets/fish_red_outline.png")
spawn_button.y = 250

# no guarantee that the `player1` and `player2` are created at this point.
# therefore, do not do this:
#player1 = game['player1']

def spwan_enemy(): 
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
    
spawn_button.when_this_sprite_clicked().add_handler(spwan_enemy) 


