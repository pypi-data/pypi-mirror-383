.. |_| unicode:: 0xA0
   :trim:

.. _tolerances:

Numeric Tolerances
==================

PICOS allows you to fine-tune how accurate your solution needs to be.
Tolerances fall in three categories:

- **Feasibility** tolerances, abbreviated ``fsb``, control the magnitude of
  constraint violation that is tolerated. The :ref:`integrality tolerance
  <option_integrality_tol>` also falls into this category.
- **Optimality** tolerances, abbreviated ``opt``, control the maximum allowed
  deviation from the mathematically exact optimum solution and serve as a
  termination criterion. An exception is the the Simplex algorithm that uses the
  :ref:`dual feasibility <option_abs_dual_fsb_tol>` as its stopping criterion.
- The remaining tolerances are used at intermediate steps of specific
  algorithms, such as the :ref:`Markowitz threshold <option_markowitz_tol>` used
  in a pivoting strategy of the Simplex algoritm.

Solvers differ in how they measure deviations from the ideal values. Some bound
**absolute** values while others consider the deviation **in relation** to the
magnitude of the numbers that occur in the problem.
PICOS abbreviates the former measurement with ``abs`` and the latter with
``rel``.
If both measurements are supported by a solver, then the standard approach is to
allow values if they are sufficiently accurate according to either one.

If solvers use a single value for **primal** and **dual** feasibility but PICOS
is configured to use differing accuracies, supplied in the options with the
``prim`` and ``dual`` abbreviations respectively, it will supply the smaller of
both values to such solvers.

By default, PICOS overrides the solver's default accuracies with common values,
so that the choice of solver becomes transparent to you.
Given that ``P`` is your problem instance, you can make PICOS respect the
solvers' individual choices as follows:

>>> import picos
>>> P = picos.Problem()
>>> P.options["*_tol"] = None

Comparison Table
----------------

The table shows what tolerance :class:`options <picos.Options>` are supported by
PICOS and each solver, and what their respective default value is.

.. list-table::
  :header-rows: 1

  * - Option |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_|
    - PICOS |_| |_| |_| |_| |_|
    - CPLEX |_| |_| |_| |_| |_|
    - CVXOPT |_|
    - ECOS |_| |_| |_| |_| |_| |_| |_|
    - GLPK |_| |_| |_| |_| |_| |_| |_|
    - Gurobi |_| |_| |_| |_| |_| |_|
    - MOSEK |_| |_| |_| |_|
    - QICS |_|
    - SCIP |_| |_| |_| |_| |_| |_| |_| |_|
    - SMCP |_| |_| |_| |_| |_| |_|

  * - :ref:`abs_prim_fsb_tol <option_abs_prim_fsb_tol>`
    - :math:`10^{-8}`
    - :mathlink:`\text{SX:}~10^{-6} <https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/Parameters/topics/EpRHS.html>`
    - unused
    - unused ?
    - :mathlink:`\text{SX:}~10^{-7}~? <https://fossies.org/linux/glpk/doc/glpk.pdf>`
    - :mathlink:`10^{-6}~? <https://www.gurobi.com/documentation/8.1/refman/feasibilitytol.html#parameter:FeasibilityTol>`
    - :mathlink:`\text{SX:}~10^{-6} <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.basis_tol_x>`
      :mathlink:`\text{LP:}~10^{-8}~? <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.intpnt_tol_pfeas>`
      :mathlink:`\text{CP:}~10^{-8}~? <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.intpnt_co_tol_pfeas>`
      :mathlink:`\text{QP:}~10^{-8}~? <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.intpnt_qo_tol_pfeas>`
      :mathlink:`\text{NL:}~10^{-8}~? <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.intpnt_nl_tol_pfeas>`
      :mathlink:`\text{IP:}~10^{-6}~? <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.mio_tol_feas>`
    - unused
    - :mathlink:`\text{SX:}~10^{-6} <https://scip.zib.de/doc/html/PARAMETERS.php>`
    - unused

  * - :ref:`rel_prim_fsb_tol <option_rel_prim_fsb_tol>`
    - :math:`10^{-8}`
    - :mathlink:`\text{LQ:}~10^{-8} <https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/Parameters/topics/BarEpComp.html>`
      :mathlink:`\text{QC:}~10^{-8} <https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/Parameters/topics/BarQCPEpComp.html>`
    - :mathlink:`\text{CP:}~10^{-7} <https://cvxopt.org/userguide/coneprog.html#algorithm-parameters>`
      :mathlink:`\text{NL:}~10^{-7} <https://cvxopt.org/userguide/solvers.html#algorithm-parameters>`
    - :mathlink:`10^{-8}~? <https://github.com/embotech/ecos/blob/develop/include/ecos.h>`
    - unused ?
    - unused ?
    - .. MOSEK :mathlink:` <>`
    - :mathlink:`10^{-8} <https://qics.readthedocs.io/en/stable/guide/reference.html#solving>`
    - :mathlink:`10^{-6} <https://scip.zib.de/doc/html/FAQ.php#feasibilitycomparison>`
    - :mathlink:`10^{-8} <https://smcp.readthedocs.io/en/latest/documentation/#smcp.solvers.chordalsolver_esd>`

  * - :ref:`abs_dual_fsb_tol <option_abs_dual_fsb_tol>`
    - :math:`10^{-8}`
    - :mathlink:`\text{SX:}~10^{-6} <https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/Parameters/topics/EpOpt.html>`
    - unused
    - unused ?
    - :mathlink:`\text{SX:}~10^{-7}~? <https://fossies.org/linux/glpk/doc/glpk.pdf>`
    - :mathlink:`10^{-6} <https://www.gurobi.com/documentation/8.1/refman/optimalitytol.html#parameter:OptimalityTol>`
    - :mathlink:`\text{SX:}~10^{-6} <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.basis_tol_s>`
      :mathlink:`\text{LP:}~10^{-8}~? <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.intpnt_tol_dfeas>`
      :mathlink:`\text{CP:}~10^{-8}~? <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.intpnt_co_tol_dfeas>`
      :mathlink:`\text{QP:}~10^{-8}~? <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.intpnt_qo_tol_dfeas>`
      :mathlink:`\text{NL:}~10^{-8}~? <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.intpnt_nl_tol_dfeas>`
    - unused
    - :mathlink:`\text{SX:}~10^{-7} <https://scip.zib.de/doc/html/PARAMETERS.php>`
    - unused

  * - :ref:`rel_dual_fsb_tol <option_rel_dual_fsb_tol>`
    - :math:`10^{-8}`
    - :mathlink:`\text{LQ:}~10^{-8} <https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/Parameters/topics/BarEpComp.html>`
      :mathlink:`\text{QC:}~10^{-8} <https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/Parameters/topics/BarQCPEpComp.html>`
    - :mathlink:`\text{CP:}~10^{-7} <https://cvxopt.org/userguide/coneprog.html#algorithm-parameters>`
      :mathlink:`\text{NL:}~10^{-7} <https://cvxopt.org/userguide/solvers.html#algorithm-parameters>`
    - :mathlink:`10^{-8}~? <https://github.com/embotech/ecos/blob/develop/include/ecos.h>`
    - unused ?
    - unused
    - :mathlink:`\text{SX:}~10^{-12} <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.basis_rel_tol_s>`
    - :mathlink:`10^{-8} <https://qics.readthedocs.io/en/stable/guide/reference.html#solving>`
    - :mathlink:`10^{-6} <https://scip.zib.de/doc/html/FAQ.php#feasibilitycomparison>`
    - :mathlink:`10^{-8} <https://smcp.readthedocs.io/en/latest/documentation/#smcp.solvers.chordalsolver_esd>`

  * - :ref:`abs_ipm_opt_tol <option_abs_ipm_opt_tol>`
    - :math:`10^{-8}`
    - unused
    - :mathlink:`\text{CP:}~10^{-7} <https://cvxopt.org/userguide/coneprog.html#algorithm-parameters>`
      :mathlink:`\text{NL:}~10^{-7} <https://cvxopt.org/userguide/solvers.html#algorithm-parameters>`
    - :mathlink:`10^{-8} <https://github.com/embotech/ecos/blob/develop/include/ecos.h>`
    - unused
    - unused
    - unused
    - unused
    - :mathlink:`0 <https://scip.zib.de/doc/html/PARAMETERS.php>`
    - :mathlink:`10^{-6} <https://smcp.readthedocs.io/en/latest/documentation/#smcp.solvers.chordalsolver_esd>`

  * - :ref:`rel_ipm_opt_tol <option_rel_ipm_opt_tol>`
    - :math:`10^{-8}`
    - :mathlink:`\text{LQ:}~10^{-8} <https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/Parameters/topics/BarEpComp.html>`
      :mathlink:`\text{QC:}~10^{-8} <https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/Parameters/topics/BarQCPEpComp.html>`
    - :mathlink:`\text{CP:}~10^{-6} <https://cvxopt.org/userguide/coneprog.html#algorithm-parameters>`
      :mathlink:`\text{NL:}~10^{-6} <https://cvxopt.org/userguide/solvers.html#algorithm-parameters>`
    - :mathlink:`10^{-8} <https://github.com/embotech/ecos/blob/develop/include/ecos.h>`
    - unused
    - :mathlink:`\text{CO:}~10^{-8} <https://www.gurobi.com/documentation/8.1/refman/barconvtol.html#parameter:BarConvTol>`
      :mathlink:`\text{QC:}~10^{-6} <https://www.gurobi.com/documentation/8.1/refman/barqcpconvtol.html#parameter:BarQCPConvTol>`
    - :mathlink:`\text{LP:}~10^{-8} <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.intpnt_tol_rel_gap>`
      :mathlink:`\text{CP:}~10^{-7} <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.intpnt_co_tol_rel_gap>`
      :mathlink:`\text{QP:}~10^{-7} <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.intpnt_qo_tol_rel_gap>`
      :mathlink:`\text{NL:}~10^{-6} <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.intpnt_nl_tol_rel_gap>`
    - :mathlink:`10^{-8} <https://qics.readthedocs.io/en/stable/guide/reference.html#solving>`
    - :mathlink:`0 <https://scip.zib.de/doc/html/PARAMETERS.php>`
    - :mathlink:`10^{-6} <https://smcp.readthedocs.io/en/latest/documentation/#smcp.solvers.chordalsolver_esd>`

  * - :ref:`abs_bnb_opt_tol <option_abs_bnb_opt_tol>`
    - :math:`10^{-6}`
    - :mathlink:`10^{-6} <https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/Parameters/topics/EpAGap.html>`
    - no IP
    - :mathlink:`10^{-6} <https://github.com/embotech/ecos/blob/develop/include/ecos_bb.h#L37>`
    - unused
    - :mathlink:`10^{-10} <https://www.gurobi.com/documentation/8.1/refman/mipgapabs.html#parameter:MIPGapAbs>`
    - :mathlink:`0 <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.mio_tol_abs_gap>`
    - no IP
    - :mathlink:`0 <https://scip.zib.de/doc/html/PARAMETERS.php>`
    - no IP

  * - :ref:`rel_bnb_opt_tol <option_rel_bnb_opt_tol>`
    - :math:`10^{-4}`
    - :mathlink:`10^{-4} <https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/Parameters/topics/EpGap.html>`
    - no IP
    - :mathlink:`10^{-3} <https://github.com/embotech/ecos/blob/develop/include/ecos_bb.h#L38>`
    - :mathlink:`0 <https://fossies.org/linux/glpk/doc/glpk.pdf>`
    - :mathlink:`10^{-4} <https://www.gurobi.com/documentation/8.1/refman/mipgap2.html#parameter:MIPGap>`
    - :mathlink:`10^{-4} <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.mio_tol_rel_gap>`
    - no IP
    - :mathlink:`0 <https://scip.zib.de/doc/html/PARAMETERS.php>`
    - no IP

  * - :ref:`integrality_tol <option_integrality_tol>`
    - :math:`10^{-5}`
    - :mathlink:`10^{-5} <https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/Parameters/topics/EpInt.html>`
    - no IP
    - :mathlink:`10^{-4} <https://github.com/embotech/ecos/blob/develop/include/ecos_bb.h#L40>`
    - :mathlink:`10^{-5} <https://fossies.org/linux/glpk/doc/glpk.pdf>`
    - :mathlink:`10^{-5} <https://www.gurobi.com/documentation/8.1/refman/intfeastol.html#parameter:IntFeasTol>`
    - :mathlink:`10^{-5} <https://docs.mosek.com/8.1/pythonapi/parameters.html#mosek.dparam.mio_tol_abs_relax_int>`
    - no IP
    - unused
    - no IP

  * - :ref:`markowitz_tol <option_markowitz_tol>`
    - ``None``
    - :mathlink:`0.01 <https://www.ibm.com/support/knowledgecenter/SSSA5P_12.8.0/ilog.odms.cplex.help/CPLEX/Parameters/topics/EpMrk.html>`
    - no SX
    - no SX
    - :mathlink:`0.1 <https://fossies.org/linux/glpk/doc/glpk.pdf>`
    - :mathlink:`2^{-7} <https://www.gurobi.com/documentation/8.1/refman/markowitztol.html#parameter:MarkowitzTol>`
    - unused ?
    - no SX
    - unused
    - no SX

.. rubric:: Pooled options

- ECOS, CVXOPT, QICS, SCIP and SMCP merge :ref:`rel_prim_fsb_tol
  <option_rel_prim_fsb_tol>` and :ref:`rel_dual_fsb_tol
  <option_rel_dual_fsb_tol>`.
- CPLEX merges :ref:`rel_prim_fsb_tol <option_rel_prim_fsb_tol>`,
  :ref:`rel_dual_fsb_tol <option_rel_dual_fsb_tol>` and
  :ref:`rel_ipm_opt_tol <option_rel_ipm_opt_tol>`.
- SCIP appears to merge :ref:`abs_ipm_opt_tol <option_abs_ipm_opt_tol>` with
  :ref:`abs_bnb_opt_tol <option_abs_bnb_opt_tol>` and :ref:`rel_ipm_opt_tol
  <option_rel_ipm_opt_tol>` with :ref:`rel_bnb_opt_tol
  <option_rel_bnb_opt_tol>` with its ``limits/absgap`` and ``limits/gap``
  options, respectively.

.. rubric:: Legend

.. list-table::
  :widths: auto

  * - ?
    - It is unclear whether an absolute or relative measure is used,
      or if an option is not available.
  * - SX
    - Linear Programs via Simplex
  * - LP
    - Linear Programs via Interior-Point Method
  * - CP
    - Conic Programs
  * - LQ
    - Linear and Quadratic Programs
  * - QP
    - Quadratic Programs
  * - QC
    - Quadratically Constrained (Quadratic) Programs
  * - NL
    - Nonlinear Programs
  * - IP
    - (Mixed) Integer Programs
