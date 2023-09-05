========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |github-actions|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/pyknowbase/badge/?style=flat
    :target: https://pyknowbase.readthedocs.io/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/mrtj/pyknowbase/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/mrtj/pyknowbase/actions

.. |codecov| image:: https://codecov.io/gh/mrtj/pyknowbase/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://app.codecov.io/github/mrtj/pyknowbase

.. |version| image:: https://img.shields.io/pypi/v/pyknowbase.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/pyknowbase

.. |wheel| image:: https://img.shields.io/pypi/wheel/pyknowbase.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/pyknowbase

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/pyknowbase.svg
    :alt: Supported versions
    :target: https://pypi.org/project/pyknowbase

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/pyknowbase.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/pyknowbase

.. |commits-since| image:: https://img.shields.io/github/commits-since/mrtj/pyknowbase/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/mrtj/pyknowbase/compare/v0.0.0...main



.. end-badges

Python library managing textual knowledge bases.

* Free software: MIT license

Installation
============

::

    pip install pyknowbase

You can also install the in-development version with::

    pip install https://github.com/mrtj/pyknowbase/archive/main.zip


Documentation
=============


https://pyknowbase.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
