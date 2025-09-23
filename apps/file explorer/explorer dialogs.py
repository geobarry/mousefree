from talon import Context,Module,actions,clip
from talon.windows import ax as ax

mod = Module()

mod.list("file_type_description","file type description in application save or open dialog using windows file explorer dialog component")

ctx = Context()

@mod.action_class
class Actions:
    def explorer_dialog_new_folder():
        """Invokes the new folder button in un explorer style dialog"""
        root = actions.user.window_root()
        prop_seq = [
        	[("class_name","DUIViewWndClassName")],
        	[("name","Command Module"),("class_name","FolderBandModuleInner")],
        	[("name","New folder"),("class_name","AJOSplitButton")]
        ]
        el = actions.user.find_el_by_prop_seq(prop_seq,root,verbose = True)
        if el:
            actions.user.act_on_element(el,'invoke')
    def explorer_dialog_file_name():
        """Focuses on the File Name edit box and assigns the given value if input string is not empty"""
        actions.key("alt-n")
        prop_list = [("name","File name:"),("class_name","Edit"),("automation_id","1001")]
        el = actions.user.wait_for_element(prop_list)
        if el:
            txt = actions.edit.selected_text()
            print(f'txt: {txt}')
            sep_idx = txt.rfind(".")
            actions.key(f"right left:{len(txt)-sep_idx}")
            actions.edit.extend_line_start()
    def explorer_dialog_file_type(file_type_regex: str = ""):
        """Opens up the 'Save as type' combo box and optionally selects the given filetype"""
        # Used keyboard shortcut to get to combo box
        actions.key("alt-t")
        # Make sure combo box is in focus
        prop_list = [("name","Save as type:"),("automation_id","FileTypeControlHost")]
        el = actions.user.wait_for_element(prop_list)
        if el:
            # Open combo box
            actions.key("alt-down")
            # Navigate to designated filetype
            if file_type_regex != '':
                prop_list = [("value",file_type_regex)]
                el = actions.user.safe_focused_element()
                if el:
                    if not actions.user.element_match(el,prop_list):
                        actions.edit.file_start()
                        actions.key("down up")
                        actions.user.key_to_matching_element("down",prop_list,verbose = True)
                        # Make sure that we have found the right type
                        el = actions.user.safe_focused_element()
                        if el:
                            if actions.user.element_match(el,prop_list):
                                # press enter to close dropdown
                                actions.key("enter")
    def explorer_dialog_button(button_name: str, commit: bool = False):
        """Navigates to and optionally invokes the save, open or cancel button"""
        prop_list = [("name",button_name),("class_name","Button")]
        actions.user.key_to_matching_element("tab",prop_list)
        if commit:
            el = actions.user.wait_for_element(prop_list)
            if el:
                actions.sleep(0.3)
                actions.user.act_on_element(el,'invoke')

