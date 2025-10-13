CHANGELOG
=========

Daddy's boring math library
---------------------------

Mathematical hobby projects. Done under the PyPI boring-math namespace.

The name of this library was suggested by my then 13 year old daughter Mary.

Release based versioning
------------------------

Unlike the PyPI projects that make up Boring Math, which use strict semantic versioning,
the overall version number is based on consistent relative release. The release string
changes when

- **MAJOR:** a consistent, coordinated release of Boring Math PyPI projects happens
- **MINOR:** breaking API changes are made to a Boring Math PyPI project
- **PATCH:** minor code improvements and homepage updates are made

Important Milestones
--------------------

2025-10-12 - PyPI Boring Math release 2.0.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Minor homepage consistency changes with Pythonic FP.

2025-10-11 - PyPI Boring Math release 2.0.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Decided to make this a consistent coordinated release anyway. I want to
get the documentation in a more or less final structural form so that I
can concentrate on further software development.

Updated for boring-math-recursive-functions (API changes - minor bump)
First release boring-math-special-functions (still empty shell - patch bump)

========================================  =========
 PyPI and GitHub Name                     Version  
========================================  =========
 boring-math-combinatorics                2.0.0
 boring-math-number-theory                2.0.0
 boring-math-probability-distributions    0.8.1
 boring-math-pythagorean-triples          0.8.3
 boring-math-recursive-functions          1.0.0
 boring-math-special-functions            0.1.0
========================================  =========

2025-10-09 - PyPI Boring Math release 1.2.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Updated for boring-math-pythagorean-triples 1.8.3

In retrospect, last version bump boring-math should
have been 1.2.0 and not the 1.1.4 version.
      
2025-10-09 - PyPI Boring Math release 1.1.4
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- released boring-math-combinatorics 2.0.0
- released boring-math-number-theory 2.0.0

2025-10-09 - Split up boring-math-integer-math
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deprecating boring-math-integer-math, split it into 2 PyPI projects.

- boring-math-combinatorics
- boring-math-number-theory


2025-10-05 - Converted from Piccolo to Furo Theme
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Furo a bit old school, but very readable. Some tweaking will be needed.


2025-10-04 - Finished initial Sphinx migration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Things are good enough content-wise until I do some real work.

TODO:

- finish Boring Math homepage
- find another Sphinx dark theme

  - Piccolo theme does not make tables, code blocks, and separators stand out too well
  - heard good things about the Furo theme

    - simple, uncluttered design without a lot of built-in components.
    - maximum readability for your content.
    - ability to easily customize colors and fonts using modern CSS variables. 

2025-09-29 - Redoing infrastructure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Redoing entire project's infrastructure along the lines of ``pythonic-fp``.

- update code

  - no code changes needed for updated version of Pythonic FP
  - removed all ``from __future__ import annotation`` from the code

    - made the necessary typing changes to accomplish this
    - should not require a bump in major version

- created a Sphinx based homepage for the overall Boring Math effort

  - still need to update to Sphinx the individual Boring Math PyPI projects
  - still need to plumb in the old pdoc documentation

- both Boring Math and Pythonic FP use .github/workflows/static.yml

  - both configured to use GitHub Actions
  - quite a bit of thrashing to get things straightened out

2025-08-04 - PyPI Boring Math release 1.1.3
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

I created a separate CHANGELOG for the ``boring_math.special_functions``
package. It is in Markdown format. The entire Boring Math effort and
the special functions package will share the same version number.

I am adopting what I did for for my Pythonic Functional Programming
namespace (pythonic-fp) projects. I will keep the information I maintain
in README files to a minimum and driver Sphinx based documentation based
on the content of docstrings. 

Here is what got installed when I downloaded boring-math namespace packages.

.. code-block:: console

    $ pip list | grep boring
    boring-math                           1.1.3
    boring-math-integer-math              1.0.2
    boring-math-probability-distributions 0.8.0
    boring-math-pythagorean-triples       0.8.2
    boring-math-recursive-functions       0.8.0

    $ pip list | grep pythonic
    pythonic-fp                           1.1.0
    pythonic-fp-circulararray             5.3.1
    pythonic-fp-fptools                   5.0.0
    pythonic-fp-iterables                 5.0.0
    pythonic-fp-singletons                1.0.0

2025-08-04 - PyPI releases boring-math & boring-math-integer-math
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Released boring-math 1.1.2 & boring-math-integer-math 0.8.1. Using these
two to iron out the release process. Still need to bootstrap Sphinx
documentation. As I correct problems with these, I update the rest of
the boring math repos.

2025-07-30 - changing namespace to boring-math
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The boring-math name is not claimed on PyPI. I set up a stub project
under that name like I did with pythonic-fp. I will also move the
recursive-functions project to it. The other 3 will have to wait until
I deploy the next parallel release of my pythonic-fp PyPI projects.

2025-07-14 - pythonic-fp migration complete
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Migration complete, all dtools PyPI projects and corresponding GitHub
repos have been archived. 

Latest PyPI Releases for

- bm.integer-math 0.7.1
- bm.probability-distributions 0.7.1
- bm.pythagorean-triples 0.6.1
- bm.recursive-functions 0.6.1

Also got rid of links to the old grscheller.bm documentation.


2025-07-13 - pythonic-fp migration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Migrating dependencies from dtools to pythonic-fp PyPI namespace. Once
completed, I plan to archive my PyPI and GitHub dtools namespace repos.

2025-04-22 - Renamed repo
~~~~~~~~~~~~~~~~~~~~~~~~~

This project is a collection of PyPI namespace projects all under the ``bm``
namespace name. Did not realize at the time that the ``bm`` name was already
taken on PyPI.

- renamed ``grscheller/boring-math-docs`` GitHub repo to ``grscheller/bm-docs`` 
- created this CHANGELOG.md file
- is not associated with

  - either the ``https://pypi.org/project/bm`` PyPI project
  - or the ``https://github.com/cym13/bookmark`` GitHub repo

