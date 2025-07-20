from settings import *

RANGE_THRESHOLD = 300

class enemy_pos_e(Enum):
    ENEMY_POS_NONE = 0
    ENEMY_POS_FRONT_LEFT = 1
    ENEMY_POS_FRONT = 2
    ENEMY_POS_FRONT_RIGHT = 3
    ENEMY_POS_LEFT = 4
    ENEMY_POS_RIGHT = 5
    ENEMY_POS_FRONT_AND_FRONT_LEFT = 6
    ENEMY_POS_FRONT_AND_FRONT_RIGHT = 7
    ENEMY_POS_FRONT_ALL = 8
    ENEMY_POS_IMPOSSIBLE = 9

class enemy_range_e(Enum):
    ENEMY_RANGE_NONE = 0
    ENEMY_RANGE_CLOSE = 1
    ENEMY_RANGE_MID = 2
    ENEMY_RANGE_FAR = 3

@dataclass
class enemy_s():
    position: enemy_pos_e
    range: enemy_range_e

enemy_null: enemy_s = enemy_s(enemy_pos_e.ENEMY_POS_NONE, enemy_range_e.ENEMY_RANGE_NONE)

def enemy_at_left(enemy: enemy_s):
    return enemy.position == enemy_pos_e.ENEMY_POS_LEFT \
        or enemy.position == enemy_pos_e.ENEMY_POS_FRONT_LEFT \
        or enemy.position == enemy_pos_e.ENEMY_POS_FRONT_AND_FRONT_LEFT

def enemy_at_right(enemy: enemy_s):
    return enemy.position == enemy_pos_e.ENEMY_POS_RIGHT \
        or enemy.position == enemy_pos_e.ENEMY_POS_FRONT_RIGHT \
        or enemy.position == enemy_pos_e.ENEMY_POS_FRONT_AND_FRONT_RIGHT

def enemy_at_front(enemy: enemy_s):
    return enemy.position == enemy_pos_e.ENEMY_POS_FRONT or enemy.position == enemy_pos_e.ENEMY_POS_FRONT_ALL

def enemy_detected(enemy: enemy_s):
    return enemy.position != enemy_pos_e.ENEMY_POS_NONE and enemy.range != enemy_range_e.ENEMY_RANGE_NONE
