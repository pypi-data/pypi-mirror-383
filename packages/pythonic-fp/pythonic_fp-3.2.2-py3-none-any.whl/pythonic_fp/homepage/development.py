"""
Semantic versioning
===================

Maintainer has adopted strict 3 digit `semantic versioning <https://semver.org>`_
and does not put `caps on dependencies <https://iscinumpy.dev/post/bound-version-constraints>`_.

This allows for more package management flexibility for software developers using these
libraries, and easier access to the latest features. For those concerned with stability,
periodically known consistent sets of releases are given in the Releases section of
these docs.

Changelog
=========

Pythonic FP overarching
`CHANGELOG <https://github.com/grscheller/pythonic-fp/blob/main/CHANGELOG.rst>`_.

Each individual *Pythonic FP* project has its own CHANGELOG too.

Module Dependencies
===================

Arrows point from modules to their dependencies.

Internal
--------

There are no external dependency except for the Python standard library.

.. graphviz::

    digraph Modules {
        bgcolor="#957fb8";
        node [style=filled, fillcolor="#181616", fontcolor="#dcd7ba"];
        edge [color="#181616", fontcolor="#dcd7ba"];
        containers -> fptools;
        containers -> iterables;
        containers -> circulararray;
        splitends -> fptools;
        splitends -> iterables;
        splitends -> queues;
        queues -> fptools;
        queues -> circulararray;
        circulararray -> gadgets;
        fptools -> circulararray;
        fptools -> gadgets;
        fptools -> booleans;
        booleans -> gadgets;
        iterables -> gadgets;
        iterables -> fptools;
    }

External
--------

All Python Std Library non-typing related dependencies.

.. graphviz::

    digraph Modules {
        bgcolor="#957fb8";
        node [style=filled, fillcolor="#181616", fontcolor="#dcd7ba"];
        edge [color="#181616", fontcolor="#dcd7ba"];
        booleans -> threading;
        gadgets -> inspect;
        gadgets -> threading;
        iterables -> enum;
    }

"""
