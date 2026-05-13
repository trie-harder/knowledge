# Event Loops, Worker Threads, and CPU Parallelism

## The Event Loop Model (Python asyncio and Node.js)

Both Python asyncio and Node.js are built on the same core idea: a **single-threaded event loop** that handles thousands of concurrent I/O operations without blocking.

```
Event loop (both systems):

  1. Run all ready callbacks/coroutines
  2. Poll OS for I/O events (epoll/kqueue)   ← blocks here if nothing ready
  3. Wake tasks whose I/O completed
  4. Repeat
```

Neither blocks waiting for I/O — they register interest with the OS kernel and move on. This is why one thread can serve thousands of concurrent requests: it's almost always waiting on the OS, not executing code.

### Syntax difference: callbacks vs. coroutines

Node.js uses callbacks/Promises; Python uses coroutines. Functionally equivalent for I/O concurrency.

```javascript
// Node.js
async function fetchData() {
    const data = await db.query('SELECT ...');
    return data;
}
```

```python
# Python
async def fetch_data():
    data = await db.fetch('SELECT ...')
    return data
```

---

## The Main Thread Serves Everything

In both systems, the **main thread handles all incoming requests** — accepting connections, parsing requests, running route handlers, sending responses. One thread, potentially thousands of concurrent connections.

This works because I/O (database queries, network calls, file reads) is non-blocking. The thread never sits idle waiting — it registers the I/O with the OS and immediately moves to the next request.

**The only thing that breaks this: synchronous CPU work.**

```
Main thread — bad: CPU computation in a route handler

  [req 1] → fibonacci(45) → [freezes for 8 seconds] → respond
                              ↑
             [req 2] queued here, not served
             [req 3] queued here, not served
             [req 4] queued here, not served
```

Any route handler that runs significant CPU computation without offloading it stalls every other request for its entire duration.

### The threshold: more than a few milliseconds = offload it

Fine in the main thread: JSON parsing, input validation, simple arithmetic on request data, small sorts.

Must be offloaded: image/video processing, cryptography on large inputs, ML inference, compression, recursive computation, large matrix operations.

### Important: `async` does not make CPU work non-blocking

```python
# WRONG — still blocks the event loop
async def handle():
    result = await cpu_heavy_function()  # no I/O suspension points → runs to completion
```

`async`/`await` only suspends at actual I/O wait points. Pure computation has nowhere to yield. The async keyword changes nothing for CPU-bound work.

---

## CPU Parallelism: Node.js vs. CPython

### Node.js: true CPU parallelism via worker threads

Node.js `worker_threads` are real OS threads with their own V8 isolate — a completely separate JavaScript engine instance with its own heap, its own GC, and its own event loop.

```
Node.js process
├── Main thread  [V8 isolate — own heap, own event loop]
├── Worker 1     [V8 isolate — own heap, own event loop]  ← runs on Core 1
└── Worker 2     [V8 isolate — own heap, own event loop]  ← runs on Core 2
```

Workers run on separate CPU cores simultaneously. **V8 has no GIL** — it uses a tracing GC so there are no per-assignment refcount updates to race on. Multiple workers execute JavaScript in true parallel.

```javascript
// Offload CPU work to a worker, main event loop stays free
const { Worker } = require('worker_threads');

app.get('/compute', async (req, res) => {
    const result = await new Promise((resolve, reject) => {
        const worker = new Worker('./compute-worker.js', { workerData: req.query });
        worker.on('message', resolve);
        worker.on('error', reject);
    });
    res.json({ result });
});
```

Workers cannot share JS objects — each isolate's heap is private. Communication is via `postMessage` (copies data via structured clone) or `SharedArrayBuffer` (raw bytes, explicitly shared, programmer-managed synchronization).

### CPython: no CPU parallelism from threads (GIL)

CPython threads are real OS threads, but the **GIL (Global Interpreter Lock)** ensures only one thread executes Python bytecode at a time. On a 16-core machine, Python threads still only use one core's worth of Python execution.

The GIL exists because CPython uses reference counting for memory management — every object tracks how many pointers point to it. Incrementing/decrementing that counter is not atomic, so without the GIL two threads could corrupt it simultaneously. The GIL serializes all Python bytecode execution to prevent this.

```
CPython with 4 threads, 4-core machine:

Core 0: [Thread A][Thread B][Thread A][Thread C]  ← only one runs at a time
Core 1: [idle]
Core 2: [idle]
Core 3: [idle]
```

**CPython threads ARE useful for I/O concurrency** — the GIL is released during all I/O operations (network, disk, `sleep`). Multiple threads can have requests in-flight simultaneously; they just can't compute simultaneously.

### CPython: true CPU parallelism via processes

`ProcessPoolExecutor` / `multiprocessing` gives real CPU parallelism — separate OS processes, each with their own Python interpreter, their own GIL, running on separate cores.

```python
from concurrent.futures import ProcessPoolExecutor
import asyncio

pool = ProcessPoolExecutor(max_workers=4)

async def handle_compute(n):
    loop = asyncio.get_event_loop()
    # offload to a process — doesn't block the event loop
    result = await loop.run_in_executor(pool, heavy_computation, n)
    return result
```

---

## Comparison Table

| | Node.js workers | CPython threads | CPython processes |
|---|---|---|---|
| True CPU parallelism | **Yes** | No (GIL) | **Yes** |
| I/O concurrency | Yes | Yes (GIL released during I/O) | Yes |
| Startup cost | Low (new V8 isolate) | Very low | High (fork new process) |
| Shared memory | `SharedArrayBuffer` only | Yes — shared heap (with locks) | No — explicit `shared_memory` |
| Communication cost | `postMessage` (structured clone) | Direct pointer (zero copy) | `pickle` serialization |
| Memory per worker | Medium (V8 isolate overhead) | Low (shared heap) | High (full process + interpreter) |

### Why Node.js has no GIL

V8 uses a **tracing garbage collector** — application threads never increment or decrement a reference counter on object assignment. There's nothing to race on, so no global lock is needed. Isolated worker heaps reinforce this: no JS objects are shared, so there's no cross-thread mutation of shared state at the language level.

Python's reference counting model requires every pointer operation to update a counter — a race condition without serialization. That serialization is the GIL.

---

## Python 3.13 No-GIL (PEP 703)

CPython 3.13 ships an experimental no-GIL build (`python3.13t`) that solves this with **biased reference counting**: objects have a fast non-atomic local refcount (used when only one thread touches them) and a slow atomic shared refcount (used when multiple threads share the object). Single-threaded performance is within ~5% of the GIL build.

With no-GIL CPython, threads get true CPU parallelism and share the same heap — closer to Go/Java than to the current CPython model, and more ergonomic than Node.js workers (no serialization required to share data between threads).

---

## Summary: When to Use What

| Situation | Node.js | Python |
|---|---|---|
| Many concurrent I/O-bound requests | Main event loop | `asyncio` event loop |
| CPU-heavy work alongside I/O | `worker_threads` | `ProcessPoolExecutor` with `run_in_executor` |
| High-volume CPU-only work | Worker thread pool (`piscina`) | `multiprocessing.Pool` |
| Shared mutable data between parallel workers | `SharedArrayBuffer` + `Atomics` | `multiprocessing.shared_memory` + locks |
| Future: CPU parallelism with shared objects | N/A (isolated heaps by design) | CPython 3.13t no-GIL threads |
