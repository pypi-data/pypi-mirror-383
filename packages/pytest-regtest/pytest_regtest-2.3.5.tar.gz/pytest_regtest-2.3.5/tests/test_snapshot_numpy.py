import pytest


@pytest.fixture
def setup_1d(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot_np_1d(snapshot):
            snapshot.check(np.array([1, 2, 3, 4.0]))
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot error(s) for test_snapshot_np_1d_*.py::test_snapshot_np_1d:",
            "",
            "snapshot not recorded yet:",
            "    > snapshot.check(np.array([1, 2, 3, 4.0]))",
            "    [1. 2. 3. 4.]",
        ],
        consecutive=True,
    )

    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)


@pytest.fixture
def setup_2d(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot(snapshot):
            snapshot.check(np.eye(4))
        """
    )

    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot error(s) for test_snapshot_np_2d_*.py::test_snapshot:",
            "",
            "snapshot not recorded yet:",
            "    > snapshot.check(np.eye(4))",
            "    [[1. 0. 0. 0.]",
            "     [0. 1. 0. 0.]",
            "     [0. 0. 1. 0.]",
            "     [0. 0. 0. 1.]]",
        ],
        consecutive=True,
    )

    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)


def test_snapshot_np_1d_dtype_mismatch(setup_1d, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot_np_1d(snapshot):
            snapshot.check(np.array([1, 2, 3, 4], dtype=np.int64))
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot error(s) for test_snapshot_np_1d_*.py::test_snapshot_np_1d:",
            "",
            "snapshot mismatch:",
            "    > test_snapshot_np_1d_*.py +3:",
            "    > snapshot.check(np.array([1, 2, 3, 4], dtype=np.int64))",
            "    dtype mismatch: current dtype: int64",
            "                   recorded dtype: float64",
        ],
        consecutive=True,
    )


def test_snapshot_np_1d_shape_mismatch(setup_1d, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot_np_1d(snapshot):
            snapshot.check(np.array([1, 2, 3, 4.0, 5.0]))
        """
    )

    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot mismatch:",
            "    > test_snapshot_np_1d_*.py +3:",
            "    > snapshot.check(np.array([1, 2, 3, 4.0, 5.0]))",
            "    shape mismatch: current shape: (5,)",
            "                   recorded shape: (4,)",
            "    ",
            "    --- current",
            "    +++ expected",
            "    @@ -1 +1 @@",
            "    -[1. 2. 3. 4. 5.]",
            "    +[1. 2. 3. 4.]",
        ],
        consecutive=True,
    )


def test_snapshot_np_1d_entry_changed(setup_1d, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot_np_1d(snapshot):
            snapshot.check(np.array([1, 2, 3, 4.00001]))
        """
    )

    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot mismatch:",
            "    > test_snapshot_np_1d_*.py +3:",
            "    > snapshot.check(np.array([1, 2, 3, 4.00001]))",
            "    max relative deviation: 2.500000e-06",
            "    max absolute deviation: 1.000000e-05",
            "    both arrays differ in 1 out of 4 entries",
            "    up to given precision settings rtol=0.000000e+00 and atol=0.000000e+00",
            "    ",
            "    --- current",
            "    +++ expected",
            "    @@ -1 +1 @@",
            "    -[1.      2.      3.      4.00001]",
            "    +[1. 2. 3. 4.]",
        ],
        consecutive=True,
    )


def test_snapshot_np_1d_entry_changed_rtol_atol(setup_1d, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot_np_1d(snapshot):
            snapshot.check(np.array([1, 2, 3, 4.00001]), rtol=1e-3)
        """
    )

    result = testdir.runpytest()
    assert_outcomes(result, passed=1)

    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot_np_1d(snapshot):
            snapshot.check(np.array([1, 2, 3, 4.00001]), atol=1e-3)
        """
    )

    result = testdir.runpytest()
    assert_outcomes(result, passed=1)


def test_snapshot_np_2d_shape_mismatch(setup_2d, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot(snapshot):
            # this is needed on CI because for whatever reason the runpytest below runs
            # the wrong file (caching?)
            snapshot.check(np.eye(5))
            print()
        """
    )

    result = testdir.runpytest("-s")
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "    > test_snapshot_np_2d_*.py +5:",
            "    > snapshot.check(np.eye(5))",
            "    shape mismatch: current shape: (5, 5)",
            "                   recorded shape: (4, 4)",
            "    --- current",
            "    +++ expected",
            "    row   0: -[1. 0. 0. 0. 0.]",
            "             +[1. 0. 0. 0.]",
            "    row   1: -[0. 1. 0. 0. 0.]",
            "             +[0. 1. 0. 0.]",
            "    row   2: -[0. 0. 1. 0. 0.]",
            "             +[0. 0. 1. 0.]",
            "    row   3: -[0. 0. 0. 1. 0.]",
            "             +[0. 0. 0. 1.]",
        ],
        consecutive=True,
    )


def test_snapshot_np_2d_with_printoptions(setup_2d, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot(snapshot):
            with np.printoptions(precision=3, sign="+", floatmode="fixed"):
                snapshot.check(np.eye(4) * 1.001)
        """
    )

    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot mismatch:",
            "    > test_snapshot_np_2d_*.py +4:",
            "    > snapshot.check(np.eye(4) * 1.001)",
            "    max relative deviation: 1.000000e-03",
            "    max absolute deviation: 1.000000e-03",
            "    both arrays differ in 4 out of 16 entries",
            "    up to given precision settings rtol=0.000000e+00"  # no , here!
            " and atol=0.000000e+00",
            "    --- current",
            "    +++ expected",
            "    row   0: -[+1.001 +0.000 +0.000 +0.000]",
            "             +[+1.000 +0.000 +0.000 +0.000]",
            "    row   1: -[+0.000 +1.001 +0.000 +0.000]",
            "             +[+0.000 +1.000 +0.000 +0.000]",
            "    row   2: -[+0.000 +0.000 +1.001 +0.000]",
            "             +[+0.000 +0.000 +1.000 +0.000]",
            "    row   3: -[+0.000 +0.000 +0.000 +1.001]",
            "             +[+0.000 +0.000 +0.000 +1.000]",
        ],
        consecutive=True,
    )


def test_snapshot_np_2d_with_printoptions_and_rtol(setup_2d, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot(snapshot):
            snapshot.check(np.eye(4) * 1.001, rtol=1e-2,
                           print_options=dict(precision=3, sign="+", floatmode="fixed")
                          )
        """
    )

    result = testdir.runpytest("--regtest-tee", "-v")
    assert_outcomes(result, passed=1)
    result.stdout.fnmatch_lines(
        [
            "test_snapshot_np_2d_*.py::test_snapshot PASSED*",
            "recorded snapshots: ----------*",
            "> test_snapshot_np_2d_*.py +3",
            "> snapshot.check(np.eye(4) * 1.001, rtol=1e-2,",
            "[[+1.001 +0.000 +0.000 +0.000]",
            " [+0.000 +1.001 +0.000 +0.000]",
            " [+0.000 +0.000 +1.001 +0.000]",
            " [+0.000 +0.000 +0.000 +1.001]]",
            "------------------------------*",
            "",
        ]
    )


def test_snapshot_np_2d_different_entry(setup_2d, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot(snapshot):
            ma = np.eye(4)
            ma[2, 2] = 2.0
            snapshot.check(ma)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    lines = [
        "snapshot mismatch:",
        "    > test_snapshot_np_2d_*.py +5:",
        "    > snapshot.check(ma)",
        "    max relative deviation: 1.000000e+00",
        "    max absolute deviation: 1.000000e+00",
        "    both arrays differ in 1 out of 16 entries",
        "    up to given precision settings rtol=0.000000e+00 and atol=0.000000e+00",
        "    --- current",
        "    +++ expected",
        "    row   2: -[0. 0. 2. 0.]",
        "             +[0. 0. 1. 0.]",
    ]
    result.stdout.fnmatch_lines(lines, consecutive=True)


def test_snapshot_np_2d_print_options_depreciation_warning(
    setup_2d, testdir, assert_outcomes
):
    testdir.makepyfile(
        """
        import numpy as np
        import pytest
        def test_snapshot(snapshot, recwarn):
            ma = np.eye(4)
            with pytest.warns(DeprecationWarning) as record:
                snapshot.check(ma,
                               print_options=dict(precision=3, sign="+",
                                                  floatmode="fixed")
                               )
                assert recore[0].message.args[0] == "xxx"
        """
    )
    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, failed=1)


def test_snapshot_np_2d_empty_diff(setup_2d, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        import pytest
        def test_snapshot(snapshot, recwarn):
            ma = np.eye(4)
            ma[2, 2] = 1.0002
            with np.printoptions(precision=3, sign="+", floatmode="fixed"):
                snapshot.check(ma)
        """
    )
    result = testdir.runpytest("--regtest-tee", "-v")
    assert_outcomes(result, failed=1)
    lines = [
        "snapshot mismatch:",
        "    > test_snapshot_np_2d_*.py +7:",
        "    > snapshot.check(ma)",
        "    max relative deviation: 2.000000e-04",
        "    max absolute deviation: 2.000000e-04",
        "    both arrays differ in 1 out of 16 entries",
        "    up to given precision settings rtol=0.000000e+00 and atol=0.000000e+00",
        "    diff is empty, you may want to change the print options",
    ]
    result.stdout.fnmatch_lines(lines, consecutive=True)


def test_snapshot_np_2d_atol_rtol(setup_2d, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot(snapshot):
            ma = np.eye(4)
            ma[2, 2] = 1.0002
            snapshot.check(ma, atol=1e-4)
        """
    )
    result = testdir.runpytest("--regtest-tee", "-v")
    assert_outcomes(result, failed=1)

    lines = [
        "snapshot mismatch:",
        "    > test_snapshot_np_2d_*.py +5:",
        "    > snapshot.check(ma, atol=1e-4)",
        "    max relative deviation: 2.000000e-04",
        "    max absolute deviation: 2.000000e-04",
        "    both arrays differ in 1 out of 16 entries",
        "    up to given precision settings rtol=0.000000e+00 and atol=1.000000e-04",
    ]
    result.stdout.fnmatch_lines(lines, consecutive=True)

    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot(snapshot):
            ma = np.eye(4)
            ma[2, 2] = 1.0002
            snapshot.check(ma, atol=1e-3)
        """
    )
    result = testdir.runpytest("--regtest-tee", "-v")
    assert_outcomes(result, passed=1)

    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot(snapshot):
            ma = np.eye(4)
            ma[2, 2] = 1.0002
            snapshot.check(ma, rtol=1e-4)
        """
    )
    result = testdir.runpytest("--regtest-tee", "-v")
    assert_outcomes(result, failed=1)
    lines = [
        "snapshot mismatch:",
        "    > test_snapshot_np_2d_*.py +5:",
        "    > snapshot.check(ma, rtol=1e-4)",
        "    max relative deviation: 2.000000e-04",
        "    max absolute deviation: 2.000000e-04",
        "    both arrays differ in 1 out of 16 entries",
        "    up to given precision settings rtol=1.000000e-04 and atol=0.000000e+00",
    ]
    result.stdout.fnmatch_lines(lines, consecutive=True)


def test_binary_output(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot_np_2d(regtest):
            print(chr(25), file=regtest)
        """
    )

    result = testdir.runpytest("--regtest-tee", "-v")
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "  def test_snapshot_np_2d(regtest):",
            "E       recorded output for regression test"
            " contains unprintable characters.",
        ]
    )


def test_snapshot_np_3d(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot_np_3d(snapshot):
            cube = np.arange(8).reshape(2, 2, 2)
            snapshot.check(cube)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot error(s) for test_snapshot_np_3d.py::test_snapshot_np_3d:",
            "",
            "snapshot not recorded yet:",
            "    > snapshot.check(cube)",
            "    [[[0 1]",
            "      [2 3]]",
            "    ",
            "     [[4 5]",
            "      [6 7]]]",
        ],
        consecutive=True,
    )

    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)

    result = testdir.runpytest()
    assert_outcomes(result, passed=1)

    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot_np_3d(snapshot):
            cube = np.arange(8).reshape(2, 2, 2)
            cube[0, 0] = 1.0
            snapshot.check(cube)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot mismatch:",
            "    > test_snapshot_np_3d.py +5:",
            "    > snapshot.check(cube)",
            "    max relative deviation: inf",
            "    max relative deviation except inf: 0.000000e+00",
            "    max absolute deviation: 1.000000e+00",
            "    both arrays differ in 1 out of 8 entries",
            "    up to given precision settings rtol=0.000000e+00"  # no , here!
            " and atol=0.000000e+00",
        ],
        consecutive=True,
    )


def test_numpy_eq_nan(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot_np_1d(snapshot):
            snapshot.check(np.array([1, 2, 3, np.nan]))
        """
    )

    result = testdir.runpytest()
    assert_outcomes(result, failed=1)

    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)

    result = testdir.runpytest()
    assert_outcomes(result, passed=1)

    testdir.makepyfile(
        """
        import numpy as np
        def test_snapshot_np_1d(snapshot):
            snapshot.check(np.array([1, 2, 3, np.nan]), equal_nan=False)
        """
    )

    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
