import sys

import pytest

IS_WIN = sys.platform == "win32"


@pytest.fixture
def create_test_regtest_context_manager(testdir):
    testdir.makepyfile(
        """
        import tempfile
        import pytest_regtest

        def test_regtest(regtest, tmpdir):

            print("this is not recorded")
            with regtest:
                print("this is expected outcome")
                print(tmpdir.join("test").strpath)
                print(tempfile.gettempdir())
                print(tempfile.mkdtemp())
                print("obj id is", hex(id(tempfile)))
            regtest.flush()

         """
    )
    yield testdir


@pytest.fixture
def create_test_regtest_fh(testdir):
    testdir.makepyfile(
        """
        import tempfile

        def test_regtest(regtest, tmpdir):

            print("this is not recorded")
            print("this is expected outcome", file=regtest)
            print(tmpdir.join("test").strpath, file=regtest)
            print(tempfile.gettempdir(), file=regtest)
            print(tempfile.mkdtemp(), file=regtest)
            print("obj id is", hex(id(tempfile)), file=regtest)
            regtest.flush()

         """
    )
    yield testdir


def break_test_regtest_fh(create_test_regtest_fh):
    create_test_regtest_fh.makepyfile(
        """
        import tempfile

        def test_regtest(regtest, tmpdir):

            print("this is not recorded ")
            print("this is expected outcome ", file=regtest)
            print(tmpdir.join("test").strpath, file=regtest)
            print(tempfile.gettempdir(), file=regtest)
            print(tempfile.mkdtemp(), file=regtest)
            print("the obj id is", hex(id(tempfile)), file=regtest)
            regtest.flush()

         """
    )


@pytest.fixture
def create_test_regtest_all(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import tempfile

        def test_regtest(regtest_all, tmpdir):

            print("this is expected outcome")
            print(tmpdir.join("test").strpath)
            print(tempfile.gettempdir())
            print(tempfile.mkdtemp())
            print("obj id is", hex(id(tempfile)))
         """
    )
    yield testdir


def test_regtest_context_manager(create_test_regtest_context_manager, assert_outcomes):
    _test_regtest_output(create_test_regtest_context_manager, assert_outcomes)


def test_regtest_fh(create_test_regtest_fh, assert_outcomes):
    _test_regtest_output(create_test_regtest_fh, assert_outcomes)


def test_regtest_all(create_test_regtest_all, assert_outcomes):
    _test_regtest_output(create_test_regtest_all, assert_outcomes)


def _test_regtest_output(test_setup, assert_outcomes):
    result = test_setup.runpytest("-s")
    assert_outcomes(result, failed=1, passed=0, xfailed=0)

    expected_diff = """
    regression test output not recorded yet for test_regtest_*::test_regtest:

    this is expected outcome
    <tmpdir_from_fixture>/test
    <tmpdir_from_tempfile_module>
    <tmpdir_from_tempfile_module>
    obj id is 0x?????????""".strip().splitlines()

    result.stdout.fnmatch_lines(
        [line.lstrip() for line in expected_diff], consecutive=True
    )


def test_xfail(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import tempfile
        import pytest

        @pytest.mark.xfail
        def test_regtest_xfail(regtest_all, tmpdir):

            print("this is expected outcome")
            print(tmpdir.join("test").strpath)
            print(tempfile.gettempdir())
            print(tempfile.mkdtemp())
            print("obj id is", hex(id(tempfile)))
         """
    )
    result = testdir.runpytest()
    assert_outcomes(result, xfailed=1)

    # With --regtest-reset, xfail tests are not reset (output not recorded)
    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, xfailed=1)

    # Run again - still xfailed because no output was recorded
    result = testdir.runpytest()
    assert_outcomes(result, xfailed=1)


def test_xfail_strict(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import tempfile
        import pytest

        @pytest.mark.xfail(strict=True)
        def test_regtest_xfail_strict(regtest_all, tmpdir):

            print("this is expected outcome")
            print(tmpdir.join("test").strpath)
            print(tempfile.gettempdir())
            print(tempfile.mkdtemp())
            print("obj id is", hex(id(tempfile)))
         """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=0, passed=0, xfailed=1)

    # With --regtest-reset, xfail tests are not reset (output not recorded)
    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, xfailed=1)

    # Run again - still xfailed because no output was recorded
    # With strict=True, an xpass would become a failure, but this stays xfailed
    result = testdir.runpytest()
    assert_outcomes(result, xfailed=1)


def test_conditional_xfail(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import sys
        import pytest

        @pytest.mark.xfail(condition=sys.platform == "win32", reason="Windows only")
        def test_conditional_xfail_windows(regtest_all):
            print("This test is xfailed on Windows only")
            print(f"Platform: {sys.platform}")
            # This should pass on non-Windows

        @pytest.mark.xfail(condition=sys.platform != "win32", reason="Non-Windows only")
        def test_conditional_xfail_non_windows(regtest_all):
            print("This test is xfailed on non-Windows only")
            print(f"Platform: {sys.platform}")
            # This should pass on Windows
         """
    )

    # Run initially - one should fail (no recorded output), one should xfail
    result = testdir.runpytest()
    assert_outcomes(result, failed=1, xfailed=1)

    # Run with --regtest-reset
    # xfail tests should NOT be reset - they run but output is not recorded
    # The non-xfailed test gets reset, the xfailed one still fails (no output file)
    result = testdir.runpytest("--regtest-reset")
    if IS_WIN:
        # On Windows: test_windows is xfailed, test_non_windows gets reset
        assert_outcomes(result, passed=1, xfailed=1)
    else:
        # On non-Windows: test_windows gets reset, test_non_windows is xfailed
        assert_outcomes(result, passed=1, xfailed=1)

    # Run again to verify
    # The non-xfailed test should pass (was reset)
    # The xfailed test should still fail (no output file was created)
    result = testdir.runpytest()
    assert_outcomes(result, passed=1, xfailed=1)


def test_failed_test(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import tempfile
        import pytest

        def test_regtest(regtest_all, tmpdir):

            print("this is expected outcome")
            print(tmpdir.join("test").strpath)
            print(tempfile.gettempdir())
            print(tempfile.mkdtemp())
            print("obj id is", hex(id(tempfile)))

            assert False
         """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)

    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, failed=1)


def test_converter_pre_v2(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import tempfile
        from pytest_regtest import register_converter_pre

        @register_converter_pre
        def to_upper_conv(line):
            return line.upper()

        def test_regtest(regtest_all, tmpdir):
            print("this is expected outcome")
            print("obj id is 0xabcdeffff")
         """
    )
    # suprorcess to avoid that converters from other test functions
    # here in test_plugin.py are still registered:
    import pytest_regtest

    pytest_regtest.clear_converters()
    result = testdir.runpytest()
    pytest_regtest.clear_converters()
    assert_outcomes(result, failed=1)

    result.stdout.fnmatch_lines(
        [
            "regression test output not recorded yet for test_converter_pre_v2.py::test_regtest:",
            "",
            "THIS IS EXPECTED OUTCOME",
            "OBJ ID IS 0XABCDEFFFF",
        ]
    )

    pytest_regtest.clear_converters()
    result = testdir.runpytest("--regtest-reset")
    pytest_regtest.clear_converters()
    assert_outcomes(result, passed=1)


def test_converter_pre(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import tempfile
        from pytest_regtest import register_converter_pre

        @register_converter_pre
        def to_upper_conv(line, request):
            return line.upper()

        def test_regtest(regtest_all, tmpdir):
            print("this is expected outcome")
            print("obj id is 0xabcdeffff")
         """
    )
    # suprorcess to avoid that converters from other test functions
    # here in test_plugin.py are still registered:
    import pytest_regtest

    pytest_regtest.clear_converters()
    result = testdir.runpytest()
    pytest_regtest.clear_converters()
    assert_outcomes(result, failed=1)

    result.stdout.fnmatch_lines(
        [
            "regression test output not recorded yet for test_converter_pre.py::test_regtest:",
            "",
            "THIS IS EXPECTED OUTCOME",
            "OBJ ID IS 0XABCDEFFFF",
        ]
    )

    pytest_regtest.clear_converters()
    result = testdir.runpytest("--regtest-reset")
    pytest_regtest.clear_converters()
    assert_outcomes(result, passed=1)


def test_converter_post_pre_v2(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import tempfile
        from pytest_regtest import register_converter_post

        @register_converter_post
        def to_upper_conv(line):
            return line.upper()

        def test_regtest(regtest_all, tmpdir):
            print("this is expected outcome")
            print(tmpdir.join("test").strpath)
            print(tempfile.gettempdir())
            print(tempfile.mkdtemp())
            print("obj id is", hex(id(tempfile)))
         """
    )
    import pytest_regtest

    pytest_regtest.clear_converters()
    result = testdir.runpytest()
    pytest_regtest.clear_converters()
    assert_outcomes(result, failed=1)
    expected_diff = """
    regression test output not recorded yet for test_*::test_regtest:

    THIS IS EXPECTED OUTCOME
    <TMPDIR_FROM_FIXTURE>/TEST
    <TMPDIR_FROM_TEMPFILE_MODULE>
    <TMPDIR_FROM_TEMPFILE_MODULE>
    OBJ ID IS 0X?????????""".strip().splitlines()

    result.stdout.fnmatch_lines(
        [line.lstrip() for line in expected_diff], consecutive=True
    )

    pytest_regtest.clear_converters()
    result = testdir.runpytest("--regtest-reset")
    pytest_regtest.clear_converters()
    assert_outcomes(result, passed=1)


def test_converter_post(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import tempfile
        from pytest_regtest import register_converter_post

        @register_converter_post
        def to_upper_conv(line, request):
            return line.upper()

        def test_regtest(regtest_all, tmpdir):
            print("this is expected outcome")
            print(tmpdir.join("test").strpath)
            print(tempfile.gettempdir())
            print(tempfile.mkdtemp())
            print("obj id is", hex(id(tempfile)))
         """
    )
    import pytest_regtest

    pytest_regtest.clear_converters()
    result = testdir.runpytest()
    pytest_regtest.clear_converters()
    assert_outcomes(result, failed=1)

    expected_diff = """
    regression test output not recorded yet for test_*::test_regtest:

    THIS IS EXPECTED OUTCOME
    <TMPDIR_FROM_FIXTURE>/TEST
    <TMPDIR_FROM_TEMPFILE_MODULE>
    <TMPDIR_FROM_TEMPFILE_MODULE>
    OBJ ID IS 0X?????????""".strip().splitlines()

    result.stdout.fnmatch_lines(
        [line.lstrip() for line in expected_diff], consecutive=True
    )

    pytest_regtest.clear_converters()
    result = testdir.runpytest("--regtest-reset")
    pytest_regtest.clear_converters()
    assert_outcomes(result, passed=1)


def test_consider_line_endings(create_test_regtest_fh, assert_outcomes):
    create_test_regtest_fh.runpytest("--regtest-reset")

    # just check if cmd line flags work without throwing exceptions:
    result = create_test_regtest_fh.runpytest("--regtest-consider-line-endings")
    assert_outcomes(result, passed=1)

    break_test_regtest_fh(create_test_regtest_fh)
    result = create_test_regtest_fh.runpytest("--regtest-consider-line-endings")
    expected_diff = """
    >   --- current
    >   +++ expected
    >   @@ -1,5 +1,5 @@
    >   -'this is expected outcome '
    >   +'this is expected outcome'
    >    '<tmpdir_from_fixture>/test'
    >    '<tmpdir_from_tempfile_module>'
    >    '<tmpdir_from_tempfile_module>'
    >   -'the obj id is 0x?????????'
    >   +'obj id is 0x?????????'""".strip("\n").splitlines()
    result.stdout.fnmatch_lines([line for line in expected_diff], consecutive=True)

    result = create_test_regtest_fh.runpytest()
    expected_diff = """
    >   --- current
    >   +++ expected
    >   @@ -2,4 +2,4 @@
    >    <tmpdir_from_fixture>/test
    >    <tmpdir_from_tempfile_module>
    >    <tmpdir_from_tempfile_module>
    >   -the obj id is 0x?????????
    >   +obj id is 0x?????????""".strip("\n").splitlines()
    result.stdout.fnmatch_lines([line for line in expected_diff], consecutive=True)


def test_tee(create_test_regtest_fh, assert_outcomes):
    create_test_regtest_fh.runpytest("--regtest-reset")

    # just check if cmd line flags work without throwing exceptions:
    result = create_test_regtest_fh.runpytest("--regtest-tee")
    assert_outcomes(result, passed=1)
    result.stdout.fnmatch_lines(
        """
recorded raw output to regtest fixture: *
this is expected outcome
*
*
*
obj id is 0x*
""".strip().splitlines(),
        consecutive=True,
    )


def test_parameterized_tests(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        import pytest

        @pytest.mark.parametrize("a", [1, "2", (1, 2, 3), "[]", "'a", '"b'])
        def test_regtest_parameterized(regtest, a):
            print(a, file=regtest)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=6)

    result = testdir.runpytest("--regtest-reset", "-v")
    assert_outcomes(result, passed=6)

    result = testdir.runpytest()
    assert_outcomes(result, passed=6)


def test_with_long_filename_result_file(testdir, assert_outcomes):
    long_str = "abc123" * 20
    testdir.makepyfile(
        f"""
        import pytest

        @pytest.mark.parametrize("a", ["{long_str}"])
        def test_regtest_long(regtest, a):
            print(a, file=regtest)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)

    test_func_id = "test_with_long_filename_result_file.py::test_regtest_long"
    test_func_id_fname = test_func_id.replace(".py::", ".")

    result.stdout.fnmatch_lines(
        f"""
regression test output not recorded yet for {test_func_id}[{long_str}]:

{long_str}
            """.strip().splitlines()
    )

    result = testdir.runpytest("--regtest-reset", "-v")
    assert_outcomes(result, passed=1)

    result.stdout.fnmatch_lines(
        f"""
total number of failed regression tests: 0
total number of failed snapshot tests  : 0
the following output files have been reset:
  _regtest_outputs/{test_func_id_fname}[{long_str[:70]}__fa3b11731b.item
  _regtest_outputs/{test_func_id_fname}[{long_str[:70]}__fa3b11731b.out
""".strip().splitlines(),
        consecutive=True,
    )

    result = testdir.runpytest()

    assert_outcomes(result, passed=1)


def test_disabled_std_conversion(testdir, assert_outcomes):
    testdir.makepyfile(
        """
        def test_regtest_long(regtest):
            print("object at 0x1027cbd90", file=regtest)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)

    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)

    result = testdir.runpytest("--regtest-disable-stdconv")
    assert_outcomes(result, failed=1)

    result.stdout.fnmatch_lines(
        [
            "    >   -object at 0x1027cbd90",
            "    >   +object at 0x?????????",
        ],
        consecutive=True,
    )


def test_identifier(testdir, assert_outcomes, regtest):
    testdir.makepyfile(
        """
        def test_with_identifier(regtest):
            print("object at 0x1027cbd90", file=regtest)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)

    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)

    result = testdir.runpytest()
    assert_outcomes(result, passed=1)

    for p in sorted((testdir.tmpdir / "_regtest_outputs").listdir()):
        print(p.relto(testdir.tmpdir), file=regtest)

    testdir.makepyfile(
        """
        def test_with_identifier(regtest):
            regtest.identifier = "test-id"
            print("object at 0x1027cbd90", file=regtest)
        """
    )
    result = testdir.runpytest()
    assert_outcomes(result, failed=1)

    result = testdir.runpytest("--regtest-reset")
    assert_outcomes(result, passed=1)

    result = testdir.runpytest()
    assert_outcomes(result, passed=1)

    print(file=regtest)
    for p in sorted((testdir.tmpdir / "_regtest_outputs").listdir()):
        print(p.relto(testdir.tmpdir), file=regtest)
