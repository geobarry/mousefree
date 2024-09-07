from talon.windows import ax as ax,ui as winui
from talon import app, Context,Module,actions, ctrl,ui
from enum import Enum

ax_dir_options = ["NEXT","PREVIOUS","ANY"]
ax_unit_options = ["Character","Format","Word","Line","Paragraph","Page","Document"]

mod = Module()

mod.list("text_search_direction","directions from cursor in which text can be searched")

@mod.action_class
class Actions:
    def find_target(target_regex: str, 
                    scope_dir: str = "ANY",
                    scope_unit: str = "Line",
                    scope_unit_count: int = 7):
        """Returns a text range corresponding to the given target"""
        print(f'scope_dir: {scope_dir}')
        print(f'scope_unit: {scope_unit}')
        # Error Checking
        if scope_dir not in ax_dir_options:
            print("Error in function find_target: scope_dir not in ax_dir_options")
            return 
        if scope_unit not in ax_unit_options:
            print("Error in function find_target: scope_unit not in ax_unit_options")
            return 
        el = ui.focused_element()
        if "Text" not in el.patterns:
            print("Error in function find_target: focused element does not have text pattern")
            return 
        # Get scope as a text range
        cur_range = el.text_pattern.selection[0].clone()
        cur_range.expand_to_enclosing_unit(scope_unit)
        cur_range.move_endpoint_by_unit("End",scope_unit,scope_unit_count)
        cur_range.move_endpoint_by_unit("Start",scope_unit,-1*scope_unit_count)
        # get rid of this later once everything is working:
        cur_range.select()
