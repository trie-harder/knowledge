# CPU Cores, Cache, and Atomic Operations

## The Memory Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                         CPU DIE (chip)                          │
│                                                                 │
│  ┌─────────────────┐      ┌─────────────────┐                  │
│  │     Core 0      │      │     Core 1      │                  │
│  │  ┌───────────┐  │      │  ┌───────────┐  │                  │
│  │  │ Registers │  │      │  │ Registers │  │                  │
│  │  │  ~32 × 8B │  │      │  │  ~32 × 8B │  │                  │
│  │  └─────┬─────┘  │      │  └─────┬─────┘  │                  │
│  │        │ 1 cycle│      │        │ 1 cycle│                  │
│  │  ┌─────▼─────┐  │      │  ┌─────▼─────┐  │                  │
│  │  │  L1 Cache │  │      │  │  L1 Cache │  │                  │
│  │  │   32 KB   │  │      │  │   32 KB   │  │                  │
│  │  │  ~4 cycles│  │      │  │  ~4 cycles│  │                  │
│  │  └─────┬─────┘  │      │  └─────┬─────┘  │                  │
│  │  ┌─────▼─────┐  │      │  ┌─────▼─────┐  │                  │
│  │  │  L2 Cache │  │      │  │  L2 Cache │  │                  │
│  │  │  256 KB   │  │      │  │  256 KB   │  │                  │
│  │  │ ~12 cycles│  │      │  │ ~12 cycles│  │                  │
│  │  └─────┬─────┘  │      │  └─────┬─────┘  │                  │
│  └────────┼────────┘      └────────┼────────┘                  │
│           └──────────┬─────────────┘                           │
│                ┌─────▼──────┐                                   │
│                │  L3 Cache  │  ← shared across all cores        │
│                │  8–32 MB   │                                   │
│                │ ~40 cycles │                                   │
│                └─────┬──────┘                                   │
└──────────────────────┼─────────────────────────────────────────┘
                       │
              ┌────────▼────────┐
              │   RAM (DIMM)    │  ← off-chip, connected via memory bus
              │   8–128 GB      │
              │  ~100 cycles    │
              └─────────────────┘
```

| Level | Size | Latency | Shared? |
|---|---|---|---|
| Registers | ~256 bytes | 1 cycle | No — per core |
| L1 | 32 KB | ~4 cycles | No — per core |
| L2 | 256 KB | ~12 cycles | No — per core |
| L3 | 8–32 MB | ~40 cycles | Yes — all cores |
| RAM | GBs | ~100 cycles | Yes — all cores |

The CPU can only operate on data in **registers**. Everything else must be loaded there first. Each cache level is a progressively larger, slower buffer. A cache miss at L1 falls through to L2, then L3, then RAM — each step is a significant penalty.

The cache reads and writes in **cache lines** of 64 bytes — never individual bytes. If you touch one byte, the entire 64-byte chunk surrounding it is loaded into L1.

---

## Why Atomic Operations Are Expensive

A regular increment is three separate micro-operations:

```
LOAD  [address] → register    # read from cache
ADD   register, 1             # compute in register
STORE register → [address]    # write back to cache
```

On a single core, nothing interrupts this. On multiple cores, another core can read and write the same address between your LOAD and STORE — a race condition.

An **atomic** increment (`LOCK XADD` on x86) must execute as one indivisible unit. To guarantee that, the CPU must have **exclusive ownership** of the cache line — no other core can hold a copy.

---

## The MESI Cache Coherence Protocol

Every cache line in every core's L1/L2 is tagged with a state:

```
M — Modified   this core has the only copy, and it's been written (dirty)
E — Exclusive  this core has the only copy, not yet written
S — Shared     multiple cores have a read-only copy
I — Invalid    this core's copy is stale, must re-fetch
```

For a **normal read**: a core only needs S (shared) state — multiple cores read simultaneously, no coordination needed.

For a **normal write**: a core sends an "invalidate" to others asynchronously and proceeds — it doesn't wait for acknowledgement.

For an **atomic read-modify-write**: the core issues a **Read For Ownership (RFO)** request — a synchronous message that simultaneously fetches the value AND forces all other cores to invalidate their copies. The core must **wait** for every other core to acknowledge before it can proceed.

```
Core 0 executes LOCK XADD [address]:

  Core 0 → bus: "I need exclusive ownership (RFO)"
                         │
            ┌────────────┴────────────┐
            ▼                         ▼
         Core 1                    Core 2
    "ok, invalidating"         "ok, invalidating"
    L1 line → state I          L1 line → state I
            │                         │
            └────────────┬────────────┘
                         ▼
         Core 0 waits for all acknowledgements
         Core 0: READ → ADD → WRITE   ← now truly atomic
```

That round-trip through L3 costs **40–300+ cycles** depending on contention, vs. ~4 cycles for a cached non-atomic read.

---

## Contention Makes It Worse Non-Linearly

When multiple cores all atomically modify the same address, they fully serialize — each waits for the previous to finish and hand over ownership:

```
4 cores all atomically incrementing the same counter:

Core 0 gets ownership → Cores 1,2,3 invalidated, wait
Core 1 gets ownership → Cores 0,2,3 invalidated, wait
Core 2 gets ownership → Cores 0,1,3 invalidated, wait
Core 3 gets ownership → Cores 0,1,2 invalidated, wait
```

At this point you have a hardware-enforced serial queue. Adding more cores makes it strictly worse — more invalidation messages, more waiting.

---

## Why This Caused CPython's 5x Slowdown

CPython touches a refcount on virtually every operation — every assignment, every function argument, every return value, every scope exit. Making all of those atomic means paying 40–100 cycles instead of 4 cycles for the most frequent operation in the interpreter, even with zero other threads running. The overhead is purely from the CPU needing to acquire exclusive cache line ownership on every single object touch.

This is also why the biased reference counting in PEP 703 works: it keeps a **non-atomic local refcount** for the common case (one thread owns the object) and only pays the atomic cost when an object is genuinely shared between threads. Most objects never become shared, so the atomic path is the exception rather than the hot path.

---

## Practical Implications

**Prefer per-core data over shared atomics for hot counters:**
```c
// Bad — all cores contend on one atomic
atomic_int global_counter;
// on each core: atomic_fetch_add(&global_counter, 1);

// Good — each core writes to its own slot, sum once when needed
int per_core_counter[NUM_CORES];  // each on its own cache line
// on core N: per_core_counter[N]++;  // no atomic needed
// to read total: sum all slots
```

**Array layout matters more than algorithm complexity for real-world speed:**
A tight loop on a contiguous array (NumPy, C array) stays in L1/L2 and runs at full speed. A loop over Python list objects chases pointers across the heap — each object is a cache miss into a random RAM location.

---

## Summary

- CPUs don't read RAM directly — data moves up a cache hierarchy: **RAM → L3 → L2 → L1 → registers**. Each level is smaller, faster, and closer to the core.
- The unit of transfer is a **64-byte cache line**, not individual bytes. Loading one byte loads 64.
- **Atomic operations** require exclusive ownership of the cache line: the CPU broadcasts an invalidation to all other cores and waits for acknowledgements before it can read-modify-write. This is called an RFO (Read For Ownership).
- **Cost:** ~4 cycles for a cached non-atomic access vs. **40–300+ cycles** for an atomic under contention — a 10–75x difference.
- This is why making CPython's `ob_refcnt` updates atomic caused a **~5x single-threaded slowdown** — reference count updates are the most frequent operation in the interpreter.
- **PEP 703** (no-GIL Python) solves this with biased reference counting: non-atomic by default, atomic only when an object is genuinely shared between threads.
- **Layout matters:** tight loops over contiguous arrays (NumPy, C arrays) stay in L1/L2 cache. Looping over Python lists chases pointers to scattered heap objects — one cache miss per element.
