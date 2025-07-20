import pygame as pg 
import math, sys, random
from enum import Enum
from dataclasses import dataclass

# GAME CONSTANTS
CS = 30
ROWS = 22
COLS = 22 
W = COLS * CS
H = ROWS * CS
CENTER = [W//2, H//2]
FPS = 60

# COLORS
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# OTHER 
inf = float('inf')

# DEFAULTS 
POSITIONS = {'main': [CENTER[0], CENTER[1]-100], 'target': [CENTER[0], CENTER[1]+100]}
ARENA = {'rad': 220, 'w': 6}
BOT_TYPES = {'main': 0, 'target': 1}

# PATHS 
ASSETS_PATH = 'assets/'
IMG_PATH = f'{ASSETS_PATH}images/'