import pyscratch as pysc

player = pysc.create_single_costume_sprite("assets/fish_brown_outline.png")
player.set_draggable(True)

def scale_move(): 

    for i in range(20):
        player.scale_by(1.025)
        yield 0.03 

    for i in range(20):
        player.scale_by(0.975)
        yield 0.03 

player.when_this_sprite_clicked().add_handler(scale_move) 


# Remember: The function is the stack of scratch blocks without the event block at the top
def move(): 
    while True: # the forever loop 
        if pysc.is_key_pressed("d"):  # the sensing block: 'key [w] pressed'
            player.x += 4   # the motion block: change y by [-4]

        # the control block: wait [1/60] seconds 
        # because the frame rate is 60, this is basically to wait for one frame
        yield 1/60  # must have an yield in a loop! 

# Attach the function to the event
game_start = player.when_game_start() 
game_start.add_handler(move) 

# Or just in one line
#player.when_game_start().add_handler(move) 
