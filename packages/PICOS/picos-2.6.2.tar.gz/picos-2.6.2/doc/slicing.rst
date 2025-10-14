.. _slicing:

Matrix Slicing
==============

Affine matrix expressions form the core of PICOS' modeling toolbox: All
:class:`constant <picos.Constant>` and :class:`variable
<picos.expressions.variables>` expressions that you enter, including integral
variables, and any linear combination of these objects, are stored as instances
of the multidimensional :class:`~picos.expressions.ComplexAffineExpression` or
its real subclass :class:`~picos.expressions.AffineExpression`. Their common
base class :class:`~picos.expressions.BiaffineExpression` implements plenty of
algebraic operations to combine and modify your initial expressions to yield the
desired statements. One of these operations is slicing, denoted by ``A[·]`` for
an affine expression ``A``.

.. rubric:: Preliminaries

Unlike in NumPy, all multidimensional expressions are strictly matrices. In
particular, there are no flat arrays but only row and column vectors, and any
scalar expression is also a :math:`1 \times 1` matrix. PICOS does not support
tensors or higher order expressions, but it does support the `Kronecker product
<https://en.wikipedia.org/wiki/Kronecker_product>`_ as well as :meth:`partial
trace <.exp_biaffine.BiaffineExpression.partial_trace>` and :meth:`partial
transposition <.exp_biaffine.BiaffineExpression.partial_transpose>` operations
to enable some of the optimization problems naturally defined on tensors. If you
enter data in the form of a flat array (e.g. a Python :class:`list` or a NumPy
:class:`~numpy:numpy.ndarray` with one axis), it will be read as a column
vector.

In PICOS, all indices start from zero.

.. rubric:: Slicing modes

PICOS has two modes for slicing: :ref:`arbitrary_access` and
:ref:`proper_slicing`.

Arbitrary Access lets you select individual elements from a vector or matrix
expression and put them in a column vector in the desired order.
:meth:`Transposition <.exp_biaffine.BiaffineExpression.T>`, :meth:`reshaping
<.exp_biaffine.BiaffineExpression.reshaped>` and :meth:`broadcasting
<.exp_biaffine.BiaffineExpression.broadcasted>` can then be used to put the
selection into the desired shape. Arbitrary Access has the form ``A[·]`` where
``·`` stands for an integer, a Python :class:`slice`, a flat collection of
integers such as a :class:`list`, or a dictionary storing sparse index pairs.

Proper Slicing refers to selecting certain rows and columns of a matrix, and
forming a new matrix where all elements that are not selected are removed.
It has the form ``A[·,·]`` where each ``·`` stands for an integer, a
:class:`slice`, or a flat collection of integers.

To demonstrate the different possibilities, we use a constant :math:`5 \times 5`
expression:

>>> from picos import Constant
>>> A = Constant("A", range(25), (5,5))
>>> A
<5×5 Real Constant: A>
>>> print(A)
[ 0.00e+00  5.00e+00  1.00e+01  1.50e+01  2.00e+01]
[ 1.00e+00  6.00e+00  1.10e+01  1.60e+01  2.10e+01]
[ 2.00e+00  7.00e+00  1.20e+01  1.70e+01  2.20e+01]
[ 3.00e+00  8.00e+00  1.30e+01  1.80e+01  2.30e+01]
[ 4.00e+00  9.00e+00  1.40e+01  1.90e+01  2.40e+01]

.. _arbitrary_access:

Arbitrary Access
----------------

.. rubric:: By integer

If a single integer or a single flat collection of integers is given, then these
indices refer to the column-major vectorization of the matrix, represented by
the order of the numbers in the demonstration matrix ``A``.

The most common case is selecting a single element via an integer index:

>>> A[0]  # Select the first element as a scalar expression.
<1×1 Real Constant: A[0]>
>>> print(A[0])  # Print its value.
0.0
>>> print(A[7])  # The value of the eighth element.
7.0
>>> # Negative indices are counted from the rear; -1 refers to the last element:
>>> print(A[-1])
24.0

.. rubric:: By slice

Python slices allow you to compactly specify a structured sequence of elements
to extract.
A Python slice has the form ``a:b`` or ``a:b:s`` with :math:`a` the inclusive
start index, :math:`b` the exclusive stop index and :math:`s` a step size.
Negative :math:`a` and :math:`b`, as in the integer index case, are counted from
the rear, while a negative step size reverses the order.
All of :math:`a`, :math:`b` and :math:`s` may be omitted. Then, the defaults are

.. math::

  s &= 1, \\
  a &= \begin{cases}
    0,~&\text{if}~s > 0, \\
    \text{len}(A) - 1,~&\text{if}~s < 0,
  \end{cases} \\
  b &= \begin{cases}
    \text{len}(A),~&\text{if}~s > 0, \\
    \textbf{None},~&\text{if}~s < 0.
  \end{cases}

Note the :obj:`None` in the statement above: When going backwards, this special
token is the only way to stop at the first element with index :math:`0` as
:math:`-1` refers to the last element. For example, the first two elements in
reverse order are selected via the slice ``1:None:-1`` or just ``1::-1``.

>>> A[:2]  # The first two elements as a column vector.
<2×1 Real Constant: A[:2]>
>>> print(A[:2])
[ 0.00e+00]
[ 1.00e+00]
>>> print(A[1::-1])  # The first two elements reversed (indices 1 and 0).
[ 1.00e+00]
[ 0.00e+00]
>>> print(A[-2:])  # The last two elements.
[ 2.30e+01]
[ 2.40e+01]
>>> print(A[2:7].T)  # The third to seventh element (transposed).
[ 2.00e+00  3.00e+00  4.00e+00  5.00e+00  6.00e+00]
>>> print(A[2:7:2].T)  # As before, but with a step size of 2.
[ 2.00e+00  4.00e+00  6.00e+00]

You could use this to vectorize :math:`A` in column-major order, but ``A.vec``
is both individually faster and has its result cached:

>>> A[:].equals(A.vec)
True
>>> A.vec is A.vec  # Cached.
True
>>> A[:] is A[:]  # Computed again as new expression.
False

.. rubric:: By integer sequence

By providing a :class:`list` or a similar vector of integers, you can select
arbitrary elements in any order, including duplicates:

>>> print(A[[0,1,0,1,-1]])
[ 0.00e+00]
[ 1.00e+00]
[ 0.00e+00]
[ 1.00e+00]
[ 2.40e+01]

Note that you cannot provide a :class:`tuple` instead of a list, as ``A[(·,·)]``
is understood by Python as ``A[·,·]`` (see :ref:`proper_slicing`).
Any other object that the function :func:`~picos.expressions.data.load_data`
with ``typecode="i"`` loads as an integer row or column vector works, including
integral NumPy arrays.

.. _sparse_index_dict:
.. rubric:: By sparse index pair dictionary

If you provide a dictionary with exactly two keys that can be compared via
``<`` and whose values are integer sequences of same length (anything recognized
by :func:`~picos.expressions.data.load_data` as an integer vector), PICOS
interprets the sequence corresponding to the smaller key as row indices and the
sequence corresponding to the greater key as the corresponding column indices:

>>> print(A[{"x": range(3), "y": [1]*3}])  # Select (0,1), (1,1) and (2,1).
[ 5.00e+00]
[ 6.00e+00]
[ 7.00e+00]
>>> print(A[{"y": range(3), "x": [1]*3}])  # Transposed selection, as "x" < "y".
[ 1.00e+00]
[ 6.00e+00]
[ 1.10e+01]

You could use this to extract the main diagonal of :math:`A`, but ``A.maindiag``
is both individually faster and has its result cached:

>>> indices = dict(enumerate([range(min(A.shape))]*2))
>>> indices
{0: range(0, 5), 1: range(0, 5)}
>>> A[indices].equals(A.maindiag)
True
>>> A.maindiag is A.maindiag  # Cached.
True
>>> A[indices] is A[indices]  # Computed again as new expression.
False

.. _proper_slicing:

Proper Slicing
--------------

If you provide not one but two integers, slices, or integer sequences separated
by a comma or given as a :obj:`tuple`, then they are understood as row and
column indices, respectively.
Unlike when providing a sparse index pair by dictionary, these indices select
*entire* rows and columns and PICOS returns the matrix of all elements that are
selected twice (both by row and by column):

>>> print(A[1,2])  # The single element at (1,2) (second row, third column).
11.0
>>> print(A[0,:])  # The first row of the matrix.
[ 0.00e+00  5.00e+00  1.00e+01  1.50e+01  2.00e+01]
>>> print(A[range(3),-1])  # The first three elements of the last column.
[ 2.00e+01]
[ 2.10e+01]
[ 2.20e+01]
>>> print(A[[0,1],[0,1]])  # The first second-order principal submatrix.
[ 0.00e+00  5.00e+00]
[ 1.00e+00  6.00e+00]
>>> print(A[1:-1,1:-1])  # Cut away the outermost pixels of an image.
[ 6.00e+00  1.10e+01  1.60e+01]
[ 7.00e+00  1.20e+01  1.70e+01]
[ 8.00e+00  1.30e+01  1.80e+01]
>>> print(A[::2,::2])  # Sample every second element.
[ 0.00e+00  1.00e+01  2.00e+01]
[ 2.00e+00  1.20e+01  2.20e+01]
[ 4.00e+00  1.40e+01  2.40e+01]

You can even select the entire matrix to effectively create a copy of it, though
this is discouraged as expressions are supposed to be immutable so that reusing
an expression in multiple places is always safe.

>>> A[:,:].equals(A)
True
>>> A[:,:] is A
False

We refer to this as proper slicing because you cut out the rows that you want,
throwing away the rest, then cut the desired columns out from the remainder.
It's like cutting a square cake except that you can also duplicate the pieces!

.. note::
  In NumPy, ``A[[0,1],[0,1]]`` would create a flat array with the elements
  ``A[0,0]`` and ``A[1,1]`` while PICOS creates a submatrix from the first two
  rows and columns as in the example above. If you want to mirror NumPy's
  behavior in PICOS, see :ref:`sparse_index_dict`.
