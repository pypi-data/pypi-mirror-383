#!/usr/bin/env python3

"""Simplify a morphological code using the common subexpression elimination."""

import itertools
import numbers
import typing

from morphomath.kernel import Kernel

TYPE_VAR = tuple[str, tuple[int, ...]]
TYPE_CODE = list[tuple[TYPE_VAR, list[TYPE_VAR]]]


def create_naive_code(kernel: Kernel, shape: tuple[int, ...], borders: bool=False) -> TYPE_CODE:
    """Generate the full naive code of the morphological operation in the full image.

    Parameters
    ----------
    kernel : Kernel
        The structurant element, including the anchor.
    shape : tuple[int, ...]
        The final image shape.
    borders : boolean, default=False
        If False, it include the edges effect with a similar beavour as
        cv2.BORDER_REPLICATE, using the nilpotence of the morphological law.
        Overwise, it consider than the src indices are allway valid,
        even if they are out of the shape boundaries.

    Returns
    -------
    code : TYPE_CODE
        The naive source code.

    Examples
    --------
    >>> import pprint
    >>> from morphomath.cse import create_naive_code
    >>> from morphomath.kernel import Kernel
    >>> pprint.pprint(create_naive_code(Kernel([[1, 1], [0, 1]]), (3, 3), borders=True))
    [(('dst', (0, 0)), [('src', (0, 0)), ('src', (0, 1)), ('src', (1, 1))]),
     (('dst', (0, 1)), [('src', (0, 1)), ('src', (0, 2)), ('src', (1, 2))]),
     (('dst', (0, 2)), [('src', (0, 2)), ('src', (1, 2))]),
     (('dst', (1, 0)), [('src', (1, 0)), ('src', (1, 1)), ('src', (2, 1))]),
     (('dst', (1, 1)), [('src', (1, 1)), ('src', (1, 2)), ('src', (2, 2))]),
     (('dst', (1, 2)), [('src', (1, 2)), ('src', (2, 2))]),
     (('dst', (2, 0)), [('src', (2, 0)), ('src', (2, 1))]),
     (('dst', (2, 1)), [('src', (2, 1)), ('src', (2, 2))]),
     (('dst', (2, 2)), [('src', (2, 2))])]
    >>>
    """
    # verifications
    assert isinstance(kernel, Kernel), kernel.__class__.__name__
    assert isinstance(shape, tuple), shape.__class__.__name__
    assert len(shape) == kernel.ndim, (
        f"the provided kernel is {kernel.ndim} dimensional "
        f"but the shape is {len(shape)} dimentional"
    )
    assert all(isinstance(s, int) and s > 0 for s in shape), shape
    assert isinstance(borders, bool), borders.__class__.__name__

    # creation
    code: TYPE_CODE = []
    for coord in itertools.product(*(range(s) for s in shape)):
        dst = ("dst", coord)
        shift = tuple(c - a for c, a in zip(coord, kernel.anchor))  # coord - kernel.anchor
        if borders:
            src = sorted({  # in favor of c contiguous memory jump
                (
                    "src",
                    tuple(
                        max(0, min(si-1, pi + ai))  # min and max for border effect
                        for pi, ai, si in zip(p, shift, shape)
                    )
                )
                for p in kernel.points
            })
        else:
            src = sorted({  # in favor of c contiguous memory jump
                ("src", tuple(pi + ai for pi, ai in zip(p, shift)))
                for p in kernel.points
            })
        code.append((dst, src))

    return code


def cse(code: TYPE_CODE) -> TYPE_CODE:
    """Perfom common subexpression elimination on the code.

    Parameters
    ----------
    code : TYPE_CODE
        The naive source code.
        It can comes from :py:func:`create_naive_code`.

    Returns
    -------
    compact_code : TYPE_CODE
        A factorized version of the source code.

    Examples
    --------
    >>> import pprint
    >>> from morphomath.cse import cse
    >>> code = [(('dst', (0, 0)), [('src', (0, 0)), ('src', (0, 1)), ('src', (1, 1))]),
    ...         (('dst', (0, 1)), [('src', (0, 1)), ('src', (0, 2)), ('src', (1, 2))]),
    ...         (('dst', (0, 2)), [('src', (0, 2)), ('src', (1, 2))]),
    ...         (('dst', (1, 0)), [('src', (1, 0)), ('src', (1, 1)), ('src', (2, 1))]),
    ...         (('dst', (1, 1)), [('src', (1, 1)), ('src', (1, 2)), ('src', (2, 2))]),
    ...         (('dst', (1, 2)), [('src', (1, 2)), ('src', (2, 2))]),
    ...         (('dst', (2, 0)), [('src', (2, 0)), ('src', (2, 1))]),
    ...         (('dst', (2, 1)), [('src', (2, 1)), ('src', (2, 2))]),
    ...         (('dst', (2, 2)), [('src', (2, 2))])]
    >>> pprint.pprint(cse(code))
    [(('dst', (0, 0)), [('src', (0, 0)), ('src', (0, 1)), ('src', (1, 1))]),
     (('buff', (1,)), [('src', (0, 2)), ('src', (1, 2))]),
     (('dst', (0, 1)), [('buff', (1,)), ('src', (0, 1))]),
     (('dst', (0, 2)), [('buff', (1,))]),
     (('dst', (1, 0)), [('src', (1, 0)), ('src', (1, 1)), ('src', (2, 1))]),
     (('buff', (0,)), [('src', (1, 2)), ('src', (2, 2))]),
     (('dst', (1, 1)), [('buff', (0,)), ('src', (1, 1))]),
     (('dst', (1, 2)), [('buff', (0,))]),
     (('dst', (2, 0)), [('src', (2, 0)), ('src', (2, 1))]),
     (('dst', (2, 1)), [('src', (2, 1)), ('src', (2, 2))]),
     (('dst', (2, 2)), [('src', (2, 2))])]
    >>>
    """
    # verification
    assert isinstance(code, list), code.__class__.__name__
    assert all(isinstance(l, tuple) and len(l) == 2 for l in code), code

    # initialisation
    code: list[tuple[TYPE_VAR, set[TYPE_VAR]]] = [
        (alloc, set(comp)) for alloc, comp in code
    ]
    subexprs: dict[tuple[int, int], set[tuple[int, ...]]] = {  # all common subexpressions
        (i, j): code[i][1] & code[j][1]
        for i, j in itertools.combinations(range(len(code)), 2)
    }
    buff_counter: int = 0

    # iterative simplification
    while subexprs := {lines: s for lines, s in subexprs.items() if len(s) >= 2}:

        # select one subgroup with an heuristic that try to minimize the number of comparisons
        # and the memory distance to reduce the cache jump size, in a c contiguous array
        (l_i, l_j), subexpr = max(subexprs.items(), key=lambda ijs: (len(ijs[1]), ijs[0]))
        # replace the sub comparisons in the code
        var = ("buff", (buff_counter,))
        buff_counter += 1
        code[l_i] = (code[l_i][0], (code[l_i][1]-subexpr)|{var})
        code[l_j] = (code[l_j][0], (code[l_j][1]-subexpr)|{var})
        code.insert(l_i, (var, subexpr))  # this position to limmit memory jump

        # remove the no longer valid subexprs
        del subexprs[(l_i, l_j)]
        subexprs = {
            (i, j): s-subexpr if i in {l_i, l_j} or j in {l_i, l_j} else s
            for (i, j), s in subexprs.items()
        }
        # update the subexpr line number to fit the new code
        subexprs = {(i+int(i>=l_i), j+int(j>=l_i)): s for (i, j), s in subexprs.items()}
        # compute new subexprs
        subexprs |= {
            (min(l_i, j), max(l_i, j)): code[l_i][1] & code[j][1]
            for j in range(len(code)) if l_i != j
        }

    code = [(alloc, sorted(comp)) for alloc, comp in code]  # in favor of c contiguous
    return code


def limit_buff(code: TYPE_CODE) -> TYPE_CODE:
    """Reduce the len of the buffer.

    Parameters
    ----------
    code : TYPE_CODE
        The factorized source code with  a non reduced buffer.
        It can comes from :py:func:`cse`.

    Returns
    -------
    compact_code : TYPE_CODE
        A version of the source code with the minimal buffer size.

    Examples
    --------
    >>> import pprint
    >>> from morphomath.cse import limit_buff
    >>> code = [(('dst', (0, 0)), [('src', (0, 0)), ('src', (0, 1)), ('src', (1, 1))]),
    ...         (('buff', (1,)), [('src', (0, 2)), ('src', (1, 2))]),
    ...         (('dst', (0, 1)), [('buff', (1,)), ('src', (0, 1))]),
    ...         (('dst', (0, 2)), [('buff', (1,))]),
    ...         (('dst', (1, 0)), [('src', (1, 0)), ('src', (1, 1)), ('src', (2, 1))]),
    ...         (('buff', (0,)), [('src', (1, 2)), ('src', (2, 2))]),
    ...         (('dst', (1, 1)), [('buff', (0,)), ('src', (1, 1))]),
    ...         (('dst', (1, 2)), [('buff', (0,))]),
    ...         (('dst', (2, 0)), [('src', (2, 0)), ('src', (2, 1))]),
    ...         (('dst', (2, 1)), [('src', (2, 1)), ('src', (2, 2))]),
    ...         (('dst', (2, 2)), [('src', (2, 2))])]
    >>> pprint.pprint(limit_buff(code))
    [(('dst', (0, 0)), [('src', (0, 0)), ('src', (0, 1)), ('src', (1, 1))]),
     (('buff', (0,)), [('src', (0, 2)), ('src', (1, 2))]),
     (('dst', (0, 1)), [('buff', (0,)), ('src', (0, 1))]),
     (('dst', (0, 2)), [('buff', (0,))]),
     (('dst', (1, 0)), [('src', (1, 0)), ('src', (1, 1)), ('src', (2, 1))]),
     (('buff', (0,)), [('src', (1, 2)), ('src', (2, 2))]),
     (('dst', (1, 1)), [('buff', (0,)), ('src', (1, 1))]),
     (('dst', (1, 2)), [('buff', (0,))]),
     (('dst', (2, 0)), [('src', (2, 0)), ('src', (2, 1))]),
     (('dst', (2, 1)), [('src', (2, 1)), ('src', (2, 2))]),
     (('dst', (2, 2)), [('src', (2, 2))])]
    >>>
    """
    # verification
    assert isinstance(code, list), code.__class__.__name__
    assert all(isinstance(l, tuple) and len(l) == 2 for l in code), code

    # searches for positions where variables are used for the last
    released: dict[int, int] = {}  # to each buff idx, associate the line of last used
    for i, ((alloc_symb, alloc_idx), comp) in enumerate(reversed(code)):
        for comp_symb, comp_idx in comp:
            if comp_symb == "buff":
                (idx,) = comp_idx
                released[idx] = released.get(idx, len(code)-i-1)

    # reverse the released var order
    inv_released: dict[int, list[int]] = {}  # line -> indices
    for idx, line in released.items():
        inv_released[line] = inv_released.get(line, [])
        inv_released[line].append(idx)

    # find the replacement table
    subs: dict[int, int] = {}  # correspondance table: old_idx -> new_idx
    used: set(int) = set()  # buffer indices currently used
    for line, ((alloc_symb, alloc_idx), _) in enumerate(code):
        if alloc_symb == "buff":
            (idx,) = alloc_idx
            if idx not in subs:  # if it is the first time we meet the indice
                free = min(set(range(len(used)+1))-used)  # the smallest free index
                subs[idx] = free
                used.add(free)
        for idx in inv_released.get(line, []):  # last appearance of the variable
            used.remove(subs[idx])  # we make it available for the suite

    # replace the indices
    code = [
        (
            (a_s, a_i if a_s != "buff" else (subs[a_i[0]],)),
            [(s, idx if s != "buff" else (subs[idx[0]],)) for s, idx in comp],
        )
        for (a_s, a_i), comp in code
    ]

    return code
