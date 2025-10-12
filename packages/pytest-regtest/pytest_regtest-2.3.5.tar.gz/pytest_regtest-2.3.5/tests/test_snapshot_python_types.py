def test_snapshot_python_data_types(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        def test_snapshot_python(snapshot):
            snapshot.check([1, 2, 3])
            snapshot.check(dict(a=[1, 2, 3]))
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot error(s) for"
            " test_snapshot_python_data_types.py::test_snapshot_python:",
            "",
            "snapshot not recorded yet:",
            "    > snapshot.check([1, 2, 3])",
            "    [1, 2, 3]",
            "",
            "snapshot not recorded yet:",
            "    > snapshot.check(dict(a=[1, 2, 3]))",
            "    {'a': [1, 2, 3]}",
        ],
        consecutive=True,
    )

    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)

    result = testdir.runpytest()
    assert_outcomes(result, passed=1)

    testdir.makepyfile(
        """
        def test_snapshot_python(snapshot):
            snapshot.check([1, 2, 3, 4])
            snapshot.check(dict(a=[1, 2, 3]))
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot mismatch:",
            "    > test_snapshot_python_data_types.py +2:",
            "    > snapshot.check([1, 2, 3, 4])",
            "    --- current",
            "    +++ expected",
            "    @@ -1 +1 @@",
            "    -[1, 2, 3, 4]",
            "    +[1, 2, 3]",
            "",
            "snapshot ok:",
            "    > test_snapshot_python_data_types.py +3",
            "    > snapshot.check(dict(a=[1, 2, 3]))",
        ],
        consecutive=True,
    )

    result = testdir.runpytest("--regtest-nodiff")
    assert_outcomes(result, failed=1)
    result.stdout.fnmatch_lines(
        [
            "snapshot mismatch:",
            "    > test_snapshot_python_data_types.py +2:",
            "    > snapshot.check([1, 2, 3, 4])",
            "    5 lines in report",
            "",
            "snapshot ok:",
            "    > test_snapshot_python_data_types.py +3",
            "    > snapshot.check(dict(a=[1, 2, 3]))",
        ],
        consecutive=True,
    )


def test_snapshot_with_version(testdir, assert_outcomes, regtest):
    testdir.makepyfile(
        """
        def test_snapshot_python(snapshot):
            snapshot.check([1, 2, 3])
            snapshot.check(dict(a=[1, 2, 3]))
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)

    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)

    for p in sorted((testdir.tmpdir / "_regtest_outputs").listdir()):
        print(p.relto(testdir.tmpdir), file=regtest)

    testdir.makepyfile(
        """
        def test_snapshot_python(snapshot):
            snapshot.check([1, 2, 3], version="a")
            snapshot.check(dict(a=[1, 2, 3]), version="a")
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)

    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)

    print(file=regtest)
    for p in sorted((testdir.tmpdir / "_regtest_outputs").listdir()):
        print(p.relto(testdir.tmpdir), file=regtest)
