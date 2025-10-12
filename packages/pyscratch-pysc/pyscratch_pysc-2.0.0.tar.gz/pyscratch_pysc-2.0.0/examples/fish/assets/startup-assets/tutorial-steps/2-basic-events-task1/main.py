import pyscratch as pysc
import player # Very important!
import enemy # Very important!

# start the game
WIN_WIDTH = 500 # change me
WIN_HEIGHT = 500 # change me
framerate = 60

pysc.game.update_screen_mode((WIN_WIDTH, WIN_HEIGHT)) 
pysc.game.start(framerate)
