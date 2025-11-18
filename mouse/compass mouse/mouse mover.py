from talon import Module, ui, Context, ctrl, cron, actions, screen
from talon.types import Point2d as Point2d, Rect
import math

mod = Module()

ctx = Context()
interval = 15
time_mult = 1
class mouse_mover:
    """Moves mouse using cron intervals until destination is reached"""
    def __init__(self, dest: Point2d, ms = None, callback = None):        
        self.callback = callback
        # need to validate destination, can get error: Python int too large to convert to C long
        print("CLASS mouse_mover __init__")
        s = actions.user.containing_screen(dest.x,dest.y)
        if s:
            self.dest = dest
            self.orig = ctrl.mouse_pos()
            self.cur = self.orig
            dx = self.dest.x - self.orig[0]
            dy = self.dest.y - self.orig[1]
            totD = ((dx ** 2) + (dy ** 2)) ** 0.5
            if ms != None:
                totT = ms
            else:
                totT = self.get_move_time(totD)
            self.num_intervals = max(1,math.floor(totT / interval))
            self.interval_x = dx / self.num_intervals
            self.interval_y = dy / self.num_intervals
            self.job = cron.interval(f'{interval}ms', self.move_next)
            self.completed = 0
    def get_move_time(self,d):
        """Calculates the total time to move the mouse based on distance in pixels"""
        # Keys: move distance (pixels)
        # Values: move time (ms)
        print("FUNCTION: get_move_time")
        move_times = {
            -1:50,
            100:200,
            500:350,
            1000:450,
            2000:700,
            10000:1200,
            1000000:100000
        }
        dkeys = sorted(list(move_times))

        d = abs(d)
        id = 0
        while dkeys[id] < d:
            id += 1
        lowD,highD = dkeys[id-1],dkeys[id]
        lowT,highT = time_mult * move_times[lowD],time_mult * move_times[highD]
        print(f'lowT: {lowT}')
        print(f'highT: {highT}')
        return int(lowT + (highT - lowT) * (d - lowD) / (highD - lowD))
    def move_next(self):
        """Moves mouse by one interval until destination reached"""
        # handle last move
        if self.completed >= self.num_intervals:
            ctrl.mouse_move(self.dest.x,self.dest.y)
            cron.cancel(self.job)
            if self.callback != None:
                self.callback()
        else:
            # handle previous moves
            self.completed += 1
            x = round(self.orig[0] + self.interval_x * self.completed)
            y = round(self.orig[1] + self.interval_y * self.completed)
            ctrl.mouse_move(x,y)

@mod.action_class
class Actions:
    def slow_mouse(x: int, y: int, ms: int = None, callback: any = None):
        """moves the mouse slowly towards the target"""
        loc = Point2d(x,y)
        mouse_obj = mouse_mover(loc, ms = ms,callback = callback)
    def slow_mouse_relative(dx: int, dy: int, ms: int = 300, callback: any = None):
        """Slowly moves the mouse in the given relative direction"""
        pos = ctrl.mouse_pos()
        x = pos[0]
        y = pos[1]
        actions.user.slow_mouse(x + dx,y + dy,ms,callback)
