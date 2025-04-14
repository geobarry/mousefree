from talon import Module, Context, clip, ctrl, cron, actions, canvas, screen, settings
from talon.windows import ax as ax, ui as winui
from talon.types import Point2d, Rect
from talon.skia import  Paint
from typing import Callable

saved_rect = []
last_mouse = None

mod = Module()

@mod.action_class
class Actions:
    def snip_rect(rect: Rect):
        """performs a screen capture of given rectangle and copies to clipboard"""
        actions.sleep(2.5)
        ctrl.mouse_move(rect.x,rect.y)
        actions.key("super-shift-s")
        actions.sleep(2.0)
        actions.user.mouse_drag(0)
        actions.user.slow_mouse(rect.x + rect.width-1,rect.y + rect.height-1, ms=300, callback = lambda: actions.mouse_release(0))
    def snip_screen():
        """copies current screen capture to clipboard"""
        actions.user.snip_rect(winui.main_screen().rect)
    def snip_window():
        """copies current window capture to clipboard"""
        actions.user.snip_rect(winui.active_window().rect)
    def snip_element():
        """copies the currently focused element capture to clipboard"""
        actions.user.snip_rect(ax.get_focused_element().rect)
    def save_rect(pt1: tuple = None, pt2: tuple = None, pos: int = -1):
        """records a rectangle for snipping"""
        # get first point
        if pt1 == None:
            pt1 = ctrl.mouse_pos()
        # get second point
        if pt2 == None:
            global last_mouse
            pt2 = last_mouse
            if pt2 == None:
                exit
        # construct rectangle
        xmin = min(pt1[0],pt2[0])
        ymin = min(pt1[1],pt2[1])
        xmax = max(pt1[0],pt2[0])
        ymax = max(pt1[1],pt2[1])
        rect = Rect(xmin,ymin,xmax - xmin,ymax - ymin)
        # manage rectangles list
        if pos < 0 or pos > len(saved_rect) - 1:
            saved_rect.append(rect)
        else:
            saved_rect[pos] = rect
        print(f"FUNCTION save_rect saved_rect:\n{saved_rect}")
    def start_rect():
        """Records current mouse position as start of rectangle"""
        global last_mouse
        last_mouse = ctrl.mouse_pos()
    def snip_saved_rect(pos: int = 0):
        """Captures screen for designated rectangle"""
        if -1 < pos < len(saved_rect):
            actions.user.snip_rect(saved_rect[pos])
    def clear_snip_rect():
        """clears the list of saved snip rectangles"""
        global saved_rect
        saved_rect = []
            