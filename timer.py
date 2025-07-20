from settings import *

TIME_CLEARED = 0

class Timer():
    def __init__(self, app) -> None:
        self.app = app
        self.timeout = 0
        self.time = 0
        self.timer_on = False

    def clear(self):
        self.reset_timeout()
        self.time = 0

    def reset_timeout(self): 
        self.timeout = 0

    def tick(self):
        self.time += self.app.dt * 1000
        if self.time > 5000:
            self.timer = 0

    def start(self):
        self.timer_on = True

    def stop(self):
        self.timer_on = False

    def start_new_timer(self, timeout):
        self.time = 0
        self.timeout = timeout
        self.start()

    def timer_timeout(self):
        if self.timeout == TIME_CLEARED:
            return False
        timed_out = self.time > self.timeout
        if timed_out:
            self.clear()
            self.reset_timeout()
            self.stop()
        return timed_out