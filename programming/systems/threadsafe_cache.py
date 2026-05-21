"""
Thread-safe Cache with Condition Variables (Python)
==================================================

Implements a cache where, if a value is missing, a slow function is called to compute it.
Multiple threads requesting the same missing key will *not* trigger duplicate computations:
- The first thread computes and populates the cache.
- Others wait for the result, then return it.

Concurrency is managed with `threading.Lock` and `threading.Condition`.

---

**Python concurrency notes:**
- Uses `threading` (not `multiprocessing`):
    - GIL (Global Interpreter Lock) means only one thread runs Python bytecode at a time in CPython.
    - For I/O-bound or lock-coordination tasks, threads are fine. For CPU-bound, use `multiprocessing`.
- `threading.Lock` is a mutual exclusion primitive.
- `threading.Condition` allows threads to wait for a state change (e.g., value becomes available).

---

Edge cases handled:
- Only one thread computes a missing value per key.
- If the slow function raises, all waiting threads are notified and the exception is propagated.
- No deadlocks: all locks are acquired/released in a consistent order.

---

Usage:
    cache = ThreadSafeCache(slow_func)
    result = cache.get("foo")

---
"""

import threading
from typing import Callable, Any, Dict

class ThreadSafeCache:
    def __init__(self, slow_func: Callable[[Any], Any]):
        self._cache: Dict[Any, Any] = {}
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._in_progress: Dict[Any, int] = {}  # key → number of threads computing/fetching
        self._slow_func = slow_func
        self._exceptions: Dict[Any, Exception] = {}  # key → exception raised during computation

    def get(self, key: Any) -> Any:
        with self._lock:
            if key in self._cache:
                return self._cache[key]
            if key in self._in_progress:
                # Someone else is computing this key; wait for it
                while key in self._in_progress:
                    self._cond.wait()
                # After being notified, check if value is now present or if an exception occurred
                if key in self._exceptions:
                    raise self._exceptions.pop(key)
                return self._cache[key]
            # Mark this key as being computed
            self._in_progress[key] = 1
        # Compute outside the lock (slow_func may take a long time)
        try:
            value = self._slow_func(key)
        except Exception as e:
            with self._lock:
                self._exceptions[key] = e
                del self._in_progress[key]
                self._cond.notify_all()
            raise
        with self._lock:
            self._cache[key] = value
            del self._in_progress[key]
            self._cond.notify_all()
        return value

# --- Example usage and test ---
if __name__ == "__main__":
    import time
    import random
    def slow_double(x):
        print(f"Computing {x}...")
        time.sleep(1 + random.random())
        return x * 2

    cache = ThreadSafeCache(slow_double)

    def worker(key):
        try:
            v = cache.get(key)
            print(f"Thread got {key} → {v}")
        except Exception as e:
            print(f"Thread got exception for {key}: {e}")

    threads = [threading.Thread(target=worker, args=(42,)) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Should see only one "Computing 42..." print, all threads get 84
