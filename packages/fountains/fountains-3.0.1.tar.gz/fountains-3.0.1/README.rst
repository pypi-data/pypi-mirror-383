=========
fountains
=========

Python library for generating and concisely specifying reproducible pseudorandom binary data for unit testing.

|pypi| |readthedocs| |actions| |coveralls|

.. |pypi| image:: https://badge.fury.io/py/fountains.svg#
   :target: https://badge.fury.io/py/fountains
   :alt: PyPI version and link.

.. |readthedocs| image:: https://readthedocs.org/projects/fountains/badge/?version=latest
   :target: https://fountains.readthedocs.io/en/latest/?badge=latest
   :alt: Read the Docs documentation status.

.. |actions| image:: https://github.com/reity/fountains/workflows/lint-test-cover-docs/badge.svg#
   :target: https://github.com/reity/fountains/actions/workflows/lint-test-cover-docs.yml
   :alt: GitHub Actions status.

.. |coveralls| image:: https://coveralls.io/repos/github/reity/fountains/badge.svg?branch=main
   :target: https://coveralls.io/github/reity/fountains?branch=main
   :alt: Coveralls test coverage summary.

Purpose
-------
This library makes it possible to generate pseudorandom binary test data in a reproducible way, as well as to embed concise specifications of correct function behavior on that test data. This enables the construction of functional tests within unit testing suites that fit within one-line definitions but still test a function's behavior against a large number of inputs. More background information about this library's purpose, design, and implementation can be found in a `related article <https://github.com/reity/article-specifications-for-distinguishing-functions>`__.

Installation and Usage
----------------------
This library is available as a `package on PyPI <https://pypi.org/project/fountains>`__:

.. code-block:: bash

    python -m pip install fountains

The library can be imported in the usual manner:

.. code-block:: python

    import fountains
    from fountains import fountains

Examples
^^^^^^^^

.. |fountains| replace:: ``fountains``
.. _fountains: https://fountains.readthedocs.io/en/3.0.1/_source/fountains.html#fountains.fountains.fountains

An object of the |fountains|_ class can be used to generate pseudorandom binary test data:

.. code-block:: python

    >>> [bs.hex() for bs in fountains(length=3, limit=4)]
    ['e3b0c4', 'ce1bc4', '2ed5b5', '781f5a']

Supplying a function as a parameter to a |fountains|_ object makes it possible to generate a concise (but necessarily incomplete) specification for that function's behavior on a stream of pseudorandom inputs:

.. code-block:: python

    >>> add = lambda bs: bytes([(bs[0] + bs[1] + bs[2]) % 256])
    >>> bits = list(fountains(3, 8, function=add))
    >>> bits
    [0, 0, 1, 1, 1, 0, 1, 0]

When converted to a hexadecimal string, this specification encodes partial information about four distinct input-output test cases in every character:

.. code-block:: python

    >>> from bitlist import bitlist
    >>> bitlist(bits).hex()
    '3a' # Partial outputs from eight distinct tests.

Supplying the specification generated in the manner above as an additional parameter makes it possible to test the function's behavior:

.. code-block:: python

    >>> list(fountains(3, 8, function=add, bits='3a'))
    [True, True, True, True, True, True, True, True]

Each individual boolean value in the above represents the result of an individual test case. A different function might not satisfy the same partial specification:

.. code-block:: python

    >>> mul = lambda bs: bytes([(bs[0] * bs[1] * bs[2]) % 256])
    >>> list(fountains(3, 8, function=mul, bits='3a'))
    [True, False, True, True, False, True, False, True]

Each boolean value in the outputs of the last two code blocks above may be a false negative (i.e., ``True`` may mean that the function satisfies the specification only in a portion of its output for the corresponding input) but is *never a false positive signal of incorrect behavior* (i.e., ``False`` indicates the function does not satisfy the specification for the corresponding input-output pair).

Development
-----------
All installation and development dependencies are fully specified in ``pyproject.toml``. The ``project.optional-dependencies`` object is used to `specify optional requirements <https://peps.python.org/pep-0621>`__ for various development tasks. This makes it possible to specify additional options (such as ``docs``, ``lint``, and so on) when performing installation using `pip <https://pypi.org/project/pip>`__:

.. code-block:: bash

    python -m pip install ".[docs,lint]"

Documentation
^^^^^^^^^^^^^
The documentation can be generated automatically from the source files using `Sphinx <https://www.sphinx-doc.org>`__:

.. code-block:: bash

    python -m pip install ".[docs]"
    cd docs
    sphinx-apidoc -f -E --templatedir=_templates -o _source .. && make html

Testing and Conventions
^^^^^^^^^^^^^^^^^^^^^^^
All unit tests are executed and their coverage is measured when using `pytest <https://docs.pytest.org>`__ (see the ``pyproject.toml`` file for configuration details):

.. code-block:: bash

    python -m pip install ".[test]"
    python -m pytest

Alternatively, all unit tests are included in the module itself and can be executed using `doctest <https://docs.python.org/3/library/doctest.html>`__:

.. code-block:: bash

    python src/fountains/fountains.py -v

Style conventions are enforced using `Pylint <https://pylint.readthedocs.io>`__:

.. code-block:: bash

    python -m pip install ".[lint]"
    python -m pylint src/fountains

Contributions
^^^^^^^^^^^^^
In order to contribute to the source code, open an issue or submit a pull request on the `GitHub page <https://github.com/reity/fountains>`__ for this library.

Versioning
^^^^^^^^^^
Beginning with version 0.2.0, the version number format for this library and the changes to the library associated with version number increments conform with `Semantic Versioning 2.0.0 <https://semver.org/#semantic-versioning-200>`__.

Publishing
^^^^^^^^^^
This library can be published as a `package on PyPI <https://pypi.org/project/fountains>`__ via the GitHub Actions workflow found in ``.github/workflows/build-publish-sign-release.yml`` that follows the `recommendations found in the Python Packaging User Guide <https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/>`__.

Ensure that the correct version number appears in ``pyproject.toml``, and that any links in this README document to the Read the Docs documentation of this package (or its dependencies) have appropriate version numbers. Also ensure that the Read the Docs project for this library has an `automation rule <https://docs.readthedocs.io/en/stable/automation-rules.html>`__ that activates and sets as the default all tagged versions.

To publish the package, create and push a tag for the version being published (replacing ``?.?.?`` with the version number):

.. code-block:: bash

    git tag ?.?.?
    git push origin ?.?.?
