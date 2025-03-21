from talon import Module, ui, Context, clip, ctrl, cron, actions, canvas, screen, settings
from talon.windows import ax as ax, ui as winui
import re

mod = Module()

mod.list("element_property","name of property that can be accessed with actions.user.el_prop_val")

ctx = Context()

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
            
@mod.action_class
class Actions:
    def element_information(el: ax.Element, headers: str = False, as_dict: bool = False, verbose: str = False):
        """Returns information separated by tabs that can be pasted into a spreadsheet"""
        msg = ""
        prop_list = ["name","class_name",
                        "help_text","automation_id",
                        "printout",
                        "patterns","access_key",
                        "is_keyboard_focusable","is_enabled",
                        "rect.height","item_status","flows_to",
                    ]
        other_prop = [
                        "clickable_point",
                        "rect.x","rect.y",
                        "rect.width",
                    "window_handle","pid","access_key","has_keyboard_focus",
                    "children","is_control_element","is_content_element",
                    "item_type","item_status","described_by",
                    "provider_description",
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
            # Get property values, removing line breaks
            return  "\t".join([" ".join(str(actions.user.el_prop_val(el,prop,as_text = True)).splitlines()) for prop in prop_list])
    def copy_elements_accessible_by_key(key: str, limit: int=20, delay: int = 0.03, verbose: bool = False):
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
        msg = actions.user.element_information(el,headers = True)
        msg += "\n" + actions.user.element_information(el)
        clip.set_text(msg)
    def copy_focused_element_to_clipboard():
        """Copies information about currently focused element to the clipboard"""
        el = winui.focused_element()
        msg = actions.user.element_information(el, headers = True, verbose = False)
        msg += "\n" + actions.user.element_information(el, verbose = False)
        clip.set_text(msg)
    def element_descendant_tree(el: ax.Element, max_level: int = 7):
        """Returns a list of [level,cur_id,parent_id,el]"""
        el_info = breadth_first_tree(el,max_level = max_level)
        return el_info
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
    def copy_focused_element_descendants(levels: int = 12):
        """Copies information about currently focused element and children to the clipboard"""
        el = winui.focused_element()
        actions.user.copy_elements_to_clipboard(levels,root = el)
    def element_ancestors(el: ax.Element, max_gen: int = -1):
        """Returns a list of element ancestors including current element"""
        if max_gen == -1:
            max_gen = 200
        el_list = [el]
        i = 0
        
        while True:
            i += 1
            if i > max_gen:
                break
            try:
                el = el.parent
                el_list.append(el)
            except Exception as error:
                print(f'FUNCTION element_ancestors - error: {error}\n   (this is probably by design)')
                break
        return el_list
    def copy_element_sequence_to_clipboard(el: ax.Element, props: str):
        """copies python code for property sequence to access element to clipboard"""
        el_list = actions.user.element_ancestors(el)
        el_list.reverse()
        props = props.split(",")
        props = [x.strip() for x in props]
        prop_seq = []
        for el in el_list:
            prop_list = []
            for prop in props:
                val = actions.user.el_prop_val(el,prop,as_text = True)
                prop_list.append(f'("{prop}","{val}")')
            prop_seq.append(f'\t[{",".join(prop_list)}]')
        r = "[\n\t\t" + ",\n\t\t".join(prop_seq[2:]) + "\n\t]"
        r = f"\troot = winui.active_window().element\nprop_seq = {r}\nel = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = True)"
        clip.set_text(r)
    def copy_element_ancestors(el: ax.Element, verbose: bool = False):
        """Copies information on element ancestors to clipboard"""
        el_list = actions.user.element_ancestors(el)
        hdr = actions.user.element_information(el,verbose = False,headers = True)
        msg = "\n".join([actions.user.element_information(x,verbose = False) for x in el_list])
        msg = hdr + "\n" + msg
        clip.set_text(msg)
    def copy_mouse_element_sequence(props: str):
        """Copies python code for property sequence to access element under mouse position to clipboard"""
        pos = ctrl.mouse_pos()        
        actions.user.copy_element_sequence_to_clipboard(ui.element_at(pos[0],pos[1]),props)
    def copy_focused_element_sequence(props: str):
        """Copy python code for focused element's property sequence to clipboard"""
        actions.user.copy_element_sequence_to_clipboard(winui.focused_element(),props)
    def copy_mouse_element_ancestors(verbose: bool = False):
        """Retrieves list of ancestors of current mouse element"""
        pos = ctrl.mouse_pos()        
        el = winui.element_at(pos[0],pos[1])
        print("FUNCTION: copy_mouse_element_ancestors")
        print(f'el: {el}')
        actions.user.copy_element_ancestors(el,verbose)
    def copy_focused_element_ancestors(verbose: bool = False):
        """Retrieves list of ancestors of currently focused element"""
        el = winui.focused_element()
        print("FUNCTION: copy_focused_element_ancestors")
        print(f'el: {el}')
        actions.user.copy_element_ancestors(el,verbose)

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
        print(f'first_access_key: {first_access_key}')
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
#                print(f'heading_access_key: {heading_access_key}')
                # hello check that we're not back at the first element
                if name == first_name and access_key == first_access_key:
                    print("the same name and access key as first element")
                    break
                # check that access key begins with (but is not the same as) first access key
                elif access_key.startswith(heading_access_key) and not access_key == heading_access_key:
                    r.append((name,access_key))
                else:
                    # if access key is the same as first element but name is not, we have a phantom element
                    print("access key does not match ribbon heading")
                    pass
            except Exception as error:
                print(f'error: {error}')
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
    def copy_descendant_sequences(root: ax.Element, 
                                props: list = ["name","class_name"],
                                stop_patterns: list = ["Invoke","ExpandCollapse"],
                                require_name: bool = True):
        """Returns a list of property strings to get from the root to each 
            element with a matching stop pattern"""
        def walk_children(el, prop_str_list):
            prop_str_list.append(actions.user.get_property_string(el))
            stop = False
            for pattern in stop_patterns:
                if pattern in el.patterns:
                    stop = True
            if require_name:
                if el.name == '':
                    stop = False
            if stop:
                return [f"{el.name}: " + ";".join(prop_str_list)]
            else:
                print("walking children...")
                r = []
                for child in el.children:
                    r += walk_children(child,prop_str_list)
            return r
        r = []
        for child in root.children:
            r += walk_children(child,[])
        clip.set_text("\n".join(r))
    def copy_focused_element_descendant_sequences(props: list = ["name","class_name"],
                                stop_patterns: list = ["Invoke","ExpandCollapse"],
                                require_name: bool = True):
        """copy text version of property tests of focused element descendants to clipboard"""
        el = winui.focused_element()
        actions.user.copy_descendant_sequences(el,props,stop_patterns,require_name)
        
def clean(t):
    t = t.lower()
    regex = re.compile('[^a-zA-Z0-9]')
    #First parameter is the replacement, second parameter is your input string
    t = re.sub('\.\.\.', ' dialog', t)
    t = regex.sub(' ', t)
    t = re.sub(' +', ' ', t)
    return t