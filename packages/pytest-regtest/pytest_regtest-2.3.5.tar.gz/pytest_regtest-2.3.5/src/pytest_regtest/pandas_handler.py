import difflib
import io
import os.path
import warnings

import numpy as np
import pandas as pd

from .snapshot_handler import BaseSnapshotHandler


class DataFrameHandler(BaseSnapshotHandler):
    def __init__(self, handler_options, pytest_config, tw):
        if handler_options.get("display_options"):
            warnings.warn(
                "please use the 'pandas.option_context' context manager instead of"
                " the display_options argument.",
                DeprecationWarning,
            )

        # default contains a few nested dicts and we flatten those, e.g.
        # { "html": {"border": 1} } -> { "html.border": 1 }
        default = list(pd.options.display.d.items())
        default_flattened = {}
        for k, v in default:
            if isinstance(v, dict):
                for k0, v0 in v.items():
                    default_flattened[f"{k}.{k0}"] = v0
            else:
                default_flattened[k] = v

        # overwrite with user settings:
        items = (default_flattened | handler_options.get("display_options", {})).items()

        # flatten items as required by pandas.option_context:
        self.display_options_flat = [
            entry for item in items for entry in (f"display.{item[0]}", item[1])
        ]
        self.atol = handler_options.get("atol", 0.0)
        self.rtol = handler_options.get("rtol", 0.0)

    def _filename(self, folder):
        return os.path.join(folder, "dataframe.pkl")

    def save(self, folder, obj):
        obj.to_pickle(self._filename(folder), compression="gzip")

    def load(self, folder):
        return pd.read_pickle(self._filename(folder), compression="gzip")

    def show(self, obj):
        stream = io.StringIO()
        with pd.option_context(*self.display_options_flat):
            print(obj, file=stream)
        return stream.getvalue().splitlines()

    def compare(self, current, recorded):
        missing = set(
            n
            for (n, t) in set(zip(recorded.columns, recorded.dtypes))
            ^ set(zip(current.columns, current.dtypes))
        )

        if missing:
            return False

        common = set(
            n
            for (n, t) in set(zip(recorded.columns, recorded.dtypes))
            & set(zip(current.columns, current.dtypes))
        )
        current_reduced = current[[n for n in current.columns if n in common]]
        recorded_reduced = recorded[[n for n in recorded.columns if n in common]]

        def extract(df, selector):
            return df[[n for (n, t) in zip(df.columns, df.dtypes) if selector(t)]]

        def is_float(t):
            return t.type in (np.float64, np.float32)

        current_reduced_floats = extract(current_reduced, is_float).to_numpy()

        current_reduced_other = extract(current_reduced, lambda t: not is_float(t))

        recorded_reduced_floats = extract(recorded_reduced, is_float).to_numpy()

        recorded_reduced_other = extract(recorded_reduced, lambda t: not is_float(t))

        return np.allclose(
            current_reduced_floats,
            recorded_reduced_floats,
            atol=self.atol,
            rtol=self.rtol,
            equal_nan=True,
        ) and current_reduced_other.equals(recorded_reduced_other)

    def show_differences(self, current, recorded, has_markup):
        lines = []

        stream = io.StringIO()
        current.info(buf=stream, verbose=True, memory_usage=False)
        current_info = stream.getvalue().splitlines()[2:][:-1]

        stream = io.StringIO()
        recorded.info(buf=stream, verbose=True, memory_usage=False)
        recorded_info = stream.getvalue().splitlines()[2:][:-1]

        info_diff = list(
            difflib.unified_diff(
                current_info,
                recorded_info,
                "current",
                "expected",
                lineterm="",
            )
        )
        lines.extend(info_diff)

        recorded_as_text = self.show(recorded)
        current_as_text = self.show(current)

        diffs = list(
            difflib.unified_diff(
                current_as_text,
                recorded_as_text,
                "current",
                "expected",
                lineterm="",
            )
        )

        lines.append("")
        if diffs:
            lines.extend(diffs)
        else:
            lines.append("diff is empty, you may want to change the print options")

        return lines
