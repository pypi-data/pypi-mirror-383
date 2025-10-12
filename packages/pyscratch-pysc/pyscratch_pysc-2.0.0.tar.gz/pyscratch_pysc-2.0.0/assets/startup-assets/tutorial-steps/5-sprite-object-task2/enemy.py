import pyscratch as pysc
game = pysc.game

spawn_button = pysc.create_single_costume_sprite("assets/fish_red_outline.png")
spawn_button.y = 250

def spwan_enemy(): 
    enemy_blue = pysc.create_single_costume_sprite("assets/fish_blue_outline.png")

    enemy_blue.y = pysc.random_number(0, game.screen_height)
    enemy_blue.x = 0
    
    while True:
        enemy_blue.x += 4

        yield 1/game.framerate  # must have an yield in a loop! 
    
spawn_button.when_this_sprite_clicked().add_handler(spwan_enemy) 


