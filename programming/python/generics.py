"""
Generic Classes in Python
=========================
Using TypeVar + Generic (Python 3.9+) or the new syntax (Python 3.12+).

Why generics exist — comparison across languages
-------------------------------------------------
In statically typed languages (Go, Java, C++), generics are NOT optional.
Without them you must either:
  (a) duplicate code per type — IntStack, StringStack, FloatStack...
  (b) use Any / interface{} — destroys all type safety, requires manual casts

Python is dynamically typed, so generics are a static analysis tool only.
The runtime doesn't enforce them — mypy/pyright do. If you don't run a type
checker, they're just documentation.

Go (before 1.18) — the two bad options:
-----------------------------------------
  Option A — code duplication:
    type IntStack struct { data []int }
    type StringStack struct { data []string }  // copy-paste forever

  Option B — use interface{} (any):
    func (s *Stack) Pop() interface{} { ... }
    v := s.Pop()
    v + 1           // compile error — v is interface{}, not int
    v.(int) + 1     // must type-assert manually → runtime panic if wrong

Go (1.18+) — with generics:
-----------------------------
  type Stack[T any] struct { data []T }

  func (s *Stack[T]) Pop() T { ... }

  s := Stack[int]{}
  s.Push("hello")   // compile error — caught at build time
  v := s.Pop()      // v is int — no assertion needed
  v + 1             // works

Go constraints (equivalent to Python's TypeVar bound/constraints):
  type Number interface { int | float64 }    // constrained type param
  func Sum[T Number](items []T) T { ... }   // only int or float64 allowed

Comparison summary:
  Python ≤3.11  TypeVar + Generic[T]    — static only, runtime erased
  Python  3.12  class Foo[T]            — native syntax, same semantics
  Go      1.18  [T any] / [T Constraint] — enforced at compile time
  Java    5+    <T> / <T extends Foo>   — enforced at compile time (type erasure at runtime like Python)
  C++           template<typename T>    — generates specialised code per type (no erasure)
"""

from __future__ import annotations
from collections import deque
from typing import TypeVar, Generic, Iterator

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


# ── Single type parameter ─────────────────────────────────────────────────────

class Stack(Generic[T]):
    """LIFO stack — push/pop from the same end."""

    def __init__(self) -> None:
        self._data: list[T] = []

    def push(self, item: T) -> None:
        self._data.append(item)

    def pop(self) -> T:
        return self._data.pop()

    def peek(self) -> T:
        return self._data[-1]

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return bool(self._data)


class FifoQueue(Generic[T]):
    """FIFO queue backed by a deque."""

    def __init__(self) -> None:
        self._queue: deque[T] = deque()

    def push(self, item: T) -> None:
        self._queue.appendleft(item)

    def pop(self) -> T:
        return self._queue.pop()

    def __len__(self) -> int:
        return len(self._queue)


# ── Multiple type parameters ──────────────────────────────────────────────────

class Pair(Generic[K, V]):
    """Immutable typed pair — useful as a return type or lightweight record."""

    def __init__(self, key: K, value: V) -> None:
        self.key = key
        self.value = value

    def swap(self) -> Pair[V, K]:
        return Pair(self.value, self.key)

    def __repr__(self) -> str:
        return f"Pair({self.key!r}, {self.value!r})"


# ── Constrained TypeVar ───────────────────────────────────────────────────────
# bound= restricts T to a type or any of its subclasses.
# constraints (positional args) restricts T to exactly those types.

Numeric = TypeVar('Numeric', int, float)   # only int or float, nothing else


class BoundedList(Generic[Numeric]):
    """List that only accepts numeric types — rejects str, list, etc."""

    def __init__(self, lo: Numeric, hi: Numeric) -> None:
        self._lo = lo
        self._hi = hi
        self._items: list[Numeric] = []

    def add(self, item: Numeric) -> None:
        if not (self._lo <= item <= self._hi):
            raise ValueError(f"{item} out of range [{self._lo}, {self._hi}]")
        self._items.append(item)

    def __iter__(self) -> Iterator[Numeric]:
        return iter(self._items)


# ── Generic with bound (subtype constraint) ───────────────────────────────────

class Comparable:
    """Minimal protocol-like base — anything that supports <."""
    def __lt__(self, other: object) -> bool: ...


CT = TypeVar('CT', bound='Comparable')


def find_min(items: list[CT]) -> CT:
    """Works for any type that supports comparison — not just built-ins."""
    result = items[0]
    for item in items[1:]:
        if item < result:
            result = item
    return result


# ── Python 3.12 syntax (no TypeVar boilerplate) ───────────────────────────────
# Uncomment if on 3.12+:
#
# class Stack[T]:
#     def __init__(self) -> None:
#         self._data: list[T] = []
#
#     def push(self, item: T) -> None:
#         self._data.append(item)
#
#     def pop(self) -> T:
#         return self._data.pop()
#
# def find_min[T: Comparable](items: list[T]) -> T:
#     ...


# ── Usage examples ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Stack[int] — type checker will reject push("hello")
    s: Stack[int] = Stack()
    s.push(1)
    s.push(2)
    print(s.pop())   # 2

    # FifoQueue[str]
    q: FifoQueue[str] = FifoQueue()
    q.push("a")
    q.push("b")
    print(q.pop())   # "a"

    # Pair[str, int]
    p = Pair("age", 30)
    print(p.swap())  # Pair(30, 'age')

    # BoundedList — only int or float accepted by type checker
    bl: BoundedList[int] = BoundedList(0, 100)
    bl.add(50)
    bl.add(101)  # raises ValueError at runtime
