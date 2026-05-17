# Demonstrates when and why you need `global` vs `nonlocal` in nested helpers.


# ---------------------------------------------------------------------------
# 1. Mutating a mutable module-level object — no `global` needed
# ---------------------------------------------------------------------------

results = []

def collect():
    def helper():
        results.append(1)   # mutating, not rebinding — no global needed
    helper()

collect()
assert results == [1]


# ---------------------------------------------------------------------------
# 2. Rebinding a module-level immutable — `global` required
# ---------------------------------------------------------------------------

count = 0

def increment():
    def helper():
        global count        # without this, `count += 1` raises UnboundLocalError
        count += 1
    helper()

increment()
assert count == 1


# ---------------------------------------------------------------------------
# 3. Rebinding an enclosing-function variable — `nonlocal` required
# ---------------------------------------------------------------------------

def make_counter():
    count = 0

    def increment():
        nonlocal count      # one level up into make_counter's scope
        count += 1
        return count

    return increment

counter = make_counter()
assert counter() == 1
assert counter() == 2


# ---------------------------------------------------------------------------
# 4. What happens without global/nonlocal — UnboundLocalError
# ---------------------------------------------------------------------------

x = 10

def broken():
    def helper():
        # x += 1          # would raise UnboundLocalError: x referenced before assignment
        pass              # Python sees the assignment and treats x as local, but
    helper()              # it hasn't been assigned yet in this scope


# ---------------------------------------------------------------------------
# 5. Realistic use case: module-level cache counter
# ---------------------------------------------------------------------------

_cache = {}
_cache_hits = 0

def get(key):
    def _record_hit():
        global _cache_hits
        _cache_hits += 1

    if key in _cache:
        _record_hit()
        return _cache[key]
    return None

_cache["a"] = 42
get("a")
get("a")
assert _cache_hits == 2


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
#
# | Variable lives in    | You want to reassign  | Keyword needed |
# |----------------------|-----------------------|----------------|
# | Module (global)      | Yes                   | global         |
# | Enclosing function   | Yes                   | nonlocal       |
# | Anywhere             | No (mutate only)      | Neither        |
#
# `global` and `nonlocal` are only needed for rebinding (x = ..., x += 1 on
# immutables). Mutating a mutable object (list.append, dict.update, etc.)
# works without either keyword because you're not changing what the name
# points to — you're changing the object itself.

