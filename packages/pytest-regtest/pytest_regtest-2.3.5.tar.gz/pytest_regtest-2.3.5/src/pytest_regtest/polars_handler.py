import difflib
import io
import os
from typing import Any, Union

import polars as pl
from polars.testing import assert_frame_equal

from .snapshot_handler import BaseSnapshotHandler


class PolarsHandler(BaseSnapshotHandler):
    """
    PolarsHandler is a class for handling Polars DataFrame snapshots in pytest-regtest.
    """

    def __init__(self, handler_options: dict[str, Any], pytest_config, tw):
        self.atol = handler_options.get("atol", 0.0)
        self.rtol = handler_options.get("rtol", 0.0)
        self.display_options = handler_options.get("display_options", None)

    def _filename(self, folder: Union[str, os.PathLike[Any]]) -> str:
        return os.path.join(folder, "polars.parquet")

    def save(self, folder: Union[str, os.PathLike[Any]], obj: pl.DataFrame):
        obj.write_parquet(self._filename(folder))

    def load(self, folder: Union[str, os.PathLike[Any]]) -> pl.DataFrame:
        return pl.read_parquet(self._filename(folder))

    def show(self, obj: pl.DataFrame) -> list[str]:
        stream = io.StringIO()
        if self.display_options:
            with pl.Config(**self.display_options):
                stream.write(str(obj))
        else:
            stream.write(str(obj))
        return stream.getvalue().splitlines()

    def compare(self, current_obj: pl.DataFrame, recorded_obj: pl.DataFrame) -> bool:
        try:
            assert_frame_equal(
                current_obj, recorded_obj, atol=self.atol, rtol=self.rtol
            )
            return True
        except AssertionError:
            return False

    @staticmethod
    def create_schema_info(df: pl.DataFrame) -> list[str]:
        """
        Generate a summary of the schema information for a given Polars DataFrame.

        Parameters:
            df (pl.DataFrame): The Polars DataFrame for which to generate schema information.

        Returns:
            list[str]: A list of strings representing the schema information, including
                   the total number of columns, column names, non-null counts, and data types.
        """
        schema = df.schema
        schema_string_repr = [
            "Data columns (total {} columns):".format(len(schema)),
            " #   Column  Non-Null Count  Dtype  ",
            "---  ------  --------------  -----  ",
        ]
        for i, (column, dtype) in enumerate(schema.items()):
            total_count = df.height
            null_count = df[column].null_count()
            non_null_count = total_count - null_count
            dtype_str = str(dtype)
            schema_string_repr.append(
                f" {i}   {column}       {non_null_count} non-null      {dtype_str}"
            )
        return schema_string_repr

    def show_differences(
        self, current_obj: pl.DataFrame, recorded_obj: pl.DataFrame, has_markup: bool
    ) -> list[str]:
        lines = []

        current_schema = self.create_schema_info(current_obj)
        recorded_schema = self.create_schema_info(recorded_obj)

        info_diff = list(
            difflib.unified_diff(
                current_schema,
                recorded_schema,
                "current",
                "expected",
                lineterm="",
            )
        )
        lines.extend(info_diff)
        recorded_as_text = self.show(recorded_obj)
        current_as_text = self.show(current_obj)

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
