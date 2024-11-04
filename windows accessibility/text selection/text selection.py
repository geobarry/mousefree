from talon.windows import ax as ax,ui as winui
from talon import app, Context,Module,actions,ctrl,ui,settings,clip
import re
import itertools

ax_units = ["Character","Format","Word","Line","Paragraph","Page","Document"]

mod = Module()

mod.setting("win_selection_distance",type = int,default = 100,
            desc = "Number of lines to search forward or backwards")

mod.list("text_search_direction","directions from cursor in which text can be searched")
mod.list("text_search_unit","units of text that can be searched for in windows accessibility")

def precise_target_and_position(target: re.Pattern, 
                text_range: ax.TextRange,
                search_dir: str = "DOWN",
                ordinal: int = 1):
    """Returns a tuple of (str,int) representing the precise match 
        and the ordinal rank of that precise match from the beginning, 
        so that we can transfer information from the regex match 
        to the windows accessibility TextRange.find_text function"""
    # Note this is not going to work very well for things like "second previous parens"

    # find all instances of the target within the text range text
    t = text_range.text
    print(f"target: {target}")
    m = re.findall(target,t)
    if m and len(m) >= ordinal:
        print(f'm: {m}')
        # determine precise target and loop parameters to iterate through preceding matches
        if search_dir.upper() == "UP":
            precise_trg = m[-ordinal]
            start,stop,step = len(m) - 1, len(m) - ordinal, -1
        else:
            precise_trg = m[ordinal - 1]
            start,stop,step = 0,ordinal - 1,1
        # precise_ordinal is index of target within windows accessibility search
        # i.e. number of times needed to iterate forward or backward
        precise_ordinal = 1
        for i in range(start,stop,step):
            if m[i] == precise_trg:
                precise_ordinal += 1
        print(f'precise_trg: {precise_trg}')
        return (precise_trg,precise_ordinal)
    else:
        return (None,None)
def find_target(trg: re.Pattern, 
                text_range: ax.TextRange = None,
                search_dir: str = "DOWN",
                ordinal: int = 1) -> ax.TextRange:
    """Searches for the target and return a ax.TextRange object or None"""
    # Handle case of no TextRange input
    if text_range is None:
        el = ui.focused_element()
        if "Text" not in el.patterns:
            print("Error in function find_target: focused element does not have text pattern")
            return None
        text_range = el.text_pattern.selection[0]
    # Use regex to find exact match text and its position
    precise_trg,precise_ordinal = precise_target_and_position(trg,text_range,search_dir,ordinal)
    if precise_trg != None:
        # Iteratively search for precise target using windows accessibility
        back = search_dir.upper() == "UP"
        r = text_range.find_text(precise_trg,backward = back)
        while precise_ordinal > 1:
            actions.sleep(0.05)
            precise_ordinal -= 1
            if search_dir.upper() == "UP":
                text_range.move_endpoint_by_range("End","Start",target = r)
            else:
                text_range.move_endpoint_by_range("Start","End",target = r)
            r = text_range.find_text(precise_trg,backward = back)            
            r.select()
        return r
    else:
        print("Target not found :(")
        return None
def get_scope(scope_dir: str = "DOWN",
                scope_unit: str = "Line",
                scope_unit_count: int = 100):
    """Returns a text range corresponding to the search scope"""
    # Error Checking
    if scope_unit not in ax_units:
        print("Error in function get_scope: scope_unit not valid")
        return 
    el = ui.focused_element()
    if "Text" not in el.patterns:
        print("Error in function get_scope: focused element does not have text pattern")
        return 
    # Get scope as a text range
    cur_range = el.text_pattern.selection[0]
    # avoid selecting anything in current selection#
    if scope_dir.upper() == "UP":
        cur_range.move_endpoint_by_range("End","Start",target = cur_range)
    if scope_dir.upper() == "DOWN":
        cur_range.move_endpoint_by_range("Start","End",target = cur_range)
    if scope_dir.upper() != "UP":
        cur_range.move_endpoint_by_unit("End",scope_unit,scope_unit_count)
    if scope_dir.upper() != "DOWN":
        cur_range.move_endpoint_by_unit("Start",scope_unit,-1*scope_unit_count)
    print(f"FUNCTION: get_scope")
    print(f'scope_dir: {scope_dir}')
    
#    print(f"cur_range: {cur_range.text}")
    return cur_range
def process_selection(processing_function,trg: str, scope_dir: str = "DOWN", ordinal: int = 1):
    """Performs function on selected text and then returns cursor to original position"""
    # get textRange so we can return cursor to original position
    el = ui.focused_element()
    init_range = None
    if "Text2" in el.patterns:
        init_range = el.text_pattern2.selection[0]
    if "Text" in el.patterns:
        init_range = el.text_pattern.selection[0]
    # find target
    actions.user.select_text(trg,scope_dir,ordinal)
    # perform processing function
    processing_function()
    # return to original selection
    if init_range != None:
        actions.sleep(0.2)
        init_range.select()
def scroll_to_selection(r,init_rect):
    """Scrolls to the input text range"""
    # Attempt to scroll into view
    try:
        trg_rect = r.bounding_rectangles[0]
        if trg_rect:
            if trg_rect.y <= -0.0:
                # target selection is offscreen
                r.scroll_into_view(align_to_top = True)
                # does not work if mouse is not on scrolling element
                actions.user.mouse_scroll_up(0.5)
            else:
                # try to scroll so that selected texas in the same position as previous cursor location
                # but this won't work consistently because of dpi scaling
                # better if scale_factor is too high than too low
                scale_factor = 2
                dy = int((trg_rect.y - init_rect.y) / scale_factor)
                actions.mouse_scroll(y=dy)
        else:
            r.scroll_into_view(align_to_top = True)
    except Exception as error:
        print(f"FUNCTION: scroll_to_selection\n{error}") # some apps or windows versions don't have bounding rectangles yet?

ctx = Context()
mod.list("win_dynamic_nav_target")
@ctx.dynamic_list("user.win_dynamic_nav_target")
def win_dynamic_nav_target(_) -> str:
    print("FUNCTION: win_dynamic_nav_target")
    cur_range = get_scope("both","Line",15)
    return f"""
    {cur_range.text}
    """
mod.list("win_fwd_dyn_nav_trg")
@ctx.dynamic_list("user.win_fwd_dyn_nav_trg")
def win_fwd_dyn_nav_trg(_) -> str:
    print("FUNCTION: win_fwd_dyn_nav_trg")
    cur_range = get_scope("DOWN","Line",settings.get("user.win_selection_distance"))
    t = re.sub(r'[^A-Za-z]+', ' ', cur_range.text)
    return f"""
    {t}
    """
mod.list("win_bkwd_dyn_nav_trg")
@ctx.dynamic_list("user.win_bkwd_dyn_nav_trg")
def win_bkwd_dyn_nav_trg(_) -> str:
    print("FUNCTION: win_bkwd_dyn_nav_trg")
    cur_range = get_scope("UP","Line",settings.get("user.win_selection_distance"))
    t = re.sub(r'[^A-Za-z]+', ' ', cur_range.text)
    # t = t.replace("’","'")
    print(f't: {t}')
    return f"""
    {t}
    """
# Note: the windows dynamic navigation target will take precedence over the following capture, according to observed behavior (not sure if this is guaranteed). So if a windows accessibility text element is in focus and there is both the word comma and a comma punctuation mark, the word will be selected.
@mod.capture(rule="[(letter|character)] <user.any_alphanumeric_key> | (abbreviate|abbreviation|brief) {user.abbreviation} | variable {user.variable_list} | function {user.function_list} | number <user.real_number> | word <user.word> | phrase <user.text>")
def win_nav_target(m) -> str:
    """A target to navigate to. Returns a regular expression."""
    include_homophones = False
    if hasattr(m, "any_alphanumeric_key"):
        return re.compile(re.escape(m.any_alphanumeric_key), re.IGNORECASE).pattern
    if hasattr(m, "navigation_target_name"):
        return re.compile(m.navigation_target_name).pattern
    if hasattr(m,"abbreviation"):
        t = m.abbreviation
    if hasattr(m,"variable_list"):
        t = m.variable_list
    if hasattr(m,"function_list"):
        t = m.function_list
    if hasattr(m,"real_number"):
        x = int(m.real_number)
        y = float(m.real_number)
        t = str(x) if x == y else str(y)
    if hasattr(m,"word"):
        t = m.word
        include_homophones = True
    if hasattr(m,"text"):
        t = m.text
        include_homophones = True
    if include_homophones:
        # include homophones
        word_list = re.findall(r"\w+",t)
        word_list = set(word_list)
        for w in word_list:
            phone_list = actions.user.homophones_get(w)
            if phone_list:
                t = t.replace(w,"(?:" + '|'.join(phone_list) + ")")
        # accommodate formatting by allowing non-letter characters between words
        t = t.replace(" ","[^a-z|A-Z]*")
    return t

@mod.action_class
class Actions:
    def select_text(trg: str, scope_dir: str = "DOWN", ordinal: int = 1):
        """Selects text using windows accessibility pattern if possible"""
        print("FUNCTION: select_text")
        print(f'select_text: scope_dir: {scope_dir}')
        trg = re.compile(trg.replace(" ",".{,3}"), re.IGNORECASE)
        el = ui.focused_element()
        if "Text" in el.patterns:
            try:
                r = find_target(trg,get_scope(scope_dir),search_dir = scope_dir,ordinal = ordinal)
                if r != None:
                
                    r.select()
            except:
                actions.user.navigation("SELECT",scope_dir,"DEFAULT","default",trg,1)
        else:
            actions.user.navigation("SELECT",scope_dir,"DEFAULT","default",trg,1)
    def replace_text(new_text: str, trg: str, scope_dir: str = "DOWN", ordinal: int = 1):
        """Replaces target with the new text"""
        def replace_process():
            with clip.revert():
                clip.set_text(new_text)
                actions.edit.paste()
                actions.sleep(0.15)
        process_selection(replace_process,trg,scope_dir,ordinal)
    def format_text(fmt: str, trg: str, scope_dir: str = "DOWN", ordinal: int = 1):
        """Applies formatter to targeted text"""
        def format_process():
            t = actions.edit.selected_text()
            t = actions.user.formatted_text(t,fmt)
            with clip.revert():
                clip.set_text(t)
                actions.sleep(0.15)
                actions.edit.paste()
                actions.sleep(0.15)
        process_selection(format_process,trg,scope_dir,ordinal)
    def phones_text(trg: str, scope_dir: str = "DOWN", ordinal: int = 1):
        """Performs homophone conversion on targeted text"""
        print("FUNCTION: phones_text")
        print(f'trg: {trg}')
        def phones_process():
            # perform homophones operation
            w = actions.edit.selected_text()
            options = actions.user.homophones_get(w)
            lower_options = [x.lower() for x in options]
            print(f'options: {options}')
            i = lower_options.index(w.lower())
            i = (i + 1) % len(options)
            x = options[i]
            print(f'i: {i}')
            print(f'x: {x}')
            # would be nice to match case with the original selected text here
            with clip.revert():
                clip.set_text(x)
                actions.sleep(0.15)
                actions.edit.paste()
                actions.sleep(0.15)
        process_selection(phones_process,trg,scope_dir,ordinal)
    def go_text(trg: str, scope_dir: str, before_or_after: str, ordinal: int = 1):
        """Navigates to text using windows accessibility pattern if possible"""
        trg = re.compile(trg, re.IGNORECASE)
        el = ui.focused_element()
        if "Text" in el.patterns:
            try:
                cur_range = el.text_pattern.selection[0]
                # for automatic scrolling; should be moved to separate function for other operations
                init_rect = None
                trg_rect = None
                try:
                    init_rect = cur_range.bounding_rectangles[0]
                except Exception as error:
                    pass # some apps or windows versions don't have bounding rectangles yet?
                r = find_target(trg,get_scope(scope_dir),search_dir = scope_dir,ordinal = ordinal)
                if r != None:
                    src_pos = "End" if before_or_after.upper() == "BEFORE" else "Start"
                    trg_pos = "Start" if before_or_after.upper() == "BEFORE" else "End"
                    r.move_endpoint_by_range(src_pos,trg_pos,target = r)
                    r.select()
                    scroll_to_selection(r,init_rect)
            except:
                print("unhandled exception in windows accessibility text selection; reverting to old method")
                actions.user.navigation("GO",scope_dir,"DEFAULT",before_or_after,trg,ordinal)               
        else:
        	actions.user.navigation("GO",scope_dir,"DEFAULT",before_or_after,trg,ordinal)
    def extend_selection(trg: str,
                        scope_dir: str,
                        before_or_after: str,
                        ordinal: int = 1):
        """Extend currently selected text using windows accessibility pattern if possible"""
        trg = re.compile(trg, re.IGNORECASE)
        el = ui.focused_element()
        if "Text" in el.patterns:
            try:
                cur_range = el.text_pattern.selection[0]
                r = find_target(trg,get_scope(scope_dir),search_dir = scope_dir,ordinal = ordinal)
                if r != None:
                    src_pos = "Start" if scope_dir.upper() == "UP" else "End"
                    trg_pos = "Start" if before_or_after.upper() == "BEFORE" else "End"
                    cur_range.move_endpoint_by_range(src_pos,trg_pos,target = r)
                    cur_range.select()
            except:
                actions.user.navigation("EXTEND",scope_dir,"DEFAULT",before_or_after,trg,ordinal)
        else:
            actions.user.navigation("EXTEND",scope_dir,"DEFAULT",before_or_after,trg,ordinal)
    def move_by_unit(unit: str, scope_dir: str, ordinal: int = 1):
        """Moves the cursor by the selected number of units"""
        el = ui.focused_element()
        if "Text" in el.patterns:
            cur_range = el.text_pattern.selection[0]
            if scope_dir.upper() == "UP":
                ordinal = -ordinal
                cur_range.move_endpoint_by_range("End","Start",target = cur_range)
            else:
                cur_range.move_endpoint_by_range("Start","End",target = cur_range)
            cur_range.move(unit,ordinal)
            cur_range.select()
            cur_range.scroll_into_view(True)
    def extend_by_unit(unit: str, scope_dir: str, ordinal: int = 1):
        """Extends the selection to the end/beginning of next unit"""
        el = ui.focused_element()
        if "Text" in el.patterns:
            print(f"Selection Ranges: {len(el.text_pattern.selection)}")
            print(f"Visible Ranges: {len(el.text_pattern.visible_ranges)}")
            print(f"First Visible Range: {el.text_pattern.visible_ranges[0]}")
            cur_range = el.text_pattern.selection[0]
            ext_range = el.text_pattern.selection[0]
            ordinal = -ordinal if scope_dir.upper() == "UP" else ordinal
            pos = "Start" if scope_dir.upper() == "UP" else "End"
            src_pos = "End" if pos == "Start" else "Start"
            ext_range.move_endpoint_by_range(src_pos,pos,target = ext_range)
            ext_range.move(unit,ordinal)
            cur_range.move_endpoint_by_range(pos,pos,target = ext_range)
            cur_range.select()            
            cur_range.scroll_into_view(True)
    def expand_selection(left: bool = True, right: bool = True, 
            unit: str = "Character", ordinal: int = 1):
        """Expands selection in the specified directions"""
        el = ui.focused_element()
        if "Text" in el.patterns:
            cur_range = el.text_pattern.selection[0]
#            ordinal = -ordinal if scope_dir.upper() == "UP" else ordinal
#            pos = "Start" if scope_dir.upper() == "UP" else "End"
#     def move_endpoint_by_unit(self, endpoint: str, unit: str, count: int) -> int: ...        
        if left:
            cur_range.move_endpoint_by_unit("Start",unit,-1*ordinal)
        if right:
            cur_range.move_endpoint_by_unit("End",unit,ordinal)
        cur_range.select()            
        cur_range.scroll_into_view(True)
    def select_unit(unit: str):
        """Selects the enclosing unit around the current cursor position"""
        el = ui.focused_element() 
        if "Text" in el.patterns:
            cur_range = el.text_pattern.selection[0]
            cur_range.expand_to_enclosing_unit(unit)
            cur_range.select()
        else:
            actions.user.edit_command("select", unit)
    def test_backward_search():
        """for debugging"""
        el = ui.focused_element()
        cur_range = el.text_pattern.selection[0]
        r = cur_range.find_text("distance",backward = True)
        r.select()
    def test_forward_search():
        """for debugging"""
        el = ui.focused_element()
        cur_range = el.text_pattern.selection[0]
        r = cur_range.find_text("distance",backward = False)
        r.select()