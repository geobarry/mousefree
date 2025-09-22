import os
from talon.windows import ax as ax, ui as winui
from talon import Context, Module, actions, app, ui
from talon.types import Rect as Rect

mod = Module()

ctx = Context()
ctx.matches = """
os: windows
"""


@mod.action_class
class Actions:
    def invoke_taskbar_item(item_name: str):
        """Invokes given taskbar item"""
        # Talon #958 seems to have a regression where the talon tray menu has no accessible elements
        # ISSUE: The act of accessing the Talon taskbar icon
        #          seems to make the icon disappear
        
        # possible states:
        # 1. In a normal application
        # 2. In a normal application, tray is open
        # 3. Tray show button is selected, Tray is closed
        # 4. Tray show button is selected, tray is open
        # 5. Tray normal button is selected
        # 6. Talon menu is open, nothing selected
        # 7. Talon menu item is selected
        # 8. We are in this weird nonexistent tray window

        # goal is to get talon button
        talon_btn = None
        talon_seq = [
            [("name",""),("class_name","Windows.UI.Input.InputSite.WindowClass")],
            [("name",item_name),("class_name","SystemTray.NormalButton")]
        ]
        app_btn_list = [("class_name","SystemTray.NormalButton"),("name",r"^(?!Show Hidden Icons).*$")]
        def super_b_for_taskbar():
            # pressing super-b sometimes hits the windows start button instead of the taskbar button
            # so we have to look for that
            tray_props = [("name","Show Hidden Icons.*"),("class_name","SystemTray.NormalButton")]
            start_btn_props = [("automation_id","StartButton")]
            prop_list = ["or",[tray_props,start_btn_props]]
            actions.key("super-b")
            el = actions.user.wait_for_element(prop_list,time_limit = 1)
            if el:
                if actions.user.element_match(el,start_btn_props):
                    # need to try again
                    actions.key("super-b")
                    el = actions.user.wait_for_element(tray_props)
            return el
        # handle easy ones first
        el = actions.user.safe_focused_element()
        if el:
            # 5 TRAY NORMAL BUTTON IS SELECTED
            if actions.user.element_match(el,app_btn_list):
                print("situation 5 confirmed")
                root = actions.user.window_root()
                talon_btn = actions.user.find_el_by_prop_seq(talon_seq,root)
            if not talon_btn:
                # 3 TRAY BUTTON SELECTED TRAY CLOSED
                prop_list = [("name","Show Hidden Icons"),("class_name","SystemTray.NormalButton")]
                if actions.user.element_match(el,prop_list):
                    actions.key("enter")
                    prop_list = [("name","^(?!Show Hidden Icons$).*")]
                    el = actions.user.wait_for_element(prop_list)
                    if el:
                        print("situation 3 confirmed")
                        root = actions.user.window_root()
                        talon_btn = actions.user.find_el_by_prop_seq(talon_seq,root)
            if not talon_btn:
                # 6. Talon menu is open, nothing selected
                prop_list = [("name","Application"),("automation_id","MenuBar")]
                if actions.user.element_match(el,prop_list):
                    print("situation 6 confirmed")
                    actions.key("esc:2")
                    prop_list = prop_list = [("name","T"),("class_name","Tray Window")]
                    el = actions.user.wait_for_element(prop_list)
                    # now we are in situation 8
                # 8. We are in this weird nonexistent system tray
                prop_list = [("name","T"),("class_name","Tray Window")]
                if actions.user.element_match(el,prop_list):
                    print("situation 8 confirmed")
                    # actions.key("super-b")
                    # prop_list = [("name","Show Hidden Icons Hide"),("class_name","SystemTray.NormalButton")]
                    # el = actions.user.wait_for_element(prop_list)
                    el = super_b_for_taskbar()
                    print(f'el: {el}')
                    # now we are in situation 4
                # 4 TRAY BUTTON SELECTED TRAY OPEN
                prop_list = [("name","Show Hidden Icons Hide"),("class_name","SystemTray.NormalButton")]
                if actions.user.element_match(el,prop_list):
                    print("situation 4 confirmed")
                    actions.key("enter")
                    prop_list = [("name","Show Hidden Icons"),("class_name","SystemTray.NormalButton")]
                    el = actions.user.wait_for_element(prop_list)
                    if el:
                        actions.key("enter")
                        el = actions.user.wait_for_element(app_btn_list)
                        if el:
                            root = actions.user.window_root()
                            talon_btn = actions.user.find_el_by_prop_seq(talon_seq,root)
            if not talon_btn:
                # 1-2. In a normal application
                print("situation 1-2")
                # actions.key("super-b")
                # prop_list = [("name","Show Hidden Icons.*"),("class_name","SystemTray.NormalButton")]
                # el = actions.user.wait_for_element(prop_list)
                el = super_b_for_taskbar()
                print(f'el: {el}')
                if el:
                    prop_list = [("name","Show Hidden Icons Hide"),("class_name","SystemTray.NormalButton")]
                    if actions.user.element_match(el,prop_list):
                        actions.key("enter")
                        prop_list = [("name","Show Hidden Icons"),("class_name","SystemTray.NormalButton")]
                        el = actions.user.wait_for_element(prop_list)
                    if el:
                        actions.key("enter")
                        el = actions.user.wait_for_element(app_btn_list)
                        if el:
                            root = actions.user.window_root()
                            talon_btn = actions.user.find_el_by_prop_seq(talon_seq,root)
                    

        print(f'talon_btn: {talon_btn}')
        if talon_btn:
            actions.user.act_on_element(talon_btn,'hover')
            actions.user.act_on_element(talon_btn,'invoke')
            actions.key('down')
            return True
        else:
            return False

    def go_talon_menu(menu_path: str):
        """Opens up a specific talon setting; path should be labels in taskbar separated by commas"""
        highlighting = actions.user.currently_highlighting()
        labelling = actions.user.currently_labelling()
        actions.user.auto_highlight(False)
        actions.user.auto_label(False)
        try:
            root = winui.root_element()
            if actions.user.invoke_taskbar_item("Talon"):
                item_list = menu_path.split(",")
                desktop = actions.user.root_element()
                if desktop:
                    prop_list = [("name","Context")]
                    root = actions.user.matching_child(desktop,prop_list)
                    if root:
                        for i,item in enumerate(item_list):
                            if item:
                                if item != "":                
                                    prop_list = [("name",item)]
                                    el = actions.user.matching_child(root,prop_list)
                                    if el:
                                        # we want to highlight element, but highlight will be hidden behind taskbar
                                        actions.user.reset_element_tracker()
                                        actions.user.act_on_element(el,'highlight')
                                        if i == len(item_list) - 1:
                                            actions.sleep(0.5)
                                        else:
                                            actions.sleep(0.25)
                                        actions.user.clear_highlights()
                                        actions.user.act_on_element(el,"invoke")
                                        actions.sleep(0.1)
                                        actions.key("down")
                                        desktop = actions.user.root_element()
                                        root = actions.user.matching_child(desktop,prop_list)
                                    else:
                                        return 
        except Exception as error:
            print(f"error in go_talon_menu: {error}")
        finally:
            # return to original highlighting/labelling state
            actions.user.auto_highlight(highlighting)
            actions.user.auto_label(labelling)
                        
    def exit_talon():
        """Exits talon!"""
        root = ax.get_root_element()
        print("FUNCTION EXIT TALON")
        print(f'root: {root.name}')
        # Open the system tray
        actions.key("super-b enter")
        # make sure the system tray is open
        actions.sleep(0.2)
        if ui.focused_element().name == "Show Hidden Icons":
            actions.key("enter")
        actions.key("up:12")
        i = 0
        tray_item = ui.focused_element().name
        while i < 30 and tray_item != "Talon":
            i += 1
            # try going right
            actions.key("right")
            if ui.focused_element().name == tray_item:
                # go down and all the way to the left
                actions.key("down left:25")
            tray_item = ui.focused_element().name
        # provide visual sign that this is happening
        actions.user.act_on_element(ui.focused_element(),"highlight")
        actions.user.act_on_element(ui.focused_element(),"click")
        actions.sleep(1.5)
        actions.key("up enter")
