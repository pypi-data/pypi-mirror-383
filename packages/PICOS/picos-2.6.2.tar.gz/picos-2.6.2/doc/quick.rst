.. _quick_examples:

Quick examples
==============

The short examples below are all self-contained and can be copied to a Python
source file or pasted into a Python console.


Projection onto a convex hull
-----------------------------

We solve the problem

.. math::

  \underset{x \in \mathbb{R}^n}{\text{minimize}}\quad&\lVert Ax - b \rVert \\
  \text{subject to}\quad&\sum_{i=1}^n x_i = 1, \\
  &x \succeq 0,

which asks for the projection :math:`Ax` of the point :math:`b \in \mathbb{R}^m`
onto the convex hull of the columns of :math:`A \in \mathbb{R}^{m \times n}`:

.. plot::
  :include-source:

  #!/usr/bin/env python3

  import numpy as np
  import picos as pc
  from matplotlib import pyplot
  from scipy import spatial

  # Make the result reproducible.
  np.random.seed(12)

  # Define the data.
  n = 20
  A = np.random.rand(2, n)
  b = np.array([1, 0])

  # Define the decision variable.
  x = pc.RealVariable("x", n)

  # Define and solve the problem.
  P = pc.Problem()
  P.minimize = abs(A*x - b)
  P += pc.sum(x) == 1, x >= 0
  P.solve(solver="cvxopt")

  # Obtain the projection point.
  p = (A*x).np

  # Plot the results.
  V = spatial.ConvexHull(A.T).vertices
  figure = pyplot.figure(figsize=(8.7, 4))
  figure.gca().set_aspect("equal")
  pyplot.axis("off")
  pyplot.fill(A.T[V, 0], A.T[V, 1], "lightgray")
  pyplot.plot(A.T[:, 0], A.T[:, 1], "k.")
  pyplot.plot(*zip(b, p), "k.--")
  pyplot.annotate("$\mathrm{conv} \{a_1, \ldots, a_n\}$", [0.25, 0.5])
  pyplot.annotate("$b$", b + 1/100)
  pyplot.annotate("$Ax$", p + 1/100)
  pyplot.tight_layout()
  pyplot.show()

.. rubric:: Example notes

- The Python builtin function :func:`abs` (absolute value) is understood as the
  default norm. For real vectors, this is the Euclidean norm.
- The attribute :attr:`~picos.valuable.Valuable.np` returns the value of a PICOS
  expression as a NumPy type.
- The choice of the CVXOPT solver is optional. Explicit solver choice is made
  throughout the documentation to make its automatic validation more reliable.


Worst-case projection
---------------------

We solve the same problem as before but now we assume that the point :math:`b`
to be projected is only known to live inside an ellipsoid around its original
location. In this case we cannot hope to obtain an exact projection but we may
compute a point :math:`p` on the convex hull of the columns of :math:`A` that
minimizes the worst-case distance to :math:`b`. This approach is known as
`robust optimization <https://en.wikipedia.org/wiki/Robust_optimization>`_.
Formally, we solve the min-max problem

.. math::

  \underset{x \in \mathbb{R}^n}{\text{minimize}}\quad&\max_{\theta \in
    \Theta}~\lVert Ax - (b + \theta) \rVert \\
  \text{subject to}\quad&\sum_{i=1}^n x_i = 1, \\
  &x \succeq 0, \\

where :math:`\Theta = \{\theta \mid L\theta \leq 1\}` is an ellipsoidal
*perturbation set* (for some invertible matrix :math:`L`):

.. plot::
  :include-source:

  #!/usr/bin/env python3

  import numpy as np
  import picos as pc
  from matplotlib import pyplot
  from matplotlib.patches import Ellipse
  from scipy import spatial

  # Make the result reproducible.
  np.random.seed(12)

  # Define the data.
  n = 20
  A = np.random.rand(2, n)
  b = np.array([1, 0])

  # Define an ellipsoidal uncertainty set Θ and a perturbation parameter θ.
  # The perturbation is later added to the data, rendering it uncertain.
  Theta = pc.uncertain.ConicPerturbationSet("θ", 2)
  Theta.bound(  # Let ‖Lθ‖ ≤ 1.
    abs([[ 5,  0],
         [ 0, 10]] * Theta.element) <= 1
  )
  theta = Theta.compile()

  # Define the decision variable.
  x = pc.RealVariable("x", n)

  # Define and solve the problem.
  P = pc.Problem()
  P.minimize = abs(A*x - (b + theta))
  P += pc.sum(x) == 1, x >= 0
  P.solve(solver="cvxopt")

  # Obtain the projection point.
  p = (A*x).np

  # Plot the results.
  V = spatial.ConvexHull(A.T).vertices
  E = Ellipse(b, 0.4, 0.2, color="lightgray", ec="k", ls="--")
  figure = pyplot.figure(figsize=(8.7, 4))
  axis = figure.gca()
  axis.add_artist(E)
  axis.set_aspect("equal")
  axis.set_xlim(0.5, 1.21)
  axis.set_ylim(-0.11, 0.5)
  pyplot.axis("off")
  pyplot.fill(A.T[V, 0], A.T[V, 1], "lightgray")
  pyplot.plot(A.T[:, 0], A.T[:, 1], "k.")
  pyplot.plot(*zip(b, p), "k.")
  pyplot.annotate("$\mathrm{conv} \{a_1, \ldots, a_n\}$", [0.25, 0.5])
  pyplot.annotate("$b$", b + 1/200)
  pyplot.annotate("$Ax$", p + 1/200)
  pyplot.tight_layout()
  pyplot.show()

.. rubric:: Example notes

- One can also scale and shift the parameter obtained from a
  :class:`~picos.uncertain.UnitBallPerturbationSet` to obtain ellipsoidal
  uncertainty. Its parent class :class:`~picos.uncertain.ConicPerturbationSet`
  that we showcased is more versatile and can represent any conically bounded
  perturbation set through repeated use of its
  :meth:`~picos.expressions.uncertain.pert_conic.ConicPerturbationSet.bound`
  method.
- A report of the robust and distributionally robust optimization models
  supported by PICOS and their mathematical background is found in
  :ref:`[1] <quick_refs>`.


Optimal Minecraft mob farm
--------------------------

Minecraft is a popular sandbox video game in which some players aim to build
efficient automated factories, referred to as *farms*. One type of farm waits
for hostile creatures (*mobs*) to appear on a platform, then pushes them off the
platform with a water dispenser in the center to collect any valuables that they
might carry. Such a farm is threatened by the possibility of Spiders to appear,
which are too large for the collection mechanism to handle. Fortunately, the
Spider requires a :math:`3 \times 3` area to spawn on while the other mobs
require just a single free :math:`1 \times 1` cell, so Spider spawns can be
prevented by blocking off some of the platform's cells.

In the following we compute an optimal platform that maximizes the number of
cells that mobs can spawn on while admitting no :math:`3 \times 3` spawnable
region for Spiders. We further compute an optimal highly symmetric (w.r.t. both
axes and diagonals) solution for those who value looks over efficiency:

.. plot::
  :include-source:

  #!/usr/bin/env python3

  import picos as pc
  from matplotlib import colors, pyplot

  # Represent the spawning platform by a 15×15 binary matrix variable S where a
  # one represents a spawnable field and a zero one that is not spawnable.
  S = pc.BinaryVariable("S", (15, 15))

  # Maximize the number of spawnable blocks.
  P = pc.Problem("Optimal Mob Farm")
  P.maximize = pc.sum(S)

  # The actual platform is shaped like a diamond of cells with taxicab distance
  # of at most seven from the center block. Mark all other cells not spawnable.
  P += [
      S[x, y] == 0
      for x in range(S.shape[0])
      for y in range(S.shape[1])
      if abs(x - 7) + abs(y - 7) > 7
  ]

  # The center block is not spawnable due to the water dispenser.
  P += S[7, 7] == 0

  # Additionally, we require that there is no 3x3 spawnable area.
  P += [
      sum([
          S[a, b]
          for a in range(x - 1, x + 2)
          for b in range(y - 1, y + 2)
      ]) <= 8
      for x in range(1, S.shape[0] - 1)
      for y in range(1, S.shape[1] - 1)
  ]

  # Solve the problem and store the optimal platform.
  P.solve(solver="glpk")
  S_opt = S.np

  # Now modify the problem to require a more symmetric solution.
  P += [S[x, :] == S[14 - x, :] for x in range(S.shape[0] // 2)]  # Vertical.
  P += S == S.T  # Diagonal.

  # Re-solve the updated problem.
  P.solve()
  S_sym = S.np

  # Display both solutions.
  figure, axes = pyplot.subplots(ncols=2, figsize=(8.7, 5))
  titles = ["An optimal platform", "An optimal symmetric platform"]
  cmap = colors.ListedColormap(["#1c1c1c", "#78ae00", "#d35e1a"])

  for axis, title, solution in zip(axes, titles, [S_opt, S_sym]):
    solution[7, 7] = 2  # Mark the center.
    axis.axis("off")
    axis.set_title(title)
    axis.pcolormesh(solution, edgecolor="#2f2f2f", linewidth=0.5, cmap=cmap)

  pyplot.tight_layout()
  pyplot.show()

.. rubric:: Example notes

- Excluding the center, the platform has 112 cells. The solutions show that an
  optimal platform has 9 obstacles and 103 free cells (92.0%) while an optimal
  symmetric platform has 12 obstacles and thus only 100 free cells (89.3%).
- The two symmetry conditions require symmetry along one axis and one main
  diagonal, respectively. Symmetry along the remaining axis and diagonal is
  obtained implicitly. With an adjustment it can be seen that only requiring
  axial symmetry does not increase efficiency.


.. _quick_refs:

References
----------

  1. "`Robust conic optimization in Python
     <https://www.static.tu.berlin/fileadmin/www/10005693/Publications/Stahlberg20.pdf>`_",
     M. Stahlberg, Master's thesis, 2020.
