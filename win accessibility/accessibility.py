from talon import Module, ui, Context, clip, ctrl, cron, actions, canvas, screen, settings
from talon.windows import ax as ax, ui as winui
from talon.types import Point2d as Point2d
from talon.skia import  Paint
import inspect
import math
import re

from copy import deepcopy
import time
from typing import Callable, Any, List, Tuple
n = 0
start_time = None

mod = Module()

mod.list("nav_key","keys commonly used to navigate UI elements")
mod.list("action_key","keys commonly used to invoke UI elements")
mod.list("ui_action","actions that can be performed on accessibility elements")

@mod.capture(rule = "[control] [(alt|alternate)] [(shift|sky)] {user.nav_key}")
def nav_key(m) -> str:
    """A navigation key preceded or not by standard modifiers"""
    print(f'm: {m}')
    r = str(m)
    r = r.replace("control ","ctrl-").replace("alternate","alt").replace("alt ","alt-").replace("sky","shift").replace("shift ","shift-")
    return r

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

def match(el: ax.Element, prop_list: List[Any], mod_func: Callable = None, verbose: bool = False) -> bool:
    """
    Evaluate a property list where prop_list is a possibly nested list windows automation element conditions in one of two forms:
    (1) Simple list of zero or more conditions as tuples in the form of ("<prop_name>","<prop_val>").
		A simple list is an "AND" list, i.e. it evaluates to True only if every tuple condition evaluates to True. Empty list -> True.
		- or -
	(2) Nested list in which the first item is a string boolean conjunction, and the second item is a list of valid property lists in either simple or nested form, i.e. ["OR", subprop_list] or ["AND", subprop_list].
    """
    if verbose:
        print("FUNCTION: match")
        print(f'prop_list: {prop_list}')
        print(f'conjunction: {conjunction}')
    def eval_cond(prop,trg_val):
        if verbose:
            print(f'prop: {prop}')
            print(f'trg_val: {trg_val}')
        def value_match(prop_val,trg_val):
            # if trg_val is a string, convert to a regex pattern
            if verbose:
                print("inside value_match sub function")
            if type(trg_val) != re.Pattern:
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
                if prop_val != None:
                    return re.match(trg_val,prop_val) != None
                else:
                    return None
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
            try:
                prop_val = actions.user.el_prop_val(el, prop, as_text = True)
            except Exception as error:
                print("MATCH: error retrieving property value")
                print(f'el: {el}')
                print(f'prop: {prop}')
                raise Exception(error)
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
    

    if not isinstance(prop_list, list):
        raise TypeError("match expects a list prop_list")

    # empty list => True
    if len(prop_list) == 0:
        return True

    # helper to evaluate a single item which may be a tuple or a nested list
    def eval_item(item: Any) -> bool:
        if isinstance(item, tuple):
            return eval_cond(item[0],item[1])
        if isinstance(item, list):
            return match(el,item,mod_func,verbose)
        print(f'item: {item}')
        raise TypeError("List items must be tuples or lists")

    # operator form: ["OR" or "AND", subprop_list]
    if len(prop_list) == 2 and isinstance(prop_list[0], str) and prop_list[0].upper() in ("OR", "AND"):
        op = prop_list[0]
        sub = prop_list[1]
        if not isinstance(sub, list):
            raise TypeError("Operator second argument must be a list prop_list")
        values = [eval_item(item) for item in sub]
        return any(values) if op.upper() == "OR" else all(values)

    # plain list form: evaluate each element and require all True
    return all(eval_item(item) for item in prop_list)

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
        print(f'prop_str: {prop_str}')
        r = []
        prop_name = {"n":"name","c":"class_name","a":"automation_id","p":"printout"}
        props = prop_str.split(",")
        for prop in props:
            if prop != '':
                val = prop.split("=")            
                if len(val) == 1:
                    val = ["n",val[0]]
                r.append((prop_name[val[0].strip()],val[1].strip()))
        return r
    def get_property_sequence(prop_seq_str: str):
        """creates a property sequence from a string of the form <prop_str>;<prop_str>..."""
        prop_str_list = prop_seq_str.split(";")
        r = []
        for prop_str in prop_str_list:
            prop_list = actions.user.get_property_list(prop_str)
            r.append(prop_list)
        return r
    def ax_action(action: str, prop_seq_str: str, verbose: bool = False):
        """Finds element threw accessibility sequence from current window root, and performs action if found"""
        root = actions.user.window_root()
        if root:
            prop_seq = actions.user.get_property_sequence(prop_seq_str)
            el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = verbose)
            if el:
                actions.user.act_on_element(el,action)
    def element_match(el: ax.Element, prop_list: list, conjunction: str="AND", mod_func: Callable = None, verbose: bool = False):
        """Returns true if the element matches all of the properties in the property dictionary"""
        if el:
            actions.user.el_tracker_pause_updating()
            r = match(el,prop_list,mod_func,verbose)
            actions.user.el_tracker_resume_updating()
            return r
        else:
            return False
    def element_exists(prop_list: list,max_level: int = 7):
        """Returns true if an element where the given properties exists"""
        actions.user.el_tracker_pause_updating()
        root = actions.user.window_root()
        elements = list(get_every_child(root,max_level = max_level))
        for el in elements:
            if actions.user.element_match(el,prop_list):            
                actions.user.el_tracker_resume_updating()
                return True
        actions.user.el_tracker_resume_updating()
        return False
    def element_list():
        """returns_a_list_of_all_elements"""
        actions.user.el_tracker_pause_updating()
        root = actions.user.window_root()
        r = list(get_every_child(root))
        actions.user.el_tracker_resume_updating()
        return r
    def matching_element(prop_list: list, item_num: int = 0, max_level: int = 12,root: ax.Element = None):
        """returns the zero based nth item matching the property list, or None"""
        if root == None:
            root = actions.user.window_root()
        matches = actions.user.matching_elements(prop_list,max_level = max_level,root = root)
        if len(matches) > item_num:
            return matches[item_num]
        else:
            return None
    def matching_elements(prop_list: list, max_level: int = 12, root: ax.Element = None):
        """Returns a list of all UI elements under the root that match the property list"""
        actions.user.el_tracker_pause_updating()
        r = []
        # get list of elements
        if root == None:
            root = actions.user.window_root()
        elements = list(get_every_child(root,max_level = max_level))       
        # search for match
        for el in elements:
            # print(el.class_name)
            try:
                if actions.user.element_match(el,prop_list):
                    r.append(el)
            except Exception as error:
                print(f'error: {error}')
        actions.user.el_tracker_resume_updating()
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
    def matching_descendants(el: ax.Element, prop_list: list, generation: int,extra_gen: int = 0, time_limit: float = 5,verbose: bool = False):
        """Returns the matching descendants of the input element at the given generation, 
        or continues the search up to the given number of extra generations"""
        actions.user.el_tracker_pause_updating()
        if verbose:
            print("FUNCTION matching_descendants...")
            print(f'root: {el} prop_list: {prop_list}')
        cur_level = 0
        el_id = -1
        parent_id = -1
        r = []
        Q = []
        Q.append((cur_level,parent_id,el))    
        stopper = actions.user.stopper(time_limit)
        while len(Q) > 0:        
            cur_level,parent_id,el = Q.pop(0)
            if cur_level <= generation + extra_gen:
                el_id += 1
                try:
                    if el:
                        children = el.children
                        if verbose:
                            print(f'children: {children}')
                        if children:
                            for child in children:
                                if stopper.over():
                                    if verbose:
                                        print(f"FUNCTION: matching_descendants - stopping due to stopper overage")
                                    return 
                                stopper.increment()
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
        actions.user.el_tracker_resume_updating()
        return r
    def matching_descendant(el: ax.Element, prop_list: list, gen: int, extra_gen: int = 0, verbose: bool = False):
        """Returns the descendant of the input element that matches the property list"""
        el_list = actions.user.matching_descendants(el,prop_list,gen,extra_gen,verbose = verbose)
        if el_list:
            if len(el_list) > 0:
                return el_list[0]
        return None
    def matching_ancestor(el: ax.Element, prop_list: list, max_gen: int = 25, time_limit: float = 5, verbose: bool = False):
        """Returns the first ancestor that meets prop_list conditions, or None if none is found"""
        actions.user.el_tracker_pause_updating()
        if max_gen == -1:
            max_gen == 25
        el_list = [el]
        i = 0
        stopper = actions.user.stopper(time_limit)
        while True:
            try:
                if stopper.over():
                    print("MATCHING_ANCESTOR time is over")
                    actions.user.el_tracker_resume_updating()
                    return 
                stopper.increment()
                if el:
                    el = actions.user.el_prop_val(el,"parent")
                if el:
                    if verbose:
                        msg = ' | '.join(f"{prop[0]}: {actions.user.el_prop_val(el,prop[0])}" for prop in prop_list)
                        print(f'msg: {msg}')
                    if actions.user.element_match(el,prop_list):
                        actions.user.el_tracker_resume_updating()
                        return el
                else:
                    actions.user.el_tracker_resume_updating()
                    return None
            except Exception as error:
                print("FUNCTION matching_ancestor: ancestor not found :(")
                print(f'error: {error}')
                actions.user.el_tracker_resume_updating()
                return None
    def find_el_by_prop_seq(prop_seq: list, root: ax.Element = None, extra_search_levels: int = 2, time_limit: float = 5, ordinal: int = 1, verbose: bool = False):
        """Finds element by working down from root"""
        actions.user.el_tracker_pause_updating()
        if verbose:
            print("FUNCTION: actions.user.find_el_by_prop_seq()")
        if root == None:
            root = actions.user.window_root()
        el_list = [root]
        def perform_search(el_list,level,verbose = False):
            valid_matches = []        
            # print(f'el_list: {el_list}')
            # print(f'prop_list: {prop_list}')
            for el in el_list:
                x = actions.user.matching_descendants(el,prop_list,level,verbose = verbose)
                if x:
                    valid_matches += x
            return valid_matches
        stopper = actions.user.stopper(time_limit)
        if verbose:
            print(f'FUNCTION find_el_by_prop_seq() root: {root}')
        stopper = actions.user.stopper()
        for prop_list in prop_seq:
            # NEW METHOD TO SEARCH EXTRA LEVELS MORE EFFICIENTLY
            valid_matches = []
            extra_levels = 0
            parent_list = el_list
            while len(valid_matches) == 0 and extra_levels <= extra_search_levels:
                next_parents = []
                for parent in parent_list:
                    children = actions.user.el_prop_val(parent,'children')
                    if children:
                        next_parents += children
                        for child in children:
                            if stopper.over():
                                return
                            if actions.user.element_match(child,prop_list):
                                valid_matches.append(child)
                parent_list = next_parents
                extra_levels += 1            
            # OLD METHOD
            # valid_matches = perform_search(el_list,extra_levels)
            # if stopper.over():
                # if verbose:
                    # print(f"FUNCTION find_el_by_prop_seq stopping due to stopper overage")
                # return 
            # print(f'len(valid_matches): {len(valid_matches)}')
            # while len(valid_matches) == 0 and extra_levels < extra_search_levels:
                # extra_levels += 1
                # valid_matches = perform_search(el_list,extra_levels,False)
                # if stopper.over():
                    # if verbose:
                        # print(f"FUNCTION find_el_by_prop_seq stopping due to stopper overage")
                    # return 

            if len(valid_matches) == 0:
                if verbose:
                    print(f"Could not find {prop_list}")
                    
                    for el in el_list:
                        print(f'el: {el}')
                        children = actions.user.el_prop_val(el,"children")
                        print(f'children: {children}')
                        if children:
                            for child in children:
                                msg = actions.user.element_information(child,prop_list = ["name","class_name","printout"])
                                print(f'child: {msg}')
                        
                el_list = []
                break        
            else:
                el_list = valid_matches
                if verbose:
                    print(f"found {prop_list}")
        if verbose:
            print(f"found {len(el_list)} matches")
        actions.user.el_tracker_resume_updating()
        if len(el_list) >= ordinal:
            return el_list[ordinal-1]
        else:
            return None

    def act_on_focused_element(action: str, mouse_delay: int = 0):
        """Performs action on currently focused element"""
        el = actions.user.safe_focused_element()
        actions.user.act_on_element(el,action,mouse_delay)
    def act_on_mouse_element(action: str, mouse_delay: int = 0):
        """Returns the UI element at the current mouse position"""
        pos = ctrl.mouse_pos()
        el = ui.element_at(pos[0],pos[1])
        actions.user.act_on_element(el,action,mouse_delay)
    def act_on_named_element(name: str, action: str, mouse_delay: int = 0):
        """Performs action on first element beginning with given name"""
        prop_list = [("name",name)]
        elements = actions.user.matching_elements(prop_list)
        if len(elements) > 0:
            actions.user.act_on_element(elements[0],action,mouse_delay)
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
                        use_registered_element: bool = False,
                        verbose: bool = False):
        """press give him key until matching element is reached"""
        def key_continue(prop_list,use_registered_element,first_el, try_number = 0):
            print("FUNCTION key_continue")

            if use_registered_element:
                el = actions.user.focused_element()
            else:
                el = actions.user.safe_focused_element()
            print("FUNCTION key_to_element_by_prop_list")                    
            print(f'user_focus: {el} name: {el.name}')
            if el:
                if el.__eq__(first_el):
                    print(f"FUNCTION key_to_element_by_prop_list - stopping because equal to first element")
                    actions.user.terminate_traversal()
                elif actions.user.element_match(el,prop_list):
                    print("found what we are looking for - terminating traversal")
                    actions.user.terminate_traversal()
                else:
                    actions.key(key)
            else:
                print("FUNCTION key_to_element_by_prop_list - stopping due to element is none")
                actions.user.terminate_traversal()

        first_el = actions.user.safe_focused_element() if avoid_cycles else None
        actions.key(key)
        actions.user.initialize_traversal(
                    lambda: key_continue(prop_list,use_registered_element,first_el),
                    sec_lim, iter_limit,finish_function = final_func)
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
            key,prop_list,key,sec_lim,iter_limit,avoid_cycles,final_func = final_func,verbose = verbose)
        
    def new_key_to_elem_by_val(key: str, val: str, prop: str="name", ordinal: int=1, limit: int=-1, escape_key: str=None, delay: float = 0.09):
        """press key until element with exact value for one property is reached"""
        prop_list = [(prop,val)]
        actions.user.new_key_to_matching_element(key,prop_list,ordinal = ordinal,limit = limit,escape_key = escape_key,delay = delay)
        
    def key_to_matching_element(key: str, 
                                prop_list: list, 
                                ordinal: int=1, 
                                limit: int=30, 
                                escape_key: str=None, 
                                delay: float = 0.03, 
                                sec_lim: float = 5,
                                avoid_cycles: bool = False,
                                mod_func: Callable = None,
                                el_func: Callable = actions.user.safe_focused_element,
                                verbose: bool = False):
        """press given key until the first matching element is reached"""
        if verbose:
            print(f"FUNCTION: key_to_matching_element \n  prop_list: {prop_list}  \nlimit: {limit} delay: {delay} avoids_cycles: {avoid_cycles}")
        el = actions.user.safe_focused_element()
        first_el = el
        if verbose:
            print(f'first_el: {first_el}')
        last_el = el
        i = 1
        matches = 0
        if el:
            stopper = actions.user.stopper(sec_lim,[limit])
            while True:
               # if elapsed_sec > max_sec:
                if stopper.over():
                    print("break due to time overage")
                    break
                actions.key(key)
                
                if delay > 0:
                    actions.sleep(delay)
                el = actions.user.safe_focused_element()
                if verbose:
                    msg = actions.user.element_information(el,prop_list = [prop[0] for prop in prop_list])
                    print(f"element: {msg}")

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
                        print(f"Found #{ordinal} matching element!")
                        print(f'el: {el} prop_list: {prop_list}')
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
#                            break
                else:
                    print(f"Element is None... :(")
                    break
            if actions.user.element_match(el,prop_list,mod_func = mod_func):
                return el
            else:
                print(f"Element doesn't match property list... :(")
                print(f"element properties: {actions.user.element_information(el,prop_list = [prop[0] for prop in prop_list])}")
                return None
    def key_to_elem_by_val(key: str, val: str, prop: str="name", ordinal: int=1, limit: int=200, escape_key: str=None, delay: float = 0.03):
        """press key until element with exact value for one property is reached"""
        prop_list = [(prop,val)]
        actions.user.key_to_matching_element(key,prop_list,ordinal = ordinal,limit = limit,escape_key = escape_key,delay = delay)
    def key_to_name_and_class(key: str, name: str, class_name: str = ".*",limit: int=-1,delay: float = 0.03):
        """Press key until element with matching name and classes reached"""
        prop_list = [("name",name),("class_name",class_name)]
        actions.user.key_to_matching_element(key,prop_list,limit = limit,delay = delay)
    def wait_for_element(prop_list: list, el_func: Callable = actions.user.safe_focused_element, delay: float = 0.2, time_limit: float = 5, verbose: bool = False):
        """Waits until an element matching the property list becomes focused, and returns that element or None"""
        stopper = actions.user.stopper(time_limit,[int(time_limit/delay) + 1])
        while True:
            el = el_func()
            # el = actions.user.safe_focused_element()
            if verbose:
                print(f'el: {el} name: {el.name} prop_list: {prop_list}')
            if el:
                if actions.user.element_match(el,prop_list):
                    return el
            if stopper.over():
                return None
            stopper.increment(0)
            actions.sleep(delay)

    def invoke_by_value(val: str, prop: str = "name", max_level: int = 99):
        """Searches for first element with given property value and invokes it."""
        prop_list = [prop,val]
        el = actions.user.matching_element(prop_list,max_level = max_level)
        actions.user.act_on_element(el,"invoke")

    
    

    def scroll_el_to_top(el: ax.Element = None, increment: float = 2, delay: float = 0.00):
        """Scrolls container to bring input element to the top"""
        # for now we are going to assume element is vertically not horizontally scrollable
        # NOTES ON SCROLL PATTERN:
        # - pattern.scroll takes keywords not floats as input: NoAmount, SmallIncrement, LargeDecrement
        # - if horizontal scrolling is not allowed, pattern.set_scroll_percent horizontal argument must be set to -1
        if not el:
            el = actions.user.safe_focused_element()
        if el:
            # find container
            prop_list = [("patterns",".*'Scroll'.*")]
            container = actions.user.matching_ancestor(el,prop_list,verbose = False)
            if container:
                # from here need to scroll down as needed until element y == container yield
                pattern = container.scroll_pattern
                if pattern:
                    # first scroll to bottom
                    vrt = pattern.vertical_percent
                    container_rect = actions.user.el_prop_val(container,"rect")
                    el_rect = actions.user.el_prop_val(el,"rect")
                    el_ht = el_rect.height
                    dy = el_rect.y - container_rect.y
                    i = 0
                    while dy > el_ht and vrt < 100 and i < 100:
                        actions.sleep(delay)
                        pattern.set_scroll_percent(-1,min(vrt + increment,100))
                        vrt = pattern.vertical_percent
                        container_rect = actions.user.el_prop_val(container,"rect")
                        el_rect = actions.user.el_prop_val(el,"rect")
                        container_ht = pattern.vertical_size
                        dy = el_rect.y - container_rect.y


                    
                