from settings import * 

class state_e(Enum):
    STATE_WAIT = 0
    STATE_SEARCH = 1
    STATE_ATTACK = 2
    STATE_RETREAT = 3
    STATE_MANUAL = 4

class state_event_e(Enum):
    STATE_EVENT_TIMEOUT = 0
    STATE_EVENT_LINE = 1
    STATE_EVENT_ENEMY = 2
    STATE_EVENT_FINISHED = 3
    STATE_EVENT_COMMAND = 4 
    STATE_EVENT_NONE = 5
