from talon import Module, Context, actions, ui
from talon.windows import ax as ax
import re

mod = Module()

@mod.action_class
class Actions:
    def app_switch_by_title(title_regex: str):
        """Switches to an app with the given regular expression in the title"""
        print(f'title_regex: {title_regex}')
        title_regex = re.compile(title_regex,re.IGNORECASE)
        win_list = ui.windows()
        win_list = [w for w in win_list if not w.hidden]
        [print(f"{w.title} enabled: {w.enabled} hidden: {w.hidden}") for w in win_list if w.title]
        win_list = [w for w in win_list if re.match(title_regex,w.title) != None]
        print(f'win_list: {win_list}')
        if len(win_list) > 0:
            # for now choose the first window
            w = win_list[0]
            print(f"changing focus to {w.title}")
            w.focus()
    def focus_explorer():
        """Opens the correct windows explorer window"""
        print("debugging user.focus_explorer")
        explorer_list = ui.apps(name="Windows Explorer")
        print(len(explorer_list))
        for explorer in explorer_list:
            win_list = [w for w in explorer.windows() if w.cls == "CabinetWClass" or w.cls == "ExplorerWClass"]
            if len(win_list) > 0:
                w = next(window for window in explorer.windows() if window.cls == "CabinetWClass" or window.cls == "ExplorerWClass")
                w.focus()            
    def focus_outlook():
        """Opens the first Outlook window that is not a dialog"""
        outlook_list = ui.apps(name="Microsoft Outlook")
        if len(outlook_list) > 0:
            outlook = outlook_list[0]
            # narrow down to windows that are not hidden
            win_list = [w for w in outlook.windows() if not w.hidden]
            # exclude dialogs - this is painful because getting something from the dialog directly causes accessibility to hang
            # so we have to start from the focused element and move upwards
            r = win_list
            prop_list = [("printout","dialog")]
            if len(r) > 0:
                trg = r[0]
                trg.focus()        
                actions.sleep(1)
                el = actions.user.safe_focused_element()
                try_number = 0
                if not actions.user.element_match(el,prop_list) and try_number < 5:
                    trg = r[try_number + 1]
                    trg.focus()
                    el = actions.user.safe_focused_element()
                    try_number += 1

ctx = Context()
