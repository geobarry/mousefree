from talon import Module, Context, clip, ctrl, cron, actions, canvas, screen, settings
from talon.windows import ax as ax, ui as winui
from talon.types import Point2d as Point2d, rect as rect
from talon.skia import  Paint
from typing import Callable

mod = Module()

@mod.action_class
class Actions:
    def snip_rect(rect: rect):
        """performs a screen capture of given rectangle and copies to clipboard"""
        ctrl.mouse_move(rect.x+20,rect.y+20)
        actions.key("super-shift-s")
        actions.sleep(1.5)
        #actions.mouse_click()
        #actions.sleep(1.5)
        actions.user.mouse_drag(0)
        # actions.sleep(1.5)
        actions.user.slow_mouse(rect.x + rect.width-20,rect.y + rect.height-20, ms=3000)
        actions.mouse_release(0)
    def snip_screen():
        """copies current screen capture to clipboard"""
        # move mouse to upper left
        actions.user.snip_rect(winui.main_screen().rect)