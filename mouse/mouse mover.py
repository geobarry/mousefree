from talon import Module, ui, Context, ctrl, cron, actions, screen
from talon.types import Point2d as Point2d, Rect
from talon.windows import ax as ax, ui as winui
import math

mod = Module()
mod.list("handle_position","position for grabbing ui elements")    
mod.list("move_coordinates","x & y differentials for moving mouse")    
mod.list("move_direction","simple words for mouse movement directions")

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
            self.num_intervals = max(1,math.ceil(totT / interval))
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
    def mouse_to_obj_handle(obj: Rect,hnd_pos: str, ms: int = 350, x_offset: int = 0, y_offset: int = 0):
        """Assumes obj has x,y,width,height properties"""
        #
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
        actions.user.slow_mouse(x,y,ms = ms)
    def mouse_to_screen_handle(hnd_pos: str, ms: int = 350, x_offset: int = 0, y_offset: int = 0):
        """moves mouse to one of eight positions on edge of the main screen"""
        obj = ui.main_screen()
        actions.user.mouse_to_obj_handle(obj,hnd_pos,ms,x_offset,y_offset)
    def mouse_to_focused_element_handle(hnd_pos: str,ms: int = 350, x_offset: int = 0, y_offset: int = 0):
        """Moves mouse to one of eight positions on edge of element"""
        obj = winui.focused_element().rect
        actions.user.mouse_to_obj_handle(obj,hnd_pos,ms,x_offset,y_offset)
    def mouse_to_active_window_handle(hnd_pos: str,ms: int = 350, x_offset: int = 0, y_offset: int = 0):
        """Moves the mouse to one of eight positions on window"""
        obj = winui.active_window().rect
        actions.user.mouse_to_obj_handle(obj,hnd_pos,ms,x_offset,y_offset)
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
    def drag_window_center (bearing: float, d: float):
        """Drags the given bearing and distance in pixels is on the center of the active window"""
        w = winui.active_window()
        if w:
            rect = w.rect
            if rect:
                print(f'rect: {rect}')
                x = rect.x + rect.width/2
                y = rect.y + rect.height / 2
                dx = math.sin(math.radians(bearing))
                dy = math.cos(math.radians(bearing))
                actions.user.slow_mouse(x + dx * d / 2,y - dy * d / 2,100)
                actions.sleep(0.2)
                actions.user.mouse_drag(0)
                # actions.user.compass_jiggle()
                # actions.user.mouse_drag(0)
                actions.sleep(0.5)
                actions.user.slow_mouse(x - dx * d / 2,y + dy * d / 2,1000)
                actions.sleep(1.1)
                actions.user.mouse_drag_end()
    def get_screen_bounds():
        """Experimental function to get bounds of out screens"""
        for x in screen.screens():
            print(f'x: {x}')
    def containing_screen(x: int, y: int):
        """Returns boolean describing if in per coordinates are in any screen"""
        for s in screen.screens():
            if x >= s.x:
                if x < s.x + s.width:
                    if y >= s.y:
                        if y < s.y + s.height:
                            return s
        return None