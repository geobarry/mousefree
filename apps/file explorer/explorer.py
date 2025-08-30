from talon import Context,Module,actions,clip
from talon.windows import ax as ax
import subprocess
import re
import os
from pathlib import Path
import itertools


# from ..utilities.spoken_form_utils import text_to_spoken_forms
mod = Module()
 
mod.list("explorer_column","headings that can be sorted by")
mod.list("dynamic_file", desc="Files in current Items View in Windows File Explorer")
mod.list("dynamic_folder", desc="Folders in current Items View in Windows File Explorer")
mod.list("file_ext",desc = "File extension without period")
mod.list("dynamic_file_with_ext",desc = "Experimental dynamic list with input argument")
mod.list("explorer_context_option",desc = "Context many options available for files in Windows File Explorer")
mod.list("subfolder",desc = "Subfolder names common to many folders")
mod.list("explorer_action",desc = "Actions you can perform on files or folders in explorer")
mod.list("explorer_app_bar_item",desc = "Commands available from the application bar")

ctx = Context()

def explorer_window():
    """Gets root window, whether in main application or dialog"""
    print("EXPLORER_WINDOW")
    root = actions.user.window_root()
    c = actions.user.el_prop_val(root,"class_name")
    if c == None or not "#" in c:
        children = root.children
        prop_list = [("class_name","ShellTabWindowClass")]
        root = actions.user.matching_child(root,prop_list)
    return root
def retrieve_item(name: str, item_type: str = "file"):
    """Returns the file or folder ax.Element from the items view"""
    print(f"RETRIEVE_ITEM {item_type} (name: {name})")
    root = explorer_window()
    prop_seq = [
        [("class_name","DUIViewWndClassName")],
#        [("class_name","DUIListView")], # not present in dialogues
        [("class_name","UIItemsView")]
    ]        
    el = actions.user.find_el_by_prop_seq(prop_seq,root = root,verbose = False)
    if el:
        children = el.children
        if children:
            for child in children:
                if actions.user.element_match(child,[("class_name",("UIItem"))]):
                    el = child
                    break
            if el:
                actions.user.act_on_element(el,"select")
                actions.edit.file_start()
                actions.sleep(0.1)
                prop_list = [("name",name)]
                # check if top element is what we are looking for
                el = actions.user.safe_focused_element()
                if not actions.user.element_match(el,prop_list):
                    # try typing out item name directly
                    actions.insert(name)
                    el = actions.user.wait_for_element(prop_list,time_limit = 0.2)
                    if not el:
                        # try getting to item with key presses
                        actions.key("up")
                        actions.sleep(0.5)
                        actions.user.key_to_matching_element("down",prop_list,delay = 0.02,avoid_cycles = True,limit = 20,sec_lim = 3,verbose = False)
                el = actions.user.safe_focused_element()
                if actions.user.element_match(el,prop_list):
                    return el
                else:
                    return None
def current_folder_from_title():
    path = actions.user.file_manager_current_path()
    path = path.replace(" - File Explorer","")
    if os.path.isdir(path):
        print("got path from title")
        return path
    else:
        return None
def current_folder_from_menu():
    # This is still inconsistent, and sometimes doesn't return anything
    # and sometimes operates on selected item but sometimes on containing folder
    print("CURRENT_FOLDER_FROM_MENU")
    # Obtain file items panel
    actions.user.explorer_select_items_panel()
    root = actions.user.window_root()
    print(f'root: {root}')
    prop_seq = [
        [("class_name","ShellTabWindowClass")],
        [("class_name","DUIViewWndClassName")],
        [("name","Items View"),("class_name","UIItemsView")],
    ]
    el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = False)
    print(f'ITEMS VIEW el: {el}')
    if el:
        selection = actions.user.el_prop_val(el,"selection")
        if not selection:
            print("selecting items panel...")
            # need to select something
            actions.user.explorer_select_items_panel()
        # open up the more button
        prop_seq = [
            [("class_name","Microsoft.UI.Content.DesktopChildSiteBridge")],
            [("class_name","ApplicationBar"),("automation_id","FileExplorerCommandBar")],
            [("class_name","Button"),("automation_id","MoreButton")]
        ]
        el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = False)
        print(f'MORE BUTTON el: {el}')
        if el:
            actions.user.act_on_element(el,"invoke")
            prop_list = [("class_name","AppBarButton")]
            actions.user.wait_for_element(prop_list)
            # invoke the copy path button
            prop_seq = [
                [("class_name","Microsoft.UI.Content.DesktopChildSiteBridge")],
                [("class_name","ApplicationBar"),("automation_id","FileExplorerCommandBar")],
                [("name","Popup"),("class_name","Popup"),("automation_id","OverflowPopup")],
                [("name","Copy path"),("class_name","AppBarButton")]
            ]
            el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = False)
            print(f'COPY PATH BUTTON el: {el}')
            if el:
                actions.user.act_on_element(el,'invoke')
                path = clip.text().strip('"')
                print(f'CLIP path: {path}')
                # path is to item, so get parent folder
                if path:
                    path = os.path.dirname(path)
                    print(f'----------> SELECT INVOKE path: {path}')
                # clean up UI
                actions.key("esc")
                actions.user.explorer_select_items_panel()
                return path

def current_folder_from_dialog():
    print("CURRENT_FOLDER_FROM_DIALOG")
    root = actions.user.window_root()
    prop_seq = [
#        	[("name","Save As"),("class_name","#32770")],
        [("class_name","ReBarWindow32")],
        [("class_name","Address Band Root")],
        [("name","Loading"),("class_name","msctls_progress32")],
        [("class_name","Breadcrumb Parent")],
        [("name","Address.*")],
#        	[("name","Address"),("class_name","Edit")]
    ]
    el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = False)
    if el:
        path = actions.user.el_prop_val(el,"name")
        if path:
            path = path.lstrip("Address: ")
            return path
def current_folder_from_address_bar():
    # seems like this will require keyboard shortcut, won't work for special folders :(
    print("CURRENT_FOLDER_FROM_ADDRESS_BAR")
    root = actions.user.window_root()
    print(f'root: {root}')
    prop_seq = [
        [("class_name","Microsoft.UI.Content.DesktopChildSiteBridge")],
        [("class_name","AutoSuggestBox")],
        [("name","Address Bar")]
    ]
    el = actions.user.find_el_by_prop_seq(prop_seq,root)
    print(f'el: {el}')
    val = actions.user.el_prop_val(el,'value')
    print(f'val: {val}')
def current_folder(path_type: str = "directory"):
    root = actions.user.window_root()
    cls = actions.user.el_prop_val(root,'class_name')
    if cls == "#32770":
        print("****IN A DIALOG")
        return current_folder_from_dialog()
    else:
        print("****MAIN EXPLORER WINDOW")
        folder = current_folder_from_title()
        if folder:
            return folder
        else:
            # User has not selected option to place path in window title
            # We're going to have to do this the hard way
            # Try menu button
            folder = current_folder_from_menu()
            if folder:
                return folder
            else:
                # If that fails, maybe we are in a dialog after all
                return current_folder_from_dialog()
def app_bar_button(button_name: str):        
    root = actions.user.window_root()
    prop_seq = [
        [("class_name","Microsoft.UI.Content.DesktopChildSiteBridge")],
        [("automation_id","FileExplorerCommandBar")],
    ]
    el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = True)
    if el:
        prop_list = [("name",button_name),("class_name",".*Button")]    
        button = actions.user.matching_child(el,prop_list)
        if not button:
            # window is too small, try more options button
            more_button_prop_list = [("name","More options"),("class_name","Button")]
            more_button = actions.user.matching_child(el,more_button_prop_list)
            if more_button:
                actions.user.act_on_element(more_button,'invoke')
                sort_prop_list = [("name","Sort")]
                actions.user.wait_for_element(sort_prop_list,time_limit = 1)
                if button_name != "Sort":
                    actions.user.key_to_matching_element("down",prop_list,limit = 10,sec_lim = 1)
            button = actions.user.wait_for_element(prop_list,time_limit = 1)
        print(f'button: {button}')
        if button:
            actions.user.act_on_element(button,'invoke')
def retrieve_item_list(item_type: str = "file", ext: str = ""):
    """Returns a list of spoken forms for each file or folder in items view"""
    # value cannot be trusted without pressing keyboard shortcut
    global current_folder_items
    print("RETRIEVE_ITEM_LIST")
    folder = current_folder("directory")
    print(f'folder: {folder}')
    if folder:
        # catch situation where folder cannot be found
        if folder == "" or folder is None:
            print("FUNCTION: retrieve_item_list ERROR: cannot obtain folder path")
            return 
        get_files = item_type == "file"
        current_folder_items = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) == get_files]
        if ext != '':
            n = len(ext)
            current_folder_items = [item for item in current_folder_items if item[-n:] == ext]
        spoken_form_dict = actions.user.create_spoken_forms_from_list(current_folder_items)
        # print(f'spoken_form_dict: {dict(itertools.islice(spoken_form_dict.items(), 20))}')
        # print(f'len(spoken_form_dict): {len(spoken_form_dict)}')
#        out = actions.user.text_to_spoken_forms(current_folder_items)
        # print(f'out: {dict(itertools.islice(out.items(), 20))}')
        # print(f'len(out): {len(out)}')
#        actions.user.explorer_select_items_panel()
        return spoken_form_dict

ext_dict = {
    "project":"aprx",
    "document":"docx",
    "spreadsheet":"xlsx",
    "excel":"xlsx",
    "power":"pptx",
    "powerpoint":"pptx",
    "pdf":"pdf"
    }

@ctx.dynamic_list("user.dynamic_file_with_ext")
def dynamic_file_with_ext(spoken_form) -> dict[str,str]:
    ext = ext_dict[spoken_form[0]]
    output = retrieve_item_list("file",ext)
    return output

@ctx.dynamic_list("user.dynamic_file")
def dynamic_file(_) -> dict[str,str]:
    return retrieve_item_list("file")

@ctx.dynamic_list("user.dynamic_folder")
def dynamic_folder(spoken_form) -> dict[str,str]:
    # NOTE: Sometimes this doesn't work in dialogs even though the return value is correct, 
    #        the talon command ends up being the lowercase version of the key, not the associated dictionary value
    # NOTE: It looks like you are not allowed to call an action from inside a dynamic list in another module
    print("DYNAMIC_FOLDER")
    dynamic_output = retrieve_item_list("folder")
    return dynamic_output

time_last_pop = 0
num_recent_pops = 0

@mod.action_class
class Actions:
    def explorer_test():
        """test"""
        current_folder_from_menu()
    def explorer_process_item(name: str = "", item_type: str = "file",action: str = "select"):
        """Attempts to open the item with a given name and type (file over folder), or else the currently selected item"""
        print(f"FUNCTION: explorer_process_item ({item_type} {name})")
        if name == "":
            el = actions.user.safe_focused_element()
        else:
            el = retrieve_item(name,item_type)
        if el:
            prop_list = [("name",name),("class_name","UIItem")]
            if actions.user.element_match(el,prop_list):
                if action == "open":
                    actions.user.act_on_element(el,"invoke")
                elif "select" in action:
                    actions.user.act_on_element(el,action)
                elif action in ["copy","cut","delete"]:
                    actions.user.act_on_element(el,"select")
                    el = actions.user.wait_for_element(prop_list)
                    if el:
                        if action == 'copy':
                            actions.key("ctrl-c")
                        elif action == 'cut':
                            actions.key("ctrl-x")
                        elif action == "delete":
                            actions.key("del")

    def explorer_show_button_options(button_name: str):
        """Selects and expands the given button (sort, view, more)"""
        actions.key("esc:5")
        button = app_bar_button(button_name)
    def explorer_invoke_app_bar_item(item_sequence: str):
        """Invokes the given button on the app bar"""
        item_list = item_sequence.split("|")

        if len(item_list) > 0:
            print(f'first button: |{item_list[0]}|')
            item = item_list[0].strip(" ")
            print(f'item: |{item}|')
            actions.user.explorer_show_button_options(item)
            print("ASPARAGUS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#            return 
            
            for item in item_list[1:]:
                prop_list = [("class_name",".*MenuFlyout.*Item")]
                el = actions.user.wait_for_element(prop_list)
                print(f'el: {el}')
                item = item.strip(" ")
                print(f'item: {item}')
                prop_list = [("name",item)]
                root = actions.user.window_root()
                prop_seq = [
#                    [("class_name","Microsoft.UI.Content.DesktopChildSiteBridge")],
                    [("name","Popup"),("class_name","Popup")],
                    [("class_name","MenuFlyout")],
                    [("name",item),("class_name",".*MenuFlyout.*Item")]
                ]
                el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = True)                
                if not el:
                    break 
                else:
                    pattern_list = actions.user.el_prop_val(el,'patterns')
                    actions.user.act_on_element(el,'select')
                    actions.sleep(0.3)
                    if 'ExpandCollapse' in pattern_list:
                        actions.user.act_on_element(el,'expand')
                    elif 'Toggle' in pattern_list:
                        actions.user.act_on_element(el,'toggle')
                    elif 'Invoke' in pattern_list:
                        actions.user.act_on_element(el,'invoke')
                    else:
                        break 
                actions.sleep(0.3)
            if len(item_list) > 2:
                actions.key(f"esc:{len(item_list) - 1}")
    def explorer_select_items_panel():
        """Uses windows accessibility to select file panel"""
        root = explorer_window()
        # get to file container
        prop_seq = [
            [("class_name","DUIViewWndClassName")],
            [("class_name","DUIListView")],
            [("class_name","UIItemsView")]
        ]        
        el = actions.user.find_el_by_prop_seq(prop_seq,root = root,verbose = False)
        # make sure that all items are selected
        if el:
            el_list = el.selection_pattern.selection
            if len(el_list) == 0:
                el_list = [x for x in el.children if actions.user.element_match(x,[("class_name","UIItem")])][0:1]
            for el in el_list:
                el.selectionitem_pattern.add_to_selection()
    def explorer_select_navigation_panel():
        """Uses windows accessibility to select navigation panel"""
        root = actions.user.window_root()
        print(f'root: {root} root.name: {root.name}')
        prop_seq = [
        	[("class_name","ShellTabWindowClass")],
        	[("class_name","DUIViewWndClassName")],
        	[("name","Navigation Pane"),("class_name","SysTreeView32")],
        ]
        el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = True)   
        print(f'el: {el}')
        if el:
            if "Selection" in el.patterns:
                pattern = el.selection_pattern
                if pattern:
                    el_list = pattern.selection
                    if len(el_list) > 0:
                        el = el_list[0]
                        actions.user.act_on_element(el,"select")
    def explorer_copy_folder():
        """Returns the folder path"""
        folder = current_folder()
        clip.set_text(folder) # for backwards compatibility; please use return value
        return folder
    def explorer_copy_full_path():
        """Copies the full path of the currently selected file to the clipboard"""
        actions.key("f2 ctrl-a")
        actions.sleep(0.2)
        filename = actions.edit.selected_text()
        folder = actions.user.file_explorer_copy_folder()
        clip.set_text(f"{folder}\\{filename}")
    def explorer_navigate_to_folder(path: str):
        """navigates to given folder in ff explorer like application or dialog"""
        actions.key("alt-d")
        el = actions.user.safe_focused_element()
        actions.sleep(0.1)
        success = False
        i = 0
        while success == False and i < 10:
            try:
                el.value_pattern.value = path
                success = True
            except:
                i += 1
                actions.sleep(0.1)
        actions.sleep(0.1)
        actions.key("enter")
        actions.user.explorer_select_items_panel()
    def explorer_open_with(app_name: str):
        """Opens currently selected file with app"""
        # prop_list = [("class_name","UIItem")]
        # make sure that we have an item selected
        # if actions.user.element_match(winui.focused_element(),prop_list):
            # actions.key("menu")
            # prop_list = [("name","Open with")]
            # actions.sleep(0.9)
            # def open_with_app(prop_list,app_name):
                # actions.sleep(0.5)
                # el = actions.user.safe_focused_element()
                # if el:
                    # if actions.user.element_match(el,prop_list):
                        # actions.key("right")
                        # prop_list = [("name",f"{app_name}.*")]
                        # actions.sleep(0.1)
                        # actions.user.key_to_element_by_prop_list("down",prop_list)
            # actions.user.key_to_element_by_prop_list("up",prop_list,final_func = lambda: open_with_app(prop_list,app_name))
        actions.key("menu")
        actions.sleep(1)
        el = actions.user.safe_focused_element()
        parent = el.parent
        print(f'parent: {parent}')
        prop_seq = [
        	[("name","Open with"),("class_name","AppBarButton")]
        ]
        el = actions.user.find_el_by_prop_seq(prop_seq,parent,verbose = True)            
        if el:
            if actions.user.element_match(el,prop_seq[-1]):
                actions.user.act_on_element(el,"expand")
                el = actions.user.safe_focused_element()
                parent = el.parent
                print(f'parent: {parent}')
                prop_seq = [
                    [("name",app_name),("class_name","MenuFlyoutItem")]
                ]
                el = actions.user.find_el_by_prop_seq(prop_seq,parent,verbose = True)
                if el:
                    if actions.user.element_match(el,prop_seq[-1]):
                        actions.user.act_on_element(el,"select")
    def explorer_manage_column(col_name: str = '', action: str = '', delta_width: int = -50):
        """Shows, hides, toggles or resizes the designated column"""
        # Tab to the column heading element
        prop_list = [("class_name","UIColumnHeader")]
        el = actions.user.safe_focused_element()
        if not actions.user.element_match(el,prop_list):
#            actions.user.key_to_matching_element("tab",prop_list)
            actions.user.explorer_select_items_panel()
            actions.key("tab")
        # Use the context menu to open the dialog and place focus on column headings list
        actions.key("menu m alt-t")
        # Go to the top of the list
        actions.key("home")
        if col_name != '':
            # Go down to the desired column
            actions.sleep(0.1)
            root = actions.user.window_root()
            print(f'root #1: {root}') # if we can catch this maybe we can make it quicker
            if root:
                actions.sleep(0.1) # apparently this needs a long time
                # prop_seq = [
                    # [("class_name","SysListView32"),("name","Details:")],
                    # [("name","col_name"),("automation_id","ListViewItem.*")]
                # ]
                # el = actions.user.find_el_by_prop_seq(prop_seq,root)
                actions.insert(col_name)
                actions.sleep(0.2)
                el = actions.user.safe_focused_element()
                print(f'el: {el}')
                if el:
                    pattern = el.scrollitem_pattern
                    print(f'ScrollItem_pattern: {pattern}')
                    if pattern:
                        el.scrollitem_pattern.scroll_into_view()
                    actions.sleep(0.5)
                    pattern = el.toggle_pattern
                    print(f'toggle_pattern: {pattern}')
                    if pattern:
                        el.toggle_pattern.toggle()
                        el.toggle_pattern.toggle()
                        actions.key("down up")
                        # Performed the designated action
                        if action != '':
                            if action.lower() == "show":
                                actions.key("alt-s")
                            elif action.lower() == "hide":
                                actions.key("alt-h")
                            elif "size" in action.lower():
                                actions.key("alt-w")
                                x = actions.edit.selected_text()
                                x = int(x)
                                if action.lower() == "sizeup":
                                    x += delta_width
                                else:
                                    x -= delta_width
                                actions.insert(str(x))
                            # Finish up
                            actions.key("enter shift-tab") 
    def explorer_sort_by(col_name: str):
        """sort files and folders by column"""
        print(col_name)
        prop_list = [("class_name","UIColumnHeader")]
        actions.user.key_to_matching_element("tab",prop_list)
        el = actions.user.safe_focused_element()
        if el:
            if actions.user.element_match(el,prop_list):
                prop_list = [("name",f"{col_name}.*")]
                actions.user.key_to_matching_element("right",prop_list,limit = 15)
                el = actions.user.safe_focused_element()
                if el:
                    if actions.user.element_match(el,prop_list):
                        actions.user.act_on_element(el,"double-click")

    def explorer_context_action(action_name: str):
        """Select option in context menu"""
        print(f"FUNCTION: explore_context_action({action_name})")
        actions.key("menu")
        prop_list = [("name",action_name),("class_name","AppBarButton")]
        actions.user.key_to_matching_element("down",prop_list,delay = 0.1)
        el = actions.user.safe_focused_element()
        if el:
            print(f'el: {el}')
            if "ExpandCollapse" in el.patterns:
                print("expanding...")
                actions.user.act_on_element(el,"expand")
                actions.sleep(0.5)
                actions.key("down up")
            else:
                actions.sleep(1)
                actions.key("enter")
    def explorer_special_group(group_name: str):
        """Attempts to navigate to the recent files section of the files panel"""
        # First we need to open the HOME item in the navigation panel
        root = actions.user.window_root()
        print(f'root: {root}')
        # This is stupid but we're going to select another item first for consistency
        prop_seq = [
        	[("class_name","ShellTabWindowClass")],
        	[("class_name","DUIViewWndClassName")],
        	[("name","Navigation Pane"),("class_name","SysTreeView32")],
        	[("name","Desktop")]
        ]
        el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = False)
        if el:
            prop_list = [("name","Home")]
            children = actions.user.el_prop_val(el,"children")
            # return 
            el = actions.user.matching_child(el,prop_list)
            if el:
                # select the desktop item
                print(f'el: {el}')
                actions.user.act_on_element(el,"select")
                actions.user.wait_for_element(prop_list,time_limit = 2)
                actions.key("enter")
#                    wait for the recommended button to be selected
                prop_list = [("name","Recommended.*")]
                el = actions.user.wait_for_element(prop_list,time_limit = 2,verbose = True)
                if not el:
                    print("Trying the tab key...")
                    actions.key("tab")
                el = actions.user.wait_for_element(prop_list,time_limit = 2,verbose = True)                
                print(f'el: {el}')
                if el:
                    actions.user.act_on_element(el,"collapse")
                    actions.sleep(0.5)
                    actions.key("down")
 #                     explorer will revert back to recommended group one time
                    el = actions.user.wait_for_element(prop_list,time_limit = 2)
                    if el:
                        actions.key("down")
                        actions.sleep(1)
                        actions.key("down")


    def explorer_filter():
        """Opens the filter by button"""
        root = actions.user.window_root()
        prop_seq = [
        	[("class_name","Microsoft.UI.Content.DesktopChildSiteBridge")],
        	[("class_name","ApplicationBar")],
        	[("class_name","AppBarButton"),("name","Filter")]
        ]
        el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = True)
        if el:
            actions.user.act_on_element(el,"expand")
    def explorer_open_path_in_terminal():
        """Open path in terminal"""
        actions.user.file_explorer_copy_folder()
        process = subprocess.Popen(["cmd.exe"], cwd=clip.text())
        process.returncode = 0
    def explorer_start_server():
        """starts a server from the current directory and opens it up in browser"""
        actions.user.explorer_open_path_in_terminal()
        actions.sleep(1.0)
        actions.insert("python -m http.server 8080")
        actions.sleep(1.0)
        actions.key("enter")
        actions.sleep(1.0)
        actions.key("super")
        actions.sleep(1.0)
        actions.insert("edge")
        actions.key("enter")
        actions.sleep(1.0)
        actions.key("ctrl-l")
        actions.insert("localhost:8080/")
        actions.sleep(1.0)
        actions.key("backspace enter")
    def explorer_create_animations_from_subfolders():
        """Creates animation from files in current folder and saves to parent folder"""
        print("FUNCTION: explorer_create_animations_from_subfolders")
        parent = actions.user.file_explorer_copy_folder()
        print(f'parent: {parent}')
        import os
        x = [
            name for name in os.listdir(parent) 
            if os.path.isdir(os.path.join(parent, name))
        ]
        process = subprocess.Popen(["cmd.exe"], cwd=parent)
        process.returncode = 0
        for folder in x[4:]:
            print(folder)
            subfolder = f"{parent}\\{folder}"
            # actions.sleep(2.0)
            msg = f"ffmpeg -framerate 30 -i {folder}\\k_%d.png -c:v libx264 -r 30 -pix_fmt yuv420p {folder}_animation.mp4"
            actions.sleep(1.5)
            actions.insert(msg)
            actions.key("enter")
            actions.sleep(5.0)
