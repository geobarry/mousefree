from talon import Module, ui, Context, clip, ctrl, cron, actions, canvas, screen, settings
from talon.windows import ax as ax, ui as winui
from talon.types import Point2d as Point2d
from talon.skia import  Paint
import inspect
import math
import re
from io import StringIO
from contextlib import redirect_stdout
import io
from copy import deepcopy

# list for tracking a set of clickable points
marked_elements = []

class mouse_mover:
    """Moves mouse using cron intervals until destination is reached"""
    def __init__(self, dest: Point2d, ms = None, callback = None):        
        self.callback = callback
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
        self.num_intervals = max(1,math.ceil(totT / 30))
        self.interval_x = dx / self.num_intervals
        self.interval_y = dy / self.num_intervals
        self.job = cron.interval('30ms', self.move_next)
        self.completed = 0
    def get_move_time(self,d):
        """Calculates the total time to move the mouse based on distance in pixels"""
        # Keys: move distance (pixels)
        # Values: move time (ms)
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
        lowT,highT = move_times[lowD],move_times[highD]
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

mod = Module()

mod.list("handle_position","position for grabbing ui elements")    
mod.list("nav_key","keys commonly used to navigate UI elements")
mod.list("action_key","keys commonly used to invoke UI elements")
mod.list("ui_action","actions that can be performed on accessibility elements")

mod.setting(
    "ax_auto_highlight",
    type = bool,
    default = False,
    desc = "If true, each action on an element will highlight the target element."
)

ctx = Context()

def settings_change_handler(*args):
    cur_tags = [tag for tag in ctx.tags]
    if settings.get("user.ax_auto_highlight"):
        cur_tags.append("user.ax_auto_highlight")
    else:
        cur_tags.remove("user.ax_auto_highlight")
    ctx.tags = cur_tags
    
settings.register("user.ax_auto_highlight",settings_change_handler)

@mod.capture(rule="<user.any_alphanumeric_key> | phrase <user.text> | <user.text>")
def ax_target(m) -> str:
    """A target string to navigate to. Returns a regular expression as a string."""
    if hasattr(m, "any_alphanumeric_key"):
        return m.any_alphanumeric_key
    t = m.text
    # include homophones
    word_list = re.findall(r"\w+",t)
    t = ".*".join(word_list)
    for w in word_list:
        phone_list = actions.user.homophones_get(w)
        if phone_list:
            phone_list = [f"{x}.*" for x in phone_list]
            t = t.replace(w,"(" + '|'.join(phone_list) + ")")
    return t

def match(el: ax.Element, prop_list: list, conjunction: str="AND", verbose: bool = False):
    """Returns true if the element matches all of the properties in the property dictionary"""
    # prop_list is either a list of form [(property, trg_val),...]
    #     where trg_val is either a string (for case-insensitive match at start of string)
    #     or a regex expression
    # or a list of ["OR",list] or ["AND",list]
    # or just a string, in which case property will be "name"
    # Conditions in the top level list are connected with an AND conjunction
    def eval_cond(prop,trg_val):
        if verbose:
            print(f'prop: {prop}')
            print(f'trg_val: {trg_val}')
        def value_match(prop_val,trg_val):
            # if trg_val is a string, convert to a regex pa'ttern
            if verbose:
                print("inside value_match sub function")
            if type(trg_val) != re.Pattern:
#            if type(trg_val) == str:
                trg_val = str(trg_val)
                trg_val = re.compile(trg_val,re.IGNORECASE)
            if verbose:
                print(f'trg_val: {trg_val}')
                print(f'type(trg_val): {type(trg_val)}')
                print("Let's try converting this to a string")
                print(str(trg_val))
            # check if property value matches regex pattern...
            
            if type(trg_val) == re.Pattern:
                if verbose:
                    print(f'trg_val: {trg_val}')
                    print(f'prop_val: {prop_val}')
                    print(f"regex match: {re.match(trg_val,prop_val)}")
                return re.match(trg_val,prop_val) != None
        if prop in ["AND","OR"]:
            return match(el,trg_val,prop)
        elif prop == "clickable":
            clickable = True
            try:
                loc = el.clickable_point
            except:
                clickable = False
            finally:
                return trg_val == clickable
        else:
            prop_val = actions.user.el_prop_val(el, prop, as_text = True)
            if verbose:
                print(f'prop_val: {prop_val}')
                print(f"type: {type(prop_val)}")
                print(f"value_match: {value_match(prop_val, trg_val)}")
            return value_match(prop_val, trg_val)
        # if something is not properly specified, return true so that other conditions can be evaluated
        print("ERROR in function actions.user.element_match (accessibility.py)")
        print(f"No matching property found (looking for property: {prop})")
        print(prop_list)
        return True
    # handle case that property list is a simple string
    if type(prop_list) == str:
        prop_list = [("name",prop_list)]
    # handle case that property list is of the form [conjunction,list]
    if prop_list[0] in ["AND","OR","and","or","And","Or"]:
        r = match(el,prop_list[1],prop_list[0])
    # handle the case that property list is a list of (property, value) tuples
    elif conjunction.upper() == "AND":
        r =  all([eval_cond(prop,val) for prop,val in prop_list])
    elif conjunction.upper() == "OR":
        r = any([eval_cond(prop,val) for prop,val in prop_list])
    # next line as for debugging
    if verbose:
        print(f"{r} | element: {el.name[:25]} | rule: {prop_list}")
    return r
def breadth_first_tree(el: ax.Element, max_level: int = 7):
    # do a breadth first search keeping track of levels, ids and parents
    # returns list of (level,cur_id,parent_id,el)
    cur_level = 0
    el_id = -1
    parent_id = -1
    Q = []
    r = []
    Q.append((cur_level,parent_id,el))    
    while len(Q) > 0:        
        cur_level,parent_id,el = Q.pop(0)
        if cur_level <= max_level:
            el_id += 1
            r.append((cur_level,el_id,parent_id,el))
            try:
                for child in el.children:
                    Q.append((cur_level+1,el_id,child))        
            except:
                pass
    return r
def depth_first_tree(el: ax.Element, max_level: int = 7):
    # do a breadth first search keeping track of levels, ids and parents
    # returns list of (level,cur_id,parent_id,el)
    el_id = 0
    r = [(0,el_id,-1,el)]
    def get_children(el, el_id, level, max_level):
        r = []
        if level < max_level:
            parent_id = el_id
            for el in el.children:
                el_id += 1
                r.append((level + 1,el_id,parent_id,el))
                r = r + get_children(el,el_id,level + 1, max_level)
        return r
    r = r + get_children(el,el_id,0,max_level)
    return r
            
def get_every_child(el: ax.Element, cur_level: int = 0, max_level: int = 7):
    # possibly keeping elements in memory is very expensive,
    # might be better to find some way to do what you want with element properties
    if cur_level <= max_level:
        if el:
            yield el
            for child in el.children:
                yield from get_every_child(child,cur_level + 1,max_level)
def identity(el: ax.Element):
    r = []
    prop = ["name","class_name","automation_id"]
    for p in prop:
        val = actions.user.el_prop_val(el,p)
        if val != '':
            r.append(f"{p}: {val}")
    r = ";".join(r)
    return r

mod.list("dynamic_element", desc="List of children of the active window")

@ctx.dynamic_list("user.dynamic_element")
def dynamic_element(_) -> dict[str,str]:
    root = winui.active_window().element
    elements = list(get_every_child(root))
    out = {}
    for el in elements:
        alias = str(el.name)
        if alias == "":
            alias = str(el.help_text)
        if alias != "":
            # add full name to dictionary
            out[str(el.name)] = str(el.name)
            # add single word command to dictionary
            singles = re.split('[^a-zA-Z]',str(el.name))
            out[singles[0]] = str(el.name)
            # add double word command to dictionary
            if len(singles) > 1:
                out[" ".join(singles[:2])] = str(el.name)
    return out

@mod.action_class
class Actions:
    def el_prop_val(el: ax.Element, prop_name: str, as_text: bool = False):
        """Returns the property value or None if the property value cannot be retrieved"""
        try:
            if prop_name.lower() == "name":
                return el.name
            elif prop_name.lower() == "pid":
                return el.pid
            elif prop_name.lower() == "control_type":
                return el.control_type
            elif prop_name.lower() == "localized_control_type":
                return el.localized_control_type
            elif prop_name.lower() == "accelerator_key":
                return el.accelerator_key
            elif prop_name.lower() == "access_key":
                return el.access_key
            elif prop_name.lower() == "has_keyboard_focus":
                return el.has_keyboard_focus
            elif prop_name.lower() == "is_keyboard_focusable":
                return el.is_keyboard_focusable
            elif prop_name == "is_enabled":
                return el.is_enabled
            elif prop_name.lower() == "class_name":
                return el.class_name
            elif prop_name.lower() == "automation_id":
                return el.automation_id
            elif prop_name.lower() == "printout":
                s = StringIO()               
                with redirect_stdout(s):
                    print(el)
                x = s.getvalue().strip().replace("<","").replace(">","") 
                return x                
            elif prop_name.lower() == "help_text":
                return el.help_text
            elif prop_name.lower() == "culture":
                return el.culture
            elif prop_name.lower() == "is_control_element":
                return el.is_control_element
            elif prop_name.lower() == "is_content_element":
                return el.is_content_element
            elif prop_name.lower() == "is_password":
                return el.is_password
            elif prop_name.lower() == "window_handle":
                return el.window_handle
            elif prop_name.lower() == "item_type":
                return el.item_type
            elif prop_name.lower() == "is_offscreen":
                return el.is_offscreen
            elif prop_name.lower() == "clickable_.":
                if as_text:
                    loc = el.clickable_point
                    return f"x: {loc.x}   y: {loc.y}"
                else:
                    return el.clickable_point
            elif prop_name.lower() == "children":
                if as_text:
                    return str(len(el.children))
                else:
                    return el.children
            elif prop_name.lower() == "item_status":
                return el.item_status
            elif prop_name.lower() == "patterns":
                return el.patterns
            elif prop_name.lower() == "described_by":
                return el.is_described_by
            elif prop_name.lower() == "flows_to":
                return el.flows_to
            elif prop_name.lower() == "provider_description":
                return el.provider_description
            elif prop_name.lower() == "children":
                return el.children
            elif prop_name.lower() == "rect":
                return el.rect
            elif prop_name.lower() == "rect.x":
                return el.rect.x
            elif prop_name.lower() == "rect.y":
                return el.rect.y
            elif prop_name.lower() == "rect.width":
                return el.rect.width
            elif prop_name.lower() == "rect.height":
                return el.rect.height
            elif prop_name.lower() == "value":
                return el.value_pattern.value
            elif prop_name.lower() == "value.is_read_only":
                return el.value_pattern.is_read_only
            elif prop_name.lower() == "legacy.value":
                return el.legacyiaccessible_pattern.value
            elif prop_name.lower() == "legacy.selection":
                return el.legacyiaccessible_pattern.selection
            elif prop_name.lower() == "text":
                if "Text" in el.patterns:
                    text_range = el.text_pattern.selection[0]
                    return text_range.text
                else:
                    if as_text:
                        return ''
                    else:
                        return None
                    
        except:
            if as_text:
                return ''
            else:
                return  None
    def element_location(el: ax.Element):
        """Returns a point that can be clicked on, or else None"""
        try: # try clickable point property
            return el.clickable_point
        except:
            try: # try rectangle
                rect = el.rect
                return Point2d(rect.x + int(rect.width/2),rect.y + int(rect.height/2))
            except:
                print("accessibility: element_location: NO LOCATION FOUND :(")
                return None
    def element_match(el: ax.Element, prop_list: list, conjunction: str="AND", verbose: bool = False):
        """Returns true if the element matches all of the properties in the property dictionary"""
        return match(el,prop_list,conjunction,verbose)
    def element_exists(prop_list: list,max_level: int = 7):
        """Returns true if an element where the given properties exists"""
        root = winui.active_window().element
        elements = list(get_every_child(root,max_level = max_level))
        for el in elements:
            if actions.user.element_match(el,prop_list):            
                return True
        return False
    def element_list():
        """returns_a_list_of_all_elements"""
        root = winui.active_window().element
        return list(get_every_child(root))
    def matching_element(prop_list: list, item_num: int = 0, max_level: int = 12,root: ax.Element = None):
        """returns the zero based nth item matching the property list, or None"""
        if root == None:
            root = winui.active_window().element
        matches = actions.user.matching_elements(prop_list,max_level = max_level,root = root)
        if len(matches) > item_num:
            return matches[item_num]
        else:
            return None
    def matching_elements(prop_list: list, max_level: int = 12, root: ax.Element = None):
        """Returns a list of all UI elements under the root that match the property list"""
        r = []
        # get list of elements
        if root == None:
            root = winui.active_window().element
        elements = list(get_every_child(root,max_level = max_level))
        # search for match
        for el in elements:
            # print(el.class_name)
            try:
                if actions.user.element_match(el,prop_list):
                    r.append(el)
            except:
                pass
        return r  
    def count_matching_children(el: ax.Element,prop_list: list):
        """Returns the number of children matching the property list conditions"""
        n = 0
        for child in el.children:
            if actions.user.element_match(child,prop_list):
                n += 1
        return n
    def matching_child(el: ax.Element,prop_list: list):
        """Returns the child of the input element that matches the property list"""
        for child in el.children:
            if actions.user.element_match(child,prop_list):
                return child
        return None
    def matching_descendants(el: ax.Element, prop_list: list, generation: int):
        """Returns the descendants of the input element """
        r = []
        def get_descendants(el: ax.Element, prop_list, cur_gen: int, trg_gen: int, r):
            if cur_gen == trg_gen:
                return [child for child in el.children if actions.user.element_match(child,prop_list)]
            else:
                for child in el.children:
                    r += get_descendants(child, prop_list,cur_gen + 1,trg_gen,r)
                return r
        r = get_descendants(el, prop_list,1,generation,r)
        return r
    def matching_descendant(el: ax.Element, prop_list: list, generation: int, extra_gen: int = 0):
        """Returns the descendant of the input element that matches the property list"""
        # def get_descendant(el: ax.Element, prop_list: list, cur_gen: int, trg_gen: int):
            # if cur_gen == trg_gen:
                # for child in el.children:
                    # if actions.user.element_match(child,prop_list):
                        # return child
                # return None
            # else:
                # for child in el.children:
                    # el = get_descendant(child,prop_list,cur_gen + 1,trg_gen)
                    # if el:
                        # return el
                # return None
        # el = get_descendant(el,prop_list,1,generation)
        # return el
        cur_level = 0
        el_id = -1
        parent_id = -1
        Q = []
        # r = []
        Q.append((cur_level,parent_id,el))    
        while len(Q) > 0:        
            cur_level,parent_id,el = Q.pop(0)
            if cur_level <= generation + extra_gen:
                el_id += 1
#                r.append((cur_level,el_id,parent_id,el))
                try:
                    for child in el.children:
                        Q.append((cur_level+1,el_id,child))        
                        if cur_level+1  >= generation:
                            if actions.user.element_match(child,prop_list):
                                return child
                except:
                    pass
#        return r

    def find_el_by_prop_seq(prop_seq: list, root: ax.Element = None, verbose: bool = False):
        """Finds element by working down from root"""
        if root == None:
            root = winui.active_window().element
        el = root
        for prop_list in prop_seq:
            if verbose:
                n = actions.user.count_matching_children(el,prop_list)
                print(f"{prop_list}: {n} matching children")
            el = actions.user.matching_child(el,prop_list)            
            if el == None:
                break
        return el
    def act_on_element(el: ax.Element, action: str, delay_after_ms: int=0):
        """Perform action on element. Get actions from {user.ui_action}"""
        if action == "click" or action == "right-click":
            loc = actions.user.element_location(el)
            if loc != None:            
                mouse_obj = mouse_mover(loc, ms = delay_after_ms)
            else:
                print(f"Error in accessibility.py function act_on_element: Element has no location.")
        elif action == "hover":
            loc = actions.user.element_location(el)
            if loc != None:    
                mouse_obj = mouse_mover(loc, ms = delay_after_ms)
            else:
                print(f"Error in accessibility.py function act_on_element: Element has no location.")
        elif action == "highlight":
            print("HIGHLIGHTING...")
            actions.user.highlight_element(el)
        elif action == "label":
            actions.user.highlight_element(el,el.name)
        elif action == "select":
            if "SelectionItem" in el.patterns:
                el.selectionitem_pattern.select()
            elif "LegacyIAccessible" in el.patterns:
                el.legacyiaccessible_pattern.select(1)
            else:
                print(f"Error in accessibility.py function act_on_element: Element cannot be selected.")
        elif action == "invoke":
            if "Invoke" in el.patterns:
                el.invoke_pattern.invoke()
            else:
                print(f"Error in accessibility.py function act_on_element: Element cannot be invoked.")
        elif action == "toggle":
            if "Toggle" in el.patterns:
                el.toggle_pattern.toggle()
        actions.sleep(f"{delay_after_ms + 50}ms")
        if action == "click" or action == "right-click":
            if action == "click":
                ctrl.mouse_click()
            elif action == "right-click":
                ctrl.mouse_click(1)
    def act_on_focused_element(action: str, delay_after_ms: int = 0):
        """Performs action on currently focused element"""
        el = winui.focused_element()
        actions.user.act_on_element(el,action,delay_after_ms)
    def act_on_mouse_element(action: str, delay_after_ms: int = 0):
        """Returns the UI element at the current mouse position"""
        pos = ctrl.mouse_pos()
        el = ui.element_at(pos[0],pos[1])
        actions.user.act_on_element(el,action,delay_after_ms)
    def act_on_named_element(name: str, action: str, delay_after_ms: int = 0):
        """Performs action on first element beginning with given name"""
        prop_list = [("name",name)]
        elements = actions.user.matching_elements(prop_list)
        if len(elements) > 0:
            actions.user.act_on_element(elements[0],action,delay_after_ms)
    def act_on_matching_element(prop_list: list, action: str, item_num: int = 0, max_level: int = 99):
        """Perform action on first UI element that matches the property list"""
        el = actions.user.matching_element(prop_list,item_num = item_num,max_level = max_level)
        if el != None:
            actions.user.act_on_element(el,action)
    def key_to_matching_element(key: str, 
                                prop_list: list, 
                                ordinal: int=1, 
                                limit: int=20, 
                                escape_key: str=None, 
                                delay: float = 0.09, 
                                verbose: bool = False):
        """press given key until the first matching element is reached"""
        # TO-DO:
        # Modifies so this goes one element at a time and is integrated with slow repeater,
        # so cycle can be stopped with "Stop" or "Stop It"
        # ---
        # if the previous action has not completed an error can occur
        # (e.g. PowerPoint accessing format panel from context menu)
        # to avoid this, wrap in try except clause 
        print("FUNCTION: key_to_matching_element")
        # remove previous highlights
        if settings.get("user.ax_auto_highlight"):
            actions.user.clear_highlights()
        # Function to get next element, sometimes need to be persistent
        def focused_element():
            n = 0
            while n < 3:
                try:
                    return winui.focused_element()
                except:
                    n += 1
                    actions.sleep(delay)
            return None
        # initialize
        el = focused_element()
        print(f'el: {el}')
        last_el = el
        i = 1
        matches = 0
        if el:
            try:
                first_el_id = identity(el)
                print(f"1st element: {first_el_id}")
                while True:
                    actions.key(key)
                    if delay > 0:
                        actions.sleep(delay)
                    el = focused_element()
                    if el:
                        if actions.user.element_match(el,prop_list,verbose = False):
                            matches += 1
                        if verbose:
                            print(f"ELEMENT: {el.name}")      
                        if (last_el == el) and (escape_key != None):
                            actions.key(escape_key)
                        last_el = el
                        i += 1
                        if matches == ordinal:
                            break
                        if i == limit:
                            break
                        if identity(el) == first_el_id:
                            break
                    else:
                        break
            except Exception as error:
                print(error)
            if actions.user.element_match(el,prop_list):
                return el
            else:
                return None
    def key_to_elem_by_val(key: str, val: str, prop: str="name", ordinal: int=1, limit: int=99, escape_key: str=None, delay: float = 0.09):
        """press key until element with exact value for one property is reached"""
        prop_list = [(prop,val)]
        actions.user.key_to_matching_element(key,prop_list,ordinal = ordinal,limit = limit,escape_key = escape_key,delay = delay)
    def key_to_name_and_class(key: str, name: str, class_name: str = ".*",limit: int=99,delay: float = 0.03):
        """Press key until element with matching name and classes reached"""
        prop_list = [("name",name),("class_name",class_name)]
        actions.user.key_to_matching_element(key,prop_list,limit = limit,delay = delay)
    def mark_focused_element():
        """records the clickable point of the currently focused item"""
        global marked_elements
        el = winui.focused_element()
        marked_elements.append(el)
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
    def invoke_by_value(val: str, prop: str = "name", max_level: int = 99):
        """Searches for first element with given property value and invokes it."""
        prop_list = [prop,val]
        el = actions.user.matching_element(prop_list,max_level = max_level)
        actions.user.act_on_element(el,"invoke")
    def move_mouse_to_handle(pos: str="center", x_offset: int=0, y_offset: int=0):
        """moves mouse to left,right or center and top,bottom or center of currently focused element"""
        el = winui.focused_element()
        try:
            rect = el.rect
            if "left" in pos:
                x = rect.x
            elif "right" in pos:
                x = rect.x + rect.width
            else:
                x = rect.x + int(rect.width/2)
            if "upper" in pos or "top" in pos:
                y = rect.y
            elif "lower" in pos or "bottom" in pos:
                y = rect.y + rect.height
            else:
                y = rect.y + int(rect.height/2)
            x += x_offset
            y += y_offset
            ctrl.mouse_move(x,y)
        except:
            pass
    def element_information(el: ax.Element, headers: str = False, as_dict: bool = False, verbose: str = False):
        """Returns information separated by tabs that can be pasted into a spreadsheet"""
        msg = ""
        prop_list = ["name","class_name",
                        "help_text","automation_id",
                        "printout",
                        "children","patterns",
                        "is_offscreen",
                        "clickable_point",
                        "rect.x","rect.y",
                        "rect.width","rect.height"
                    ]
        other_prop = [
                    "window_handle","pid","access_key","has_keyboard_focus",
                    "is_keyboard_focusable","is_enabled",
                    "children","is_control_element","is_content_element",
                    "item_type","item_status","described_by",
                    "flows_to","provider_description",
                    "value.is_read_only",
                    "legacy.value","legacy.selection",
                    "value","text"
                ]
        if verbose:
            prop_list += other_prop
        # Construct headers
        if headers:
            return "\t".join(prop_list)
        elif as_dict:
            return  {prop:str(actions.user.el_prop_val(el,prop,as_text = True)) for prop in prop_list}
        else:
            # Get property values
            return  "\t".join([str(actions.user.el_prop_val(el,prop,as_text = True)) for prop in prop_list])
    def copy_elements_accessible_by_key(key: str, limit: int=20, delay: int = 0.03, verbose: bool = True):
        """Gets information on elements accessible by pressing input key"""        
        i = 1
        el = winui.focused_element()
        orig_el = el
        msg = actions.user.element_information(el, verbose = verbose)
        messages = []
        while True:
            print(f"*******\nELEMENT NUMBER: {i}\n*******")
            messages.append(msg)
            actions.sleep(delay)
            actions.key(key)
            el = winui.focused_element()
            msg = actions.user.element_information(el, verbose = verbose)    
            if i > limit or el.__eq__(orig_el):
                break
            i += 1
        clip.set_text("\n".join(messages))
    def copy_mouse_elements_to_clipboard():
        """Copies elements with rectangle containing current mouse position"""
        pos = ctrl.mouse_pos()
        # get element designated by windows accessibility
        el = ui.element_at(pos[0],pos[1])
        root = winui.active_window().element
        elements = [el] + list(get_every_child(root,max_level = 17))
        n = 0
        msg = actions.user.element_information(elements[0],headers = True)
        for el in elements:
            r = actions.user.el_prop_val(el,"rect")
            if r:
                if (r.x < pos[0] < r.x + r.width) and (r.y < pos[1] < r.y + r.height):
                    msg += "\n" + actions.user.element_information(el)
                    n += 1                
        msg += f"\n\n {n} elements found"
        clip.set_text(msg)
    def copy_focused_element_to_clipboard():
        """Copies information about currently focused element to the clipboard"""
        el = winui.focused_element()
        msg = actions.user.element_information(el, headers = True, verbose = True)
        msg += "\n" + actions.user.element_information(el, verbose = True)
        clip.set_text(msg)
    def copy_focused_element_descendants(levels: int = 12):
        """Copies information about currently focused element and children to the clipboard"""
        el = winui.focused_element()
        actions.user.copy_elements_to_clipboard(levels,el)
    def copy_element_ancestors(el: ax.Element, verbose: bool = False):
        """Copies information on element ancestors to clipboard"""
        i = 0
        el_list = [el]
        hdr = actions.user.element_information(el,verbose = False,headers = True)
        while True:
            i += 1
            try:
                el = el.parent
                el_list.append(el)
            except Exception as error:
                print(f'error: {error}')
                break
        msg = "\n".join([actions.user.element_information(x,verbose = False) for x in el_list])
        msg = hdr + "\n" + msg
        clip.set_text(msg)
    def copy_mouse_element_ancestors(verbose: bool = True):
        """Retrieves list of ancestors of current mouse element"""
        pos = ctrl.mouse_pos()        
        actions.user.copy_element_ancestors(ui.element_at(pos[0],pos[1]),verbose)
    def copy_focused_element_ancestors(verbose: bool = True):
        """Retrieves list of ancestors of currently focused element"""
        actions.user.copy_element_ancestors(winui.focused_element(),verbose)
        
    def copy_elements_to_clipboard(max_level: int = 7, breadth_first: bool = True, root: ax.Element = None):
        """Attempts to retrieve all properties from all elements"""
        print("INSIDE FUNCTION COPY ELEMENTS TO CLIPBOARD")
        if root == None:
            root = winui.active_window().element
        # mark elements with special status
        # focused element
        focused_el = winui.focused_element()
        prop_list = ["name","class_name","automation_id","printout"]
        focus_fingerprint = [actions.user.el_prop_val(focused_el,prop) for prop in prop_list]
        # mouse elements
        mouse_fingerprints = []
        pos = ctrl.mouse_pos()
        def el_data(level,cur_id,parent_id,el):
            status = []
            # check to see if this is the focused element
            el_fingerprint = []
            for prop in prop_list:
                try:
                    el_fingerprint.append(actions.user.el_prop_val(el,prop) for prop in prop_list)
                except:
                    print(f"EXCEPTION retrieving property {prop}")
            if el_fingerprint == focus_fingerprint:
                status.append("focused")
            # check to see if mouse is on element
            r = actions.user.el_prop_val(el,"rect")
            if r:
                if (r.x < pos[0] < r.x + r.width) and (r.y < pos[1] < r.y + r.height):
                    status.append("mouse")
            status = "|".join(status)
            r = f"{status}\t{level}\t{cur_id}\t{parent_id}\t" + re.sub(r"\r?\n","<<new line>>",actions.user.element_information(el)) 
            return r
        if breadth_first:
            el_info = breadth_first_tree(root,max_level = max_level)
        else:
            el_info = depth_first_tree(root,max_level = max_level)
        print(f"{len(el_info)} elements in tree...")
        msg = "status\tlevel\tid\tparent_id\t" + actions.user.element_information(root,headers = True)
        messages = [el_data(level,cur_id,parent_id,el) for level,cur_id,parent_id,el in el_info]
        clip.set_text(msg + "\n" + "\n".join(messages))
    def copy_ribbon_elements_as_talon_list():
        """Copies to clipboard list of ribbon elements with accessible keyboard shortcut; 
            assumes menu heading is selected with rectangle around it, and ribbon is expanded"""
        i = 1
        el = winui.focused_element()
        heading_access_key = clean(actions.user.el_prop_val(el,"access_key")) 
        # convention: use menu heading name as prefix for every command
        prefix = el.name
        # press tab to get to the first command; note grayed out commands will not be reached
        actions.key("tab")
        el = winui.focused_element()
        first_name = f"{prefix} {clean(el.name)}"
        first_access_key = clean(actions.user.el_prop_val(el,"access_key"))
        r = []
        while True:
            i += 1
            if i > 60:
                print("Stopping because exceeded count threshold")
                break
            actions.key("tab")
            actions.sleep(0.05)
            try:
                el = winui.focused_element()
                name = f"{prefix} {clean(el.name)}"
                access_key = clean(actions.user.el_prop_val(el,"access_key"))
                print(f'{i} access_key: {access_key}')
                print(f'heading_access_key: {heading_access_key}')
                # hello check that we're not back at the first element
                if name == first_name and access_key == first_access_key:
                    break
                # check that access key begins with (but is not the same as) first access key
                elif access_key.startswith(heading_access_key) and not access_key == heading_access_key:
                    r.append((name,access_key))
                else:
                    # if access key is the same as first element but name is not, we have a phantom element
                    pass
            except:
                pass
        print("Got to the end...")
        msg = "\n".join([f"{key}:{val}" for key,val in r])
        print(f'msg: {msg}')
        clip.set_text(msg)
    def copy_ribbon_headings_as_talon_list():
        """Copies information on ribbon headings to the clipboard"""
        actions.key("esc:5 alt")
        actions.sleep(0.2)
        i = 1
        el = winui.focused_element()
        first_name = clean(el.name)
        first_access_key = actions.user.el_prop_val(el,"access_key")
        r = {}
        r[first_name] = clean(first_access_key)
        while True:
            i += 1
            if i > 100:
                break
            actions.key("right")
            el = winui.focused_element()
            name = clean(el.name)
            if name == first_name:
                break
            else:
                access_key = actions.user.el_prop_val(el,"access_key")
                r[name] = clean(access_key)
        clip.set_text("\n".join([f"{key}:{val}" for key,val in r.items()]))

def clean(t):
    t = t.lower()
    regex = re.compile('[^a-zA-Z0-9]')
    #First parameter is the replacement, second parameter is your input string
    t = re.sub('\.\.\.', ' dialog', t)
    t = regex.sub(' ', t)
    t = re.sub(' +', ' ', t)
    return t