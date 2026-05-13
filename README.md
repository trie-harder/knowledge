# knowledge
Knowledge bank of all things technical or non-technical that I'm curious about

## Contents

| File | Summary |
|---|---|
| [hardware/cpu-cache-and-atomics.md](hardware/cpu-cache-and-atomics.md) | CPU memory hierarchy (registers, L1/L2/L3, RAM), cache lines, MESI coherence protocol, and why atomic operations are expensive |
| [os/processes-threads-concurrency.md](os/processes-threads-concurrency.md) | What processes and threads are, how the OS schedules them, concurrency vs. parallelism, synchronization primitives, and when to use each model |
| [os/ram-and-memory.md](os/ram-and-memory.md) | Physical RAM, virtual address spaces, MMU, page tables, TLB, swapping, shared memory, and memory protection |
| [programming/concurrency/event-loops-and-parallelism.md](programming/concurrency/event-loops-and-parallelism.md) | Python asyncio vs. Node.js event loops, CPU offload strategies, worker threads, and why CPython can't do true thread parallelism |
| [programming/python/gil.md](programming/python/gil.md) | The CPython GIL — why it exists, what it protects, when it's released, comparison with other runtimes, and PEP 703 removal |
| [programming/python/memory_model.md](programming/python/memory_model.md) | How CPython allocates memory — heap-only objects, reference counting, cyclic GC, arenas/pools, and practical implications |
| [programming/python/primitives.md](programming/python/primitives.md) | Python's built-in scalar types, why there are no true primitives, how `bool` subclasses `int` at the C level, comparison with Go and Java |
