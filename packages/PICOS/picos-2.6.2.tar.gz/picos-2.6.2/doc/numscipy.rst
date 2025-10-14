.. _numscipy:

NumPy and SciPy
===============

As a lightweight computer algebra system, PICOS sits one level above numerics
libraries such as NumPy and SciPy and acts in concert with them. Let's define a
variable and some data:

>>> import picos, numpy, scipy.sparse
>>> x = picos.RealVariable("x", 4)
>>> N = numpy.reshape(range(16), (4, 4))
>>> type(N)
<class 'numpy.ndarray'>
>>> S = scipy.sparse.spdiags(range(4), 0, 4, 4)
>>> type(S)
<class 'scipy.sparse._dia.dia_matrix'>

.. rubric:: Taking input from NumPy or SciPy

PICOS also allows loading of NumPy and SciPy data on the fly, with one caveat to
watch out for:

>>> x.T*N
<1×4 Real Linear Expression: xᵀ·[4×4]>
>>> N*x
<4×1 Real Linear Expression: [4×4]·x>
>>> x.T*S
<1×4 Real Linear Expression: xᵀ·[4×4]>
>>> S*x
Traceback (most recent call last):
    [...]
picos.valuable.NotValued: Mutable x is not valued.

The last command fails as SciPy sparse matrices `do not currently respect the
__array_priority__ attribute <https://github.com/scipy/scipy/issues/4819>`__, so
that SciPy tries to load ``x`` as an array as opposed to conceding the operation
to PICOS like NumPy does. You can fix this behavior as follows:

>>> picos.patch_scipy_array_priority()
>>> S*x
<4×1 Real Linear Expression: [4×4]·x>

Note that this `monkey-patches <https://en.wikipedia.org/wiki/Monkey_patch>`__
SciPy, so that applications importing your code calling
:func:`~picos.valuable.patch_scipy_array_priority` will also see a patched
version of SciPy.

.. rubric:: Returning NumPy or SciPy data as output

PICOS uses CVXOPT as a numerics backend and thus outputs numeric values as
CVXOPT (sparse) matrices or Python scalar types by default:

>>> x.value = range(4)
>>> x.value
<4x1 matrix, tc='d'>
>>> type(x.value)
<class 'cvxopt.base.matrix'>

However, all objects that can be valued, in particular expressions and problem
instances, also offer properties to query that value as a NumPy type, namely
:attr:`~picos.valuable.Valuable.np` and :attr:`~picos.valuable.Valuable.np2d`:

>>> x.np  # Returns a NumPy scalar, 1D, or 2D array.
array([0., 1., 2., 3.])
>>> type(x.np)
<class 'numpy.ndarray'>
>>> x.np.shape
(4,)
>>> x.np2d  # Always returns a 2D array.
array([[0.],
       [1.],
       [2.],
       [3.]])
>>> x.np2d.shape
(4, 1)

For SciPy, the :attr:`~picos.valuable.Valuable.sp` property returns a sparse
matrix whenever the data stored by PICOS internally is sparse and a NumPy 2D
array otherwise:

>>> I = picos.I(3)
>>> print(I)
[ 1.00e+00     0         0    ]
[    0      1.00e+00     0    ]
[    0         0      1.00e+00]
>>> type(I.sp)
<class 'scipy.sparse._csc.csc_matrix'>
>>> J = picos.J(3, 3)
>>> print(J)
[ 1.00e+00  1.00e+00  1.00e+00]
[ 1.00e+00  1.00e+00  1.00e+00]
[ 1.00e+00  1.00e+00  1.00e+00]
>>> type(J.sp)
<class 'numpy.ndarray'>

A full list of methods for returning values in different formats can be found in
the documentation of the :class:`~picos.valuable.Valuable` base class.