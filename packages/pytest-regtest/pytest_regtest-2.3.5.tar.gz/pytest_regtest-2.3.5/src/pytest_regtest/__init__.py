from importlib.metadata import version as _version

import pytest

from .pytest_regtest import clear_converters  # noqa: F401
from .pytest_regtest import patch_terminal_size  # noqa: F401
from .pytest_regtest import register_converter_post  # noqa: F401
from .pytest_regtest import register_converter_pre  # noqa: F401
from .pytest_regtest import (
    PytestRegtestCommonHooks,
    PytestRegtestPlugin,
    RegtestStream,
    Snapshot,
    SnapshotPlugin,
)
from .register_third_party_handlers import (
    register_numpy_handler,
    register_pandas_handler,
    register_polars_handler,
)
from .snapshot_handler import register_python_object_handler

__version__ = _version(__package__)


def pytest_addoption(parser):
    """Add options to control the timeout plugin"""
    group = parser.getgroup("regtest", "regression test plugin")
    group.addoption(
        "--regtest-reset",
        action="store_true",
        help="do not run regtest but record current output",
    )
    group.addoption(
        "--regtest-tee",
        action="store_true",
        default=False,
        help="print recorded results to console too",
    )
    group.addoption(
        "--regtest-consider-line-endings",
        action="store_true",
        default=False,
        help="do not strip whitespaces at end of recorded lines",
    )
    group.addoption(
        "--regtest-nodiff",
        action="store_true",
        default=False,
        help="do not show diff output for failed regresson tests",
    )
    group.addoption(
        "--regtest-disable-stdconv",
        action="store_true",
        default=False,
        help=(
            "do not apply standard output converters to clean up indeterministic output"
        ),
    )


def pytest_configure(config):
    common = PytestRegtestCommonHooks()
    config.pluginmanager.register(common)
    config.pluginmanager.register(PytestRegtestPlugin(common))
    config.pluginmanager.register(SnapshotPlugin(common))


@pytest.fixture
def regtest(request):
    yield RegtestStream(request)


@pytest.fixture
def snapshot(request):
    yield Snapshot(request)


@pytest.fixture
def regtest_all(regtest):
    yield regtest


snapshot_all_output = regtest_all

register_python_object_handler()

try:
    import pandas  # noqa: F401

    register_pandas_handler()
except ImportError:
    pass

try:
    import numpy  # noqa: F401

    register_numpy_handler()
except ImportError:
    pass

try:
    import polars  # noqa: F401

    register_polars_handler()
except ImportError:
    pass
