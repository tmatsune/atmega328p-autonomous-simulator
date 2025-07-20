from statemachine.state_common import * 
from timer import * 
from common.ring_buffer import * 
from statemachine.line import * 
from statemachine.enemy import * 
from statemachine.drive import * 

class state_transition_s:
    def __init__(self, from_state, state_event, to_state) -> None:
        self.from_state: state_e = from_state
        self.state_event: state_event_e = state_event
        self.to_state: state_e = to_state

state_transitions = [
    state_transition_s(state_e.STATE_WAIT, state_event_e.STATE_EVENT_NONE,    state_e.STATE_WAIT),
    state_transition_s(state_e.STATE_WAIT, state_event_e.STATE_EVENT_LINE,    state_e.STATE_WAIT),
    state_transition_s(state_e.STATE_WAIT, state_event_e.STATE_EVENT_ENEMY,   state_e.STATE_WAIT),
    state_transition_s(state_e.STATE_WAIT, state_event_e.STATE_EVENT_COMMAND, state_e.STATE_SEARCH),

    state_transition_s(state_e.STATE_SEARCH, state_event_e.STATE_EVENT_NONE,    state_e.STATE_SEARCH),
    state_transition_s(state_e.STATE_SEARCH, state_event_e.STATE_EVENT_TIMEOUT, state_e.STATE_SEARCH),
    state_transition_s(state_e.STATE_SEARCH, state_event_e.STATE_EVENT_ENEMY,   state_e.STATE_ATTACK),
    state_transition_s(state_e.STATE_SEARCH, state_event_e.STATE_EVENT_LINE,    state_e.STATE_RETREAT),
    state_transition_s(state_e.STATE_SEARCH, state_event_e.STATE_EVENT_COMMAND, state_e.STATE_MANUAL),

    state_transition_s(state_e.STATE_ATTACK, state_event_e.STATE_EVENT_ENEMY,   state_e.STATE_ATTACK),
    state_transition_s(state_e.STATE_ATTACK, state_event_e.STATE_EVENT_LINE,    state_e.STATE_RETREAT),
    state_transition_s(state_e.STATE_ATTACK, state_event_e.STATE_EVENT_NONE,    state_e.STATE_SEARCH), 
    state_transition_s(state_e.STATE_ATTACK, state_event_e.STATE_EVENT_COMMAND, state_e.STATE_MANUAL),
    state_transition_s(state_e.STATE_ATTACK, state_event_e.STATE_EVENT_TIMEOUT, state_e.STATE_ATTACK),

    state_transition_s(state_e.STATE_RETREAT, state_event_e.STATE_EVENT_LINE,     state_e.STATE_RETREAT),
    state_transition_s(state_e.STATE_RETREAT, state_event_e.STATE_EVENT_FINISHED, state_e.STATE_SEARCH),
    state_transition_s(state_e.STATE_RETREAT, state_event_e.STATE_EVENT_TIMEOUT,  state_e.STATE_RETREAT),
    state_transition_s(state_e.STATE_RETREAT, state_event_e.STATE_EVENT_ENEMY,    state_e.STATE_RETREAT),
    state_transition_s(state_e.STATE_RETREAT, state_event_e.STATE_EVENT_NONE,     state_e.STATE_RETREAT),
    state_transition_s(state_e.STATE_RETREAT, state_event_e.STATE_EVENT_COMMAND,  state_e.STATE_MANUAL),

    state_transition_s(state_e.STATE_MANUAL, state_event_e.STATE_EVENT_COMMAND, state_e.STATE_MANUAL),
    state_transition_s(state_e.STATE_MANUAL, state_event_e.STATE_EVENT_NONE,    state_e.STATE_MANUAL),
    state_transition_s(state_e.STATE_MANUAL, state_event_e.STATE_EVENT_LINE,    state_e.STATE_MANUAL),
    state_transition_s(state_e.STATE_MANUAL, state_event_e.STATE_EVENT_ENEMY,   state_e.STATE_MANUAL),
]

class StateMachine:
    def __init__(self, user) -> None:
        from bot.bot import Bot
        self.user: Bot = user 
        self.state = state_e.STATE_WAIT

        # states
        self.wait_state: state_wait_s
        self.search_state: state_search_s
        self.attack_state: state_attack_s
        self.retreat_state: state_retreat_s
        self.manual_state: state_manual_s

        # other 
        self.internal_event: state_event_e
        self.timer: Timer = 0
        self.input_history: RingBuffer

        # common data 
        self.enemy: enemy_s
        self.line: line_pos_e
        self.command: ir_command_e

    def has_internal_event(self): 
        return self.internal_event != state_event_e.STATE_EVENT_NONE
    
    def take_internal_event(self):
        event = self.internal_event
        self.internal_event = state_event_e.STATE_EVENT_NONE
        return event
    
    def post_internal_event(self, event):
        self.internal_event = event

    def statemachine_init(self) -> None:
        self.wait_state = state_wait_s(self)
        self.search_state = state_search_s(self)
        self.attack_state = state_attack_s(self)
        self.retreat_state = state_retreat_s(self)
        self.manual_state = state_manual_s(self) 
        self.internal_event = state_event_e.STATE_EVENT_NONE
        self.timer = self.user.timer

        # TODO init input history 

        self.enemy = enemy_s(enemy_pos_e.ENEMY_POS_NONE, enemy_range_e.ENEMY_RANGE_NONE)        
        self.line = line_pos_e.LINE_NONE
        self.command = ir_command_e.NONE

        # init states 
        self.search_state.state_search_init()
        self.attack_state.state_attack_init()
        self.retreat_state.state_retreat_init()

    def process_input(self) -> state_event_e: # get intput from drivers
        self.line: line_pos_e = self.user.get_line_position()
        self.enemy: enemy_s = self.user.get_enemy_position()
        self.command: ir_command_e = self.user.get_ir_command()

        # TODO get input history and save to ring buffer 

        if self.command != ir_command_e.NONE:
            return state_event_e.STATE_EVENT_COMMAND
        elif self.has_internal_event():
            return self.take_internal_event()
        elif self.timer.timer_timeout():
            return state_event_e.STATE_EVENT_TIMEOUT
        elif self.line != line_pos_e.LINE_NONE:
            return state_event_e.STATE_EVENT_LINE
        elif enemy_detected(self.enemy):
            return state_event_e.STATE_EVENT_ENEMY
        return state_event_e.STATE_EVENT_NONE

    def process_event(self, next_event): # choose event based on input 
        for i in range(len(state_transitions)):
            if self.state == state_transitions[i].from_state and next_event == state_transitions[i].state_event:
                self.state_enter(state_transitions[i].from_state, next_event, state_transitions[i].to_state)
                return 
        assert(0, 'no event found')

    def state_enter(self, from_state, next_event, to_state):
        #print(from_state, next_event, to_state, self.timer.time)
        if from_state != to_state: 
            self.timer.clear()
            self.state = to_state

        if to_state == state_e.STATE_WAIT:
            self.wait_state.enter(from_state, next_event)
            return
        elif to_state == state_e.STATE_SEARCH:
            self.search_state.enter(from_state, next_event)
            return 
        elif to_state == state_e.STATE_ATTACK:
            self.attack_state.enter(from_state, next_event)
            return
        elif to_state == state_e.STATE_RETREAT:
            self.retreat_state.enter(from_state, next_event)
            return 
        elif to_state == state_e.STATE_MANUAL:
            self.manual_state.enter(from_state, next_event)
            return 

    def run(self):
        event = self.process_input()
        self.process_event(event)

# --------------------------------- SEARCH ------------------------------ #
class Internal_Search_State(Enum):
    SEARCH_STATE_ROTATE = 0
    SEARCH_STATE_FORWARD = 1

SEARCH_ROTATE_TIMEOUT = 600
SEARCH_FORWARD_TIMEOUT = 800

class state_search_s:
    def __init__(self, state_machine) -> None:
        self.state_machine: StateMachine = state_machine
        self.state: state_e = state_e.STATE_SEARCH
        self.internal_state: Internal_Search_State

    def enter(self, from_state: state_e, event: state_event_e):
        if from_state == state_e.STATE_WAIT:
            # COMING FROM WAIT, ONLY IF COMMAND IS RECEIVED
            assert (0, 'state event')
            self.run()
        elif from_state == state_e.STATE_ATTACK or from_state == state_e.STATE_RETREAT:
            if event == state_event_e.STATE_EVENT_NONE:  # IF FROM ATTACK AND EVENT IS NONE
                assert from_state == state_e.STATE_ATTACK, f'ERROR: in SEARCH_STATE_ENTER, EVENT: {event}, SHOULD ONLY COME FROM {state_e.STATE_ATTACK}'
                self.run()
            elif event == state_event_e.STATE_EVENT_FINISHED:  # IF FROM RETREAT AND FINISHED WITH ALL RETREATS
                assert from_state == state_e.STATE_RETREAT, f'ERROR: in SEARCH_STATE_ENTER, EVENT: {event}, SHOULD ONLY COME FROM {state_e.STATE_RETREAT}'
                if self.internal_state == Internal_Search_State.SEARCH_STATE_FORWARD:  # PREVENT FROM GOING BACK AND FORTH
                    self.internal_state = Internal_Search_State.SEARCH_STATE_ROTATE
                self.run()
            elif event in (
                state_event_e.STATE_EVENT_COMMAND,
                state_event_e.STATE_EVENT_TIMEOUT,
                state_event_e.STATE_EVENT_LINE,
                state_event_e.STATE_EVENT_ENEMY
            ):
                assert 0, f'ERROR: in SEARCH_STATE_ENTER, event should never be {event}'

        elif from_state == state_e.STATE_SEARCH:
            if event == state_event_e.STATE_EVENT_NONE:  # IN SEARCH STATE AND NOTHING HAS HAPPENED
                return
            elif event == state_event_e.STATE_EVENT_TIMEOUT:  # STILL IN SEARCH GO TO NEXT SEARCH MOVE
                if self.internal_state == Internal_Search_State.SEARCH_STATE_ROTATE:
                    self.internal_state = Internal_Search_State.SEARCH_STATE_FORWARD
                elif self.internal_state == Internal_Search_State.SEARCH_STATE_FORWARD:
                    self.internal_state = Internal_Search_State.SEARCH_STATE_ROTATE
                self.run()
            else:
                assert 0, f'ERROR: in SEARCH_STATE_ENTER, EVENT SHOULD NEVER BE |{event}| IF FROM |{state_e.STATE_SEARCH}|'
        elif from_state == state_e.STATE_MANUAL:
            pass

    def run(self):
        if self.internal_state == Internal_Search_State.SEARCH_STATE_ROTATE:
            rnd = random.choice([Drive_Dir.DRIVE_DIR_ROTATE_LEFT, Drive_Dir.DRIVE_DIR_ROTATE_RIGHT])
            drive_set(rnd, Drive_Speed.DRIVE_SPEED_MAX, self.state_machine.user)
            self.state_machine.timer.start_new_timer(SEARCH_ROTATE_TIMEOUT)
            '''
            TODO 
            last_enemy: enemy_s = input_history_last_directed_enemy(search_state.common_data.input_history)
            if last_enemy and enemy_at_right(last_enemy):
                drive_set(Drive_Dir.DRIVE_DIR_ROTATE_RIGHT, Drive_Speed.DRIVE_SPEED_MAX, self.common_data.state_machine.user)
            else:
                drive_set(Drive_Dir.DRIVE_DIR_ROTATE_LEFT, Drive_Speed.DRIVE_SPEED_MAX, search_state.common_data.state_machine.user)           
            '''

        elif self.internal_state == Internal_Search_State.SEARCH_STATE_FORWARD:
            drive_set(Drive_Dir.DRIVE_DIR_FORWARD, Drive_Speed.DRIVE_SPEED_MAX, self.state_machine.user)
            self.state_machine.timer.start_new_timer(SEARCH_FORWARD_TIMEOUT)

    def state_search_init(self):
        self.internal_state = Internal_Search_State.SEARCH_STATE_ROTATE

# --------------------------------- ATTACK ------------------------------ #
class Internal_Attack_State(Enum):  # three internal states
    ATTACK_STATE_FORWARD = 0
    ATTACK_STATE_LEFT = 1
    ATTACK_STATE_RIGHT = 2
ATTACK_STATE_TIMEOUT = 3400

class state_attack_s:
    def __init__(self, state_machine) -> None:
        self.state: state_e = state_e.STATE_ATTACK
        self.state_machine: StateMachine = state_machine
        self.internal_state: Internal_Attack_State

    def enter(self, from_state: state_e, event: state_event_e):  
        prev_attack_state = self.internal_state
        self.internal_state = self.next_attack_state(self.state_machine.enemy)

        if from_state == state_e.STATE_SEARCH: # JUST DETECTED ENEMY
            if event == state_event_e.STATE_EVENT_ENEMY:
                self.state_attack_run()
            else:
                assert 0, f'ERROR IN ATTACK ENTER FROM SEARCH, EVENT SHOULD NOT BE {event}'
        elif from_state == state_e.STATE_ATTACK: # STILL IN ATTACK STATE
            if event == state_event_e.STATE_EVENT_ENEMY: # IF DETECTED ENEMY AGAIN, COULD BE IN DIFFERENCE DIRECTION
                if prev_attack_state != self.internal_state:
                    self.state_attack_run()
                    # BREAK
            elif event == state_event_e.STATE_EVENT_TIMEOUT:
                assert 0, "NOTE: MIGHT HAVE TO IMPLEMENT NEW STRATEGY"
            else:
                assert 0, f'ERROR: IN ATTACK ENTER FROM ATTACK, EVENT SHOULD NOT BE {event}'
        elif from_state == state_event_e.STATE_RETREAT:
            assert 0, f'ERROR: IN ATTACK FROM RETREAT, SHOULD GO THROUGH SEARCH BEFORE THIS'
        else:
            assert 0, f'ERROR: IN ATTACK FROM |{from_state}|'

    def next_attack_state(self, enemy: enemy_s) -> Internal_Attack_State:
        if enemy_at_front(enemy):
            return Internal_Attack_State.ATTACK_STATE_FORWARD
        elif enemy_at_left(enemy):
            return Internal_Attack_State.ATTACK_STATE_LEFT
        elif enemy_at_right(enemy):
            return Internal_Attack_State.ATTACK_STATE_RIGHT
        else:
            assert 0, f'ERROR: ENEMY SHOULD BE ONE OF THREE DIRECTIONS'
        return Internal_Attack_State.ATTACK_STATE_FORWARD

    def state_attack_run(self):
        if self.internal_state == Internal_Attack_State.ATTACK_STATE_FORWARD:
            drive_set(Drive_Dir.DRIVE_DIR_FORWARD, Drive_Speed.DRIVE_SPEED_MAX,
                    self.state_machine.user)
        elif self.internal_state == Internal_Attack_State.ATTACK_STATE_LEFT:
            drive_set(Drive_Dir.DRIVE_DIR_ARCTURN_WIDE_LEFT,
                    Drive_Speed.DRIVE_SPEED_MAX, self.state_machine.user)
        elif self.internal_state == Internal_Attack_State.ATTACK_STATE_RIGHT:
            drive_set(Drive_Dir.DRIVE_DIR_ARCTURN_WIDE_RIGHT,
                    Drive_Speed.DRIVE_SPEED_MAX, self.state_machine.user)
        self.state_machine.timer.start_new_timer(ATTACK_STATE_TIMEOUT)

    def state_attack_init(self):
        self.internal_state = Internal_Attack_State.ATTACK_STATE_FORWARD

# --------------------------------- RETREAT ----------------------------- #
class Internal_Retreat_State(Enum):
    RETREAT_STATE_REVERSE = 0
    RETREAT_STATE_FORWARD = 1
    RETREAT_STATE_ROTATE_LEFT = 2
    RETREAT_STATE_ROTATE_RIGHT = 3
    RETREAT_STATE_ARCTURN_LEFT = 4
    RETREAT_STATE_ARCTURN_RIGHT = 5
    RETREAT_STATE_ALIGN_LEFT = 6
    RETREAT_STATE_ALIGN_RIGHT = 7

@dataclass
class Move:
    direction: Drive_Dir
    speed: Drive_Speed
    duration: float

class Retreat_Move:
    def __init__(self, moves, move_count) -> None:
        self.moves: list[Move] = moves
        self.move_count: int = move_count

retreat_states: list[Retreat_Move] = [
    Retreat_Move(  # RETREAT_STATE_REVERSE
        moves=[Move(direction=Drive_Dir.DRIVE_DIR_REVERSE, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=300)], 
        move_count=1
    ),
    Retreat_Move(  # RETREAT_STATE_FORWARD
        moves=[Move(direction=Drive_Dir.DRIVE_DIR_FORWARD, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=300)], 
        move_count=1
    ),
    Retreat_Move(  # RETREAT_STATE_ROTATE_LEFT
        moves=[Move(direction=Drive_Dir.DRIVE_DIR_ROTATE_LEFT, speed=Drive_Speed.DRIVE_SPEED_FAST, duration=300)],
        move_count=1
    ),
    Retreat_Move(  # RETREAT_STATE_ROTATE_RIGHT
        moves=[Move(direction=Drive_Dir.DRIVE_DIR_ROTATE_RIGHT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=300)],
        move_count=1
    ),
    Retreat_Move(  # RETREAT_STATE_ARCTURN_LEFT
        moves=[Move(direction=Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_LEFT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=300)],
        move_count=1
    ),
    Retreat_Move(  # RETREAT_STATE_ARCTURN_RIGHT
        moves=[Move(direction=Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_RIGHT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=300)],
        move_count=1
    ),
    Retreat_Move(  # RETREAT_STATE_ALIGN_LEFT
        moves=[
            Move(direction=Drive_Dir.DRIVE_DIR_REVERSE, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=250),
            Move(direction=Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_LEFT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=120),
            Move(direction=Drive_Dir.DRIVE_DIR_ARCTURN_MID_RIGHT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=120),
        ],
        move_count=3
    ),
    Retreat_Move(  # RETREAT_STATE_ALIGN_RIGHT
        moves=[
            Move(direction=Drive_Dir.DRIVE_DIR_REVERSE, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=250),
            Move(direction=Drive_Dir.DRIVE_DIR_ARCTURN_SHARP_RIGHT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=120),
            Move(direction=Drive_Dir.DRIVE_DIR_ARCTURN_MID_LEFT, speed=Drive_Speed.DRIVE_SPEED_MAX, duration=120),
        ],
        move_count=3
    ),
]

class state_retreat_s:
    def __init__(self, state_machine) -> None:
        self.state: state_e = state_e.STATE_RETREAT
        self.state_machine: StateMachine = state_machine
        self.internal_state: Internal_Retreat_State
        self.move_idx: int = 0

    def enter(self, from_state: state_e, event: state_event_e):
        if from_state == state_e.STATE_SEARCH or from_state == state_e.STATE_ATTACK:
            if event == state_event_e.STATE_EVENT_LINE:
                self.state_retreat_run()
            else:
                assert 0, f'ERROR IN ENTER_RETREAT_STATE, EVENT |{event}| SHOULD NOT CAUSE REREAT'
        elif from_state == state_e.STATE_RETREAT:  # CURRENTLY DRIVING AWAY FROM LINE
            if event == state_event_e.STATE_EVENT_LINE:  # DETECTED LINE AGAIN, RESTART
                self.state_retreat_run()
            elif event == state_event_e.STATE_EVENT_TIMEOUT:  # DONE WITH CURRENT MOVE, INCREMENT MOVE INDEX
                self.move_idx += 1
                if self.retreat_state_done():
                    # POST EVENT FINISHED SINCE REREAT STATE IS ONLY PLACE KNOWS WHETHER DONE WITH THIS STATE
                    # STATE MACHINE WILL PICK UP THIS EVENT AND TRANSITION TO NEW STATE
                    self.state_machine.post_internal_event(state_event_e.STATE_EVENT_FINISHED)
                else:
                    self.start_retreat_move()
            elif event == state_event_e.STATE_EVENT_NONE or event == state_event_e.STATE_EVENT_ENEMY:  # IGNORE ENEMY WHEN RETREATING
                pass
            else:
                assert 0, f'ERROR IN ENTER_RETREAT_STATE, EVENT |{event}| SHOULD NOT CAUSE RETREAT'
        else:
            assert 0, f'ERROR IN ENTER_RETREAT_STATE, SHOULD NOT COME FROM |{from_state}|'

    def state_retreat_run(self):
        self.move_idx = 0
        self.internal_state = self.next_retreat_state()  # DECIDE WHICH NEXT RETREAT STATE TO USE BASED ON LINE DETECTION
        self.start_retreat_move()

    def start_retreat_move(self):
        assert self.move_idx < retreat_states[self.internal_state.value].move_count, f'ERROR IN START_RETREAT_MOVE, INDEX TOO LARGE FOR RETERAT MOVES {retreat_states[self.internal_state.value]}'
        move: Move = retreat_states[self.internal_state.value].moves[self.move_idx]
        self.state_machine.timer.start_new_timer(move.duration)

        drive_set(move.direction, move.speed, self.state_machine.user)

    def retreat_state_done(self) -> bool: 
        return self.move_idx == retreat_states[self.internal_state.value].move_count

    def current_move(self) -> Move:
        return retreat_states[self.internal_state.value].moves[self.move_idx]

    def next_retreat_state(self) -> Internal_Retreat_State:
        line: line_pos_e = self.state_machine.line

        if line == line_pos_e.LINE_FRONT_LEFT:
            if enemy_at_right(self.state_machine.enemy) or enemy_at_front(self.state_machine.enemy):
                return Internal_Retreat_State.RETREAT_STATE_ALIGN_RIGHT
            elif enemy_at_left(self.state_machine.enemy):
                return Internal_Retreat_State.RETREAT_STATE_ALIGN_LEFT
            else:
                return Internal_Retreat_State.RETREAT_STATE_REVERSE

        elif line == line_pos_e.LINE_FRONT_RIGHT:
            if enemy_at_left(self.state_machine.enemy) or enemy_at_front(self.state_machine.enemy):
                return Internal_Retreat_State.RETREAT_STATE_ALIGN_LEFT
            elif enemy_at_right(self.state_machine.enemy):
                return Internal_Retreat_State.RETREAT_STATE_ALIGN_RIGHT
            else:
                return Internal_Retreat_State.RETREAT_STATE_REVERSE

        elif line == line_pos_e.LINE_BACK_LEFT:
            if self.current_move().direction == Drive_Dir.DRIVE_DIR_REVERSE:
                return Internal_Retreat_State.RETREAT_STATE_ARCTURN_RIGHT
            elif self.internal_state == Internal_Retreat_State.RETREAT_STATE_ARCTURN_RIGHT:
                return Internal_Retreat_State.RETREAT_STATE_ARCTURN_RIGHT
            return Internal_Retreat_State.RETREAT_STATE_FORWARD

        elif line == line_pos_e.LINE_BACK_RIGHT:
            if self.current_move().direction == Drive_Dir.DRIVE_DIR_REVERSE:
                return Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT
            elif self.internal_state == Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT:
                return Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT
            return Internal_Retreat_State.RETREAT_STATE_FORWARD

        elif line == line_pos_e.LINE_FRONT:
            if enemy_at_front(self.state_machine.enemy):
                return Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT
            elif enemy_at_right(self.state_machine.enemy):
                return Internal_Retreat_State.RETREAT_STATE_ALIGN_RIGHT
            else:
                return Internal_Retreat_State.RETREAT_STATE_REVERSE

        elif line == line_pos_e.LINE_BACK:
            return Internal_Retreat_State.RETREAT_STATE_FORWARD

        elif line == line_pos_e.LINE_LEFT:
            return Internal_Retreat_State.RETREAT_STATE_ARCTURN_RIGHT

        elif line == line_pos_e.LINE_RIGHT:
            return Internal_Retreat_State.RETREAT_STATE_ARCTURN_LEFT

        elif line == line_pos_e.LINE_DIAGONAL_LEFT:
            assert 0, f'ERROR IN NEXT_RETREAT_STATE, LINE: |{line}| NOT LIKELY'
        elif line == line_pos_e.LINE_DIAGONAL_RIGHT:
            assert 0, f'ERROR IN NEXT_RETREAT_STATE, LINE: |{line}| NOT LIKELY'
        elif line == line_pos_e.LINE_NONE:
            assert 0, f'ERROR IN NEXT_RETREAT_STATE, LINE SHOULD NOT BE NONE'

        return Internal_Retreat_State.RETREAT_STATE_REVERSE

    def state_retreat_init(self):
        self.internal_state = Internal_Retreat_State.RETREAT_STATE_REVERSE
        self.move_idx = 0

# ---------------------------------- WAIT ------------------------------- #
class state_wait_s:
    def __init__(self, state_machine) -> None:
        self.state_machine = state_machine
        self.state: state_e = state_e.STATE_WAIT

    def enter(self, from_state: state_e, event: state_event_e):
        assert from_state == state_e.STATE_WAIT, "SHOULD ONLY ONE FROM WAIT STATE"

# --------------------------------- MANUAL ------------------------------ #
class state_manual_s: 
    def __init__(self, state_machine) -> None:
        self.state_machine: StateMachine = state_machine
        self.state: state_e = state_e.STATE_MANUAL

    def enter(self, from_state: state_e, event: state_event_e):
        print(event)
        if event != state_event_e.STATE_EVENT_COMMAND:
            return
        command = self.state_machine.command
        if command == ir_command_e.TWO:
            drive_set(Drive_Dir.DRIVE_DIR_FORWARD, Drive_Speed.DRIVE_SPEED_MAX, self.state_machine.user)
        elif command == ir_command_e.THREE:
            drive_set(Drive_Dir.DRIVE_DIR_REVERSE, Drive_Speed.DRIVE_SPEED_MAX, self.state_machine.user)
        elif command == ir_command_e.FOUR:
            drive_set(Drive_Dir.DRIVE_DIR_ROTATE_LEFT, Drive_Speed.DRIVE_SPEED_MAX, self.state_machine.user)
        elif command == ir_command_e.FIVE:
            drive_set(Drive_Dir.DRIVE_DIR_ROTATE_RIGHT, Drive_Speed.DRIVE_SPEED_MAX, self.state_machine.user)
        elif command == ir_command_e.SIX:
            DRIVE_STOP(self.state_machine.user)