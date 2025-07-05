from talon import Module, Context, clip, ctrl, cron, actions, canvas, screen, settings, ui
from talon.windows import ax as ax, ui as winui
from talon.types import Point2d as Point2d, rect as rect
from talon.skia import  Paint
from typing import Callable
import time

mod = Module()

mod.tag("Text_pattern","Focused element has windows accessibility text pattern")

# list for tracking a set of clickable points
marked_elements = []

class element_tracker:
    def __init__(self):        
        self.screen = winui.main_screen()
        self.canvas = None
        self.update_screen(self.screen)
        self.rectangles = []
        self.labels = []
        self.auto_highlight = False
        self.auto_label = False
        self.active_tags = set()
        self.traversal_function = None
        self.retrieving = False
        print("initializing element tracker...")
        self.focused_element = None
        self.focused_rect = None
        self.focused_label = ""
        self.traversal_count = 0
#        self.job = cron.interval("5000ms", self.update_highlight)
    def update_screen(self, s):
        # updates canvas to input screen 
        if s:
            self.screen = s
            if self.canvas:
                self.canvas.close()
            self.canvas = canvas.Canvas.from_screen(s)
            self.canvas.register('draw', self.draw_canvas) 
            self.canvas.freeze() # uncomment this line for debugging
            
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
        """retrieves new focused element unless already processing"""
        if not self.retrieving:
            print("FUNCTION: check_focused_element")
            self.retrieving = True
            try:
                self.focused_element = ax.get_focused_element()
            finally:
                self.retrieving = False
        else:
            pass
            # print("FUNCTION: check_focused_element - in the middle of retrieving another element...")
    def update_highlight(self):
        # print("FUNCTION: update_highlight")
        if not self.retrieving:
            self.retrieving = True
            try:
                rectangle_found = False
                if self.auto_highlight or self.auto_label:
                    el = self.focused_element
                    if el:
                        rect = None
                        rect = actions.user.el_prop_val(el,"rect")
                        if rect:
                            rectangle_found = True
                            if rect != self.focused_rect:
                                self.focused_rect = rect
                                s = screen.containing(rect.x,rect.y)
                                if not s == self.screen:
                                    self.update_screen(s)
                                if self.auto_label:
                                    print("FUNCTION update_highlight")
                                    self.focused_label = el.name
                                    print(f"focused_label: self.focused_label")
                                self.canvas.freeze() # this forces canvas redraw
                            if not self.auto_label:
                                if self.focused_label != "":
                                    self.focused_label = ""
                                    self.canvas.freeze() # this forces canvas redraw
                    else:
                        pass
                if not rectangle_found:
                    self.focused_rect = None
                    self.focused_label = ""
                self.canvas.freeze()
            except Exception as error:
                print(f'FUNCTION update_highlight - error: {error}')
                self.check_focused_element()            
            finally:
                self.retrieving = False
        else:
            # print("FUNCTION: update_highlight - in the middle of retrieving another element...")
            pass
    def handle_focus_change(self,el):
        # print("FUNCTION handle_focus_change")
        if el:           
            self.focused_element = el
        # handle automatic element traversal
        if self.traversal_function != None:
            print("Running traversal function...")
            self.traversal_function()
        # handle auto highlight
        self.update_highlight()
el_track = element_tracker()

def handle_focus_change(el):
    # print("FUNCTION handle_focus_change")
    # print(f'windows.ui.register"element_focus" input: {el}')
    # print(f'windows.ui.focused_element: {winui.focused_element()}')
    # print(f"ax.focused_element: {ax.get_focused_element()}")
    el_track.handle_focus_change(el)
winui.register("element_focus",handle_focus_change)

    
        
    
traversal_termination_function = None

@mod.action_class
class Actions:
    def reset_tracker():
        """Resets the element tracker used for automatic highlighting and labeling"""
        el_track = element_tracker()
        el_track.retrieving = False
    def auto_highlight(on: bool = True):
        """automatically highlight focused element"""
        el_track.auto_highlight = on
        el_track.update_highlight()
    def auto_label(on: bool = True):
        """automatically highlight and label focused element"""
        el_track.auto_label = on
        el_track.update_highlight()
    def currently_highlighting():
        """Returns boolean representing current highlighting state"""
        return el_track.auto_highlight
    def highlight_element(el: ax.Element, lbl: str = ""):
        """Highlight specified element, with optional label"""
        rect = el.rect
        if len(lbl) > 50:
            lbl = lbl[:50]
        el_track.add_element(rect,lbl)
    def highlight_rectangle(rect: rect):
        """Highlights input rectangle without associated element"""
        el_track.add_element(rect,"")
    def remove_highlight(el: ax.Element):
        """Remove element from highlights"""
        try:
            el_track.remove_element(el.rect)
        except:
            print("Unable to remove highlight: Element rectangle does not match any current highlight")
    def clear_highlights():
        """Removes all ui elements from the highlight list"""
        el_track.clear_elements()
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
        """manages windows focused element retrieval;
           places request only if there is no other request in process;
           returns currently focused element"""
#        el_track.check_focused_element()
        return el_track.focused_element
    def set_winax_retrieving(state: bool = True):
        """Used this to prevent windows accessibility freezes"""
        el_track.retrieving = state
    def winax_retrieving():
        """if true, you should not request a focused element because we are probably waiting for windows to respond to a previous request"""
        return el_track.retrieving
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
        # debugging
        win_focus = winui.focused_element()
        user_focus = actions.user.focused_element()
        print("FUNCTION terminate_traversal")
        print(f'win_focus: {win_focus}')
        print(f'user_focus: {user_focus}')
    def mark_focused_element():
        """records the clickable point of the currently focused item"""
        print("FUNCTION: mark_focused_element")
        global marked_elements
        el = winui.focused_element()
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
        el = winui.focused_element()
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