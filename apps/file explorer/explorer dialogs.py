from talon import Context,Module,actions,clip
from talon.windows import ax as ax

mod = Module()
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