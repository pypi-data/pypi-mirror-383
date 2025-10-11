/**
 * @file python/binding.c
 * @brief Python C-API bindings for BitVector.
 *
 * Defines the Python-level BitVector type wrapping the C BitVector API,
 * including:
 * - PyBitVector type and lifecycle (tp_new, tp_init, tp_dealloc)
 * - Core BitVector methods (get, set, clear, flip, rank, copy)
 * - Sequence, numeric and richcompare protocols
 *
 * @see include/bitvector.h
 * @author lambdaphoenix
 * @version 0.2.0
 * @copyright Copyright (c) 2025 lambdaphoenix
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "bitvector.h"

/**
 * @def CHECK_BV_OBJ(o)
 * @brief Verify that @a o is a PyBitVector instance or raise @c TypeError.
 */
#define CHECK_BV_OBJ(o)                                         \
    if (!PyObject_TypeCheck(o, PyBitVectorPtr)) {               \
        PyErr_SetString(PyExc_TypeError, "Expected BitVector"); \
        return NULL;                                            \
    }

/**
 * @def CHECK_BV_BOTH(a, b)
 * @brief Verify both @a a and @a b are PyBitVector, else return @c
 * NotImplemented.
 */
#define CHECK_BV_BOTH(a, b)                       \
    if (!PyObject_TypeCheck(a, PyBitVectorPtr) || \
        !PyObject_TypeCheck(b, PyBitVectorPtr)) { \
        Py_RETURN_NOTIMPLEMENTED;                 \
    }

/**
 * @struct PyBitVector
 * @brief Python object containing a pointer to a native BitVector.
 *
 * Includes a cached hash value @c 'hash_cache' to speed up repeated
 * dictionary/set lookups.
 */
typedef struct {
    PyObject_HEAD BitVector *bv; /**< Reference to the BitVector */
    Py_hash_t hash_cache;        /**< Cached hash value or -1 if invalid */
} PyBitVector;

/** Global pointer to the PyBitVector type object. */
PyTypeObject *PyBitVectorPtr = NULL;

/**
 * @brief Wrap a native BitVector in a new PyBitVector Python object.
 * @param bv_data Pointer to an allocated BitVector.
 * @return New reference to a PyBitVector, or NULL on allocation failure.
 */
static PyObject *
bv_wrap_new(BitVector *bv_data)
{
    PyBitVector *obj =
        (PyBitVector *) PyBitVectorPtr->tp_alloc(PyBitVectorPtr, 0);
    if (!obj) {
        bv_free(bv_data);
        return NULL;
    }
    obj->bv = bv_data;
    obj->hash_cache = -1;
    return (PyObject *) obj;
}

/* -------------------------------------------------------------------------
 * Deallocation and object lifecycle
 * ------------------------------------------------------------------------- */

/**
 * @brief Deallocate a PyBitVector object.
 * @param self A Python PyBitVector instance.
 */
static void
py_bv_free(PyObject *self)
{
    PyBitVector *bvself = (PyBitVector *) self;
    if (bvself->bv) {
        bv_free(bvself->bv);
        bvself->bv = NULL;
    }
    Py_TYPE(self)->tp_free(self);
}

/**
 * @brief __new__ for BitVector: allocate the Python object.
 * @param type The Python type object.
 * @param args Positional args (unused).
 * @param kwds Keyword args (unused).
 * @return New, uninitialized PyBitVector or NULL on failure.
 */
static PyObject *
py_bv_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PyBitVector *bvself = (PyBitVector *) type->tp_alloc(type, 0);
    if (!bvself) {
        return NULL;
    }
    bvself->bv = NULL;
    bvself->hash_cache = -1;
    return (PyObject *) bvself;
}

/**
 * @brief Python binding for BitVector.copy() → BitVector.
 * @param self A Python PyBitVector instance.
 * @param UNUSED
 * @return New BitVector copy
 */
static PyObject *
py_bv_copy(PyObject *self, PyObject *ignored)
{
    BitVector *copy = bv_copy(((PyBitVector *) self)->bv);
    if (!copy) {
        PyErr_SetString(PyExc_MemoryError,
                        "Failed to allocate BitVector in copy()");
        return NULL;
    }
    return bv_wrap_new(copy);
}

/**
 * @brief Python binding for BitVector.__deepcopy__(memo) → BitVector.
 * @param self A Python PyBitVector instance.
 * @param memo
 * @return New BitVector copy
 */
static PyObject *
py_bv_deepcopy(PyObject *self, PyObject *memo)
{
    PyObject *copy = py_bv_copy(self, NULL);
    if (!copy) {
        return NULL;
    }
    if (memo && PyDict_Check(memo)) {
        if (PyDict_SetItem(memo, self, copy) < 0) {
            Py_DECREF(copy);
            return NULL;
        }
    }
    return copy;
}

/**
 * @brief __init__ for BitVector(size): allocate the underlying C BitVector.
 * @param self A Python PyBitVector instance.
 * @param args Positional args tuple.
 * @param kwds Keyword args dict.
 * @return 0 on success, -1 on error (with exception set).
 */
static int
py_bv_init(PyObject *self, PyObject *args, PyObject *kwds)
{
    Py_ssize_t n_bits;
    static char *kwlist[] = {"size", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "n", kwlist, &n_bits)) {
        return -1;
    }
    PyBitVector *bvself = (PyBitVector *) self;
    bvself->bv = bv_new((size_t) n_bits);
    if (!bvself->bv) {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate BitVector");
        return -1;
    }
    return 0;
}

/* -------------------------------------------------------------------------
 * Core BitVector Methods
 * ------------------------------------------------------------------------- */

/**
 * @brief Parse and validate a single index argument.
 * @param self A Python PyBitVector instance.
 * @param arg Python argument.
 * @param p_index Output pointer to store the validated index.
 * @return 0 on success (p_index set), -1 on failure (exception set).
 */
static inline int
bv_parse_index(PyObject *self, PyObject *arg, size_t *p_index)
{
    if (!PyLong_Check(arg)) {
        PyErr_SetString(PyExc_TypeError, "BitVector index must be an integer");
        return -1;
    }
    Py_ssize_t index = PyLong_AsSsize_t(arg);
    if (index == -1 && PyErr_Occurred()) {
        return -1;
    }
    PyBitVector *bvself = (PyBitVector *) self;
    size_t n_bits = bvself->bv->n_bits;
    if (index < 0) {
        index += (Py_ssize_t) n_bits;
    }
    if (index < 0 || index >= n_bits) {
        PyErr_SetString(PyExc_IndexError, "BitVector index out of range");
        return -1;
    }
    *p_index = (size_t) index;
    return 0;
}

/**
 * @brief Parse and validate a (start, length) range tuple.
 * @param self A Python PyBitVector instance.
 * @param args   Python argument tuple (start, length).
 * @param p_start Output pointer for start index.
 * @param p_len   Output pointer for length.
 * @return 0 on success (outputs set), -1 on failure (exception set).
 * @since 0.2.0
 */
static inline int
bv_parse_tuple(PyObject *self, PyObject *args, size_t *p_start, size_t *p_len)
{
    Py_ssize_t start, len;
    if (!PyArg_ParseTuple(args, "nn", &start, &len)) {
        return -1;
    }
    if (start < 0 || len < 0) {
        PyErr_SetString(PyExc_ValueError,
                        "start and length must be non-negative");
        return -1;
    }
    PyBitVector *bvself = (PyBitVector *) self;
    if ((size_t) start + (size_t) len > bvself->bv->n_bits) {
        PyErr_SetString(PyExc_IndexError, "BitVector range out of bounds");
        return -1;
    }
    *p_start = (size_t) start;
    *p_len = (size_t) len;
    return 0;
}

/**
 * @brief Python binding for BitVector.get(index) → bool.
 * @param self A Python PyBitVector instance.
 * @param arg Python argument.
 * @return true is bit is set, false otherwise
 */
static PyObject *
py_bv_get(PyObject *self, PyObject *arg)
{
    size_t index;
    if (bv_parse_index(self, arg, &index) < 0) {
        return NULL;
    }

    int bit = bv_get(((PyBitVector *) self)->bv, index);
    return PyBool_FromLong(bit);
}

/**
 * @brief Python binding for BitVector.set(index).
 * @param self A Python PyBitVector instance.
 * @param arg Python argument.
 * @return None on success, NULL on error.
 */
static PyObject *
py_bv_set(PyObject *self, PyObject *arg)
{
    size_t index;
    if (bv_parse_index(self, arg, &index) < 0) {
        return NULL;
    }

    bv_set(((PyBitVector *) self)->bv, index);
    ((PyBitVector *) self)->hash_cache = -1;
    Py_RETURN_NONE;
}

/**
 * @brief Python binding for BitVector.clear(index).
 * @param self A Python PyBitVector instance.
 * @param args Python argument.
 * @return None on success, NULL on error.
 */
static PyObject *
py_bv_clear(PyObject *self, PyObject *arg)
{
    size_t index;
    if (bv_parse_index(self, arg, &index) < 0) {
        return NULL;
    }

    bv_clear(((PyBitVector *) self)->bv, index);
    ((PyBitVector *) self)->hash_cache = -1;
    Py_RETURN_NONE;
}

/**
 * @brief Python binding for BitVector.flip(index).
 * @param self A Python PyBitVector instance.
 * @param arg Python argument.
 * @return None on success, NULL on error.
 */
static PyObject *
py_bv_flip(PyObject *self, PyObject *arg)
{
    size_t index;
    if (bv_parse_index(self, arg, &index) < 0) {
        return NULL;
    }

    bv_flip(((PyBitVector *) self)->bv, index);
    ((PyBitVector *) self)->hash_cache = -1;
    Py_RETURN_NONE;
}

/**
 * @brief Python binding for BitVector.set_range(start, length).
 *
 * Calls bv_set_range() to set all bits in the half‑open range
 * [start, start+length). Marks the hash cache invalid and returns None.
 *
 * @param self A Python PyBitVector instance.
 * @param args Tuple (start, length).
 * @return Py_None on success, NULL on error (with exception set).
 * @since 0.2.0
 */
static PyObject *
py_bv_set_range(PyObject *self, PyObject *args)
{
    size_t start, len;
    if (bv_parse_tuple(self, args, &start, &len) < 0) {
        return NULL;
    }
    bv_set_range(((PyBitVector *) self)->bv, start, len);
    ((PyBitVector *) self)->hash_cache = -1;
    Py_RETURN_NONE;
}

/**
 * @brief Python binding for BitVector.clear_range(start, length).
 *
 * Calls bv_clear_range() to clear all bits in the half‑open range
 * [start, start+length). Marks the hash cache invalid and returns None.
 *
 * @param self A Python PyBitVector instance.
 * @param args Tuple (start, length).
 * @return Py_None on success, NULL on error (with exception set).
 * @since 0.2.0
 */
static PyObject *
py_bv_clear_range(PyObject *self, PyObject *args)
{
    size_t start, len;
    if (bv_parse_tuple(self, args, &start, &len) < 0) {
        return NULL;
    }
    bv_clear_range(((PyBitVector *) self)->bv, start, len);
    ((PyBitVector *) self)->hash_cache = -1;
    Py_RETURN_NONE;
}

/**
 * @brief Python binding for BitVector.flip_range(start, length).
 *
 * Calls bv_flip_range() to toggle all bits in the half‑open range
 * [start, start+length). Marks the hash cache invalid and returns None.
 *
 * @param self A Python PyBitVector instance.
 * @param args Tuple (start, length).
 * @return Py_None on success, NULL on error (with exception set).
 * @since 0.2.0
 */
static PyObject *
py_bv_flip_range(PyObject *self, PyObject *args)
{
    size_t start, len;
    if (bv_parse_tuple(self, args, &start, &len) < 0) {
        return NULL;
    }
    bv_flip_range(((PyBitVector *) self)->bv, start, len);
    ((PyBitVector *) self)->hash_cache = -1;
    Py_RETURN_NONE;
}

/**
 * @brief Python binding for BitVector.rank(index) → bool.
 * @param self A Python PyBitVector instance.
 * @param args Array of Python arguments.
 * @param n_args Number of arguments expected (should be 1).
 * @return Number of bits set in range [0...pos]
 */
static PyObject *
py_bv_rank(PyObject *self, PyObject *arg)
{
    size_t index;
    if (bv_parse_index(self, arg, &index) < 0) {
        return NULL;
    }

    size_t rank = bv_rank(((PyBitVector *) self)->bv, index);
    return PyLong_FromSize_t(rank);
}

PyDoc_STRVAR(
    py_bv_get__doc__,
    "get(index: int) -> bool\n"
    "\n"
    "Return the boolean value of the bit at position *index*.\n"
    "Negative indices are supported. Raises IndexError if out of range.");

PyDoc_STRVAR(
    py_bv_set__doc__,
    "set(index: int) -> None\n"
    "\n"
    "Set the bit at position *index* to True. Supports negative indexing.\n"
    "Raises IndexError if out of range.");

PyDoc_STRVAR(py_bv_clear__doc__,
             "clear(index: int) -> None\n"
             "\n"
             "Clear the bit (set to False) at position *index*. Supports "
             "negative indexing.\n"
             "Raises IndexError if out of range.");

PyDoc_STRVAR(py_bv_set_range__doc__,
             "set_range(start: int, length: int) -> None\n"
             "\n"
             "Set all bits in the half-open range [start, start+length).\n"
             "Raises IndexError if the range is out of bounds.");

PyDoc_STRVAR(py_bv_clear_range__doc__,
             "clear_range(start: int, length: int) -> None\n"
             "\n"
             "Clear all bits in the half-open range [start, start+length).\n"
             "Raises IndexError if the range is out of bounds.");

PyDoc_STRVAR(py_bv_flip_range__doc__,
             "flip_range(start: int, length: int) -> None\n"
             "\n"
             "Toggle all bits in the half-open range [start, start+length).\n"
             "Raises IndexError if the range is out of bounds.");

PyDoc_STRVAR(
    py_bv_flip__doc__,
    "flip(index: int) -> None\n"
    "\n"
    "Toggle the bit at position *index*. Supports negative indexing.\n"
    "Raises IndexError if out of range.");

PyDoc_STRVAR(
    py_bv_rank__doc__,
    "rank(index: int) -> int\n"
    "\n"
    "Count the number of bits set to True in the half-open range [0..index].\n"
    "Supports negative indexing. Raises IndexError if out of range.");

PyDoc_STRVAR(py_bv_copy__doc__,
             "copy() -> BitVector\n"
             "\n"
             "Return a copy of this BitVector.");
PyDoc_STRVAR(py_bv_copy_inline__doc__,
             "__copy__() -> BitVector\n"
             "\n"
             "Return a copy of this BitVector.");
PyDoc_STRVAR(py_bv_deepcopy__doc__,
             "__deepcopy__(memo: dict) -> BitVector\n"
             "\n"
             "Return a copy of this BitVector, registering it in *memo*.");

/**
 * @brief Method table for BitVector core methods.
 */
static PyMethodDef BitVector_methods[] = {
    {"get", (PyCFunction) py_bv_get, METH_O, py_bv_get__doc__},
    {"set", (PyCFunction) py_bv_set, METH_O, py_bv_set__doc__},
    {"clear", (PyCFunction) py_bv_clear, METH_O, py_bv_clear__doc__},
    {"flip", (PyCFunction) py_bv_flip, METH_O, py_bv_flip__doc__},
    {"set_range", (PyCFunction) py_bv_set_range, METH_VARARGS,
     py_bv_set_range__doc__},
    {"clear_range", (PyCFunction) py_bv_clear_range, METH_VARARGS,
     py_bv_clear_range__doc__},
    {"flip_range", (PyCFunction) py_bv_flip_range, METH_VARARGS,
     py_bv_flip_range__doc__},
    {"rank", (PyCFunction) py_bv_rank, METH_O, py_bv_rank__doc__},
    {"copy", (PyCFunction) py_bv_copy, METH_NOARGS, py_bv_copy__doc__},
    {"__copy__", (PyCFunction) py_bv_copy, METH_NOARGS,
     py_bv_copy_inline__doc__},
    {"__deepcopy__", (PyCFunction) py_bv_deepcopy, METH_O,
     py_bv_deepcopy__doc__},
    {NULL, NULL, 0, NULL},
};

/* -------------------------------------------------------------------------
 * Magic Methods
 * ------------------------------------------------------------------------- */

/**
 * @brief __repr__ for BitVector.
 * @param self A Python PyBitVector instance.
 * @return New Python string describing the object.
 */
static PyObject *
py_bv_repr(PyObject *self)
{
    PyBitVector *bvself = (PyBitVector *) self;
    return PyUnicode_FromFormat("<cbits.BitVector object at %p bits=%zu>",
                                self, bvself->bv->n_bits);
}

/**
 * @brief __str__ for BitVector.
 * @param self A Python PyBitVector instance.
 * @return New Python string "BitVector with X bits".
 */
static PyObject *
py_bv_str(PyObject *self)
{
    PyBitVector *bvself = (PyBitVector *) self;
    return PyUnicode_FromFormat("BitVector with %zu bits", bvself->bv->n_bits);
}

/**
 * @brief Rich comparison (== and !=) for BitVector.
 * @param a First operant.
 * @param b Second operant.
 * @param op Comparison operation (Py_EQ or Py_NE).
 * @return Py_True or Py_False on success; Py_RETURN_NOTIMPLEMENTED if
 * unsupported.
 */
static PyObject *
py_bv_richcompare(PyObject *a, PyObject *b, int op)
{
    if (op != Py_EQ && op != Py_NE) {
        Py_RETURN_NOTIMPLEMENTED;
    }
    CHECK_BV_BOTH(a, b)
    BitVector *A = ((PyBitVector *) a)->bv;
    BitVector *B = ((PyBitVector *) b)->bv;

    bool eq = bv_equal(((PyBitVector *) a)->bv, ((PyBitVector *) b)->bv);
    if ((op == Py_EQ) == eq) {
        Py_RETURN_TRUE;
    }
    Py_RETURN_FALSE;
}

/**
 * @brief __hash__ for a BitVector object.
 *
 * Computes a hash over the vector’s packed bit data using Python’s internal
 * _Py_HashBytes helper. The result is cached in the object until the BitVector
 * is mutated.
 *
 * @param self A Python PyBitVector instance.
 * @return A Py_hash_t value derived from the bit‐pattern contents.
 */
static Py_hash_t
py_bv_hash(PyObject *self)
{
    PyBitVector *pbv = (PyBitVector *) self;
    if (pbv->hash_cache != -1) {
        return pbv->hash_cache;
    }
    BitVector *bv = pbv->bv;
    size_t n_bytes = (bv->n_bits + 7) >> 3;
    if (n_bytes == 0) {
        return 0;
    }
    PyObject *b = PyBytes_FromStringAndSize((const char *) bv->data,
                                            (Py_ssize_t) n_bytes);
    if (b == NULL) {
        return -1;
    }
    Py_hash_t hash = PyObject_Hash(b);
    Py_DECREF(b);

    if (hash == -1) {
        hash = -2;
    }
    pbv->hash_cache = hash;
    return hash;
}

/* -------------------------------------------------------------------------
 * Sequence Protocol
 * ------------------------------------------------------------------------- */

/**
 * @brief __len__(BitVector) → number of bits.
 * @param self A Python PyBitVector instance.
 * @return Number of bits as Py_ssize_t.
 */
static Py_ssize_t
py_bv_len(PyObject *self)
{
    BitVector *bv = ((PyBitVector *) self)->bv;
    return (Py_ssize_t) (bv ? bv->n_bits : 0);
}

/**
 * @brief Implements BitVector.__getitem__, returns the bit at position i.
 *
 * This function checks bounds and returns the corresponding Python boolean
 * (True/False). On out-of-range access it raises IndexError.
 *
 * @param self A Python PyBitVector instance.
 * @param i Index to access
 * @return New reference to Py_True or Py_False on success; NULL and IndexError
 * on failure.
 */
static PyObject *
py_bv_item(PyObject *self, Py_ssize_t i)
{
    BitVector *bv = ((PyBitVector *) self)->bv;
    if (!bv || bv->n_bits <= (size_t) i) {
        PyErr_SetString(PyExc_IndexError, "BitVector index out of range");
        return NULL;
    }
    return PyBool_FromLong(bv_get(bv, (size_t) i));
}

/**
 * @brief Implements slicing for BitVector.__getitem__ with a slice object.
 *
 * Creates and returns a new BitVector containing elements from
 * [start:stop:step]. Raises IndexError if any index is out of bounds.
 *
 * @param self A Python PyBitVector instance.
 * @param start Start index of the slice.
 * @param stop End index (exclusive) of the slice.
 * @param step Step size for the slice.
 * @param slicelength Number of elements in the resulting slice.
 * @return New PyBitVector wrapping the sliced BitVector; NULL and IndexError
 * on failure.
 */
static PyObject *
py_bv_slice(PyObject *self, size_t start, size_t stop, size_t step,
            size_t slicelength)
{
    PyBitVector *pbv = (PyBitVector *) self;
    BitVector *src = pbv->bv;

    BitVector *out = bv_new(slicelength);
    if (!out) {
        return NULL;
    }

    if (step == 1 && slicelength > 0) {
        size_t s_word = start >> 6;
        unsigned s_off = (unsigned) (start & 63);
        size_t words_needed = out->n_words;

        uint64_t carry = 0;
        for (size_t j = 0; j < words_needed; ++j) {
            size_t aw = s_word + j;
            uint64_t lo = (aw < src->n_words) ? src->data[aw] : 0ULL;
            uint64_t hi = (aw + 1 < src->n_words) ? src->data[aw + 1] : 0ULL;

            uint64_t word = (lo >> s_off) | (hi << (64 - s_off));
            out->data[j] = word;
        }
        bv_apply_tail_mask(out);
        return bv_wrap_new(out);
    }

    size_t n_bits = src->n_bits;
    for (size_t i = 0, idx = start; i < slicelength; ++i, idx += step) {
        if (n_bits <= idx) {
            bv_free(out);
            PyErr_SetString(PyExc_IndexError, "BitVector slice out of range");
            return NULL;
        }
        if (bv_get(src, idx)) {
            bv_set(out, i);
        }
    }

    return bv_wrap_new(out);
}

/**
 * @brief Implements BitVector.__getitem__ dispatch for index or slice.
 *
 * Delegates either to py_bv_item (for integer indices) or to py_bv_slice (for
 * slice objects). Raises TypeError for unsupported types.
 *
 * @param self A Python PyBitVector instance.
 * @param arg Index or slice object.
 * @return New reference to a Python bool or PyBitVector; NULL and exception on
 * error.
 */
static PyObject *
py_bv_subscript(PyObject *self, PyObject *arg)
{
    if (PyIndex_Check(arg)) {
        Py_ssize_t idx = PyNumber_AsSsize_t(arg, PyExc_IndexError);
        if (idx == -1 && PyErr_Occurred()) {
            return NULL;
        }
        return py_bv_item(self, idx);
    }

    if (PySlice_Check(arg)) {
        PyObject *slice = (PyObject *) arg;
        PyBitVector *bv = (PyBitVector *) self;
        Py_ssize_t start, stop, step, slicelength;
        if (PySlice_GetIndicesEx(slice, bv->bv->n_bits, &start, &stop, &step,
                                 &slicelength) < 0) {
            return NULL;
        }
        return py_bv_slice(self, (size_t) start, (size_t) stop, (size_t) step,
                           (size_t) slicelength);
    }

    PyErr_Format(PyExc_TypeError,
                 "indices must be integers or slices, not %.200s",
                 Py_TYPE(arg)->tp_name);
    return NULL;
}

/**
 * @brief Implements BitVector.__setitem__ for a single index.
 *
 * Sets or clears the bit at position i based on the truth value of `value`.
 * Raises IndexError if the index is out of range.
 *
 * @param self A Python PyBitVector instance.
 * @param i Index of the bit to assign.
 * @param value Python object interpreted as boolean.
 * @return 0 on success; -1 on error (with exception set).
 */
static int
py_bv_ass_item(PyObject *self, Py_ssize_t i, PyObject *value)
{
    BitVector *bv = ((PyBitVector *) self)->bv;
    if (!bv || bv->n_bits <= (size_t) i) {
        PyErr_SetString(PyExc_IndexError,
                        "BitVector assignment index out of range");
        return -1;
    }
    int bit = PyObject_IsTrue(value);
    if (bit < 0) {
        return -1;
    }
    if (bit) {
        bv_set(bv, (size_t) i);
    }
    else {
        bv_clear(bv, (size_t) i);
    }
    ((PyBitVector *) self)->hash_cache = -1;
    return 0;
}

/**
 * @brief Implements BitVector.__setitem__ for slice assignment.
 *
 * Assigns bits from an iterable `value` to the slice [start:stop:step]. Raises
 * IndexError or ValueError on length mismatch or out-of-range.
 *
 * @param self A Python PyBitVector instance.
 * @param start Start index of the slice.
 * @param stop End index (exclusive) of the slice.
 * @param step Step size for the slice.
 * @param slicelength Number of elements in the resulting slice.
 * @param value Iterable of boolean-convertible Python objects.
 * @return 0 on success; -1 on error (with exception set).
 */
static int
py_bv_ass_slice(PyObject *self, size_t start, size_t stop, size_t step,
                size_t slicelength, PyObject *value)
{
    BitVector *bv = ((PyBitVector *) self)->bv;

    PyObject *seq =
        PySequence_Fast(value, "can only assign iterable to BitVector slice");
    if (!seq) {
        return -1;
    }

    Py_ssize_t vlen = PySequence_Fast_GET_SIZE(seq);
    if ((size_t) vlen != slicelength) {
        Py_DECREF(seq);
        PyErr_Format(PyExc_ValueError,
                     "attempt to assign sequence of length %zd "
                     "to slice of length %zu",
                     vlen, slicelength);
        return -1;
    }

    PyObject **items = PySequence_Fast_ITEMS(seq);

    size_t n_bits = bv->n_bits;
    for (size_t i = 0, idx = start; i < slicelength; ++i, idx += step) {
        if (n_bits <= idx) {
            Py_DECREF(seq);
            PyErr_SetString(PyExc_IndexError, "BitVector slice out of range");
            return -1;
        }
        int bit = PyObject_IsTrue(items[i]);
        if (bit < 0) {
            Py_DECREF(seq);
            return -1;
        }
        if (bit) {
            bv_set(bv, idx);
        }
        else {
            bv_clear(bv, idx);
        }
        ((PyBitVector *) self)->hash_cache = -1;
    }

    Py_DECREF(seq);
    return 0;
}

/**
 * @brief Implements BitVector.__setitem__ dispatch for index or slice.
 *
 * Delegates to py_bv_ass_item or py_bv_ass_slice depending on type of `arg`.
 * Does not support item deletion (value==NULL).
 *
 * @param self A Python PyBitVector instance.
 * @param arg Index or slice object.
 * @param value Python object to assign (must not be NULL).
 * @return 0 on success; -1 on error (with exception set).
 */
static int
py_bv_ass_subscript(PyObject *self, PyObject *arg, PyObject *value)
{
    if (value == NULL) {
        PyErr_SetString(PyExc_TypeError,
                        "BitVector does not support item deletion");
        return -1;
    }

    if (PyIndex_Check(arg)) {
        Py_ssize_t idx = PyNumber_AsSsize_t(arg, PyExc_IndexError);
        if (idx == -1 && PyErr_Occurred()) {
            return -1;
        }
        return py_bv_ass_item(self, idx, value);
    }

    if (PySlice_Check(arg)) {
        PyObject *slice = (PyObject *) arg;
        PyBitVector *bv = (PyBitVector *) self;
        Py_ssize_t start, stop, step, slicelength;
        if (PySlice_GetIndicesEx(slice, bv->bv->n_bits, &start, &stop, &step,
                                 &slicelength) < 0) {
            return -1;
        }
        return py_bv_ass_slice(self, (size_t) start, (size_t) stop,
                               (size_t) step, (size_t) slicelength, value);
    }

    PyErr_Format(PyExc_TypeError,
                 "indices must be integers or slices, not %.200s",
                 Py_TYPE(arg)->tp_name);
    return -1;
}

/**
 * @brief __contains__(BitVector, other) → boolean.
 * @param self A Python PyBitVector instance. (haystack).
 * @param value A Python PyBitVector instance (needle).
 * @return 1 if contained, 0 otherwise
 */
static int
py_bv_contains(PyObject *self, PyObject *value)
{
    if (!PyObject_TypeCheck((PyObject *) value, PyBitVectorPtr)) {
        return false;
    }

    PyBitVector *A = (PyBitVector *) self;
    PyBitVector *B = (PyBitVector *) value;
    return bv_contains_subvector(A->bv, B->bv);
}

/**
 * @struct PyBitVectorIter
 * @brief Iterator structure for PyBitVector
 *
 * Stores a reference to the original PyBitVector and tracks
 * the current bit position and buffer state for iteration.
 */
typedef struct {
    PyObject_HEAD PyBitVector
        *bv;               /**< Reference to the PyBitVector being iterated */
    size_t n_bits;         /**< Total number of bits in the vector */
    size_t position;       /**< Current bit index (0-based) */
    size_t word_index;     /**< Index into the 64-bit word array */
    uint64_t current_word; /**< Local copy of the active 64-bit word */
    uint64_t mask;         /**< Bit mask for next bit */
} PyBitVectorIter;

/**
 * @brief Deallocate a BitVector iterator object.
 *
 * Releases the reference to the parent PyBitVector and frees the iterator
 * struct.
 *
 * @param self A PyBitVectorIter instance.
 */
static void
py_bviter_dealloc(PyObject *self)
{
    PyBitVectorIter *iter = (PyBitVectorIter *) self;
    Py_XDECREF(iter->bv);
    Py_TYPE(iter)->tp_free(self);
}

/**
 * @brief Return the next bit as a Python boolean.
 *
 * Reads one bit from the internal buffer and shifts it out. If all bits have
 * been yielded, raises StopIteration.
 *
 * @param self A PyBitVectorIter instance.
 * @return Py_True or Py_False on success; NULL with StopIteration set at
 * end-of-iteration.
 */
static PyObject *
py_bviter_iternext(PyObject *self)
{
    PyBitVectorIter *iter = (PyBitVectorIter *) self;

    if (iter->position >= iter->n_bits) {
        PyErr_SetNone(PyExc_StopIteration);
        return NULL;
    }

    if (iter->mask == 0) {
        if (iter->word_index >= iter->bv->bv->n_words) {
            PyErr_SetNone(PyExc_StopIteration);
            return NULL;
        }
        iter->current_word = iter->bv->bv->data[iter->word_index++];
        iter->mask = 1ULL;
        cbits_prefetch(&iter->bv->bv->data[iter->word_index]);
    }

    int bit = (iter->current_word & iter->mask) != 0;
    iter->mask <<= 1;
    iter->position++;

    if (bit) {
        Py_RETURN_TRUE;
    }
    else {
        Py_RETURN_FALSE;
    }
}

/**
 * @brief Slots for the _BitVectorIter type.
 *
 * Defines deallocator, __iter__ and __next__.
 */
static PyType_Slot PyBitVectorIter_slots[] = {
    {Py_tp_dealloc, py_bviter_dealloc},
    {Py_tp_iter, PyObject_SelfIter},
    {Py_tp_iternext, py_bviter_iternext},
    {0, 0},
};

/**
 * @brief Type specification for cbits._BitVectorIter.
 *
 * This is the bit‐wise iterator returned by BitVector.__iter__().
 */
static PyType_Spec PyBitVectorIter_spec = {
    .name = "cbits._BitVectorIter",
    .basicsize = sizeof(PyBitVectorIter),
    .flags = Py_TPFLAGS_DEFAULT,
    .slots = PyBitVectorIter_slots,
};

/** Global pointer for the iterator type object */
static PyTypeObject *PyBitVectorIterType = NULL;

/**
 * @brief Create and return a new BitVector iterator.
 *
 * Implements the tp_iter slot. Allocates a fresh PyBitVectorIter, initializes
 * its state, and returns it.
 *
 * @param self A Python PyBitVector instance.
 * @return New iterator object or NULL on allocation failure.
 */
static PyObject *
py_bv_iter(PyObject *self)
{
    PyBitVector *bv = (PyBitVector *) self;
    PyBitVectorIter *iter = PyObject_New(PyBitVectorIter, PyBitVectorIterType);
    if (!iter) {
        return NULL;
    }
    Py_INCREF(bv);
    iter->bv = bv;
    iter->n_bits = bv->bv->n_bits;
    iter->position = 0;
    iter->word_index = 0;
    iter->current_word = 0;
    iter->mask = 0;

    return (PyObject *) iter;
}

/* -------------------------------------------------------------------------
 * Number Protocol
 * ------------------------------------------------------------------------- */

/**
 * @brief __and__(BitVector, BitVector) → BitVector.
 * @param a Left operand.
 * @param b Right operand.
 * @return New BitVector representing bitwise AND; NULL on error.
 */
static PyObject *
py_bv_and(PyObject *oA, PyObject *oB)
{
    CHECK_BV_BOTH(oA, oB)

    PyBitVector *A = (PyBitVector *) oA;
    PyBitVector *B = (PyBitVector *) oB;

    size_t size = A->bv->n_bits;
    if (size != B->bv->n_bits) {
        PyErr_Format(PyExc_ValueError, "length mismatch: A=%zu, B=%zu", size,
                     B->bv->n_bits);
        return NULL;
    }
    BitVector *C = bv_new(size);
    if (!C) {
        PyErr_SetString(PyExc_MemoryError,
                        "BitVector allocation failed in __and__");
        return NULL;
    }

    uint64_t *restrict a = A->bv->data;
    uint64_t *restrict b = B->bv->data;
    uint64_t *restrict c = C->data;

    size_t i = 0;
    for (; i + 3 < A->bv->n_words; i += 4) {
        cbits_prefetch(&a[i + 16]);
        cbits_prefetch(&b[i + 16]);

        c[i] = a[i] & b[i];
        c[i + 1] = a[i + 1] & b[i + 1];
        c[i + 2] = a[i + 2] & b[i + 2];
        c[i + 3] = a[i + 3] & b[i + 3];
    }
    for (; i < A->bv->n_words; ++i) {
        c[i] = a[i] & b[i];
    }
    bv_apply_tail_mask(C);
    return bv_wrap_new(C);
}

/**
 * @brief __iand__(BitVector, BitVector) in-place AND.
 * @param a Left operand (modified in place).
 * @param b Right operand.
 * @return Self on success, NULL on error.
 */
static PyObject *
py_bv_iand(PyObject *self, PyObject *arg)
{
    CHECK_BV_OBJ(arg)

    PyBitVector *A = (PyBitVector *) self;
    PyBitVector *B = (PyBitVector *) arg;

    size_t size = A->bv->n_bits;
    if (size != B->bv->n_bits) {
        PyErr_Format(PyExc_ValueError, "length mismatch: A=%zu, B=%zu", size,
                     B->bv->n_bits);
        return NULL;
    }

    uint64_t *restrict a = A->bv->data;
    uint64_t *restrict b = B->bv->data;

    size_t i = 0;
    for (; i + 3 < A->bv->n_words; i += 4) {
        cbits_prefetch(&a[i + 16]);
        cbits_prefetch(&b[i + 16]);

        a[i] &= b[i];
        a[i + 1] &= b[i + 1];
        a[i + 2] &= b[i + 2];
        a[i + 3] &= b[i + 3];
    }
    for (; i < A->bv->n_words; ++i) {
        a[i] &= b[i];
    }
    bv_apply_tail_mask(A->bv);
    A->bv->rank_dirty = true;
    A->hash_cache = -1;
    Py_INCREF(self);
    return self;
}

/**
 * @brief __or__(BitVector, BitVector) → BitVector.
 * @param a Left operand.
 * @param b Right operand.
 * @return New BitVector representing bitwise OR; NULL on error.
 */
static PyObject *
py_bv_or(PyObject *oA, PyObject *oB)
{
    CHECK_BV_BOTH(oA, oB)

    PyBitVector *A = (PyBitVector *) oA;
    PyBitVector *B = (PyBitVector *) oB;

    size_t size = A->bv->n_bits;
    if (size != B->bv->n_bits) {
        PyErr_Format(PyExc_ValueError, "length mismatch: A=%zu, B=%zu", size,
                     B->bv->n_bits);
        return NULL;
    }
    BitVector *C = bv_new(size);
    if (!C) {
        PyErr_SetString(PyExc_MemoryError,
                        "BitVector allocation failed in __or__");
        return NULL;
    }

    uint64_t *restrict a = A->bv->data;
    uint64_t *restrict b = B->bv->data;
    uint64_t *restrict c = C->data;

    size_t i = 0;
    for (; i + 3 < A->bv->n_words; i += 4) {
        cbits_prefetch(&a[i + 16]);
        cbits_prefetch(&b[i + 16]);

        c[i] = a[i] | b[i];
        c[i + 1] = a[i + 1] | b[i + 1];
        c[i + 2] = a[i + 2] | b[i + 2];
        c[i + 3] = a[i + 3] | b[i + 3];
    }
    for (; i < A->bv->n_words; ++i) {
        c[i] = a[i] | b[i];
    }
    bv_apply_tail_mask(C);
    return bv_wrap_new(C);
}

/**
 * @brief __ior__(BitVector, BitVector) in-place OR.
 * @param a Left operand (modified in place).
 * @param b Right operand.
 * @return Self on success, NULL on error.
 */
static PyObject *
py_bv_ior(PyObject *self, PyObject *arg)
{
    CHECK_BV_OBJ(arg)

    PyBitVector *A = (PyBitVector *) self;
    PyBitVector *B = (PyBitVector *) arg;

    size_t size = A->bv->n_bits;
    if (size != B->bv->n_bits) {
        PyErr_Format(PyExc_ValueError, "length mismatch: A=%zu, B=%zu", size,
                     B->bv->n_bits);
        return NULL;
    }

    uint64_t *restrict a = A->bv->data;
    uint64_t *restrict b = B->bv->data;
    size_t i = 0;
    for (; i + 3 < A->bv->n_words; i += 4) {
        cbits_prefetch(&a[i + 16]);
        cbits_prefetch(&b[i + 16]);

        a[i] |= b[i];
        a[i + 1] |= b[i + 1];
        a[i + 2] |= b[i + 2];
        a[i + 3] |= b[i + 3];
    }
    for (; i < A->bv->n_words; ++i) {
        a[i] |= b[i];
    }
    bv_apply_tail_mask(A->bv);
    A->bv->rank_dirty = true;
    A->hash_cache = -1;
    Py_INCREF(self);
    return self;
}

/**
 * @brief __xor__(BitVector, BitVector) → BitVector.
 * @param a Left operand.
 * @param b Right operand.
 * @return New BitVector representing bitwise XOR; NULL on error.
 */
static PyObject *
py_bv_xor(PyObject *oA, PyObject *oB)
{
    CHECK_BV_BOTH(oA, oB)

    PyBitVector *A = (PyBitVector *) oA;
    PyBitVector *B = (PyBitVector *) oB;

    size_t size = A->bv->n_bits;
    if (size != B->bv->n_bits) {
        PyErr_Format(PyExc_ValueError, "length mismatch: A=%zu, B=%zu", size,
                     B->bv->n_bits);
        return NULL;
    }
    BitVector *C = bv_new(size);
    if (!C) {
        PyErr_SetString(PyExc_MemoryError,
                        "BitVector allocation failed in __xor__");
        return NULL;
    }

    uint64_t *restrict a = A->bv->data;
    uint64_t *restrict b = B->bv->data;
    uint64_t *restrict c = C->data;

    size_t i = 0;
    for (; i + 3 < A->bv->n_words; i += 4) {
        cbits_prefetch(&a[i + 16]);
        cbits_prefetch(&b[i + 16]);

        c[i] = a[i] ^ b[i];
        c[i + 1] = a[i + 1] ^ b[i + 1];
        c[i + 2] = a[i + 2] ^ b[i + 2];
        c[i + 3] = a[i + 3] ^ b[i + 3];
    }
    for (; i < A->bv->n_words; ++i) {
        c[i] = a[i] ^ b[i];
    }
    bv_apply_tail_mask(C);
    return bv_wrap_new(C);
}

/**
 * @brief __ixor__(BitVector, BitVector) in-place XOR.
 * @param a Left operand (modified in place).
 * @param b Right operand.
 * @return Self on success, NULL on error.
 */
static PyObject *
py_bv_ixor(PyObject *self, PyObject *arg)
{
    CHECK_BV_OBJ(arg)

    PyBitVector *A = (PyBitVector *) self;
    PyBitVector *B = (PyBitVector *) arg;

    size_t size = A->bv->n_bits;
    if (size != B->bv->n_bits) {
        PyErr_Format(PyExc_ValueError, "length mismatch: A=%zu, B=%zu", size,
                     B->bv->n_bits);
        return NULL;
    }

    uint64_t *restrict a = A->bv->data;
    uint64_t *restrict b = B->bv->data;
    size_t i = 0;
    for (; i + 3 < A->bv->n_words; i += 4) {
        cbits_prefetch(&a[i + 16]);
        cbits_prefetch(&b[i + 16]);

        a[i] ^= b[i];
        a[i + 1] ^= b[i + 1];
        a[i + 2] ^= b[i + 2];
        a[i + 3] ^= b[i + 3];
    }
    for (; i < A->bv->n_words; ++i) {
        a[i] ^= b[i];
    }
    bv_apply_tail_mask(A->bv);
    A->bv->rank_dirty = true;
    A->hash_cache = -1;
    Py_INCREF(self);
    return self;
}

/**
 * @brief __invert__(BitVector) → BitVector.
 * @param self A Python PyBitVector instance.
 * @return New BitVector instance with all bits toggled, NULL on error;
 */
static PyObject *
py_bv_invert(PyObject *self)
{
    PyBitVector *A = (PyBitVector *) self;
    BitVector *C = bv_new(A->bv->n_bits);
    if (!C) {
        PyErr_SetString(PyExc_MemoryError,
                        "BitVector allocation failed in __invert__");
        return NULL;
    }
    uint64_t *restrict a = A->bv->data;
    uint64_t *restrict c = C->data;

    size_t i = 0;
    for (; i + 3 < A->bv->n_words; i += 4) {
        cbits_prefetch(&a[i + 16]);

        c[i] = ~a[i];
        c[i + 1] = ~a[i + 1];
        c[i + 2] = ~a[i + 2];
        c[i + 3] = ~a[i + 3];
    }
    for (; i < A->bv->n_words; ++i) {
        c[i] = ~a[i];
    }
    bv_apply_tail_mask(C);
    return bv_wrap_new(C);
}

/**
 * @brief __bool__(BitVector) → boolean.
 * @param self A Python PyBitVector instance.
 * @return 1 if any bit is set, 0 otherwise
 */
static int
py_bv_bool(PyObject *self)
{
    PyBitVector *bvself = (PyBitVector *) self;
    return bv_rank(bvself->bv, bvself->bv->n_bits - 1) > 0;
}

/* -------------------------------------------------------------------------
 * Properties
 * ------------------------------------------------------------------------- */

/**
 * @brief Getter for the read-only "bits" property.
 * @param self A Python PyBitVector instance.
 * @param closure Unused.
 * @return Python integer of the bit-length
 */
static PyObject *
py_bv_get_size(PyObject *self, void *closure)
{
    PyBitVector *bvself = (PyBitVector *) self;
    return PyLong_FromSize_t(bvself->bv->n_bits);
}

/**
 * @brief Setter for the read-only "bits" property, always raises.
 * @param self A Python PyBitVector instance.
 * @param closure Unused.
 * @return -1 and sets AttributeError
 */
static int
py_bv_set_size(PyObject *self, void *closure)
{
    PyErr_SetString(PyExc_AttributeError, "size is read-only");
    return -1;
}

/**
 * @brief Property definitions for the BitVector type.
 *
 * This table lists all read-only and writable properties exposed
 * on the Python BitVector object.
 *
 * @see PyGetSetDef
 */
static PyGetSetDef PyBitVector_getset[] = {
    {"bits", (getter) py_bv_get_size, (setter) py_bv_set_size,
     PyDoc_STR("The number of bits"), NULL},
    {NULL},
};

/* -------------------------------------------------------------------------
 * Type Object Definition
 * ------------------------------------------------------------------------- */

PyDoc_STRVAR(
    BitVector__doc__,
    "BitVector(size: int)\n"
    "\n"
    "A high-performance, fixed-size 1D bit array.\n\n"
    "Supports random access, slicing, bitwise ops, and fast iteration.\n\n"
    "Parameters\n"
    "----------\n"
    "size : int\n"
    "    Number of bits in the vector.\n\n"
    "Attributes\n"
    "----------\n"
    "bits : int\n"
    "    The length of this BitVector.\n");

/**
 * @brief Slot table for the PyBitVector type.
 *
 * Maps Python’s type callbacks (new, init, dealloc, repr, etc.)
 * and protocol slots (sequence, number, richcompare) to our C functions.
 *
 * @see PyType_Slot
 */
static PyType_Slot PyBitVector_slots[] = {
    {Py_tp_doc, (const char *) BitVector__doc__},

    {Py_tp_new, py_bv_new},
    {Py_tp_init, py_bv_init},
    {Py_tp_dealloc, py_bv_free},
    {Py_tp_methods, BitVector_methods},
    {Py_tp_repr, py_bv_repr},
    {Py_tp_str, py_bv_str},
    {Py_tp_getset, PyBitVector_getset},
    {Py_tp_richcompare, py_bv_richcompare},
    {Py_tp_hash, py_bv_hash},

    {Py_tp_iter, py_bv_iter},
    {Py_mp_length, py_bv_len},
    {Py_mp_subscript, py_bv_subscript},
    {Py_mp_ass_subscript, py_bv_ass_subscript},
    {Py_sq_contains, py_bv_contains},

    {Py_nb_and, py_bv_and},
    {Py_nb_inplace_and, py_bv_iand},
    {Py_nb_or, py_bv_or},
    {Py_nb_inplace_or, py_bv_ior},
    {Py_nb_xor, py_bv_xor},
    {Py_nb_inplace_xor, py_bv_ixor},
    {Py_nb_invert, py_bv_invert},
    {Py_nb_bool, py_bv_bool},

    {0, 0},
};

/**
 * @brief Type specification for BitVector.
 *
 * This structure describes the Python type name, size,
 * inheritance flags, and slot table used to create the type.
 *
 * @see PyType_Spec
 */
PyType_Spec PyBitVector_spec = {
    .name = "cbits.BitVector",
    .basicsize = sizeof(PyBitVector),
    .itemsize = 0,
    .flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .slots = PyBitVector_slots,
};

/* -------------------------------------------------------------------------
 * Module Init
 * ------------------------------------------------------------------------- */

#if PY_VERSION_HEX >= 0x030C0000
    /**
     * @def ADD_OBJECT(module, name, object)
     * @brief Add a PyObject to a module, handling reference counts portably.
     *
     * On Python ≥ 3.12, PyModule_AddObjectRef() is available and automatically
     * steals a reference. On older versions, we fall back to
     * PyModule_AddObject() and manually increment the reference on success.
     *
     * @param module The Python module to which the object is added.
     * @param name The attribute name under which the object is registered.
     * @param object The PyObject pointer to add.
     * @return 0 on success, -1 on failure (exception set by
     * PyModule_AddObject*).
     */
    #define ADD_OBJECT(module, name, object) \
        (PyModule_AddObjectRef(module, name, object))
#else

    /**
     * @def ADD_OBJECT(module, name, object)
     * @brief Add a PyObject to a module, handling reference counts portably.
     *
     * On Python ≥ 3.12, PyModule_AddObjectRef() is available and automatically
     * steals a reference. On older versions, we fall back to
     * PyModule_AddObject() and manually increment the reference on success.
     *
     * @param module The Python module to which the object is added.
     * @param name The attribute name under which the object is registered.
     * @param object The PyObject pointer to add.
     * @return 0 on success, -1 on failure (exception set by
     * PyModule_AddObject*).
     */
    #define ADD_OBJECT(module, name, object)           \
        (PyModule_AddObject(module, name, object) == 0 \
             ? (Py_XINCREF(object), 0)                 \
             : -1)
#endif
#ifdef PYPY_VERSION
    #undef ADD_OBJECT
static inline int
cbits_add_object(PyObject *module, const char *name, PyObject *obj)
{
    int err = PyModule_AddObject(module, name, obj);
    if (err < 0) {
        return err;
    }
    Py_XINCREF(obj);
    return 0;
}

    /**
     * @def ADD_OBJECT(module, name, object)
     * @brief Add a PyObject to a module, handling reference counts portably.
     *
     * On Python ≥ 3.12, PyModule_AddObjectRef() is available and automatically
     * steals a reference. On older versions, we fall back to
     * PyModule_AddObject() and manually increment the reference on success.
     *
     * @param module The Python module to which the object is added.
     * @param name The attribute name under which the object is registered.
     * @param object The PyObject pointer to add.
     * @return 0 on success, -1 on failure (exception set by
     * PyModule_AddObject*).
     */
    #define ADD_OBJECT(module, name, object) \
        cbits_add_object(module, name, object)
#endif

/**
 * @brief Module exec callback: register BitVector type and metadata.
 * @param module New module instance.
 * @return 0 on success; -1 on failure (exception set).
 */
static int
cbits_module_exec(PyObject *module)
{
/* Register BitVector */
#if defined(_MSC_VER)
    init_cpu_dispatch();
#endif
#if PY_VERSION_HEX >= 0x030B0000
    PyBitVectorPtr = (PyTypeObject *) PyType_FromModuleAndSpec(
        module, &PyBitVector_spec, NULL);
    if (!PyBitVectorPtr) {
        PyErr_SetString(PyExc_RuntimeError,
                        "Failed to initialize BitVector type");
        return -1;
    }
    PyBitVectorIterType = (PyTypeObject *) PyType_FromModuleAndSpec(
        module, &PyBitVectorIter_spec, NULL);
    if (!PyBitVectorIterType) {
        PyErr_SetString(PyExc_RuntimeError,
                        "Failed to initialize _BitVectorIter type");
        return -1;
    }
#else
    PyBitVectorPtr = (PyTypeObject *) PyType_FromSpec(&PyBitVector_spec);
    if (!PyBitVectorPtr || PyType_Ready(PyBitVectorPtr) < 0) {
        PyErr_SetString(PyExc_RuntimeError,
                        "Failed to initialize BitVector type");
        return -1;
    }
    PyBitVectorIterType =
        (PyTypeObject *) PyType_FromSpec(&PyBitVectorIter_spec);
    if (!PyBitVectorIterType || PyType_Ready(PyBitVectorIterType) < 0) {
        PyErr_SetString(PyExc_RuntimeError,
                        "Failed to initialize _BitVectorIter type");
        return -1;
    }
#endif
    if (!PyBitVectorPtr) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to create BitVector type");
        return -1;
    }

    if (ADD_OBJECT(module, "BitVector", (PyObject *) PyBitVectorPtr) < 0) {
        return -1;
    }

    /* Metadata */
    if (PyModule_AddStringConstant(module, "__author__", "lambdaphoenix") <
        0) {
        return -1;
    }
    if (PyModule_AddStringConstant(module, "__version__", "0.2.0") < 0) {
        return -1;
    }
    if (PyModule_AddStringConstant(module, "__license__", "Apache-2.0") < 0) {
        return -1;
    }
    if (PyModule_AddStringConstant(
            module, "__license_url__",
            "https://github.com/lambdaphoenix/cbits/blob/main/LICENSE") < 0) {
        return -1;
    }
    return 0;
}

/**
 * @brief Module initialization slots.
 *
 * Lists callbacks invoked when the module is loaded; here,
 * we use Py_mod_exec to register types and module constants.
 *
 * @see PyModuleDef_Slot
 */
static PyModuleDef_Slot cbits_module_slots[] = {
    {Py_mod_exec, cbits_module_exec},
    {0, NULL},
};

/**
 * @brief Definition of the _cbits extension module.
 *
 * Describes the module’s name, docstring, memory footprint,
 * and its initialization slot table.
 *
 * @see PyModuleDef
 */
static PyModuleDef cbits_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "_cbits",
    .m_doc = PyDoc_STR("cbits"),
    .m_size = 0,
    .m_slots = cbits_module_slots,
};

/**
 * @brief Python entrypoint for _cbits extension module.
 * @param void
 * @return New module object (borrowed reference).
 */
PyMODINIT_FUNC
PyInit__cbits(void)
{
    return PyModuleDef_Init(&cbits_module);
}
