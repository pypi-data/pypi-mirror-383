[![Doxygen](https://img.shields.io/badge/docs-doxygen-2c4aa8.svg?logo=doxygen)](https://lambdaphoenix.github.io/cbits/)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/cbits.svg)](https://pypi.org/project/cbits/)
[![PyPI - Version](https://img.shields.io/pypi/v/cbits.svg)](https://pypi.org/project/cbits/)
[![PyPI - Format](https://img.shields.io/pypi/format/cbits.svg)](https://pypi.org/project/cbits/#files)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cbits.svg)](https://pypi.org/project/cbits/)
[![Changelog](https://img.shields.io/badge/CHANGELOG-md-blue.svg)](https://github.com/lambdaphoenix/cbits/blob/main/CHANGELOG.md)
[![GitHub License](https://img.shields.io/github/license/lambdaphoenix/cbits.svg)](https://github.com/lambdaphoenix/cbits/blob/main/LICENSE)

# cbits

> High-performance BitVector for Python.


## Description
cbits implements a powerful bit vector type in C that is accessible via a Python API. It stores bits contiguously in memory and minimizes overhead compared to a list of Boolean values. Core operations such as setting, clearing, flipping and counting bits run in constant or near-constant time per word, making it ideal for extensive bit manipulation.


## Installation

```bash
pip install cbits
```

## Quick Start
```python
from cbits import BitVector

# Create a 64-bit vector
bv = BitVector(64)

# Set bits, clear, flip, query
bv.set(3)
bv.clear(3)
bv.flip(0)
print(bv.get(0))                # → True or False
print(len(bv), bv.bits)

# Range operations
bv.set_range(10, 5)             # set bits 10..14
bv.clear_range(12, 2)           # clear bits 12..13
bv.flip_range(0, 64)            # toggle all bits

# Negative indexing
bv.set(-1)
print(bv.get(63))

# Boolean test & rank
print(bool(bv))
print(bv.rank(32))              # count of set bits up to index 32

# Copy & deepcopy
import copy
bv2 = bv.copy()
bv3 = copy.deepcopy(bv)

# Bitwise operations
a = BitVector(8); b = BitVector(8)
a.set(0); a.set(2)
b.set(1); b.set(2)
print((a & b)[0], (a | b)[0], (a ^ b)[0], (~a)[0])

# Sequence & iteration
bv[5] = True
print(bv[5])
print([i for i, bit in enumerate(bv) if bit])

# Slicing
sv = bv[2:10]                   # positions 2..9
print([sv.get(i) for i in range(len(sv))])
sv2 = bv[:5]                    # first five bits
sv3 = bv[5:]                    # bits from 5 to end
sv4 = bv[::2]                   # every other bit
sv_rev = bv[::-1]               # reversed vector
print([sv4.get(i) for i in range(len(sv4))])
print([sv_rev.get(i) for i in range(len(sv_rev))])

# Slice assignment from iterables or BitVector
bv[0:4] = [True, False, True, False]
print([bv.get(i) for i in range(4)])

bv[4:8] = BitVector(4)          # assign via another BitVector
print([bv.get(i) for i in range(4, 8)])

# Negative-step assignment
bv[9:5:-1] = (i % 2 == 0 for i in range(4))
print([bv.get(i) for i in range(9, 5, -1)])

# Contains
a = BitVector(8); b = BitVector(4)
a.set(0); a.set(2); a.set(5)    # 10100100
b.set(0); b.set(3)              # 1001
print(b in a)
```

## API Reference
### Class: BitVector
```python
class BitVector:
    def __init__(self, size: int)

    @property
    def bits(self) -> int

    def get(self, index: int) -> bool
    def set(self, index: int) -> None
    def clear(self, index: int) -> None
    def flip(self, index: int) -> None
    def set_range(self, start: int, length: int) -> None
    def clear_range(self, start: int, length: int) -> None
    def flip_range(self, start: int, length: int) -> None
    def rank(self, index: int) -> int

    def copy(self) -> BitVector
    def __copy__(self) -> BitVector
    def __deepcopy__(self, memo) -> BitVector

    # Sequence protocol
    def __len__(self) -> int

    # Single-index access
    def __getitem__(self, index: int) -> bool
    def __setitem__(self, index: int, value: bool) -> None

    # Slicing access & assignment
    def __getitem__(self, s: slice) -> BitVector
    def __setitem__(self, s: slice, value: Iterable[bool]) -> None

    def __contains__(self, other: BitVector) -> bool
    def __iter__(self) -> Iterator[bool]

    # Numeric & bitwise protocol
    def __and__(self, other: BitVector) -> BitVector
    def __iand__(self, other: BitVector) -> BitVector
    def __or__(self, other: BitVector) -> BitVector
    def __ior__(self, other: BitVector) -> BitVector
    def __xor__(self, other: BitVector) -> BitVector
    def __ixor__(self, other: BitVector) -> BitVector
    def __invert__(self) -> BitVector
    def __bool__(self) -> bool

    def __repr__(self) -> str
    def __str__(self) -> str
```

## License
Apache License 2.0 See [LICENSE](https://github.com/lambdaphoenix/cbits/blob/main/LICENSE) for details.

## Project Links
- [📖 Documentation & Source](https://github.com/lambdaphoenix/cbits)
- [🐛 Issues](https://github.com/lambdaphoenix/cbits/issues)
- [📋 Changelog](https://github.com/lambdaphoenix/cbits/blob/main/CHANGELOG.md)
- [📦 PyPI](https://pypi.org/project/cbits/)
