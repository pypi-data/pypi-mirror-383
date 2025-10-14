Changelog
=========

This file documents major changes to PICOS. The format is based on
`Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_.

.. _2.6: https://gitlab.com/picos-api/picos/compare/v2.5...v2.6
.. _2.5: https://gitlab.com/picos-api/picos/compare/v2.4...v2.5
.. _2.4: https://gitlab.com/picos-api/picos/compare/v2.3...v2.4
.. _2.3: https://gitlab.com/picos-api/picos/compare/v2.2...v2.3
.. _2.2: https://gitlab.com/picos-api/picos/compare/v2.1...v2.2
.. _2.1: https://gitlab.com/picos-api/picos/compare/v2.0...v2.1
.. _2.0: https://gitlab.com/picos-api/picos/compare/v1.2.0...v2.0
.. _1.2.0: https://gitlab.com/picos-api/picos/compare/v1.1.3...v1.2.0
.. _1.1.3: https://gitlab.com/picos-api/picos/compare/v1.1.2...v1.1.3
.. _1.1.2: https://gitlab.com/picos-api/picos/compare/v1.1.1...v1.1.2
.. _1.1.1: https://gitlab.com/picos-api/picos/compare/v1.1.0...v1.1.1
.. _1.1.0: https://gitlab.com/picos-api/picos/compare/v1.0.2...v1.1.0
.. _1.0.2: https://gitlab.com/picos-api/picos/compare/v1.0.1...v1.0.2
.. _1.0.1: https://gitlab.com/picos-api/picos/compare/v1.0.0...v1.0.1
.. _1.0.0: https://gitlab.com/picos-api/picos/compare/b65a05be...v1.0.0
.. _0.1.3: about:blank
.. _0.1.2: about:blank
.. _0.1.1: about:blank
.. _0.1.0: about:blank


`2.6`_ - 2025-02-08
--------------------------------------------------------------------------------

.. rubric:: Added

- Support for additional entropies:

  - Rényi entropy
    (:func:`picos.renyientr <picos.expressions.algebra.renyientr>`),
  - sandwiched Rényi entropy
    (:func:`picos.sandrenyientr <picos.expressions.algebra.sandrenyientr>`),
  - quasi-relative entropy
    (:func:`picos.quasientr <picos.expressions.algebra.quasientr>`), and
  - sandwiched quasi-relative entropy
    (:func:`picos.sandquasientr <picos.expressions.algebra.sandquasientr>`).

- Support for MOSEK 11 (which renamed ``setdefaults`` to ``resetparameters``).


`2.5`_ - 2024-10-20
--------------------------------------------------------------------------------

*The quantum relative entropy update.*

.. rubric:: Important

- The :meth:`complex inner product <.exp_biaffine.BiaffineExpression.__or__>`
  now follows the physics convention of conjugate linearity in the first and
  linearity in the second argument. Thus ``(A | B)`` now represents
  :math:`\langle A \mid B \rangle = \operatorname{Tr}(A^\dagger B)`
  instead of :math:`\operatorname{Tr}(B^\dagger A)`. The change amounts to
  taking the complex conjugate of the result and only affects complex operands
  which are not both Hermitian.

.. rubric:: Added

- Support for QICS, a new conic solver which supports solving LP, SOCP, SDP,
  EXP, as well as a new class of problems called quantum relative entropy
  programs (QREP).
- New expressions for quantum entropic and nonlinear matrix-valued functions,
  including arising in quantum information theory, as well as constraints
  representing the epigraphs or hypographs of these functions. These include

  - Quantum entropy
    (:func:`picos.quantentr <picos.expressions.algebra.quantentr>`),
  - Quantum relative entropy
    (:func:`picos.quantrelentr <picos.expressions.algebra.quantrelentr>`),
  - Quantum conditional entropy
    (:func:`picos.quantcondentr <picos.expressions.algebra.quantcondentr>`),
  - Operator relative entropy
    (:func:`picos.oprelentr <picos.expressions.algebra.oprelentr>`), and
  - Matrix geometric mean
    (:func:`picos.mtxgeomean <picos.expressions.algebra.mtxgeomean>`).

- Documentation examples for solving quantum relative entropy programs.
- Test cases for new quantum entropy and non-commutative perspective functions.
- Affine expression properties
  :attr:`~picos.expressions.exp_biaffine.BiaffineExpression.opreal` (equals
  :attr:`~picos.expressions.exp_biaffine.BiaffineExpression.hermitianized`) and
  :attr:`~picos.expressions.exp_biaffine.BiaffineExpression.opimag`.

.. rubric:: Changed

- Kronecker products of sparse matrices are now computed using SciPy, if
  available.
- Updated :class:`~picos.constraints.con_kldiv.KullbackLeiblerConstraint` so
  that it can be used as a constraint without having to convert to the
  exponential cone.
- CI/CD now uses ruff instead of pylama for linting.

.. rubric:: Fixed

- Indexing into a Gurobi variable container which cannot be indexed anymore.
- Creating a squared Frobenius norm of a complex expression.
- :class:`~picos.expressions.exp_wsum.WeightedSum` not working for a single
  weighted expression.
- A doctest failure related to
  :func:`~picos.valuable.patch_scipy_array_priority`.
- A doctest failure related to
  :meth:`~picos.modeling.problem.Problem.add_variable`.

.. rubric:: Deprecated

- The ``rng`` argument in :meth:`~picos.expressions.samples.Samples.shuffled`,
  which is no longer a parameter in :func:`random.shuffle` as of Python 3.11.


`2.4`_ - 2022-02-12
--------------------------------------------------------------------------------

*The performance update.*

.. rubric:: Added

- Support for noncovex quadratic constraints with Gurobi 9 (or later).
- Setting :data:`UNRELIABLE_STRATEGIES <picos.settings.UNRELIABLE_STRATEGIES>`
  to enable passing of problems to solvers that nominally support them but have
  proven unreliable.
- Setting :data:`PREFER_GUROBI_MATRIX_INTERFACE
  <picos.settings.PREFER_GUROBI_MATRIX_INTERFACE>` and option
  :ref:`gurobi_matint <option_gurobi_matint>` to toggle between Gurobi's legacy
  and matrix interface.
- Option :ref:`mosek_basic_sol <option_mosek_basic_sol>` to let MOSEK
  (Optimizer) compute a basic solution for LPs.

.. rubric:: Changed

- The performance for solving problems with large data has been improved

  - drastically for CVXOPT and MOSEK (Optimizer; LPs in particular),
  - significantly for Cplex and SCIP, and
  - subtly for GLPK, Gurobi and ECOS.

  This is most notable for LPs with a dense constraint matrix where the overhead
  for data passing can be significant in relation to the search time.

- The performance of :func:`picos.sum` when summing a large number of
  (bi-)affine expressions has been improved drastically.
- When possible, Gurobi is now interfaced through its matrix interface, which is
  faster for large data. This requires Gurobi 9 (or later) and SciPy.
- By default, solving with MOSEK (Optimizer) does not return a basic LP solution
  any more. Use :ref:`mosek_basic_sol <option_mosek_basic_sol>` to control this.
- The default value of :ref:`cvxopt_kktsolver <option_cvxopt_kktsolver>` is now
  :obj:`None` and means "try the fast ``"chol"`` first and fall back to the
  reliable ``"ldl"`` on error".
- Dualization now makes use of variable bounds to reduce the number of auxiliary
  constraints.
- The Python interface used to communicate with a solver is now mentioned in
  various log messages and exceptions.

.. rubric:: Fixed

- On-the-fly loading of a data vector in a multiplication with a matrix
  expression.
- Maximization of a squared norm not being detected as a nonconvex quadratic
  objective and being passed to solvers that do not support it.


`2.3`_ - 2021-10-07
--------------------------------------------------------------------------------

*The syntactic sugar update.*

.. rubric:: Important

- When forming linear matrix inequalities with the ``<<`` or ``>>`` operator,
  if one operand is an :math:`n \times n` matrix and the other is an
  :math:`n`-dimensional vector (or a scalar), the latter is now understood as
  (respectively broadcasted along) the main diagonal of an :math:`n \times n`
  diagonal matrix. In particular ``X >> 1`` is now understood as :math:`X
  \succeq I` as opposed to :math:`X \succeq J`. If you want to express a
  constraint :math:`X \succeq \alpha J` where :math:`J` is a matrix of all ones,
  use the new :func:`picos.J`.

.. rubric:: Added

- Support for the OSQP solver.
- On-the-fly loading of :mod:`scipy.sparse` matrices. (See new note
  :ref:`numscipy`.)
- Ability to negate or scale any expression and to sum any two expressions with
  the same or with a different type. This is established through a new
  :class:`~picos.expressions.exp_wsum.WeightedSum` fallback class. Convex or
  concave weighted sums can be used as an objective or in a constraint like any
  other expression.
- Properties :attr:`~picos.valuable.Valuable.sp`,
  :attr:`~picos.valuable.Valuable.np` and :attr:`~picos.valuable.Valuable.np2d`
  to query the value of an expression as a SciPy or NumPy type. (See new class
  :class:`~picos.valuable.Valuable` for all value query options.)
- Ability to use :func:`numpy.array` directly on valued PICOS objects, returning
  a zero, one or two-dimensional array depending on the shape of the value.
- New method :meth:`~picos.modeling.problem.Problem.require` and an equivalent
  overload for ``+=`` to add constraints to a
  :meth:`~picos.modeling.problem.Problem`.
- Cached functions :func:`~picos.I`, :func:`~picos.J`, and :func:`~picos.O` that
  create, respectively, an identity matrix, a matrix of all ones, and a zero
  matrix.
- Cached properties :attr:`BiaffineExpression.rowsum
  <picos.expressions.exp_biaffine.BiaffineExpression.rowsum>` and
  :attr:`~picos.expressions.exp_biaffine.BiaffineExpression.colsum` to
  complement the existing property
  :attr:`~picos.expressions.exp_biaffine.BiaffineExpression.sum` and an argument
  ``axis`` to :func:`picos.sum` for the same purpose.
- Option to give a name to :class:`problems <picos.modeling.problem.Problem>`
  via the first initialization argument or the
  :attr:`~picos.modeling.problem.Problem.name` property.
- Ability to perform some algebraic operations on :class:`objectives
  <picos.modeling.objective.Objective>`.
- Support for solving nonconvex continuous
  quadratic programs (QPs) with CPLEX and Gurobi. Gurobi further allows convex
  quadratic constraints to be present.
- Ability to
  :meth:`reshape <picos.expressions.exp_biaffine.BiaffineExpression.reshaped>`
  affine expressions in C-order, like NumPy.
- Ability to pass constant values to :func:`picos.sum`, :func:`~picos.min` and
  :func:`~picos.max`.
- Global option :data:`settings.RETURN_SOLUTION
  <picos.settings.RETURN_SOLUTION>` that controls whether
  :meth:`~picos.modeling.problem.Problem.solve` returns a
  :class:`~picos.modeling.solution.Solution`.
- Methods :class:`Samples.shuffled <picos.expressions.samples.Samples.shuffled>`
  and :class:`~picos.expressions.samples.Samples.kfold`.
- Support for MOSEK remote optimization with the :ref:`mosek_server
  <option_mosek_server>` option.
- Option :ref:`cplex_vmconfig <option_cplex_vmconfig>` to load a virtual machine
  configuration file with CPLEX.
- Function :func:`picos.patch_scipy_array_priority` to work around `SciPy#4819
  <https://github.com/scipy/scipy/issues/4819>`__.

.. rubric:: Changed

- The performance of solving semidefinite programs with trivial linear matrix
  inequalities of the form ``X >> 0`` using MOSEK (Optimizer) has been improved
  dramatically. Depending on your problem, you might experience this speedup
  when using the :ref:`dualize <option_dualize>` option.
- :attr:`Problem.minimize <picos.modeling.problem.Problem.minimize>` and
  :attr:`Problem.maximize <picos.modeling.problem.Problem.maximize>` are now
  properties that you can assign a minimization or maximization objective to,
  respectively.
- All expression types as well as the classes
  :class:`~picos.modeling.problem.Problem` and
  :class:`~picos.modeling.objective.Objective` now share the same interface to
  query their (objective) value. In particular, the new
  :attr:`~picos.valuable.Valuable.np` property can be used on all.
- Solving with ``duals=True`` will now raise an exception when duals were
  returned by the solver but not all could be converted. Use the default of
  ``duals=None`` to accept also incomplete duals.
- The new argument ``name`` is the only optional argument to
  :class:`~picos.modeling.problem.Problem` that may be passed as a positional
  argument; the arguments ``copyOptions`` and ``useOptions`` must now be passed
  as keyword arguments.

.. rubric:: Fixed

- Running ``setup.py`` under Python 3.6 and earlier.
- Bad shebang lines; all are now properly reading ``#!/usr/bin/env python3``.
- Incorrect duals returned by MOSEK (Fusion).
- An assertion failure when multiplying some quadratic expressions with a
  negative scalar.
- A false expression being created when multiplying a
  :class:`~picos.expressions.exp_detrootn.DetRootN` with a negative scalar.
- An exception when multiplying a scalar power with a constant.
- A modify-during-iteration issue that could result in a suboptimal solver being
  chosen.
- Building piecewise affine functions from a mix of certain and random
  expressions.
- A failure when computing the convex hull of a
  :class:`ScenarioPerturbationSet <picos.uncertain.ScenarioPerturbationSet>`
  with few points.
- Detection of string groups where the variable part is at the start or end of
  the strings.
- CVXOPT reacting inconsistently to some infeasible problems.
- A potential variable clash when reformulating a
  :class:`~picos.constraints.con_matnorm.NuclearNormConstraint`.
- Grammatical issues when printing variable groups of a problem.

.. rubric:: Removed

- The deprecated functions :attr:`Problem.minimize
  <picos.modeling.problem.Problem.minimize>` and
  :attr:`Problem.maximize <picos.modeling.problem.Problem.maximize>`. See
  **Changed** for the new meaning of these names.
- The deprecated arguments ``it`` and ``indices`` to :func:`picos.sum`.


`2.2`_ - 2021-02-09
--------------------------------------------------------------------------------

*The Python 3 update.*

.. rubric:: Important

- PICOS now requires Python 3.4 or later; Python 2 support was dropped.

.. rubric:: Added

- A synopsis to the :exc:`NoStrategyFound <.strategy.NoStrategyFound>`
  exception, explaining why strategy search failed.

.. rubric:: Fixed

- Optimizing matrix :math:`(p,q)`-norms when columns of the matrix are constant.
- Refining norms over a sparse constant term to a constant affine expression.
- Gurobi printing empty lines to console when dual retrieval fails.

.. rubric:: Changed

- A bunch of Python 2 compatibility code was finally removed.
- Exception readability has been improved using Python 3's ``raise from`` syntax
  where applicable.
- The ``__version_info__`` field now contains integers instead of strings.
- :attr:`QuadraticExpression.scalar_factors
  <.exp_quadratic.QuadraticExpression.scalar_factors>` is now :obj:`None`
  instead of an empty tuple when no decomposition into scalar factors is known.

.. rubric:: Deprecated

- :attr:`QuadraticExpression.quadratic_forms
  <.exp_quadratic.QuadraticExpression.quadratic_forms>`, as write access would
  leave the expression in an inconsistent state. (At your own risk, use the
  equivalent ``_sparse_quads`` instead.)


`2.1`_ - 2020-12-29
--------------------------------------------------------------------------------

*The robust optimization update.*

.. rubric:: Important

- The sign of dual values for affine equality constraints has been fixed by
  inversion.

.. rubric:: Added

- Support for a selection of robust optimization (RO) and distributionally
  robust stochastic programming (DRO) models through a new
  :mod:`picos.uncertain` namespace. You may now solve

  - scenario-robust conic programs via :class:`ScenarioPerturbationSet
    <picos.uncertain.ScenarioPerturbationSet>`,
  - conically robust linear programs and robust conic quadratic programs under
    ellipsoidal uncertainty via :class:`ConicPerturbationSet
    <picos.uncertain.ConicPerturbationSet>` and :class:`UnitBallPerturbationSet
    <picos.uncertain.UnitBallPerturbationSet>`, and
  - least squares and piecewise linear stochastic programs where the data
    generating distribution is defined ambiguously through a Wasserstein ball or
    through bounds on its first two moments via :class:`WassersteinAmbiguitySet
    <picos.uncertain.WassersteinAmbiguitySet>` and :class:`MomentAmbiguitySet
    <picos.uncertain.MomentAmbiguitySet>`, respectively.

- New function :func:`picos.block` to create block matrices efficiently.
- New convenience class :class:`picos.Samples` for data-driven applications.
- New set class :class:`picos.Ellipsoid` (has overlap with but a different
  scope than :class:`picos.Ball`).
- Support for :meth:`matrix reshuffling
  <picos.expressions.exp_biaffine.BiaffineExpression.reshuffled>` (aka *matrix
  realignment*) used in quantum information theory.
- Ability to define cones of fixed dimensionality and :class:`product cones
  <picos.ProductCone>` thereof.
- Ability to query the :attr:`solver-reported objective value
  <.solution.Solution.reported_value>` (useful with RO and DRO objectives).
- Methods :meth:`Problem.conic_form <.problem.Problem.conic_form>` and
  :meth:`reformulated <.problem.Problem.reformulated>` for internal use and
  educational purposes.
- New module :mod:`picos.settings` defining global options that can be set
  through environment variables prefixed with ``PICOS_``. Among other things,
  you can now blacklist all proprietary solvers for an application by passing
  ``PICOS_NONFREE_SOLVERS=False`` to the Python interpreter.
- A new base class :class:`BiaffineExpression
  <.exp_biaffine.BiaffineExpression>` for all (uncertain) affine expression
  types. This gives developers extending PICOS a framework to support models
  with parameterized data.
- Support for :meth:`factoring out
  <.exp_biaffine.BiaffineExpression.factor_out>` variables and parameters
  from (bi)affine vector expression.
- Support for :meth:`replacing <.expression.Expression.replace_mutables>`
  variables and parameters with affine expressions of same shape to perform a
  change of variables in a mathematical sense.
- Support for SCIP Optimization Suite 7.
- CVXOPT-specific solution search options
  :ref:`cvxopt_kktsolver <option_cvxopt_kktsolver>` and :ref:`cvxopt_kktreg
  <option_cvxopt_kktreg>`.

.. rubric:: Fixed

- Quadratic expressions created from a squared norm failing to decompose due to
  a numerically singular quadratic form.
- Solution objects unintendedly sharing memory.
- Solution search options that take a dictionary as their argument.
- Solution search with :ref:`assume_conic <option_assume_conic>` set to
  :obj:`False`.
- The :class:`EpigraphReformulation <picos.reforms.EpigraphReformulation>`
  falsely claiming that it can reformulate any nonconvex objective.
- A division by zero that could occur when computing the solution search
  overhead.
- An exception with functions that look for short string descriptions, in
  particular with :meth:`picos.sum`.

.. rubric:: Changed

- The functions :func:`picos.max` and :func:`picos.min` can now be used to
  express the maximum over a list of convex and the minimum over a list of
  concave expressions, respectively.
- Squared norms are now implemented as a subclass of quadratic expressions
  (:class:`SquaredNorm <picos.SquaredNorm>`), skipping an unnecessary
  decomposition on constraint creation.
- Commutation matrices used internally for various algebraic tasks are now
  retrieved from a centralized cached function, improving performance.
- The string description of :class:`Problem <.problem.Problem>` instances is not
  enclosed by dashed lines any more.


`2.0`_ - 2020-03-03
--------------------------------------------------------------------------------

*The backend update.*

.. rubric:: Important

This is a major release featuring vast backend rewrites as well as interface
changes. Programs written for older versions of PICOS are expected to raise
deprecation warnings but should otherwise work as before. The following lists
notable exceptions:

- The solution returned by :meth:`~.problem.Problem.solve` is now an instance of
  the new :class:`~picos.Solution` class instead of a dictionary.
- If solution search fails to find an optimal primal solution, PICOS will now
  raise a :class:`~picos.SolutionFailure` by default. Old behavior of not
  raising an exception is achieved by setting ``primals=None`` (see
  :ref:`primals <option_primals>` and :ref:`duals <option_duals>` options).
- The definition of the :math:`L_{p,q}`-norm has changed: It no longer refers
  to the :math:`p`-norm of the :math:`q`-norms of the matrix rows but to the
  :math:`q`-norm of the :math:`p`-norms of the matrix columns. This matches
  the definition you would find `on
  Wikipedia <https://en.wikipedia.org/wiki/Matrix_norm#L2,1_and_Lp,q_norms>`_
  and should reduce confusion for new users. See :class:`~picos.Norm`.
- The signs in the Lagrange dual problem of a conic problem are now more
  consistent for all cones, see :ref:`duals`. In particular the signs of dual
  values for (rotated) second order conic constraints have changed and the
  problem obtained by :attr:`Problem.dual <.problem.Problem.dual>` (new for
  :meth:`~.problem.Problem.as_dual`) has a different (but equivalent) form.

.. rubric:: Added

- A modular problem reformulation framework. Before selecting a solver, PICOS
  now builds a map of problem types that your problem can be reformulated to
  and makes a choice based on the expected complexity of the reposed problem.
- An object oriented interface to solution search options. See
  :class:`~picos.Options`.
- Support for arbitrary objective functions via an epigraph reformulation.
- Support for MOSEK 9.
- Support for ECOS 2.0.7.
- Support for multiple subsystems with :func:`~picos.partial_trace`.
- Quick-solve functions :func:`picos.minimize` and :func:`picos.maximize`.
- Lower and upper diagonal matrix variable types.
- :class:`~picos.SecondOrderCone` and :class:`~picos.RotatedSecondOrderCone`
  sets to explicitly create the associated constraints. *(You now need to use
  these if you want to obtain a conic instead of a quadratic dual.)*
- Possibility to use :func:`picos.sum` to sum over the elements of a single
  multidimensional expression.
- Possibility to create a :class:`~picos.Ball` or :class:`~picos.Simplex` with a
  non-constant radius.
- Many new properties (postfix operations) to work with affine expressions; for
  instance ``A.vec`` is a faster and cached way to express the vectorization
  ``A[:]``.
- Options :ref:`assume_conic <option_assume_conic>` and
  :ref:`verify_prediction <option_verify_prediction>`.
- An option for every solver to manipulate the chances of it being selected
  (e.g. :ref:`penalty_cvxopt <option_penalty_cvxopt>`).
- Ability to run doctests via ``test.py``.

.. rubric:: Fixed

The following are issues that were fixed in an effort of their own. If a bug is
not listed here, it might still be fixed as a side effect of some of the large
scale code rewrites that this release ships.

- Upgrading the PyPI package via pip.
- A regression that rendered the Kronecker product unusable.
- Noisy exception handling in a sparse matrix helper function.
- Shape detection for matrices given by string.
- The :ref:`hotstart <option_hotstart>` option when solving with CPLEX.
- Low precision QCP duals from Gurobi.

.. rubric:: Changed

- All algebraic expression code has been rewritten and organized in a new
  :mod:`~picos.expressions` package. In particular, real and complex expressions
  are distinguished more clearly.
- All algebraic expressions are now immutable.
- The result of any unary operation on algebraic expressions (e.g. negation,
  transposition) is cached (only computed once per expression).
- Slicing of affine expressions is more powerful, see :ref:`slicing`.
- Loading of constant numeric data has been unified, see
  :func:`~picos.expressions.data.load_data`.
- Variables are now created independently of problems by instanciating one of
  the new :mod:`variable types <picos.expressions.variables>`.
  *(*:meth:`Problem.add_variable <.problem.Problem.add_variable>`
  *is deprecated.)*
- Constraints are added to problems as they are; any transformation is done
  transparently during solution search.
- In particular, :math:`x^2 \leq yz` is now initially a (nonconvex) quadratic
  constraint and transformation to a conic constraint is controlled by the new
  :ref:`assume_conic <option_assume_conic>` option.
- Expressions constrained to be positive semidefinite are now required to be
  symmetric/hermitian by their own definition. *(Use*
  :class:`~picos.SymmetricVariable` *or* :class:`~picos.HermitianVariable`
  *whenever applicable!)*
- Options passed to :meth:`~.problem.Problem.solve` are only used for that
  particular search.
- The default value for the :ref:`verbosity <option_verbosity>` option (formerly
  ``verbose``) is now :math:`0`.
- Available solvers are only imported when they are actually being used, which
  speeds up import of PICOS on platforms with many solvers installed.
- The code obeys PEP 8 and PEP 257 more strongly. Exceptions: D105, D203, D213,
  D401, E122, E128, E221, E271, E272, E501, E702, E741.
- Production testing code was moved out of the :mod:`picos` package.

.. rubric:: Removed

- The ``NoAppropriateSolverError`` exception that was previously raised by
  :meth:`~.problem.Problem.solve`. This is replaced by the new
  :class:`~picos.SolutionFailure` exception with error code :math:`1`.
- Some public functions in the :mod:`~picos.tools` module that were originally
  meant for internal use.

.. rubric:: Deprecated

This section lists deprecated modules, functions and options with their
respective replacement or deprecation reason on the right hand side.
Deprecated entities produce a warning and will be removed in a future release.

- The :mod:`~picos.tools` module as a whole. It previously contained both
  algebraic functions for the user as well as functions meant for internal use.
  The former group of functions can now be imported directly from the
  :mod:`picos` namespace (though some are also individually deprecated). The
  other functions were either relocated (but can still be imported from
  :mod:`~picos.tools` while it lasts) or removed.
- In the :class:`~.problem.Problem` class:

  - :meth:`~.problem.Problem.add_variable`,
    :meth:`~.problem.Problem.remove_variable`,
    :meth:`~.problem.Problem.set_var_value`
    → variables are instanciated directly and added to problems automatically
  - :meth:`~.problem.Problem.minimize` → :func:`picos.minimize`
  - :meth:`~.problem.Problem.maximize` → :func:`picos.maximize`
  - :meth:`~.problem.Problem.set_option`
    → assign to attributes or items of :attr:`Problem.options <picos.Options>`
  - :meth:`~.problem.Problem.update_options`
    → :meth:`options.update <.options.Options.update>`
  - :meth:`~.problem.Problem.set_all_options_to_default`
    → :meth:`options.reset <.options.Options.reset>`
  - :meth:`~.problem.Problem.obj_value` → :attr:`~.valuable.Valuable.value`
  - :meth:`~.problem.Problem.is_continuous`
    → :attr:`~.problem.Problem.continuous`
  - :meth:`~.problem.Problem.is_pure_integer`
    → :attr:`~.problem.Problem.pure_integer`
  - :meth:`~.problem.Problem.verbosity`
    → :ref:`options.verbosity <option_verbosity>`
  - :meth:`~.problem.Problem.as_dual` → :attr:`~.problem.Problem.dual`
  - :meth:`~.problem.Problem.countVar`,
    :meth:`~.problem.Problem.countCons`,
    :meth:`~.problem.Problem.numberOfVars`,
    :meth:`~.problem.Problem.numberLSEConstraints`,
    :meth:`~.problem.Problem.numberSDPConstraints`,
    :meth:`~.problem.Problem.numberQuadConstraints`,
    :meth:`~.problem.Problem.numberConeConstraints`
    → were meant for internal use
  - arguments ``it``, ``indices`` and ``key`` to
    :meth:`~.problem.Problem.add_list_of_constraints` → are ignored

- All expression types:

  - constraint creation via ``<`` → ``<=``
  - constraint creation via ``>`` → ``>=``
  - :meth:`~.expression.Expression.is_valued`
    → :attr:`~.valuable.Valuable.valued`
  - :meth:`~.expression.Expression.set_value`
    → assign to :attr:`~.valuable.Valuable.value`

- Affine expressions:

  - :meth:`~.exp_biaffine.BiaffineExpression.fromScalar`
    → :meth:`~.exp_biaffine.BiaffineExpression.from_constant`
    or :func:`picos.Constant`
  - :meth:`~.exp_biaffine.BiaffineExpression.fromMatrix`
    → :meth:`~.exp_biaffine.BiaffineExpression.from_constant`
    or :func:`picos.Constant`
  - :meth:`~.exp_biaffine.BiaffineExpression.hadamard` → ``^``
  - :meth:`~.exp_biaffine.BiaffineExpression.isconstant`
    → :meth:`~.expression.Expression.constant`
  - :meth:`~.exp_biaffine.BiaffineExpression.same_as`
    → :meth:`~.exp_biaffine.BiaffineExpression.equals`
  - :meth:`~.exp_biaffine.BiaffineExpression.transpose`
    → :attr:`~.exp_biaffine.BiaffineExpression.T`
  - :attr:`~.exp_biaffine.BiaffineExpression.Tx`
    → :meth:`~.exp_biaffine.BiaffineExpression.partial_transpose`
  - :meth:`~.exp_biaffine.BiaffineExpression.conjugate`
    → :attr:`~.exp_biaffine.BiaffineExpression.conj`
  - :meth:`~.exp_biaffine.BiaffineExpression.Htranspose`
    → :attr:`~.exp_biaffine.BiaffineExpression.H`
  - :meth:`~.exp_biaffine.BiaffineExpression.copy`
    → expressions are immutable
  - :meth:`~.exp_biaffine.BiaffineExpression.soft_copy`
    → expressions are immutable

- Algebraic functions and shorthands in the ``picos`` namespace:

  - :func:`~picos.tracepow` → :class:`~picos.PowerTrace`
  - :func:`~picos.new_param` → :func:`~picos.Constant`
  - :func:`~picos.flow_Constraint` → :class:`~picos.FlowConstraint`
  - :func:`~picos.diag_vect` → :func:`~picos.maindiag`
  - :func:`~picos.simplex` → :class:`~picos.Simplex`
  - :func:`~picos.truncated_simplex` → :class:`~picos.Simplex`
  - arguments ``it`` and ``indices`` to :func:`~picos.sum` → are ignored

- Solution search options:

  - ``allow_license_warnings``
    → :ref:`license_warnings <option_license_warnings>`
  - ``verbose`` → :ref:`verbosity <option_verbosity>` (takes an integer)
  - ``noprimals`` → :ref:`primals <option_primals>` (the meaning is inverted)
  - ``noduals`` → :ref:`duals <option_duals>` (the meaning is inverted)
  - ``tol`` →  ``*_fsb_tol`` and ``*_ipm_opt_tol``
  - ``gaplim`` → :ref:`rel_bnb_opt_tol <option_rel_bnb_opt_tol>`
  - ``maxit`` → :ref:`max_iterations <option_max_iterations>`
  - ``nbsol`` → :ref:`max_fsb_nodes <option_max_fsb_nodes>`
  - ``pool_relgap`` → :ref:`pool_rel_gap <option_pool_rel_gap>`
  - ``pool_absgap`` → :ref:`pool_abs_gap <option_pool_abs_gap>`
  - ``lboundlimit`` → :ref:`cplex_lwr_bnd_limit <option_cplex_lwr_bnd_limit>`
  - ``uboundlimit`` → :ref:`cplex_upr_bnd_limit <option_cplex_upr_bnd_limit>`
  - ``boundMonitor`` → :ref:`cplex_bnd_monitor <option_cplex_bnd_monitor>`
  - ``solve_via_dual`` → :ref:`dualize <option_dualize>` (may not be :obj:`None`
    any more)


`1.2.0`_ - 2019-01-11
--------------------------------------------------------------------------------

.. rubric:: Important

- :attr:`A scalar expression's value <.valuable.Valuable.value>` and
  :attr:`a scalar constraint's dual <.constraint.Constraint.dual>` are returned
  as scalar types as opposed to 1×1 matrices.
- The dual value returned for rotated second order cone constraints is now a
  proper member of the dual cone (which equals the primal cone up to a factor of
  :math:`4`). Previously, the dual of an equivalent second order cone constraint
  was returned.
- The Python 2/3 compatibility library ``six`` is no longer a dependency.

.. rubric:: Added

- Support for the ECOS solver.
- Experimental support for MOSEK's new Fusion API.
- Full support for exponential cone programming.
- A production testing framework featuring around 40 novel optimization test
  cases that allows quick selection of tests, solvers, and solver options.
- A "glyph" system that allows the user to adjust the string representations of
  future expressions and constraints. For instance, :func:`picos.latin1()
  <picos.glyphs.latin1>` disables use of unicode symbols.
- Support for symmetric variables with all solvers, even if they do not support
  semidefinite programming.

.. rubric:: Changed

- Solver implementations each have a source file of their own, and a common
  interface that makes implementing new solvers easier.
- Likewise, constraint implementations each have a source file of their own.
- The implementations of CPLEX, Gurobi, MOSEK and SCIP have been rewritten.
- Solver selection takes into account how well a problem is supported,
  distinguishing between native, secondary, experimental and limited support.
- Unsupported operations on expressions now produce meaningful exceptions.
- :meth:`add_constraint <.problem.Problem.add_constraint>` and
  :meth:`add_list_of_constraints <.problem.Problem.add_list_of_constraints>`
  always return the constraints
  passed to them.
- :meth:`add_list_of_constraints <.problem.Problem.add_list_of_constraints>`
  and :func:`picos.sum` find a short string representation automatically.

.. rubric:: Removed

- The old production testing script.
- Support for the SDPA solver.
- Support for sequential quadratic programming.
- The options ``convert_quad_to_socp_if_needed``, ``pass_simple_cons_as_bound``,
  ``return_constraints``, ``handleBarVars``, ``handleConeVars`` and
  ``smcp_feas``.
- Support for GLPK and MOSEK through CVXOPT.

.. rubric:: Fixed

- Performance issues when exporting variable bounds to CVXOPT.
- Hadamard product involving complex matrices.
- Adding constant terms to quadratic expression.
- Incorrect or redundant expression string representations.
- GLPK handling of the default ``maxit`` option.
- Miscellaneous solver-specific bugs in the solvers that were re-implemented.


`1.1.3`_ - 2018-10-05
--------------------------------------------------------------------------------

.. rubric:: Added

- Support for the solvers GLPK and SCIP.
- PICOS packages `on Anaconda Cloud <https://anaconda.org/picos/picos>`_.
- PICOS packages `in the Arch Linux User Repository
  <https://aur.archlinux.org/packages/?SeB=b&K=python-picos>`_.

.. rubric:: Changed

- The main repository has moved to
  `GitLab <https://gitlab.com/picos-api/picos>`_.
- Releases of packages and documentation changes are
  `automated <https://about.gitlab.com/features/gitlab-ci-cd/>`_ and thus more
  frequent. In particular, post release versions are available.
- Test bench execution is automated for greater code stability.
- Improved test bench output.
- Improved support for the SDPA solver.
- :func:`~picos.partial_trace` can handle rectangular subsystems.
- The documentation was restructured; examples were converted to Python 3.

.. rubric:: Fixed

- Upper bounding the norm of a complex scalar.
- Multiplication with a complex scalar.
- A couple of Python 3 specific errors, in particular when deleting constraints.
- All documentation examples are reproducible with the current state of PICOS.


`1.1.2`_ - 2016-07-04
--------------------------------------------------------------------------------

.. rubric:: Added

- Ability to dynamically add and remove constraints.
- Option ``pass_simple_cons_as_bound``, see below.

.. rubric:: Changed

- Improved efficiency when processing large expressions.
- Improved support for the SDPA solver.
- :meth:`add_constraint <.problem.Problem.add_constraint>` returns a handle to
  the constraint when the option `return_constraints` is set.
- New signature for the function :func:`~picos.partial_transpose`, which can now
  transpose arbitrary subsystems from a kronecker product.
- PICOS no longer turns constraints into variable bounds, unless the new option
  ``pass_simple_cons_as_bound`` is enabled.

.. rubric:: Fixed

- Minor bugs with complex expressions.


`1.1.1`_ - 2015-08-29
--------------------------------------------------------------------------------

.. rubric:: Added

- Support for the SDPA solver.
- Partial trace of an affine expression, see :func:`~picos.partial_trace`.

.. rubric:: Changed

- Improved PEP 8 compliance.

.. rubric:: Fixed

- Compatibility with Python 3.


`1.1.0`_ - 2015-04-15
--------------------------------------------------------------------------------

.. rubric:: Added

- Compatibility with Python 3.

.. rubric:: Changed

- The main repository has moved to `GitHub <https://github.com/gsagnol/picos>`_.


`1.0.2`_ - 2015-01-30
--------------------------------------------------------------------------------

.. rubric:: Added

- Ability to read and write problems in
  `conic benchmark format <http://cblib.zib.de/>`_.
- Support for inequalities involving the sum of the :math:`k` largest or
  smallest elements of an affine expression, see :func:`~picos.sum_k_largest`
  and :func:`~picos.sum_k_smallest`.
- Support for inequalities involving the sum of the :math:`k` largest or
  smallest eigenvalues of a symmetric matrix, see
  :func:`~picos.sum_k_largest_lambda`, :func:`~picos.sum_k_smallest_lambda`,
  :func:`~picos.lambda_max` and :func:`~picos.lambda_min`.
- Support for inequalities involving the :math:`L_{p,q}`-norm of an affine
  expression, see :func:`~picos.norm`.
- Support for equalities involving complex coefficients.
- Support for antisymmetric matrix variables.
- Set expressions that affine expressions can be constrained to be an element
  of, see :func:`~picos.ball`, :func:`~picos.simplex` and
  :func:`~picos.truncated_simplex`.
- Shorthand functions :meth:`maximize <.problem.Problem.maximize>` and
  :meth:`minimize <.problem.Problem.minimize>` to specify the objective function
  of a problem and solve it.
- Hadamard (elementwise) product of affine expression, as an overload of the
  ``^`` operator, read :ref:`the tutorial on overloads <overloads>`.
- Partial transposition of an aAffine Expression, see
  :func:`~picos.partial_transpose`.

.. rubric:: Changed

- Improved efficiency of the sparse SDPA file format writer.
- Improved efficiency of the complex to real transformation.

.. rubric:: Fixed

- Scalar product of hermitian matrices.
- Conjugate of a complex expression.


`1.0.1`_ - 2014-08-27
--------------------------------------------------------------------------------

.. rubric:: Added

- Support for semidefinite programming over the complex domain, see
  :ref:`the documentation on complex problems <complex>`.
- Helper function to input (multicommodity) graph flow problems, see
  :ref:`the tutorial on flow constraints <flowcons>`.
- Additional argument to :func:`~picos.tracepow`, to represent constraints
  of the form :math:`\operatorname{trace}(M X^p) \geq t`.

.. rubric:: Changed

- Significantly improved slicing performance for affine expressions.
- Improved performance when loading data.
- Improved performance when retrieving primal solution from CPLEX.
- The documentation received an overhaul.


`1.0.0`_ - 2013-07-19
--------------------------------------------------------------------------------

.. rubric:: Added

- Ability to express rational powers of affine expressions with the ``**``
  operator, traces of matrix powers with :func:`~picos.tracepow`,
  (generalized) p-norms with :func:`~picos.norm` and :math:`n`-th roots of a
  determinant with :func:`~picos.detrootn`.
- Ability to specify variable bounds directly rather than by adding constraints,
  see :meth:`add_variable <.problem.Problem.add_variable>`.
- Problem dualization.
- Option ``solve_via_dual`` which controls passing the dual problem to the
  solver instead of the primal problem. This can result in a significant
  speedup for certain problems.
- Semidefinite programming interface for MOSEK 7.0.
- Options ``handleBarVars`` and ``handleConeVars`` to customize how SOCPs and
  SDPs are passed to MOSEK. When these are set to ``True``, PICOS tries to
  minimize the number of variables of the MOSEK instance.

.. rubric:: Changed

- If the chosen solver supports this, updated problems will be partially
  re-solved instead of solved from scratch.

.. rubric:: Removed

- Option ``onlyChangeObjective``.


`0.1.3`_ - 2013-04-17
--------------------------------------------------------------------------------

.. rubric:: Added

- A :func:`~picos.geomean` function to construct geometric mean inequalities
  that will be cast as rotated second order cone constraints.
- Options ``uboundlimit`` and ``lboundlimit`` to tell CPLEX to stop the search
  as soon as the given threshold is reached for the upper and lower bound,
  respectively.
- Option ``boundMonitor`` to inspect the evolution of CPLEX lower and upper
  bounds.
- Ability to use the weak inequality operators as an alias for the strong ones.

.. rubric:: Changed

- The solver search time is returned in the dictionary returned by
  :meth:`solve <.problem.Problem.solve>`.

.. rubric:: Fixed

- Access to dual values of fixed variables with CPLEX.
- Evaluation of constant affine expressions with a zero coefficient.
- Number of constraints not being updated in
  :meth:`remove_constraint <.problem.Problem.remove_constraint>`.


`0.1.2`_ - 2013-01-10
--------------------------------------------------------------------------------

.. rubric:: Fixed

- Writing SDPA files. The lower triangular part of the constraint matrix was
  written instead of the upper triangular part.
- A wrongly raised :class:`IndexError` from
  :meth:`remove_constraint <.problem.Problem.remove_constraint>`.


`0.1.1`_ - 2012-12-08
--------------------------------------------------------------------------------

.. rubric:: Added

- Interface to Gurobi.
- Ability to give an initial solution to warm-start mixed integer optimizers.
- Ability to get a reference to a constraint that was added.

.. rubric:: Fixed

- Minor bugs with quadratic expressions.


`0.1.0`_ - 2012-06-22
--------------------------------------------------------------------------------

.. rubric:: Added

- Initial release of PICOS.
