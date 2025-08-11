from talon import Module, ui, Context, actions, screen
from talon.types import Rect

mod = Module()


ctx = Context()
@mod.action_class
class Actions:
    def containing_screen(x: int, y: int):
        """Returns boolean describing if in per coordinates are in any screen"""
        for s in screen.screens():
            if x >= s.x:
                if x < s.x + s.width:
                    if y >= s.y:
                        if y < s.y + s.height:
                            return s
        return None
    def get_screen_bounds():
        """Experimental function to get bounds of out screens"""
        x_min = float('inf')
        y_min = float('inf')
        x_max = float('-inf')
        y_max = float('-inf')
        i = 0
        for s in screen.screens():
            i += 1
            rect = s.rect
            print(f'screen {i} rect: {rect}')
            if rect.x < x_min:
                x_min = rect.x
            if rect.y < y_min:
                y_min = rect.y
            if x_max < rect.x + rect.width:
                x_max = rect.x + rect.width
            if y_max < rect.y + rect.height:
                y_max = rect.y + rect.height
        rect = Rect(x_min,y_min,x_max - x_min,y_max - y_min)
        print(f'COMPREHENSIVE rect: {rect}')
        return rect        