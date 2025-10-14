.. _optdes:

Optimal Experimental Design
===========================

Optimal experimental design is a theory
at the interface of statistics and optimization,
which studies how to allocate some statistical trials
within a set of available design points.
The goal is to allow for the best possible
estimation of an unknown parameter :math:`\theta`.
In what follows, we assume the standard linear model with
multiresponse experiments: a trial in the :math:`i^{\textrm{th}}`
design point gives a multidimensional observation that
can be written as :math:`y_i = A_i^T \theta+\epsilon_i`,
where :math:`y_i` is of dimension :math:`l_i`,
:math:`A_i` is a :math:`m \times l_i-` matrix,
and the error vectors :math:`\epsilon_i` are i.i.d. with a unit variance.

Several optimization criteria exist, leading to different SDP, SOCP and LP
formulations.
As such, optimal experimental design problens are natural examples for problems
in conic optimization. For a review of the different formulations
and more references, see :ref:`[1] <optdes_refs>`.

The code below initializes the data used in all the examples of this page.
It should be run prior to any of the codes presented in this page.

>>> import cvxopt as cvx
>>> import picos
>>> #---------------------------------#
>>> # First generate some data :      #
>>> #       _ a list of 8 matrices A  #
>>> #       _ a vector c              #
>>> #---------------------------------#
>>> A = [cvx.matrix([[1,0,0,0,0],
...                  [0,3,0,0,0],
...                  [0,0,1,0,0]]),
...      cvx.matrix([[0,0,2,0,0],
...                  [0,1,0,0,0],
...                  [0,0,0,1,0]]),
...      cvx.matrix([[0,0,0,2,0],
...                  [4,0,0,0,0],
...                  [0,0,1,0,0]]),
...      cvx.matrix([[1,0,0,0,0],
...                  [0,0,2,0,0],
...                  [0,0,0,0,4]]),
...      cvx.matrix([[1,0,2,0,0],
...                  [0,3,0,1,2],
...                  [0,0,1,2,0]]),
...      cvx.matrix([[0,1,1,1,0],
...                  [0,3,0,1,0],
...                  [0,0,2,2,0]]),
...      cvx.matrix([[1,2,0,0,0],
...                  [0,3,3,0,5],
...                  [1,0,0,2,0]]),
...      cvx.matrix([[1,0,3,0,1],
...                  [0,3,2,0,0],
...                  [1,0,0,2,0]])
... ]
>>> c = cvx.matrix([1,2,3,4,5])

Multi-response c-optimal design (SOCP)
--------------------------------------

We compute the c-optimal design (``c=[1,2,3,4,5]``)
for the observation matrices ``A[i].T`` from the variable ``A`` defined above.
The results below suggest that we should allocate 12.8% of the
experimental effort on design point #5, and 87.2% on the design point #7.

.. rubric:: Primal problem

The SOCP for multiresponse c-optimal design is:

.. math::
   :nowrap:

   \begin{center}
   \begin{eqnarray*}
   &\underset{\substack{\mu \in \mathbb{R}^s\\
                        \forall i \in [s],\ z_i \in \mathbb{R}^{l_i}}}{\mbox{minimize}}
                      & \sum_{i=1}^s \mu_i\\
   &\mbox{subject to} & \sum_{i=1}^s A_i z_i = c\\
   &                  & \forall i \in [s],\ \Vert z_i \Vert_2 \leq \mu_i,
   \end{eqnarray*}
   \end{center}

>>> # create the problem, variables and params
>>> c_primal_SOCP = picos.Problem()
>>> AA = [picos.Constant('A[{0}]'.format(i), Ai)
...       for i, Ai in enumerate(A)] # each AA[i].T is a 3 x 5 observation matrix
>>> s  = len(AA)
>>> cc = picos.Constant('c', c)
>>> z  = [picos.RealVariable('z[{0}]'.format(i), AA[i].size[1])
...        for i in range(s)]
>>> mu = picos.RealVariable('mu', s)

>>> # define the constraints and objective function
>>> cones = c_primal_SOCP.add_list_of_constraints([abs(z[i]) <= mu[i] for i in range(s)])
>>> lin   = c_primal_SOCP.add_constraint(picos.sum([AA[i] * z[i] for i in range(s)]) == cc)
>>> c_primal_SOCP.set_objective('min', mu.sum)
>>> print(c_primal_SOCP)
Second Order Cone Program
  minimize ∑(mu)
  over
    3×1 real variable z[i] ∀ i ∈ [0…7]
    8×1 real variable mu
  subject to
    ‖z[i]‖ ≤ mu[i] ∀ i ∈ [0…7]
    ∑(A[i]·z[i] : i ∈ [0…7]) = c

>>> #solve the problem and retrieve the optimal weights of the optimal design.
>>> solution = c_primal_SOCP.solve(solver='cvxopt')
>>> mu = mu.value
>>> w = mu / sum(mu) #normalize mu to get the optimal weights

The optimal design is:

>>> print(w)# doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[...]
[...]
[...]
[...]
[ 1.28e-01]
[...]
[ 8.72e-01]
[...]

The ``[...]`` above indicate a numerical zero entry
(*i.e., which can be something like 2.84e-10*).
We use the ellipsis ``...`` instead for clarity and compatibility with **doctest**.

.. rubric:: Dual problem

This is only to check that we obtain the same solution with the dual problem,
and to provide one additional example in this tutorial:

.. math::
   :nowrap:

   \begin{center}
   \begin{eqnarray*}
   &\underset{u \in \mathbb{R}^m}{\mbox{maximize}}
                      & c^T u\\
   &\mbox{subject to} & \forall i \in [s],\ \Vert A_i^T u \Vert_2 \leq 1
   \end{eqnarray*}
   \end{center}


>>> # create the problem, variables and params
>>> c_dual_SOCP = picos.Problem()
>>> AA = [picos.Constant('A[{0}]'.format(i), Ai)
...       for i, Ai in enumerate(A)] # each AA[i].T is a 3 x 5 observation matrix
>>> s  = len(AA)
>>> cc = picos.Constant('c',c)
>>> u  = picos.RealVariable('u',c.size)
>>> # define the constraints and objective function
>>> cones = c_dual_SOCP.add_list_of_constraints(
...         [abs(AA[i].T*u)<=1 for i in range(s)])
>>> c_dual_SOCP.set_objective('max', (cc | u))
>>> print(c_dual_SOCP)#
Second Order Cone Program
  maximize ⟨c, u⟩
  over
    5×1 real variable u
  subject to
    ‖A[i]ᵀ·u‖ ≤ 1 ∀ i ∈ [0…7]
>>> #solve the problem and retrieve the weights of the optimal design
>>> solution = c_dual_SOCP.solve(solver='cvxopt')
>>> mu = [cons.dual[0] for cons in cones] #Lagrangian duals of the SOC constraints
>>> mu = cvx.matrix(mu)
>>> w=mu/sum(mu) #normalize mu to get the optimal weights

The optimal design is:

>>> print(w)# doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[...]
[...]
[...]
[...]
[ 1.28e-01]
[...]
[ 8.72e-01]
[...]


Single-response c-optimal design (LP)
-------------------------------------

When the observation matrices are row vectors (single-response framework),
the SOCP above reduces to a simple LP, because the variables
:math:`z_i` are scalar.
We solve below the LP for the case where there are 11
available design points, corresponding to the columns of the matrices
``A[4]``, ``A[5]``, ``A[6]``, and ``A[7][:,:-1]`` defined in the preambule.

The optimal design allocates 3.37% to point #5 (2nd column of ``A[5]``),
27.9% to point #7 (1st column of ``A[6]``),
11.8% to point #8 (2nd column of ``A[6]``),
27.6% to point #9 (3rd column of ``A[6]``),
and 29.3% to point #11 (2nd column of ``A[7]``).

>>> # create the problem, variables and params
>>> c_primal_LP = picos.Problem()
>>> A1 = [cvx.sparse(a[:,i],tc='d') for i in range(3) for a in A[4:]] #12 column vectors
>>> A1 = A1[:-1] # remove the last design point (it is the same as the last-but-one)
>>> s = len(A1)
>>> AA = [picos.Constant('A[{0}]'.format(i), Ai)
...       for i, Ai in enumerate(A1)] # each AA[i].T is a 1 x 5 observation matrix
>>> cc = picos.Constant('c', c)
>>> z = [picos.RealVariable('z[{0}]'.format(i), 1) for i in range(s)]
>>> mu = picos.RealVariable('mu', s)

>>> #define the constraints and objective function
>>> abs_con = c_primal_LP.add_list_of_constraints([abs(z[i]) <= mu[i] for i in range(s)])
>>> lin_con = c_primal_LP.add_constraint(picos.sum([AA[i]*z[i] for i in range(s)]) == cc)
>>> c_primal_LP.set_objective('min', mu.sum)

Note that there are no cone constraints, because
the constraints of the form :math:`|z_i| \leq \mu_i` are handled as two
inequalities when :math:`z_i` is scalar, so the problem is a LP indeed:

>>> print(c_primal_LP)
Linear Program
  minimize ∑(mu)
  over
    1×1 real variable z[i] ∀ i ∈ [0…10]
    11×1 real variable mu
  subject to
    |z[i]| ≤ mu[i] ∀ i ∈ [0…10]
    ∑(A[i]·z[i] : i ∈ [0…10]) = c

>>> #solve the problem and retrieve the weights of the optimal design
>>> solution = c_primal_LP.solve(solver='cvxopt')
>>> mu = mu.value
>>> w = mu / sum(mu) #normalize mu to get the optimal weights

The optimal design is:

>>> print(w)# doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[...]
[...]
[...]
[...]
[ 3.37e-02]
[...]
[ 2.79e-01]
[ 1.18e-01]
[ 2.76e-01]
[...]
[ 2.93e-01]

SDP formulation of c-optimal design
-----------------------------------

We give below the SDP for c-optimality, in primal and dual
form. You can observe that we obtain the same results as
with the SOCP presented earlier:
12.8% on design point #5, and 87.2% on design point #7.

.. rubric:: Primal problem

The SDP formulation of the c-optimal design problem is:

.. math::
   :nowrap:

   \begin{center}
   \begin{eqnarray*}
   &\underset{\mu \in \mathbb{R}^s}{\mbox{minimize}}
                      & \sum_{i=1}^s \mu_i\\
   &\mbox{subject to} & \sum_{i=1}^s \mu_i A_i A_i^T \succeq c c^T,\\
   &                  & \mu \geq 0.
   \end{eqnarray*}
   \end{center}

>>> # create the problem, variables and params
>>> c_primal_SDP = picos.Problem()
>>> AA = [picos.Constant('A[{0}]'.format(i), Ai)
...       for i, Ai in enumerate(A)] # each AA[i].T is a 3 x 5 observation matrix
>>> s  = len(AA)
>>> cc = picos.Constant('c', c)
>>> mu = picos.RealVariable('mu',s)
>>> # define the constraints and objective function
>>> lmi = c_primal_SDP.add_constraint(
...         picos.sum([mu[i] * AA[i] * AA[i].T for i in range(s)]) >> cc*cc.T)
>>> lin_cons = c_primal_SDP.add_constraint(mu >= 0)
>>> c_primal_SDP.set_objective('min', mu.sum)
>>> print(c_primal_SDP)
Semidefinite Program
  minimize ∑(mu)
  over
    8×1 real variable mu
  subject to
    ∑(mu[i]·A[i]·A[i]ᵀ : i ∈ [0…7]) ≽ c·cᵀ
    mu ≥ 0

>>> #solve the problem and retrieve the weights of the optimal design
>>> solution = c_primal_SDP.solve(solver='cvxopt')
>>> w = mu.value
>>> w = w / sum(w) #normalize mu to get the optimal weights

The optimal design is:

>>> print(w)# doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[...]
[...]
[...]
[...]
[ 1.28e-01]
[...]
[ 8.72e-01]
[...]

.. rubric:: Dual problem

This is only to check that we obtain the same solution with the dual problem,
and to provide one additional example in this tutorial:

.. math::
   :nowrap:

   \begin{center}
   \begin{eqnarray*}
   &\underset{X \in \mathbb{R}^{m \times m}}{\mbox{maximize}}
                      &  c^T X c\\
   &\mbox{subject to} & \forall i \in [s],\ \langle A_i A_i^T,\ X \rangle \leq 1,\\
   &                  &  X \succeq 0.
   \end{eqnarray*}
   \end{center}

>>> #create the problem, variables and params
>>> c_dual_SDP = picos.Problem()
>>> AA = [picos.Constant('A[{0}]'.format(i), Ai)
...       for i, Ai in enumerate(A)] # each AA[i].T is a 3 x 5 observation matrix
>>> s  = len(AA)
>>> cc = picos.Constant('c', c)
>>> m  = c.size[0]
>>> X  = picos.SymmetricVariable('X',(m,m))

>>> #define the constraints and objective function
>>> lin_cons = c_dual_SDP.add_list_of_constraints(
...                  [(AA[i]*AA[i].T | X) <= 1 for i in range(s)])
>>> psd = c_dual_SDP.add_constraint(X>>0)
>>> c_dual_SDP.set_objective('max', cc.T*X*cc)

>>> print(c_dual_SDP)
Semidefinite Program
  maximize cᵀ·X·c
  over
    5×5 symmetric variable X
  subject to
    ⟨A[i]·A[i]ᵀ, X⟩ ≤ 1 ∀ i ∈ [0…7]
    X ≽ 0

>>> # solve the problem and retrieve the weights of the optimal design
>>> solution = c_dual_SDP.solve(solver='cvxopt')
>>> mu = [cons.dual for cons in lin_cons] #Lagrangian duals of the linear constraints
>>> mu = cvx.matrix(mu)
>>> w = mu / sum(mu) #normalize mu to get the optimal weights

The optimal design is:

>>> print(w)# doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[...]
[...]
[...]
[...]
[ 1.28e-01]
[...]
[ 8.72e-01]
[...]

And the optimal positive semidefinite matrix X is:

>>> print(X)
[ 5.92e-03  8.98e-03  2.82e-03 -3.48e-02 -1.43e-02]
[ 8.98e-03  1.36e-02  4.27e-03 -5.28e-02 -2.17e-02]
[ 2.82e-03  4.27e-03  1.34e-03 -1.66e-02 -6.79e-03]
[-3.48e-02 -5.28e-02 -1.66e-02  2.05e-01  8.39e-02]
[-1.43e-02 -2.17e-02 -6.79e-03  8.39e-02  3.44e-02]

A-optimality (SOCP)
-------------------

We compute the A-optimal design
for the observation matrices ``A[i].T`` defined in the preambule.
The optimal design allocates
24.9% on design point #3,
14.2% on point #4,
8.51% on point #5,
12.1% on point #6,
13.2% on point #7,
and 27.0% on point #8.

.. rubric:: Primal problem

The SOCP for the A-optimal design problem is:

.. math::
   :nowrap:

   \begin{center}
   \begin{eqnarray*}
   &\underset{\substack{\mu \in \mathbb{R}^s\\
                        \forall i \in [s],\ Z_i \in \mathbb{R}^{l_i \times m}}}{\mbox{minimize}}
                      & \sum_{i=1}^s \mu_i\\
   &\mbox{subject to} & \sum_{i=1}^s A_i Z_i = I\\
   &                  & \forall i \in [s],\ \Vert Z_i \Vert_F \leq \mu_i,
   \end{eqnarray*}
   \end{center}

>>> # create the problem, variables and params
>>> A_primal_SOCP = picos.Problem()
>>> AA = [picos.Constant('A[{0}]'.format(i), Ai)
...       for i, Ai in enumerate(A)] # each AA[i].T is a 3 x 5 observation matrix
>>> s  = len(AA)
>>> Z = [picos.RealVariable('Z[{0}]'.format(i), AA[i].T.size) for i in range(s)]
>>> mu = picos.RealVariable('mu', s)

>>> #define the constraints and objective function
>>> cone_cons = A_primal_SOCP.add_list_of_constraints(
...                     [abs(Z[i]) <= mu[i] for i in range(s)])
>>> lin_cons = A_primal_SOCP.add_constraint(
...                      picos.sum([AA[i] * Z[i] for i in range(s)]) == 'I')
>>> A_primal_SOCP.set_objective('min', mu.sum)
>>> print(A_primal_SOCP)
Second Order Cone Program
  minimize ∑(mu)
  over
    3×5 real variable Z[i] ∀ i ∈ [0…7]
    8×1 real variable mu
  subject to
    ‖Z[i]‖ ≤ mu[i] ∀ i ∈ [0…7]
    ∑(A[i]·Z[i] : i ∈ [0…7]) = I

>>> # solve the problem and retrieve the weights of the optimal design
>>> solution = A_primal_SOCP.solve(solver='cvxopt')
>>> w = mu.value
>>> w = w / sum(w) #normalize mu to get the optimal weights

The optimal design is:

>>> print(w)# doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[...]
[...]
[ 2.49e-01]
[ 1.42e-01]
[ 8.51e-02]
[ 1.21e-01]
[ 1.32e-01]
[ 2.70e-01]

.. rubric:: Dual problem

This is only to check that we obtain the same solution with the dual problem,
and to provide one additional example in this tutorial:

.. math::
   :nowrap:

   \begin{center}
   \begin{eqnarray*}
   &\underset{U \in \mathbb{R}^{m \times m}}{\mbox{maximize}}
                      &  \mbox{trace}\ U\\
   &\mbox{subject to} & \forall i \in [s],\ \Vert A_i^T U \Vert_2 \leq 1
   \end{eqnarray*}
   \end{center}

>>> #create the problem, variables and params
>>> D_SOCPual_A=picos.Problem()
>>> AA = [picos.Constant('A[{0}]'.format(i), Ai)
...       for i, Ai in enumerate(A)] # each AA[i].T is a 3 x 5 observation matrix
>>> s  = len(AA)
>>> m  = AA[0].size[0]
>>> U  = picos.RealVariable('U',(m,m))
>>> #define the constraints and objective function
>>> cone_cons = D_SOCPual_A.add_list_of_constraints(
...       [abs(AA[i].T*U) <= 1 for i in range(s)])
>>> D_SOCPual_A.set_objective('max', U.tr)
>>> print(D_SOCPual_A)
Second Order Cone Program
  maximize tr(U)
  over
    5×5 real variable U
  subject to
    ‖A[i]ᵀ·U‖ ≤ 1 ∀ i ∈ [0…7]

>>> # solve the problem and retrieve the weights of the optimal design
>>> solution = D_SOCPual_A.solve(solver='cvxopt')
>>> mu = [cons.dual[0] for cons in cone_cons] # Lagrangian duals of the SOC constraints
>>> mu = cvx.matrix(mu)
>>> w = mu / sum(mu) # normalize mu to get the optimal weights

The optimal design is:

>>> print(w)# doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[...]
[...]
[ 2.49e-01]
[ 1.42e-01]
[ 8.51e-02]
[ 1.21e-01]
[ 1.32e-01]
[ 2.70e-01]

A-optimality with multiple constraints (SOCP)
---------------------------------------------

A-optimal designs can also be computed by SOCP
when the vector of weights :math:`\mathbf{w}` is subject
to several linear constraints.
To give an example, we compute the A-optimal design for
the observation matrices given in the preambule, when the weights
must satisfy: :math:`\sum_{i=0}^3 w_i \leq 0.5` and :math:`\sum_{i=4}^7 w_i \leq 0.5`.
This problem has the following SOCP formulation:

.. math::
   :nowrap:

   \begin{center}
   \begin{eqnarray*}
   &\underset{\substack{\mathbf{w} \in \mathbb{R}^s\\
                        \mu \in \mathbb{R}^s\\
                        \forall i \in [s],\ Z_i \in \mathbb{R}^{l_i \times m}}}{\mbox{minimize}}
                      & \sum_{i=1}^s \mu_i\\
   &\mbox{subject to} & \sum_{i=1}^s A_i Z_i = I\\
   &                  & \sum_{i=0}^3 w_i \leq 0.5\\
   &                  & \sum_{i=4}^7 w_i \leq 0.5\\
   &                  & \forall i \in [s],\ \Vert Z_i \Vert_F^2 \leq \mu_i w_i,
   \end{eqnarray*}
   \end{center}

The optimal solution allocates 29.7% and 20.3% to the design points #3 and #4,
and  respectively 6.54%, 11.9%, 9.02% and 22.5% to the design points #5 to #8:

>>> # create the problem, variables and params
>>> A_multiconstraints = picos.Problem()
>>> AA = [picos.Constant('A[{0}]'.format(i), Ai)
...       for i, Ai in enumerate(A)] # each AA[i].T is a 3 x 5 observation matrix
>>> s  = len(AA)
>>> mu = picos.RealVariable('mu',s)
>>> w  = picos.RealVariable('w',s)
>>> Z  = [picos.RealVariable('Z[{0}]'.format(i), AA[i].T.size)
...                          for i in range(s)]
>>> # define the constraints and objective function
>>> lin_cons0 = A_multiconstraints.add_constraint(
...         picos.sum([AA[i] * Z[i] for i in range(s)]) == 'I')
>>> lin_cons1 = A_multiconstraints.add_constraint(w[:4].sum <= 0.5)
>>> lin_cons2 = A_multiconstraints.add_constraint(w[4:].sum <= 0.5)
>>> cone_cons = A_multiconstraints.add_list_of_constraints(
...       [ abs(Z[i]) **2 <= mu[i] * w[i] for i in range(s)])
>>> A_multiconstraints.set_objective('min', mu.sum)
>>> print(A_multiconstraints)
Quadratically Constrained Program
  minimize ∑(mu)
  over
    3×5 real variable Z[i] ∀ i ∈ [0…7]
    8×1 real variables mu, w
  subject to
    ∑(A[i]·Z[i] : i ∈ [0…7]) = I
    ∑(w[:4]) ≤ 0.5
    ∑(w[4:]) ≤ 0.5
    ‖Z[i]‖² ≤ mu[i]·w[i] ∀ i ∈ [0…7]

>>> # solve the problem and retrieve the weights of the optimal design
>>> solution = A_multiconstraints.solve(solver='cvxopt')
>>> w = w.value
>>> w = w / sum(w) # normalize w to get the optimal weights

The optimal design is:

>>> print(w)# doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[...]
[...]
[ 2.97e-01]
[ 2.03e-01]
[ 6.54e-02]
[ 1.19e-01]
[ 9.02e-02]
[ 2.25e-01]


Exact A-optimal design (MISOCP)
-------------------------------

In the exact version of A-optimality, a number :math:`N \in \mathbb{N}`
of trials is given, and the goal is to find the optimal number of times
:math:`n_i \in \mathbb{N}` that a trial on design point #i should be performed,
with :math:`\sum_i n_i =N`.

The SOCP formulation of A-optimality for constrained designs
also accept integer constraints, which results in a MISOCP for exact A-optimality:

.. math::
   :nowrap:

   \begin{center}
   \begin{eqnarray*}
   &\underset{\substack{\mathbf{t} \in \mathbb{R}^s\\
                        \mathbf{n} \in \mathbb{N}^s\\
                        \forall i \in [s],\ Z_i \in \mathbb{R}^{l_i \times m}}}{\mbox{minimize}}
                      & \sum_{i=1}^s t_i\\
   &\mbox{subject to} & \sum_{i=1}^s A_i Z_i = I\\
   &                  & \forall i \in [s],\ \Vert Z_i \Vert_F^2 \leq n_i t_i,\\
   &                  & \sum_{i=1}^s n_i = N.
   \end{eqnarray*}
   \end{center}

The exact optimal design is :math:`\mathbf{n}=[0,0,5,3,2,2,3,5]`:

>>> # create the problem, variables and params
>>> A_exact = picos.Problem()
>>> AA = [picos.Constant('A[{0}]'.format(i), Ai)
...       for i, Ai in enumerate(A)] # each AA[i].T is a 3 x 5 observation matrix
>>> s  = len(AA)
>>> m  = AA[0].size[0]
>>> N  = picos.Constant('N', 20) # number of trials allowed
>>> I = picos.Constant('I', cvx.spmatrix([1]*m,range(m),range(m),(m,m))) #identity matrix
>>> Z = [picos.RealVariable('Z[{0}]'.format(i), AA[i].T.size) for i in range(s)]
>>> n = picos.IntegerVariable('n', s)
>>> t = picos.RealVariable('t', s)

>>> # define the constraints and objective function
>>> cone_cons = A_exact.add_list_of_constraints(
...         [ abs(Z[i])**2 <= n[i] * t[i] for i in range(s)])
>>> lin_cons = A_exact.add_constraint(
...          picos.sum([AA[i]*Z[i] for i in range(s)]) == I)
>>> wgt_cons = A_exact.add_constraint(n.sum <= N)
>>> A_exact.set_objective('min', t.sum)
>>> print(A_exact)
Mixed-Integer Quadratically Constrained Program
  minimize ∑(t)
  over
    8×1 integer variable n
    3×5 real variable Z[i] ∀ i ∈ [0…7]
    8×1 real variable t
  subject to
    ‖Z[i]‖² ≤ n[i]·t[i] ∀ i ∈ [0…7]
    ∑(A[i]·Z[i] : i ∈ [0…7]) = I
    ∑(n) ≤ N

>>> #solve the problem and display the optimal design
>>> solution = A_exact.solve()# doctest:+SKIP
>>> print(n)# doctest:+SKIP
[...]
[...]
[ 5.00e+00]
[ 3.00e+00]
[ 2.00e+00]
[ 2.00e+00]
[ 3.00e+00]
[ 5.00e+00]

.. note::

    The above output is not validated as we lack an appropriate solver on
    the build server.

Approximate and exact D-optimal design ((MI)SOCP)
-------------------------------------------------

The D-optimal design problem has a SOCP formulation involving a
geometric mean in the objective function:

.. math::
   :nowrap:

   \begin{center}
   \begin{eqnarray*}
   &\underset{\substack{\mathbf{L} \in \mathbb{R}^{m \times m}\\
                        \mathbf{w} \in \mathbb{R}^s\\
                        \forall i \in [s],\ V_i \in \mathbb{R}^{l_i \times m}}}{\mbox{maximize}}
                      & \left(\prod_{i=1}^m L_{i,i}\right)^{1/m}\\
   &\mbox{subject to} & \sum_{i=1}^s A_i V_i = L,\\
   &                  & L\ \mbox{lower triangular},\\
   &                  & \Vert V_i \Vert_F \leq \sqrt{m}\ w_i,\\
   &                  & \sum_{i=1}^s w_i \leq 1.
   \end{eqnarray*}
   \end{center}

By introducing a new variable :math:`t` such that
:math:`t \leq \left(\prod_{i=1}^m L_{i,i}\right)^{1/m}`, we can pass
this problem to PICOS with the function :func:`~picos.geomean`,
which reformulates the geometric mean inequality as a set of equivalent second order cone
constraints.
The example below allocates respectively 22.7%, 3.38%, 1.65%, 5.44%, 31.8% and 35.1%
to the design points #3 to #8.

>>> #create the problem, variables and params
>>> D_SOCP = picos.Problem()
>>> AA = [picos.Constant('A[{0}]'.format(i), Ai)
...       for i, Ai in enumerate(A)] # each AA[i].T is a 3 x 5 observation matrix
>>> s  = len(AA)
>>> m  = AA[0].size[0]
>>> mm = picos.Constant('m', m)
>>> L = picos.RealVariable('L', (m,m))
>>> V = [picos.RealVariable('V['+str(i)+']', AA[i].T.size) for i in range(s)]
>>> w = picos.RealVariable('w',s)
>>> # additional variable to handle the geometric mean in the objective function
>>> t = picos.RealVariable('t',1)

>>> # define the constraints and objective function
>>> lin_cons = D_SOCP.add_constraint(picos.sum([AA[i]*V[i] for i in range(s)]) == L)
>>> # L is lower triangular
>>> lowtri_cons = D_SOCP.add_list_of_constraints([L[i,j] == 0
...                for i in range(m)
...                for j in range(i+1,m)])
>>> cone_cons = D_SOCP.add_list_of_constraints([abs(V[i]) <= (mm**0.5)*w[i]
...                                                 for i in range(s)])
>>> wgt_cons = D_SOCP.add_constraint(w.sum <= 1)
>>> geomean_cons = D_SOCP.add_constraint(t <= picos.geomean(picos.maindiag(L)))
>>> D_SOCP.set_objective('max',t)

>>> #solve the problem and display the optimal design
>>> print(D_SOCP)
Optimization Problem
  maximize t
  over
    1×1 real variable t
    3×5 real variable V[i] ∀ i ∈ [0…7]
    5×5 real variable L
    8×1 real variable w
  subject to
    L = ∑(A[i]·V[i] : i ∈ [0…7])
    L[i,j] = 0 ∀ (i,j) ∈ zip([0,0,…,2,3],[1,2,…,4,4])
    ‖V[i]‖ ≤ m^(1/2)·w[i] ∀ i ∈ [0…7]
    ∑(w) ≤ 1
    geomean(maindiag(L)) ≥ t

>>> solution = D_SOCP.solve(solver='cvxopt')
>>> print(w)# doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[...]
[...]
[ 2.27e-01]
[ 3.38e-02]
[ 1.65e-02]
[ 5.44e-02]
[ 3.18e-01]
[ 3.51e-01]


As for the A-optimal problem, there is an alternative SOCP formulation
of D-optimality :ref:`[2] <optdes_refs>`, in which integer constraints may be added.
This allows us to formulate the exact D-optimal problem as a MISOCP.
For :math:`N=20`,
we obtain the following N-exact D-optimal design:
:math:`\mathbf{n}=[0,0,5,1,0,1,6,7]`:

>>> # create the problem, variables and params
>>> D_exact = picos.Problem()
>>> L = picos.RealVariable('L',(m,m))
>>> V = [picos.RealVariable('V['+str(i)+']',AA[i].T.size) for i in range(s)]
>>> T = picos.RealVariable('T', (s,m))
>>> n = picos.IntegerVariable('n', s)
>>> N = picos.Constant('N', 20)
>>> # additional variable to handle the geomean inequality
>>> t = picos.RealVariable('t',1)

>>> # define the constraints and objective function
>>> lin_cons = D_exact.add_constraint(
...         picos.sum([AA[i]*V[i] for i in range(s)]) == L)
>>> # L is lower triangular
>>> lowtri_cons = D_exact.add_list_of_constraints([L[i,j] == 0
...                                  for i in range(m)
...                                  for j in range(i+1,m)])
>>> cone_cons = D_exact.add_list_of_constraints([ abs(V[i][:,k])**2 <= n[i]/N*T[i,k]
...                 for i in range(s) for k in range(m)])
>>> lin_cons2 = D_exact.add_list_of_constraints([T[:,k].sum <= 1
...                       for k in range(m)])
>>> wgt_cons = D_exact.add_constraint(n.sum <= N)
>>> geomean_cons = D_exact.add_constraint(t <= picos.geomean(picos.maindiag(L)))
>>> D_exact.set_objective('max',t)
>>> print(D_exact)
Mixed-Integer Optimization Problem
  maximize t
  over
    8×1 integer variable n
    1×1 real variable t
    3×5 real variable V[i] ∀ i ∈ [0…7]
    5×5 real variable L
    8×5 real variable T
  subject to
    L = ∑(A[i]·V[i] : i ∈ [0…7])
    L[i,j] = 0 ∀ (i,j) ∈ zip([0,0,…,2,3],[1,2,…,4,4])
    ‖V[i][:,j]‖² ≤ n[i]/N·T[i,j] ∀ (i,j) ∈
      zip([0,0,…,7,7],[0,1,…,3,4])
    ∑(T[:,i]) ≤ 1 ∀ i ∈ [0…4]
    ∑(n) ≤ N
    geomean(maindiag(L)) ≥ t

>>> #solve the problem and display the optimal design
>>> solution = D_exact.solve()# doctest:+SKIP
>>> print(n)# doctest:+SKIP
[...]
[...]
[ 5.00e+00]
[ 1.00e+00]
[...]
[ 1.00e+00]
[ 6.00e+00]
[ 7.00e+00]

.. note::

    The above output is not validated as we lack an appropriate solver on
    the build server.

Former MAXDET formulation of the D-optimal design (SDP)
-------------------------------------------------------

A so-called MAXDET Programming formulation of the D-optimal design
has been known since the late 90's :ref:`[3] <optdes_refs>`, and
can be reformulated as a SDP thanks to the :func:`~picos.detrootn` function.
The following code finds the same design as the SOCP approach presented above.

>>> # problem, variables and parameters
>>> D_MAXDET = picos.Problem()
>>> AA = [picos.Constant('A[{0}]'.format(i), Ai)
...       for i, Ai in enumerate(A)] # each AA[i].T is a 3 x 5 observation matrix
>>> s  = len(AA)
>>> m  = AA[0].size[0]
>>> w = picos.RealVariable('w', s, lower=0)
>>> t = picos.RealVariable('t', 1)
>>> # constraint and objective
>>> wgt_cons = D_MAXDET.add_constraint(w.sum <= 1)
>>> Mw = picos.sum([w[i] * AA[i] * AA[i].T for i in range(s)])
>>> detrootn_cons = D_MAXDET.add_constraint(t <= picos.DetRootN(Mw))
>>> D_MAXDET.set_objective('max', t)

>>> print(D_MAXDET)
Optimization Problem
  maximize t
  over
    1×1 real variable t
    8×1 real variable w (bounded below)
  subject to
    ∑(w) ≤ 1
    det(∑(w[i]·A[i]·A[i]ᵀ : i ∈ [0…7]))^(1/5) ≥ t

>>> #solve and display
>>> solution = D_MAXDET.solve(solver='cvxopt')
>>> print(w)# doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[ ...]
[ ...]
[ 2.27e-01]
[ 3.38e-02]
[ 1.65e-02]
[ 5.44e-02]
[ 3.18e-01]
[ 3.51e-01]



General Phi_p optimal design (SDP)
----------------------------------

The A- and D-optimal design problems presented above can be obtained as special cases of the general
Kiefer :math:`\Phi_p-` optimal design problem, where :math:`p` is a real in :math:`(-\infty,1]` :

.. math::
   :nowrap:

   \begin{center}
   \begin{eqnarray*}
   &\underset{w \in \mathbb{R}^s}{\mbox{maximize}}
                      &\quad \left( \frac{1}{m} \operatorname{trace}\ \big(\sum_{i=1}^s w_i A_i A_i^T \big)^p \right)^{1/p} \\
   &\textrm{subject to} &\quad w\geq0,\ \sum_{i=1}^s w_i \leq 1.
   \end{eqnarray*}

   \end{center}

These problems are easy to enter in PICOS, thanks to the :func:`~picos.tracepow` function,
that automatically replaces inequalities involving trace of matrix powers as a set of equivalent linear matrix
inequalities (SDP) (cf. :ref:`[4] <optdes_refs>`). Below are two examples with :math:`p=0.2` and :math:`p=-3`,
allocating respectively (20.6%, 0.0%, 0.0%, 0.92%, 40.8%, 37.7%), and
(24.8%, 16.6%, 10.8%, 14.1%, 7.84%, 26.0%) of the trials to the design points 3 to 8.

>>> #problems, variables and parameters
>>> P0dot2_SDP  = picos.Problem()
>>> Pminus3_SDP = picos.Problem()
>>> AA = [picos.Constant('A[{0}]'.format(i), Ai)
...       for i, Ai in enumerate(A)] # each AA[i].T is a 3 x 5 observation matrix
>>> s  = len(AA)
>>> m  = AA[0].size[0]
>>> w = picos.RealVariable('w', s, lower=0)
>>> t = picos.RealVariable('t', 1)

>>> # constraint and objective
>>> wgt02_cons = P0dot2_SDP.add_constraint(w.sum <= 1)
>>> wgtm3_cons = Pminus3_SDP.add_constraint(w.sum <= 1)

>>> Mw = picos.sum([w[i]*AA[i]*AA[i].T for i in range(s)])

>>> tracep02_cons = P0dot2_SDP.add_constraint(t <= picos.PowerTrace(Mw, 0.2))
>>> P0dot2_SDP.set_objective('max', t)

>>> tracepm3_cons = Pminus3_SDP.add_constraint(t >= picos.PowerTrace(Mw, -3))
>>> Pminus3_SDP.set_objective('min', t)

>>> # p=0.2
>>> print(P0dot2_SDP)
Optimization Problem
  maximize t
  over
    1×1 real variable t
    8×1 real variable w (bounded below)
  subject to
    ∑(w) ≤ 1
    tr(∑(w[i]·A[i]·A[i]ᵀ : i ∈ [0…7])^(1/5)) ≥ t

>>> #solve and display
>>> solution = P0dot2_SDP.solve(solver='cvxopt')
>>> print(w)# doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[ ...]
[ ...]
[ 2.06e-01]
[ ...]
[ ...]
[ 9.20e-03]
[ 4.08e-01]
[ 3.77e-01]

>>> # p=-3
>>> print(Pminus3_SDP)
Optimization Problem
  minimize t
  over
    1×1 real variable t
    8×1 real variable w (bounded below)
  subject to
    ∑(w) ≤ 1
    tr(∑(w[i]·A[i]·A[i]ᵀ : i ∈ [0…7])^(-3)) ≤ t
>>> solution = Pminus3_SDP.solve(solver='cvxopt')
>>> print(w)# doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
[ ...]
[ ...]
[ 2.48e-01]
[ 1.66e-01]
[ 1.08e-01]
[ 1.41e-01]
[ 7.83e-02]
[ 2.60e-01]

.. _optdes_refs:

References
----------

        1. "`Computing Optimal Designs of multiresponse Experiments reduces to
           Second-Order Cone Programming <http://arxiv.org/abs/0912.5467>`_", G. Sagnol,
           *Journal of Statistical Planning and Inference*,
           141(5), p. *1684-1708*, 2011.

        2. "`Computing exact D-optimal designs by mixed integer second order cone
           programming <http://arxiv.org/abs/1307.4953>`_",
           G. Sagnol and R. Harman, Submitted: arXiv:1307.4953.

        3. "`Determinant maximization with linear matrix inequality
           constraints <http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.38.7483&rep=rep1&type=pdf>`_",
           L. Vandenberghe, S. Boyd and S.P. Wu, *SIAM journal on matrix analysis and applications*,
           19(2), 499-533, 1998.

        4. "`On the semidefinite representations of real functions applied to symmetric
           matrices <http://opus4.kobv.de/opus4-zib/frontdoor/index/index/docId/1751>`_", G. Sagnol,
           *Linear Algebra and its Applications*,
           439(10), p. *2829-2843*, 2013.
