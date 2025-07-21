from settings import *
from utils import * 
from bot.bot import *
from timer import * 

'''
    A0: front right line
    A1: front left line
    A2: back right line
    A3: back left line
    A4: right range 
    A5: front range
    A6: left range 
    D12: AIN2
    D11: AIN1
    D10: PWMB 
    D9: PWMA
    D8: BIN2
    D7: BIN1
    D2: IR S
'''

class Engine:
    def __init__(self):
        pg.init()
        # GAME SETTINGS 
        self.running = True
        self.font = pg.font.Font(None, 16)
        self.clock = pg.time.Clock()
        self.screen: pg.display = pg.display.set_mode((W, H))
        self.surf: pg.Surface = pg.Surface((W, H))
        self.dt = 0
        self.tt = 0 
        # INTERACTION SETTINGS 
        self.timer = Timer(self)
        self.mous_pos = [0, 0]
        self.movement = [False, False, False, False]
        self.commands = {1:False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False}
        # BOT 
        self.main_bot = Bot(
            self, 
            POSITIONS['main'].copy(), 
            [CS, CS], 
            get_image(f'{IMG_PATH}temp-bot-0.png', [CS, CS]),
            BOT_TYPES['main']
            )
        self.target_bot = Bot(
            self,
            POSITIONS['target'].copy(),
            [CS, CS],
            get_image(f'{IMG_PATH}temp-bot-1.png', [CS, CS]),
            BOT_TYPES['target']
            )
        self.main_bot.target = self.target_bot   
        self.timer.start_new_timer(1000)

    def render(self):
        self.surf.fill(BLACK)

        # other
        mouse_pos: list = pg.mouse.get_pos()

        # timer 
        self.timer.tick()
        
        # arena
        pg.draw.circle(self.surf, WHITE, (CENTER[0], CENTER[1]), ARENA['rad'], ARENA['w'])

        # bots
        self.main_bot.render(self.surf, self.dt)
        self.target_bot.target_render(self.surf, self.dt)

        # reset
        self.commands = {1:False, 2: False, 3: False, 4: False, 5: False, 6: False, 7: False, 8: False, 9: False}

        self.screen.blit(self.surf, (0, 0))
        pg.display.flip()
        pg.display.update()

    def update(self):
        fps = self.clock.get_fps()
        self.dt = self.clock.tick(FPS) / 1000
        pg.display.set_caption(f"FPS: {fps:.2f}")
        self.tt += self.dt

    def check_inputs(self):
        for e in pg.event.get():
            if e.type == pg.QUIT:
                self.running = False
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    self.running = False
                if e.key == pg.K_a:
                    self.movement[0] = True 
                if e.key == pg.K_d:
                    self.movement[1] = True
                if e.key == pg.K_w:
                    self.movement[2] = True 
                if e.key == pg.K_s:
                    self.movement[3] = True

                if e.key == pg.K_1: self.commands[1] = True
                if e.key == pg.K_2: self.commands[2] = True
                if e.key == pg.K_3: self.commands[3] = True
                if e.key == pg.K_4: self.commands[4] = True
                if e.key == pg.K_5: self.commands[5] = True
                if e.key == pg.K_6: self.commands[6] = True
                if e.key == pg.K_7: self.commands[7] = True
                if e.key == pg.K_8: self.commands[8] = True
                if e.key == pg.K_9: self.commands[9] = True

                if e.key == pg.K_p:
                    self.main_bot.change_mode()
                if e.key == pg.K_o:
                    self.target_bot.change_mode()

            if e.type == pg.KEYUP:
                if e.key == pg.K_a:
                    self.movement[0] = False 
                if e.key == pg.K_d:
                    self.movement[1] = False
                if e.key == pg.K_w:
                    self.movement[2] = False
                if e.key == pg.K_s:
                    self.movement[3] = False
    def run(self):
        while self.running:
            self.check_inputs()
            self.update()
            self.render()

def main():
    eng = Engine()
    eng.run()

main()