# Processes, Threads, and Concurrency

## Starting Point: Running a Program

When you double-click an application or run a command in a terminal, the operating system doesn't just execute your code directly. It creates a controlled environment for it first. That environment is a **process**.

---

## Processes

A **process** is an instance of a running program. It is the OS's fundamental unit of isolation — a container that holds everything your program needs to run, completely separated from every other running program.

When the OS creates a process it sets up:

- **A private virtual address space** — a range of memory addresses the process believes it owns entirely, isolated from all other processes
- **A copy of the program's code** loaded into that space
- **A heap** — memory available for dynamic allocation during runtime
- **A stack** — memory for function call frames and local variables
- **File descriptor table** — open files, network sockets
- **Process ID (PID)** — a unique number the OS uses to track it
- **CPU registers** and program counter (saved when the process isn't running)

```
Process A (PID 1042)              Process B (PID 1187)
┌─────────────────────┐           ┌─────────────────────┐
│ Virtual address space│           │ Virtual address space│
│  Stack              │           │  Stack              │
│  ↓                  │           │  ↓                  │
│                     │           │                     │
│  ↑                  │           │  ↑                  │
│  Heap               │           │  Heap               │
│  Static data        │           │  Static data        │
│  Code               │           │  Code               │
└─────────────────────┘           └─────────────────────┘
         │                                  │
         └──────────── OS ───────────────────┘
                        │
                   Physical RAM
         (OS maps each process to separate pages)
```

### Key property: isolation

Process A cannot read or write Process B's memory. The OS enforces this through hardware memory protection. If Process A crashes, Process B keeps running. If Process A has a bug that corrupts its own heap, Process B is unaffected.

This is why web browsers run each tab as a separate process — a crash in one tab doesn't take down the whole browser.

### Creating processes

Processes are created by other processes. On Unix/Linux, this is done with `fork()` — which creates an exact copy of the current process — followed by `exec()` to replace the copy with a new program.

```
init/systemd (PID 1)
  └── bash (PID 500)
        └── python3 script.py (PID 1042)   ← bash forked this
              └── subprocess.Popen(...) (PID 1043)  ← python forked this
```

### Inter-process communication (IPC)

Because processes are isolated, they have to explicitly communicate through OS-provided mechanisms:

| Mechanism | How it works | Speed |
|---|---|---|
| Pipes | Unidirectional byte stream | Fast |
| Sockets | Bidirectional, works over network | Medium |
| Shared memory | OS maps same physical RAM into both address spaces | Very fast |
| Files | Write to disk, other process reads | Slow |
| Signals | OS sends a notification (e.g. SIGTERM) | Instant, limited |
| Message queues | Kernel-buffered message passing | Fast |

---

## Threads

A **thread** is a unit of execution *within* a process. Every process starts with one thread (the main thread), but can create more.

All threads inside a process **share the same address space** — the same heap, the same global variables, the same open files. But each thread has its **own stack** and its **own CPU register state** (including its own program counter).

```
Process (PID 1042) — one virtual address space
┌───────────────────────────────────────────────┐
│                                               │
│  HEAP (shared by all threads)                 │
│  ┌─────────────────────────────────────────┐  │
│  │ objects, arrays, dynamically allocated  │  │
│  └─────────────────────────────────────────┘  │
│                                               │
│  Thread 1 Stack    Thread 2 Stack             │
│  ┌──────────┐      ┌──────────┐               │
│  │ frame    │      │ frame    │               │
│  │ locals   │      │ locals   │               │
│  └──────────┘      └──────────┘               │
│                                               │
│  CODE (shared, read-only)                     │
│  FILE DESCRIPTORS (shared)                    │
└───────────────────────────────────────────────┘
```

### What each thread owns privately

- **Stack** — its own call stack; function calls and local variables don't interfere with other threads
- **Stack pointer register** — points to the top of its stack
- **Program counter** — which instruction it's currently executing
- **All other CPU registers** — saved and restored when the thread is context-switched

### What all threads in a process share

- Heap memory
- Global and static variables
- Open file handles and sockets
- Process ID and process-level permissions

### Why threads exist

Creating a process is expensive: the OS must set up a new virtual address space, copy file descriptors, initialize data structures. This takes microseconds to milliseconds.

Creating a thread is cheap: just allocate a new stack (usually 1–8MB) and register state. The rest already exists. This takes microseconds.

Threads are also cheaper to switch between because they share an address space — no need to flush the TLB (translation lookaside buffer, the CPU cache for address translations).

| | Process | Thread |
|---|---|---|
| Creation cost | High (new address space, fork/exec) | Low (new stack only) |
| Context switch cost | High (TLB flush, address space swap) | Low (register save/restore) |
| Memory isolation | Complete | None — shared heap |
| Crash isolation | Yes | No — one thread can corrupt the shared heap |
| Communication | Requires IPC | Direct — just read/write shared memory |

---

## The CPU's Perspective: Scheduling

The CPU doesn't know about processes or threads directly — it just executes instructions. The **OS scheduler** is what creates the illusion that many things are running at once on limited hardware.

### On a single core

The OS rapidly switches the CPU between threads (and processes), giving each a small time slice (typically 1–10ms). This is **preemptive multitasking** — the OS can interrupt any thread at any time and switch to another.

```
Time →
Core 0: [Thread A][Thread B][Thread A][Thread C][Thread A][Thread B]
              ↑           ↑           ↑
         context switch (OS saves A's registers, loads B's)
```

From a human perspective this looks simultaneous. At the nanosecond level it's strictly sequential — one instruction at a time per core.

### On multiple cores

Each core runs independently. The scheduler assigns threads to cores. True parallelism: multiple threads executing at the exact same nanosecond.

```
Time →
Core 0: [Thread A][Thread A][Thread A][Thread A]
Core 1: [Thread B][Thread B][Thread B][Thread B]
Core 2: [Thread C][Thread C][Thread C][Thread C]

Thread A, B, and C are genuinely running simultaneously.
```

### Context switching

When the OS switches which thread a core is running, it must:
1. Save the current thread's CPU registers (including program counter) to memory
2. Load the next thread's saved registers
3. If switching processes: also swap the memory mapping (expensive; flushes TLB)

---

## Concurrency vs. Parallelism

These two words are often used interchangeably but mean different things.

**Concurrency** — multiple tasks are *in progress* at the same time, making progress by taking turns. This can happen on a single core. It's about structure: your program is designed to handle multiple things at once.

**Parallelism** — multiple tasks are *executing* at the exact same physical instant on separate hardware. This requires multiple cores. It's about execution.

```
Concurrency (1 core, 3 tasks):          Parallelism (3 cores, 3 tasks):

Time →                                  Time →
Core 0: [A][B][C][A][B][C][A]          Core 0: [A][A][A][A][A][A][A]
                                        Core 1: [B][B][B][B][B][B][B]
Tasks interleave. No two run            Core 2: [C][C][C][C][C][C][C]
at the same instant.
                                        All three run simultaneously.
```

A system can be:
- **Concurrent but not parallel** — single-core multitasking, or Python threads (GIL prevents parallelism)
- **Parallel but not concurrent** — rare; SIMD instructions are an example
- **Both** — multiple cores, each running multiple threads that time-share
- **Neither** — a simple single-threaded sequential program

---

## Concurrency Models

### 1. Preemptive multithreading (OS threads)
The OS controls when threads switch. Any thread can be interrupted at any time. This is what `threading.Thread` in Python, `goroutines` in Go, and `Thread` in Java use under the hood.

- **Pro**: Works automatically; CPU-bound and I/O-bound tasks both benefit
- **Con**: Shared state requires locks; race conditions are possible; context switching has overhead

### 2. Cooperative multitasking (async / event loop)
Threads (or coroutines) voluntarily yield control at defined points — usually when waiting for I/O. Only one runs at a time within the event loop. This is what `asyncio` in Python, `node.js`, and Go's goroutines do when blocked on I/O.

- **Pro**: No race conditions on shared state (only one runs at a time); very low overhead
- **Con**: A task that never yields blocks everything; doesn't use multiple cores for CPU work

```python
import asyncio

async def fetch(url):
    # yields control while waiting for network
    response = await http_get(url)
    return response

# All fetches are in-flight simultaneously on ONE thread
# No threads, no locks, no race conditions
async def main():
    results = await asyncio.gather(
        fetch("https://api1.example.com"),
        fetch("https://api2.example.com"),
        fetch("https://api3.example.com"),
    )
```

### 3. Actor model
Each unit of computation (actor) has its own private state and communicates only by sending messages. No shared memory at all. Used in Erlang, Akka (Java/Scala), and partially in Go via channels.

- **Pro**: No shared state → no race conditions possible
- **Con**: Message passing overhead; more complex for problems that naturally share data

### 4. Multiple processes
Run separate processes, each with their own memory. Communicate via IPC. Python's `multiprocessing` module does this to get around the GIL.

- **Pro**: True isolation; each process gets its own GIL (in Python), its own core
- **Con**: High memory overhead; data must be serialized to cross process boundaries

---

## Race Conditions and Shared State

Whenever multiple threads share mutable data, you risk a **race condition** — the outcome depends on the exact timing of thread scheduling, which is nondeterministic.

```python
# Classic race condition
balance = 1000

def withdraw(amount):
    global balance
    if balance >= amount:       # step 1: check
        # another thread can run here and also see balance >= amount
        balance -= amount       # step 2: update

import threading
t1 = threading.Thread(target=withdraw, args=(800,))
t2 = threading.Thread(target=withdraw, args=(800,))
t1.start(); t2.start()
t1.join(); t2.join()

print(balance)  # Could be 200, -600, or 1000 depending on timing
```

The fix is to make the check-and-update atomic with a lock:

```python
import threading

balance = 1000
lock = threading.Lock()

def withdraw(amount):
    global balance
    with lock:                  # only one thread in here at a time
        if balance >= amount:
            balance -= amount
```

### Deadlocks

Locks introduce the risk of **deadlocks** — two threads each waiting for a lock the other holds:

```
Thread A holds Lock 1, waiting for Lock 2
Thread B holds Lock 2, waiting for Lock 1
→ Neither can proceed. Program hangs forever.
```

Strategies to avoid deadlocks:
- Always acquire multiple locks in the same order
- Use timeouts (`lock.acquire(timeout=1.0)`)
- Minimize lock scope and nesting
- Prefer higher-level abstractions (`queue.Queue`, `asyncio`) that handle locking internally

---

## Synchronization Primitives

### Mutex (Mutual Exclusion Lock)

A mutex ensures only one thread can be inside a critical section at a time. All other threads block until the lock is released.

```python
import threading
lock = threading.Lock()

with lock:       # acquire on entry, release on exit (even if exception)
    balance -= amount
```

Use when: protecting a shared resource that only one thread should access at a time.

### Reentrant Lock (RLock)

A regular mutex deadlocks if the same thread tries to acquire it twice (e.g. in recursive code). An `RLock` tracks the owning thread and allows re-acquisition by the same thread.

```python
rlock = threading.RLock()

def recursive_fn(n):
    with rlock:           # same thread can acquire this multiple times
        if n > 0:
            recursive_fn(n - 1)
```

### Semaphore

A semaphore holds an internal counter (initialized to `n`) and allows up to `n` threads to proceed simultaneously. Each `acquire()` decrements the counter; each `release()` increments it. Threads block when the counter is zero.

```python
sem = threading.Semaphore(3)  # at most 3 threads in this section at once

def connect_to_db():
    with sem:
        # only 3 simultaneous DB connections allowed
        db.query(...)
```

A semaphore with `n=1` behaves like a mutex, but unlike a mutex it has no concept of ownership — any thread can release it. This makes semaphores useful for **signaling** between threads (one thread signals, another waits).

### Event

An event is a simple one-bit signal. One thread waits on it; another sets it. Used to signal that some condition has occurred.

```python
ready = threading.Event()

def worker():
    ready.wait()    # blocks until event is set
    process()

def setup():
    initialise()
    ready.set()     # unblocks all waiting threads
```

### Condition Variable

Combines a lock with the ability to wait for a specific state. Threads release the lock and sleep atomically, then reacquire it when woken.

```python
cond = threading.Condition()
queue = []

def producer():
    with cond:
        queue.append(item)
        cond.notify()       # wake one waiting consumer

def consumer():
    with cond:
        while not queue:
            cond.wait()     # release lock, sleep, reacquire on wake
        item = queue.pop(0)
```

---

## Atomic Operations

An **atomic operation** completes as a single, indivisible step — no other thread can observe it in a partial state. No locks needed.

At the hardware level, CPUs provide atomic instructions: `LOCK XADD` (atomic increment), `CMPXCHG` (compare-and-swap), etc. Languages expose these through standard libraries.

### What makes an operation atomic vs. not

```python
# NOT atomic — three separate steps (read, add, write)
counter += 1

# These ARE atomic in CPython (single bytecode + C call, GIL held throughout):
some_list.append(x)
some_dict[key] = value
x = y               # simple name rebinding
```

In languages without a GIL (Go, Java, C), you must use explicit atomic types:

```go
// Go — explicit atomic operations
import "sync/atomic"

var counter int64

atomic.AddInt64(&counter, 1)           // atomic increment
val := atomic.LoadInt64(&counter)      // atomic read
atomic.StoreInt64(&counter, 0)         // atomic write
atomic.CompareAndSwapInt64(&counter, old, new) // CAS
```

```java
// Java
import java.util.concurrent.atomic.AtomicInteger;

AtomicInteger counter = new AtomicInteger(0);
counter.incrementAndGet();   // atomic
counter.get();               // atomic read
counter.compareAndSet(expected, newVal); // CAS
```

Atomic operations are faster than mutex-protected operations because they use a single CPU instruction rather than acquiring/releasing a lock. Use them for simple counters and flags; use mutexes for multi-step critical sections.

### Compare-and-Swap (CAS)

The fundamental building block of lock-free data structures. Atomically: "if the value is still `expected`, set it to `new`; otherwise do nothing and tell me it changed."

```
CAS(&counter, expected=5, new=6):
  if *counter == 5:
      *counter = 6
      return true
  else:
      return false   ← someone else changed it; caller retries
```

Most lock-free algorithms are retry loops built on CAS.

---

## Thread Safety

A data structure or function is **thread-safe** if it behaves correctly when called concurrently from multiple threads, without the caller needing to add their own synchronization.

### Thread-safe in Python's standard library (CPython)

Due to the GIL and internal locking, these are safe to use from multiple threads without extra locks:

| Operation | Thread-safe? |
|---|---|
| `list.append(x)` | Yes |
| `list.pop()` | Yes |
| `dict[key] = value` | Yes |
| `dict.get(key)` | Yes |
| `queue.Queue.put/get` | Yes — explicitly designed for threading |
| `logging` module | Yes — has internal lock |
| `i += 1` on a global | **No** — read-modify-write, not atomic |
| `if x: x.method()` | **No** — check and call are separate steps |

### Not thread-safe: anything with check-then-act

Even individually thread-safe operations become unsafe when combined:

```python
# UNSAFE — check and act are two separate steps
if key in shared_dict:          # step 1
    value = shared_dict[key]    # step 2 — key may be gone by now

# SAFE — single atomic operation
value = shared_dict.get(key)    # one step, returns None if missing
```

### Immutability as thread safety

Immutable objects need no synchronization — if nothing can change them, there's nothing to race on. In Python, `int`, `str`, `tuple`, `frozenset` are all immutable and inherently thread-safe to share. This is one reason functional programming styles with immutable data are naturally concurrency-friendly.

---

## Choosing the Right Model

```
Is your bottleneck I/O (network, disk, database)?
  └── Yes → Use threads or async
              Is the code complexity acceptable?
                └── Yes, many connections → asyncio (single thread, very scalable)
                └── Simpler code preferred → threading

Is your bottleneck CPU (computation, data processing)?
  └── Yes → Need true parallelism
              Python? → multiprocessing (separate processes)
              Go/Java/C? → threads (true parallel on multiple cores)

Do tasks need to share large amounts of data?
  └── Yes → Threads (shared heap, zero copy) with locks
  └── No  → Processes (isolated, communicate via messages)

Do you need crash isolation?
  └── Yes → Processes
  └── No  → Threads
```

---

## Summary

- A **process** is the OS's isolated container for a running program — its own virtual address space, heap, code, and file descriptors. Processes cannot accidentally access each other's memory.
- A **thread** is a unit of execution within a process. Threads are cheaper to create than processes and share the same heap, but have no memory isolation between them.
- The OS **scheduler** creates the illusion of concurrency by rapidly switching between threads on limited cores. True parallelism requires multiple cores running simultaneously.
- **Concurrency models:**
  - Preemptive OS threads — OS switches automatically; shared state needs locks
  - Cooperative async (`asyncio`) — code yields voluntarily; no locks needed for shared state within one thread
  - Multiple processes — full isolation; communication via IPC (pipes, queues, shared memory)
- **Shared mutable state** between threads requires explicit synchronization (mutexes, semaphores, atomics) to avoid race conditions and deadlocks.
- **Context switch cost:** thread switches are cheap (same page table, TLB stays warm); process switches are expensive (new page table, TLB flush).
