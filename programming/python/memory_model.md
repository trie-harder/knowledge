# Python Memory Model: Heap vs. Stack Allocation

## The Short Answer

In Python, **almost everything lives on the heap**. Python does not give programmers direct control over stack vs. heap placement the way C, Go, or Rust do. The call stack exists (for function frames), but the *objects* Python code manipulates are heap-allocated.

---

## The Call Stack in Python

When a function is called, Python creates a **frame object** (`PyFrameObject`) and pushes it onto the call stack. This frame holds:

- A reference to the code object being executed
- The local variable namespace (a dict-like structure)
- The evaluation stack (operand stack for the bytecode interpreter)
- The current instruction pointer

```python
import inspect

def outer():
    x = 10
    return inner()

def inner():
    # Print the call stack frames
    for frame_info in inspect.stack():
        print(frame_info.function, frame_info.lineno)

outer()
# Output:
# inner   9
# outer   4
# <module> 12
```

**Crucially**: the frame itself (`PyFrameObject`) is **a heap-allocated C struct**. The call stack in Python is a linked list of heap objects, not a contiguous block of native memory like in C or Java.

---

## Where Objects Live: Always the Heap

Every Python object — `int`, `str`, `list`, `dict`, class instance, function — is allocated on the **heap** via Python's memory allocator (which layers on top of `malloc`).

```
C call stack (native)
┌─────────────────────────────┐
│  CPython interpreter loop   │
│  PyFrameObject* frame  ──────────────────────────────────┐
└─────────────────────────────┘                            │
                                                           ▼
Python heap (managed by pymalloc + GC)
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  PyFrameObject { locals, globals, f_back → prev frame }      │
│                                                              │
│  PyObject (int 42) { ob_refcnt=2, ob_type=int, ob_ival=42 }  │
│                                                              │
│  PyObject (str "hi") { ob_refcnt=1, ob_type=str, … }        │
│                                                              │
│  PyListObject { ob_item=[ptr, ptr, ptr], ob_size=3 }         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

Variables in Python are not memory locations — they are **names bound to objects**:

```python
x = 42       # name 'x' in current frame's locals dict → PyObject (int 42) on heap
y = x        # name 'y' also → same PyObject; refcount incremented to 2
x = 100      # name 'x' rebound → new PyObject (int 100); old object refcount → 1
del y        # name 'y' removed → refcount of int 42 drops to 0 → deallocated
```

---

## Python's Memory Management Layers

Python manages heap memory through several cooperating layers:

### 1. The Raw Allocator (OS / malloc)
Python requests large blocks of memory from the OS via `malloc` / `VirtualAlloc`. These are the raw pages Python owns.

### 2. The Arena Allocator
Python subdivides OS memory into **arenas** (256 KB each on 64-bit). Arenas are returned to the OS only when completely empty — long-lived objects can prevent arena release.

### 3. pymalloc (Object Allocator)
For objects **≤ 512 bytes**, CPython uses its own pool-based allocator (`pymalloc`) instead of calling `malloc` for every object. This dramatically reduces allocation overhead.

```
Arena (256 KB)
  └── Pools (4 KB each, one size class per pool)
        └── Blocks (8, 16, 24 … 512 bytes)
              └── Individual PyObjects
```

### 4. The Garbage Collector (cyclic GC)
Reference counting handles most deallocation immediately. The cyclic GC runs periodically to break **reference cycles** that reference counting cannot resolve.

```python
import gc

# Reference cycles prevent refcount from reaching 0
a = []
b = [a]
a.append(b)   # a → b → a: cycle

del a, b      # refcounts drop but never reach 0
gc.collect()  # cyclic GC detects and frees the cycle

print(gc.get_count())   # (gen0, gen1, gen2) object counts
print(gc.get_threshold()) # thresholds that trigger each generation
```

---

## Reference Counting in Detail

Every Python object has an `ob_refcnt` field. CPython increments it when a reference is created and decrements it when a reference is removed. When `ob_refcnt` hits zero, the object is immediately deallocated.

```python
import sys

x = [1, 2, 3]
print(sys.getrefcount(x))  # 2 — x itself + getrefcount argument

y = x
print(sys.getrefcount(x))  # 3 — x, y, getrefcount argument

def f(obj):
    print(sys.getrefcount(obj))  # one more inside f

f(x)   # prints 4 inside f, drops back to 3 after return
del y
print(sys.getrefcount(x))  # back to 2
```

---

## Generational Garbage Collection

The cyclic GC divides objects into three generations:

| Generation | Collected When                    | Holds                          |
|------------|-----------------------------------|--------------------------------|
| 0          | After ~700 new allocations        | Recently allocated objects     |
| 1          | After gen-0 collected ~10 times   | Survived one collection        |
| 2          | After gen-1 collected ~10 times   | Long-lived objects             |

Objects that survive a collection are promoted to the next generation and collected less frequently — this is the **generational hypothesis**: most objects die young.

```python
import gc

gc.disable()          # turn off automatic cyclic GC (refcount still works)
# ... create lots of short-lived objects ...
gc.collect(0)         # manually collect generation 0 only
gc.collect()          # collect all generations
gc.enable()
```

---

## Stack-Like Behavior in Python: The Evaluation Stack

Inside each frame, CPython maintains a small **operand/evaluation stack** — a C array of `PyObject*` pointers used to evaluate expressions. This is analogous to a hardware register file or expression stack in a stack-based VM.

```python
# Python bytecode for: result = a + b * c
import dis
def calc(a, b, c):
    return a + b * c

dis.dis(calc)
# LOAD_FAST  a     → push reference to a
# LOAD_FAST  b     → push reference to b
# LOAD_FAST  c     → push reference to c
# BINARY_OP  *     → pop b,c; push result of b*c
# BINARY_OP  +     → pop a, (b*c); push result
# RETURN_VALUE     → pop and return
```

The pointers on this eval stack live in the C stack (or frame object), but the **objects they point to** are on the heap.

---

## Practical Consequences

### 1. No Stack Overflow From Deep Object Graphs
Deeply nested data structures don't overflow the C stack — objects are on the heap. However, deeply recursive *function calls* do, because each call adds a Python frame.

```python
import sys
sys.setrecursionlimit(1000)  # default 1000; each call adds a frame

def recurse(n):
    return recurse(n + 1)

# recurse(0)  → RecursionError after ~1000 frames
```

### 2. Assignment Does Not Copy
Because variables are references to heap objects, assignment never copies data:

```python
a = [1, 2, 3]
b = a           # b points to the same list object
b.append(4)
print(a)        # [1, 2, 3, 4] — a and b are the same object

import copy
c = copy.copy(a)    # shallow copy — new list, same element objects
d = copy.deepcopy(a) # deep copy — new list AND new element objects
```

### 3. Interning (Reusing Heap Objects)
Python interns (reuses) certain objects to save heap space:
- Small integers: **-5 to 256** (CPython implementation detail)
- Short strings that look like identifiers (interned automatically)
- Explicitly interned strings via `sys.intern()`

```python
import sys

# Integer interning
a, b = 100, 100
print(a is b)   # True — same object

a, b = 1000, 1000
print(a is b)   # False (may vary; don't rely on this)

# String interning
s1 = sys.intern("hello_world")
s2 = sys.intern("hello_world")
print(s1 is s2)  # True — forced to same object; O(1) comparison
```

### 4. Memory Profiling

```python
import tracemalloc

tracemalloc.start()

data = [i ** 2 for i in range(100_000)]

snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics("lineno")[:5]:
    print(stat)
# Shows heap allocations by line with size in bytes
```

---

## Comparison: Python vs. Go vs. Java

| Aspect                   | Python                              | Go                                  | Java                                 |
|--------------------------|-------------------------------------|-------------------------------------|--------------------------------------|
| Primitive storage        | Heap (always objects)               | Stack or heap (escape analysis)     | Stack (primitives), heap (objects)   |
| Object storage           | Heap                                | Heap (escape analysis may inline)   | Heap                                 |
| Stack allocation         | Frame pointers only; objects on heap| Local vars on stack if they don't escape | Primitives only                 |
| Memory management        | Refcount + cyclic GC                | Tricolor mark-and-sweep GC          | Generational GC (G1, ZGC, etc.)      |
| Deallocation timing      | Immediate (refcount=0) or GC cycle  | GC pause / concurrent               | GC pause / concurrent                |
| Cycle detection          | Optional cyclic GC                  | GC handles cycles natively          | GC handles cycles natively           |
| Escape analysis          | No (everything escapes to heap)     | Yes — compiler decides stack/heap   | Yes (JIT can stack-allocate)         |
| Explicit memory control  | No                                  | No (but `unsafe` package exists)    | No                                   |

---

## Summary

- Python has **no stack-allocated objects** from the programmer's perspective.
- All Python objects live on the **heap**, managed by pymalloc and reference counting.
- The **call stack** exists as a chain of heap-allocated frame objects.
- **Reference counting** provides immediate deallocation in most cases.
- The **cyclic GC** handles the reference cycles that refcounting cannot.
- For memory-critical work, prefer **NumPy/Pandas** (raw C arrays) or use `__slots__` to reduce per-instance overhead.

```python
# __slots__ reduces memory by avoiding a per-instance __dict__
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y

import sys
class PointDict:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p1 = Point(1, 2)
p2 = PointDict(1, 2)
print(sys.getsizeof(p1))  # ~56 bytes  (slots, no dict)
print(sys.getsizeof(p2))  # ~48 bytes  (but + dict overhead of ~232 bytes)
```
