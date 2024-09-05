from talon.windows import ax as ax,ui as winui
from talon import app, Context,Module,actions, ctrl,ui
from enum import Enum

ax_dir_options = ["NEXT","PREVIOUS","ANY"]
ax_unit_options = ["Character","Format","Word","Line","Paragraph","Page","Document"]

@mod.action_class
class Actions:
    def find_target(target_regex: str, 
                    scope_dir: str = "NEXT",
                    scope_unit: str = "Line",
                    scope_unit_count: int = 15):
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
        