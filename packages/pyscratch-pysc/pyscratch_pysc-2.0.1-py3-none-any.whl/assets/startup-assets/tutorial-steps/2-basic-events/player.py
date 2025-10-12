import pyscratch as pysc

player = pysc.create_single_costume_sprite("assets/fish_brown_outline.png")
player.set_draggable(True)

# 1. Create a function that does the thing (any function name is fine)
def rotate_move(): 

    player.direction += 45
    player.move_indir(20)
    yield 0.2 

    player.direction += 45
    player.move_indir(20)
    yield 0.2 

    player.direction += 45
    player.move_indir(20)
    yield 0.2 
    
    player.direction += 45
    player.move_indir(20)

# 2. Create an event object (any event name is fine)
click_event = player.when_this_sprite_clicked() 

# 3. Attach the function to the event block
click_event.add_handler(rotate_move) 

# Or step 2 and 3 together in one line
#player.when_this_sprite_clicked().add_handler(rotate_move) 
