import pygame
from pygame import mixer

# MIXER MUST BE INITIALIZED
if mixer.get_init() is None:
    raise Exception('\nPygame mixer is not initialized!')