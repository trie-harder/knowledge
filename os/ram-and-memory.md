# RAM and Memory: Virtual Addresses, Physical Addresses, and How Processes Use Them

## Physical RAM: What It Actually Is

RAM (Random Access Memory) is a flat array of bytes attached to your CPU via a memory bus. Every byte has a unique **physical address** — a number from `0` to `(RAM size - 1)`.

On a machine with 16GB of RAM:
- Physical address `0x0000_0000` → first byte of RAM
- Physical address `0x3FFF_FFFF` → last byte of 16GB

The CPU reads and writes RAM by putting an address on the memory bus and signaling read or write. This is the hardware reality everything else builds on.

```
CPU ←──── memory bus ────→ RAM chips
      (address + data)
```

---

## The Problem With Direct Physical Addresses

If every process used physical addresses directly, several catastrophic things would happen:

1. **Process A could read Process B's memory** — no isolation, no security
2. **Two programs compiled to run at address `0x1000` couldn't both run at once** — address conflict
3. **Fragmented free RAM couldn't be used efficiently** — holes between allocations would be wasted
4. **A process could accidentally (or maliciously) overwrite the OS kernel** — which lives in RAM too

The solution: **virtual address spaces**.

---

## Virtual Address Spaces

Every process gets its own **virtual address space** — a private, independent range of addresses it believes it owns entirely. On a 64-bit system, this space is enormous (typically 0 to 2⁴⁸, about 256 terabytes) even though the machine may have only 16GB of physical RAM.

The addresses a process uses — the ones in your code, your pointers, your stack pointer — are all **virtual addresses**. The CPU translates them to physical addresses on every memory access, invisibly, in hardware.

```
Process A's view              Process B's view
(virtual addresses)           (virtual addresses)

0x0000_0000_0000              0x0000_0000_0000
     │                             │
     │  "I own all of this"        │  "I own all of this"
     │                             │
0xFFFF_FFFF_FFFF              0xFFFF_FFFF_FFFF

Both processes see the same virtual address range.
They map to completely different physical RAM pages.
```

Two processes can both have a local variable at virtual address `0x7ffe_1234`. Those identical virtual addresses map to different physical RAM locations. They never interfere.

---

## The Memory Management Unit (MMU)

The translation from virtual to physical address is done by hardware: the **MMU** (Memory Management Unit), a dedicated circuit built into the CPU.

On every single memory access — every instruction fetch, every variable read, every pointer dereference — the MMU:

1. Takes the virtual address from the CPU
2. Looks up where it maps in the current process's **page table**
3. Returns the corresponding physical address
4. The physical address goes out on the memory bus to RAM

This happens billions of times per second, in nanoseconds, in hardware. Software never sees it happening.

```
CPU generates                MMU translates              RAM accessed
virtual address   ────────→  virtual → physical  ──────→ physical address
0x7ffe_0010                  (page table lookup)          0x3A2C_0010
```

---

## Pages: The Unit of Translation

The MMU doesn't translate individual bytes — that would require a table with billions of entries. Instead it works in **pages**: fixed-size chunks, typically **4KB** (4096 bytes) on x86.

Every virtual address is split into two parts:
- **Page number** — which 4KB chunk this address belongs to
- **Offset** — the position within that 4KB chunk

```
Virtual address (48-bit on x86-64):
┌─────────────────────────────────┬──────────────┐
│         Page number             │    Offset    │
│         (upper bits)            │  (lower 12)  │
└─────────────────────────────────┴──────────────┘

The MMU translates the page number → physical page frame number
The offset stays the same (same position within the page)
```

The page table maps virtual page numbers to physical page frame numbers. One entry per page, not one per byte.

### Physical frames

A **physical frame** (or "page frame") is the physical counterpart to a virtual page — a fixed-size, aligned 4KB slot carved out of physical RAM. The MMU divides all of RAM into consecutive numbered frames:

```
Physical RAM (16GB = ~4 million frames of 4KB each)

Frame 0:      0x0000_0000 – 0x0000_0FFF  (4KB)
Frame 1:      0x0000_1000 – 0x0000_1FFF  (4KB)
Frame 2:      0x0000_2000 – 0x0000_2FFF  (4KB)
...
Frame 0x3A2C: 0x3A2C_0000 – 0x3A2C_0FFF (4KB)
...
Frame N:      0x3FFF_F000 – 0x3FFF_FFFF  (4KB)
```

A page table entry stores a **frame number**. The physical address is just the frame's base address plus the offset from the virtual address:

```
Virtual:  page 0x0002, offset 0x1234
Table:    page 0x0002 → frame 0x3A2C
Physical: 0x3A2C_0000 + 0x1234 = 0x3A2C_1234
```

The OS maintains a global free-frame list and hands frames out on demand. "Frame" is purely a physical concept — there is nothing special about the memory inside one, it's just a named 4KB slot in the flat RAM array.

---

## Page Tables: The Translation Map

Each process has its own **page table** — a data structure maintained by the OS in RAM that records which virtual pages map to which physical frames.

```
Process A's page table:

Virtual Page │ Physical Frame │ Flags
─────────────┼────────────────┼──────────────────
0x0001       │ 0x3A2C         │ read/write
0x0002       │ 0x1F0A         │ read/write
0x0003       │ 0x8812         │ read-only (code)
0x0004       │ NOT PRESENT    │ → page fault (not allocated yet)
...

Process B's page table:

Virtual Page │ Physical Frame │ Flags
─────────────┼────────────────┼──────────────────
0x0001       │ 0x5C44         │ read/write  ← different physical frame than A's 0x0001
0x0002       │ 0x2201         │ read/write
...
```

When the OS switches from Process A to Process B, it loads Process B's page table address into a CPU register (`CR3` on x86). Every subsequent memory access uses B's table. Process A's physical pages become invisible to the CPU.

### Page faults

If a process accesses a virtual page with no mapping (the "NOT PRESENT" case), the CPU raises a **page fault** — an interrupt that transfers control to the OS kernel. The OS decides what to do:

- If the address is valid but the page hasn't been allocated yet (e.g. stack growing downward) → allocate a physical frame, create the mapping, return
- If the page was swapped to disk → read it back into RAM, create the mapping, return
- If the address is completely invalid (bug, null pointer dereference) → send SIGSEGV to the process (segmentation fault)

---

## The TLB: Caching Translations

Looking up the page table in RAM on every memory access would double the cost of every operation. The CPU has a hardware cache specifically for page table entries: the **TLB** (Translation Lookaside Buffer).

The TLB stores the most recently used virtual→physical translations. A TLB hit (translation cached) takes ~1 cycle. A TLB miss (must walk the page table in RAM) takes ~10-100 cycles.

```
Virtual address arrives at MMU
         │
         ▼
   TLB lookup
   ┌──────────────────────┐
   │ Hit? Return physical │ ← ~1 cycle
   │ address immediately  │
   └──────────────────────┘
         │ Miss
         ▼
   Walk page table in RAM  ← ~10-100 cycles
   Cache result in TLB
   Return physical address
```

### Why this matters for processes vs. threads

**Process context switch**: the OS loads a completely different page table. The TLB entries for the old process are now wrong and must be **flushed** (invalidated). After a process switch, every memory access is a TLB miss until the cache warms up again. This is expensive.

**Thread context switch within a process**: the page table stays the same (threads share an address space). The TLB is not flushed. Translations remain valid. Much cheaper.

This is one of the core reasons threads have lower context-switch overhead than processes.

---

## How a Process's Virtual Address Space Is Organized

The OS lays out a process's virtual address space in a standard arrangement:

```
High virtual addresses (e.g. 0x7FFF_FFFF_FFFF on Linux x86-64)
┌──────────────────────────────────┐
│           Stack                  │ ← grows downward
│           ↓                      │   function frames, local variables
│                                  │   fixed size limit (ulimit -s, default 8MB)
│                                  │
│     (unmapped — large gap)       │ ← accessing this = stack overflow (SIGSEGV)
│                                  │
│           ↑                      │
│           Heap                   │ ← grows upward
│     (malloc, new, etc.)          │   managed by runtime allocator
│                                  │
│     Memory-mapped files          │ ← mmap() — files mapped into address space
│     Shared libraries (.so/.dll)  │ ← libc, libpthread, etc.
│                                  │
│     BSS segment                  │ ← zero-initialized global/static variables
│     Data segment                 │ ← initialized global/static variables
│     Text segment (Code)          │ ← program instructions, read-only
│                                  │
Low virtual addresses (0x0000_0000_0000)
(address 0 is intentionally unmapped — null pointer dereference → SIGSEGV)
```

---

## How Threads Share the Address Space

All threads in a process share the **same virtual address space** — the same page table, the same heap, the same code. The OS does not create a separate address space per thread.

What each thread gets privately:
- Its own **stack** — a range of virtual addresses allocated in the address space for that thread's exclusive use
- Its own **CPU register state** (saved/restored on context switch)
- Its own **thread-local storage (TLS)** — a small per-thread data area

```
Process virtual address space with 3 threads:

┌───────────────────────────────────────────────────────┐
│  Thread 3 Stack (0x7FFE_8000 – 0x7FFF_0000)           │
│  Thread 2 Stack (0x7FFD_8000 – 0x7FFE_0000)           │
│  Thread 1 Stack (0x7FFC_8000 – 0x7FFD_0000)  ← main  │
│                                                       │
│  Heap (shared — all threads allocate here)            │
│                                                       │
│  Shared libraries                                     │
│  Code (read-only, shared)                             │
└───────────────────────────────────────────────────────┘
         │              │              │
         │              │              │
    mapped to       mapped to      mapped to
    physical RAM    physical RAM   physical RAM
    (same pages)    (same pages)   (same pages)
```

A pointer to a heap object has the same virtual address in all three threads — and maps to the same physical RAM. This is why thread communication via shared memory is so fast (no copying) and why it requires locks (no isolation).

---

## Virtual Memory Beyond Physical RAM: Swapping

The virtual address space can be **larger than physical RAM**. The OS keeps rarely-used pages on disk (in a **swap partition** or swap file) and loads them back on demand when accessed.

```
Virtual pages of a process:

Page 1 → Physical frame 0x3A2C   (in RAM, recently used)
Page 2 → Physical frame 0x1F0A   (in RAM)
Page 3 → DISK: swap offset 0x800 (swapped out — not in RAM)
Page 4 → Physical frame 0x8812   (in RAM)

When the CPU accesses Page 3:
  1. MMU sees "not present" → page fault
  2. OS reads Page 3 from disk into a free physical frame
  3. OS updates page table: Page 3 → Physical frame 0xAA01
  4. CPU retries the instruction (transparent to the program)
```

This is why a machine can run more memory than it physically has — at the cost of disk I/O speed when pages are swapped. A system that is constantly swapping (thrashing) becomes extremely slow.

---

## Shared Memory Between Processes

Normally processes are isolated. But the OS can map the **same physical page** into two different processes' virtual address spaces. Both processes see different virtual addresses, but they point to the same physical RAM:

```
Process A virtual space          Process B virtual space
0x7F00_0000 ──────────┐          0x6E00_0000 ──────────┐
                       │                                 │
                       └──── Physical Frame 0x5C44 ────┘
                                (same physical RAM)
```

This is `mmap(MAP_SHARED)` on Unix or `CreateFileMapping` on Windows. It's the fastest possible IPC — no copying, no kernel involvement for individual reads/writes, just direct memory access to the shared pages. Used by databases, video players, and high-performance message queues.

---

## Memory Protection Flags

Each page table entry carries **permission bits** that the MMU enforces on every access:

| Flag | Meaning | Violation result |
|---|---|---|
| Read | Page can be read | SIGSEGV |
| Write | Page can be written | SIGSEGV |
| Execute | Page can be executed as code | SIGSEGV (or SIGILL) |
| User/Kernel | Accessible from user space or kernel only | SIGSEGV |

This is what enforces:
- **Code is read-only** — a bug can't accidentally overwrite its own instructions
- **Stack/heap are not executable** — prevents many classes of exploits (NX bit / DEP)
- **Kernel memory is inaccessible** — user programs can't read kernel data structures
- **Meltdown** was a bug where CPUs were incorrectly allowing speculative reads across this kernel boundary

---

## Memory Usage: What the Numbers Mean

```bash
# Linux tools for inspecting memory

# Per-process virtual and resident memory
ps aux | grep myprogram
# VSZ = virtual size (all virtual pages, including not-in-RAM ones)
# RSS = resident set size (pages actually in physical RAM right now)

# Detailed per-process memory map
cat /proc/1042/maps   # 1042 = PID

# System-wide memory
free -h
# total = physical RAM
# used  = RAM in use
# buff/cache = RAM used by OS for disk caching (reclaimable)
# available = how much can be given to processes right now
```

**VSZ vs RSS** is often confusing:
- A process may show 2GB VSZ (virtual) but only 200MB RSS (resident/physical)
- The other 1.8GB of virtual space is either: not yet touched (lazy allocation), memory-mapped files not yet read, or pages swapped to disk
- The OS doesn't actually allocate physical RAM until a page is first written to (demand paging)

---

## Summary: The Full Picture

```
Your code                     OS + Hardware
────────────────              ──────────────────────────────────────────────

int x = 42;                   Compiler places x on the stack
&x = 0x7ffe_1234              Virtual address — what your code sees

                              MMU translates:
                              0x7ffe_1234 → page 0x7ffe, offset 0x1234
                              Page table: page 0x7ffe → frame 0x3A2C
                              Physical address: 0x3A2C_1234

                              Memory bus: READ 0x3A2C_1234 → returns 42

Thread A and Thread B         Both use virtual addresses in the same range
sharing a heap object:        Both virtual addresses map to the same physical frame
                              MMU enforces this silently

Process A and Process B       Each has its own page table
with the same virtual addr:   Same virtual address → different physical frames
                              MMU enforces isolation silently

Swap:                         Page table entry marked "not present"
                              CPU page faults → OS reads from disk → updates table
                              Transparent to your code
```

The virtual address system is one of the most important abstractions in all of computing. It gives every process the illusion of owning the entire machine while enforcing complete isolation — all enforced in hardware at full CPU speed.
