"""
Python String Formatting, Parsing, and File Parsing Cheatsheet

Covers:
- String formatting (f-strings, format, %)
- String parsing (split, strip, replace, find, slicing)
- String validation (isdigit, isalpha, isspace, etc.)
- File parsing basics (open, read, readline, readlines, with statement)
- Output formatting (print, join, repr, etc.)
"""

# --- String Formatting ---

# f-strings (Python 3.6+)
name = "Alice"
age = 30
print(f"Name: {name}, Age: {age}")

# str.format()
print("Name: {}, Age: {}".format(name, age))
print("Name: {n}, Age: {a}".format(n=name, a=age))

# %-formatting (old style)
print("Name: %s, Age: %d" % (name, age))

# Number formatting
pi = 3.14159
print(f"Pi rounded: {pi:.2f}")  # 2 decimal places
print("Pi rounded: {:.2f}".format(pi))

# Padding and alignment
print(f"|{name:<10}|{age:>5}|")  # left/right align

# --- String Parsing ---

s = "  hello, world!  "
print(s.strip())         # Remove leading/trailing whitespace
print(s.lstrip())        # Remove leading whitespace
print(s.rstrip())        # Remove trailing whitespace

csv = "a,b,c"
print(csv.split(","))   # ['a', 'b', 'c']

words = "one two three".split()  # Split on whitespace
print(words)

joined = ",".join(words)         # 'one,two,three'
print(joined)

# Replace substrings
print(s.replace("hello", "hi"))

# Find substrings
print(s.find("world"))   # Returns index or -1
print(s.index("world"))  # Returns index or raises ValueError

# Slicing
print(s[2:7])

# --- String Validation ---

num = "12345"
print(num.isdigit())      # True
alpha = "abcXYZ"
print(alpha.isalpha())    # True
alnum = "abc123"
print(alnum.isalnum())    # True
space = "   "
print(space.isspace())    # True

# Check prefix/suffix
print(s.startswith("  h"))
print(s.endswith("!  "))

# --- File Parsing ---

# Reading a file line by line
with open("example.txt", "r") as f:
    for line in f:
        print(line.strip())

# Read all lines into a list
with open("example.txt", "r") as f:
    lines = f.readlines()
    print(lines)

# Read entire file as a string
with open("example.txt", "r") as f:
    content = f.read()
    print(content)

# Writing to a file
with open("output.txt", "w") as f:
    f.write("Hello, file!\n")
    f.writelines(["Line 1\n", "Line 2\n"])

# --- Output Formatting ---

# Print with separator and end
print("A", "B", "C", sep=", ", end="!\n")

# repr vs str
x = 42
print(str(x))   # '42'
print(repr(x))  # '42'

# Pretty printing data structures
import pprint
pp = pprint.PrettyPrinter(indent=2)
data = {"a": [1,2,3], "b": {"c": 4}}
pp.pprint(data)

# --- Miscellaneous ---

# Convert string to int/float
s = "123"
print(int(s))
s = "3.14"
print(float(s))

# Safe conversion with try/except
try:
    val = int("abc")
except ValueError:
    val = None
print(val)

# Remove all whitespace from a string
s = " a b c "
print("".join(s.split()))

# Remove specific characters (e.g., punctuation)
import string
s = "hello, world!"
print(s.translate(str.maketrans('', '', string.punctuation)))
