from settings import * 
from utils import * 
from statemachine.statemachine import * 
from statemachine.line import * 
from statemachine.enemy import * 

LINE_DIST = 22
LINE_R = 4

class Bot:
    def __init__(self, eng, pos, size, img, bot_type) -> None:
        self.eng = eng 
        self.pos = pos.copy()
        self.size = size 
        self.img = img 
        self.bot_type = bot_type
        self.statemachine = StateMachine(self)
        # other 
        self.timer = self.eng.timer
        # Movement
        self.vel = [0,0]
        self.force = [0,0]
        self.target = None 
        self.speed = 4
        self.turn_speed = 4
        self.angle = 0 

        # Properties 
        self.modes = {'manual': 0, 'auto': 1}
        self.mode = self.modes['manual'] 
        self.mask = pg.mask.from_surface(img)
        self.angles = [45, 135, 225, 315]
        self.vertices = [[0,0], [0,0], [0,0], [0,0]]
        self.drive_setting: Drive_Settings = Drive_Settings(0, 0, 0)

        # Peripherals
        self.line_sensors = [False, False, False, False]
        self.enemy_sensors = [False, False, False]
        self.range_distance = [inf, inf, inf]
        self.obj_range = inf 
        self.obj_sensor = False

        # init 
        self.statemachine.statemachine_init() 

    def get_state_machine_data(self):
        if self.statemachine.state == state_e.STATE_WAIT:
            print('WAIT')
        elif self.statemachine.state == state_e.STATE_SEARCH:
            print('SEARCH')
        elif self.statemachine.state == state_e.STATE_RETREAT:
            print('RETREAT')
        elif self.statemachine.state == state_e.STATE_ATTACK:
            print('ATTACK')
        elif self.statemachine.state == state_e.STATE_MANUAL:
            print('MANUAL')
    
    def update(self, dt):
        self.angle %= 360
        if self.mode == self.modes['manual']:
            self.manual_movement()
        else:
            self.auto_movement()
        self.statemachine.run()

        #self.get_state_machine_data()

    def render(self, surf, dt):
        self.update(dt)
        img = pg.transform.rotate(self.img, -self.angle)
        img_rect = img.get_rect(center=(self.pos[0], self.pos[1]))
        surf.blit(img, img_rect)

        if self.mode == self.modes['manual']: pg.draw.circle(surf, GREEN, (self.pos[0], self.pos[1]), 6)
        else: pg.draw.circle(surf, RED, (self.pos[0], self.pos[1]), 6)

        self.update_line_sensors(surf)
        self.raycast()

    def manual_movement(self):
        movement = self.eng.movement.copy() 
        self.angle += (movement[1] - movement[0]) * self.turn_speed
        fwd = self.speed if movement[2] else 0
        bwd = -self.speed if movement[3] else 0
        v = [math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))]
        v = v_normalize(v)
        v = v_scale(v,fwd + bwd)
        self.pos[0] += v[0]
        self.pos[1] += v[1]

    def auto_movement(self):
        self.angle += self.drive_setting.right - self.drive_setting.left
        x_speed = math.cos(math.radians(self.angle))
        y_speed = math.sin(math.radians(self.angle))
        vel = v_scale([x_speed, y_speed], self.drive_setting.speed * 0.6)
        self.pos[0] += vel[0]
        self.pos[1] += vel[1]

    def change_mode(self):
        if self.mode == self.modes['manual']: self.mode = self.modes['auto']
        else: self.mode = self.modes['manual']

    # get driver data 
    def get_ir_command(self):
        for i in range(9):
            if self.eng.commands[i+1]:
                return command_enums[i]
        return ir_command_e.NONE 
    
    def get_line_position(self):
        front_right = self.line_sensors[0]
        front_left = self.line_sensors[3]
        back_right = self.line_sensors[1]
        back_left = self.line_sensors[2]
        if front_left:
            if front_right:
                return line_pos_e.LINE_FRONT
            elif back_left:
                return line_pos_e.LINE_LEFT
            elif back_right:
                return line_pos_e.LINE_DIAGONAL_LEFT
            else:
                return line_pos_e.LINE_FRONT_LEFT
        elif front_right:
            if back_right:
                return line_pos_e.LINE_RIGHT
            elif back_left:
                return line_pos_e.LINE_DIAGONAL_RIGHT
            else:
                return line_pos_e.LINE_FRONT_RIGHT
        elif back_left:
            if back_right:
                return line_pos_e.LINE_BACK
            else:
                return line_pos_e.LINE_BACK_LEFT
        elif back_right:
            return line_pos_e.LINE_BACK_RIGHT
        return line_pos_e.LINE_NONE
    
    def get_enemy_position(self):
        enemy = enemy_s(enemy_pos_e.ENEMY_POS_NONE, enemy_range_e.ENEMY_RANGE_NONE)
        enemy_range: int = 0

        front_range: float = self.range_distance[1]
        front_left_range: float = self.range_distance[0]
        front_right_range: float = self.range_distance[2]

        front: bool = front_range < RANGE_THRESHOLD
        front_left: bool = front_left_range < RANGE_THRESHOLD
        front_right: bool = front_right_range < RANGE_THRESHOLD

        if front and front_left and front_right:
            enemy.position = enemy_pos_e.ENEMY_POS_FRONT_ALL
            enemy_range = (front_range + front_left_range + front_right_range) // 3
        elif front_left and front_right:
            enemy.position = enemy_pos_e.ENEMY_POS_IMPOSSIBLE
        elif front_left:
            if front:
                enemy.position = enemy_pos_e.ENEMY_POS_FRONT_AND_FRONT_LEFT
                enemy_range = (front_range + front_left_range) // 2
            else:
                enemy.position = enemy_pos_e.ENEMY_POS_FRONT_LEFT
                enemy_range = front_left_range // 1
        elif front_right:
            if front:
                enemy.position = enemy_pos_e.ENEMY_POS_FRONT_AND_FRONT_RIGHT
                enemy_range = (front_range + front_right_range) // 2
            else:
                enemy.position = enemy_pos_e.ENEMY_POS_FRONT_RIGHT
                enemy_range = front_right_range // 1
        elif front:
            enemy.position = enemy_pos_e.ENEMY_POS_FRONT
            enemy_range = front_range // 1
        else:
            enemy.position = enemy_pos_e.ENEMY_POS_NONE
        
        if enemy_range == 0: return enemy

        if enemy_range > 200: enemy.range = enemy_range_e.ENEMY_RANGE_FAR
        elif enemy_range > 100: enemy.range = enemy_range_e.ENEMY_RANGE_MID
        else: enemy.range = enemy_range_e.ENEMY_RANGE_CLOSE
        return enemy

    # drivers 
    def update_line_sensors(self, surf):
        self.line_sensors = [False, False, False, False]
        for i in range(len(self.angles)):
            offset = self.angles[i]
            x_speed = math.cos(math.radians(self.angle + offset)) * LINE_DIST
            y_speed = math.sin(math.radians(self.angle + offset)) * LINE_DIST
            vertex = [ self.pos[0] + x_speed, self.pos[1] + y_speed ]

            pg.draw.circle(surf, GREEN, (vertex[0], vertex[1]), LINE_R)
            if not check_circle_collision([vertex[0], vertex[1], LINE_R], [CENTER[0], CENTER[1], ARENA['rad']-LINE_R]):
                pg.draw.circle(surf, RED, (vertex[0], vertex[1]), LINE_R)
                self.line_detected_bool = True
                self.line_sensors[i] = True

            vertex_pos = [ self.pos[0] , self.pos[1] ]
            if self.angles[i] == 45: self.vertices[2] = vertex_pos     # bottom right
            elif self.angles[i] == 135: self.vertices[3] = vertex_pos  # bottom left
            elif self.angles[i] == 225: self.vertices[0] = vertex_pos  # top left
            elif self.angles[i] == 315: self.vertices[1] = vertex_pos  # top right

    def raycast(self):
        self.enemy_sensors = [False, False, False]
        self.range_distance = [inf, inf, inf]
        angles = [-15, 0, 15]
        for i in range(len(angles)):
            angle = math.radians(self.angle + angles[i]) + .0001
            if angle < 0:
                angle += 2 * math.pi
            if angle > math.pi * 2:
                angle -= 2 * math.pi

            horiz_dist = float('inf')
            vert_dist = float('inf')

            player_pos = self.pos.copy()

            horiz_x, horiz_y, horiz_hit = self.check_horizontal(angle, player_pos)
            vert_x, vert_y, vert_hit = self.check_vertical(angle, player_pos)

            horiz_dist = distance(player_pos, [horiz_x,horiz_y])
            vert_dist = distance(player_pos, [vert_x,vert_y])
            end_x = 0
            end_y = 0

            if vert_dist < horiz_dist:
                end_x, end_y = vert_x, vert_y
            if horiz_dist < vert_dist:
                end_x, end_y = horiz_x, horiz_y

            if not horiz_hit and not vert_hit:
                tile_key = f'{int(end_x // CS)},{int(end_y // CS)}'
                self.line_of_sight = False
                self.enemy_in_front_bool = False
                pg.draw.line(self.eng.surf, RED, (self.pos[0], self.pos[1]), (end_x, end_y), 1)
            else:
                self.line_of_sight = True
                self.enemy_in_front_bool = True
                self.enemy_sensors[i] = True
                self.range_distance[i] = min(horiz_dist, vert_dist)
                pg.draw.line(self.eng.surf, GREEN, (self.pos[0], self.pos[1]), (end_x, end_y), 1)

    def check_horizontal(self, ray_angle, player_pos):
        player_x = player_pos[0]
        player_y = player_pos[1]
        ray_pos_x = 0
        ray_pos_y = 0
        y_offset = 0
        x_offset = 0
        a_tan = -1 / math.tan(ray_angle)
        dof = 16
        player_hit = False

        if ray_angle > math.pi:  # looking up
            ray_pos_y = int(player_y // CS) * CS - .0001
            ray_pos_x = (player_y - ray_pos_y) * a_tan + player_x
            y_offset = -CS
            x_offset = -y_offset * a_tan
        if ray_angle < math.pi:  # looking down
            ray_pos_y = int(player_y // CS) * CS + CS
            ray_pos_x = (player_y - ray_pos_y) * a_tan + player_x
            y_offset = CS
            x_offset = -y_offset * a_tan
        if ray_angle == 0 or ray_angle == math.pi:
            ray_pos_x = player_x
            ray_pos_y = player_y
            dof = 0

        player_key = f'{int(self.target.pos[0] // CS)},{int(self.target.pos[1] // CS)}'
        for i in range(dof):
            ray_pos = (int(ray_pos_x // CS), int(ray_pos_y // CS))
            str_ray_pos = f'{ray_pos[0]},{ray_pos[1]}'
            if ray_pos[0] < -1 or ray_pos[0] > 20 or ray_pos[1] < -1 or ray_pos[1] > 20:
                break
            # if str_ray_pos in self.app.tile_map.tiles: break
            if player_key == str_ray_pos:
                player_hit = True
                break
            ray_pos_x += x_offset
            ray_pos_y += y_offset

        return ray_pos_x, ray_pos_y, player_hit

    def check_vertical(self, ray_angle, player_pos):
        player_x = player_pos[0]
        player_y = player_pos[1]
        ray_pos_x = 0
        ray_pos_y = 0
        y_offset = 0
        x_offset = 0
        n_tan = -math.tan(ray_angle)
        dof = 16
        player_hit = False

        P2 = math.pi / 2
        P3 = (math.pi * 3) / 2

        if ray_angle > P2 and ray_angle < P3:  # looking left
            ray_pos_x = int(player_x // CS) * CS - .0001
            ray_pos_y = (player_x - ray_pos_x) * n_tan + player_y
            x_offset = -CS
            y_offset = -x_offset * n_tan
        if ray_angle < P2 or ray_angle > P3:  # looking right
            ray_pos_x = int(player_x // CS) * CS + CS
            ray_pos_y = (player_x - ray_pos_x) * n_tan + player_y
            x_offset = CS
            y_offset = -x_offset * n_tan
        if ray_angle == 0 or ray_angle == math.pi:
            ray_pos_x = player_x
            ray_pos_y = player_y
            dof = 0

        player_key = f'{int(self.target.pos[0] // CS)},{int(self.target.pos[1] // CS)}'
        for i in range(dof):
            ray_pos = (int(ray_pos_x // CS),
                       int(ray_pos_y // CS))
            str_ray_pos = f'{ray_pos[0]},{ray_pos[1]}'
            if ray_pos[0] < -1 or ray_pos[0] > 20 or ray_pos[1] < -1 or ray_pos[1] > 20:
                break
            # if str_ray_pos in self.app.tile_map.tiles: break
            if player_key == str_ray_pos:
                player_hit = True
                break
            ray_pos_x += x_offset
            ray_pos_y += y_offset

        return ray_pos_x, ray_pos_y, player_hit
    # target 
    def target_update(self, dt):
        self.angle %= 360
        if self.mode == self.modes['manual']:
            self.manual_movement()
        else:
            self.auto_movement()

    def target_render(self, surf, dt):
        self.target_update(dt)
        img = pg.transform.rotate(self.img, -self.angle)
        img_rect = img.get_rect(center=(self.pos[0], self.pos[1]))
        surf.blit(img, img_rect)

        self.update_line_sensors(surf)
        if self.mode == self.modes['manual']: pg.draw.circle(surf, GREEN, (self.pos[0], self.pos[1]), 6)
        else: pg.draw.circle(surf, RED, (self.pos[0], self.pos[1]), 6)
