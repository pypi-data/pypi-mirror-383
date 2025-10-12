import shutil
import subprocess


def get_terminal_width():
    return 80, 40


shutil.get_terminal_width = get_terminal_width


def test_cli(regtest, pytestconfig):
    output = str(subprocess.check_output(["pytest", "--help"]), "utf-8")
    lines = output.splitlines()
    regtest_lines = [li for li in lines if "--regtest" in li]
    print("\n".join(regtest_lines), file=regtest)


def test_tee(regtest, pytester):
    pytester.makepyfile(
        r"""
        import pytest_regtest
        import re
        import os

        pytest_regtest.patch_terminal_size(80, 40)

        @pytest_regtest.register_converter_pre
        def fix_ts(line):
            return re.sub(r"\d+\.\d+s", "TIME", line)

        def test_regtest(regtest, pytestconfig):
            print("this is some output of time: 1.02s", file=regtest)
         """
    )
    result = pytester.runpytest()

    # ingore first 5 lines which contain instable information
    # such as the exact python version used:
    print("\n".join(result.outlines[5:]), file=regtest)

    result = pytester.runpytest("--regtest-tee")
    print("\n".join(result.outlines[5:]), file=regtest)

    result = pytester.runpytest("--regtest-reset")
    print("\n".join(result.outlines[5:]), file=regtest)


def test_fixtures(regtest, pytester):
    pytester.makepyfile(
        """
        import pytest_regtest

        def test_regtest(regtest):
            print("this is some output", file=regtest)

        def test_snapshot(snapshot):
            print("this is some output", file=snapshot)

        def test_regtest_all(regtest_all):
            print("this is some output")

        def test_snapshot(snapshot_all_output):
            print("this is some output")

         """
    )
    result = pytester.runpytest("--regtest-reset")
    assert result.ret == 0
