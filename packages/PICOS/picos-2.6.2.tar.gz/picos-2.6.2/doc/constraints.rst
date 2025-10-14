.. warning::

    This part of the documentation has not been touched for a while. It might
    be incomplete, reference deprecated functions or make a claim that does not
    apply to the latest version of PICOS any more. On the bright side, code
    listings are validated and still work. Watch your step!


.. _constraints:

Additional constraints
======================

This section introduces additional expression and constraint types that didn't
fit into the tutorial. Again, let us import PICOS:

>>> import picos as pc

We replicate some of the variables and data used in the tutorial:

>>> from picos import Constant, RealVariable
>>> t = RealVariable("t")
>>> x = RealVariable("x", 4)
>>> Y = RealVariable("Y", (2, 4))
>>> alpha = Constant("α", 23)
>>> A = [Constant("A[{}]".format(i), range(i, i + 8), (2, 4)) for i in range(5)]

This time, :math:`Z` and :math:`b` are lists:

>>> Z = [RealVariable("Z[{0}]".format(i), (4,2)) for i in range(5)]
>>> b = ([0, 2, 0, 3], [1, 1, 0, 5], [-1, 0, 2, 4], [0, 0, -2, -1],
...      [1, 1, 0, 0])
>>> b = [Constant("b[{}]".format(i), b[i]) for i in range(len(b))]


.. _flowcons:

Graph flow constraints
----------------------

Flow constraints in graphs are entered using a Networkx_ graph. The following
example finds a (trivial) maximal flow from ``'S'`` to ``'T'`` in ``G``.

.. _Networkx: https://networkx.github.io/

>>> import networkx as nx
>>> G = nx.DiGraph()
>>> G.add_edge('S','A', capacity=1)
>>> G.add_edge('A','B', capacity=1)
>>> G.add_edge('B','T', capacity=1)
>>> pb = pc.Problem()
>>> # Adding the flow variables
>>> f={}
>>> for e in G.edges():
...     f[e]=pb.add_variable('f[{},{}]'.format(e[0], e[1]), 1)
>>> # A variable for the value of the flow
>>> F = pb.add_variable('F',1)
>>> # Creating the flow constraint
>>> flowCons = pb.add_constraint(pc.flow_Constraint(
...     G, f, 'S', 'T', F, capacity='capacity', graphName='G'))
>>> pb.set_objective('max',F)
>>> sol = pb.solve(solver='cvxopt')
>>> flow = {key: var.value for key, var in f.items()}

Picos allows you to define single source - multiple sinks problems.
You can use the same syntax as for a single source - single sink problems.
Just add a list of sinks and a list of flows instead.

.. TODO: Get rid of these testcode/testoutput so we can test via unittest.

.. testcode::

    import picos as pc
    import networkx as nx

    G=nx.DiGraph()
    G.add_edge('S','A', capacity=2); G.add_edge('S','B', capacity=2)
    G.add_edge('A','T1', capacity=2); G.add_edge('B','T2', capacity=2)

    pbMultipleSinks=pc.Problem()
    # Flow variable
    f={}
    for e in G.edges():
        f[e]=pbMultipleSinks.add_variable('f[{},{}]'.format(e[0], e[1]), 1)

    # Flow value
    F1=pbMultipleSinks.add_variable('F1',1)
    F2=pbMultipleSinks.add_variable('F2',1)

    flowCons = pc.flow_Constraint(
        G, f, source='S', sink=['T1','T2'], capacity='capacity',
        flow_value=[F1, F2], graphName='G')

    pbMultipleSinks.add_constraint(flowCons)
    pbMultipleSinks.set_objective('max',F1+F2)

    # Solve the problem
    pbMultipleSinks.solve(solver='cvxopt')

    print(pbMultipleSinks)
    print()
    print('The optimal flow F1 has value {:.1f}'.format(F1.value))
    print('The optimal flow F2 has value {:.1f}'.format(F2.value))

.. testoutput::
    :options: +NORMALIZE_WHITESPACE

    Linear Program
      maximize F1 + F2
      over
        1×1 real variables F1, F2, f[A,T1], f[B,T2], f[S,A], f[S,B]
      subject to
        Feasible S-(T1,T2)-flow in G has values F1, F2.

    The optimal flow F1 has value 2.0
    The optimal flow F2 has value 2.0

A similar syntax can be used for multiple sources-single sink flows.


Second Order Cone constraints
-----------------------------

.. TODO: Remove the warning and document the difference between a conic
..       quadratic constraint and an explicit SOC/RSOC constraint. Needs #157.

.. warning::

    This section in particular is outdated: The only direct way to create
    rotated second order cone constraints is now via the :func:`~picos.rsoc`
    set-generating function. If you input such a constraint as below, then you
    will receive either a convex or a conic quadratic constraint. The former is
    handled depending on the solver used. The latter will be transformed either
    to a rotated conic constraint (which implicitly adds additional constraints
    that are part of the rotated second order cone definition) or it will remain
    nonconvex quadratic, depending on an option.

There are two types of second order cone constraints supported in PICOS.

    * The constraints of the type :math:`\Vert x \Vert \leq t`, where :math:`t`
      is a scalar affine expression and :math:`x` is
      a multidimensional affine expression (possibly a matrix, in which case the
      norm is Frobenius). This inequality forces
      the vector :math:`[t; x]` to belong to a Lorrentz-Cone (also called
      *ice-cream cone*).
    * The constraints of the type :math:`\Vert x \Vert^2 \leq t u,\ t \geq 0`,
      where :math:`t` and :math:`u` are scalar affine expressions and
      :math:`x` is a multidimensional affine expression, which constrain
      the vector :math:`[t; u; x]` inside a rotated version of the Lorretz cone.

A few examples:

>>> # A simple ice-cream cone constraint
>>> abs(x) < (2|x-1)
<5×1 SOC Constraint: ‖x‖ ≤ ⟨[2], x - [1]⟩>
>>> # SOC constraint with Frobenius norm
>>> abs(Y+Z[0].T) < t+alpha
<9×1 SOC Constraint: ‖Y + Z[0]ᵀ‖ ≤ t + α>
>>> # Rotated SOC constraint
>>> abs(Z[1][:,0])**2 < (2*t-alpha)*(x[2]-x[-1])
<Conic Quadratic Constraint: ‖Z[1][:,0]‖² ≤ (2·t - α)·(x[2] - x[-1])>
>>> # t**2 is internally represented as the squared norm of [t]
>>> t**2 < alpha + t
<Squared Scalar Constraint: t² ≤ α + t>
>>> # 1 is understood as the squared norm of [1]
>>> 1 < (t-1)*(x[2]+x[3])
<Conic Quadratic Constraint: (t - 1)·(x[2] + x[3]) ≥ 1>


Semidefinite constraints
------------------------

Linear matrix inequalities (LMI) can be entered thanks to an overload of the
operators ``<<`` and ``>>``. For example, the LMI

.. math::
    :nowrap:

    \begin{equation*}
        \sum_{i=0}^3 x_i b_i b_i^T \succeq b_4 b_4^T,
    \end{equation*}

where :math:`\succeq` is used to denote the Löwner ordering, is passed to PICOS
by writing:

>>> pc.sum([x[i]*b[i]*b[i].T for i in range(4)]) >> b[4]*b[4].T
<4×4 LMI Constraint: ∑(x[i]·b[i]·b[i]ᵀ : i ∈ [0…3]) ≽ b[4]·b[4]ᵀ>

Note the difference with

>>> pc.sum([x[i]*b[i]*b[i].T for i in range(4)]) > b[4]*b[4].T
<4×4 Affine Constraint: ∑(x[i]·b[i]·b[i]ᵀ : i ∈ [0…3]) ≥ b[4]·b[4]ᵀ>

which yields an elementwise inequality.

For convenience, it is possible to add a symmetric matrix variable ``X``,
by specifying the option ``vtype=symmetric``. This has the effect to
store all the affine expressions which depend on ``X`` as a function
of its lower triangular elements only.

>>> sdp = pc.Problem()
>>> X = sdp.add_variable('X',(4,4),vtype='symmetric')
>>> C = sdp.add_constraint(X >> 0)
>>> print(sdp)
Feasibility Problem
  find an assignment
  for
    4×4 symmetric variable X
  subject to
    X ≽ 0

In this example, you see indeed that the problem has 10=(4*5)/2 variables,
which correspond to the lower triangular elements of ``X``.

.. warning::

     When a constraint of the form ``A >> B`` is passed to PICOS, it is not
     enforced that :math:`A - B` is symmetric. How the constraint is passed then
     depends on the solver, for instance it could be that the lower or upper
     triangular part is ignored. You can add a constraint of the form
     ``A - B == (A - B).T`` to enforce symmetry.


Inequalities involving geometric means
--------------------------------------

It is possible to enter an inequality of the form

.. math::
    t \leq \prod_{i=1}^n x_i^{1/n}

in PICOS, where :math:`t` is a scalar affine expression and :math:`x` is an
affine expression of dimension :math:`n` (possibly a matrix, in which case
:math:`x_i` is counted in column major order). This inequality is internally
converted to an equivalent set of second order cone inequalities, by using
standard techniques (cf. e.g. :ref:`[1] <tuto_refs>`).

Many convex constraints can be formulated using inequalities that involve
a geometric mean. For example, :math:`t \leq x_1^{2/3}` is equivalent
to :math:`t \leq t^{1/4} x_1^{1/4} x_1^{1/4}`, which can be entered in PICOS
thanks to the function :func:`~picos.geomean`:

  >>> t < pc.geomean(t //x[1] //x[1] //1)
  <Geometric Mean Constraint: geomean([t; x[1]; x[1]; 1]) ≥ t>

Note that the latter example can also be passed to PICOS in a more simple way,
thanks to an overloading of the ``**`` exponentiation operator:

  >>> t < x[1]**(2./3)
  <Power Constraint: x[1]^(2/3) ≥ t>

Such a power constraint will be reformulated as a geometric mean inequality when
the problem is solved, which in turn will be translated to conic inequalities.


Inequalities involving real powers or trace of matrix powers
------------------------------------------------------------

As mentionned above, the ``**`` exponentiation operator has been overloaded
to support real exponents. A rational approximation of the exponent is used,
and the inequality are internally reformulated as a set of equivalent SOC
inequalities. Note that only inequalities defining a convex regions can be
passed:

>>> t**0.6666 > x[0]
<Power Constraint: t^(2/3) ≥ x[0]>
>>> t**-0.5 < x[0]
<Power Constraint: t^(-1/2) ≤ x[0]>
>>> t**-0.5 > x[0]
Traceback (most recent call last):
  ...
TypeError: Cannot lower-bound a nonconcave (trace of) power.

More generally, inequalities involving trace of matrix powers can be passed to
PICOS, by using the :func:`~picos.tracepow` function. The following example
creates the constraint

.. math::

    \operatorname{trace}\ \big(x_0 A_0 A_0^T + x_2 A_2 A_2^T\big)^{2.5} \leq 3.

>>> pc.tracepow(x[0] * A[0]*A[0].T + x[2] * A[2]*A[2].T, 2.5) <= 3
<Trace of Power Constraint: tr((x[0]·A[0]·A[0]ᵀ + x[2]·A[2]·A[2]ᵀ)^(5/2)) ≤ 3>

.. Warning::

    when a power expression :math:`x^p` (resp. the trace of matrix power
    :math:`\operatorname{trace}\ X^p` ) is used, the base :math:`x` is forced
    to be nonnegative (resp. the base :math:`X` is forced to be positive
    semidefinite) by picos.

When the exponent is :math:`0<p<1`,
it is also possible to represent constraints of the form
:math:`\operatorname{trace}(M X^p) \geq t`
with SDPs, where :math:`M\succeq 0`, see :ref:`[2] <tuto_refs>`.

>>> pc.tracepow(X, 0.6666, coef = A[0].T*A[0]+"I") >= t
<Trace of Scaled Power Constraint: tr((A[0]ᵀ·A[0] + I)·X^(2/3)) ≥ t>

As for geometric means, inequalities involving real powers yield their internal
representation via the ``constraints`` and ``variables`` attributes.


.. _pnorms:

Inequalities involving generalized p-norm
-----------------------------------------

Inequalities of the form :math:`\Vert x \Vert_p \leq t` can be entered by using the
function :func:`~picos.norm`. This function is also defined for :math:`p < 1`
by the usual formula :math:`\Vert x \Vert_p :=  \Big(\sum_i |x_i|^p \Big)^{1/p}`.
The norm function is convex over :math:`\mathbb{R}^n` for all :math:`p\geq 1`, and
concave over the set of vectors with nonnegative coordinates for :math:`p \leq 1`.

>>> pc.norm(x,3) < t
<Vector p-Norm Constraint: ‖x‖_3 ≤ t>
>>> pc.norm(x,'inf') < 2
<Maximum Norm Constraint: ‖x‖_max ≤ 2>
>>> pc.norm(x,0.5) > x[0]-x[1]
<Generalized p-Norm Constraint: ‖x‖_(1/2) ≥ x[0] - x[1] ∧ x ≥ 0>

.. Warning::

    Note that when a constraint of the form ``norm(x,p) >= t`` is entered (with
    :math:`p \leq 1` ), PICOS forces the vector ``x`` to be nonnegative
    (componentwise).

Inequalities involving the generalized :math:`L_{p,q}` norm of
a matrix can also be handled with picos, cf. the documentation of
:func:`~picos.norm` .

As for geometric means, inequalities involving p-norms yield their internal
representation via the ``constraints`` and ``variables`` attributes.


Inequalities involving the nth root of a determinant
----------------------------------------------------

The function :func:`~picos.detrootn`
can be used to enter the :math:`n`-th root of the determinant of a
:math:`(n \times n)`-symmetric positive semidefinite matrix:

>>> M = sdp.add_variable('M',(5,5),'symmetric')
>>> t < pc.detrootn(M)
<n-th Root of a Determinant Constraint: det(M)^(1/5) ≥ t>

.. warning::

    Note that when a constraint of the form ``t < pc.detrootn(M)`` is entered
    (with :math:`p \leq 1`), PICOS forces the matrix ``M`` to be positive
    semidefinite.

As for geometric means, inequalities involving the nth root of a determinant
yield their internal representation via the ``constraints`` and ``variables``
attributes.


Set membership
--------------

Since Picos 1.0.2, there is a :class:`Set <picos.expressions.Set>` class that
can be used to pass constraints as membership of an affine expression to a set.

Following sets are currently supported:

    * :math:`L_p-` balls representing the set
      :math:`\{x: \Vert x \Vert_p \leq r\}` can be constructed with the function
      :func:`~picos.ball`
    * The standard simplex (scaled by a factor :math:`\gamma`)
      :math:`\{x \geq 0: \sum_i x_i \leq r \}` can be constructed with the
      function :func:`~picos.simplex`
    * Truncated simplexes :math:`\{0 \leq x \leq 1: \sum_i x_i \leq r \}`
      and symmetrized Truncated simplexes
      :math:`\{x: \Vert x \Vert_\infty \leq 1, \Vert x \Vert_1\leq r \}`
      can be constructed with the function :func:`~picos.truncated_simplex`

Membership of an affine expression to a set can be expressed with the overloaded
operator ``<<``. This returns a temporary object that can be passed to a picos
problem with the function :meth:`~.problem.Problem.add_constraint`.

>>> x << pc.simplex(1)
<Unit Simplex Constraint: x ∈ {x ≥ 0 : ∑(x) ≤ 1}>
>>> x << pc.truncated_simplex(2)
<Box-Truncated Simplex Constraint: x ∈ {0 ≤ x ≤ 1 : ∑(x) ≤ 2}>
>>> x << pc.truncated_simplex(2,sym=True)
<Box-Truncated 1-norm Ball Constraint: x ∈ {-1 ≤ x ≤ 1 : ∑(|x|) ≤ 2}>
>>> x << pc.ball(3)
<5×1 SOC Constraint: ‖x‖ ≤ 3>
>>> pc.ball(2,'inf') >> x
<Maximum Norm Constraint: ‖x‖_max ≤ 2>
>>> x << pc.ball(4,1.5)
<Vector p-Norm Constraint: ‖x‖_(3/2) ≤ 4>


.. _tuto_refs:

References
----------

1. "`Applications of second-order cone programming`",
   M.S. Lobo, L. Vandenberghe, S. Boyd and H. Lebret,
   *Linear Algebra and its Applications*,
   284, p. *193-228*, 1998.

2. "`On the semidefinite representations of real functions applied to symmetric
   matrices <http://opus4.kobv.de/opus4-zib/frontdoor/index/index/docId/1751>`_"
   , G. Sagnol,
   *Linear Algebra and its Applications*,
   439(10), p. *2829-2843*, 2013.
