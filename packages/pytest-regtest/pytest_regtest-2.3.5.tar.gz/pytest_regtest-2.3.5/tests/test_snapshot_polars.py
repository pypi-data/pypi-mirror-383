import pytest


@pytest.fixture
def setup_pl(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import polars as pl

        def test_snapshot_dataframe(snapshot):
            df = pl.DataFrame(
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
            "snapshot error(s) for test_snapshot_polars*.py::test_snapshot_dataframe:",
            "",
            "snapshot not recorded yet:",
            "    > snapshot.check(df)",
            "    shape: (3, 3)",
            "    ┌─────┬─────┬─────┐",
            "    │ a   ┆ b   ┆ c   │",
            "    │ --- ┆ --- ┆ --- │",
            "    │ i64 ┆ str ┆ f64 │",
            "    ╞═════╪═════╪═════╡",
            "    │ 1   ┆ a   ┆ 1.0 │",
            "    │ 2   ┆ b   ┆ 1.5 │",
            "    │ 3   ┆ c   ┆ 2.0 │",
            "    └─────┴─────┴─────┘",
        ],
        consecutive=True,
    )

    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)

    result = testdir.runpytest()
    assert_outcomes(result, passed=1)


def test_snapshot_polars_changed_entry(setup_pl, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import polars as pl

        def test_snapshot_dataframe(snapshot):
            df = pl.DataFrame(
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
            "    > test_snapshot_polars_*.py +11:",
            "    > snapshot.check(df)",
            "    ",
            "    --- current",
            "    +++ expected",
            "    @@ -6,5 +6,5 @@",
            "     ╞═════╪═════╪═════╡",
            "     │ 1   ┆ a   ┆ 1.0 │",
            "     │ 2   ┆ b   ┆ 1.5 │",
            "    -│ 3   ┆ c   ┆ 3.0 │",
            "    +│ 3   ┆ c   ┆ 2.0 │",
            "     └─────┴─────┴─────┘",
        ],
        consecutive=True,
    )


def test_snapshot_polars_empty_diff(setup_pl, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import polars as pl

        def test_snapshot_dataframe(snapshot):
            df = pl.DataFrame(
                dict(
                    a=[1, 2, 3],
                    b=["a", "b", "c"],
                    c=[1.0, 1.5, 2.000001],
                )
            )
            snapshot.check(df, display_options=dict(float_precision=3))
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot mismatch:",
            "    > test_snapshot_polars_*.py +11:",
            "    > snapshot.check(df, display_options=dict(float_precision=3))",
            "    ",
            "    diff is empty, you may want to change the print options",
        ]
    )


def test_snapshot_polars_rtol_atol(setup_pl, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import polars as pl

        def test_snapshot_dataframe(snapshot):
            df = pl.DataFrame(
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
        import polars as pl

        def test_snapshot_dataframe(snapshot):
            df = pl.DataFrame(
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


def test_snapshot_polars_diff_num_columns(setup_pl, testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import polars as pl

        def test_snapshot_dataframe(snapshot):
            df = pl.DataFrame(
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
        "    > test_snapshot_polars_*.py +10:",
        "    > snapshot.check(df)",
        "    --- current",
        "    +++ expected",
        "    @@ -1,5 +1,6 @@",
        "    -Data columns (total 2 columns):",
        "    +Data columns (total 3 columns):",
        "      #   Column  Non-Null Count  Dtype  ",
        "     ---  ------  --------------  -----  ",
        "      0   a       3 non-null      Int64",
        "    - 1   c       3 non-null      Float64",
        "    + 1   b       3 non-null      String",
        "    + 2   c       3 non-null      Float64",
        "    ",
        "    --- current",
        "    +++ expected",
        "    @@ -1,10 +1,10 @@",
        "    -shape: (3, 2)",
        "    -┌─────┬─────┐",
        "    -│ a   ┆ c   │",
        "    -│ --- ┆ --- │",
        "    -│ i64 ┆ f64 │",
        "    -╞═════╪═════╡",
        "    -│ 1   ┆ 1.0 │",
        "    -│ 2   ┆ 1.5 │",
        "    -│ 3   ┆ 2.0 │",
        "    -└─────┴─────┘",
        "    +shape: (3, 3)",
        "    +┌─────┬─────┬─────┐",
        "    +│ a   ┆ b   ┆ c   │",
        "    +│ --- ┆ --- ┆ --- │",
        "    +│ i64 ┆ str ┆ f64 │",
        "    +╞═════╪═════╪═════╡",
        "    +│ 1   ┆ a   ┆ 1.0 │",
        "    +│ 2   ┆ b   ┆ 1.5 │",
        "    +│ 3   ┆ c   ┆ 2.0 │",
        "    +└─────┴─────┴─────┘",
    ]
    result.stdout.fnmatch_lines(lines, consecutive=True)
