import pyscratch as pysc

# This is the line that create the sprite. Note that you need to match the image file name! 
player = pysc.create_single_costume_sprite("assets/fish_brown_outline.png")
player.set_draggable(True) # optional: make the sprite draggable
