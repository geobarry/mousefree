from talon import Module,Context,actions,ui
from talon.windows import ax as ax

mod = Module()

@mod.action_class
class Actions:
    def auto_highlight_scroll(amount: int):
        """Scrolls and then re highlights"""
        actions.mouse_scroll(amount)
        actions.user.clear_highlights()
        actions.sleep(0.5)
        actions.user.act_on_focused_element("highlight")
