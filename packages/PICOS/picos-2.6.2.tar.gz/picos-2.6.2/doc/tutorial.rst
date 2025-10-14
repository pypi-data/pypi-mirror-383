.. TODO: Once #161 is resolved, document how to assess the solution status.
.. TODO: Bring back the commented-out section on writing to file once it works.


.. _tutorial:

Tutorial
========

First of all, let us import PICOS:

>>> import picos


.. rubric:: Output settings

PICOS makes heavy use of unicode symbols to generate pretty output.
If you find that some of these symbols are not available on your terminal, you
can call :func:`~picos.ascii` or :func:`~picos.latin1` to restrict the charset
used:

>>> X = picos.SymmetricVariable("X", 4)       # Create a dummy variable.
>>> print(X >> 0)                             # Default representation of X ≽ 0.
X ≽ 0
>>> picos.latin1()                            # Limit to ISO 8859-1 (Latin-1).
>>> print(X >> 0)
X » 0
>>> picos.ascii()                             # Limit to pure ASCII.
>>> print(X >> 0)
X >> 0

For the sake of this tutorial, we return to the full beauty of unicode:

>>> picos.default_charset()  # The same as picos.unicode().


Variables
---------

Every optimization endeavor starts with variables. As of PICOS 2.0, the
preferred way to create variables is to create an instance of the desired
variable class:

>>> from picos import RealVariable, BinaryVariable
>>> t = RealVariable("t")                     # A scalar.
>>> x = RealVariable("x", 4)                  # A column vector with 4 elements.
>>> Y = RealVariable("Y", (2, 4))             # A 2×4 matrix.
>>> Z = RealVariable("Z", (4, 2))             # A 4×2 matrix.
>>> w = BinaryVariable("w")                   # A binary scalar.

Now, let's inspect these variables:

>>> w
<1×1 Binary Variable: w>
>>> Y
<2×4 Real Variable: Y>
>>> x.shape
(4, 1)
>>> Z.name
'Z'


.. rubric:: Assigning a value

Assigning values to variables is usually the solver's job, but we can do it
manually:

>>> t.value = 2
>>> # In the case of a binary variable, we can only assign a (near) 0 or 1:
>>> w.value = 0.5  # doctest: +NORMALIZE_WHITESPACE
Traceback (most recent call last):
  ...
ValueError: Failed to assign a value to mutable w: Data is not near-binary with
    absolute tolerance 1.0e-04: Largest difference is 5.0e-01.
>>> print(Z)
Z
>>> Z.value = range(8)
>>> print(Z)  # If a variable is valued, prints the value instead.
[ 0.00e+00  4.00e+00]
[ 1.00e+00  5.00e+00]
[ 2.00e+00  6.00e+00]
[ 3.00e+00  7.00e+00]

As you can see from the last example, PICOS uses column-major order when
loading one-dimensional data such as a Python :class:`range` into a matrix.
The documentation of :func:`~picos.expressions.data.load_data` explains PICOS'
data loading concept in greater detail.


Affine expressions
------------------

The fundamental building blocks of optimization models are affine (matrix)
expressions. Each entry of such an expression is simply a linear combination of
any number of scalar variables plus a constant offset. The variable objects that
we have defined above are special cases of affine expression that refer to
themselves via an identity transformation.

We can now use our variables to create more advanced affine expressions, which
are stored as instances of :class:`~picos.expressions.ComplexAffineExpression`
or of its subclass :class:`~picos.expressions.AffineExpression`. For instance,
we may transpose a matrix variable using the suffix ``.T``:

>>> Y
<2×4 Real Variable: Y>
>>> Y.T
<4×2 Real Linear Expression: Yᵀ>

PICOS expression types overload the standard Python math operators so that you
can denote, for instance, the sum of two expressions as follows:

>>> Z + Y.T
<4×2 Real Linear Expression: Z + Yᵀ>

The overloaded operators will convert arbitrary data on the fly:

>>> t + 1
<1×1 Real Affine Expression: t + 1>
>>> x + 1  # The 1 is broadcasted to a 4×1 vector of all ones.
<4×1 Real Affine Expression: x + [1]>


.. rubric:: Constants

Constants are simply affine expressions with no linear part and are more
commonly referred to as *data*. By default, PICOS uses a short dummy string to
represent multidimensional constants, and reshapes them as needed:

>>> Y + [1, -2, 3, -4, 5, -6, 7, 8]           # Load list as a 2×4 matrix.
<2×4 Real Affine Expression: Y + [2×4]>

If you want to give your constant data a meaningful name and fix its shape for
more type safety, you can do this using :func:`~picos.expressions.Constant`:

>>> from picos import Constant
>>> alpha = Constant("α", 23)                 # Load 23 under the name α.
>>> b = Constant("b", range(4))               # Load as a column vector.
>>> C = Constant("C", [1, -2, 3, -4, 5, -6, 7, 8], (2, 4)); C
<2×4 Real Constant: C>
>>> Y + C
<2×4 Real Affine Expression: Y + C>

The data loading semantics of :func:`~picos.expressions.Constant` or when
loading data on the fly are the same as when valuing variables
(:func:`~picos.expressions.data.load_data`). In particular, you can seamlessly
input CVXOPT or NumPy matrices:

>>> import numpy
>>> Y + numpy.array([[1, 2, 3, 4], [5, 6, 7, 8]])
<2×4 Real Affine Expression: Y + [2×4]>


.. _overloads:

Overloaded operators
--------------------

Now that we have some variables (:math:`t`, :math:`x`, :math:`w`, :math:`Y` and
:math:`Z`) and a couple of constant parameters (:math:`\alpha`, :math:`b`,
:math:`C`), let us create some more affine expressions with them:

>>> C.shape, Z.shape                          # Recall the shapes.
((2, 4), (4, 2))
>>> C*Z                                       # Left multiplication.
<2×2 Real Linear Expression: C·Z>
>>> Z*C                                       # Right multiplication.
<4×4 Real Linear Expression: Z·C>
>>> C*Z*C                                     # Left and right multiplication.
<2×4 Real Linear Expression: C·Z·C>
>>> alpha*Y                                   # Scalar multiplication.
<2×4 Real Linear Expression: α·Y>
>>> t/alpha - alpha/2                         # Division and subtraction.
<1×1 Real Affine Expression: t/α - α/2>
>>> (b | x)                                   # Dot product.
<1×1 Real Linear Expression: ⟨b, x⟩>
>>> # Generalized dot product for matrices: ⟨A, B⟩ = tr(Aᴴ·B):
>>> (C | Y)
<1×1 Real Linear Expression: ⟨C, Y⟩>
>>> b^x                                       # Hadamard (element-wise) product.
<4×1 Real Linear Expression: b⊙x>
>>> C@Z                                       # Kronecker product.
<8×8 Real Linear Expression: C⊗Z>


.. rubric:: Slicing

Python slicing notation can be used to extract single elements or submatrices:

>>> Y[0, 1]                                   # Element in 1st row, 2nd column.
<1×1 Real Linear Expression: Y[0,1]>
>>> x[1:3]                                    # 2nd and 3rd element of x.
<2×1 Real Linear Expression: x[1:3]>
>>> x[-1]                                     # Last element of x.
<1×1 Real Linear Expression: x[-1]>
>>> Y[1,:]                                    # 2nd row of Y.
<1×4 Real Linear Expression: Y[1,:]>
>>> C[:, 1:3]*Y[:, -2::-2]                    # Extended slicing with step size.
<2×2 Real Linear Expression: C[:,1:3]·Y[:,-2::-2]>

In the last example, we select only the second and third column of :math:`C` as
well as the columns of :math:`Y` with an even index considered in reverse order.
The full power and notation of slicing is explained in :ref:`slicing`.


.. rubric:: Concatenation

We can also create larger affine expressions by concatenating them vertically
with ``&`` or horizontally with ``//``:

>>> (b & 2*b & x & C.T*C*x) // x.T
<5×4 Real Affine Expression: [b, 2·b, x, Cᵀ·C·x; xᵀ]>

You have to be a little careful when it comes to operator precedence, because
Python has the binding strength of ``&`` and ``//`` built into its grammar with
logical disjunction and integral division in mind. When in doubt, use
parenthesis around your blocks.


.. rubric:: Broadcasting and reshaping

To recall an example we've seen earlier with variables, scalars are broadcasted
to the necessary shape to allow an addition or subtraction to take place:

>>> 5*x - alpha
<4×1 Real Affine Expression: 5·x - [α]>

Note, however, that apart from this simple broadcasting rule, the shape of a
PICOS constant (loaded via :func:`~picos.Constant`) is already fixed. You can't
add a :math:`8 \times 1` vector to a :math:`4 \times 2` matrix:

>>> Z + (x // b)  # doctest: +NORMALIZE_WHITESPACE
Traceback (most recent call last):
  ...
TypeError: Invalid operation BiaffineExpression.__add__(Z, [x; b]):
    The operand shapes of 4×2 and 8×1 do not match.

The reason is simply that PICOS does not know *which* side to reshape. You can
make the example work by being more explicit:

>>> Z + (x // b).reshaped((4, 2))
<4×2 Real Affine Expression: Z + reshaped([x; b], 4×2)>


.. rubric:: Summing multiple expressions

Since affine expressions overload ``+``, you could use Python's :func:`sum` to
add a bunch of them. However, the string representation can become rather long:

>>> # Create a sequence of matrix constants with sensible names:
>>> A = [Constant("A[{}]".format(i), range(i, i + 8), (2, 4)) for i in range(5)]
>>> A[0]
<2×4 Real Constant: A[0]>
>>> sum([A[i]*Z for i in range(5)])
<2×2 Real Linear Expression: A[0]·Z + A[1]·Z + A[2]·Z + A[3]·Z + A[4]·Z>

To obtain a shorter representation, use :func:`picos.sum` instead:

>>> picos.sum([A[i]*Z for i in range(5)])
<2×2 Real Linear Expression: ∑(A[i]·Z : i ∈ [0…4])>

This works for all kinds of expressions and will look hard to find some pattern
in the summands' string descriptions.


Norms and quadratics
--------------------

.. rubric:: Norms

The norm of an affine expression can be expressed using Python's built-in
:func:`abs` function. If :math:`x` is an affine vector, ``abs(x)`` denotes its
Euclidean norm :math:`\sqrt{x^T x}`:

>>> abs(x)
<Euclidean Norm: ‖x‖>

If the affine expression is a matrix, :func:`abs` returns its Frobenius norm
:math:`\Vert M \Vert_F = \sqrt{\operatorname{trace} (M^T M)}`:

>>> abs(Z - 2*C.T)
<Frobenius Norm: ‖Z - 2·Cᵀ‖>

The absolute value of a scalar is expressed in the same way:

>>> abs(t)
<Absolute Value: |t|>

As is the modulus of a complex expression:

>>> t + 1j
<1×1 Complex Affine Expression: t + 1j>
>>> abs(t + 1j)
<Complex Modulus: |t + 1j|>

Additional norms are available through the :class:`~picos.Norm` class.

.. rubric:: Quadratics

Quadratic expressions can be formed in several ways:

>>> abs(x)**2                                 # Squared norm.
<Squared Norm: ‖x‖²>
>>> t**2 - x[1]*x[2] + 2*t - alpha            # Sum involving quadratic terms.
<Quadratic Expression: t² - x[1]·x[2] + 2·t - α>
>>> (x[1] - 2) * (t + 4)                      # Product of affine expressions.
<Quadratic Expression: (x[1] - 2)·(t + 4)>
>>> Y[0,:]*x                                  # Row vector times column vector.
<Quadratic Expression: Y[0,:]·x>
>>> (x + 2 | Z[:,1])                          # Scalar product.
<Quadratic Expression: ⟨x + [2], Z[:,1]⟩>
>>> (t & alpha) * C * x                       # Quadratic form.
<Quadratic Expression: [t, α]·C·x>

Note that there is no natural way to define a vector or matrix of quadratic
expressions. In PICOS, only affine expressions can be multidimensional.


Defining a problem
------------------

Now that we know how to construct affine and quadratic expressions and norms, it
is time to use them as part of an optimization problem:

>>> from picos import Problem
>>> P = Problem()
>>> P.set_objective("min", (t - 5)**2 + 2)
>>> print(P)
Quadratic Program
  minimize (t - 5)² + 2
  over
    1×1 real variable t

Next we'll search a solution for this problem, but first we configure that only
the solver `CVXOPT <https://cvxopt.org/>`_ may be used so that the documentation
examples are reproducible. We can do this by assigning to the problem's
:attr:`~.problem.Problem.options` attribute:

>>> P.options.solver = "cvxopt"

We can now obtain a solution by calling :meth:`~.problem.Problem.solve`:

>>> solution = P.solve()
>>> solution
<feasible primal solution (claimed optimal) from cvxopt>
>>> solution.primals# doctest: +SKIP
{<1×1 Real Variable: t>: [4.999997568104307]}

Unless disabled by passing ``apply_solution=False`` to
:meth:`~.problem.Problem.solve`, the solution is automatically applied to the
variables involved in the problem definition, so that the entire Problem is now
valued:

>>> round(t, 5)
5.0
>>> round(P, 5)
2.0

The Python functions :func:`round`, :class:`int`, :class:`float` and
:class:`complex` are automatically applied to the ``value`` attribute of
variables, expressions and problems.


Setting options
---------------


We've already seen the ``solver`` option used which allows you to take control
over which of the available solvers should be used. You can display all
available options and their default values by printing the
:attr:`~.problem.Problem.options` instance (we've cut some from the output):

>>> print(P.options)# doctest: +ELLIPSIS
Modified solver options:
  solver              = cvxopt (default: None)
<BLANKLINE>
Default solver options:
  ...
  apply_solution      = True
  ...
  verbosity           = 0
  ...

If you want to change an option only for a single solution attempt, you can also
pass it to :meth:`~.problem.Problem.solve` as a keyword argument:

>>> # Solve again but don't apply the result.
>>> solution = P.solve(apply_solution=False)


Constraints
-----------

Constrained optimization is only half the fun without the constraints. PICOS
again provides overloaded operators to define them:

>>> t <= 5
<1×1 Affine Constraint: t ≤ 5>
>>> x[0] == x[-1]
<1×1 Affine Constraint: x[0] = x[-1]>
>>> abs(x)**2 <= t
<Squared Norm Constraint: ‖x‖² ≤ t>
>>> abs(x)**2 >= t
<Nonconvex Quadratic Constraint: ‖x‖² ≥ t>

Unless there are solvers or reformulation strategies that can deal with a
certain nonconvex constraint type, as is the case for the
:math:`\lVert x \rVert^2 \geq t` constranint above, PICOS will raise a
:exc:`TypeError` to let you know that such a constraint is not supported:

>>> abs(x) <= t
<5×1 SOC Constraint: ‖x‖ ≤ t>
>>> abs(x) >= t
Traceback (most recent call last):
  ...
TypeError: Cannot lower-bound a nonconcave norm.

When working with multidimensional affine expressions, the inequality operators
``>=`` and ``<=`` are understood element-wise (or to put it more mathy, they
represent conic inequality with respect to the nonnegative orthant):

>>> Y >= C
<2×4 Affine Constraint: Y ≥ C>

It is possible to define linear matrix inequalities for use in semidefinite
programming with the operators ``>>`` and ``<<`` denoting the Loewner order:

>>> from picos import SymmetricVariable
>>> S = SymmetricVariable("S", 4)
>>> S >> C.T*C
<4×4 LMI Constraint: S ≽ Cᵀ·C>

Other conic inequalities do not have a Python operator of their own, but you can
denote set membership of an affine expression in a cone. To make this possible,
the operator ``<<`` is also overloaded to denote "is element of":

>>> abs(x) <= t            # Recall that this is a second order cone inequality.
<5×1 SOC Constraint: ‖x‖ ≤ t>
>>> t // x << picos.soc()  # We can also write it like this.
<5×1 SOC Constraint: ‖[t; x][1:]‖ ≤ [t; x][0]>

Here :func:`~picos.soc` is a shorthand for :class:`~picos.SecondOrderCone`,
defined as the convex set

.. math::

    \mathcal{Q}^n = \left\{
        x \in \mathbb{R}^n
    ~\middle|~
        x_1 \geq \sqrt{\sum_{i = 2}^n x_i^2}
    \right\}.

Similarly, we can constrain an expression to be in the rotated second order cone

.. math::

    \mathcal{R}_p^n = \left\{
        x \in \mathbb{R}^n
    ~\middle|~
        p x_1 x_2 \geq \sum_{i = 2}^n x_i^2 \land x_1, x_2 \geq 0
    \right\}

parameterized by :math:`p`:

>>> picos.rsoc(p=1) >> x
<4×1 RSOC Constraint: ‖x[2:]‖² ≤ x[0]·x[1] ∧ x[0], x[1] ≥ 0>

Other sets you can use like this include :class:`~picos.Ball`,
:class:`~picos.Simplex` and the :class:`~picos.ExponentialCone`.


Constrained optimization
------------------------

Let's get back to our quadratic program :math:`P`, which we have already solved
to optimality with :math:`t = 5`:

>>> print(P)
Quadratic Program
  minimize (t - 5)² + 2
  over
    1×1 real variable t


.. rubric:: Adding constraints

We can now add the constraints that :math:`t` must be the sum over all elements
of :math:`x` and that every element of :math:`x` may be at most :math:`1`:

>>> Csum = P.add_constraint(t == x.sum)
>>> Cone = P.add_constraint(x <= 1)
>>> print(P)
Quadratic Program
  minimize (t - 5)² + 2
  over
    1×1 real variable t
    4×1 real variable x
  subject to
    t = ∑(x)
    x ≤ [1]

Now let's solve the problem again and see what we get:

>>> P.solve()
<primal feasible solution pair (claimed optimal) from cvxopt>
>>> round(P, 5)
3.0
>>> round(t, 5)
4.0
>>> x.value
<4x1 matrix, tc='d'>
>>> print(x.value)
[ 1.00e+00]
[ 1.00e+00]
[ 1.00e+00]
[ 1.00e+00]
<BLANKLINE>

Note that multidimensional values such as that of :math:`x` are returned as
`CVXOPT matrix types <https://cvxopt.org/userguide/matrices.html>`_.


.. rubric:: Slack and duals

Since our problem has constraints, we now have slack values and a dual solution
as well:

>>> Csum.slack# doctest: +SKIP
-0.0
>>> Csum.dual# doctest: +SKIP
2.000004393989704
>>> print(Cone.slack)# doctest: +SKIP
[ 9.31e-12]
[ 9.31e-12]
[ 9.31e-12]
[ 9.31e-12]
<BLANKLINE>
>>> print(Cone.dual)# doctest: +SKIP
[ 2.00e+00]
[ 2.00e+00]
[ 2.00e+00]
[ 2.00e+00]
<BLANKLINE>

We did not round the values this time, to showcase that solvers don't always
produce exact solutions even if the problem is "easy". The variable :math:`t` is
also not exactly :math:`4`:

>>> t.value# doctest: +SKIP
3.999999999962744

To learn more about dual values, see :ref:`duals`. For controlling the numeric
precision requirements, see :ref:`tolerances`.


.. rubric:: Removing constraints

Let's say we are not happy with our upper bound on :math:`x` and we'd rather
constrain it to be inside a unit simplex. We can remove the former constraint as
follows:

>>> P.remove_constraint(Cone)

Instead of the constraint itself, we could also have supplied its index in the
problem, as constraints remain in the order in which you add them. Now let's add
the new constraint:

>>> Csimplex = P.add_constraint(x << picos.Simplex())
>>> print(P)
Quadratic Program
  minimize (t - 5)² + 2
  over
    1×1 real variable t
    4×1 real variable x
  subject to
    t = ∑(x)
    x ∈ {x ≥ 0 : ∑(x) ≤ 1}

If we solve again we expect :math:`t` to be :math:`1`:

>>> solution = P.solve()
>>> round(t, 5)
1.0

If the selected solver supports this, changes to a problem's constraints and
objective are passed in the form of updates to the solver's internal state which
can make successive solution searches much faster. Unfortunately, CVXOPT is
stateless so we don't get an advantage here.


.. rubric:: Grouping constraints

You can also add and remove constraints as a group. Let's compute four real
numbers between :math:`0` and :math:`1`, represented by :math:`x_1` to
:math:`x_4` (``x[0]`` to ``x[3]``), such that their minimum distance is
maximized:

>>> from pprint import pprint
>>> P.reset()                                 # Reset the problem, keep options.
>>> d = RealVariable("d", 3)                  # A vector of distances.
>>> P.set_objective("max", picos.min(d))      # Maximize the minimum distance.
>>> C1 = P.add_constraint(x[0] >= 0)          # Numbers start at 0.
>>> C2 = P.add_constraint(x[3] <= 1)          # And end at 1.
>>> # Use constraint groups to order the x[i] and map their distance to y:
>>> G1 = P.add_list_of_constraints([x[i - 1] <= x[i] for i in range(4)])
>>> G2 = P.add_list_of_constraints([d[i] == x[i+1] - x[i] for i in range(3)])
>>> pprint(G1)                                # Show the constraints added.
[<1×1 Affine Constraint: x[-1] ≤ x[0]>,
 <1×1 Affine Constraint: x[0] ≤ x[1]>,
 <1×1 Affine Constraint: x[1] ≤ x[2]>,
 <1×1 Affine Constraint: x[2] ≤ x[3]>]
>>> pprint(G2)
[<1×1 Affine Constraint: d[0] = x[1] - x[0]>,
 <1×1 Affine Constraint: d[1] = x[2] - x[1]>,
 <1×1 Affine Constraint: d[2] = x[3] - x[2]>]
>>> print(P)
Optimization Problem
  maximize min(d)
  over
    3×1 real variable d
    4×1 real variable x
  subject to
    x[0] ≥ 0
    x[3] ≤ 1
    x[i-1] ≤ x[i] ∀ i ∈ [0…3]
    d[i] = x[i+1] - x[i] ∀ i ∈ [0…2]

This looks promising and the constraint groups are nicely formatted, let's solve
the problem and see what we get:

>>> P.solve()
<primal feasible solution pair (claimed optimal) from cvxopt>
>>> print(x)# doctest: +SKIP
[ 5.00e-01]
[ 5.00e-01]
[ 5.00e-01]
[ 5.00e-01]
>>> print(d)# doctest: +SKIP
[ 1.88e-11]
[ 1.88e-11]
[ 1.88e-11]

Apparently there is an error! Revisiting our problem definition, it seems the
first constraint in :math:`G_1`, that is ``x[-1] <= x[0]``, was unnecessary and
forces all :math:`x_i` to take the same value. Luckily, we can remove it from
the group by first specifying the group to access (counting single constraints
as groups of size one) and then the constraint to remove from it:

>>> P.remove_constraint((2, 0))          # Remove 1st constraint from 3rd group.
>>> pprint(P.get_constraint((2,)))       # Show the modified 3rd group.
[<1×1 Affine Constraint: x[0] ≤ x[1]>,
 <1×1 Affine Constraint: x[1] ≤ x[2]>,
 <1×1 Affine Constraint: x[2] ≤ x[3]>]

Now it should work:

>>> print(P)
Optimization Problem
  maximize min(d)
  over
    3×1 real variable d
    4×1 real variable x
  subject to
    x[0] ≥ 0
    x[3] ≤ 1
    x[i] ≤ x[i+1] ∀ i ∈ [0…2]
    d[i] = x[i+1] - x[i] ∀ i ∈ [0…2]
>>> _ = P.solve()  # Don't show or save the solution object.
>>> print(x)#  doctest: +ELLIPSIS
[ ...]
[ 3.33e-01]
[ 6.67e-01]
[ 1.00e+00]
>>> print(d)
[ 3.33e-01]
[ 3.33e-01]
[ 3.33e-01]

(If you see an ellipsis `...` in an example that means we've cut out a near-zero
to allow the other values to be validated automatically.)


.. Problem Export
.. --------------
..
.. Lastly, we show how you can export a problem to a file, in this case in the
.. ``.lp`` format:
..
.. >>> P.reset()
.. >>> P.set_objective("min", t)
.. >>> P.add_constraint(x[0] >= 1.5)
.. >>> P.add_constraint(t - x[0] >= 0.7)
.. >>> print(P)
.. -----------------------
.. Linear Program
..   minimize t
..   over
..     1×1 real variable t
..     4×1 real variable x
..   subject to
..     x[0] ≥ 1.5
..     t - x[0] ≥ 0.7
.. -----------------------
.. >>> P.write_to_file(".helloworld.lp")
.. >>> with open(".helloworld.lp", "r") as fp:
.. ...     print(fp.read())
.. ???
.. >>> import os
.. >>> os.unlink(".helloworld.lp")
