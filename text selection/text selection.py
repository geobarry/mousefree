from talon.windows import ax as ax
from talon import app, Context,Module,actions,ctrl,ui,settings,clip
import re
import itertools

ax_units = ["Character","Format","Word","Line","Paragraph","Page","Document"]

mod = Module()

mod.setting("win_selection_distance",type = int,default = 20,
            desc = "Number of lines to search forward or backwards")
mod.setting("winax_text",type = bool,default = True,
            desc = "Whether or not to use accessibility text selection functions. If False, will use default text selection functions even if accessibility text pattern is present.")

mod.list("search_dir","directions from cursor in which text can be searched")
mod.list("text_search_unit","units of text that can be searched for in windows accessibility")
mod.list("win_next_dyn_nav_trg")
mod.list("win_previous_dyn_nav_trg")
mod.list("win_inside_dyn_nav_trg")
mod.list("win_any_dyn_nav_trg")
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
    if not text_range:
        return 
    t = modify_regex_include_homophones(target.pattern)
    t = re.sub(r"'","[’']",t)
    print(f't: {t}')
    target = re.compile(t, re.IGNORECASE)
    # find all instances of the target within the text range text
    if actions.user.wait_for_access():
        actions.user.set_winax_retrieving(True)
        try:
            t = text_range.text
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
                return (precise_trg,precise_ordinal)
        except Exception as error:
            print(f"TEXT SELECTION PRECISE TARGET AND POSITION error:\n{error}")
            return (None,None)
        finally:
            actions.user.set_winax_retrieving(False)
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
        el = actions.user.safe_focused_element()
        if el:
            pattern_list = actions.user.el_prop_val(el,'patterns')
            if pattern_list:
                if "Text" not in pattern_list:
                    print("Error in function find_target: focused element does not have text pattern")
                    return None
                text_range = actions.user.el_prop_val(el,'text_selection')
    if text_range:
        # Use regex to find exact match text and its position
        precise_trg,precise_ordinal = precise_target_and_position(trg,text_range,search_dir,ordinal)
        if precise_trg != None:
            # Iteratively search for precise target using windows accessibility
            back = search_dir.upper() == "UP"
            r = actions.user.safe_access(lambda: text_range.find_text(precise_trg,backward = back),"FIND_TARGET (a)")
            if r:
                while precise_ordinal > 1:
                    # iterate to find next instance
                    precise_ordinal -= 1
                    # eliminate portion of text range up to and including previous instance
                    if search_dir.upper() == "UP":
                        actions.user.safe_access(lambda: text_range.move_endpoint_by_range("End","Start",target = r),"FIND_TARGET (b)")
                    else:
                        actions.user.safe_access(lambda: text_range.move_endpoint_by_range("Start","End",target = r),"FIND_TARGET (c)")
                    r = actions.user.safe_access(lambda: text_range.find_text(precise_trg,backward = back)            , "FIND_TARGET (d)")
                return r
        else:
            print("Target not found :(")
            return None
def get_scope(scope_dir: str = "DOWN", scope_unit: str = "Line", verbose: bool = False):
    """Returns a text range corresponding to the search scope. Valid scope directions include UP,DOWN,BOTH,INSIDE"""
    if verbose:
        print(f"get_scope - win_selection_distance: {settings.get('user.win_selection_distance')}")
    # Error Checking
    if scope_unit not in ax_units:
        print("Error in function get_scope: scope_unit not valid")
        return 
    el = actions.user.safe_focused_element()
    if el:
        cur_range = actions.user.el_prop_val(el,'text_selection')
        if cur_range:
            if scope_dir.upper() == "UP":
                # go to beginning of current selection
                actions.user.safe_access(lambda:cur_range.move_endpoint_by_range("End","Start",target = cur_range),"GET_SCOPE (a)")
                # extend up
                d = -1*settings.get("user.win_selection_distance")
                actions.user.safe_access(lambda: cur_range.move_endpoint_by_unit("Start",scope_unit,d),"GET_SCOPE (b)")
            elif scope_dir.upper() == "DOWN":
                # go to end of current selection
                actions.user.safe_access(lambda: cur_range.move_endpoint_by_range("Start","End",target = cur_range),"GET_SCOPE (c)")
                # extend down
                actions.user.safe_access(lambda: cur_range.move_endpoint_by_unit("End",scope_unit,settings.get("user.win_selection_distance")),"GET_SCOPE(d)")
            elif scope_dir.upper() == "BOTH":
                # extend down
                actions.user.safe_access(lambda: cur_range.move_endpoint_by_unit("End",scope_unit,settings.get("user.win_selection_distance")),"GET_SCOPE(d)")
                # extend up
                d = -1*settings.get("user.win_selection_distance")
                actions.user.safe_access(lambda: cur_range.move_endpoint_by_unit("Start",scope_unit,d),"GET_SCOPE (b)")
            elif scope_dir.upper() == "INSIDE":
                # do nothing
                pass
            if verbose:
                print(f'FUNCTION get_scope return range text:\n{cur_range.text}')
            return cur_range

def process_selection(processing_function,trg: str, scope_dir: str = "DOWN", ordinal: int = 1):
    """Performs function on selected text and then returns cursor to original position"""
    print(f"PROCESS_SELECTION trg: {trg}")
    # get textRange so we can return cursor to original position
    el = actions.user.safe_focused_element()
    if el:
        init_range = actions.user.el_prop_val(el,'text_selection')
        # perform selection
        t = actions.user.winax_select_text(trg,scope_dir,ordinal)        
        # perform processing function
        if t:
            processing_function(t)
        # return to original selection
        if init_range != None:
            actions.sleep(0.2)
            actions.user.safe_access(lambda: init_range.select(),"PROCESS_SELECTION")

def scroll_to_selection(r,init_rect = None):
    """Scrolls to the input text range"""
    # ********************************
    # RESUME ACCESSIBILITY ERROR PROOFING HERE
    # ********************************
    
    # Attempt to scroll into view
    # Would like to make it so that the selected items goes to the center of the screen
    # but so far attempts to do that have failed to work consistently
    # hmm... seems like scroll into view only works going down...
    actions.user.safe_access(lambda: r.scroll_into_view(align_to_top = True), "SCROLL_TO_SELECTION")
def modify_regex_include_homophones(t: str):
    word_list = re.findall(r"\w+",t)
    word_list = set(word_list)
    for w in word_list:
        phone_list = actions.user.homophones_get(w)
        if phone_list:
            phone_list = sorted(phone_list,key = lambda x: len(x))
            phone_list.reverse()
            t = t.replace(w,"(?:" + '|'.join(phone_list) + ")")
    # accommodate formatting by allowing non-letter characters between words
    t = t.replace(" ","[^a-z|A-Z]*")
    return t

ctx = Context()

def win_dyn_nav_trg(search_dir: str) -> str:
    use_winax = settings.get("user.winax_text")
    if use_winax:
        el = actions.user.safe_focused_element()
        if el:
            pattern_list = actions.user.el_prop_val(el,'patterns')
            if "Text" in pattern_list:
                cur_range = get_scope(search_dir,"Line")
                txt = actions.user.safe_access(lambda: cur_range.text, "WIN_NEXT_DYN_NAV_TRG")
                t = re.sub(r"[^A-Za-z'’]+", ' ', txt)
                t = re.sub(r"’","'",t)
                print(f'dynamic t: {t}')
                return f"""
                {t}
                """

@ctx.dynamic_list("user.win_next_dyn_nav_trg")
def win_next_dyn_nav_trg(_) -> str:
    return win_dyn_nav_trg("DOWN")

@ctx.dynamic_list("user.win_previous_dyn_nav_trg")
def win_previous_dyn_nav_trg(_) -> str:
    return win_dyn_nav_trg("UP")

@ctx.dynamic_list("user.win_inside_dyn_nav_trg")
def win_inside_dyn_nav_trg(_) -> str:
    return win_dyn_nav_trg("INSIDE")

@ctx.dynamic_list("user.win_any_dyn_nav_trg")
def win_any_dyn_nav_trg(_) -> str:
    return win_dyn_nav_trg("BOTH")


@mod.capture(rule="word <user.word> | phrase <user.text> | <user.formatters> <user.prose>")
def direct_text(m) -> str:
    """Constructs text for inserting, without any regex"""
    if hasattr(m,"word"):
        t = m.word
    elif hasattr(m,"text"):
        t = m.text
    elif hasattr(m,"formatters"):
        t = actions.user.formatted_text(m.prose,m.formatters)
    return t

@mod.capture(rule="<user.direct_text>")
def phony_text(m) -> str:
    """Creates a navigation target including homophone options"""
    t = m.direct_text
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

@mod.capture(rule="[(letter|character)] <user.any_alphanumeric_key> | {user.delimiter_pair} | (abbreviate|abbreviation|brief) {user.abbreviation} | number <user.real_number> | variable <user.extended_variable> | person [name] {user.person} | student [name] {user.student} | place [name] {user.place} | module [name] {user.module} | function [name] {user.function} | keyword {user.keyword} | app [name] {user.app} | font [name] {user.font}")
def coded_text(m) -> str:
    """Creates text from letters, characters, numbers or other user defined spoken forms. From 'variable' onwards are personal lists and captures that I have made that are not public. So you can remove these or else create your own lists/captures with the same name."""
    if hasattr(m,"real_number"):
        x = int(m.real_number)
        y = float(m.real_number)
        t = str(x) if x == y else str(y)
    else:
        cls_list = ["any_alphanumeric_key","delimiter_pair","abbreviation","real_number","extended_variable","person","student","place","module","function","keyword","app","font"]
        for cls in cls_list:
            if hasattr(m,cls):
                t = getattr(m,cls)
                break
    return t

@mod.capture(rule = "<user.direct_text>|<user.coded_text>")
def constructed_text(m) -> str:
    """Text to be inserted"""
    return str(m)

@mod.capture(rule = "<user.phony_text>|<user.coded_text>")
def win_nav_target(m) -> str:
    """text to be searched for, including regex for disambiguation"""
    if hasattr(m,"phony_text"):
        return str(m)
    else:
        t = str(m)
        if t in ["()","{}","[]","<>","''",'""']:
            return f"{t[0]}.*{t[1]}"
        else:
            return re.escape(t)
    
@mod.action_class
class Actions:
    def winax_select_text(trg: str, scope_dir: str = "DOWN", ordinal: int = 1):
        """Selects text using windows accessibility pattern if possible, and returns the selected text"""
        print(f"WINAX_SELECT_TEXT trg: {trg}")
        regex = re.compile(trg.replace(" ",".{,3}"), re.IGNORECASE)
        use_winax = settings.get("user.winax_text")
        print(f'use_winax: {use_winax}')
        if use_winax:
            el = actions.user.safe_focused_element()
            if el:
                if "Text" in el.patterns:
                    try:
                        r = find_target(regex,get_scope(scope_dir),search_dir = scope_dir,ordinal = ordinal)
                        if r != None:
                            r.select()
                            scroll_to_selection(r)
                            return r.text
                    except Exception as error:
                        print(f'error: {error}')
                        actions.user.navigation("SELECT",scope_dir,"DEFAULT","default",regex,1)
                else:
                    print("No text pattern")
                    use_winax = False
        if not use_winax:
            txt = actions.user.navigation("SELECT",scope_dir,"DEFAULT","default",regex,1)
            print(f'WINAX_SELECT_TEXT txt: {txt}')
            if txt:
                actions.user.slide_selection_to_match(txt)
                r = actions.edit.selected_text()
                return r
    def winax_replace_text(new_text: str, trg: str, scope_dir: str = "DOWN", ordinal: int = 1):
        """Replaces target with the new text"""
        def replace_process(orig_text):
            with clip.revert():
                actions.sleep(0.2)
                if new_text == "":
                    actions.key("backspace")
                else:
                    clip.set_text(new_text)
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
        print(f"WINAX_FORMAT_TEXT trg: {trg}")
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
        """Navigates to text using windows accessibility pattern, returns True if successful"""
        trg = re.compile(trg, re.IGNORECASE)
        use_winax = settings.get("user.winax_text")
        if use_winax:
            el = actions.user.safe_focused_element()
            pattern_list = actions.user.el_prop_val(el,'patterns')
            if "Text" in pattern_list:
                try:
                    pattern = actions.user.el_pattern(el,"text")
                    if pattern:
                        cur_range = actions.user.safe_access(lambda: pattern.selection[0],"WINAX_GO_TEXT (a)")
                        if cur_range:
                            # for automatic scrolling; should be moved to separate function for other operations
                            init_rect = None
                            trg_rect = None
                            init_rect = actions.user.safe_access(lambda: cur_range.bounding_rectangles[0], "WINAX_GO_TEXT (b)")
                            if init_rect:
                                r = find_target(trg,get_scope(scope_dir),search_dir = scope_dir,ordinal = ordinal)
                                if r != None:
                                    src_pos = "End" if before_or_after.upper() == "BEFORE" else "Start"
                                    trg_pos = "Start" if before_or_after.upper() == "BEFORE" else "End"
                                    actions.user.safe_access(lambda: r.move_endpoint_by_range(src_pos,trg_pos,target = r),"WINAX_GO_TEXT (c)")
                                    actions.user.safe_access(lambda: r.select(),"WINAX_GO_TEXT (d)")
                                    scroll_to_selection(r,init_rect)
                                    return True
                except:
                    print("unhandled exception in windows accessibility text selection; reverting to old method")
                    actions.user.navigation("GO",scope_dir,"DEFAULT",before_or_after,trg,ordinal)               
            else:
                use_winax = False
        if not use_winax:
            txt = actions.user.navigation("SELECT",scope_dir,"DEFAULT","default",trg,ordinal)
            if txt:
                actions.user.slide_selection_to_match(txt)
                if before_or_after.lower() == "before":
                    actions.key("left")
                else:
                    actions.key("right")
                return True
    def winax_extend_selection(trg: str, scope_dir: str, before_or_after: str, ordinal: int = 1):
        """Extend currently selected text using windows accessibility pattern if possible"""
        trg = re.compile(trg, re.IGNORECASE)
        use_winax = settings.get("user.winax_text")
        if use_winax:
            el = actions.user.safe_focused_element()
            if el:
                pattern_list = actions.user.el_prop_val(el,'patterns')
                if "Text" in pattern_list:
                    try:
                        cur_range = actions.user.safe_access(lambda: el.text_pattern.selection[0],"WINAX_EXTEND_SELECTION")
                        r = find_target(trg,get_scope(scope_dir),search_dir = scope_dir,ordinal = ordinal)
                        if r != None:
                            src_pos = "Start" if scope_dir.upper() == "UP" else "End"
                            trg_pos = "Start" if before_or_after.upper() == "BEFORE" else "End"
                            actions.user.safe_access(lambda: cur_range.move_endpoint_by_range(src_pos,trg_pos,target = r),"WINAX_EXTEND_SELECTION")
                            actions.user.safe_access(lambda: cur_range.select(),"WINAX EXTEND SELECTION")
                    except:
                        actions.user.navigation("EXTEND",scope_dir,"DEFAULT",before_or_after,trg,ordinal)
                else:
                    use_winax = False
        if not use_winax:
            actions.user.navigation("EXTEND",scope_dir,"DEFAULT",before_or_after,trg,ordinal)
    def winax_insert_text(txt: str,before_or_after: str,ordinals: int, scope_dir: str,trg: str):
        """inserts text before or after target"""
        success = actions.user.winax_go_text(trg,scope_dir,before_or_after,ordinals)
        if success:
            actions.insert(txt)
# *** stall-proofed up to here ***
    def winax_move_by_unit(unit: str, scope_dir: str, ordinal: int = 1):
        """Moves the cursor by the selected number of units"""
        el = actions.user.safe_focused_element()
        print(f'el: {el}')
        if el:
            pattern_list = actions.user.el_prop_val(el,"patterns")
            if pattern_list:
                if "Text" in pattern_list:
                    pattern = el.text_pattern
                    if pattern:
                        selection_list = pattern.selection
                        if selection_list:
                            if len(selection_list) > 0:
                                cur_range = selection_list[0]
                                if cur_range:
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
        el = actions.user.safe_focused_element()
        if el:
            pattern = el.patterns
            print(f'pattern: {pattern}')
            if "Text" in pattern:
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
                # scroll up or down depending on scope_dir
                print(f'scope_dir: {scope_dir}')
                # scroll_to_range
                scroll_to_range = cur_range.clone()
                print(f'scroll_to_range: {scroll_to_range}')
                if scope_dir == "DOWN":
                    scroll_to_range.move_endpoint_by_range("Start","End",target = scroll_to_range)
                    scroll_to_range.scroll_into_view(False)
                else:
                    scroll_to_range.move_endpoint_by_range("End","Start",target = scroll_to_range)
                    scroll_to_range.scroll_into_view(True)
                # scroll down a little to see the next text
                pattern = el.scroll_pattern
                if pattern:
                    print(f'pattern: {pattern}')
                    if pattern.vertically_scrollable:
                        print("attempting scroll...")
                        for i in range(10):
                            if scope_dir == "DOWN":
                                pattern.scroll(horizontal = "NoAmount",vertical = "SmallIncrement")
                            else:
                                pattern.scroll(horizontal = "NoAmount",vertical = "SmallDecrement")
    def winax_expand_selection(left: bool = True, right: bool = True, 
            unit: str = "Character", ordinal: int = 1):
        """Expands selection in the specified direction(s)"""
        print(f"FUNCTION winax_expand_selection: left: {left} | right: {right} | units: {unit} | ordinal: {ordinal}")
        el = actions.user.safe_focused_element()
        if el:
            pattern_list = actions.user.el_prop_val(el,"patterns")
            if "Text" in pattern_list:
                selection = el.text_pattern.selection
                if len(selection) > 0:
                    cur_range = selection[0]
                    print(f"selected text: {cur_range.text}")
                    if left:
                        cur_range.move_endpoint_by_unit("Start",unit,-1*ordinal)
                    if right:
                        cur_range.move_endpoint_by_unit("End",unit,ordinal)
                    cur_range.select()            
                    cur_range.scroll_into_view(True)
    def winax_peek(scope_dir: str = "DOWN", unit: str = "Character"):
        """returns the text to the left or right of the current selection"""
        el = actions.user.safe_focused_element()
        if el:
            pattern_list = actions.user.el_prop_val(el,"patterns")
            if "Text" in pattern_list:
                selection = el.text_pattern.selection
                if len(selection) > 0:
                    cur_range = selection[0]
                    print(f"selected text: {cur_range.text}")
                    cur_range = cur_range.clone()
                    if scope_dir == "DOWN":
                        cur_range.move_endpoint_by_range("Start","End",target = cur_range)
                        cur_range.move_endpoint_by_unit("End",unit,1)
                    else:
                        cur_range.move_endpoint_by_range("End","Start",target = cur_range)
                        cur_range.move_endpoint_by_unit("Start",unit,1)
                    txt = cur_range.text
                    print(f'txt: {txt}')
                    return txt
    def winax_expand_if(trg_val: str, scope_dir: str = "DOWN", unit: str = "Character"):
        """Expands the current selection if the expansion matches the expression"""
        expand_txt = actions.user.winax_peek(scope_dir,unit)
        trg_val = re.compile(f"^{trg_val}$")
        expand = re.match(trg_val,expand_txt) != None
        if expand:
            if scope_dir == "DOWN":
                actions.user.winax_expand_selection(left = False,right = True,unit = unit)
            else:
                actions.user.winax_expand_selection(left = True,right = False,unit = unit)            
    def winax_select_unit(unit: str):
        """Selects the enclosing unit around the current cursor position"""
        el = actions.user.safe_focused_element()
        if el:
            if "Text" in el.patterns:
                selection = el.text_pattern.selection
                if len(selection) > 0:
                    cur_range = selection[0]
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
# settings
    def winax_text(use_ax: bool = True):
        """If true, uses windows accessibility for text selection"""
        print(f"winax_text: {use_ax}")
        ctx.settings["user.winax_text"] = use_ax
        
    def winax_set_selection_distance(d: int):
        """Allows user to change selection distance with a command"""
        if d > 0:
            ctx.settings["user.win_selection_distance"] = d
