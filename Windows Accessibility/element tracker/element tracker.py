from talon import Module, Context, clip, ctrl, cron, actions, canvas, screen, settings, ui, app
from talon.windows import ax as ax, ui as winui
from talon.types import Point2d as Point2d, rect as rect
from talon.skia import  Paint
from typing import Callable
import time


mod = Module()

#mod.tag("Text_pattern","Focused element has wfindows accessibility text pattern")

# list for tracking a set of clickable points
marked_elements = []

class element_tracker:
    def __init__(self):        
        self.canvas = None
        rect = actions.user.get_screen_bounds()
        self.canvas = canvas.Canvas.from_rect(rect)
        self.canvas.register('draw',self.draw_canvas)
        self.canvas.freeze()
        self.rectangles = []
        self.labels = []
        self.auto_highlight = False
        self.auto_label = False
        self.traversal_function = None
        print("initializing element tracker...")
        self.focused_element = None
        self.focused_rect = None
        self.focused_label = ""
        self.traversal_count = 0
        self.interval = 300
        self.job = cron.interval(f"{self.interval}ms", self.update_highlight)
        self.accessibility_check_paused = False
        
    def add_element(self,rect,label = ''):
        self.rectangles.append(rect)
        self.labels.append(label)
        self.canvas.freeze() # this forces canvas redraw
    def remove_element(self,rect):
        try:
            idx = self.rectangles.index(rect)
            del self.rectangles[idx]
            del self.labels[idx]
            self.canvas.freeze() # this forces canvas redraw
        except:
            pass
        print(f"There are now {len(self.rectangles)} elements in highlight list")
    def clear_elements(self):
        self.rectangles = []
        self.labels = []
        self.canvas.freeze() # this forces canvas redraw
    def draw_canvas(self, canvas):
        # return 
        try:
            # print("DRAW_CANVAS")
            paint = canvas.paint
            paint.color = 'f3f'
            paint.style = paint.Style.STROKE
            paint.stroke_width = 5
            def highlight_element(rect,lbl,paint):
                if rect != None:
                    canvas.draw_round_rect(rect,11,11,paint)
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
                # print(f"rectangles: {len(self.rectangles)}")
                for idx in range(len(self.rectangles)):
                    rect = self.rectangles[idx]
                    # print(f'drawing rect: {rect}')
                    canvas_rect = canvas.rect
                    # print(f'canvas_rect: {canvas_rect}')
                    # print(f'highlighted     rect: {rect}')
                    lbl = self.labels[idx]
                    highlight_element(rect,lbl,paint)
            if self.auto_highlight or self.auto_label:
                highlight_element(self.focused_rect,self.focused_label,paint)
        except Exception as error:
            print(f'DRAW_CANVAS error: {error}')
    def disable(self):
        self.canvas.close()
        self.canvas = None
    def update_highlight(self):
        """Updates the focused element using windows accessibility"""
        if not self.accessibility_check_paused:
            try:
                rectangle_found = False
                if self.auto_highlight or self.auto_label:
                    el = actions.user.safe_focused_element()
                    if el:
                        rect = None
                        rect = actions.user.el_prop_val(el,"rect")
                        if rect:
                            rectangle_found = True
                            if rect != self.focused_rect:
                                self.focused_rect = rect
                                if self.auto_label:
                                    self.focused_label = el.name
                            if not self.auto_label:
                                if self.focused_label != "":
                                    self.focused_label = ""
                        else:
                            pass
                    else:
                        pass
                if not rectangle_found:
                    self.focused_rect = None
                    self.focused_label = ""
                self.canvas.freeze()
            except Exception as error:
                print(f'FUNCTION update_highlight - error: {error}')
    def handle_focus_change(self,el):
        if el:           
            self.focused_element = el
        # handle automatic element traversal
        if self.traversal_function != None:
            print("Running traversal function...")
            self.traversal_function()
        # handle auto highlight
        print("HANDLE_FOCUS_CHANGE")
        self.update_highlight()


def handle_focus_change(el):
    el_track.handle_focus_change(el)

black_list = ["Microsoft Excel"]
prior_state = (True,False)

def check_app(app):
    print("test")
    if el_track:
        app = winui.active_app()
        name = app.name
        print(f'name: {name}')
        global prior_state
        if name in black_list:
            print("app on blacklist, pausing highlighting...")
            prior_state = [el_track.auto_highlight,el_track.auto_label]
            el_track.auto_highlight = False
            el_track.auto_label = False
        else:
            print("app not on blacklist, resuming highlighting...")
            el_track.auto_highlight = prior_state[0]
            el_track.auto_label = prior_state[1]

#winui.register("element_focus",handle_focus_change)
winui.register("element_focus",check_app)

el_track = None
def on_ready():
    global el_track
    el_track = element_tracker()
    actions.user.auto_highlight(True)
app.register("ready",on_ready)
traversal_termination_function = None

@mod.action_class

class Actions:
    def auto_highlight(on: bool = True):
        """automatically highlight focused element"""
        el_track.auto_highlight = on
        el_track.update_highlight()
    def auto_label(on: bool = True):
        """automatically highlight and label focused element"""
        el_track.auto_label = on
        el_track.update_highlight()
    def el_tracker_pause_updating():
        """pauses checking current focused element, but keeps highlighting"""
        if el_track:
            el_track.accessibility_check_paused = True
    def el_tracker_resume_updating():
        """resumes checking current focused element, but keeps highlighting"""
        if el_track:
            el_track.accessibility_check_paused = False
    def currently_highlighting():
        """Returns boolean representing current highlighting state"""
        return el_track.auto_highlight
    def currently_labelling():
        """Returns bulling representing current labeling state"""
        return el_track.auto_label
    def highlight_element(el: ax.Element, lbl: str = ""):
        """Highlight specified element, with optional label"""
        if el:
            print(f'HIGHLIGHT_ELEMENT el: {el}')
            rect = actions.user.el_prop_val(el,"rect")
            print(f'rect: {rect}')
            if rect:
                if len(lbl) > 50:
                    lbl = lbl[:50]
                el_track.add_element(rect,lbl)
                
                return 
        print("HIGHLIGHT_ELEMENT: unable to highlight element")
    def highlight_rectangle(rect: rect):
        """Highlights input rectangle without associated element"""
        el_track.add_element(rect,"")
    def remove_highlight(el: ax.Element):
        """Remove element from highlights"""
        if el:
            rect = actions.user.el_prop_val(el,"rect")
            if rect:
                try:
                    el_track.remove_element(el.rect)
                except:
                    print("Unable to remove highlight: Element rectangle does not match any current highlight")
    def clear_highlights():
        """Removes all ui elements from the highlight list"""
        el_track.clear_elements()

    def focused_element():
        """manages windows focused element retrieval;
           places request only if there is no other request in process;
           returns currently focused element"""
        return el_track.focused_element
    def reset_element_tracker():
        """deletes the element tracker and creates a new one. """
        global el_track
        del el_track
        el_track = element_tracker()

    def initialize_traversal(traversal_function: Callable, 
        sec_lim: float = 5,
        max_iter: int = 500, 
        delay: float = 0.015,
        finish_function: Callable = None):
        """initialize a traversal of windows accessibility elements; 
        traversal_function should guarantee that actions.user.terminate_traversal 
        will eventually be called or else use max_iter"""     
        stopper = actions.user.stopper(sec_lim)        
        global traversal_termination_function
        traversal_termination_function = finish_function
        def do_traversal(stopper):
            print("FUNCTION do_traversal")
            actions.sleep(delay)
            if stopper.over():
                del stopper
                actions.user.terminate_traversal()
                print("traversal stopped due to over time")
            elif max_iter > -1 and el_track.traversal_count > max_iter:
                del stopper
                actions.user.terminate_traversal()
                print("traversal stopped due to over count")
            else:
                el_track.traversal_count += 1
                print("...continuing traversal...")
                traversal_function()

        el_track.traversal_count = 0
        actions.mode.enable("user.slow_repeating")
        actions.mode.disable("command")
        el_track.traversal_function = lambda: do_traversal(stopper)
        el_track.traversal_function()
    def terminate_traversal():
        """terminate the continued traversal using a key"""
        actions.mode.enable("command")
        actions.mode.disable("user.slow_repeating")
            # return
        el_track.traversal_count = 0
        el_track.traversal_function = None
        

        global traversal_termination_function
        if traversal_termination_function:
            traversal_termination_function()
            traversal_termination_function = None
    def mark_focused_element():
        """records the clickable point of the currently focused item"""
        print("FUNCTION: mark_focused_element")
        global marked_elements
        el = actions.user.safe_focused_element()
        if el:
            marked_elements.append(el)
    def mouse_to_marked_element_handle(hnd_pos: str, ordinal: int = 0,ms: int = 350):
        """moves the mouse to the marked element"""
        if ordinal < len(marked_elements):
            rect = actions.user.el_prop_val(marked_elements[ordinal],"rect")
            if rect:
                actions.user.mouse_to_obj_handle(rect,hnd_pos,ms = ms)
    def select_marked():
        """selects marked elements and then empties list"""
        global marked_elements
        # clear any selection
        el = actions.user.safe_focused_element()
        try:
            pattern = el.selectionitem_pattern
            pattern.remove_from_selection()
        except Exception as error:
            print(f"Error removing from selection in accessibility.py function select_marked: {error}")        
        # select all marked elements
        for el in marked_elements:
            try:
                pattern = el.selectionitem_pattern
                pattern.add_to_selection()
            except Exception as error:
                print(f"Error adding to selection in accessibility.py function select_marked: {error}")        
        # reset list of marked elements
        marked_elements = []
    def clear_marked():
        """clears the list of marked elements"""
        global marked_elements
        marked_elements = []