"""
Boring Math
===========

These are the most resent *Boring Math* project PyPI releases.

======================================== ======================================= ========= =============
 PyPI and GitHub Name                    Python Module                           Version   Date Released
======================================== ======================================= ========= =============
 boring-math-combinatorics               boring_math.combinatorics               2.0.0     2025-10-09
 boring-math-integer-math [#]_           boring_math.integer_math                1.2.0     2025-10-09
 boring-math-number-theory               boring_math.number_theory               2.0.0     2025-10-09
 boring-math-probability-distributions   boring_math.probability_distributions   0.8.1     2025-08-04
 boring-math-pythagorean-triples         boring_math.pythagorean_triples         0.8.3     2025-10-09
 boring-math-recursive-functions         boring_math.recursive_functions         0.8.1     2025-08-04
 boring-math-special-functions           boring_math.special_functions           0.1.0     2025-10-TBD
======================================== ======================================= ========= =============

Remarks
-------

.. attention::
    Maintainer will try to keep these top level releases consistent
    with each other as much as possible.

.. important::

    When a package needs updated dependencies, the package
    will be deployed to PyPI first before any of the dependencies.
    This will prevent pip from installing the version of the package
    until all its dependencies are in place.

    When a package needs updating in a way that is not
    consistent with packages that depend on it, the packages
    dependent on it will be deployed to PyPI first.

.. note::

    In the development environment, packages and their
    dependencies are usually developed in parallel along
    with their test suites.

----

**Footnotes**

.. [#]

    **DEPRECATED:** boring-math-integer-math was broken up
    into two PyPI projects, ``boring-math-number-theory`` and
    ``boring-math-combinatorics``.

"""
