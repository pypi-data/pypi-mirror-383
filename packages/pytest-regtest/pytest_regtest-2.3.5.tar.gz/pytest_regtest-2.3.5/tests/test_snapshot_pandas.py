import pytest


@pytest.fixture
def setup_pd(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import pandas as pd

        def test_snapshot_dataframe(snapshot):
            df = pd.DataFrame(
                dict(
                    a=[1, 2, 3],
                    b=["a", "b", "c"],
                    c=[1.0, 1.5, 2.0],
                )
            )
            snapshot.check(df)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.lines
    result.stdout.fnmatch_lines(
        [
            "snapshot error(s) for test_snapshot_pandas*.py::test_snapshot_dataframe:",
            "",
            "snapshot not recorded yet:",
            "    > snapshot.check(df)",
            "       a  b    c",
            "    0  1  a  1.0",
            "    1  2  b  1.5",
            "    2  3  c  2.0",
        ],
        consecutive=True,
    )

    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)

    result = testdir.runpytest()
    assert_outcomes(result, passed=1)


def test_snapshot_pandas_changed_entry(setup_pd, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import pandas as pd

        def test_snapshot_dataframe(snapshot):
            df = pd.DataFrame(
                dict(
                    a=[1, 2, 3],
                    b=["a", "b", "c"],
                    c=[1.0, 1.5, 3.0],
                )
            )
            snapshot.check(df)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot mismatch:",
            "    > test_snapshot_pandas_*.py +11:",
            "    > snapshot.check(df)",
            "    ",
            "    --- current",
            "    +++ expected",
            "    @@ -1,4 +1,4 @@",
            "        a  b    c",
            "     0  1  a  1.0",
            "     1  2  b  1.5",
            "    -2  3  c  3.0",
            "    +2  3  c  2.0",
        ],
        consecutive=True,
    )


def test_snapshot_pandas_empty_diff(setup_pd, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import pandas as pd
        import pytest

        def test_snapshot_dataframe(snapshot):
            df = pd.DataFrame(
                dict(
                    a=[1, 2, 3],
                    b=["a", "b", "c"],
                    c=[1.0, 1.5, 2.000001],
                )
            )
            with pd.option_context("display.precision", 3):
                snapshot.check(df)
        """
    )
    result = testdir.runpytest("-s")
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot mismatch:",
            "    > test_snapshot_pandas_*.py +13:",
            "    > snapshot.check(df)",
            "    ",
            "    diff is empty, you may want to change the print options",
        ]
    )


def test_snapshot_pandas_display_options_deprecation_warning(
    setup_pd, testdir, assert_outcomes
):
    testdir.makepyfile(
        """
        import pandas as pd
        import pytest

        def test_snapshot_dataframe(snapshot):
            df = pd.DataFrame(
                dict(
                    a=[1, 2, 3],
                    b=["a", "b", "c"],
                    c=[1.0, 1.5, 2.000001],
                )
            )
            with pytest.warns(DeprecationWarning) as record:
                snapshot.check(df, display_options=dict(precision=3))
                assert record[0].message.args[0].startswith(
                    "please use the 'pandas.option_context' context manager"
                )
        """
    )
    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)


def test_snapshot_pandas_rtol_atol(setup_pd, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import pandas as pd

        def test_snapshot_dataframe(snapshot):
            df = pd.DataFrame(
                dict(
                    a=[1, 2, 3],
                    b=["a", "b", "c"],
                    c=[1.02, 1.5, 2.0],
                )
            )
            snapshot.check(df, rtol=1e-1)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, passed=1)

    testdir.makepyfile(
        """
        import pandas as pd

        def test_snapshot_dataframe(snapshot):
            df = pd.DataFrame(
                dict(
                    a=[1, 2, 3],
                    b=["a", "b", "c"],
                    c=[1.02, 1.5, 2.0],
                )
            )
            snapshot.check(df, atol=1e-1)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, passed=1)


def test_snapshot_pandas_diff_num_columns(setup_pd, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import pandas as pd

        def test_snapshot_dataframe(snapshot):
            df = pd.DataFrame(
                dict(
                    a=[1, 2, 3],
                    c=[1.0, 1.5, 2.0],
                )
            )
            snapshot.check(df)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)

    lines = [
        "snapshot mismatch:",
        "    > test_snapshot_pandas_*.py +10:",
        "    > snapshot.check(df)",
        "    --- current",
        "    +++ expected",
        "    @@ -1,5 +1,6 @@",
        "    -Data columns (total 2 columns):",
        "    +Data columns (total 3 columns):",
        "      #   Column  Non-Null Count  Dtype  ",
        "     ---  ------  --------------  -----  ",
        "      0   a       3 non-null      int64  ",
        "    - 1   c       3 non-null      float64",
        "    + 1   b       3 non-null      object ",
        "    + 2   c       3 non-null      float64",
        "    ",
        "    --- current",
        "    +++ expected",
        "    @@ -1,4 +1,4 @@",
        "    -   a    c",
        "    -0  1  1.0",
        "    -1  2  1.5",
        "    -2  3  2.0",
        "    +   a  b    c",
        "    +0  1  a  1.0",
        "    +1  2  b  1.5",
        "    +2  3  c  2.0",
    ]
    result.stdout.fnmatch_lines(lines, consecutive=True)
