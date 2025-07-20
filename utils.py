from settings import * 

# image functions 
def get_image(path: str, scale: list):
    image = pg.image.load(path)
    image = pg.transform.scale(image, (scale[0], scale[1]))
    return image

# proj specific 
def mask_collision(mask1, pos1, mask2, pos2): 
    return mask2.overlap(mask1, (pos1.x - pos2.x, pos1.y - pos2.y))

def check_circle_collision(circle1, circle2):
    dist = math.sqrt( math.pow(circle1[0] - circle2[0], 2) + math.pow(circle1[1] - circle2[1], 2) )
    if dist < circle1[2] + circle2[2]: return True
    return False

# math functions 
def distance(p1, p2): 
    return math.sqrt( math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2) )

# random functions
def rnd_percent_chance(probability_per_frame=0.1):
    return random.random() < probability_per_frame

# Vector Functions
def v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1]

def v_normalize(v):
    res = v.copy()
    l = v_length(v)
    res[0] = res[0] / l
    res[1] = res[1] / l
    return res

def v_length(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1])

def v_add(a, b):
    return [a[0]+b[0], a[1]+b[1]]

def v_scale(v, x):
    return [v[0] * x, v[1] * x]

def v_angle(v):
    angle_rad = math.atan2(v[1], v[0])
    angle_deg = math.degrees(angle_rad)
    return angle_deg


