import pyscratch as pysc
game = pysc.game

enemy = pysc.create_single_costume_sprite("assets/fish_red_outline.png")
enemy.set_draggable(True) # optional: make the sprite draggable

def appear():
    enemy.x = game.screen_width/2
    enemy.y = game.screen_height/2
    enemy.hide()
    yield 3
    enemy.show()

enemy.when_game_start().add_handler(appear)