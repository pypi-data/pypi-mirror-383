"""Methods implementing J verbs.

Where possible, dyads are implemented as ufuncs. This equips the dyads with
efficient reduce, outer and accumulate methods over arrays.

Specifically where a dyadic application of a verb has left and right rank both 0,
this is equivalent to elementwise application of the verb to the arrays. This is
what ufuncs capture. For example, dyadic `+` is equivalent to `np.add` and dyadic
`*` is equivalent to `np.multiply`.

It is important that all implementations here share the same "rank" characteristics
as their J counterparts.
"""

import itertools
import math
import random
from typing import Callable

import numpy as np
from jinx.errors import (
    DomainError,
    JIndexError,
    JinxNotImplementedError,
    LengthError,
    ValenceError,
)
from jinx.execution.numpy.conversion import box_dtype
from jinx.execution.numpy.helpers import (
    get_fill_value,
    hash_box,
    increase_ndim,
    is_box,
    is_same_array,
    mark_ufunc_based,
    maybe_pad_by_duplicating_atoms,
    maybe_pad_with_fill_value,
)
from jinx.word_formation import form_words

np.seterr(divide="ignore")


def eq_monad(y: np.ndarray) -> np.ndarray:
    nub = tildedot_monad(y)
    result = []
    for item in nub:
        value = np.all(item == y, axis=tuple(range(1, y.ndim)))
        result.append(value)
    return np.asarray(result).astype(np.int64)


@mark_ufunc_based
def percent_monad(y: np.ndarray) -> np.ndarray:
    """% monad: returns the reciprocal of the array."""
    # N.B. np.reciprocal does not support integer types, use division instead.
    return 1 / y


@mark_ufunc_based
def percentco_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.power(y, 1 / x)


def plusdot_monad(y: np.ndarray) -> np.ndarray:
    """+. monad: returns real and imaginary parts of numbers."""
    y = np.atleast_1d(y)
    return np.concatenate([np.real(y), np.imag(y)], axis=-1)


@mark_ufunc_based
def plusco_monad(y: np.ndarray) -> np.ndarray:
    """+: monad: double the values in the array."""
    return 2 * y


@mark_ufunc_based
def minusdot_monad(y: np.ndarray) -> np.ndarray:
    """-.: monad: returns 1 - y."""
    return 1 - y


@mark_ufunc_based
def minusco_monad(y: np.ndarray) -> np.ndarray:
    """-: monad: halve the values in the array."""
    return y / 2


def minusco_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """-: dyad: match, returns true if x and y have same shape and values."""
    is_equal = np.array_equal(x, y, equal_nan=True)
    return np.asarray(is_equal)


@mark_ufunc_based
def plusco_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """+: dyad: not-or operation."""
    # N.B. This is not the same as the J implementation which forbids values
    # outside of 0 and 1.
    return ~np.logical_or(x, y).astype(np.int64)


def stardot_monad(y: np.ndarray) -> np.ndarray:
    """*. monad: convert x-y coordinates to r-theta coordinates."""
    y = np.atleast_1d(y)
    r = np.abs(y)
    theta = np.angle(y)
    return np.concatenate([r, theta])


@mark_ufunc_based
def starco_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """*: dyad: not-and operation."""
    # N.B. This is not the same as the J implementation which forbids values
    # outside of 0 and 1.
    return ~np.logical_and(x, y).astype(np.int64)


@mark_ufunc_based
def hatdot_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """^. dyad: logarithm of y to the base x."""
    return np.log(y) / np.log(x)


def lt_monad(y: np.ndarray) -> np.ndarray:
    """< monad: box a noun."""
    return np.array([(y,)], dtype=box_dtype).squeeze()


def gt_monad(y: np.ndarray) -> np.ndarray:
    """> monad: open a boxed element or array of boxed elements."""
    if not is_box(y):
        return y
    elements = [np.asarray(item[0]) for item in y.ravel().tolist()]
    elements_padded = maybe_pad_with_fill_value(elements)
    return np.asarray(elements_padded).squeeze()


@mark_ufunc_based
def ltco_monad(y: np.ndarray) -> np.ndarray:
    """<: monad: decrements the array."""
    return y - 1


@mark_ufunc_based
def gtco_monad(y: np.ndarray) -> np.ndarray:
    """>: monad: increments the array."""
    return y + 1


def comma_monad(y: np.ndarray) -> np.ndarray:
    """, monad: returns the flattened array."""
    y = np.atleast_1d(y)
    return np.ravel(y)


def comma_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """, dyad: returns array containing the items of x followed by the items of y."""

    x = np.atleast_1d(x)
    y = np.atleast_1d(y)

    dtype = np.promote_types(x.dtype, y.dtype)

    if x.shape == (1,):
        x = np.full_like(y[:1], x[0], dtype=dtype)
    elif y.shape == (1,):
        y = np.full_like(x[:1], y[0], dtype=dtype)
    else:
        trailing_dims = [
            max(xs, ys)
            for xs, ys in itertools.zip_longest(
                reversed(x.shape), reversed(y.shape), fillvalue=1
            )
        ]
        trailing_dims.reverse()
        trailing_dims = trailing_dims[1:]  # ignore dimension that we concatenate along

        ndmin = max(x.ndim, y.ndim)
        x = increase_ndim(x, ndmin)
        y = increase_ndim(y, ndmin)

        x = np.pad(
            x,
            [(0, 0)] + [(0, d - s) for s, d in zip(x.shape[1:], trailing_dims)],
            constant_values=get_fill_value(x),
        )
        y = np.pad(
            y,
            [(0, 0)] + [(0, d - s) for s, d in zip(y.shape[1:], trailing_dims)],
            constant_values=get_fill_value(y),
        )

    return np.concatenate([x, y], axis=0)


def commadot_monad(y: np.ndarray) -> np.ndarray:
    """,. monad: ravel items."""
    y = np.atleast_1d(y)
    return y.reshape(y.shape[0], -1)


def commadot_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """,. dyad: join each item of x to each item of y."""
    x = np.atleast_1d(x)
    y = np.atleast_1d(y)

    if x.shape == (1,):
        x = np.repeat(x, y.shape[0], axis=0)

    if y.shape == (1,):
        y = np.repeat(y, x.shape[0], axis=0)

    if len(x) != len(y):
        raise LengthError(
            f"executing dyad ,. shapes {x.shape} and {y.shape} have different numbers of items"
        )

    items = []
    for x_item, y_item in zip(x, y, strict=True):
        items.append(comma_dyad(x_item, y_item))

    if len(items) == 1:
        return np.asarray(items[0])

    result = maybe_pad_with_fill_value(items)
    return np.asarray(result)


def commaco_monad(y: np.ndarray) -> np.ndarray:
    """,: monad: create array with rank 1 more than rank of y."""
    if np.isscalar(y) or y.shape == ():
        return np.array([y])
    return y[np.newaxis, :]


def commaco_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """,: dyad: create a two item array from x and y."""
    items = maybe_pad_by_duplicating_atoms([x, y], ignore_first_dim=False)
    return np.asarray(items)


@mark_ufunc_based
def bar_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """| dyad: remainder when dividing y by x."""
    x = np.atleast_1d(x)
    y = np.atleast_1d(y)
    # In J, '0 | y' is y, not 0.
    result = np.where(x, np.mod(y, x), y)
    if result.ndim == 1 and result.shape[0] == 1:
        return result[0]
    return result


def bardot_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """|. dyad: rotate the array."""
    y = np.atleast_1d(y)
    x = np.atleast_1d(x)
    if x.shape[-1] > y.ndim:
        raise ValueError(
            f"length error, executing dyad |. (x has {x.shape[-1]} atoms but y only has {y.ndim} axes)"
        )
    return np.roll(y, -x, axis=tuple(range(x.shape[-1])))


def barco_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """|: dyad: rearrange the axes of the array."""
    x = np.atleast_1d(x)
    if len(x) > y.ndim:
        raise JIndexError("|: x has more items than y has dimensions")
    if any(item > y.ndim for item in x):
        raise JIndexError("|: x has items greater than y has dimensions")
    if len(set(x)) != len(x):
        raise JIndexError("|: x contains a duplicate axis number")
    first = []
    for i in range(y.ndim):
        if i not in x:
            first.append(i)
    return np.transpose(y, axes=first + x.tolist())


def tildedot_monad(y: np.ndarray) -> np.ndarray:
    """~. monad: remove duplicates from a list."""
    y = np.atleast_1d(y)

    if is_box(y):
        seen = set()
        result = []
        for item in y:
            h = hash_box(item)
            if h not in seen:
                result.append(item if is_box(item) else (item[0],))
            seen.add(h)
        return np.array(result, dtype=box_dtype).squeeze()

    uniq, idx = np.unique(y, return_index=True, axis=0)
    return uniq[np.argsort(idx)]


def tildeco_monad(y: np.ndarray) -> np.ndarray:
    """~: monad: nub sieve."""
    y = np.atleast_1d(y)
    _, idx = np.unique(y, return_index=True, axis=0)
    result = np.zeros(y.shape[0], dtype=np.int64)
    result[idx] = 1
    return result


def dollar_monad(y: np.ndarray) -> np.ndarray:
    """$ monad: returns the shape of the array."""
    if isinstance(y, str):
        return np.array([len(y)])
    if np.isscalar(y) or y.shape == ():
        # Differs from the J implementation which returns a missing value for shape of scalar.
        return np.array(0)
    return np.array(y.shape)


def dollar_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """$ dyad: create an array with a particular shape.

    Does not support custom fill values at the moment.
    Does not support INFINITY as an atom of x.
    """
    if np.isscalar(x) or x.shape == ():
        if x < 0 or not np.issubdtype(x.dtype, np.integer):
            raise DomainError(f"Invalid shape: {x}")

    if np.isscalar(x) or x.shape == ():
        x_shape = (np.squeeze(x),)
    else:
        x_shape = tuple(x)

    if np.isscalar(y) or y.shape == ():
        if is_box(y):
            result = np.array([y] * np.prod(x_shape), dtype=box_dtype).reshape(x_shape)
        else:
            result = np.empty(x_shape, dtype=y.dtype)
            result[:] = y
        return result

    output_shape = x_shape + y.shape[1:]
    data = y.ravel()
    repeat, fill = divmod(np.prod(output_shape), data.size)
    result = np.concatenate([np.tile(data, repeat), data[:fill]]).reshape(output_shape)
    return result


def idot_monad(y: np.ndarray) -> np.ndarray:
    """i. monad: returns increasing/decreasing sequence of integer wrapperd to shape y."""
    arr = np.atleast_1d(y)
    if not np.issubdtype(y.dtype, np.integer):
        raise DomainError("y has nonintegral value")
    shape = abs(arr)
    n = np.prod(shape)
    axes_to_flip = np.where(arr < 0)[0]
    result = np.arange(n).reshape(shape)
    return np.flip(result, axes_to_flip)


def icapdot_monad(y: np.ndarray) -> np.ndarray:
    """I. monad: return indexes of every 1 in the Boolean list y."""
    arr = np.atleast_1d(y)
    if not (np.issubdtype(y.dtype, np.integer) or np.issubdtype(y.dtype, np.bool_)):
        raise DomainError("y has nonintegral value")

    if np.any(arr < 0):
        raise DomainError("y has negative values")

    indexes = np.where(arr)[0]
    nonzero = arr[indexes]
    return np.repeat(indexes, nonzero)


def number_monad(y: np.ndarray) -> np.ndarray:
    """# monad: count number of items in y."""
    if isinstance(y, str):
        return np.array(len(y))
    if np.isscalar(y) or y.shape == ():
        return np.array(1)
    return np.array(y.shape[0])


def number_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """# dyad: copy items in y exactly x times."""
    return np.repeat(y, x, axis=0)


def numberdot_monad(y: np.ndarray) -> np.ndarray:
    """#. monad: return corresponding number of a binary numeral."""
    y = np.atleast_1d(y)
    weights = 2 ** np.arange(y.size, dtype=np.int64)[::-1]
    return np.dot(y, weights)


def numberdot_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """#. dyad: generalizes #.y to bases other than 2 (including mixed bases)."""
    x = np.atleast_1d(x)
    y = np.atleast_1d(y)

    if 1 < len(x) != len(y):
        raise LengthError(
            f"Error executing dyad #. shapes {len(x)} and {len(y)} do not conform"
        )

    if len(x) == 1:
        x = np.full_like(y, x[0], dtype=np.int64)

    weights = np.multiply.accumulate(x[1:][::-1])[::-1]
    return np.dot(y[:-1], weights) + y[-1]


def numberco_monad(y: np.ndarray) -> np.ndarray:
    """#: monad: return the binary expansion of y as a boolean list."""
    y = np.atleast_1d(y)

    if np.issubdtype(y.dtype, np.floating):
        is_y_floating = True
        floor_y = np.floor(y)
        fractional_part = y - floor_y
        y = floor_y.astype(np.int64)
    else:
        is_y_floating = False

    if np.all(y == 0):
        max_bits = 1
    else:
        max_bits = np.floor(np.log2(np.max(np.abs(y)))).astype(int) + 1

    # Convert negative numbers to two's complement form.
    # They become positive, and then the bits are inverted.
    is_negative = y < 0
    y[is_negative] = ~y[is_negative]

    remainders = []

    for _ in range(max_bits):
        bits = y % 2
        y >>= 1
        remainders.append(bits)

    result = np.stack(remainders[::-1], axis=-1)
    result[is_negative] = 1 - result[is_negative]

    if is_y_floating:
        result = result.astype(np.float64)
        result[..., -1] += fractional_part

    if result.ndim > 1 and result.shape[0] == 1:
        result = result.reshape(result.shape[1:])

    return result


@mark_ufunc_based
def squarelf_monad(y: np.ndarray) -> np.ndarray:
    """[ monad: returns the whole array."""
    return y


@mark_ufunc_based
def squarelf_dyad(x: np.ndarray, _: np.ndarray) -> np.ndarray:
    """[ dyad: returns x."""
    return x


squarerf_monad = squarelf_monad


def squarerfco_monad(y: np.ndarray) -> np.ndarray:
    """[: monad: raise a ValenceError."""
    raise ValenceError("[: must be part of a capped fork.")


def squarerfco_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """[: dyad: raise a ValenceError."""
    raise ValenceError("[: must be part of a capped fork.")


def squarerf_dyad(_: np.ndarray, y: np.ndarray) -> np.ndarray:
    """] dyad: returns y."""
    return y


def slashco_monad(y: np.ndarray) -> np.ndarray:
    """/: monad: permutation that sorts y in increasing order."""
    y = np.atleast_1d(y)
    if y.ndim == 1:
        return np.argsort(y, stable=True)

    # Ravelled items of y are sorted lexicographically.
    y = y.reshape(len(y), -1)
    return np.lexsort(np.rot90(y))


def slashco_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """/: monad: sort y in increasing order."""
    y = np.atleast_1d(y)

    if is_same_array(x, y):
        # This handles /:~
        if x.ndim == 1:
            return np.sort(y, kind="stable")
        idx = slashco_monad(y)
        return y[idx]

    idx = slashco_monad(y)
    return x[idx]


def bslashco_monad(y: np.ndarray) -> np.ndarray:
    r"""\: monad: permutation that sorts y in decreasing order."""
    y = np.atleast_1d(y)
    if y.ndim == 1:
        # Stable sort in decreasing order.
        # np.argsort(a)[::-1] on its own does not work as the indices of
        # equal elements will appear reversed in the result.
        return len(y) - 1 - np.argsort(y[::-1], kind="stable")[::-1]

    y = y.reshape(len(y), -1)
    return len(y) - 1 - np.lexsort(np.rot90(y[::-1]))[::-1]


def bslashco_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    r"""\: dyad: sort y in decreasing order."""
    y = np.atleast_1d(y)

    if is_same_array(x, y):
        # This handles \:~
        if x.ndim == 1:
            # Not technically correct (see comment on monad above), but
            # good enough for now.
            return np.flip(np.sort(y, kind="stable"))
        idx = bslashco_monad(y)
        return y[idx]

    idx = bslashco_monad(y)
    return x[idx]


def curlylf_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """{ dyad: select item with index x from array y."""
    y = np.atleast_1d(y)

    if not is_box(x):
        if not np.issubdtype(x.dtype, np.integer):
            raise DomainError("{ dyad: x must be an integer")
        try:
            return y[x]
        except IndexError:
            raise JIndexError(
                f"{{ dyad: x {x} is out of bounds for y with shape {y.shape}"
            ) from None

    x_inner = gt_monad(x)

    if len(x_inner) > y.ndim:
        raise LengthError(
            f"{{ dyad: selector is overlong x has length {len(x_inner)} but rank of y is only {y.ndim}"
        )

    if not is_box(x_inner):
        if not np.issubdtype(x_inner.dtype, np.integer):
            raise DomainError("{ dyad: indices must be integers")
        try:
            return y[tuple(x_inner)]
        except IndexError:
            raise JIndexError(
                f"{{ dyad: x {x_inner} is out of bounds for y with shape {y.shape}"
            ) from None

    x_inner_inner = gt_monad(x_inner)

    if len(x_inner_inner) > y.ndim:
        raise LengthError(
            f"{{ dyad: selector is overlong x has length {len(x_inner_inner)} but rank of y is only {y.ndim}"
        )

    if not all(np.issubdtype(item.dtype, np.integer) for item in x_inner_inner):
        raise DomainError("{ dyad: indices must be integers")

    try:
        return y[np.ix_(*x_inner_inner)]
    except IndexError:
        raise JIndexError(
            f"{{ dyad: x {x_inner} is out of bounds for y with shape {y.shape}"
        ) from None


def curlylfdot_monad(y: np.ndarray) -> np.ndarray:
    """{. monad: returns the first item of y."""
    y = np.atleast_1d(y)
    if y.size == 0:
        return np.array([])
    return y[0]


def curlylfdot_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """{. dyad: the leading x items of y."""
    x = np.atleast_1d(x)
    y = np.atleast_1d(y)

    if len(x) > y.ndim:
        raise LengthError(f"x has {len(x)} atoms but y has only {y.ndim} axes")

    padding = []
    slices = []

    for dim, take in enumerate(x):
        if take == 0:
            raise JinxNotImplementedError(
                "{. dyad: Dimension with 0 items is not supported"
            )
        elif take > y.shape[dim]:
            padding.append((0, take - y.shape[dim]))
            slices.append(slice(None))
        elif take < -y.shape[dim]:
            padding.append((-take - y.shape[dim], 0))
            slices.append(slice(None))
        elif take < 0:
            padding.append((0, 0))
            slices.append(slice(y.shape[dim] + take, None))
        else:
            padding.append((0, 0))
            slices.append(slice(0, take))

    if len(x) < y.ndim:
        padding += [(0, 0)] * (y.ndim - len(x))

    result = y[tuple(slices)]
    result = np.pad(result, padding, mode="constant", constant_values=get_fill_value(y))
    return result


def curlyrtdot_monad(y: np.ndarray) -> np.ndarray:
    """}. monad: drop leading item from y."""
    y = np.atleast_1d(y)
    if y.size == 0:
        return np.array([])
    return y[1:]


def curlyrtdot_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """}. monad: drop leading x items from y."""
    x = np.atleast_1d(x)
    y = np.atleast_1d(y)

    if len(x) > y.ndim:
        raise LengthError(f"x has {len(x)} atoms but y has only {y.ndim} axes")

    if y.size == 0:
        return np.array([])

    padding = []
    slices = []

    for dim, drop in enumerate(x):
        if drop == 0:
            padding.append((0, 0))
            slices.append(slice(None))
        elif drop > y.shape[dim]:
            raise JinxNotImplementedError("}. dyad: empty dimension is not supported")
        elif drop < -y.shape[dim]:
            raise JinxNotImplementedError("}. dyad: empty dimension is not supported")
        elif drop < 0:
            padding.append((0, 0))
            slices.append(slice(None, y.shape[dim] + drop))
        else:
            padding.append((0, 0))
            slices.append(slice(drop, None))

    if len(x) < y.ndim:
        padding += [(0, 0)] * (y.ndim - len(x))

    result = y[tuple(slices)]
    result = np.pad(result, padding, mode="constant", constant_values=get_fill_value(y))
    return result


def curlylfco_monad(y: np.ndarray) -> np.ndarray:
    """{: monad: return last item of y."""
    if np.isscalar(y) or y.shape == ():
        return np.asarray(y)
    return y[-1]


def curlyrtco_monad(y: np.ndarray) -> np.ndarray:
    """}: monad: drop last item of y."""
    y = np.atleast_1d(y)
    return y[:-1] if y.size > 0 else np.array([], dtype=y.dtype)


def bang_monad(y: np.ndarray) -> np.ndarray:
    """! monad: returns y factorial (and more generally the gamma function of 1+y)."""
    if isinstance(y, int) or np.issubdtype(y.dtype, np.integer) and y >= 0:
        return np.asarray(math.factorial(y))
    return np.asarray(math.gamma(1 + y))


def bang_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """! dyad: returns y-Combinations-x."""
    if (isinstance(y, int) or np.issubdtype(y.dtype, np.integer) and y >= 0) and (
        isinstance(x, int) or np.issubdtype(x.dtype, np.integer) and x >= 0
    ):
        return np.asarray(math.comb(y, x))
    x_ = bang_monad(x)
    y_ = bang_monad(y)
    x_y = bang_monad(y - x)
    return np.asarray(y_ / x_ / x_y)


def semi_monad(y: np.ndarray) -> np.ndarray:
    """; monad: remove one level of boxing from a noun."""
    if not is_box(y):
        return y

    y = y.ravel()
    items = [item[0] for item in y.tolist()]

    is_all_boxed = all(is_box(item) for item in items)
    is_all_not_boxed = all(not is_box(item) for item in items)
    if not is_all_boxed and not is_all_not_boxed:
        raise DomainError("Contents are incompatible: numeric and boxed")

    items = maybe_pad_by_duplicating_atoms(items, ignore_first_dim=True)
    return np.concatenate(items, axis=0)


def semi_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """; dyad: link two nouns into a box."""
    x = lt_monad(x)
    if not is_box(y):
        y = lt_monad(y)

    x = np.atleast_1d(x)
    y = np.atleast_1d(y)
    return np.concatenate([x, y], axis=0)


def semico_monad(y: np.ndarray) -> np.ndarray:
    """;: monad: partition string into boxed words according to J's rules for word formation."""
    if not np.issubdtype(y.dtype, np.str_):
        raise DomainError(";: monad: y must be a string")
    string = "".join(y)
    words = [word.value for word in form_words(string)]
    return np.array(words, dtype=box_dtype)


def query_monad(y: np.ndarray) -> np.ndarray:
    """? monad: generates a random number uniformly distributed in a range determined by integer y."""
    if not np.issubdtype(y.dtype, np.integer) or y < 0:
        raise DomainError("y must be a positive integer")

    if y == 0:
        result = random.random()

    elif y == 1:
        result = 0

    elif y == 2:
        result = random.choice([0, 1])

    else:
        result = random.randint(0, int(y))

    return np.asarray(result)


def query_dyad(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """? dyad: select x items at random from list i.y."""
    if not np.issubdtype(y.dtype, np.integer) or y < 0:
        raise DomainError("y must be a positive integer")

    if not np.issubdtype(x.dtype, np.integer) or x < 0:
        raise DomainError("x must be a positive integer")

    if x == 0:
        # This should return "empty" but Jinx does not have a concept of empty.
        return np.asarray(0)

    rng = np.random.default_rng()
    return rng.choice(y, size=x, replace=False)


MonadT = Callable[[np.ndarray], np.ndarray]
DyadT = Callable[[np.ndarray, np.ndarray], np.ndarray]


def cast_bool_to_int(func: np.ufunc) -> DyadT:
    @mark_ufunc_based
    def func_(x: np.ndarray, y: np.ndarray) -> np.ndarray:
        result = func(x, y)
        return result.view(np.int8)

    return func_


# Use NotImplemented for monads or dyads that have not yet been implemented in Jinx.
# Use None for monadic or dyadic valences of the verb do not exist in J.
VERB_MAP: dict[str, tuple[MonadT | None, DyadT | None]] = {
    # VERB: (MONAD, DYAD)
    "EQ": (eq_monad, cast_bool_to_int(np.equal)),
    "MINUS": (np.negative, np.subtract),
    "MINUSDOT": (minusdot_monad, NotImplemented),
    "MINUSCO": (minusco_monad, minusco_dyad),
    "PLUS": (np.conj, np.add),
    "PLUSDOT": (plusdot_monad, np.gcd),
    "PLUSCO": (plusco_monad, plusco_dyad),
    "STAR": (np.sign, np.multiply),
    "STARDOT": (stardot_monad, np.lcm),
    "STARCO": (np.square, starco_dyad),
    "PERCENT": (percent_monad, np.divide),
    "PERCENTCO": (np.sqrt, percentco_dyad),
    "HAT": (np.exp, np.power),
    "HATDOT": (np.log, hatdot_dyad),
    "DOLLAR": (dollar_monad, dollar_dyad),
    "LT": (lt_monad, cast_bool_to_int(np.less)),
    "LTDOT": (np.floor, np.minimum),
    "LTCO": (ltco_monad, cast_bool_to_int(np.less_equal)),
    "GT": (gt_monad, cast_bool_to_int(np.greater)),
    "GTDOT": (np.ceil, np.maximum),
    "GTCO": (gtco_monad, cast_bool_to_int(np.greater_equal)),
    "IDOT": (idot_monad, NotImplemented),
    "ICAPDOT": (icapdot_monad, NotImplemented),
    "TILDEDOT": (tildedot_monad, None),
    "TILDECO": (tildeco_monad, cast_bool_to_int(np.not_equal)),
    "COMMA": (comma_monad, comma_dyad),
    "COMMADOT": (commadot_monad, commadot_dyad),
    "COMMACO": (commaco_monad, commaco_dyad),
    "BAR": (np.abs, bar_dyad),
    "BARDOT": (np.flipud, bardot_dyad),
    "BARCO": (np.transpose, barco_dyad),
    "NUMBER": (number_monad, number_dyad),
    "NUMBERDOT": (numberdot_monad, numberdot_dyad),
    "NUMBERCO": (numberco_monad, NotImplemented),
    "SQUARELF": (squarelf_monad, squarelf_dyad),
    "SQUARERF": (squarerf_monad, squarerf_dyad),
    "SQUARERFCO": (squarerfco_monad, squarerfco_dyad),
    "SLASHCO": (slashco_monad, slashco_dyad),
    "BSLASHCO": (bslashco_monad, bslashco_dyad),
    "BANG": (bang_monad, bang_dyad),
    "CURLYLF": (NotImplemented, curlylf_dyad),
    "CURLYLFDOT": (curlylfdot_monad, curlylfdot_dyad),
    "CURLYRTDOT": (curlyrtdot_monad, curlyrtdot_dyad),
    "CURLYLFCO": (curlylfco_monad, None),
    "CURLYRTCO": (curlyrtco_monad, None),
    "SEMI": (semi_monad, semi_dyad),
    "SEMICO": (semico_monad, NotImplemented),
    "QUERY": (query_monad, query_dyad),
}
