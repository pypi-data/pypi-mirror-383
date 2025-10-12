import pyscratch as pysc

player = pysc.create_single_costume_sprite("assets/fish_brown_outline.png")
player.set_draggable(True)

def scale_move(): 

    player.scale_by(1.05)
    player.move_indir(20)
    yield 0.2 

    player.scale_by(1.05)
    player.move_indir(20)
    yield 0.2 

    player.scale_by(1.05)
    player.move_indir(20)
    yield 0.2 
    
    player.scale_by(1.05)
    player.move_indir(20)

player.when_this_sprite_clicked().add_handler(scale_move) 
