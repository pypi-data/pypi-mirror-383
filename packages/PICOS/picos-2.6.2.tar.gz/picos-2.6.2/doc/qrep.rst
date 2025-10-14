.. TODO: Replace all testcode/testoutput blocks with interactive listings so
..       that test.py can validate the examples.


.. _qrep:

Quantum Relative Entropy Programming
====================================

PICOS supports quantum relative entropy programming as of version 2.5.0 when
used with the solver `QICS <https://qics.readthedocs.io/en/stable/>`_. These are
convex optimization problems which minimizing over the quantum (Umegaki)
relative entropy, which is defined as

.. math::

    S(X \| Y) = \operatorname{Tr}(X\log(X) - X\log(Y)),

over positive semidefinite matrices :math:`X\in\mathbb{H}^n_+` and
:math:`Y\in\mathbb{H}^n_+`. This function is jointly convex in both of its
arguments. In PICOS, this function is represented by the expression
:func:`~picos.quantrelentr`.

Below, we show two examples of quantum relative entropy programs which arise in
quantum information theory. These are taken from the  `QICS documentation
<https://qics.readthedocs.io/en/stable/examples/qrep/index.html>`_, which contain
many other examples of quantum relative entropy programs which can be solved
using PICOS.


Relative entropy of entanglement
--------------------------------

Consider a bipartite quantum state :math:`X\in\mathbb{H}^{n_1 n_2}`. The
relative entropy of entanglement aims to quantify how entangled :math:`X` is by
measuring the distance, in the quantum relative entropy sense, to the set of
separable states.

However, describing the set of separable states is NP-hard in general.
Therefore, it is useful to use a relaxation of this condition known as the
positive partial transpose (PPT) criterion :ref:`[1] <qrep_refs>`

.. math::

    \mathsf{PPT} = \{ X \in \mathbb{H}^{n_1n_2} : X^{T_2} \succeq 0 \},

where :math:`X \mapsto X^{T_2}` denotes the partial transpose with respect to
the second subsystem. The (approximate) relative entropy of entanglement is then
given as the optimal value of

.. math::

    \underset{Y \in \mathbb{H}^{n_1n_2}}{\text{minimize}}\quad& S(X \| Y) \\
    \text{subject to}\quad& \operatorname{Tr}(Y) = 1\\
    & Y^{T_2} \succeq 0 \\
    & Y \succeq 0. \\

This can be implemented in PICOS as follows:

.. testcode::

    import picos

    # Create a quantum state X.
    X = picos.Constant("X", [
        [0.5, 0.0, 0.0, 0.5],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.5, 0.0, 0.0, 0.5]])

    # Define the problem.
    P = picos.Problem()
    Y = picos.SymmetricVariable("Y", 4)

    P.set_objective("min", picos.quantrelentr(X, Y))
    P.add_constraint(picos.trace(Y) == 1.0)
    P.add_constraint(Y.partial_transpose(1) >> 0)

    print(P)

    # Solve the problem.
    P.solve(solver="qics")

    print("\nRelative entropy of entanglement of X:", round(P, 4))

.. testoutput::

    Quantum Relative Entropy Program
      minimize S(X‖Y)
      over
        4×4 symmetric variable Y
      subject to
        tr(Y) = 1
        Y.{[2×2]⊗[2×2]ᵀ} ≽ 0

    Relative entropy of entanglement of X: 0.6931


Entanglement-assisted channel capacity
--------------------------------------

When using a quantum channel to transmit information, we are often interested in
the maximum rate of information we can transmit in a way that is robust of
noise. Depending on what quantum resources are used, there are different
theorems which describe this limit.

For a quantum channel described by a Stinespring represntation
:math:`\mathcal{N}(X)=\operatorname{Tr}_2(VXV^\dagger)`, the entanglement-
assisted channel capacity :ref:`[2] <qrep_refs>` is given by the optimal value
of

.. math::

    \underset{X \in \mathbb{H}^{n}}{\text{maximize}}\quad& S(VXV^\dagger) -
    S(\operatorname{Tr}_1(VXV^\dagger)) + S(\operatorname{Tr}_2(VXV^\dagger)) \\
    \text{subject to}\quad& \operatorname{Tr}(X) = 1\\
    & X \succeq 0.

The objective function is known as the quantum mutual information, and can be
modelled in PICOS using the :func:`~picos.quantcondentr` and :func:`~picos.quantentr`
expressions.

.. testcode::

    import math
    import picos

    # Define Stinespring isometry for amplitude damping channel.
    gamma = 0.5
    V = picos.Constant("V", [
        [1., 0.                ],
        [0., math.sqrt(1-gamma)],
        [0., math.sqrt(gamma)  ],
        [0., 0.                ]
    ])

    # Define the problem.
    P = picos.Problem()
    X = picos.SymmetricVariable("X", 2)

    obj1 = picos.quantcondentr(V*X*V.T, 1)
    obj2 = picos.quantentr(picos.partial_trace(V*X*V.T, 0))

    P.set_objective("max", obj1 + obj2)
    P.add_constraint(picos.trace(X) == 1)
    P.add_constraint(X >> 0)

    print(P)

    # Solve the problem.
    P.solve(solver="qics")

    print("\nEntanglement-assisted channel capacity:", round(P, 4))

.. testoutput::

    Quantum Relative Entropy Program
      maximize S(V·X·Vᵀ) - S((V·X·Vᵀ).{[2×2]⊗tr([2×2])}) + S((V·X·Vᵀ).{tr([2×2])⊗[2×2]})
      over
        2×2 symmetric variable X
      subject to
        tr(X) = 1
        X ≽ 0

    Entanglement-assisted channel capacity: 0.6931


Quantum key distribution
------------------------

When designing a quantum cryptographic protocol, we are interested in computing
the quantum key rate of a given protocol which allows us to certify the security
of the protocol. This quantum key rate can be computed by solving the
quantum relative entropy program :ref:`[3] <qrep_refs>`

.. math::

    \underset{X \in \mathbb{H}^{n}}{\text{minimize}}\quad& S(\mathcal{G}(X) \|
    \mathcal{Z}(\mathcal{G}(X))) \\
    \text{subject to}\quad& \operatorname{Tr}(A_i X) = b_i, \quad i=1,\ldots,p\\
    & X \succeq 0.

where :math:`\mathcal{G}` is a completely positive linear map,
:math:`\mathcal{Z}` is the pinching map which maps off-diagonal blocks of a ,
block-matrix to zero, and :math:`A_i` and :math:`b_i` encode a set of
experimental constraints.

In PICOS, this slice of the quantum relative entropy function can be modelled
using the :func:`~picos.quantkeydist` expression. Below, we show how the key rate of
the entanglement assisted BB84 protocol from :ref:`[4] <qrep_refs>` can be
computed using PICOS.

.. testcode::

    import numpy
    import picos

    # Define entanglement assisted BB84 protocol.
    qx = 0.25
    qz = 0.75

    X0 = numpy.array([[.5,  .5], [ .5, .5]])
    X1 = numpy.array([[.5, -.5], [-.5, .5]])
    Z0 = numpy.array([[1.,  0.], [ 0., 0.]])
    Z1 = numpy.array([[0.,  0.], [ 0., 1.]])

    Ax = numpy.kron(X0, X1) + numpy.kron(X1, X0)
    Az = numpy.kron(Z0, Z1) + numpy.kron(Z1, Z0)

    # Define the problem.
    P = picos.Problem()
    X = picos.SymmetricVariable("X", 4)

    P.set_objective("min", picos.quantkeydist(X))
    P.add_constraint(picos.trace(X) == 1)
    P.add_constraint((X | Ax) == qx)
    P.add_constraint((X | Az) == qz)

    print(P)

    # Solve the problem.
    P.solve(solver="qics")

    print("\nebBB84 key rate:", round(P, 4))

.. testoutput::

    Quantum Relative Entropy Program
      minimize S(X‖Z(X))
      over
        4×4 symmetric variable X
      subject to
        tr(X) = 1
        ⟨X, [4×4]⟩ = 0.25
        ⟨X, [4×4]⟩ = 0.75

    ebBB84 key rate: 0.1308


.. _qrep_refs:

References
----------

    1. “Separability of mixed states: necessary and sufficient conditions,”
       M. Horodecki, P. Horodecki, and R. Horodecki,
       Physics Letters A, vol. 223, no. 1, pp. 1–8, 1996.

    2. “Entanglement-assisted capacity of a quantum channel and the reverse Shannon
       theorem,” C. H. Bennett, P. W. Shor, J. A. Smolin, and A. V. Thapliyal,
       IEEE transactions on Information Theory,
       vol. 48, no. 10, pp. 2637–2655, 2002.

    3. “Reliable numerical key rates for quantum key distribution”,
       A. Winick, N. Lutkenhaus, and P. J. Coles. Quantum, vol. 2, p. 77, 2018.

    4. “Quantum key distribution rates from non-symmetric conic optimization”,
       L. A. Gonzalez, et al. arXiv preprint arXiv:2407.00152, 2024.