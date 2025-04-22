from talon import Module, Context, actions
import time

class time_stopper:
    def __init__(self,sec_lim,counter_limits = []):
        self.sec_lim = sec_lim
        self.start_time = time.perf_counter()
        self.count_limit = counter_limits
        self.n = [0]*len(self.count_limit)
    def increment(self,counter_number = 0):
        self.n[counter_number]+=1
    def over(self):
        for i in range(len(self.count_limit)):
            if self.n[i] >= self.count_limit[i]:
                print(f"stopper stopped due to counter {i} over limit")
                return True
        cur_time = time.perf_counter()
        elapsed_sec = cur_time - self.start_time
        if elapsed_sec > self.sec_lim:
            print(f"stopper stopped due to time ({elapsed_sec} sec) over limit ({self.sec_lim} sec)")
            return True
        else:
            return False


mod = Module()

@mod.action_class
class Actions:
    def stopper(sec_lim: float, count_limit: list = []):
        """initializes stopper with given limits"""
        stopper = time_stopper(sec_lim,count_limit)
        return stopper
#        
        
ctx = Context()