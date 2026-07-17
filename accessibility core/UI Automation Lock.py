# UIA lock with per-call threading/timeout configuration
# Drop this file anywhere in your Talon user directory.
#
# Key idea:
#   actions.user.uia_lock(...) returns a *configured lock wrapper*
#   whose settings apply ONLY for that specific "with" block.
#
# No global mutation. No persistent flags.
# Your gateway functions decide threading per call.

import time
import threading
from threading import RLock
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from talon import Module, actions, ui


# ============================================================
#   Base lock (global singleton, but no global config)
# ============================================================

class _BaseUIALock:
    """
    The underlying lock object.
    Holds the actual RLock and thread pool.
    Does NOT store per-call configuration.
    """

    def __init__(self, max_workers=2):
        self._lock = RLock()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    def acquire(self, timeout):
        if timeout is None:
            return self._lock.acquire()
        return self._lock.acquire(timeout=timeout)

    def release(self):
        self._lock.release()

    def submit(self, func, *args, **kwargs):
        return self._executor.submit(func, *args, **kwargs)


# Global base lock instance
_base_lock = _BaseUIALock(max_workers=2)


# ============================================================
#   Per-call lock wrapper (returned by actions.user.uia_lock)
# ============================================================

class UIALockWrapper:
    """
    A per-call wrapper around the global base lock.

    Each wrapper has its own:
      - name
      - entry_timeout
      - debug
      - warn_hold_secs
      - use_threading
      - uia_timeout

    These settings apply ONLY inside the "with" block.
    """

    def __init__(
        self,
        name="UIALock",
        entry_timeout=None,
        debug=False,
        warn_hold_secs=None,
        use_threading=False,
        uia_timeout=None,
    ):
        self.name = name
        self.entry_timeout = entry_timeout
        self.debug = debug
        self.warn_hold_secs = warn_hold_secs
        self.use_threading = use_threading
        self.uia_timeout = uia_timeout

        self._held_since = None
        self._owner = None

    # --- logging ---

    def _log(self, msg):
        if self.debug:
            thread_name = threading.current_thread().name
            print(f"[{self.name}] ({thread_name}) {msg}")

    # --- context manager ---

    def __enter__(self):
        thread_name = threading.current_thread().name
        start_wait = time.time()

        acquired = _base_lock.acquire(self.entry_timeout)
        if not acquired:
            raise TimeoutError(
                f"{self.name}: could not acquire lock within {self.entry_timeout} seconds"
            )

        wait_time = time.time() - start_wait
        self._held_since = time.time()
        self._owner = thread_name
        if self.warn_hold_secs and wait_time > self.warn_hold_secs:
            self._log(f"acquired (waited {wait_time:.3f}s) by {thread_name}")
        return self

    def __exit__(self, exc_type, exc, tb):
        held_time = (
            time.time() - self._held_since if self._held_since is not None else 0.0
        )

        if self.warn_hold_secs is not None and held_time > self.warn_hold_secs:
            self._log(
                f"WARNING: lock held for {held_time:.3f}s "
                f"(threshold {self.warn_hold_secs:.3f}s)"
            )

#        self._log(f"released after {held_time:.3f}s by {self._owner}")

        self._owner = None
        self._held_since = None
        _base_lock.release()

    # --- UIA execution ---

    def call(self, func, *args, **kwargs):
        """
        Run func(...) under this wrapper's configuration.
        """

        with self:
            if not self.use_threading:
                # Direct/blocking mode
                start = time.time()
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    elapsed = time.time() - start
                    self._log(
                        f"UIA DIRECT ERROR: func={getattr(func, '__name__', func)} "
                        f"elapsed={elapsed:.3f}s error={e}"
                    )
                    raise
                else:
                    elapsed = time.time() - start
                    self._log(
                        f"UIA DIRECT OK: func={getattr(func, '__name__', func)} "
                        f"elapsed={elapsed:.3f}s"
                    )
                    return result

            # Threaded mode
            future = _base_lock.submit(func, *args, **kwargs)
            start = time.time()
            timeout = self.uia_timeout

            try:
                if timeout is None:
                    result = future.result()
                else:
                    result = future.result(timeout=timeout)
            except TimeoutError:
                elapsed = time.time() - start
                self._log(
                    f"UIA TIMEOUT: func={getattr(func, '__name__', func)} "
                    f"{ui.active_app()} "
                    f"elapsed={elapsed:.3f}s timeout={timeout:.3f}s"
                )
                return None
            except Exception as e:
                elapsed = time.time() - start
                self._log(
                    f"UIA ERROR: func={getattr(func, '__name__', func)} "
                    f"{ui.active_app()} "
                    f"elapsed={elapsed:.3f}s error={e}"
                )
                raise
            else:
                elapsed = time.time() - start
                if elapsed > self.warn_hold_secs:
                    self._log(
                        f"UIA OK: func={getattr(func, '__name__', func)} "
                        f"{ui.active_app()} "
                        f"elapsed={elapsed:.3f}s"
                    )
                return result

    # --- decorator helper ---

    def wrap(self, func):
        def wrapped(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapped


# ============================================================
#   Talon actions
# ============================================================

mod = Module()

@mod.action_class
class UIAActions:
    def uia_lock(
        name: str | None = None,
        entry_timeout: float = 1,
        debug: bool | None = None,
        warn_hold_secs: float = 2,
        use_threading: bool | None = None,
        uia_timeout: float | None = None,
    ):
        """
        Return a per-call UIA lock wrapper.

        Example:
            with actions.user.uia_lock(use_threading=True, uia_timeout=0.5):
                val = el.name
        """
        return UIALockWrapper(
            name=name or "UIALock",
            entry_timeout=entry_timeout,
            debug=debug or False,
            warn_hold_secs=warn_hold_secs,
            use_threading=use_threading or False,
            uia_timeout=uia_timeout,
        )

    def uia_call(func: callable, use_threading: bool = False, uia_timeout: float | None = None):
        """
        Convenience wrapper for per-call UIA execution.

        Example:
            rect = actions.user.uia_call(lambda: el.rect, use_threading=True, uia_timeout=0.3)
        """
        wrapper = UIALockWrapper(use_threading=use_threading, uia_timeout=uia_timeout)
        return wrapper.call(func)
