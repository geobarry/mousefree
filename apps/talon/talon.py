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
                    actions.key("super-b")
                    prop_list = [("name","Show Hidden Icons Hide"),("class_name","SystemTray.NormalButton")]
                    el = actions.user.wait_for_element(prop_list)
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
                actions.key("super-b")
                prop_list = [("name","Show Hidden Icons.*"),("class_name","SystemTray.NormalButton")]
                el = actions.user.wait_for_element(prop_list)
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

    def go_talon_setting(setting_path: str):
        """Opens up a specific talon setting; path should be labels in taskbar separated by commas"""
        highlighting = actions.user.currently_highlighting()
        labelling = actions.user.currently_labelling()
        actions.user.auto_highlight(False)
        actions.user.auto_label(False)
        try:
            root = winui.root_element()
            print(f'root: {root}')
            if actions.user.invoke_taskbar_item("Talon"):
                # no longer works because tray items are not marked as focused elements,
                # nor are they available from the active application I think
                # they are available from def root_element() -> Element: ...
                # Here are some example mouse element sequences:
                # name	class_name
                # Speech Recognition	
                # Context	#32768
                # Desktop 1	#32769
                    
                # name	class_name
                # Install: Conformer D2 (2025-01-06) + Whisper	
                # Speech Recognition	#32768
                # Desktop 1	#32769

                print(f'setting_path: {setting_path}')
    #            return 
                item_list = setting_path.split(",")
                print(f'item_list: {item_list}')
                desktop = actions.user.root_element()
                print(f'desktop: {desktop}')
                if desktop:
                    prop_list = [("name","Context")]
                    root = actions.user.matching_child(desktop,prop_list)
                    print(f'root: {root}')
                    if root:
                        for i,item in enumerate(item_list):
                            if item:
                                if item != "":                
                                    prop_list = [("name",item)]
                                    el = actions.user.matching_child(root,prop_list)
                                    msg = actions.user.el_prop_val(el,'printout')
                                    print(f'FUNCTION go_talon_setting: el = {msg} | looking for |{item}|')
                                    if el:
                                        # we want to highlight element, but highlight will be hidden behind taskbar
                                        actions.user.reset_element_tracker()
                                        # rect = actions.user.el_prop_val(el,'rect')
                                        # if rect:
                                            # rect = Rect(rect.x-20,rect.y-20,rect.width+40,rect.height+40)
                                            # actions.user.highlight_rectangle(rect)
                                        actions.user.act_on_element(el,'highlight')
                                        if i == len(item_list) - 1:
                                            actions.sleep(0.5)
                                        else:
                                            actions.sleep(0.25)
                                        actions.user.clear_highlights()
                                        # actions.user.display_highlights()
                                        # actions.user.clear_highlights()
                                        actions.user.act_on_element(el,"invoke")
                                        actions.sleep(0.1)
                                        actions.key("down")
                                        desktop = actions.user.root_element()
                                        print(f'desktop: {desktop}')
                                        root = actions.user.matching_child(desktop,prop_list)
                                        print(f'root: {root}')
                                        # actions.sleep(0.2)
                                    else:
                                        return 
        except Exception as error:
            print(f"error in GO_TALON_SETTING: {error}")
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
