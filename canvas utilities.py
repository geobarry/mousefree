from talon import Context, Module, canvas, cron, ctrl, cron, screen, ui, actions
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


ctx = Context()