from talon import Module,Context,actions,ui
from talon.windows import ax as ax

mod = Module()

mod.mode("zen","Limited set of general commands plus applications specific commands.")

@mod.action_class
class Actions:
    def do_nothing():
        """Capture text but don't do anything."""
        pass