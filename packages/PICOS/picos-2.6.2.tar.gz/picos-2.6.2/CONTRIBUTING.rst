Contribution Guide
==================

Filing a bug report or feature request
--------------------------------------

.. rubric:: Via GitLab

If you have a GitLab account, just head to PICOS' official
`issue tracker <https://gitlab.com/picos-api/picos/issues>`_.

.. rubric:: Via mail

If you don't have a GitLab account you can still create an issue by writing to
`incoming+picos-api/picos@incoming.gitlab.com
<incoming+picos-api/picos@incoming.gitlab.com>`_. Unlike issues created directly
on GitLab, issues created by mail are *not* publicly visible.

Submitting a code change
------------------------

The canonical way to submit a code change is to

1. fork the `PICOS repository on GitLab <https://gitlab.com/picos-api/picos>`_,
2. clone your fork and make your application use it instead of your system's
   PICOS installation,
3. optionally create a local topic branch to work with,
4. modify the source and commit your changes, and lastly
5. make a pull request on GitLab so that we can test and merge your changes.

Code style
----------

Set your linter to enforce :pep:`8` and :pep:`257` except for the following
codes:

.. code::

    D105,D203,D213,D401,E122,E128,E221,E271,E272,E501,E702,E741

Our line width limit is ``80`` characters.

Release procedure
-----------------

.. rubric:: Version scheme

When installed from the git repository or from a source distribution (sdist),
PICOS versions have the format ``MAJOR.MINOR.PATCH``, where ``PATCH`` is the
commit distance to the last minor release. When installed from a source tarball
that carries no metadata from either git or setuptools, the version format is
just ``MAJOR.MINOR`` as the commit distance defining the ``PATCH`` bit is not
known. Note that the ``PATCH`` bit is not strictly incremental as not every
commit to the ``master`` branch is released individually.

.. rubric:: Bumping the version

To bump the major or minor version, run ``version.py -b MAJOR.MINOR``. This
commits that base version to the ``picos/.version`` file and creates an
annotated tag (``vMAJOR.MINOR``) for that commit. The release of version
``MAJOR.MINOR.0`` is then published by pushing the tagged commit to the top of
``origin/master``, which triggers a GitLab CI/CD pipeline for that commit. By
the same logic, the ``PATCH`` bit is bumped and the resulting version is
published automatically whenever a number of commits is pushed to the ``master``
branch between two minor versions.

Note that source distributions are aware of the ``PATCH`` bit as setuptools
writes it to the ``picos/.version`` file in the source tree.

.. rubric:: Justification

The result of this unorthodox release procedure is that bugfix releases can be
made quickly simply by pushing a commit to ``master``. On the other hand,
changes that should go into the next minor or major release must remain on topic
branches and pushed onto ``master`` together with the commit from
``version.py -b``.

Implementing a test case
------------------------

Production test sets are implemented in the files in the ``tests`` folder that
start with ``ptest_``. If you want to add to our test pool, feel free to either
extend these files or create a new set, whatever is appropriate. Make sure that
the tests you add are not too computationally expensive since they are also run
as part of our continuous integration pipeline whenever a commit is pushed to
GitLab.

Implementing a solver
---------------------

If you want to implement support for a new solver, all you have to do is update
``solvers/__init__.py`` where applicable, and add a file named
``solver_<name>.py`` in the same directory with your implementation. We
recommend that you read two or three of the existing solver implementations to
get an idea of how things are done. If you want to know exactly how PICOS
communicates with your implementation, refer to the solver base class in
``solver.py``.
