import sys

import numpy
import pdbp  # noqa
import pytest

# hack to disable reload numpy in pytester (current code only prevent reload of
# zope, so we trick pytester:
# (see also _pytest/pytester.py  __take_sys_modules_snapshot method)
sys.modules["zope"] = numpy

pytest_plugins = ["pytester"]

# for whatever reason pytester loaded the old bytcode in one test and caused it
# to fail:
sys.dont_write_bytecode = True


@pytest.fixture
def assert_outcomes():
    def check(result, **kw):
        try:
            result.assert_outcomes(**kw)
        except AssertionError:
            outcome = result.parseoutcomes()
            message = f"expected: {kw}\ngot: {outcome}\n\n" + result.stdout.str()
            raise AssertionError(message)

    yield check
