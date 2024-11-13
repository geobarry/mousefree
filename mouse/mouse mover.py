from talon import Module, ui, Context, ctrl, cron, actions
from talon.types import Point2d as Point2d
import math

mod = Module()
mod.list("handle_position","position for grabbing ui elements")    

ctx = Context()

class mouse_mover:
    """Moves mouse using cron intervals until destination is reached"""
    def __init__(self, dest: Point2d, ms = None, callback = None):        
        self.callback = callback
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
        self.num_intervals = max(1,math.ceil(totT / 30))
        self.interval_x = dx / self.num_intervals
        self.interval_y = dy / self.num_intervals
        self.job = cron.interval('30ms', self.move_next)
        self.completed = 0
    def get_move_time(self,d):
        """Calculates the total time to move the mouse based on distance in pixels"""
        # Keys: move distance (pixels)
        # Values: move time (ms)
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
        lowT,highT = move_times[lowD],move_times[highD]
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

def mouse_to_obj_handle(obj,hnd_pos: str, ms: int = 350, x_offset: int = 0, y_offset: int = 0):
    """Assumes obj has x,y,width,height properties"""
    left = obj.x
    right = obj.x + obj.width - 1
    hz_center = int(obj.x + obj.width / 2)
    top = obj.y
    bottom = obj.y + obj.height - 1
    vrt_center = int(obj.y + obj.height / 2)
    pos = {
        'center': (hz_center,vrt_center),
        'left': (left,vrt_center),
        'right': (right,vrt_center),
        'top': (hz_center,top),
        'bottom': (hz_center,bottom),
        'lower left': (left,bottom),
        'upper left': (left,top),
        'lower right': (right,bottom),
        'upper right': (right,top)
    }
    x = pos[hnd_pos][0] + x_offset
    y = pos[hnd_pos][1] + y_offset
    actions.user.slow_mouse(x,y)

@mod.action_class
class Actions:
    def mouse_to_screen_handle(hnd_pos: str, ms: int = 350, x_offset: int = 0, y_offset: int = 0):
        """moves mouse to one of eight positions on edge of the main screen"""
        obj = ui.main_screen()
        mouse_to_obj_handle(obj,hnd_pos,ms,x_offset,y_offset)
    def mouse_to_focused_element_handle(hnd_pos: str,ms: int = 350, x_offset: int = 0, y_offset: int = 0):
        """Moves mouse to one of eight positions on edge of element"""
        obj = ui.focused_element().rect
        print(f'obj: {obj}')
        mouse_to_obj_handle(obj,hnd_pos,ms,x_offset,y_offset)
    def slow_mouse(x: int, y: int, ms: int = None, callback: any = None):
        """moves the mouse slowly towards the target"""
        loc = Point2d(x,y)
        mouse_obj = mouse_mover(loc, ms = ms,callback = callback)
