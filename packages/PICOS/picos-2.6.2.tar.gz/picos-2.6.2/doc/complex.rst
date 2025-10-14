.. TODO: Replace all testcode/testoutput blocks with interactive listings so
..       that test.py can validate the examples.


.. _complex:

Complex Semidefinite Programming
================================

PICOS supports complex semidefinite programming as of version 1.0.1. It was
overhauled in version 2.0 to provide some of the features showcased below.
This extension of semidefinite programming to the complex domain was introduced
by Goemans and Williamson :ref:`[1] <complex_refs>` in order to pose relaxations
of combinatorial optimization problems.
Applications include quantum information theory :ref:`[2] <complex_refs>` and
the phase recovery problem in signal processing :ref:`[3] <complex_refs>`.

Complex problems can be defined in PICOS using the complex-valued variable types
:class:`~picos.ComplexVariable` and :class:`~picos.HermitianVariable`:

>>> from picos import ComplexVariable, HermitianVariable
>>> z = ComplexVariable("z", 4)
>>> H = HermitianVariable("H", 4)
>>> z
<4×1 Complex Variable: z>
>>> H
<4×4 Hermitian Variable: H>
>>> z.real
<4×1 Real Linear Expression: Re(z)>
>>> z.imag
<4×1 Real Linear Expression: Im(z)>

Their value can be set and retrieved as in the real case but may contain an
imaginary part:

>>> z.value = [1, 2+2j, 3+3j, 4j]
>>> z.value  # Note the CVXOPT typecode of 'z'.
<4x1 matrix, tc='z'>
>>> print(z)
[ 1.00e+00-j0.00e+00]
[ 2.00e+00+j2.00e+00]
[ 3.00e+00+j3.00e+00]
[ 0.00e+00+j4.00e+00]
>>> z.real.value
<4x1 matrix, tc='d'>
>>> print(z.real)
[ 1.00e+00]
[ 2.00e+00]
[ 3.00e+00]
[ 0.00e+00]
>>> print(z.imag)
[ 0.00e+00]
[ 2.00e+00]
[ 3.00e+00]
[ 4.00e+00]

Just like real variables are the simplest form of an
:class:`~picos.expressions.AffineExpression`, complex variables are represented
to you as instances of :class:`~picos.expressions.ComplexAffineExpression`.
Most notably this gives access to complex conjugation and hermitian
transposition:

>>> z.conj
<4×1 Complex Linear Expression: conj(z)>
>>> z.H
<1×4 Complex Linear Expression: zᴴ>

Internally complex variables are represented as real variable vectors:

>>> z.dim  # Twice its dimension on the complex field.
8
>>> H.dim  # The same dimension as an arbitrary real matrix of same shape.
16

Note that in the hermitian case, we get away with just :math:`4 \cdot 4 = 16`
*real* scalar variables due to the vectorization used. This leads to a smaller
footprint when the problem is passed to a solver.

Unlike real-valued variables, :class:`~picos.ComplexVariable` and
:class:`~picos.HermitianVariable` do not accept variable bounds at creation, and
any properly complex expression formed from them cannot appear on either side of
an affine inequality constraint or as an objective function. However, PICOS
detects when you supply a real-valued expression in any of these places even if
it was created from complex expressions:

>>> A = ~z*~z.H  # Use the current value of z to create a constant 4×4 matrix.
>>> A
<4×4 Complex Constant: [z]·[zᴴ]>
>>> A.hermitian  # By construction this matrix is hermitian.
True
>>> (H|A)  # Create a complex expression involving H.
<1×1 Complex Linear Expression: ⟨H, [z]·[zᴴ]⟩>
>>> (H|A).isreal  # On closer inspection, it is always real-valued.
True
>>> (H|A).refined  # This means it can be "refined" to a real expression.
<1×1 Real Linear Expression: ⟨H, [z]·[zᴴ]⟩>
>>> (H|A) >= 0  # Refinement happens automatically wherever necessary.
<1×1 Affine Constraint: ⟨H, [z]·[zᴴ]⟩ ≥ 0>
>>> H == A  # Equalities involving complex expressions can be posed as normal.
<4×4 Complex Equality Constraint: H = [z]·[zᴴ]>

Complex linear matrix inequalities are created just as in the real case with the
overloaded ``<<`` and ``>>`` operators representing the Loewner order:

>>> H >> 0
<4×4 Complex LMI Constraint: H ≽ 0>

Since solvers at this time generally do not support complex optimization, PICOS
transforms such a constraint to an equivalent real LMI during solution search.
Only to demonstrate this behavior, we do it manually:

>>> from picos import Options
>>> from picos.constraints import ComplexLMIConstraint
>>> P = ComplexLMIConstraint.RealConversion.convert(H >> 0, Options())
>>> P.get_constraint(0)
<8×8 LMI Constraint: [Re(H), -Im(H); Im(H), Re(H)] ≽ 0>

.. _fidelity:

Fidelity in Quantum Information Theory
--------------------------------------

The material of this section is inspired by a lecture of John Watrous
:ref:`[4] <complex_refs>`.

The fidelity between two (hermitian) positive semidefinite operators :math:`P`
and :math:`Q` is defined as

.. math::
    F(P,Q)
    = \left\Vert P^{\frac{1}{2}} Q^{\frac{1}{2}} \right\Vert_{\text{tr}}
    = \max_U \left|
        \operatorname{trace}\left(P^{\frac{1}{2}} U Q^{\frac{1}{2}}\right)
    \right|,

where the trace norm :math:`\Vert \cdot \Vert_{\text{tr}}` is the sum of the
singular values, and the maximization goes over the set of all unitary matrices
:math:`U`.
This quantity can be expressed as the optimal value of the following
complex-valued SDP:

.. math::
    :nowrap:

    \begin{eqnarray*}
        &\underset{Z \in \mathbb{C}^{n \times n}}{\mbox{maximize}}
        &\frac{1}{2}\operatorname{trace}(Z + Z^*)
    \\
        &\mbox{subject to}
        &\left(\begin{array}{cc}
            P & Z \\
            Z^* & Q
        \end{array}\right) \succeq 0
    \end{eqnarray*}

This model can be implemented in PICOS as follows:

.. testcode::

    import numpy
    import picos

    # Create a positive semidefinite constant P.
    _P = picos.Constant([
        [ 1  -1j,  2  +2j,  1     ],
        [     3j,     -2j, -1  -1j],
        [ 1  +2j, -0.5+1j,  1.5   ]])
    P = (_P*_P.H).renamed("P")

    # Create a positive semidefinite constant Q.
    _Q = picos.Constant([
        [-1  -2j,      2j,  1.5   ],
        [ 1  +2j,     -2j,  2.0-3j],
        [ 1  +2j, -1  +1j,  1  +4j]])
    Q = (_Q*_Q.H).renamed("Q")

    # Define the problem.
    F = picos.Problem()
    Z = picos.ComplexVariable("Z", P.shape)
    F.set_objective("max", 0.5*picos.trace(Z + Z.H))
    F.add_constraint(((P & Z) // (Z.H & Q)) >> 0)

    print(F)

    # Solve the problem.
    F.solve(solver = "cvxopt")

    print("\nOptimal value:", round(F, 4))
    print("Optimal Z:", Z.value, sep="\n")

    # Also compute the fidelity via NumPy for comparison.
    PP  = numpy.matrix(P.value)
    QQ  = numpy.matrix(Q.value)
    S,U = numpy.linalg.eig(PP)
    sqP = U * numpy.diag([s**0.5 for s in S]) * U.H  # Square root of P.
    S,U = numpy.linalg.eig(QQ)
    sqQ = U * numpy.diag([s**0.5 for s in S]) * U.H  # Square root of Q.
    Fnp = sum(numpy.linalg.svd(sqP * sqQ)[1])  # Trace-norm of sqrt(P)·sqrt(Q).

    print("Fidelity F(P,Q) computed by NumPy:", round(Fnp, 4))

.. testoutput::

    Complex Semidefinite Program
      maximize 0.5·tr(Z + Zᴴ)
      over
        3×3 complex variable Z
      subject to
        [P, Z; Zᴴ, Q] ≽ 0

    Optimal value: 39.8938
    Optimal Z:
    [ 1.06e+01+j2.04e+00 -7.21e+00+j5.77e+00  3.58e+00-j8.10e+00]
    [-8.26e+00-j2.13e+00  1.65e+01+j3.61e-01  8.59e-02-j2.29e+00]
    [-1.38e+00+j6.42e+00 -5.65e-01+j1.55e+00  1.28e+01-j2.40e+00]

    Fidelity F(P,Q) computed by NumPy: 39.8938


Phase Recovery in Signal Processing
-----------------------------------

This section is inspired by :ref:`[3] <complex_refs>`.

The goal of the phase recovery problem is to reconstruct the complex phase of a
vector given only the magnitudes of some linear measurements.
This problem can be formulated as a non-convex optimization problem, and the
authors of :ref:`[3] <complex_refs>` have proposed a complex semidefinite
relaxation similar to the well known relaxation of the **Max-Cut Problem**:
Given a linear operator :math:`A` and a vector :math:`b` of measured amplitudes,
define the positive semidefinite hermitian matrix

.. math::
    M = \operatorname{Diag}(b) (I - AA^\dagger) \operatorname{Diag}(b).

The **Phase-Cut Problem** is:

.. math::
    :nowrap:

    \begin{eqnarray*}
        &\underset{U \in \mathbb{H}_n}{\mbox{minimize}}
        &\langle U, M \rangle
    \\
        &\mbox{subject to}
        &\operatorname{diag}(U) = 1
    \\
        &&U \succeq 0
    \end{eqnarray*}

Note that :math:`U` must be hermitian (:math:`U \in \mathbb{H}_n` ).
We obtain an exact solution :math:`u` to the phase recovery problem if
:math:`U = uu^*` has rank one.
Otherwise, the leading singular vector of :math:`U` is used as an approximation.

This problem can be implemented as follows using PICOS:

.. testcode::

    import cvxopt
    import numpy
    import picos

    # Make the output reproducible.
    cvxopt.setseed(1)

    # Generate an arbitrary rank-deficient hermitian matrix M.
    n, rank = 5, 4
    m = cvxopt.normal(n, rank) + 1j*cvxopt.normal(n, rank)
    M = picos.Constant("M", m*m.H)

    # Define the problem.
    P = picos.Problem()
    U = picos.HermitianVariable("U", n)
    P.set_objective("min", (U | M))
    P.add_constraint(picos.maindiag(U) == 1)
    P.add_constraint(U >> 0)

    print(P)

    # Solve the problem.
    P.solve(solver="cvxopt")

    print("\nOptimal U:", U, sep="\n")

    # Determine the rank of U.
    S, V = numpy.linalg.eig(U.value)
    Urnk = len([s for s in S if abs(s) > 1e-6])

    print("\nrank(U) =", Urnk)

.. testoutput::

    Complex Semidefinite Program
      minimize ⟨U, M⟩
      over
        5×5 hermitian variable U
      subject to
        maindiag(U) = [1]
        U ≽ 0

    Optimal U:
    [ 1.00e+00-j0.00e+00  6.31e-01-j7.76e-01 -8.84e-01+j4.68e-01  6.23e-01-j7.82e-01  7.52e-01+j6.59e-01]
    [ 6.31e-01+j7.76e-01  1.00e+00-j0.00e+00 -9.20e-01-j3.91e-01  1.00e+00-j9.69e-03 -3.75e-02+j9.99e-01]
    [-8.84e-01-j4.68e-01 -9.20e-01+j3.91e-01  1.00e+00-j0.00e+00 -9.17e-01+j4.00e-01 -3.56e-01-j9.34e-01]
    [ 6.23e-01+j7.82e-01  1.00e+00+j9.69e-03 -9.17e-01-j4.00e-01  1.00e+00-j0.00e+00 -4.72e-02+j9.99e-01]
    [ 7.52e-01-j6.59e-01 -3.75e-02-j9.99e-01 -3.56e-01+j9.34e-01 -4.72e-02-j9.99e-01  1.00e+00-j0.00e+00]

    rank(U) = 1


.. _complex_refs:

References
----------

    1. "Approximation algorithms for MAX-3-CUT and other problems via complex
       semidefinite programming",
       M.X. Goemans and D. Williamson.
       In Proceedings of the thirty-third annual
       *ACM symposium on Theory of computing*,
       pp. 443-452. ACM, 2001.

    2. "Semidefinite programs for completely bounded norms",
       J. Watrous,
       arXiv preprint 0901.4709, 2009.

    3. "Phase recovery, maxcut and complex semidefinite programming",
       I. Waldspurger, A. d'Aspremont, and S. Mallat.
       *Mathematical Programming*, pp. 1-35, 2012.

    4. "Semidefinite programs for fidelity and optimal measurements",
       J. Watrous.
       In the script of a course on Theory of Quantum Information,
       https://cs.uwaterloo.ca/~watrous/LectureNotes/CS766.Fall2011/08.pdf.
