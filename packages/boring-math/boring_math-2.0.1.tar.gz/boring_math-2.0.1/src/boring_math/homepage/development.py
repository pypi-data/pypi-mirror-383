"""
Semantic Versioning
===================

Maintainer has adopted strict 3 digit `semantic versioning <https://semver.org>`_
and does not put `caps on dependencies <https://iscinumpy.dev/post/bound-version-constraints>`_.

This allows for more package management flexibility for software developers using these
projects as libraries, For those concerned with stability, periodically known consistent
sets of releases are given in the Releases section of these docs.

Changelog
=========

Pythonic FP overarching
`CHANGELOG <https://github.com/grscheller/boring-math/blob/main/CHANGELOG.rst>`_.

Each individual *Boring Math* project has its own CHANGELOG too.

Module Dependencies
===================

All non-typing related dependencies. Arrows point from modules to their dependencies.

.. graphviz::

    digraph Modules {
        bgcolor="#957fb8";
        node [style=filled, fillcolor="#181616", fontcolor="#dcd7ba"];
        edge [color="#181616", fontcolor="#dcd7ba"];
        combinatorics -> "pythonic_fp.circulararray";
        combinatorics -> "pythonic_fp.iterables";
        combinatorics -> number_theory;
        number_theory -> "pythonic_fp.circulararray";
        number_theory -> "pythonic_fp.iterables";
        probability_distributions -> math;
        probability_distributions -> "mathplotlib.pyplot";
        probability_distributions -> "pythonic_fp.fptools";
        pythagorean_triples -> sys;
        pythagorean_triples -> number_theory;
        recursive_functions -> sys;
        recursive_functions -> "pythonic_fp.iterables";
    }

"""
