.. _duals:

Dual Values
===========

Picos typically reformulates optimization problems as
conic programs of the form

.. math::
   :nowrap:

   \begin{center}
   $\begin{array}{cclc}
   \underset{\mathbf{x} \in \mathbb{R}^n}{\mbox{minimize}}
                      & \mathbf{c}^T \mathbf{x} + \gamma & &\\
   \mbox{subject to} & A_i(\mathbf{x}) & \succeq_{K_i} \mathbf{b}_i,\ \forall i \in I,
   \end{array}$
   \end{center}

where each :math:`A_i` is a linear map from :math:`\mathbb{R}^n` to a linear
space containing the cone :math:`K_i`, and the generalized conic inequality
:math:`\mathbf{x} \succeq_K \mathbf{y}` means :math:`\mathbf{x}-\mathbf{y}\in K`
for a cone :math:`K`. For the sake of compactness, we allow generalized
inequalities over the trivial cone :math:`K_{eq} = \{\mathbf{0}\}`, such that
:math:`A \mathbf{x} \succeq_{K_{eq}} \mathbf{b}` represents an equality
constraint :math:`A \mathbf{x} = \mathbf{b}`.


The dual conic problem can be written as follows:

.. math::
   :nowrap:

   \begin{center}
   $\begin{array}{cll}
   \mbox{maximize}   & \sum_{i\in I} \mathbf{b}_i^T \mathbf{y}_i + \gamma \\
   \mbox{subject to} & \sum_{i\in I} A_i^*(\mathbf{y}_i) = \mathbf{c}, \\
                     & \mathbf{y}_i \succeq_{K_i^*} 0,\ \forall i \in I,
   \end{array}$
   \end{center}

where :math:`A^*` denotes the adjoint operator of :math:`A` and :math:`K^*`
denotes the the dual cone of :math:`K` (see the note below for a list of cones
that are supported in PICOS, together with their dual).

After an optimization problem has been solved, we can query the optimal dual
variable :math:`y_i \in K_i^*` of a conic constraint ``con`` over the cone
:math:`K_i` with its :attr:`~.constraint.Constraint.dual` attribute, i.e.,
``con.dual``.

When an optimization problem ``P`` can be reformulated to a conic program ``C``
of the above form by PICOS, we can use its :meth:`~.problem.Problem.dual`
attribute to return a :class:`~.problem.Problem` object ``D=P.dual`` which
contains the dual conic program of ``C``. It is also possible to solve ``P`` via
its dual by using the :ref:`dualize <option_dualize>` option: This passes
problem ``D`` to the solver, and the optimal primal and dual variables of ``P``
will be retrieved from the optimal solution of ``D``.


Supported cones and their dual
------------------------------

PICOS can provide dual information for problems involving the following cones:


.. rubric:: Trivial cone

The trivial cone :math:`K_{eq} = \{\mathbf{0}\}\subset \mathbb{R}^n`,
whose dual cone is the entire space :math:`K_{eq}^* = \mathbb{R}^n`.
This means that the dual variable :math:`\mathbf{y}` for an equality constraint
is unconstrained.

.. rubric:: Nonnegative Orthant

The nonnegative orthant :math:`\mathbb{R}_+^n` is self dual:
:math:`(\mathbb{R}_+^n)^* = \mathbb{R}_+^n`. Therefore the dual variable for a
set of linear inequalities is a vector :math:`\mathbf{y}\geq\mathbf{0}`.

.. rubric:: Lorentz Cone

The :ref:`Lorentz cone <lorentz>` :math:`\mathcal{Q}^n=` :math:`\{(t,\mathbf{x})
\in \mathbb{R}\times \mathbb{R}^{n-1}: \|\mathbf{x}\| \leq t \}`, which is used
to model second-order cone inequalities, is self-dual: :math:`(\mathcal{Q}^n)^*
= \mathcal{Q}^n`. This means that the dual variable for a second order cone
inequality of the form

.. math::
    :nowrap:

    $\| A \mathbf{x} - \mathbf{b} \| \leq \mathbf{h}^T \mathbf{x} - g
    \iff
    \left[
        \begin{array}{c} \mathbf{h}^T\\ A \end{array}
    \right] \mathbf{x}
    \succeq_{\mathcal{Q}^n}
    \left[
        \begin{array}{c} g\\ \mathbf{b} \end{array}
    \right]$

is a vector of the form :math:`[\lambda, \mathbf{z}^T]^T` such that
:math:`\|\mathbf{z}\| \leq \lambda`.

.. rubric:: Rotated Second-order Cone

The (widened or narrowed) :ref:`rotated second order cone <rotatedcone>` is

.. math::
    :nowrap:

    $\mathcal{R}_p^n =\{(u,v,\mathbf{x})\in\mathbb{R}\times\mathbb{R}\times\mathbb{R}^{n-2}:
    \|\mathbf{x}\|^2 \leq p\cdot u \cdot v,\ u,v\geq 0 \}$

for some :math:`p>0`, and its dual cone is :math:`(\mathcal{R}_{p}^n)^* =
\mathcal{R}_{4/p}^n`. In particular, :math:`\mathcal{R}_p^n` is self-dual for
:math:`p=2`. For example, the dual variable for the constraint :math:`\| A
\mathbf{x} - \mathbf{b} \|^2 \leq (\mathbf{h}^T \mathbf{x} - g)(\mathbf{e}^T
\mathbf{x} - f)` with :math:`(\mathbf{h}^T \mathbf{x} - g)\geq 0` and
:math:`(\mathbf{e}^T \mathbf{x} - f)\geq 0`, i.e.,

.. math::
    :nowrap:

    $
    \left[
        \begin{array}{c} \mathbf{h}^T\\ \mathbf{e}^T\\ A \end{array}
    \right] \mathbf{x}
    \succeq_{\mathcal{R}_1^n}
    \left[
        \begin{array}{c} g\\ f\\ \mathbf{b} \end{array}
    \right]$

is a vector of the form :math:`[\alpha, \beta, \mathbf{z}^T]^T` such that
:math:`\|\mathbf{z}\|^2 \leq 4 \alpha \beta`;

.. rubric:: Positive Semi-definite Cone

The positive semidefinite cone :math:`\mathbb{S}_+^n` is self dual:
:math:`(\mathbb{S}_+^n)^* = \mathbb{S}_+^n`. This means that the dual variable
for a linear matrix inequality :math:`\sum_i x_i M_i \succeq M_0` is a positive
semidefinite matrix :math:`Y \succeq 0`;

.. rubric:: Exponential Cone

PICOS can also reformulate several constraints using the *exponential cone*
:class:`~picos.expressions.ExponentialCone`, as it is the case for example for
:class:`~picos.constraints.KullbackLeiblerConstraint`. PICOS provides dual
values for :class:`~picos.constraints.ExpConeConstraint`, as computed by the
solver, but dualization of those constraints is not yet supported.
