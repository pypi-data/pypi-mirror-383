import difflib
import functools
import inspect
import os
import re
import shutil
import sys
import tempfile
from collections.abc import Callable
from hashlib import sha512
from io import StringIO
from typing import Optional

import _pytest
import pytest
from _pytest._code.code import TerminalRepr
from _pytest._io import TerminalWriter

from .snapshot_handler import PythonObjectHandler  # noqa: F401
from .snapshot_handler import SnapshotHandlerRegistry

IS_WIN = sys.platform == "win32"


def patch_terminal_size(w, h):
    def get_terminal_size(fallback=None):
        return w, h

    shutil.get_terminal_size = get_terminal_size


# we determine actual terminal size before pytest changes this:
tw, _ = shutil.get_terminal_size()


class RegtestException(Exception):
    pass


class RecordedOutputException(RegtestException):
    pass


class SnapshotException(RegtestException):
    pass


class PytestRegtestCommonHooks:
    def __init__(self):
        self._reset_snapshots = []
        self._reset_regtest_outputs = []
        self._failed_snapshots = []
        self._failed_regtests = []

    @pytest.hookimpl(hookwrapper=False)
    def pytest_terminal_summary(self, terminalreporter, exitstatus, config):
        tr = terminalreporter
        tr.ensure_newline()
        tr.section("pytest-regtest report", sep="-", blue=True, bold=True)
        tr.write("total number of failed regression tests: ", bold=True)
        tr.line(str(len(self._failed_regtests)))
        tr.write("total number of failed snapshot tests  : ", bold=True)
        tr.line(str(len(self._failed_snapshots)))

        if config.getvalue("--regtest-reset"):
            if config.option.verbose:
                tr.line("the following output files have been reset:", bold=True)
                for path in self._reset_regtest_outputs:
                    rel_path = os.path.relpath(path)
                    tr.line("  " + rel_path)
                for path in self._reset_snapshots:
                    rel_path = os.path.relpath(path)
                    tr.line("  " + rel_path)
            else:
                tr.write("total number of reset output files: ", bold=True)
                tr.line(
                    str(len(self._reset_regtest_outputs) + len(self._reset_snapshots))
                )

    @pytest.hookimpl(hookwrapper=True)
    def pytest_pyfunc_call(self, pyfuncitem):
        stdout = sys.stdout
        if "regtest_all" in pyfuncitem.fixturenames and hasattr(
            pyfuncitem, "regtest_stream"
        ):
            sys.stdout = pyfuncitem.regtest_stream
        yield
        sys.stdout = stdout

    @pytest.hookimpl(hookwrapper=True)
    def pytest_report_teststatus(self, report, config):
        outcome = yield
        if report.when == "call" and "uses-regtest" in report.keywords:
            if config.getvalue("--regtest-reset"):
                result = outcome.get_result()
                if result[0] != "failed":
                    outcome.force_result((result[0], "R", "RESET"))


class PytestRegtestPlugin:
    def __init__(self, recorder):
        self.recorder = recorder

    @pytest.hookimpl(trylast=True)
    def pytest_runtest_call(self, item):
        if hasattr(item, "regtest_stream"):
            output_exception = self.check_recorded_output(item)
            if output_exception is not None:
                raise output_exception

    def check_recorded_output(self, item):
        test_folder = item.fspath.dirname
        regtest_stream = item.regtest_stream
        version = regtest_stream.version or regtest_stream.identifier
        if not isinstance(regtest_stream, RegtestStream):
            return

        orig_identifer, recorded_output_path = result_file_paths(
            test_folder, item.nodeid, version
        )
        config = item.config

        consider_line_endings = config.getvalue("--regtest-consider-line-endings")
        reset = config.getvalue("--regtest-reset")

        # Skip reset for xfail tests that are actually expected to fail
        xfail_marker = item.get_closest_marker("xfail")
        if xfail_marker:
            # Check if xfail condition evaluates to True
            condition = xfail_marker.kwargs.get("condition", True)
            if condition is True or (condition is not False and condition):
                reset = False

        if reset:
            os.makedirs(os.path.dirname(recorded_output_path), exist_ok=True)
            with open(recorded_output_path + ".out", "w", encoding="utf-8") as fh:
                fh.write("".join(regtest_stream.get_lines()))
            if orig_identifer is not None:
                self.recorder._reset_regtest_outputs.append(
                    recorded_output_path + ".item"
                )
                with open(recorded_output_path + ".item", "w") as fh:
                    print(orig_identifer, file=fh)
            self.recorder._reset_regtest_outputs.append(recorded_output_path + ".out")
            return

        if os.path.exists(recorded_output_path + ".out"):
            with open(recorded_output_path + ".out", "r", encoding="utf-8") as fh:
                tobe = fh.readlines()
            recorded_output_file_exists = True
        else:
            tobe = []
            recorded_output_file_exists = False

        current = regtest_stream.get_lines()
        if consider_line_endings:
            current = [repr(line.rstrip("\n")) for line in current]
            tobe = [repr(line.rstrip("\n")) for line in tobe]
        else:
            current = [line.rstrip() for line in current]
            tobe = [line.rstrip() for line in tobe]

        if current != tobe:
            self.recorder._failed_regtests.append(item)
            return RecordedOutputException(
                current,
                tobe,
                recorded_output_path,
                regtest_stream,
                recorded_output_file_exists,
            )

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        result = outcome.get_result()
        if call.when == "teardown" and hasattr(item, "regtest_stream"):
            if item.config.getvalue("--regtest-tee"):
                tw = TerminalWriter()
                output = item.regtest_stream.get_output()

                if output:
                    tw.line()
                    line = "recorded raw output to regtest fixture: "
                    line = line.ljust(tw.fullwidth, "-")
                    tw.line(line, green=True)
                    tw.write(item.regtest_stream.get_output() + "\n", cyan=True)
                    line = "-" * tw.fullwidth
                    tw.line(line, green=True)

        if call.when != "call" or not getattr(item, "regtest", False):
            return

        result.keywords["uses-regtest"] = True

        if call.excinfo is not None:
            all_lines, all_colors = [], []
            if call.excinfo.type is RecordedOutputException:
                output_exception = call.excinfo
                if output_exception is not None:
                    lines, colors = self._handle_regtest_exception(
                        item, output_exception.value.args, result
                    )
                    all_lines.extend(lines)
                    all_colors.extend(colors)

            else:
                return

            result.longrepr = CollectErrorRepr(all_lines, all_colors)

    def _handle_regtest_exception(self, item, exc_args, result):
        (
            current,
            recorded,
            recorded_output_path,
            regtest_stream,
            recorded_output_file_exists,
        ) = exc_args

        nodeid = item.nodeid + (
            "" if regtest_stream.version is None else "__" + regtest_stream.version
        )
        if not recorded_output_file_exists:
            msg = "\nregression test output not recorded yet for {}:\n".format(nodeid)
            return (
                [msg] + current,
                [dict()] + len(current) * [dict(red=True, bold=True)],
            )

        nodiff = item.config.getvalue("--regtest-nodiff")
        diffs = list(
            difflib.unified_diff(current, recorded, "current", "expected", lineterm="")
        )

        msg = "\nregression test output differences for {}:\n".format(nodeid)

        if nodiff:
            msg_diff = f"    {len(diffs)} lines in diff"
        else:
            recorded_output_path = os.path.relpath(recorded_output_path)
            msg += f"    (recorded output from {recorded_output_path})\n"
            msg_diff = "    >   " + "\n    >   ".join(diffs)

        return [msg, msg_diff + "\n"], [dict(), dict(red=True, bold=True)]


class SnapshotPlugin:
    def __init__(self, recorder):
        self.recorder = recorder

    @pytest.hookimpl(trylast=True)
    def pytest_runtest_call(self, item):
        if hasattr(item, "snapshot"):
            snapshot_exception = self.check_snapshots(item)
            if snapshot_exception is not None:
                raise snapshot_exception

    def check_snapshots(self, item):
        results = []

        any_failed = False
        for idx, snapshot in enumerate(item.snapshot.snapshots):
            is_recorded, ok, msg = self.check_snapshot(idx, item, snapshot)
            if not ok:
                any_failed = True
            results.append((ok, snapshot, is_recorded, msg))

        if any_failed:
            self.recorder._failed_snapshots.append(item)
            return SnapshotException(results)

    def check_snapshot(self, idx, item, snapshot):
        handler, obj, version, _ = snapshot

        test_folder = item.fspath.dirname
        if version is not None:
            identifier = str(version) + "__" + str(idx)
        else:
            identifier = str(idx)

        config = item.config

        orig_identifer, recorded_output_path = result_file_paths(
            test_folder, item.nodeid, identifier
        )

        reset = config.getvalue("--regtest-reset")

        # Skip reset for xfail tests that are actually expected to fail
        xfail_marker = item.get_closest_marker("xfail")
        if xfail_marker:
            # Check if xfail condition evaluates to True
            condition = xfail_marker.kwargs.get("condition", True)
            if condition is True or (condition is not False and condition):
                reset = False

        if reset:
            os.makedirs(recorded_output_path, exist_ok=True)
            handler.save(recorded_output_path, obj)
            if orig_identifer is not None:
                self.recorder._reset_snapshots.append(recorded_output_path + ".item")
                with open(recorded_output_path + ".item", "w") as fh:
                    print(orig_identifer, file=fh)
            self.recorder._reset_snapshots.append(recorded_output_path)
            return True, True, None

        has_markup = item.config.get_terminal_writer().hasmarkup

        if os.path.exists(recorded_output_path):
            try:
                recorded_obj = handler.load(recorded_output_path)
            except Exception:
                msg = [
                    "snapshot handler could not load recorded object, maybe type"
                    " changed?",
                ]
                msg.extend(handler.show(obj))
                return False, False, msg

            ok = handler.compare(obj, recorded_obj)
            if ok:
                return True, True, None
            msg = handler.show_differences(obj, recorded_obj, has_markup)
            return True, False, msg

        msg = handler.show(obj)
        return False, False, msg

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        result = outcome.get_result()
        if call.when == "teardown" and hasattr(item, "snapshot"):
            if item.config.getvalue("--regtest-tee"):
                tw = TerminalWriter()
                snapshots = item.snapshot.snapshots
                if not snapshots:
                    return

                tw.line()
                line = "recorded snapshots: "
                line = line.ljust(tw.fullwidth, "-")
                tw.line(line, green=True)
                path = item.fspath.relto(item.session.fspath)
                code_lines = item.fspath.readlines()

                for handler, obj, version, line_no in snapshots:
                    info = code_lines[line_no - 1].strip()
                    tw.line(f"> {path} +{line_no}")
                    tw.line(f"> {info}")
                    lines = handler.show(obj)
                    for line in lines:
                        tw.line(line, cyan=True)
                tw.line("-" * tw.fullwidth, green=True)
                tw.line()
                tw.flush()

        if call.when != "call" or not hasattr(item, "snapshot"):
            return

        result.keywords["uses-regtest"] = True

        if call.excinfo is not None:
            all_lines, all_colors = [], []
            if call.excinfo.type is SnapshotException:
                snapshot_exception = call.excinfo
                if snapshot_exception is not None:
                    lines, colors = self._handle_snapshot_exception(
                        item, snapshot_exception.value.args, result
                    )
                    all_lines.extend(lines)
                    all_colors.extend(colors)
            else:
                return

            result.longrepr = CollectErrorRepr(all_lines, all_colors)

    def _handle_snapshot_exception(self, item, exc_args, result):
        snapshot = item.snapshot
        lines = []
        colors = []

        code_lines = item.fspath.readlines()

        NO_COLOR = dict()
        RED = dict(red=True, bold=True)
        GREEN = dict(green=True, bold=False)

        headline = "\nsnapshot error(s) for {}:".format(item.nodeid)
        lines.append(headline)
        colors.append(NO_COLOR)

        for ok, snapshot, is_recorded, msg in exc_args[0]:
            obj, version, kw, line_no = snapshot
            info = code_lines[line_no - 1].strip()

            path = item.fspath.relto(item.session.fspath)
            if ok:
                lines.append("\nsnapshot ok:")
                lines.append(f"    > {path} +{line_no}")
                lines.append(f"    > {info}")
                colors.append(GREEN)
                colors.append(NO_COLOR)
                colors.append(NO_COLOR)
            elif is_recorded:
                lines.append("\nsnapshot mismatch:")
                lines.append(f"    > {path} +{line_no}:")
                lines.append(f"    > {info}")
                colors.append(RED)
                colors.append(NO_COLOR)
                colors.append(NO_COLOR)
                nodiff = item.config.getvalue("--regtest-nodiff")
                if nodiff:
                    lines.append(f"    {len(msg)} lines in report")
                    colors.append(RED)
                else:
                    lines.extend("    " + ll for ll in msg)
                    colors.extend(len(msg) * [RED])
            else:
                headline = "\nsnapshot not recorded yet:"
                lines.append(headline)
                colors.append(NO_COLOR)
                lines.append("    > " + info.strip())
                colors.append(RED)
                lines.extend("    " + ll for ll in msg)
                colors.extend(len(msg) * [RED])

        return lines, colors


def result_file_paths(test_folder, nodeid, version):
    file_path, __, test_function_name = nodeid.partition("::")
    file_name = os.path.basename(file_path)

    orig_test_function_identifier = f"{file_name}::{test_function_name}"

    for c in "/\\:*\"'?<>|":
        test_function_name = test_function_name.replace(c, "-")

    # If file name is too long, hash parameters.
    if len(test_function_name) > 100:
        test_function_name = (
            test_function_name[:88]
            + "__"
            + sha512(test_function_name.encode("utf-8")).hexdigest()[:10]
        )
    else:
        orig_test_function_identifier = None

    test_function_name = test_function_name.replace(" ", "_")
    stem, __ = os.path.splitext(file_name)
    if version is not None:
        output_file_name = stem + "." + test_function_name + "__" + str(version)
    else:
        output_file_name = stem + "." + test_function_name

    return orig_test_function_identifier, os.path.join(
        test_folder, "_regtest_outputs", output_file_name
    )


class RegtestStream:
    def __init__(self, request):
        request.node.regtest_stream = self
        request.node.regtest = True
        self.request = request
        self.buffer = StringIO()
        self.version = None
        self.identifier = None

        self.snapshots = []

    def write(self, what):
        self.buffer.write(what)

    def flush(self):
        pass

    def get_lines(self):
        output = self.buffer.getvalue()
        if not output:
            return []
        output = cleanup(output, self.request)
        lines = output.splitlines(keepends=True)
        return lines

    def get_output(self):
        return self.buffer.getvalue()

    def __enter__(self):
        sys.stdout = self
        return self

    def __exit__(self, *a):
        sys.stdout = sys.__stdout__
        return False  # dont suppress exception


class Snapshot:
    def __init__(self, request):
        request.node.snapshot = self
        request.node.regtest = True
        self.request = request
        self.buffer = StringIO()

        self.snapshots = []

    def check(self, obj, *, version=None, **options):
        handler_class = SnapshotHandlerRegistry.get_handler(obj)
        if handler_class is None:
            raise ValueError(f"no handler registered for {obj}")

        handler = handler_class(options, self.request.config, tw)
        line_no = inspect.currentframe().f_back.f_lineno
        self.snapshots.append((handler, obj, version, line_no))


def cleanup(output, request):
    for converter in _converters_pre:
        output = converter(output, request)

    if not request.config.getvalue("--regtest-disable-stdconv"):
        output = _std_conversion(output, request)

    for converter in _converters_post:
        output = converter(output, request)

    # in python 3 a string should not contain binary symbols...:
    if contains_binary(output):
        request.raiseerror(
            "recorded output for regression test contains unprintable characters."
        )

    return output


# the function below is modified version of http://stackoverflow.com/questions/898669/
textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})


def contains_binary(txt):
    return bool(txt.translate(dict(zip(textchars, " " * 9999))).replace(" ", ""))


_converters_pre = []
_converters_post = []


def clear_converters() -> None:
    """Unregisters all converters, including the builtin converters."""
    _converters_pre.clear()
    _converters_post.clear()


def _fix_pre_v2_converter_function(function):
    @functools.wraps(function)
    def fixed_converter_function(output, request):
        return function(output)

    return fixed_converter_function


def register_converter_pre(
    function: Callable[[str, Optional[_pytest.fixtures.FixtureRequest]], None],
) -> None:
    """Registers a new conversion function at the head of the list
    of existing converters.

    Parameters:
        function: Function to cleanup given string and remove data which can change
                  between test runs without affecting the correctness of the test.
                  The second argument is optional and is a `pytest` object which holds
                  information about the current `config` or the current test function.
                  This argument can be ignored in many situations.

    """
    if function not in _converters_pre:
        signature = inspect.signature(function)
        # keep downward compatibility:
        if len(signature.parameters) == 1:
            function = _fix_pre_v2_converter_function(function)
        _converters_pre.append(function)


def register_converter_post(
    function: Callable[[str, Optional[_pytest.fixtures.FixtureRequest]], None],
) -> None:
    """Registers a new conversion function at the head of the list
    of existing converters

    Parameters:
        function: Function to cleanup given string and remove data which can change
                  between test runs without affecting the correctness of the test.
                  The second argument is optional and is a `pytest` object which holds
                  information about the current `config` or the current test function.
                  This argument can be ignored in many situations.
    """
    if function not in _converters_post:
        signature = inspect.signature(function)
        # keep downward compatibility:
        if len(signature.parameters) == 1:
            function = _fix_pre_v2_converter_function(function)
        _converters_post.append(function)


def _std_replacements(request):
    if "tmpdir" in request.fixturenames:
        tmpdir = request.getfixturevalue("tmpdir").strpath + os.path.sep
        yield tmpdir, "<tmpdir_from_fixture>/"
        tmpdir = request.getfixturevalue("tmpdir").strpath
        yield tmpdir, "<tmpdir_from_fixture>"

    regexp = os.path.join(
        os.path.realpath(tempfile.gettempdir()), "pytest-of-.*", r"pytest-\d+/"
    )
    yield regexp, "<pytest_tempdir>/"

    regexp = os.path.join(tempfile.gettempdir(), "tmp[_a-zA-Z0-9]+")

    yield regexp, "<tmpdir_from_tempfile_module>"
    yield (
        os.path.realpath(tempfile.gettempdir()) + os.path.sep,
        "<tmpdir_from_tempfile_module>/",
    )
    yield os.path.realpath(tempfile.gettempdir()), "<tmpdir_from_tempfile_module>"
    yield tempfile.tempdir + os.path.sep, "<tmpdir_from_tempfile_module>/"
    yield tempfile.tempdir, "<tmpdir_from_tempfile_module>"
    yield r"var/folders/.*/pytest-of.*/", "<pytest_tempdir>/"

    # replace hex object ids in output by 0x?????????
    yield r" 0x[0-9a-fA-F]+", " 0x?????????"


def _std_conversion(output, request):
    fixed = []
    for line in output.splitlines(keepends=True):
        for regex, replacement in _std_replacements(request):
            if IS_WIN:
                # fix windows backwards slashes in regex
                regex = regex.replace("\\", "\\\\")
            line, __ = re.subn(regex, replacement, line)
        fixed.append(line)
    return "".join(fixed)


class CollectErrorRepr(TerminalRepr):
    def __init__(self, messages, colors):
        self.messages = messages
        self.colors = colors

    def toterminal(self, out):
        for message, color in zip(self.messages, self.colors):
            out.line(message, **color)
