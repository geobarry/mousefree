from talon import Module, Context, actions
import time

class time_stopper:
    def __init__(self,sec_lim):
        self.sec_lim = sec_lim
        self.start_time = time.perf_counter()
    def over(self):
        cur_time = time.perf_counter()
        elapsed_sec = cur_time - self.start_time
        if elapsed_sec > self.sec_lim:
            return True
        else:
            return False


mod = Module()

@mod.action_class
class Actions:
    def stopper(sec_lim: float):
        """initializes stopper with given limits"""
        stopper = time_stopper(sec_lim)
        return stopper
#        
        
ctx = Context()