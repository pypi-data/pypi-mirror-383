.. _welcome:

.. include:: badges.rst

A Python interface to conic optimization solvers
================================================

|gitlab| • |pypi| |anaconda| |aur| • |license| |cov|

Welcome to the documentation of PICOS, a powerful and user friendly Python API
for convex and mixed integer optimization that dispatches your problem to the
best fit solver that is available at runtime. A `PDF version <picos.pdf>`_ of
this documentation is available for offline use. Here's a quick example:

>>> import picos as pc
>>> x = pc.RealVariable("x", 5)
>>> a = pc.Constant("a", range(5))
>>> P = pc.Problem()
>>> P.minimize = abs(x - a)                            # abs() - Euclidean norm
>>> P += pc.sum(x) == 1                                # Add a constraint
>>> opt = P.solve(solver="cvxopt")                     # Optional: Solver choice
>>> print(x.T)                                         # .T - Transpose
[-1.80e+00 -8.00e-01  2.00e-01  1.20e+00  2.20e+00]
>>> round(P.value, 3)
4.025

.. _quickstart:

Quickstart guide
----------------

- If you are **new to PICOS**, head to the :ref:`introduction
  <introduction>`, the :ref:`tutorial <tutorial>`, or see our :ref:`examples
  <examples>`.
- As an **experienced user**, check out the :ref:`changelog <changelog>` or dive
  into the :ref:`API documentation <api>`.
- If you want to report a **bug** or **contribute to PICOS**, the
  :ref:`contribution guide <contributing>` has you covered.
- If you still have a **question**, we're happy to receive
  `your mail <incoming+picos-api/picos@incoming.gitlab.com>`_!


.. _contents:

Documentation outline
---------------------

.. toctree::
   :maxdepth: 1

   Introduction <introduction>
   tutorial
   examples
   PICOS for QIS <qis>
   notes
   api
   changelog
   contributing
