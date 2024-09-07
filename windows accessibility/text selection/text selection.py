from talon.windows import ax as ax,ui as winui
from talon import app, Context,Module,actions, ctrl,ui
import re

ax_dir_options = ["NEXT","PREVIOUS","ANY"]
ax_unit_options = ["Character","Format","Word","Line","Paragraph","Page","Document"]

mod = Module()


def find_target(target: re.Pattern, 
                text_range: ax.TextRange = None) -> ax.TextRange:
    """Searches for the target"""
    print("FUNCTION: find_target")
    if text_range is None:
        el = ui.focused_element()
        if "Text" not in el.patterns:
            print("Error in function find_target: focused element does not have text pattern")
            return 
        # Get scope as a text range
        text_range = el.text_pattern.selection[0].clone()
    # find target within the text range text
    t = text_range.text
    m = re.search(target,t)
    if m:
        print("Target found:")
        print(m.group(0))
        print(m.groups())
        r = text_range.find_text(m.group(0))
        return r
    else:
        print("Target not found :(")
        return None
def get_scope(scope_dir: str = "ANY",
                scope_unit: str = "Line",
                scope_unit_count: int = 7):
    """Returns a text range corresponding to the search scope"""
    print(f'scope_dir: {scope_dir}')
    print(f'scope_unit: {scope_unit}')
    # Error Checking
    if scope_dir not in ax_dir_options:
        print("Error in function get_scope: scope_dir not in ax_dir_options")
        return 
    if scope_unit not in ax_unit_options:
        print("Error in function get_scope: scope_unit not in ax_unit_options")
        return 
    el = ui.focused_element()
    if "Text" not in el.patterns:
        print("Error in function get_scope: focused element does not have text pattern")
        return 
    # Get scope as a text range
    cur_range = el.text_pattern.selection[0].clone()
    cur_range.expand_to_enclosing_unit(scope_unit)
    cur_range.move_endpoint_by_unit("End",scope_unit,scope_unit_count)
    cur_range.move_endpoint_by_unit("Start",scope_unit,-1*scope_unit_count)
    # get rid of this later once everything is working:
#    cur_range.select()

    return cur_range


@mod.action_class
class Actions:
    def ax_test(target: re.Pattern):
        """test"""
        r = find_target(target,get_scope())
        r.select()
