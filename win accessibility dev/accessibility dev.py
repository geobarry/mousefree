from talon import Module, ui, Context, clip, ctrl, cron, actions, canvas, screen, settings
from talon.windows import ax as ax, ui as winui
import re

mod = Module()
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
