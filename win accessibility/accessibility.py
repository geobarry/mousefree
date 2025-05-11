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
import time
from typing import Callable

n = 0
start_time = None

mod = Module()

mod.list("nav_key","keys commonly used to navigate UI elements")
mod.list("action_key","keys commonly used to invoke UI elements")
mod.list("ui_action","actions that can be performed on accessibility elements")


@mod.capture(rule="<user.any_alphanumeric_key> | phrase <user.text> | <user.text>")
def ax_target(m) -> str:
    """A target string to navigate to. Returns a regular expression as a string.
       Perhaps this should be merged with win_navigation_target in text selection"""
    
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

def match(el: ax.Element, 
            prop_list: list, 
            conjunction: str="AND", 
            mod_func: Callable = None, 
            verbose: bool = False):
    """Returns true if the element matches all of the properties in the property dictionary"""
    # prop_list is either a list of form [(property, trg_val),...]
    #     where trg_val is either a string ready to be compiled into a regex expression
    #     or a regex expression
    # or a list of ["OR",list] or ["AND",list]
    # or just a string, in which case property will be "name"
    # Conditions in the top level list are connected with an AND conjunction
    # Modifier function should take input parameters prop_name:str,val: str and return a replacement value
    if verbose:
        print("FUNCTION: match")
        print(f'prop_list: {prop_list}')
        print(f'conjunction: {conjunction}')
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
#               FOLLOWING MUST BE DONE BY CALLING FUNCTION
#                trg_val = str(trg_val).replace("(","\\(").replace(")","\\)")
                trg_val = re.compile(f"^{trg_val}$",re.IGNORECASE)
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
            if mod_func:
                prop_val = mod_func(prop,prop_val)
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
    # handle case that property list is an empty list
    if len(prop_list) == 0:
        return True
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

def get_every_child(el: ax.Element, 
        cur_level: int = 0, 
        max_level: int = 15, 
        max_n: int = 500, 
        max_sec: float = 2,
        stopper = None):
    # possibly keeping elements in memory is very expensive,
    # might be better to find some way to do what you want with element properties
    if not stopper:
        stopper = actions.user.stopper(max_sec,[max_n])
    if cur_level > max_level:
        print(f"Windows accessibility element traversal reached max level {max_level}")
    else:
        if not stopper.over():
            yield el
            stopper.increment(0)
            children = el.children
            if children:
                for child in children:
                    if not stopper.over():
                        yield from get_every_child(child,cur_level + 1,max_level,max_n,max_sec,stopper)
        
mod.list("dynamic_element", desc="List of children of the active window")

ctx = Context()

@ctx.dynamic_list("user.dynamic_element")
def dynamic_element(spoken_form) -> dict[str,str]:
    print(f'FUNCTION dynamic_element: spoken_form = {spoken_form}')
    win = winui.active_window()
    if win == None:
        print("no active window...")
        return {}
    root = win.element
    if root == None:
        print("active window has no element...")
        return {}
    elements = list(get_every_child(root))
    print(f"{len(elements)} elements found...")
    out = {}
    for el in elements:
        # print(f'el: {el.name}')
        alias = str(el.name)
        if alias == "":
            alias = str(el.help_text)
        if alias != "":
            # add full name to dictionary
            out[str(alias)] = str(alias)
            # add single word command to dictionary
            singles = re.split('[^a-zA-Z]',str(alias))
            out[singles[0]] = str(alias)
            # add double word command to dictionary
            if len(singles) > 1:
                out[" ".join(singles[:2])] = str(alias)
    print("FUNCTION dynamic_element")
    print(f'window: {win}')
    print(f"ui window: {ui.active_window()}")
    print(f'root: {root}')
    # print(f'out: {out}')
    return out

@mod.action_class
class Actions:
    def el_prop_val(el: ax.Element, prop_name: str, as_text: bool = False):
        """Returns the property value or None if the property value cannot be retrieved"""
        
        try:
            # handle virtualized elements
            if "VirtualizedItem" in el.patterns:
                el.virtualizeditem_pattern.realize()
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
            elif prop_name.lower() == "clickable":
                if as_text:
                    loc = el.clickable_point
                    return f"x: {loc.x}   y: {loc.y}"
                else:
                    return el.clickable_point
            elif prop_name.lower() == "children":
                children = el.children
                if children == None:
                    if as_text:
                        return str(None)
                    else:
                        return 0
                elif as_text:
                    return str(len(children))
                else:
                    return children
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
            elif prop_name.lower() == "rect":
                return el.rect
            elif prop_name.lower() == "rect.x":
                rect = el.rect
                if rect:
                    return el.rect.x
            elif prop_name.lower() == "rect.y":
                rect = el.rect
                if rect:
                    return el.rect.y
            elif prop_name.lower() == "rect.width":
                rect = el.rect
                if rect:
                    return el.rect.width
            elif prop_name.lower() == "rect.height":
                rect = el.rect
                if rect:
                    return el.rect.height
            elif prop_name.lower() == "value":
                if "Value" in el.patterns:
                    return el.value_pattern.value
            elif prop_name.lower() == "value.is_read_only":
                if "Value" in el.patterns:
                    return el.value_pattern.is_read_only
            elif prop_name.lower() == "legacy.value":
                if "LegacyIAccessible" in el.patterns:
                    return el.legacyiaccessible_pattern.value
            elif prop_name.lower() == "legacy.state":
                if "LegacyIAccessible" in el.patterns:
                    return el.legacyiaccessible_pattern.state


            elif prop_name.lower() == "legacy.selection":
                if "LegacyIAccessible" in el.patterns:
                    return el.legacyiaccessible_pattern.selection
            elif prop_name.lower() == "legacy.name":
                if "LegacyIAccessible" in el.patterns:
                    return el.legacyiaccessible_pattern.name
            elif prop_name.lower() == "legacy.description":
                if "LegacyIAccessible" in el.patterns:
                    return el.legacyiaccessible_pattern.description
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
    def get_property_string(el: ax.Element):
        """creates a property string that can be converted into a property list"""
        prop_name = {"n":"name","c":"class_name","a":"automation_id"}
        r = []
        for prop_code in ["n","c","a"]:
            prop = prop_name[prop_code]
            val = actions.user.el_prop_val(el,prop)
            if val != '':
                r.append(f"{prop_code}={val}")
        return ",".join(r)
    def get_property_list(prop_str: str):
        """creates a property list from a string of the form n = ..., c = ..., a = ..."""
        r = []
        prop_name = {"n":"name","c":"class_name","a":"automation_id"}
        props = prop_str.split(",")
        for prop in props:
            if prop != '':
                val = prop.split("=")            
                if len(val) == 1:
                    val = ["n",val[0]]
                r.append((prop_name[val[0].strip()],val[1].strip()))
        return r
    def element_match(el: ax.Element, prop_list: list, conjunction: str="AND", mod_func: Callable = None, verbose: bool = False):
        """Returns true if the element matches all of the properties in the property dictionary"""
        return match(el,prop_list,conjunction,mod_func,verbose)
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
            except Exception as error:
                print(f'error: {error}')
        return r  
    def count_matching_children(el: ax.Element,prop_list: list):
        """Returns the number of children matching the property list conditions"""
        n = 0
        for child in el.children:
            if actions.user.element_match(child,prop_list):
                n += 1
        return n
    def matching_children(el: ax.Element, prop_list: list):
        """Returns a list of children of the input element that matches the property list"""
        r = []
        if el:
            for child in el.children:
                if actions.user.element_match(child,prop_list):
                    r.append(child)
        return r
    def matching_child(el: ax.Element,prop_list: list):
        """Returns the child of the input element that matches the property list"""
        if el:
            for child in el.children:
                if actions.user.element_match(child,prop_list):
                    return child
        return None
    def element_descendants(el: ax.Element, max_gen: int = -1):
        """obtain a list of all descendants of current element"""
    def matching_descendants(el: ax.Element, prop_list: list, generation: int,extra_gen: int = 0, verbose: bool = False):
        """Returns the matching descendants of the input element at the given generation, 
        or continues the search up to the given number of extra generations"""
        if verbose:
            print("FUNCTION matching_descendants...")
            print(f'prop_list: {prop_list}')
        cur_level = 0
        el_id = -1
        parent_id = -1
        r = []
        Q = []
        Q.append((cur_level,parent_id,el))    
        while len(Q) > 0:        
            cur_level,parent_id,el = Q.pop(0)
            if cur_level <= generation + extra_gen:
                el_id += 1
                try:
                    if el:
                        for child in el.children:
                            if verbose:
                                msg = "|".join([f"{x[0]}:{actions.user.el_prop_val(child,x[0])}" for x in prop_list])
                                print(f'cur_level: {cur_level} generation: {generation} {msg}')
                            Q.append((cur_level+1,el_id,child))        
                            if cur_level+1 >= generation:
                                if actions.user.element_match(child,prop_list,verbose = False):
                                    if verbose:
                                        print("element matches...")
                                    r.append(child)
                except Exception as error:
                    print(f'error: {error}')
        return r
    def matching_descendant(el: ax.Element, prop_list: list, gen: int, extra_gen: int = 0, verbose: bool = False):
        """Returns the descendant of the input element that matches the property list"""
        el_list = actions.user.matching_descendants(el,prop_list,gen,extra_gen,verbose)
        if el_list:
            if len(el_list) > 0:
                return el_list[0]
        return None
    def matching_ancestor(el: ax.Element, prop_list: list, max_gen: int = 25):
        """Returns the first ancestor that meets prop_list conditions, or None if none is found"""
        if max_gen == -1:
            max_gen == 25
        el_list = [el]
        i = 0
        while True:
            i += 1
            if i > max_gen:
                return None
            try:
                el = el.parent
                if actions.user.element_match(el,prop_list):
                    return el
            except Exception as error:
                print(f'error: {error}')
                return None
    def find_el_by_prop_seq(prop_seq: list, 
            root: ax.Element = None, 
            extra_search_levels: int = 2, 
            verbose: bool = False):
        """Finds element by working down from root"""
        if verbose:
            print("FUNCTION: actions.user.find_el_by_prop_seq()")
        if root == None:
            root = winui.active_window().element
        el_list = [root]
        def perform_search(el_list,level,verbose = False):
            valid_matches = []        
            for el in el_list:
                valid_matches += actions.user.matching_descendants(el,prop_list,level,verbose = verbose)
            return valid_matches
        for prop_list in prop_seq:
            extra_levels = 0
            valid_matches = perform_search(el_list,extra_levels)
            while len(valid_matches) == 0 and extra_levels < extra_search_levels:
                extra_levels += 1
                valid_matches = perform_search(el_list,extra_levels,False)
            if len(valid_matches) == 0:
                if verbose:
                    print(f"Could not find {prop_list}")
                el_list = []
                break        
            else:
                el_list = valid_matches
                if verbose:
                    print(f"found {prop_list}")
        if verbose:
            print(f"found {len(el_list)} matches")
        if len(el_list) > 0:
            return el_list[0]
        else:
            return None
    def act_on_element(el: ax.Element, action: str, delay_after_ms: int=0):
        """Perform action on element. Get actions from {user.ui_action}"""
        if el:
            action = action.lower()
            if action == "click" or action == "right-click":
                loc = actions.user.element_location(el)
                if loc != None:            
                    if delay_after_ms > 0:
                        actions.user.slow_mouse(loc.x,loc.y,delay_after_ms)
                        actions.sleep(f"{delay_after_ms + 75}ms")
                    else:
                        ctrl.mouse_move(loc.x,loc.y)
                    if action == "click":
                        ctrl.mouse_click()
                    elif action == "right-click":
                        ctrl.mouse_click(1)
                else:
                    print(f"Error in accessibility.py function act_on_element: Element has no location.")
                    return 
            elif action == "hover":
                loc = actions.user.element_location(el)
                if loc != None:    
                    actions.user.slow_mouse(loc.x,loc.y,delay_after_ms)
                else:
                    print(f"Error in accessibility.py function act_on_element: Element has no location.")
            elif action == "highlight":
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
            elif action == "expand":
                if "ExpandCollapse" in el.patterns:
                    el.expandcollapse_pattern.expand()
            elif action == "collapse":
                if "ExpandCollapse" in el.patterns:
                    el.expandcollapse_pattern.collapse()
            elif action == "scroll_into_view":
                if "ScrollItem" in el.patterns:
                    el.scrollitem_pattern.scroll_into_view()
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
    def key_to_element_by_prop_list(key: str, 
                        prop_list: str, 
                        escape_key: str=None, 
                        sec_lim: float = 5,
                        iter_limit: int = -1,
                        avoid_cycles: bool = True,
                        final_func: Callable = None,
                        verbose: bool = False):
        """press give him key until matching element is reached"""
        def key_continue(prop_list,first_el):
            el = winui.focused_element()
            if el:
                if el.__eq__(first_el):
                    actions.user.terminate_traversal()
                elif actions.user.element_match(el,prop_list):
                    actions.user.terminate_traversal()
                else:
                    actions.key(key)
            else:
                actions.user.terminate_traversal()
        first_el = winui.focused_element() if avoid_cycles else None
        actions.key(key)
        actions.user.initialize_traversal(
                    lambda: key_continue(prop_list,first_el),
                    sec_lim, iter_limit,final_func)
    def key_to_element(key: str, 
                        prop_str: str, 
                        escape_key: str=None, 
                        sec_lim: float = 5,
                        iter_limit: int = -1,
                        avoid_cycles: bool = True,
                        mod_func: Callable = None,
                        final_func: Callable = None,
                        verbose: bool = False):
        """press given key until the first matching element is reached"""
        prop_list = actions.user.get_property_list(prop_str)
        actions.user.key_to_element_by_prop_list(
            key,prop_list,key,sec_lim,iter_limit,avoid_cycles,final_func,verbose)
        
    def new_key_to_elem_by_val(key: str, val: str, prop: str="name", ordinal: int=1, limit: int=-1, escape_key: str=None, delay: float = 0.09):
        """press key until element with exact value for one property is reached"""
        prop_list = [(prop,val)]
        actions.user.new_key_to_matching_element(key,prop_list,ordinal = ordinal,limit = limit,escape_key = escape_key,delay = delay)
        
    def key_to_matching_element(key: str, 
                                prop_list: list, 
                                ordinal: int=1, 
                                limit: int=200, 
                                escape_key: str=None, 
                                delay: float = 0.03, 
                                sec_lim: float = 5,
                                avoid_cycles: bool = False,
                                mod_func: Callable = None,
                                verbose: bool = False):
        """press given key until the first matching element is reached"""
        if verbose:
            print(f"FUNCTION: key_to_matching_element limit: {limit} delay: {delay} avoids_cycles: {avoid_cycles}")
        el = actions.user.focused_element()
        first_el = el
        if verbose:
            print(f'first_el: {first_el}')
        last_el = el
        i = 1
        matches = 0
        if el:
            stopper = actions.user.stopper(sec_lim)
            while True:
               # if elapsed_sec > max_sec:
                if stopper.over():
                    print("break due to time overage")
                    break
                actions.key(key)
                if delay > 0:
                    actions.sleep(delay)
                el = actions.user.focused_element()
                if el:
                    if verbose:
                        if mod_func:
                            print(f"ELEMENT: {mod_func('name',el.name)} prop_list: {prop_list}")      
                    if actions.user.element_match(el,prop_list,mod_func = mod_func,verbose = False):
                        matches += 1
                    if (escape_key != None) and (last_el == el):
                        actions.key(escape_key)
                    last_el = el
                    i += 1
                    if matches == ordinal:
                        # print(f"Found #{ordinal} matching element!")
                        break
                    if i == limit:
                        print(f"Reached limit... (i={i}) :(")
                        break
                    if avoid_cycles:
                        if first_el == None:
                            print(f"First element no longer exists...")
                            break
                        if first_el.__eq__(el):
                            print(f"Cycled back to first element... :(")
                            break
                else:
                    print(f"Element is None... :(")
                    break
            if actions.user.element_match(el,prop_list,mod_func = mod_func):
                return el
            else:
                print(f"Element doesn't match property list... :(")
                print(f"element properties: {actions.user.element_information(el,prop_list = prop_list)}")
                return None
    def key_to_elem_by_val(key: str, val: str, prop: str="name", ordinal: int=1, limit: int=-1, escape_key: str=None, delay: float = 0.03):
        """press key until element with exact value for one property is reached"""
        prop_list = [(prop,val)]
        actions.user.key_to_matching_element(key,prop_list,ordinal = ordinal,limit = limit,escape_key = escape_key,delay = delay)
    def key_to_name_and_class(key: str, name: str, class_name: str = ".*",limit: int=-1,delay: float = 0.03):
        """Press key until element with matching name and classes reached"""
        prop_list = [("name",name),("class_name",class_name)]
        actions.user.key_to_matching_element(key,prop_list,limit = limit,delay = delay)

    def invoke_by_value(val: str, prop: str = "name", max_level: int = 99):
        """Searches for first element with given property value and invokes it."""
        prop_list = [prop,val]
        el = actions.user.matching_element(prop_list,max_level = max_level)
        actions.user.act_on_element(el,"invoke")

    

