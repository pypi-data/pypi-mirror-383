import difflib
import io
import os.path
import warnings

import numpy as np

from .snapshot_handler import BaseSnapshotHandler
from .utils import highlight_mismatches


class NumpyHandler(BaseSnapshotHandler):
    def __init__(self, handler_options, pytest_config, tw):
        self.atol = handler_options.get("atol", 0.0)
        self.rtol = handler_options.get("rtol", 0.0)
        self.equal_nan = handler_options.get("equal_nan", True)
        if handler_options.get("print_options"):
            warnings.warn(
                "please use the numpy.printoptions context manager instead of"
                " the print_options argument.",
                DeprecationWarning,
            )

        self.print_options = np.get_printoptions() | handler_options.get(
            "print_options", {}
        )

    def _filename(self, folder):
        return os.path.join(folder, "arrays.npy")

    def save(self, folder, obj):
        np.save(self._filename(folder), obj)

    def load(self, folder):
        return np.load(self._filename(folder))

    def show(self, obj):
        stream = io.StringIO()
        with np.printoptions(**self.print_options):
            print(obj, file=stream)
        return stream.getvalue().splitlines()

    def compare(self, current_obj, recorded_obj):
        return (
            isinstance(current_obj, np.ndarray)
            and current_obj.shape == recorded_obj.shape
            and current_obj.dtype == recorded_obj.dtype
            and np.allclose(
                recorded_obj,
                current_obj,
                atol=self.atol,
                rtol=self.rtol,
                equal_nan=self.equal_nan,
            )
        )

    def show_differences(self, current_obj, recorded_obj, has_markup):
        lines = []

        if recorded_obj.dtype != current_obj.dtype:
            lines.extend(
                [
                    f"dtype mismatch: current dtype: {current_obj.dtype}",
                    f"               recorded dtype: {recorded_obj.dtype}",
                ]
            )

        recorded_as_text = self.show(recorded_obj)
        current_as_text = self.show(current_obj)

        if recorded_obj.shape == current_obj.shape:
            if np.allclose(current_obj, recorded_obj, rtol=self.rtol, atol=self.atol):
                return lines or None

            lines.extend(self.error_diagnostics(recorded_obj, current_obj))

        else:
            lines.extend(
                [
                    f"shape mismatch: current shape: {current_obj.shape}",
                    f"               recorded shape: {recorded_obj.shape}",
                ]
            )

        if recorded_obj.ndim > 2:
            return lines

        if recorded_obj.ndim == 1:
            diff_lines = list(
                difflib.unified_diff(
                    current_as_text,
                    recorded_as_text,
                    "current",
                    "expected",
                    lineterm="",
                )
            )
            lines.append("")
            lines.extend(diff_lines)

        else:
            diff_lines = self.error_diagnostics_2d_linewise(
                current_obj,
                current_as_text,
                recorded_obj,
                recorded_as_text,
                has_markup,
            )
            lines.extend(diff_lines)

        if not diff_lines:
            lines.append("diff is empty, you may want to change the print options")

        return lines

    def error_diagnostics(self, recorded_obj, current_obj):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            rel_err = np.abs(current_obj - recorded_obj) / recorded_obj
        rel_err[(recorded_obj == 0) * (current_obj == recorded_obj)] = 0.0
        rel_err_max_1 = np.max(rel_err)
        rel_err_max_2 = np.max(rel_err[recorded_obj != 0])

        abs_err = np.abs(current_obj - recorded_obj)
        abs_err_max = np.max(abs_err)

        lines = []

        if rel_err_max_1 == rel_err_max_2:
            lines.append(f"max relative deviation: {rel_err_max_1:e}")
        else:
            lines.append(f"max relative deviation: {rel_err_max_1:e}")
            lines.append(f"max relative deviation except inf: {rel_err_max_2:e}")

        lines.append(f"max absolute deviation: {abs_err_max:e}")

        n_diff = np.sum(
            np.logical_not(
                np.isclose(current_obj, recorded_obj, rtol=self.rtol, atol=self.atol)
            )
        )

        lines.append(
            f"both arrays differ in {n_diff} out of {np.prod(recorded_obj.shape)}"
            " entries"
        )
        lines.append(
            f"up to given precision settings rtol={self.rtol:e} and atol={self.atol:e}"
        )

        return lines

    def error_diagnostics_2d_linewise(
        self, current_obj, current_as_text, recorded_obj, recorded_as_text, has_markup
    ):
        sub_diff = []

        for i, (l1, l2, r1, r2) in enumerate(
            zip(current_as_text, recorded_as_text, current_obj, recorded_obj)
        ):
            if r1.shape == r2.shape and np.allclose(
                r1, r2, rtol=self.rtol, atol=self.atol
            ):
                continue

            if r1.shape == r2.shape:
                # enforces more uniform formatting of both lines:
                rows_together = np.vstack((r1, r2))
                lines_together = self.show(rows_together)
                line_diff = list(
                    difflib.unified_diff(
                        [lines_together[0][1:].strip()],
                        [lines_together[1][:-1].strip()],
                        "current",
                        "expected",
                        lineterm="",
                    )
                )
            else:
                row_1 = self.show(r1)
                row_2 = self.show(r2)
                line_diff = list(
                    difflib.unified_diff(
                        row_1,
                        row_2,
                        "current",
                        "expected",
                        lineterm="",
                    )
                )

            if line_diff:
                if not sub_diff:
                    sub_diff = line_diff[:2]

                l1, l2 = line_diff[-2], line_diff[-1]
                if has_markup:
                    l1, l2 = highlight_mismatches(l1, l2)

                sub_diff.append(f"row {i:3d}: {l1}")
                sub_diff.append(f"         {l2}")

        missing = len(current_as_text) - len(recorded_as_text)
        if missing > 0:
            for i, row in enumerate(current_as_text[-missing:], len(recorded_as_text)):
                # remove duplicate brackets
                row = row.rstrip("]") + "]"
                sub_diff.append(f"row {i:3d}: -{row.lstrip()}")
        if missing < 0:
            for i, row in enumerate(recorded_as_text[missing:], len(current_as_text)):
                # remove duplicate brackets
                row = row.rstrip("]") + "]"
                sub_diff.append(f"row {i:3d}: +{row.lstrip()}")

        return sub_diff
