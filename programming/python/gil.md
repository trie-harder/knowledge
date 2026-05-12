# The Python GIL (Global Interpreter Lock)

## What Is the GIL?

The GIL is a **mutex (mutual exclusion lock)** inside CPython — the reference implementation of Python, written in C. It ensures that only **one thread can execute Python bytecode at any given moment**, regardless of how many CPU cores are available or how many threads your program spawns.

It is not part of the Python language specification. It is a CPython implementation detail.

```python
import sys
print(sys.implementation.name)  # 'cpython'

# On Python 3.13+ (no-GIL build only):
print(sys._is_gil_enabled())    # True (standard) or False (no-GIL build)
```

---

## Why the GIL Exists

### The root cause: reference counting

CPython tracks object lifetimes using **reference counting**. Every object carries a counter (`ob_refcnt`) of how many variables point to it. When the count reaches zero, the object is freed immediately.

```c
// Every Python object in C (simplified):
typedef struct _object {
    Py_ssize_t ob_refcnt;    // how many references point to this object
    PyTypeObject *ob_type;   // what type is this object
} PyObject;
```

Every time a variable is assigned, passed to a function, or goes out of scope, CPython increments or decrements `ob_refcnt`. This is a **read-modify-write** operation — not atomic on any mainstream CPU:

```
Thread A and Thread B both hold a reference to the same object (ob_refcnt = 2)

Thread A drops its reference:        Thread B drops its reference:
  READ  ob_refcnt → 2                  READ  ob_refcnt → 2   ← GIL released here
  SUBTRACT 1 → 1                       SUBTRACT 1 → 1
  WRITE 1 → ob_refcnt                  WRITE 1 → ob_refcnt

Result: ob_refcnt = 1 — object never freed (memory leak)
Or the inverse race: ob_refcnt hits 0 twice → double-free → crash
```

### The GIL as the solution

Rather than making every refcount update an atomic CPU operation (which benchmarks showed caused ~2-5x slowdown on single-threaded code — the common case), Guido chose a single global lock: **only the thread holding the GIL can run Python bytecode**. Since only one thread touches objects at a time, refcounts are always consistent.

This decision was made in **1991** when:
- Consumer hardware was single-core
- Threads were rarely used in scripting
- The target audience was scientists and sysadmins, not systems programmers
- The engineering cost of a concurrent tracing GC was not available

---

## What the GIL Protects vs. What It Doesn't

### What it DOES protect

- CPython's internal reference counts (`ob_refcnt`) on every object
- The memory allocator's internal state (pool/arena bookkeeping)
- The bytecode interpreter's own data structures
- Internal state of built-in types (dict, list internals)

### What it does NOT protect

Your application-level data. The GIL is a lock for **CPython's own internals**, not for your code's logic.

```python
counter = 0

def increment():
    global counter
    counter += 1  # 3 steps: READ, ADD, WRITE — GIL can release between any of them

import threading
threads = [threading.Thread(target=lambda: [increment() for _ in range(100_000)])
           for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()

print(counter)  # Should be 500,000 — often less due to race conditions
```

For your own shared mutable state, you need `threading.Lock()`, `threading.RLock()`, or `queue.Queue`.

---

## When the GIL Is Released

The GIL is not held permanently. CPython releases it in two situations:

### 1. Every 5 milliseconds (the switch interval)

CPython checks every 5ms whether another thread is waiting for the GIL. If so, it releases it, allowing the other thread to run. This is what gives Python threads **concurrency** (interleaving) even though there's no true parallelism.

```python
import sys
print(sys.getswitchinterval())  # 0.005 (5 milliseconds)
sys.setswitchinterval(0.001)    # can be tuned
```

### 2. During all I/O operations

Whenever a thread makes a blocking system call (network read/write, file read/write, `time.sleep`, subprocess calls), CPython releases the GIL **before** entering the call and reacquires it when the call returns.

```
Thread A makes an HTTP request:
  1. Python code calls requests.get(url)
  2. CPython releases the GIL  ← right here, before the network call
  3. Thread A blocks waiting for bytes from the network
  4. Thread B acquires GIL, runs Python bytecode simultaneously
  5. Network bytes arrive → Thread A reacquires GIL, continues

Thread A and Thread B are genuinely in-flight at the same time.
Neither is executing Python bytecode at the same nanosecond,
but they're making real progress concurrently.
```

This is why threads are genuinely useful for I/O-bound work despite the GIL.

---

## Concurrency vs. Parallelism

This is the most important distinction for understanding the GIL's practical impact.

- **Concurrency** — multiple threads making progress by taking turns. One runs while the others wait.
- **Parallelism** — multiple threads executing at the exact same nanosecond on separate CPU cores.

**The GIL prevents parallelism. It does not prevent concurrency.**

```
I/O-bound threads (HTTP requests) — concurrency IS useful:

Time →
Thread A: [send req] [....waiting for response....] [process] [send req]
Thread B:            [send req] [....waiting....] [process] [send req]
Thread C:                       [send req] [...waiting...] [process]

All 3 requests are in-flight simultaneously. Wall time ≈ 1 request's time.
GIL released during all the waiting. Real speedup achieved.

CPU-bound threads (number crunching) — concurrency is useless:

Time →
Thread A: [GIL][CPU][GIL][CPU][GIL][CPU]
Thread B:           [wait]    [wait]    [CPU]  ← only runs when A releases GIL
Thread C:                               [wait] ← never gets a core

Wall time ≈ running sequentially. No speedup. Sometimes slower due to overhead.
```

### Practical guidance

| Workload | Use | Reason |
|---|---|---|
| N independent HTTP/network calls | `threading` | GIL released during I/O wait; real concurrency |
| N independent file reads/writes | `threading` | Same |
| CPU-heavy computation | `multiprocessing` | Separate processes, separate GILs, each uses own core |
| Mixed I/O + light CPU | `threading` | I/O portions overlap; CPU portions serialized |
| Fire-and-forget tasks, event-driven | `asyncio` | Single thread, cooperative; no GIL needed |

---

## Why Other Languages Don't Need a GIL

### Go and Java: tracing garbage collection

Go and Java chose **tracing GC** instead of reference counting. The critical difference: **application threads never increment or decrement a reference counter**. There are no refcounts on objects.

Instead, a separate GC thread periodically scans the heap, finds which objects are unreachable by following pointers from live roots, and frees the unreachable ones. Since app threads never write bookkeeping data to shared objects during normal operation, the race condition that necessitated the GIL simply cannot occur.

```
CPython: every pointer assignment → write to ob_refcnt → race condition → GIL needed
Java/Go: every pointer assignment → optional write barrier (1 instruction) → no race
```

The **write barrier** Java and Go do inject is a single store to a "card table" (a bitmap marking which memory regions changed) — not a read-modify-write counter, and designed specifically to be thread-safe without locking.

### The trade-offs Go/Java accepted

| | CPython refcounting | Java/Go tracing GC |
|---|---|---|
| Cleanup timing | Immediate (deterministic) | Eventual (GC decides when) |
| Implementation complexity | Simple | Very hard |
| GC pauses | None (incremental via refcount) | Brief stop-the-world pauses |
| Cycles | Can't collect without extra cyclic GC | Handled naturally |
| Parallel threads | Requires GIL or atomic ops | Free — no per-assignment locking |

### Other Python implementations without a GIL

Because the GIL is a CPython choice, not a Python language requirement, other implementations of Python don't have it:

| Implementation | GIL? | Why |
|---|---|---|
| **CPython** | Yes (removing in 3.13) | Reference counting |
| **PyPy** | Yes | Also uses refcounting (different JIT, same GIL) |
| **GraalPy** | No | Uses GraalVM's tracing GC |
| **Jython** | No | Runs on JVM, uses JVM's tracing GC |
| **IronPython** | No | Runs on .NET CLR, uses CLR's tracing GC |

GraalPy, Jython, and IronPython get true parallel threads for free because they chose a runtime with tracing GC. The cost is lower compatibility with CPython's C extension ecosystem.

---

## Python 3.13: Removing the GIL (PEP 703)

### Why previous attempts failed

The naive approach is to make every `ob_refcnt` update an atomic CPU operation. Atomic operations require cache coherence coordination across cores — significantly more expensive than plain memory writes. Benchmarks showed this caused **~5x single-threaded slowdown**. Unacceptable — most Python code doesn't use threads, and making it 5x slower to support a use case most programs don't have was a non-starter.

### How PEP 703 solved it: biased reference counting

Sam Gross's key insight: **most objects are only ever touched by one thread**. So give each object two refcount fields:

- **Local refcount** — a plain (non-atomic) counter, updated when only one thread touches the object. Fast, same speed as before.
- **Shared refcount** — an atomic counter, used only when an object is accessed by multiple threads.

Objects start with a local refcount. When an object "escapes" to another thread, it's promoted to shared mode and pays the atomic cost only from that point on. Single-threaded code — the vast majority of Python — pays essentially zero overhead.

Result: CPython 3.13's no-GIL build runs single-threaded code within **~5% of the GIL build** on typical benchmarks.

### Current status (as of Python 3.13)

```bash
# Install the no-GIL variant (labeled 't' for free-threaded)
# Ubuntu/Debian:
apt install python3.13-nogil

# pyenv:
pyenv install 3.13t

# Check if GIL is enabled at runtime:
python3.13t -c "import sys; print(sys._is_gil_enabled())"  # False
```

The no-GIL build is opt-in and experimental in 3.13. The plan is for it to stabilize and become the default in a future release. The GIL is not gone yet — but it has a clear end date.

### What removing the GIL unlocks

- CPU-bound threads actually use all cores — wall time drops proportionally
- Large in-memory data (NumPy arrays, tensors) shared between threads with zero copying
- Single-process web servers that saturate all cores with threads instead of spawning N processes
- Python becomes viable for fine-grained shared-memory parallel workloads currently requiring Go or Java

### The new responsibility

Without the GIL, race conditions in your own code that were previously hidden by accidental serialization become real bugs. Any mutable shared state between threads now needs explicit synchronization. The tools are the same (`threading.Lock`, `queue.Queue`, etc.) — they just become mandatory rather than optional for correctness.
