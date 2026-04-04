# UIA lock + Talon action wrapper
# Drop this file anywhere in your Talon user directory.
# Then you can use:
#
#   with actions.user.uia_lock():
#       # safe UIAutomation calls here
#
# Debug logging and simple “long hold” warnings are optional and configurable.

import time
import threading
from threading import RLock

from talon import Module, actions


class UIALock:
    """
    Global lock to serialize all UIAutomation calls from this process.

    Usage in Talon code (after this file is loaded):

        from talon import actions

        def some_action():
            with actions.user.uia_lock():
                # any UIA calls here are serialized
                ...
    """

    def __init__(self, name: str, timeout: int|float, debug: bool, warn_hold_secs: int|float):
        """
        :param name:            Name used in debug messages.
        :param timeout:         Optional timeout (seconds) when acquiring the lock.
                                None = wait forever.
        :param debug:           If True, print acquire/release logs.
        :param warn_hold_secs:  If not None, print a warning if the lock is held
                                longer than this many seconds (on release).
        """
        self._name = name
        self._lock = RLock()
        self._timeout = timeout
        self.debug = debug
        self._warn_hold_secs = warn_hold_secs

        self._held_since = None
        self._owner = None

    def _log(self, msg):
        if self.debug:
            thread_name = threading.current_thread().name
            print(f"[{self._name}] ({thread_name}) {msg}")

    def __enter__(self):
        thread_name = threading.current_thread().name
        start_wait = time.time()

        if self._timeout is None:
            acquired = True
            self._lock.acquire()
        else:
            acquired = self._lock.acquire(timeout=self._timeout)

        if not acquired:
            raise TimeoutError(f"{self._name}: could not acquire lock within {self._timeout} seconds")

        wait_time = time.time() - start_wait
        self._held_since = time.time()
        self._owner = thread_name

        self._log(f"acquired (waited {wait_time:.3f}s) by {thread_name}")
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._held_since is not None:
            held_time = time.time() - self._held_since
        else:
            held_time = 0.0

        if self._warn_hold_secs is not None and held_time > self._warn_hold_secs:
            self._log(f"WARNING: lock held for {held_time:.3f}s (threshold {self._warn_hold_secs:.3f}s)")

        self._log(f"released after {held_time:.3f}s by {self._owner}")

        self._owner = None
        self._held_since = None
        self._lock.release()

    def wrap(self, func):
        """
        Decorator to run a function under the UIA lock.

        Example:

            @uia_lock.wrap
            def read_name(elem):
                return elem.name
        """
        def wrapped(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        wrapped.__name__ = func.__name__
        wrapped.__doc__ = func.__doc__
        return wrapped


# Global instance used by Talon actions below.
# Adjust these defaults as you like.
uia_lock = UIALock(
    name="UIALock",
    timeout=5.0,        # None = wait forever; 5.0 = raise if not acquired in 5 seconds
    debug=False,        # Set to True temporarily when debugging freezes/behavior
    warn_hold_secs=2.0  # Warn if a UIA call holds the lock longer than 2 seconds
)


# Talon action wrapper: exposes the lock as actions.user.uia_lock()
mod = Module()

@mod.action_class
class UIAActions:
    def uia_lock(name: str=None, timeout: float=25, debug: bool=None, warn_hold_secs: float=10):
        """Return the global UIA lock (use as a context manager)."""
        uia_lock.name=name
        uia_lock.timeout = timeout
        uia_lock.debug = debug
        uia_lock.warn_hold_secs = warn_hold_secs
        return uia_lock