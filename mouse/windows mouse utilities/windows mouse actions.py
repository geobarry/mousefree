from talon import Module, ui, Context, ctrl, cron, actions, screen
from talon.types import Point2d as Point2d, Rect
from talon.windows import ax as ax, ui as winui
import math

mod = Module()
mod.list("handle_position","position for grabbing ui elements")    
mod.list("move_coordinates","x & y differentials for moving mouse")    
mod.list("move_direction","simple words for mouse movement directions")

ctx = Context()
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
        obj = actions.user.safe_focused_element().rect
        actions.user.mouse_to_obj_handle(obj,hnd_pos,ms,x_offset,y_offset)
    def mouse_to_active_window_handle(hnd_pos: str,ms: int = 350, x_offset: int = 0, y_offset: int = 0):
        """Moves the mouse to one of eight positions on window"""
        obj = actions.user.winax_active_window_rectangle()
        actions.user.mouse_to_obj_handle(obj,hnd_pos,ms,x_offset,y_offset)
    def drag_window_center (bearing: float, d: float):
        """Drags the given bearing and distance in pixels is on the center of the active window"""
        rect = actions.user.winax_active_window_rectangle()
        if rect:
            print(f'rect: {rect}')
            x = rect.x + rect.width/2
            y = rect.y + rect.height / 2
            dx = math.sin(math.radians(bearing))
            dy = math.cos(math.radians(bearing))
            actions.user.slow_mouse(x + dx * d / 2,y - dy * d / 2,0)
            actions.sleep(0.2)
            actions.user.mouse_drag(0)
            # actions.user.compass_jiggle()
            # actions.user.mouse_drag(0)
            actions.sleep(0.5)
            actions.user.slow_mouse(x - dx * d / 2,y + dy * d / 2,1600)
            actions.sleep(2.1)
            actions.user.mouse_drag_end()
