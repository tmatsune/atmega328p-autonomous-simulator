from settings import *

class ir_command_e(Enum):
    NONE = 0 
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9

command_enums = list(ir_command_e)

class line_pos_e(Enum):
    LINE_NONE = 0
    LINE_FRONT = 1
    LINE_BACK = 2
    LINE_LEFT = 3
    LINE_RIGHT = 4
    LINE_FRONT_LEFT = 5
    LINE_FRONT_RIGHT = 6
    LINE_BACK_LEFT = 7
    LINE_BACK_RIGHT = 8
    LINE_DIAGONAL_LEFT = 9
    LINE_DIAGONAL_RIGHT = 10
