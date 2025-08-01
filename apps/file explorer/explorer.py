from talon import Context,Module,actions,clip,ui
from talon.windows import ax as ax, ui as winui
import subprocess
import re
import os
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

ctx = Context()

def explorer_window():
    """Gets root window, whether in main application or dialog"""
    root = winui.active_window().element
    print(f'root: {root}')
    c = actions.user.el_prop_val(root,"class_name")
    print(f'c: {c}')
    if c == None or not "#" in c:
        print("We're inside...")
        children = root.children
        print(f'children: {children}')
        prop_list = [("class_name","ShellTabWindowClass")]
        root = actions.user.matching_child(root,prop_list)
    return root
def retrieve_item(name: str, item_type: str = "file"):
    """Returns the file or folder ax.Element from the items view"""
    print(f"FUNCTION: retrieve_item {item_type} (name: {name})")
    root = explorer_window()
    prop_seq = [
        [("class_name","DUIViewWndClassName")],
#        [("class_name","DUIListView")], # not present in dialogues
        [("class_name","UIItemsView")]
    ]        
    print(f'root: {root}')
    el = actions.user.find_el_by_prop_seq(prop_seq,root = root,verbose = True)
    print(f'el: {el}')
    # get first item
    if el:
        for child in el.children:
            if actions.user.element_match(child,[("class_name",("UIItem"))]):
                el = child
                break
        if el:
            actions.user.act_on_element(el,"select")
            
            actions.edit.file_start()
            actions.sleep(0.1)
            prop_list = [("name",name)]
            el = winui.focused_element()
            print(f"we should be at the top: {el.name}")
            print(f'prop_list: {prop_list}')
            
#            check if top element is what we are looking for
            if not actions.user.element_match(winui.focused_element(),prop_list):
                actions.key(name[0])
                actions.sleep(0.1)
#                check if first element starting with given character is what we are looking for
                el = winui.focused_element()
                if not actions.user.element_match(el,prop_list):
                    print(f'el name: {actions.user.el_prop_val(el,"name")}')
                    actions.key("up")
                    actions.sleep(0.5)
                    actions.user.key_to_matching_element("down",prop_list,delay = 0.02,avoid_cycles = True,limit = 75,sec_lim = 3)
                
            el = winui.focused_element()
            if actions.user.element_match(winui.focused_element(),prop_list):
                return el
            else:
                return None
def current_folder():
    root = winui.active_window().element
    print(f'FUNCTION current_folder root: {root}')
    # Okay here's the situation:
    # The address bar is not reliable, might leave out the last subfolder or be empty string
    # but the address bar the only place that we can get the letter drive
    # It seems the only reliable way to get the current folder is to enter the address bar with a keyboard shortcut
    # And even then it is very delicate, We need to obtain the value before pressing anything else,
    # and only after obtaining the value can we press escape to get rid of the annoying popup
    if root:
        el = None
        actions.key("ctrl-l")
        if "dialog" in actions.user.el_prop_val(root,"printout"):
            print("We are in a dialog...")
            prop_seq = [
                [("class_name","ReBarWindow32")],
                [("class_name","Address Band Root")],
                [("name","Loading"),("class_name","msctls_progress32")],
                [("name","Address"),("class_name","ComboBox")],
                [("name","Address"),("class_name","Edit")]
            ]
            el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = False)
        else:
            print("We are in the main Windows Explorer app")
            prop_seq = [
                [("class_name","Microsoft.UI.Content.DesktopChildSiteBridge")],
                [("class_name","AutoSuggestBox")],
                [("name","Address Bar"),("class_name","Textbox")]
            ]
            el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = False)
        if el:
            val = actions.user.el_prop_val(el,"value")
            print(f'current folder: {val}')
            # Press escape NOW to get rid of the popup
            actions.sleep(0.2)
            actions.key("esc")
            actions.user.explorer_select_items_panel()
            return val
def retrieve_item_list(item_type: str = "file", ext: str = ""):
    """Returns a list of spoken forms for each file or folder in items view"""
    # value cannot be trusted without pressing keyboard shortcut
    global current_folder_items
    folder = current_folder()
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
        out = actions.user.text_to_spoken_forms(current_folder_items)
#        actions.user.explorer_select_items_panel()
        return out

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
    # NOTE: It looks like you are not allowed to call an action from inside a dynamic list in another module
    print(f"FUNCTION dynamic_folder")
    print(f"spoken_form: {spoken_form}")
    dynamic_output = retrieve_item_list("folder")
    # print(f'dynamic_output: {dynamic_output}')
    return dynamic_output

time_last_pop = 0
num_recent_pops = 0

@mod.action_class
class Actions:
    def explorer_process_item(name: str, item_type: str = "file",action: str = "select"):
        """Attempts to open the item with a given name and type (file over folder)"""
        print(f"FUNCTION: explorer_process_item ({item_type} {name})")
        el = retrieve_item(name,item_type)
        if el:
            if action == "open":
                actions.user.act_on_element(el,"invoke")
            elif action == "select":
                actions.user.act_on_element(el,"select")
            elif action == "cut":
                actions.user.act_on_element(el,"select")
                actions.key("ctrl-x")
    def explorer_select_items_panel():
        """Uses windows accessibility to select file panel"""
        root = explorer_window()
        # get to file container
        prop_seq = [
            [("class_name","DUIViewWndClassName")],
            [("class_name","DUIListView")],
            [("class_name","UIItemsView")]
        ]        
        el = actions.user.find_el_by_prop_seq(prop_seq,root = root,verbose = True)
        # make sure that all items are selected
        if el:
            el_list = el.selection_pattern.selection
            if len(el_list) == 0:
                el_list = [x for x in el.children if actions.user.element_match(x,[("class_name","UIItem")])][0:1]
            for el in el_list:
                el.selectionitem_pattern.add_to_selection()
    def explorer_select_navigation_panel():
        """Uses windows accessibility to select navigation panel"""
        root = winui.active_window().element
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
        el = winui.focused_element()
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
                # el = winui.focused_element()
                # if el:
                    # if actions.user.element_match(el,prop_list):
                        # actions.key("right")
                        # prop_list = [("name",f"{app_name}.*")]
                        # actions.sleep(0.1)
                        # actions.user.key_to_element_by_prop_list("down",prop_list)
            # actions.user.key_to_element_by_prop_list("up",prop_list,final_func = lambda: open_with_app(prop_list,app_name))
        actions.key("menu")
        actions.sleep(1)
        el = winui.focused_element()
        parent = el.parent
        print(f'parent: {parent}')
        prop_seq = [
        	[("name","Open with"),("class_name","AppBarButton")]
        ]
        el = actions.user.find_el_by_prop_seq(prop_seq,parent,verbose = True)            
        if el:
            if actions.user.element_match(el,prop_seq[-1]):
                actions.user.act_on_element(el,"expand")
                el = winui.focused_element()
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
        if not actions.user.element_match(ui.focused_element(),prop_list):
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
            root = winui.active_window().element
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
                el = winui.focused_element()
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
        el = winui.focused_element()
        if el:
            if actions.user.element_match(el,prop_list):
                prop_list = [("name",f"{col_name}.*")]
                actions.user.key_to_matching_element("right",prop_list,limit = 15)
                el = winui.focused_element()
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
    def explorer_special_group(group_name: str):
        """Attempts to navigate to the recent files section of the files panel"""
        # First we need to open the HOME item in the navigation panel
        root = winui.active_window().element
        print(f'root: {root}')
        # This is stupid but we're going to select another item first for consistency
        prop_seq = [
        	[("class_name","ShellTabWindowClass")],
        	[("class_name","DUIViewWndClassName")],
        	[("name","Navigation Pane"),("class_name","SysTreeView32")],
        	[("name","Desktop")],
        	[("name","Gallery")]
        ]
        el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = True)
        if el:
            # select the desktop item
            print(f'el: {el}')
            actions.user.act_on_element(el,"select")
            # select the home item
            prop_seq[-1] = [("name","Home")]
            el = actions.user.find_el_by_prop_seq(prop_seq,root)
            if el:
                print(f'el: {el}')
                actions.user.act_on_element(el,"select")
                actions.key("enter")
                # wait for the recommended button to be selected
                prop_list = [("name","Recommended.*")]
                el = actions.user.wait_for_element(prop_list,time_limit = 2,verbose = True)
                if not el:
                    actions.key("tab")
                el = actions.user.wait_for_element(prop_list,time_limit = 2,verbose = True)                
                print(f'el: {el}')
                if el:
                    actions.user.act_on_element(el,"collapse")
                    actions.sleep(0.5)
                    actions.key("down")
#                   explorer will revert back to recommended group one time
                    el = actions.user.wait_for_element(prop_list,time_limit = 2)
                    if el:
                        actions.key("down")
                        el = actions.user.safe_focused_element()
                        print(f'el: {el}')
                        prop_list = [("name",group_name)]
                        if not actions.user.element_match(el,prop_list):
                            actions.user.key_to_matching_element("right",prop_list,limit = 3,sec_lim = 1.5)
                        actions.key("enter down")


    def explorer_filter():
        """Opens the filter by button"""
        root = winui.active_window().element
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
