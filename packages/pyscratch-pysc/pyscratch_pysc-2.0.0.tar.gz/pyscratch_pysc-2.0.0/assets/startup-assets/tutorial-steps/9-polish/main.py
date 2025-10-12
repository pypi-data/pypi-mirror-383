import pyscratch as pysc
import player # Very important!
import enemy # Very important!
import enemy_red
import pygame
# start the game
WIN_WIDTH = 720 # change me
WIN_HEIGHT = 720 # change me
framerate = 60

pysc.game.update_screen_mode((WIN_WIDTH, WIN_HEIGHT)) 
pysc.game.start(framerate, use_frame_time=True)
