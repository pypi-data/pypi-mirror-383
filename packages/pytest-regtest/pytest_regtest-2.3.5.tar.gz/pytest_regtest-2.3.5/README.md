![](https://gitlab.com/uweschmitt/pytest-regtest/badges/main/pipeline.svg)
![](https://gitlab.com/uweschmitt/pytest-regtest/badges/main/coverage.svg?job=coverage)


The full documentation for this package are available at
https://pytest-regtest.readthedocs.org

# About

## Introduction

`pytest-regtest` is a plugin for [pytest](https://pytest.org) to implement
**regression testing**.

Unlike [functional testing](https://en.wikipedia.org/wiki/Functional_testing),
[regression testing](https://en.wikipedia.org/wiki/Regression_testing)
does not test whether the software produces the correct
results, but whether it behaves as it did before changes were introduced.

More specifically, `pytest-regtest` provides **snapshot testing**, which
implements regression testing by recording data within a test function
and comparing this recorded output to a previously recorded reference
output.


## Installation

To install and activate this plugin execute:

    $ pip install pytest-regtest


!!! note

     `pytest-regtest` provides some functionality specific to `NumPy`,
     `pandas`, and `polars`. These dependencies are not installed when
     you install `pytest-regtest`. For example, if you are using NumPy
     snapshots, we assume that your production code (the code under
     test) uses NumPy and therefore should be part of your project's
     setup.


## Use case 1: Changing code with no or little testing setup yet
If you're working with code that has little or no unit testing, you
can use regression testing to ensure that your changes don't break or
alter previous results.

**Example**:
This can be useful when working with data analysis scripts, which often
start as one long script and then are restructured into different
functions as they evolve.


## Use case 2:  Testing complex data
If a unit tests contains many `assert` statements to check a complex
data structure you can use regression tests instead.

**Example**: To test code which ingests data into a database one can
use regression tests on textual database dumps.

## Use case 3: Testing NumPy arrays or pandas data frames

If your code generates numerical results, such as `NumPy` arrays,
`pandas` or `polars` data frames, you can use `pytest-regtest` to simply record such
results and test them later, taking into account relative and absolute
tolerances.


**Example**:
A function creates a 10 x 10 matrix. Either you have to write 100
assert statements or you use summary statistics to test your result.
In both cases, you may get little debugging information if a test
fails.
