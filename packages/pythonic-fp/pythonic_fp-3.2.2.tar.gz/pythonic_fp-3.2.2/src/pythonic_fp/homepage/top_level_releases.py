"""
Pythonic FP
===========

These are the most resent *Pythonic FP* project PyPI releases.

============================ =========================== ========= =============
PyPI and GitHub Name         Python Module               Version   Date Released
============================ =========================== ========= =============
pythonic-fp-booleans         pythonic_fp.booleans        2.0.0     2025-09-27
pythonic-fp-circulararray    pythonic_fp.circulararray   6.0.0     2025-09-26
pythonic-fp-containers       pythonic_fp.containers      4.0.0     2025-09-28
pythonic-fp-fptools          pythonic_fp.fptools         5.1.2     2025-09-28
pythonic-fp-gadgets          pythonic_fp.gadgets         3.1.0     2025-09-26
pythonic-fp-iterables        pythonic_fp.iterables       5.1.2     2025-09-28
pythonic-fp-queues           pythonic_fp.queues          5.1.0     2025-09-26
pythonic-fp-sentinels [#]_   pythonic_fp.sentinels       2.1.3     2025-08-02
pythonic-fp-singletons [#]_  pythonic_fp.singletons      1.0.0     2025-09-25
pythonic-fp-splitends        pythonic_fp.splitends       2.0.0     2025-09-28
============================ =========================== ========= =============

Remarks
-------

.. attention::
    Maintainer will try to keep these top level releases consistent
    with each other as much as possible.

.. important::

    When a package needs updated dependencies, the package will be
    deployed to PyPI first before any of its internal dependencies.
    This will prevent pip from installing the version of the package
    until all its dependencies are in place.

.. note::

    In the development environment, packages and their
    dependencies are usually developed in parallel along
    with their test suites.

----

**Footnotes**

.. [#]

    Project **pythonic-fp-sentinels** was **DEPRECATED**. Content was moved
    to pythonic-fp-gadgets.

.. [#]

    Project **pythonic-fp-singletons** was **DEPRECATED**. Its GitHub repo was
    repurposed for ``pythonic-fp-sentinels`` and the Boolean content was moved
    to a new PyPI project, ``pythonic-fp-booleans``. Naming a module after an
    implementation detail turned out not to scale well.

"""
