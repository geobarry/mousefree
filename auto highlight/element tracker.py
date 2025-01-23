from talon import Module, Context, clip, ctrl, cron, actions, canvas, screen, settings
from talon.windows import ax as ax, ui as winui
from talon.types import Point2d as Point2d
from talon.skia import  Paint
from typing import Callable
import time

mod = Module()

mod.tag("Text_pattern","Focused element has windows accessibility text pattern")

class element_tracker:
    def __init__(self):        
        self.canvas = canvas.Canvas.from_screen(winui.main_screen())
        self.canvas.register('draw', self.draw_canvas) 
        self.canvas.freeze() # uncomment this line for debugging
        self.rectangles = []
        self.labels = []
        self.auto_highlight = False
        self.auto_label = False
        self.active_tags = set()
        self.traversal_function = None
        self.focused_element = None
        self.focused_rect = None
        self.focused_label = ""
        self.traversal_count = 0
    def add_element(self,rect,label = ''):
        self.rectangles.append(rect)
        self.labels.append(label)
        self.canvas.move(0,0) # this forces canvas redraw
    def remove_element(self,rect):
        try:
            idx = self.rectangles.index(rect)
            del self.rectangles[idx]
            del self.labels[idx]
            self.canvas.move(0,0) # this forces canvas redraw
        except:
            pass
        print(f"There are now {len(self.rectangles)} elements in highlight list")
    def clear_elements(self):
        self.rectangles = []
        self.labels = []
        self.canvas.move(0,0) # this forces canvas redraw
    def draw_canvas(self, canvas):
        paint = canvas.paint
        paint.color = 'f3f'
        paint.style = paint.Style.STROKE
        paint.stroke_width = 7
        def highlight_element(rect,lbl,paint):
            if self.auto_highlight:
                if rect != None:
                    canvas.draw_round_rect(rect,25,25,paint)
            if self.auto_label:
                if lbl != '':
                    if rect != None:
                        paint.stroke_width = 2
                        if len(lbl) > 50:
                            lbl = lbl[:50]
                        # determine label placement
                        # assume text dimensions
                        lbl_wd = 600
                        lbl_ht = 30
                        top_margin = rect.y
                        btm_margin = canvas.height - rect.y - rect.height
                        if top_margin > btm_margin:
                            y = max(rect.y - lbl_ht, 0)
                        else:
                            y = min(rect.y + rect.height + 60, canvas.height - lbl_ht)
                        x = min(rect.x,canvas.width - lbl_wd)
                        actions.user.text_aliased(lbl,x,y,46,canvas)        
        if len(self.rectangles) > 0:
            for idx in range(len(self.rectangles)):
                rect = self.rectangles[idx]
                lbl = self.labels[idx]
                highlight_element(rect,lbl,paint)
        if self.auto_highlight or self.auto_label:
            # references to self.focused_element inside this function
            # will interfere with talon command canvas somehow, 
            # so we structure this so that we don't need to refer to 
            # self.focused_element here
            highlight_element(self.focused_rect,self.focused_label,paint)
    def disable(self):
        self.canvas.close()
        self.canvas = None
    def check_focused_element(self):
        if self.auto_highlight or self.auto_label:
            self.update_highlight()
    def update_highlight(self):
        rectangle_found = False
        if self.auto_highlight or self.auto_label:
            el = self.focused_element
            if el:
                try:
                    rect = actions.user.el_prop_val(el,"rect")
                    if rect:
                        rectangle_found = True
                        if el.rect != self.focused_rect:
                            self.focused_rect = el.rect
                            if self.auto_label:
                                self.focused_label = el.name
                            self.canvas.move(0,0) # this forces canvas redraw
                        if not self.auto_label:
                            if self.focused_label != "":
                                self.focused_label = ""
                                self.canvas.move(0,0) # this forces canvas redraw
                except Exception as error:
                    pass
            else:
                print("FUNCTION check_for_updates: unable to get focused element")
        if not rectangle_found:
            self.focused_rect = None
            self.focused_label = ""
            self.canvas.move(0,0)

    def handle_focus_change(self,el):
        if el:
            self.focused_element = el
        # handle element traversal
        if self.traversal_function != None:
            self.traversal_function()
        # handle auto highlight
        self.update_highlight()

el_highlights = element_tracker()
def handle_focus_change(el):
    rect = actions.user.el_prop_val(el,"rect")
    el_highlights.handle_focus_change(el)
winui.register("element_focus",handle_focus_change)


@mod.action_class
class Actions:
    def auto_highlight(on: bool = True):
        """automatically highlight focused element"""
        el_highlights.auto_highlight = on
        el_highlights.update_highlight()
    def auto_label(on: bool = True):
        """automatically highlight and label focused element"""
        el_highlights.auto_label = on
        el_highlights.update_highlight()
    def highlight_element(el: ax.Element, lbl: str = ""):
        """Highlight specified element, with optional label"""
        rect = el.rect
        if len(lbl) > 50:
            lbl = lbl[:50]
        el_highlights.add_element(rect,lbl)
    def remove_highlight(el: ax.Element):
        """Remove element from highlights"""
        try:
            el_highlights.remove_element(el.rect)
        except:
            print("Unable to remove highlight: Element rectangle does not match any current highlight")
    def clear_highlights():
        """Removes all ui elements from the highlight list"""
        el_highlights.clear_elements()
    def key_highlight(keys: str, delay_before_highlight: float = 0.05, delay_after_highlight: float = 0):
        """Presses a key sequence and then highlights the focused element. If not forced, only highlights if in auto highlight mode."""
        actions.key(keys)
        if delay_before_highlight > 0:
            actions.sleep(delay_before_highlight)
        actions.user.clear_highlights()
        actions.user.highlight_element(winui.focused_element())
        if delay_after_highlight > 0:
            actions.sleep(delay_after_highlight)
    def focused_element():
        """returns currently focused element, as recorded by element_tracker"""
        return el_highlights.focused_element
    def initialize_traversal(traversal_function: Callable, max_iter: int = 30):
        """initialize a traversal of windows accessibility elements; 
        traversal_function should guarantee that actions.user.terminate_traversal 
        will eventually be called or else use max_iter"""     
        
        el_highlights.traversal_count = 0
        def do_traversal():
            if el_highlights.traversal_count < max_iter:
                el_highlights.traversal_count += 1
                traversal_function()
            else:
                actions.user.terminate_traversal()
        el_highlights.traversal_function = do_traversal
        el_highlights.traversal_function()
    def terminate_traversal():
        """terminate the continued traversal using a key"""
        el_highlights.traversal_count = 0
        el_highlights.traversal_function = None