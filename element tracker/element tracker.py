from talon import Module, Context, clip, ctrl, cron, actions, canvas, screen, settings, ui, app, speech_system
from talon.windows import ax as ax
from talon.types import Point2d as Point2d, rect as rect
from talon.skia import  Paint
from typing import Callable
from contextlib import contextmanager

import threading
import time
import inspect


mod = Module()

# list for tracking a set of clickable points
marked_elements = []

black_list = [] # ["Microsoft Excel"]
prior_state = (True,False)

# TRACKING
_pause_count = 0

"""
REDESIGN OF THE FOCUS-HIGHLIGHT POLLING  (sketch, not yet tested inside Talon)

THE BIG IDEA, IN PLAIN LANGUAGE
-------------------------------
Think of two people working in an office:

  * THE MANAGER  = Talon's main thread. It runs your update_highlight()
    every tick. If the manager gets stuck waiting on something, ALL of Talon
    freezes (voice commands, everything).

  * THE ASSISTANT = a helper thread we create below. Its only job is to go
    ask Windows/Excel "what is focused, and where is it on screen?"
    Excel sometimes takes forever to answer. That is fine, because only the
    assistant waits, not the manager.

The rules of the office:
  1. The manager NEVER waits for the assistant. Each tick, the manager just
     looks in the "inbox" to see if an answer has arrived. If not, it moves on.
  2. The assistant only works on ONE question at a time. If it is still
     stuck on the last question, the manager does not hand it another one.
     (The old code kept piling up questions, which is why Excel took so long
     to recover.)
  3. The assistant hands back plain numbers and text (a rectangle and a name),
     never the Windows "element" object itself. Those objects can go stale
     or hang if touched later from the wrong place.
  4. If Excel keeps failing, the manager asks less and less often
     (0.2s, 0.4s, 0.8s ... up to 5s), and goes back to normal speed the moment
     an answer succeeds.
"""


# ----------------------------------------------------------------------
# SETTINGS you can tune. Times are in seconds.
# ----------------------------------------------------------------------
BASE_DELAY = 0.1       # starting wait after a failure; doubles with each failure
MAX_DELAY = 5.0        # never wait longer than this between questions
MAX_FAILS = 10         # stops the doubling from growing without limit
STALL_HIDE_AFTER = 0.3 # if the assistant has been stuck this long, hide the
                       # (probably out of date) highlight box


# ======================================================================
# THE ASSISTANT
# ======================================================================
class UIAPoller:
    """
    The assistant. It lives on its own background thread and answers one
    question at a time: "what is focused right now, where is it, and
    (optionally) what is it called?"
    """

    def __init__(self):
        # A "lock" is like a key to a small cabinet. Only one person can hold
        # the key at a time. We use it so the manager and assistant never
        # read/write the shared notes (busy flag, answer inbox) at the same
        # instant, which could garble them.
        self._lock = threading.Lock()

        # An "event" is like a doorbell. The manager rings it to wake the
        # assistant up when there is a new question. The assistant sleeps
        # (using no CPU) until the bell rings.
        self._wake = threading.Event()

        # --- shared notes (always accessed while holding the lock) ---
        self._busy = False          # True while the assistant is working on a question
        self._busy_since = 0.0      # when it started the current question
        self._want_name = False     # does the manager want the element's name too?
        self._request_app = None    # which app was in front when the question was asked
        self._uia_lock = None # global lock to prevent conflicts with other uia calls
        self._result = None         # the INBOX: holds the latest answer, or None if empty

        # Start the assistant. daemon=True means "if Talon shuts down, don't
        # wait for this thread" so a hung Excel call cannot stop Talon exiting.
        thread = threading.Thread(target=self._run, daemon=True, name="uia-poller")
        thread.start()

    # ------------------------------------------------------------------
    # Called by the MANAGER
    # ------------------------------------------------------------------
    def request(self, want_name, app_key, lock):
        """
        The manager says: "please go find out what is focused."

        This returns immediately (it never waits).
          - Returns True  if the assistant accepted the question.
          - Returns False if the assistant is still busy with the last
            question. In that case nothing happens, and the manager simply
            tries again on a later tick.

        want_name: also fetch the element's name (only needed for labels).
        app_key:   a tag for which app is in front, so we can throw away
                   answers that arrive after the user switched apps.
        """

		# use the lock associated with current class/object
        with self._lock:
            if self._busy:
                return False  # still working on the last one, don't pile up
            self._busy = True
            self._busy_since = time.monotonic()
            self._want_name = want_name
            self._request_app = app_key
            self._uia_lock = lock
        self._wake.set()  # ring the doorbell (alerts the assistant to stop waiting)
        return True

    def take(self):
        """
        The manager checks the inbox.

        Returns the newest answer as (app_key, rect, name), or None if
        nothing new has arrived. Reading it also EMPTIES the inbox, so the
        same answer is never processed twice.
        """
        with self._lock:
            answer = self._result
            self._result = None
        return answer

    def stalled_for(self):
        """
        The manager asks: "how long has the assistant been stuck on the
        current question?"  Returns 0.0 if it is not busy.
        Used to decide when to hide a highlight that may be out of date.
        """
        with self._lock:
            if not self._busy:
                return 0.0
            return time.monotonic() - self._busy_since

    # ------------------------------------------------------------------
    # Runs on the ASSISTANT's own thread (the manager never calls this)
    # ------------------------------------------------------------------
    def _run(self):
        """
        The assistant's daily routine, repeated forever:
          1. Sleep until the doorbell rings.
          2. Read the question details.
          3. Ask Windows what is focused, its rectangle, and maybe its name.
             (THIS is the part that can hang in Excel. Only this thread
             suffers when it does.)
          4. Put the answer in the inbox and mark itself as free again.
        """
        while True:
            self._wake.wait()   # sleep until the manager rings the bell
            self._wake.clear()  # reset the bell for next time

            # lock 1: read the notes, then let go of the poller's lock immediately
            with self._lock:
                want_name = self._want_name
                app_key = self._request_app
            try:
                # lock 2: block other automation calls
                with self._uia_lock:
                    el = ui.focused_element()
                    rect = el.rect if el else None
                    name = ""
                    # Only ask for the name if wanted AND we got a rectangle.
                    # Every extra question to Excel is another chance to hang.

                    if el and rect and want_name:
                        name = el.name or ""
                    answer = (app_key, rect, name)
            except Exception as error:
                print(f"poller error: {type(error).__name__}: {error}")
                answer = (app_key, None, "")
            # Drop the answer in the inbox and say "I'm free now".
            # If step 3 hung for 30 seconds, we simply reach this point
            # 30 seconds later; nothing else was waiting on us.
            with self._lock:
                self._result = answer
                self._busy = False


class element_tracker:
    def __init__(self):        
        print("initializing element tracker...")
        self.canvas = None
        rect = actions.user.get_screen_bounds()
        self.canvas = canvas.Canvas.from_rect(rect)
        self.canvas.register('draw',self.draw_canvas)
        self.canvas.freeze()
        self.rectangles = []
        self.labels = []
        self.auto_highlight = True
        self.auto_label = False
        self.focused_rect = None
        self.focused_label = ""
        self.traversal_count = 0
        self.interval = 200
        self.skip_trg = 1
        self.skip_n = 1
        self.app_prev = None
        self.job = None
        # Polling Manager's Notes:
        self.poller = UIAPoller()   # hire the assistant (create ONE, once)
        self.fail_count = 0         # how many failures in a row
        self.next_attempt = 0.0     # earliest time we're allowed to ask again
        self.app_key = None         # which app was in front last tick

        self.init_cron()
    def add_element(self,rect,label = ''):
        self.rectangles.append(rect)
        self.labels.append(label)
        self.canvas.freeze() # this forces canvas redraw
    def remove_element(self,rect):
        try:
            idx = self.rectangles.index(rect)
            del self.rectangles[idx]
            del self.labels[idx]
            self.canvas.freeze() # this forces canvas redraw
        except:
            pass
    def clear_elements(self):
        self.rectangles = []
        self.labels = []
        self.canvas.freeze() # this forces canvas redraw
    def draw_canvas(self, canvas):
        try:
            paint = canvas.paint
            paint.color = 'f3f'
            paint.style = paint.Style.STROKE
            paint.stroke_width = 5
            def highlight_element(rect,lbl,paint):
                if rect != None:
                    canvas.draw_round_rect(rect,11,11,paint)
                if lbl != '':
                    if rect != None:
                        paint.stroke_width = 2
                        if len(lbl) > 50:
                            lbl = lbl[:50]
                        # determine label placement
                        # assume text dimensions
                        lbl_wd,lbl_ht = 600,30
                        top_margin = rect.y
                        btm_margin = canvas.height - rect.y - rect.height
                        if top_margin > btm_margin:
                            y = max(rect.y - lbl_ht, 0)
                        else:
                            y = min(rect.y + rect.height + 60, canvas.height - lbl_ht)
                        x = min(rect.x,canvas.width - lbl_wd)
                        actions.user.text_aliased(lbl,x,y,46,canvas)        
            if self.auto_highlight or self.auto_label:
                highlight_element(self.focused_rect,self.focused_label,paint)
            if len(self.rectangles) > 0:
                for idx in range(len(self.rectangles)):
                    rect = self.rectangles[idx]
                    canvas_rect = canvas.rect
                    lbl = self.labels[idx]
                    highlight_element(rect,lbl,paint)
        except Exception as error:
            print(f'DRAW_CANVAS error: {error}')
    def disable(self):
        self.canvas.close()
        self.canvas = None
        if self.job:
            cron.cancel(self.job)
    def init_cron(self):
        """determines whether to use cron or event handling to update"""
        if self.job:
            cron.cancel(self.job)
        self.job = cron.interval(f"{self.interval}ms", self.update_highlight)
        for name, obj in inspect.getmembers(cron):
            if isinstance(obj,cron.Cron):
                with obj.cond:
                    job_list=[job for job in obj.jobs if job not in obj.cancelled]
    def update_highlight(self):
        """
        Runs every tick (from Talon's cron timer). Must be FAST. It never waits
        for Windows. Each tick it does three things:
          A. Read any answer waiting in the inbox and update the highlight.
          B. If the assistant has been stuck a while, hide the old highlight.
          C. If enough time has passed, ask the assistant a new question.
        """

        # Do nothing if tracking is paused, or if both features are switched
        # off (nothing to draw, so no reason to bother Excel).
        if _pause_count > 0 or not (self.auto_highlight or self.auto_label):
            return

        now = time.monotonic()  # a clock that is not affected by changing system time

        # Work out which app is in front. (name, pid) is a more reliable
        # fingerprint than turning the whole app object into text.
        app = ui.active_app()
        app_key = (app.name, app.pid) if app else None

        # If the user switched apps, forget our failure history. The new app
        # deserves a fresh start at full speed, and the old highlight box
        # does not belong on the new app.
        if app_key != self.app_key:
            self.app_key = app_key
            self.fail_count = 0
            self.next_attempt = 0.0
            self._set_highlight(None, "")

        # ---- A. check the inbox ----
        answer = self.poller.take()

        if answer:
            answered_app, rect, name = answer

            # Ignore answers about an app that is no longer in front.
            if answered_app == self.app_key:
                if rect:
                    # Success: go back to full speed and show the highlight.
                    self.fail_count = 0
                    self.next_attempt = 0.0
                    self._set_highlight(rect, name if self.auto_label else "")
                else:
                    # The assistant came back empty-handed: slow down.
                    self._register_failure(now)

        # ---- B. hide a possibly out-of-date highlight while stuck ----
        # If Excel is not answering, the box on screen may no longer match the
        # real focus. Better to show nothing than to show the wrong thing.
        elif self.poller.stalled_for() > STALL_HIDE_AFTER:
            self._set_highlight(None, "")

        # ---- C. ask a new question if it is allowed ----
        # request() quietly does nothing if the assistant is still busy, so this
        # can never create a pile-up.
        if now >= self.next_attempt:    		
            # use existing uia_lock obtained from talon action
            lock = actions.user.uia_lock(entry_timeout=30)   # wait up to 30s for the lock
            self.poller.request(self.auto_label, self.app_key, lock)

    def _register_failure(self, now):
        """
        Called when the assistant could not find a focused element.
        Increase the failure count and set how long to wait before asking again.
        The wait doubles each time: 0.2s, 0.4s, 0.8s, 1.6s ... capped at MAX_DELAY.
        Also hides the highlight, since we no longer know where focus is.
        """
        self.fail_count = min(self.fail_count + 1, MAX_FAILS)
        delay = min(MAX_DELAY, BASE_DELAY * (2 ** self.fail_count))
        self.next_attempt = now + delay
        self._set_highlight(None, "")


    def _set_highlight(self, rect, label):
        """
        Update what is drawn on screen, but ONLY if something actually changed.
        (Redrawing every tick wastes effort; this skips redundant redraws.)
        rect = None and label = "" means "draw nothing".
        """
        if rect != self.focused_rect or label != self.focused_label:
            self.focused_rect = rect
            self.focused_label = label
            self.canvas.freeze()  # tells Talon to redraw the highlight canvas

    # If above continues to work well for a couple weeks (i.e. by second week of November)
    # go ahead and delete the following old version
    def OLD_update_highlight(self):
        """Updates the focused element using windows accessibility"""
        if _pause_count > 0:
            print(f"tracking paused (_pause_count={_pause_count}), skipping highlight update...")
            return 
        else:
            try:

                # handle safety valve to slowed down for unresponsive apps
                app_cur=str(ui.active_app())
                if app_cur != self.app_prev:
                    # We're in a new app, so we should be able to turn off safety valve
                    self.skip_trg = 1
                    self.skip_n = 1
                    self.app_prev=app_cur
                if self.skip_trg > self.skip_n:
                    self.skip_n += 1
                    print(f"skip_n: {self.skip_n}")
                    return
                time_limit=((self.interval/1000) * (0.9*self.skip_n))
                el=actions.user.safe_focused_element(time_limit=time_limit)
                
                rectangle_found = False
                if el:
                    if self.auto_highlight or self.auto_label:
                        rect = actions.user.el_prop_val(el,"rect")
                        if rect:
                            rectangle_found = True
                            if rect != self.focused_rect:
                                self.focused_rect = rect
                                if self.auto_label:
                                    self.focused_label = actions.user.el_prop_val(el,'name')
                            if not self.auto_label:
                                if self.focused_label != "":
                                    self.focused_label = ""
                        else:
                            pass
                    else:
                        pass
                    if rectangle_found:
                        # turn off safety valve
                        self.skip_trg = 1
                        self.skip_n = 1
                        self.app_prev=app_cur
                    else:
                        self.focused_rect = None
                        self.focused_label = ""
                    self.canvas.freeze()
                # turn up safety valve
                if not el or not rectangle_found:
                    self.skip_trg += 25 # because talon sets the timer at 20
                    self.skip_n += 1
            except Exception as error:
                print(f'FUNCTION update_highlight - error: {error}')

el_track = None
def on_ready():
    global el_track
    el_track = element_tracker()
app.register("ready",on_ready)

@mod.action_class
class Actions:
    def auto_highlight(on: bool = True):
        """automatically highlight focused element"""
        el_track.auto_highlight = on
    def auto_label(on: bool = True):
        """automatically highlight and label focused element"""
        el_track.auto_label = on


    def currently_highlighting():
        """Returns boolean representing current highlighting state"""
        return el_track.auto_highlight
    def currently_labelling():
        """Returns bulling representing current labeling state"""
        return el_track.auto_label

    def is_tracking_paused():
        """Returns true if element tracker is paused"""
        return _pause_count > 0

    @contextmanager
    def tracking_paused():
        """Allows element tracker pausing with a with block"""
        global _pause_count
        _pause_count += 1
        try:
            yield
        finally:
            _pause_count -= 1

    def highlight_element(el: ax.Element, lbl: str = ""):
        """Highlight specified element, with optional label"""
        if el:
            print(f'HIGHLIGHT_ELEMENT el: {el}')
            rect = actions.user.el_prop_val(el,"rect")
            print(f'rect: {rect}')
            if rect:
                if len(lbl) > 50:
                    lbl = lbl[:50]
                el_track.add_element(rect,lbl)
                
                return 
        print("HIGHLIGHT_ELEMENT: unable to highlight element")
    def highlight_rectangle(rect: rect):
        """Highlights input rectangle without associated element"""
        el_track.add_element(rect,"")
    def highlight_until_next_command(el: ax.Element, lbl: str = ""):
        """creates a highlight that will be removed after the next spoken command"""
        if el:
            rect = actions.user.el_prop_val(el,'rect')
            if rect:
                global num_phrases
                num_phrases = 0
                actions.user.highlight_element(el,lbl)
                def remove_highlight_after(e):
                    global num_phrases
                    num_phrases += 1
                    if num_phrases == 2:
                        el_track.remove_element(rect)
                        speech_system.unregister("post:phrase",remove_highlight_after)
                speech_system.register("post:phrase",remove_highlight_after)
        
    def remove_highlight(el: ax.Element):
        """Remove element from highlights"""
        if el:
            rect = actions.user.el_prop_val(el,"rect")
            if rect:
                try:
                    el_track.remove_element(el.rect)
                except:
                    print("Unable to remove highlight: Element rectangle does not match any current highlight")
    def clear_highlights():
        """Removes all ui elements from the highlight list"""
        el_track.clear_elements()

    def reset_element_tracker():
        """deletes the element tracker and creates a new one. """
        global el_track
        del el_track
        el_track = element_tracker()
    def mark_focused_element():
        """records the clickable point of the currently focused item"""
        print("FUNCTION: mark_focused_element")
        global marked_elements
        el = actions.user.safe_focused_element()
        if el:
            marked_elements.append(el)
    def mouse_to_marked_element_handle(hnd_pos: str, ordinal: int = 0,ms: int = 350):
        """moves the mouse to the marked element"""
        if ordinal < len(marked_elements):
            rect = actions.user.el_prop_val(marked_elements[ordinal],"rect")
            if rect:
                actions.user.mouse_to_obj_handle(rect,hnd_pos,ms = ms)
    def select_marked():
        """selects marked elements and then empties list"""
        global marked_elements
        # clear any selection
        el = actions.user.safe_focused_element()
        try:
            pattern = el.selectionitem_pattern
            pattern.remove_from_selection()
        except Exception as error:
            print(f"Error removing from selection in accessibility.py function select_marked: {error}")        
        # select all marked elements
        for el in marked_elements:
            try:
                pattern = el.selectionitem_pattern
                pattern.add_to_selection()
            except Exception as error:
                print(f"Error adding to selection in accessibility.py function select_marked: {error}")        
        # reset list of marked elements
        marked_elements = []
    def clear_marked():
        """clears the list of marked elements"""
        global marked_elements
        marked_elements = []