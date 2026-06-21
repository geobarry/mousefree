from talon import Module, Context, actions, ui



mod=Module()

def get_notification_window():
    """Returns a list of window elements"""
    root=ui.root_element()    
    if root:
        win_list=ui.windows()
        win_list=[w for w in win_list if w.title == "New notification"]
        w=win_list[0]
        el=w.element
        children=actions.user.el_prop_val(el,'children')
        # actions.user.copy_element_descendants(el)
        # element should be New notification window
        if el:
            prop_seq=[
                [("automation_id","ToastCenterScrollViewer")],
                [("automation_id",".*ToastView")]
            ]
            w=actions.user.find_el_by_prop_seq(prop_seq,el,verbose=True)
            return w

def get_notification_button(button_name: str):
    """Returns one of the three buttons on the notification popup: Settings=ellipsis, Move=X, Show details"""
    w=get_notification_window()
    if w:
        prop_list=[("control_type","button"),("name",f"{button_name}.*")]
        el=actions.user.matching_child(w,prop_list)
        return el
    

@mod.action_class
class Actions:
    def win_act_on_notification(action: str):
        """Acts on the notification pop up in windows lower right corner. Options: Settings, Move, Show details"""
        button=get_notification_button(action)
        print(f'button: {button}')
        actions.user.act_on_element(button,'invoke')