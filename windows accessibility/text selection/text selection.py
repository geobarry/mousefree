from talon.windows import ax as ax,ui as winui
from talon import app, Context,Module,actions, ctrl,ui
import re
import itertools

ax_units = ["Character","Format","Word","Line","Paragraph","Page","Document"]

mod = Module()

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
    """Searches for the target and return a ax.TextRange word object or None"""
    # Handle case of no TextRange input
    if text_range is None:
        el = ui.focused_element()
        if "Text" not in el.patterns:
            print("Error in function find_target: focused element does not have text pattern")
            return None
        text_range = el.text_pattern.selection[0].clone()
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
                text_range.move_endpoint_by_range("End","Start",target = r.clone())
            else:
                text_range.move_endpoint_by_range("Start","End",target = r.clone())
            r = text_range.find_text(precise_trg,backward = back)            
            r.select()
        return r
    else:
        print("Target not found :(")
        return None

def get_scope(scope_dir: str = "DOWN",
                scope_unit: str = "Line",
                scope_unit_count: int = 15):
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
    if "Text2" in el.patterns:
        cur_range = el.text_pattern2.selection[0].clone()
    else:
        cur_range = el.text_pattern.selection[0].clone()
    # avoid selecting anything in current selection
    if scope_dir.upper() == "UP":
        cur_range.move_endpoint_by_range("End","Start",target = cur_range.clone())
    if scope_dir.upper() == "DOWN":
        cur_range.move_endpoint_by_range("Start","End",target = cur_range.clone())
    if scope_dir.upper() != "UP":
        cur_range.move_endpoint_by_unit("End",scope_unit,scope_unit_count)
    if scope_dir.upper() != "DOWN":
        cur_range.move_endpoint_by_unit("Start",scope_unit,-1*scope_unit_count)
    return cur_range

@mod.action_class
class Actions:
    def select_text(target: re.Pattern, scope_dir: str = "DOWN", ordinal: int = 1):
        """Selects text using windows accessibility pattern if possible"""
        print(f'scope_dir: {scope_dir}')
        el = ui.focused_element()
        if "Text" in el.patterns:
            try:
                r = find_target(target,get_scope(scope_dir),search_dir = scope_dir,ordinal = ordinal)
                if r != None:
                    r.select()
            except:
                actions.user.navigation("SELECT",scope_dir,"DEFAULT","default",target,1)
        else:
            actions.user.navigation("SELECT",scope_dir,"DEFAULT","default",target,1)

    def go_text(trg: re.Pattern, scope_dir: str, before_or_after: str, ordinal: int = 1):
        """Navigates to text using windows accessibility pattern if possible"""
        el = ui.focused_element()
        if "Text" in el.patterns:
            try:
                r = find_target(trg,get_scope(scope_dir),search_dir = scope_dir,ordinal = ordinal)
                if r != None:
                    src_pos = "End" if before_or_after.upper() == "BEFORE" else "Start"
                    trg_pos = "Start" if before_or_after.upper() == "BEFORE" else "End"
                    r.move_endpoint_by_range(src_pos,trg_pos,target = r.clone())
                    r.select()
            except:
                actions.user.navigation("GO",scope_dir,"DEFAULT",before_or_after,trg,ordinal)
        else:
        	actions.user.navigation("GO",scope_dir,"DEFAULT",before_or_after,trg,ordinal)

    def extend_selection(trg: re.Pattern,
                        scope_dir: str,
                        before_or_after: str,
                        ordinal: int = 1):
        """Extend currently selected text using windows accessibility pattern if possible"""
        el = ui.focused_element()
        if "Text" in el.patterns:
            try:
                cur_range = el.text_pattern.selection[0].clone()
                r = find_target(trg,get_scope(scope_dir),search_dir = scope_dir,ordinal = ordinal)
                if r != None:
                    src_pos = "Start" if scope_dir.upper() == "UP" else "End"
                    trg_pos = "Start" if before_or_after.upper() == "BEFORE" else "End"
                    cur_range.move_endpoint_by_range(src_pos,trg_pos,target = r.clone())
                    cur_range.select()
            except:
                actions.user.navigation("EXTEND",scope_dir,"DEFAULT",before_or_after,trg,ordinal)
        else:
            actions.user.navigation("EXTEND",scope_dir,"DEFAULT",before_or_after,trg,ordinal)

    def move_by_unit(unit: str, scope_dir: str, ordinal: int = 1):
        """Moves the cursor by the selected number of units"""
        el = ui.focused_element()
        if "Text" in el.patterns:
            cur_range = el.text_pattern.selection[0].clone()
            ordinal = -ordinal if scope_dir.upper() == "UP" else ordinal
            cur_range.move(unit,ordinal)
            
            cur_range.select()
            cur_range.scroll_into_view(True)
            

    def select_unit(unit: str):
        """Selects the enclosing unit around the current cursor position"""
        el = ui.focused_element() 
        if "Text" in el.patterns:
            cur_range = el.text_pattern.selection[0].clone()
            cur_range.expand_to_enclosing_unit(unit)
            cur_range.select()
        else:
            actions.user.edit_command("select", unit)
                
    def test_backward_search():
        """for debugging"""
        el = ui.focused_element()
        cur_range = el.text_pattern.selection[0].clone()
        r = cur_range.find_text("distance",backward = True)
        r.select()
    def test_forward_search():
        """for debugging"""
        el = ui.focused_element()
        cur_range = el.text_pattern.selection[0].clone()
        r = cur_range.find_text("distance",backward = False)
        r.select()