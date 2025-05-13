from talon.windows import ax as ax,ui as winui
from talon import app, Context,Module,actions,ctrl,ui,settings,clip
import re
import itertools

ax_units = ["Character","Format","Word","Line","Paragraph","Page","Document"]

mod = Module()

mod.setting("win_selection_distance",type = int,default = 20,
            desc = "Number of lines to search forward or backwards")

mod.list("text_search_direction","directions from cursor in which text can be searched")
mod.list("text_search_unit","units of text that can be searched for in windows accessibility")
mod.list("win_dynamic_nav_target")
mod.list("win_fwd_dyn_nav_trg")
mod.list("win_bkwd_dyn_nav_trg")
mod.list("text_special_pattern","patterns to search for with text selection")

def precise_target_and_position(target: re.Pattern, 
                text_range: ax.TextRange,
                search_dir: str = "DOWN",
                ordinal: int = 1):
    """HELPER FUNCTION FOR find_target; Searches for target in text_range"""
    # Returns a tuple of (str,int) representing the precise match 
    # and the ordinal rank of that precise match from the beginning, 
    # so that we can transfer information from the regex match 
    # to the windows accessibility TextRange.find_text function
    
    # handle homophones, single quotes 
    # incoming target should have regular straight quotes
    t = modify_regex_include_homophones(target.pattern)
    t = re.sub(r"'","[’']",t)
    target = re.compile(t, re.IGNORECASE)
    # find all instances of the target within the text range text
    t = text_range.text
    m = re.findall(target,t)
    if m and len(m) >= ordinal:
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
        return (precise_trg,precise_ordinal)
    else:
        return (None,None)
def find_target(trg: re.Pattern, 
                text_range: ax.TextRange = None,
                search_dir: str = "DOWN",
                ordinal: int = 1) -> ax.TextRange:
    """Searches for the target in the text range.
        Will handle straight versus curly single quotes and homophones.
        Returns a ax.TextRange object or None"""
    # Handle case of no TextRange input
    if text_range is None:
        el = winui.focused_element()
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
                scope_unit: str = "Line"):
    """Returns a text range corresponding to the search scope"""
    print(f"get_scope - win_selection_distance: {settings.get('user.win_selection_distance')}")
    # Error Checking
    if scope_unit not in ax_units:
        print("Error in function get_scope: scope_unit not valid")
        return 
    el = winui.focused_element()
    if "Text" not in el.patterns:
        print("Error in function get_scope: focused element does not have text pattern")
        return 
    # Get scope as a text range
    cur_range = el.text_pattern.selection[0]
    print(f"selection_distance: {settings.get('user.win_selection_distance')}")
    # avoid selecting anything in current selection#
    if scope_dir.upper() == "UP":
        cur_range.move_endpoint_by_range("End","Start",target = cur_range)
    if scope_dir.upper() == "DOWN":
        cur_range.move_endpoint_by_range("Start","End",target = cur_range)
    if scope_dir.upper() != "UP":
        cur_range.move_endpoint_by_unit("End",scope_unit,settings.get("user.win_selection_distance"))
    if scope_dir.upper() != "DOWN":
        cur_range.move_endpoint_by_unit("Start",scope_unit,-1*settings.get("user.win_selection_distance"))
    return cur_range
def process_selection(processing_function,trg: str, scope_dir: str = "DOWN", ordinal: int = 1):
    """Performs function on selected text and then returns cursor to original position"""
    # get textRange so we can return cursor to original position
    el = winui.focused_element()
    init_range = None
    if "Text2" in el.patterns:
        init_range = el.text_pattern2.selection[0]
    if "Text" in el.patterns:
        init_range = el.text_pattern.selection[0]
    # find target
    t = actions.user.winax_select_text(trg,scope_dir,ordinal)
    # perform processing function
    processing_function(t.text)
    # return to original selection
    if init_range != None:
        actions.sleep(0.1)
        init_range.select()
def scroll_to_selection(r,init_rect = None):
    """Scrolls to the input text range"""
    # Attempt to scroll into view
    # Would like to make it so that the selected items grows to the center of the screen
    # but so far attempts to do that have failed to work consistently
    # hmm... seems like scroll into view only works going down...
    try:
        actions.sleep(0.1)
        r.scroll_into_view(align_to_top = True)
    except Exception as error:
        print(f"FUNCTION: scroll_to_selection\n{error}") # some apps or windows versions don't have bounding rectangles yet?
def modify_regex_include_homophones(t: str):
    word_list = re.findall(r"\w+",t)
    word_list = set(word_list)
    for w in word_list:
        phone_list = actions.user.homophones_get(w)
        if phone_list:
            t = t.replace(w,"(?:" + '|'.join(phone_list) + ")")
    # accommodate formatting by allowing non-letter characters between words
    t = t.replace(" ","[^a-z|A-Z]*")
    return t

ctx = Context()

@ctx.dynamic_list("user.win_dynamic_nav_target")
def win_dynamic_nav_target(_) -> str:
    el = actions.user.focused_element()
    if el:
        if "Text" in el.patterns:
            cur_range = get_scope("both","Line",15)
            return f"""
            {cur_range.text}
            """

@ctx.dynamic_list("user.win_fwd_dyn_nav_trg")
def win_fwd_dyn_nav_trg(_) -> str:
    el = actions.user.focused_element()
    if el:
        if "Text" in el.patterns:
            cur_range = get_scope("DOWN","Line")
            t = re.sub(r"[^A-Za-z'’]+", ' ', cur_range.text)
            t = re.sub(r"’","'",t)
            return f"""
            {t}
            """

@ctx.dynamic_list("user.win_bkwd_dyn_nav_trg")
def win_bkwd_dyn_nav_trg(_) -> str:
    print("FUNCTION: backwards dynamic navigation target")
    el = actions.user.focused_element()
    if el:
        if "Text" in el.patterns:
            cur_range = get_scope("UP","Line")
            t = re.sub(r"[^A-Za-z'’]+", ' ', cur_range.text)
            t = re.sub(r"’","'",t)
            return f"""
            {t}
            """

def process_text_capture(m) -> (str,bool):
    """Takes either a navigation target or spoken output capture
        and returns tuple of 
        (text without homophone processing, bool=homophones_allowed)"""
    include_homophones = False
    if hasattr(m,"any_alphanumeric_key"):
        t = re.compile(re.escape(m.any_alphanumeric_key), re.IGNORECASE).pattern
    if hasattr(m,"delimiter_pair"):
        t = "\\" + m.delimiter_pair.replace(" ",".*?\\")
    if hasattr(m,"navigation_target_name"):
        t = re.compile(m.navigation_target_name)
    if hasattr(m,"abbreviation"):
        t = m.abbreviation
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
    if hasattr(m,"variable"):
        t = m.variable
    if hasattr(m,"person"):
        t = m.person
    if hasattr(m,"student"):
        t = m.student
    if hasattr(m,"place"):
        t = m.place
    if hasattr(m,"module"):
        t = m.module
    if hasattr(m,"function"):
        t = m.function
    if hasattr(m,"keyword"):
        t = m.keyword
    if hasattr(m,"app"):
        t = m.app
    if hasattr(m,"font"):
        t = m.font
    if hasattr(m,"prose_formatter"):
        t = actions.user.formatted_text(m.prose,m.prose_formatter)
        # later should change this to True to allow for searching by
        # formatter, but that will probably entail returning the formatter
        # to be processed by the final function into a regex expression
        # that distinguishes the same set of words formatted in different ways
        include_homophones = False
    return (t,include_homophones)        
        
# This capture rule should match win_nav_target exactly for
# spoken form consistency; the only difference
# is that this should return text to paste into a document, 
# rather than text to search for. So no Regular Expressions.
@mod.capture(rule="[(letter|character)] <user.any_alphanumeric_key> | {user.delimiter_pair} | (abbreviate|abbreviation|brief) {user.abbreviation} | number <user.real_number> | word <user.word> | phrase <user.text> | variable {user.variable} | person [name] {user.person} | student [name] {user.student} | place [name] {user.place} | module [name] {user.module} | function [name] {user.function} | keyword {user.keyword} | app [name] {user.app} | font [name] {user.font} | {user.prose_formatter} <user.prose>")
def constructed_text(m) -> str:
    """Output of spoken text construction for windows text selection"""
    t, include_homophones = process_text_capture(m)
    return t
        
        
# Note: the windows dynamic navigation target will take precedence
# over the following capture, according to observed behavior 
# (not sure if this is guaranteed). So if a windows accessibility text element is in focus and there is both the word comma and a comma punctuation mark, the word will be selected.
@mod.capture(rule="[(letter|character)] <user.any_alphanumeric_key> | {user.delimiter_pair} | (abbreviate|abbreviation|brief) {user.abbreviation} | number <user.real_number> | word <user.word> | phrase <user.text> | variable {user.variable} | person [name] {user.person} | student [name] {user.student} | place [name] {user.place} | module [name] {user.module} | function [name] {user.function} | keyword {user.keyword} | app [name] {user.app} | font [name] {user.font}")
def win_nav_target(m) -> str:
    """A target to navigate to. Returns a regular expression."""
    t, include_homophones = process_text_capture(m)
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
    def winax_select_text(trg: str, scope_dir: str = "DOWN", ordinal: int = 1):
        """Selects text using windows accessibility pattern if possible"""
        trg = re.compile(trg.replace(" ",".{,3}"), re.IGNORECASE)
        el = winui.focused_element()
        if "Text" in el.patterns:
            try:
                r = find_target(trg,get_scope(scope_dir),search_dir = scope_dir,ordinal = ordinal)
                if r != None:
                    r.select()
                    scroll_to_selection(r)
                    return r
            except:
                actions.user.navigation("SELECT",scope_dir,"DEFAULT","default",trg,1)
        else:
            actions.user.navigation("SELECT",scope_dir,"DEFAULT","default",trg,1)
    def winax_replace_text(new_text: str, trg: str, scope_dir: str = "DOWN", ordinal: int = 1):
        """Replaces target with the new text"""
        def replace_process(orig_text):
            with clip.revert():
                clip.set_text(new_text)
                actions.sleep(0.2)
                actions.edit.paste()
                actions.sleep(0.15)
        process_selection(replace_process,trg,scope_dir,ordinal)
    def winax_format_text(fmt: str, trg: str, scope_dir: str = "DOWN", ordinal: int = 1):
        """Applies formatter to targeted text"""
        def format_process(orig_text: str):
            t = actions.user.formatted_text(orig_text,fmt)
            with clip.revert():
                clip.set_text(t)
                actions.sleep(0.15)
                actions.edit.paste()
                actions.sleep(0.15)
        process_selection(format_process,trg,scope_dir,ordinal)
    def winax_phones_text(trg: str, scope_dir: str = "DOWN", ordinal: int = 1):
        """Performs homophone conversion on targeted text"""
        def phones_process(orig_text):
            # perform homophones operation
            w = actions.edit.selected_text()
            w = orig_text
            options = actions.user.homophones_get(w)
            lower_options = [x.lower() for x in options]
            i = lower_options.index(w.lower())
            i = (i + 1) % len(options)
            x = options[i]
            # would be nice to match case with the original selected text here
            with clip.revert():
                clip.set_text(x)
                actions.sleep(0.15)
                actions.edit.paste()
                actions.sleep(0.15)
        process_selection(phones_process,trg,scope_dir,ordinal)
    def winax_go_text(trg: str, scope_dir: str, before_or_after: str, ordinal: int = 1):
        """Navigates to text using windows accessibility pattern if possible"""
        trg = re.compile(trg, re.IGNORECASE)
        el = winui.focused_element()
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
    def winax_extend_selection(trg: str, scope_dir: str, before_or_after: str, ordinal: int = 1):
        """Extend currently selected text using windows accessibility pattern if possible"""
        trg = re.compile(trg, re.IGNORECASE)
        el = winui.focused_element()
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
    def winax_move_by_unit(unit: str, scope_dir: str, ordinal: int = 1):
        """Moves the cursor by the selected number of units"""
        el = winui.focused_element()
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
    def winax_extend_by_unit(unit: str, scope_dir: str, ordinal: int = 1):
        """Extends the selection to the end/beginning of next unit"""
        el = winui.focused_element()
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
    def winax_expand_selection(left: bool = True, right: bool = True, 
            unit: str = "Character", ordinal: int = 1):
        """Expands selection in the specified direction(s)"""
        el = winui.focused_element()
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
    def winax_select_unit(unit: str):
        """Selects the enclosing unit around the current cursor position"""
        el = winui.focused_element() 
        if "Text" in el.patterns:
            cur_range = el.text_pattern.selection[0]
            cur_range.expand_to_enclosing_unit(unit)
            cur_range.select()
        else:
            # need to handle these individually because community edit commands
            # use classes that I don't know how to access
            if unit == "Line":
                # 
                actions.edit.line_start()
                actions.edit.extend_line_end()
            elif unit == "Word":
                print("selecting word...")
                actions.edit.word_left()
                actions.edit.extend_word_right()
            elif unit == "Paragraph":
                actions.edit.extend_paragraph_start()
                actions.edit.extend_paragraph_end()
    def winax_set_selection_distance(d: int):
        """Allows user to change selection distance with a command"""
        if d > 0:
            ctx.settings["user.win_selection_distance"] = d
