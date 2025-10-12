import pyscratch as pysc

spawn_button = pysc.create_single_costume_sprite("assets/button.png")

def spwan_enemy(): 
    enemy_red = pysc.create_single_costume_sprite("assets/fish_red_outline.png")
    enemy_blue = pysc.create_single_costume_sprite("assets/fish_blue_outline.png")
    
    enemy_red.x = 0
    enemy_red.y = pysc.game.screen_height/2


    enemy_blue.x = pysc.game.screen_width 
    enemy_blue.y = pysc.game.screen_height/2
    
    while True:
        enemy_red.x += 4
        enemy_blue.x -= 4

        yield 1/60  # must have an yield in a loop! 
    
spawn_button.when_this_sprite_clicked().add_handler(spwan_enemy) 

