.. |_| unicode:: 0xA0 0xA0 0xA0
   :trim:

.. _picos_for_qis:

.. role:: pyth(code)
   :language: python

PICOS for Quantum Information Science
=====================================

PICOS was among the first convex optimization interfaces to natively support
Hermitian semidefinite programming and subsystem manipulation operations such as
the partial trace and partial transpose, which were implemented with feedback
from the QIS community. This note outlines the features most relevant for the
field and links to examples.


Cheat sheet
-----------

.. list-table:: Complex expression manipulation
  :header-rows: 1

  * - on paper
    - in picos

  * - :math:`A \in \mathbb{C}^{m \times n}`
    - :pyth:`A = pc.ComplexVariable("A", (m, n))`

  * - :math:`A = B + iC`
    - :pyth:`A = B + 1j*C`

  * - :math:`\overline{A}`
    - :pyth:`A.conj`

  * - :math:`A^\dagger`
    - :pyth:`A.H`

  * - :math:`\Re(A)`
    - :pyth:`A.real`

  * - :math:`\Im(A)`
    - :pyth:`A.imag`

  * - :math:`\frac{1}{2} \left( A + A^\dagger \right)`
    - :pyth:`A.opreal` / :pyth:`A.hermitianized`

  * - :math:`\frac{1}{2i} \left( A - A^\dagger \right)`
    - :pyth:`A.opimag`

  * - :math:`\langle \phi \vert \psi \rangle`
    - :pyth:`phi.H * psi` / :pyth:`(phi | psi)`

  * - :math:`\rvert \phi \rangle \langle \psi \lvert`
    - :pyth:`phi * psi.H`


.. list-table:: Hermitian semidefinite programming
  :header-rows: 1

  * - on paper
    - in picos

  * - :math:`\rho \in \mathbb{S}^n`
    - :pyth:`rho = pc.HermitianVariable("ρ", n)`

  * - :math:`\rho \succeq 0`
    - :pyth:`rho >> 0`

  * - :math:`\rho \succeq I`
    - :pyth:`rho >> 1` / :pyth:`rho >> pc.I(n)`

  * - :math:`\operatorname{Tr}(\rho) = 1`
    - :pyth:`rho.tr == 1`

  * - :math:`\begin{bmatrix}A & B \\ C & D\end{bmatrix} \succeq 0`
    - :pyth:`pc.block([[A, B], [C, D]]) >> 0`


.. list-table:: Schatten norms
  :header-rows: 1

  * - on paper
    - in picos
    - note / aka

  * - :math:`{\lVert A \rVert}_1 = \operatorname{Tr}\left( \sqrt{A^\dagger A} \right)`
    - :pyth:`pc.NuclearNorm(A)`
    - *trace norm*

  * - :math:`{\lVert A \rVert}_\infty = \sqrt{\lambda_{\max}(A^\dagger A)}`
    - :pyth:`pc.SpectralNorm(A)`
    - :math:`\lambda_{\max}(A)` for :math:`A \in \mathbb{H}^n`


.. list-table:: Subsystem manipulation (partial trace, partial transpose, realignment)
  :header-rows: 1

  * - on paper
    - in picos
    - note / docs

  * - :math:`A = B \otimes C`
    - :pyth:`A = B @ C`
    -

  * - :math:`A_1 \otimes \cdots \otimes \operatorname{Tr}(A_i) \otimes \cdots \otimes A_n`
    - :pyth:`A.partial_trace([i-1], shapes)`
    - :meth:`~picos.expressions.exp_biaffine.BiaffineExpression.partial_trace`

  * - :math:`A_1 \otimes \cdots \otimes A_i^T \otimes \cdots \otimes A_n`
    - :pyth:`A.partial_tranpose([i-1], shapes)`
    - :meth:`~picos.expressions.exp_biaffine.BiaffineExpression.partial_transpose`

  * - :math:`A_{ij\;\mapsto\;ji} = A^T`
    - :pyth:`A.reshuffled("ji")`
    - :meth:`~picos.expressions.exp_biaffine.BiaffineExpression.reshuffled`

  * - :math:`A_{ijkl\;\mapsto\;kjil} = \operatorname{T}_1(A)`
    - :pyth:`A.reshuffled("kjil")`
    - :meth:`~picos.expressions.exp_biaffine.BiaffineExpression.reshuffled`

  * - :math:`\operatorname{Tr}_1(A),\;\ldots{},\;\operatorname{Tr}_4(A),\;\operatorname{Tr}_\text{last}(A)`
    - :pyth:`A.tr0`, ..., :pyth:`A.tr3`, :pyth:`A.trl`
    - :math:`A \in \mathbb{H}^2 \otimes \cdots \otimes \mathbb{H}^2`

  * - :math:`\operatorname{T}_1(A),\;\ldots{},\;\operatorname{T}_4(A),\;\operatorname{T}_\text{last}(A)`
    - :pyth:`A.T0`, ..., :pyth:`A.T3`, :pyth:`A.Tl`
    - :math:`A \in \mathbb{H}^2 \otimes \cdots \otimes \mathbb{H}^2`

(:math:`\operatorname{Tr}_i` and :math:`\operatorname{T}_i` denote the partial
trace and transpose of the :math:`i`-th :math:`2 \times 2` subsystem, counted
from zero)


Hermitian semidefinite programming
----------------------------------

PICOS makes use of the following identity to allow standard solvers to deal with
hermitian LMIs:

.. math::

  A \succeq 0
  \qquad
  \Longleftrightarrow
  \qquad
  \begin{bmatrix}
    \Re(A) & \Im(A) \\
    -\Im(A) & \Re(A)
  \end{bmatrix} \succeq 0

Hermitian variables are vectorized such that :math:`\rho \in \mathbb{S}^n` is
passed to solvers via :math:`n^2` real scalar variables. Alternatively, the
`QICS <https://qics.readthedocs.io/en/stable/>`__ solver is able
to directly handle hermitian variables.


Quantum relative entropy programming
------------------------------------

As of version 2.5.0, PICOS supports solving quantum relative entropy
programs with the solver `QICS <https://qics.readthedocs.io/en/stable/>`_. A
list of new expressions supported by PICOS and QICS is summarized below.

.. list-table:: Quantum entropies and non-commutative perspectives
  :header-rows: 1

  * - on paper |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_| |_|
    - in picos
    - docs

  * - :math:`S(X) = -\operatorname{Tr}(X\log(X))`
    - :pyth:`pc.quantentr(X)`
    - :meth:`~picos.expressions.exp_quantentr.QuantumEntropy`

  * - :math:`S(X \| Y) = \operatorname{Tr}(X\log(X) - X\log(Y))`
    - :pyth:`pc.quantrelentr(X, Y)`
    - :meth:`~picos.expressions.exp_quantentr.NegativeQuantumEntropy`

  * - :math:`S(X) - S(\operatorname{Tr}_i(X))`
    - :pyth:`pc.quantcondentr(X, [i-1], shapes)`
    - :meth:`~picos.expressions.exp_quantcondentr.QuantumConditionalEntropy`

  * - :math:`S(\mathcal{G}(X) \| \mathcal{Z}(\mathcal{G}(X)))`
    - :pyth:`pc.quantkeydist(X, [i-1], shapes, K_list)`
    - :meth:`~picos.expressions.exp_quantkeydist.QuantumKeyDistribution`

  * - :math:`P_{\log}(X, Y) = X^{1/2} \log(X^{1/2} Y^{-1} X^{1/2}) X^{1/2}`
    - :pyth:`pc.oprelentr(X, Y)`
    - :meth:`~picos.expressions.exp_oprelentr.OperatorRelativeEntropy`

  * - :math:`X\,\#_t\,Y = X^{1/2} (X^{1/2} Y^{-1} X^{1/2})^t X^{1/2}`
    - :pyth:`pc.mtxgeomean(X, Y, t)`
    - :meth:`~picos.expressions.exp_mtxgeomean.MatrixGeometricMean`

  * - :math:`\Psi_{\alpha}(X, Y) = \operatorname{Tr}[ X^\alpha Y^{1-\alpha} ]`
    - :pyth:`pc.quasientr(X, Y)`
    - :meth:`~picos.expressions.exp_renyientr.QuasiEntropy`

  * - :math:`\hat{\Psi}_{\alpha}(X, Y) = \operatorname{Tr}[ (Y^\frac{1-\alpha}{2\alpha} X Y^\frac{1-\alpha}{2\alpha} )^\alpha ]`
    - :pyth:`pc.sandquasientr(X, Y)`
    - :meth:`~picos.expressions.exp_renyientr.SandQuasiEntropy`

  * - :math:`D_\alpha(X \| Y) = \frac{1}{\alpha - 1} \log(\Psi_\alpha(X, Y))`
    - :pyth:`pc.renyientr(X, Y)`
    - :meth:`~picos.expressions.exp_renyientr.RenyiEntropy`

  * - :math:`\hat{D}_\alpha(X \| Y) = \frac{1}{\alpha - 1} \log(\hat{\Psi}_\alpha(X, Y))`
    - :pyth:`pc.sandrenyientr(X, Y)`
    - :meth:`~picos.expressions.exp_renyientr.SandRenyiEntropy`

Some examples for how to solve quantum relative entropy programs using PICOS can
be found :ref:`here <qrep>`. Note that these functions are supported for both
real symmetric and complex hermitian matrices :math:`X` and :math:`Y`.


Examples and exercises
----------------------

  - :ref:`Fidelity between operators <fidelity>`
  - :ref:`Quantum relative entropy programs <qrep>`
  - `Quantum channel discrimination
    <https://mybinder.org/v2/gl/picos-api%2Fmadrid23/HEAD?urlpath=tree/04_complex_sdps.ipynb>`__
    (exercise on Binder)


Course material
---------------

Jupyter notebooks for a hands-on workshop on practical semidefinite programming
aimed at quantum information students are available `on GitLab
<https://gitlab.com/picos-api/madrid23>`__. The fourth notebook is based on
[:ref:`2 <picos_for_qis_refs>`], which also comes with Python/PICOS `notebooks
<https://github.com/vsiddhu/SDP-Quantum-OR>`__.


Recent articles
---------------

The following are peer-reviewed articles relating to quantum information that
`cite PICOS <https://joss.theoj.org/papers/10.21105/joss.03915>`__ and were
published within the last four years (last update: October 2024).

- Vikesh Siddhu and John Smolin.

  *Maximum expectation of observables with restricted purity states.*

  **Quantum** 8, 2024.
  [`pdf <https://quantum-journal.org/papers/q-2024-08-13-1437/pdf/>`__]
  [`doi <https://doi.org/10.22331/q-2024-08-13-1437>`__]
  [`arXiv <https://arxiv.org/abs/2311.07680>`__]

- Aby Philip, Soorya Rethinasamy,Vincent Russo, and M. Wilde.

  *Schrödinger as a quantum programmer: estimating entanglement via steering.*

  **Quantum** 8, 2024.
  [`pdf <https://quantum-journal.org/papers/q-2024-06-11-1366/pdf/>`__]
  [`doi <https://doi.org/10.22331/q-2024-06-11-1366>`__]
  [`arXiv <https://arxiv.org/abs/2303.07911>`__]

- Piotr Mironowicz.

  *Semi-definite programming and quantum information.*

  **Journal of Physics A: Mathematical and Theoretical** 57, 2024.
  [`pdf <https://iopscience.iop.org/article/10.1088/1751-8121/ad2b85/pdf>`__]
  [`doi <https://doi.org/10.1088/1751-8121/ad2b85>`__]
  [`arXiv <https://arxiv.org/abs/2306.16560>`__]

- Yu Shi and Edo Waks.

  *Error metric for non-trace-preserving quantum operations.*

  **Physical Review A** 108, 2023.
  [`pdf <https://arxiv.org/pdf/2110.02290>`__]
  [`doi <https://doi.org/10.1103/PhysRevA.108.032609>`__]
  [`arXiv <https://arxiv.org/abs/2110.02290>`__]

- Vincent Russo and Jamie Sikora.

  *Inner products of pure states and their antidistinguishability.*

  **Physical Review A** 107, 2023.
  [`pdf <https://arxiv.org/pdf/2206.08313>`__]
  [`doi <https://doi.org/10.1103/PhysRevA.107.L030202>`__]
  [`arXiv <https://arxiv.org/abs/2206.08313>`__]
  [`code <https://github.com/vprusso/antidist>`__]

- Armin Tavakoli, Alejandro Pozas-Kerstjens, Ming-Xing Luo, and Marc-Olivier Renou.

  *Bell nonlocality in networks.*

  **Reports on Progress in Physics** 85, 2022.
  [`pdf <https://arxiv.org/pdf/2104.10700>`__]
  [`doi <https://doi.org/10.1088/1361-6633/ac41bb>`__]
  [`arXiv <https://arxiv.org/abs/2104.10700>`__]

- Feng-Jui Chan et al.

  *Maxwell's two-demon engine under pure dephasing noise.*

  **Physical Review A** 106, 2022.
  [`pdf <https://arxiv.org/pdf/2206.05921>`__]
  [`doi <https://doi.org/10.1103/PhysRevA.106.052201>`__]
  [`arXiv <https://arxiv.org/abs/2206.05921>`__]

- Viktor Nordgren et al.

  *Certifying emergent genuine multipartite entanglement with a partially blind witness.*

  **Physical Review A** 106, 2022.
  [`pdf <https://research-repository.st-andrews.ac.uk/bitstream/10023/26655/1/Nordgren_2022_PRA_Certifying_emergent_VoR.pdf>`__]
  [`doi <https://doi.org/10.1103/PhysRevA.106.062410>`__]
  [`arXiv <https://arxiv.org/abs/2103.07327>`__]

- Vikesh Siddhu and Sridhar Tayur.

  *Five starter pieces: quantum information science via semidefinite programs.*

  **Tutorials in Operations Research**, 2022.
  [`pdf <https://arxiv.org/pdf/2112.08276>`__]
  [`doi <https://doi.org/10.1287/educ.2022.0243>`__]
  [`arXiv <https://arxiv.org/abs/2112.08276>`__]

- Ulysse Chabaud, Pierre-Emmanuel Emeriau, and Frédéric Grosshans.

  *Witnessing Wigner negativity.*

  **Quantum** 5, 2021.
  [`pdf <https://arxiv.org/pdf/2102.06193>`__]
  [`doi <https://doi.org/10.22331/q-2021-06-08-471>`__]
  [`arXiv <https://arxiv.org/abs/2102.06193>`__]
  [`code <https://archive.softwareheritage.org/browse/directory/d98f70e386783ef69bf8c2ecafdb7b328b19b7ec/>`__]


Ncpol2sdpa
----------

`Ncpol2sdpa <https://ncpol2sdpa.readthedocs.io/en/stable/index.html>`_ [:ref:`1
<picos_for_qis_refs>`] exposes SDP relaxations of (non-commutative) polynomial
optimization problems as PICOS problem instances, see `here
<https://ncpol2sdpa.readthedocs.io/en/stable/exampleshtml.html#example-5-additional-manipulation-of-the-generated-sdps-with-picos>`__.


.. _picos_for_qis_refs:

References
----------

  1. Peter Wittek.
     Algorithm 950: Ncpol2sdpa—sparse semidefinite programming relaxations for
     polynomial optimization problems of noncommuting Variables.
     *ACM Transactions on Mathematical Software*, 41(3), 21, 2015.
     DOI: `10.1145/2699464 <https://doi.org/10.1145/2699464>`__.
     arXiv: `1308.6029 <http://arxiv.org/abs/1308.6029>`__.
  2. Vikesh Siddhu and Sridhar Tayur.
     Five starter pieces: quantum information science via semi-definite programs.
     *Tutorials in Operations Research*, 2022.
     DOI: `10.1287/educ.2022.0243 <https://doi.org/10.1287/educ.2022.0243>`__.
     arXiv: `2112.08276 <https://arxiv.org/abs/2112.08276>`__.
