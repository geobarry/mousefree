from talon import Context, Module, canvas, cron, ctrl, cron, screen, ui, actions
from talon.types import Point2d as Point2d, Rect
from talon.skia import Canvas as SkCanvas

mod = Module()

@mod.action_class
class Actions:
    def text_aliased(label: str, x: int, y: int, font_size: float, canvas: SkCanvas):
        """Draws some text"""
        paint = canvas.paint
        paint.font.size = font_size
        canvas.paint.style = canvas.paint.Style.FILL
        paint.typeface = "Verdana"
        paint.color = 'ffffff'
        # background thick and black
        limit = int(font_size/5) + 3
        for dx in range(-limit,limit+1):
            for dy in range(-limit,limit+1):
                dist = ((dx ** 2) + (dy ** 2)) ** 0.5
                transparency = min(255,255 * ((dist / limit)**110))
                transparency = 255 - int(transparency)
                transparency = hex(transparency)[2:]
                if len(transparency) == 1:
                    transparency = "0" + transparency
#                transparency = "ff"
                paint.color = f'000000{transparency}'
                canvas.draw_text(label,x + dx,y + dy)

        # fill-white and less transparent
        paint.color = 'ffffff'
        canvas.draw_text(label,x-1,y-1)
        canvas.draw_text(label,x-1,y)
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
    def containing_screen(x: int, y: int):
        """Returns boolean describing if in per coordinates are in any screen"""
        for s in screen.screens():
            if x >= s.x:
                if x < s.x + s.width:
                    if y >= s.y:
                        if y < s.y + s.height:
                            return s
        return None

ctx = Context()