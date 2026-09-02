import os
from talon.windows import ax as ax, ui as winui
from talon import Context, Module, actions, app, ui
from talon.types import Rect as Rect
import time

mod = Module()

ctx = Context()
ctx.matches = """
os: windows
"""

def wait_for_popup_window(app_name, cls_name = "#32768", time_limit=2, interval=0.1):
    start = time.time()
    while time.time() - start < time_limit:
        for w in ui.windows():
            if w.cls == cls_name:
                app=w.app
                name=app.name
                if name == app_name:
                    return w
        actions.sleep(interval)
    return None

def wait_for_matching_child(root, prop_list, time_limit=2, interval=0.1, verbose=False):
    """Tries polling until the matching child is found, returns none otherwise"""
    start = time.time()
    while time.time() - start < time_limit:
        if root:
            el = actions.user.matching_child(root, prop_list)
            if el:
                return el
        if verbose:
            print(f"wait_for_matching_child: not found yet, retrying... ({prop_list})")
        actions.sleep(interval)
    if verbose:
        print(f"wait_for_matching_child: timed out looking for {prop_list}")
    return None

@mod.action_class
class Actions:


    def invoke_system_tray_item(item_name: str):
        """Invokes given system_tray item"""
        # Talon #958 seems to have a regression where the talon tray menu has no accessible elements
        # ISSUE: The act of accessing the Talon system tray icon
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
        app_btn_list = [("class_name","SystemTray.NormalButton"),("automation_id","NotifyItemIcon")]
        def super_b_for_system_tray():
            # pressing super-b sometimes hits the windows start button instead of the system_tray button
            # so we have to look for that
            tray_props = [("name","Show Hidden Icons.*"),("class_name","SystemTray.NormalButton")]
            start_btn_props = [("automation_id","StartButton")]
            prop_list = ["OR",[tray_props,start_btn_props]]
            actions.key("super-b")
            el = actions.user.wait_for_element(prop_list,time_limit = 1,verbose = True)
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
                    el = super_b_for_system_tray()
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
                el = super_b_for_system_tray()
                print(f'el: {el}')
                if el:
                    prop_list = [("name","Show Hidden Icons Hide"),("class_name","SystemTray.NormalButton")]
                    if actions.user.element_match(el,prop_list):
                        actions.key("enter")
                        prop_list = [("name","Show Hidden Icons"),("class_name","SystemTray.NormalButton")]
                        el = actions.user.wait_for_element(prop_list)
                    if el:
                        print(f'el: {el}')
                        actions.key("enter")
                        el = actions.user.wait_for_element(app_btn_list)
                        print(f'el: {el}')
                        if el:
                            root = actions.user.window_root()
                            print(f'root: {root}')
                            print(f'talon_seq: {talon_seq}')
                            talon_btn = actions.user.find_el_by_prop_seq(talon_seq,root, verbose=True)
                    

        print(f'talon_btn: {talon_btn}')
        if talon_btn:
            actions.user.act_on_element(talon_btn,'select')
            actions.user.act_on_element(talon_btn,'hover')

            actions.user.act_on_element(talon_btn,'click')
            # actions.user.act_on_element(talon_btn,'invoke')
            return talon_btn

        else:
            return False

    def go_talon_menu(menu_path: str):
        """Opens up a specific talon setting; path should be labels in system tray separated by commas"""
        print("TALON MENU")
        with actions.user.tracking_paused():
            try:
                el= actions.user.invoke_system_tray_item("Talon")
                print(f'el talon system tray button: {el}')
                if el:
                    # actions.sleep(1)
                    w=wait_for_popup_window("Talon")
                    print(f'w: {w}')
                    if w:
                        root=w.element
                        print(f'root: {root}')

                        actions.key('down')
                        item_list = menu_path.split(",")

                        if root:
                            for i,item in enumerate(item_list):
                                if item:
                                    if item != "":                
                                        prop_list = [("name",item)]
                                        print(f"Looking for item {item}...")
                                        el = wait_for_matching_child(root,prop_list)
                                        print(f"Found item.")
                                        if el:
                                            # we want to highlight element, but highlight will be hidden behind system tray context menu
                                            actions.user.act_on_element(el,"invoke")
                                            # actions.sleep(0.5)
                                            actions.key("down")
                                            desktop = actions.user.root_element()
                                            root = wait_for_matching_child(desktop,prop_list)
                                        else:
                                            return 
            except Exception as error:
                print(f"error in go_talon_menu: {error}")

    def invoke_talon_update_button(trg_btn: str):
        """Navigates to the desired button using keyboard keys, because there are too many elements at the same level of the hierarchy to navigate down from the window root"""
        print(f'trg_btn: {trg_btn}')
        # For this to work, we need to make sure both the trg button name and
        # the name of the currently focused element are in the following list
        tab_seq = ["Skip This Version","Install Update","Remind Me Later"]
        if trg_btn not in tab_seq:
            tab_seq=["Install and Relaunch","Cancel"]

        if trg_btn in tab_seq:
            el = actions.user.safe_focused_element()
            if el:
                cur_btn = actions.user.el_prop_val(el,'name')
                print(f'cur_btn: {cur_btn}')
                if cur_btn in tab_seq:
                    # Get indices of cur_btn,trg_btn
                    cur_idx = tab_seq.index(cur_btn)
                    trg_idx = tab_seq.index(trg_btn)
                    print(f'trg_idx: {trg_idx}')
                    print(f'cur_idx: {cur_idx}')
                    # tab or shift tab to target if needed
                    prop_list = [("name",trg_btn)]
                    if cur_idx > trg_idx:
                        actions.user.key_to_matching_element("shift-tab",prop_list)
                    if trg_idx > cur_idx:
                        actions.user.key_to_matching_element("tab",prop_list)
                    # double-check that current element is the one that we want
                    el = actions.user.safe_focused_element()
                    if actions.user.element_match(el,prop_list):
                        # wait a second to give visual confirmation
                        actions.sleep(0.5)
                        actions.user.act_on_element(el,'invoke')

