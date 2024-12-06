from typing import Tuple
from talon import Context, Module, ctrl, cron, actions, imgui, ui, settings

# parameters
reaction_time = 1500 # set to 0 if you don't want backwards-correction
check_repeat_time = 20 # milliseconds to check to see if it's time to repeat
minimum_repeat_interval = 30 # milliseconds
speed_change = 100 # milliseconds per repeat
opposites = {
    'left': 'right',
    'right': 'left',
    'up': 'down',
    'down': 'up',
    'tab': 'shift-tab',
    'shift-tab': 'tab',
    'sky-tab': 'tab',
    'f6': 'shift-f6',
    'shift-f6': 'f6',
    'pageup': 'pagedown',
    'pagedown': 'pageup'
}
class SlowRepeater:
    def __init__(self):
        self.enabled = False
        self.cumulative_time = 0
        self.mode = ""
        self.cmd = None
    def enable_key(self, key, ms):
        self.mode = "key"
        key_parts = key.split("-")
        self.key = key_parts[-1]
        self.modifier_key = None
        if len(key_parts) > 1:
            self.modifier_key = "-".join(key_parts[:-1])
            actions.key("{}:down".format(self.modifier_key))
        self.ms = int(ms)
        if self.enabled:
            cron.cancel(self.job)
        self.enabled = True
        # check for repeat every 20 milliseconds
        self.job = cron.interval('{}ms'.format(check_repeat_time), self.repeat_command)
    def enable_command(self, ms):
        self.mode = "command"
        self.ms = int(ms)
        if self.enabled:
            cron.cancel(self.job)
        self.enabled = True
        # check for repeat every 20 milliseconds
        self.job = cron.interval('{}ms'.format(check_repeat_time), self.repeat_command)
        x = actions.core.recent_commands()
        self.cmd = x[-1][0]
    def disable(self):
        if not self.enabled:
            return
        cron.cancel(self.job)
        if self.mode == "key":
            # undo moves based on reaction time
            if reaction_time > 0:
                if self.key in opposites.keys():
                    n = int(min(self.cumulative_time, reaction_time)/self.ms)
                    for i in range(n):
                        actions.sleep(self.ms/1000)
                        actions.key(opposites[self.key])
            if self.modifier_key != None:
                actions.sleep(1.5)
                actions.key("{}:up".format(self.modifier_key))
        self.cumulative_time = 0
        self.modifier_key = None
        self.enabled = False
    def repeat_command(self):
        self.cumulative_time += check_repeat_time
        # time to repeat command if modulus remainder < check_repeat_time
        if self.cumulative_time % self.ms < check_repeat_time:
            if self.mode == "key":
                actions.key(self.key)
            elif self.mode == "command":
                actions.core.run_command(self.cmd[0],self.cmd[1])

repeater_object = SlowRepeater()
mod = Module()
mod.list("slow_repeater_speed_word", desc = "Verbal form for repetition delay")
mod.mode("slow_repeating", desc = "In the middle of repeating a task")

@imgui.open(x=700, y=0)
def gui_repeater(gui: imgui.GUI):
    if repeater_object.mode == "key":
        gui.text(f"Repeating: {repeater_object.key}")
    else:
        gui.text(f"Repeating command...")    
    gui.line()
    if gui.button("Stop repeating [stop repeating]"):
        actions.user.stop_repeating()

def init_actions():
    repeater_object.repeat_command()
    gui_repeater.show()
    actions.mode.enable("user.slow_repeating")
    actions.mode.disable("command")        
@mod.action_class
class Actions:
    def start_key_repeat(key: str, ms: str):
        """Initiate key press repetition"""
        repeater_object.enable_key(key, int(ms))
        init_actions()
    def start_cmd_repeat(ms: str):
        """Initiate command repetition"""
        repeater_object.enable_command(int(ms))
        init_actions()
    def stop_repeating():
        """Terminate repetition"""
        gui_repeater.hide()
        repeater_object.disable()
        actions.user.terminate_traversal()
        actions.mode.enable("command")
        actions.mode.disable("user.slow_repeating")
    def hard_stop_repeating():
        """Terminate Immediately"""
        repeater_object.ms = reaction_time + 1
        actions.user.stop_repeating()
    def repeat_faster(ordinal: int = 1):
        """Reduce repeat interval"""
        repeater_object.ms = max(repeater_object.ms-speed_change*ordinal,minimum_repeat_interval)
    def repeat_slower(ordinal: int = 1):
        """Increase repeat interval"""
        repeater_object.ms = max(repeater_object.ms+speed_change*ordinal,minimum_repeat_interval)
    def jiggle(key: str): 
        """Presses a key followed by its opposite."""
        if key in opposites.keys():
            actions.key(f"{key} {opposites[key]}")

ctx = Context()
