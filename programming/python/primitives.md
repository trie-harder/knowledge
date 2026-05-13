# Python Primitives in Python 3

## What Are Primitives?

In many compiled languages, **primitives** are the most basic data types built directly into the language — stored by value, typically on the stack, with fixed size and no associated methods.

Python 3 has **no true primitives** in the same sense. Everything in Python is an **object**, including integers, floats, booleans, and strings. This is a fundamental design difference from languages like Java or Go.

---

## Python 3 Built-in Scalar Types

| Type      | Example              | Notes                                        |
|-----------|----------------------|----------------------------------------------|
| `int`     | `x = 42`             | Arbitrary precision; no overflow              |
| `float`   | `x = 3.14`           | 64-bit IEEE 754 double                        |
| `bool`    | `x = True`           | Subclass of `int` (`True == 1`, `False == 0`) |
| `complex` | `x = 2 + 3j`         | Built-in complex number type                  |
| `str`     | `x = "hello"`        | Immutable Unicode sequence                    |
| `bytes`   | `x = b"hello"`       | Immutable sequence of bytes                   |
| `NoneType`| `x = None`           | Singleton null value                          |

### Key Python Behaviors

```python
x = 10
y = x        # y and x point to the same object
print(id(x) == id(y))  # True — same object in memory

x = 11       # x now points to a NEW int object
print(id(x) == id(y))  # False

# Everything is an object
print(type(42))        # <class 'int'>
print((42).bit_length()) # 6 — methods work directly on literals

# Booleans are ints
print(True + True)     # 2
print(isinstance(True, int))  # True

# Python ints have arbitrary precision
big = 10 ** 1000  # no overflow, just works
```

---

## How `bool` Is a Subclass of `int` (CPython Internals)

Python needed `True` and `False` to work like numbers (`True + True == 2`). Rather than build a separate type from scratch, `bool` **extends** `int` at the C level — the same concept as subclassing in Python, but implemented in C inside the interpreter.

### Three things make this work

**1. `bool` declares `int` as its parent in C.**

Every built-in type is a `PyTypeObject` struct with a `tp_base` field pointing to its parent. For `bool`, that field points directly at `PyLong_Type` (the C name for `int`). This single pointer is the entire inheritance declaration:

```c
// Objects/boolobject.c
PyTypeObject PyBool_Type = {
    "bool",
    // ...
    &PyLong_Type,   /* tp_base — bool inherits from int */
    // ...
    bool_new,       /* tp_new */
};
```

When the interpreter starts, `PyType_Ready(&PyBool_Type)` fills in any unset slots by copying them from `PyLong_Type` — arithmetic, hashing, comparison, etc. That's the inheritance mechanism.

**2. `True` and `False` are just integers wearing a `bool` label.**

They're the same C struct used for every integer (`_longobject`), holding the values `1` and `0`. The only difference is their type tag says `bool`:

```c
// False: a _longobject with ob_type=PyBool_Type and value 0
struct _longobject _Py_FalseStruct = {
    PyObject_HEAD_INIT(&PyBool_Type)
    { .lv_tag = _PyLong_FALSE_TAG, { 0 } }
};

// True: same struct, value 1
struct _longobject _Py_TrueStruct = {
    PyObject_HEAD_INIT(&PyBool_Type)
    { .lv_tag = _PyLong_TRUE_TAG, { 1 } }
};
```

These two structs are created once at interpreter startup and marked **immortal** — their reference count never drops to zero.

**3. `bool()` can never create a new object — it always returns one of the two singletons.**

```c
PyObject *PyBool_FromLong(long ok)
{
    return ok ? Py_True : Py_False;  // always the pre-existing static
}
```

Because of this, `True` and `False` are always the exact same object in memory, no matter how many variables point to them:

```python
a = True
b = True
print(a is b)        # True — same object, always
print(id(a) == id(b)) # True — same memory address

# Unlike regular ints outside the small-int cache:
x = 1000
y = 1000
print(x is y)   # False — two different int objects
print(x == y)   # True  — same value, but different objects
```

### What `bool` overrides vs. inherits

`bool` only overrides `&`, `|`, and `^` to return a `bool` when both operands are bools. Everything else falls through to `int`:

```python
True + True    # → 2      (int)   — addition not overridden, uses int's code
True & False   # → False  (bool)  — & is overridden to return bool
True | False   # → True   (bool)  — | is overridden to return bool
True * 5       # → 5      (int)   — multiplication not overridden
```

```c
static PyObject *
bool_and(PyObject *a, PyObject *b)
{
    if (!PyBool_Check(a) || !PyBool_Check(b))
        return PyLong_Type.tp_as_number->nb_and(a, b); // fall back to int
    return PyBool_FromLong((a == Py_True) & (b == Py_True)); // return bool
}
```

---

## Comparison with Go

Go has **true primitives**: value types stored directly, no boxing, no methods (by default).

| Concept           | Python 3                            | Go                                         |
|-------------------|-------------------------------------|--------------------------------------------|
| Integer           | `int` — object, arbitrary precision | `int`, `int8`…`int64` — fixed-size, by value |
| Float             | `float` — 64-bit object             | `float32`, `float64` — by value             |
| Boolean           | `bool` (subclass of `int`)          | `bool` — true primitive                    |
| String            | `str` — immutable object            | `string` — immutable value type             |
| Null              | `None` (singleton object)           | `nil` (zero value, not a type)             |
| Integer overflow  | Never (arbitrary precision)         | Wraps around (defined behavior)            |
| Methods on type   | Yes (`int` has `.bit_length()` etc) | No (must define on struct or use package)  |
| Memory layout     | Heap-allocated object + refcount    | Inline on stack or array                   |

```go
// Go — true primitive, stored by value
var x int = 42
var y int = x   // y is a copy of the value, not a reference

// Go has multiple integer sizes
var a int8  = 127   // max value; adding 1 wraps to -128
var b int64 = 9_223_372_036_854_775_807

// No methods on primitives
// x.something() — does not compile
```

---

## Comparison with Java

Java has a **split type system**: 8 true primitives and their boxed object equivalents.

| Java Primitive | Java Boxed   | Python Equivalent | Notes                                  |
|----------------|--------------|-------------------|----------------------------------------|
| `int`          | `Integer`    | `int`             | Python's int is always the boxed form  |
| `long`         | `Long`       | `int`             | Python int covers both                 |
| `double`       | `Double`     | `float`           | Python float is always 64-bit          |
| `float`        | `Float`      | —                 | Python has no 32-bit float built-in    |
| `boolean`      | `Boolean`    | `bool`            | Python bool is a subclass of int       |
| `char`         | `Character`  | `str` (length 1)  | Python has no char type                |
| `byte`         | `Byte`       | `int`             | Python int covers all sizes            |
| `short`        | `Short`      | `int`             | Python int covers all sizes            |

```java
// Java — primitives are not objects
int x = 42;           // stack-allocated, no methods
Integer y = 42;       // heap-allocated boxed object
x.toString();         // compile error — not an object
y.toString();         // fine — "42"

// Autoboxing bridges the gap (Java 5+)
Integer z = x;        // compiler boxes int → Integer automatically
int w = z;            // compiler unboxes Integer → int automatically

// Integer cache: Java caches Integer objects for -128..127
Integer a = 127;
Integer b = 127;
System.out.println(a == b);  // true  (same cached object)

Integer c = 128;
Integer d = 128;
System.out.println(c == d);  // false (different heap objects!)
```

```python
# Python equivalent — there is only one kind of int
x = 42         # object on the heap
y = 42         # CPython caches small ints (-5..256), same object
print(x is y)  # True  (CPython small-int cache)

x = 1000
y = 1000
print(x is y)  # False (outside cache range, different objects)
print(x == y)  # True  (value equality always works with ==)
```

---

## The Small Integer Cache (CPython Implementation Detail)

CPython (the reference Python interpreter) pre-allocates integer objects for values **-5 through 256**. This is a performance optimization — not a language guarantee.

```python
a = 255
b = 255
print(a is b)  # True  — same object (within cache range)

a = 257
b = 257
print(a is b)  # False — different objects (outside cache range)

# Always use == for value comparison, never `is`
print(a == b)  # True  — correct way to compare values
```

---

## Mutability Summary

| Type      | Mutable? | Notes                                          |
|-----------|----------|------------------------------------------------|
| `int`     | No       | Reassignment creates a new object              |
| `float`   | No       | Reassignment creates a new object              |
| `bool`    | No       | Reassignment creates a new object              |
| `str`     | No       | All string operations return new strings       |
| `bytes`   | No       | Use `bytearray` for mutable byte sequences     |
| `None`    | No       | Singleton; cannot be mutated                   |

Because scalars are immutable, Python can safely share them between variables and across threads without copying.

---

## Performance Implications

Python's object-per-value model has overhead compared to true primitives:

- Every `int` carries a **reference count**, a **type pointer**, and the **value** (~28 bytes for a small int vs. 8 bytes for a 64-bit integer in Go/Java)
- Arithmetic operations go through object allocation/deallocation
- For numeric-heavy work, use **NumPy** arrays, which store raw C-level values in contiguous memory — closer to Go/Java arrays of primitives

```python
import sys

print(sys.getsizeof(1))          # 28 bytes — Python int object
print(sys.getsizeof(True))       # 28 bytes — bool object
print(sys.getsizeof(""))         # 49 bytes — empty str object
print(sys.getsizeof("a"))        # 50 bytes — one char str

import numpy as np
arr = np.array([1, 2, 3], dtype=np.int64)
print(arr.itemsize)              # 8 bytes — raw int64, like Go/Java
```

---

## Summary

- Python 3 has **no true primitives** — every value (int, float, bool, str) is a heap-allocated object with a type pointer, reference count, and methods.
- This differs from **Go** (value types stored directly, fixed-size integers, stack-allocated when possible) and **Java** (8 true primitives + boxed object equivalents with autoboxing).
- **`bool` is a subclass of `int`** at the C level: `PyBool_Type.tp_base` points to `PyLong_Type`. `True` and `False` are statically allocated `_longobject` structs — immortal singletons that `bool()` always returns without allocating.
- CPython pre-allocates integers **-5 through 256** as singletons (the small-int cache). `a is b` is `True` for values in this range; `False` outside it.
- **Memory cost:** a Python `int` is ~28 bytes vs. 8 bytes for an `int64` in Go/Java. Every arithmetic operation may allocate a new object.
- For numeric-heavy work, use **NumPy** — arrays store raw C values contiguously in memory, bypassing the per-object overhead entirely.
