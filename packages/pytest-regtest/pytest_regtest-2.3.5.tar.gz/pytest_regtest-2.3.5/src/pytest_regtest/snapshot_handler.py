import abc
import difflib
import os
import pickle
import pprint
from collections.abc import Callable
from typing import Any, Union

import pytest


class BaseSnapshotHandler(abc.ABC):
    """
    Abstract base class to implement snapshot handlers.
    """

    @abc.abstractmethod
    def __init__(
        handler_options: dict[str, Any],
        pytest_config: type[pytest.Config],
        tw: int,
    ) -> None:
        """
        This method is called within `snapshot.check` to configure the handler.

        Parameters:
                handler_options: Keyword arguments from `shapshot.check` call
                pytest_config: `pytest` config object.
                tw: Terminal width.
        """

    @abc.abstractmethod
    def save(self, folder: Union[str, os.PathLike[Any]], obj: Any) -> None:
        """
        This method is called when a snapshot is reset, and a subclass must store the
        given object in the given folder. How this folder is managed internally is
        entirely up to the snapshot handler. It can be a single file, or a complex
        structure of multiple files and sub-folders.


        Parameters:
                folder: Path to the folder. The folder exists already when this
                        method is called.
                obj: The object from the `snapshot.check` call.
        """

    @abc.abstractmethod
    def load(self, folder: Union[str, os.PathLike[Any]]) -> Any:
        """
        This method loads an existing snapshot from the given folder and must
        be consistent with the `save` method.

        Parameters:
                folder: Path to the folder. The folder exists already when this
                        method is called.

        Returns:
               The loaded object.
        """

    @abc.abstractmethod
    def show(self, obj: Any) -> list[str]:
        """
        This method returns a line wise textual representation of the given object.

        Parameters:
                obj: The object the snapshot handler is managing.

        Returns:
                List of strings.
        """

    @abc.abstractmethod
    def compare(self, current_obj: Any, recorded_obj: Any) -> bool:
        """
        The method compares if the current object from the
        `snapshot.check` call and the object loaded with the `load`
        method are considered to be the same. If this returns `True`
        the `snapshot.check` call will pass.

        Parameters:
                current_obj: The object the snapshot handler receiving from
                            `snapshot.check`.
                recorded_obj: The object the snapshot handler is loading with
                        the `load` method.

        Returns:
                Boolean value which decides is the `snapshot.check` call will pass.
        """

    @abc.abstractmethod
    def show_differences(
        self, current_obj: Any, recorded_obj: Any, has_markup: bool
    ) -> list[str]:
        """
        The method shows differences between the object from the
        `snapshot.check` call and the object loaded with the `load`
        method.

        Parameters:
                current_obj: The object the snapshot handler receiving from
                            `snapshot.check`.
                recorded_obj: The object the snapshot handler is loading with
                        the `load` method.
                has_markup: Indicates if the tests run within a terminal and
                        the method can use color output in case `has_markup` is
                        `True`.

        Returns:
                List of strings to describe the differences.
        """


class SnapshotHandlerRegistry:
    """
    This class serves as a registry for the builtin snapshot handlers
    and can be used to add more handlers for particular data types.
    """

    _snapshot_handlers: list[tuple[Callable[[Any], bool]]] = []

    @classmethod
    def add_handler(
        clz,
        check_function: Callable[[Any], bool],
        handler_class: type[BaseSnapshotHandler],
    ):
        """Add a handler.

        Parameters:
                check_function: A function which takes an object and returns `True`
                                if the `handler_class` argument should be
                                used for the given object.
        """

        clz._snapshot_handlers.append((check_function, handler_class))

    @classmethod
    def get_handler(clz, obj: Any) -> BaseSnapshotHandler:
        """Find and initialize handler for the given object.

        Parameters:
            obj: The object for which we try to find a handler.

        Returns:
            An instance of the handler or `None` if no appropriate handler was found.
        """
        for check_function, handler in clz._snapshot_handlers:
            if check_function(obj):
                return handler
        return None


class PythonObjectHandler(BaseSnapshotHandler):
    def __init__(self, handler_options, pytest_config, tw):
        self.compact = handler_options.get("compact", False)

    def save(self, folder, obj):
        with open(os.path.join(folder, "object.pkl"), "wb") as fh:
            pickle.dump(obj, fh)

    def load(self, folder):
        with open(os.path.join(folder, "object.pkl"), "rb") as fh:
            return pickle.load(fh)

    def show(self, obj):
        return pprint.pformat(obj, compact=self.compact).splitlines()

    def compare(self, current_obj, recorded_obj):
        return recorded_obj == current_obj

    def show_differences(self, current_obj, recorded_obj, has_markup):
        return list(
            difflib.unified_diff(
                self.show(current_obj),
                self.show(recorded_obj),
                "current",
                "expected",
                lineterm="",
            )
        )


def register_python_object_handler():
    SnapshotHandlerRegistry.add_handler(
        lambda obj: isinstance(obj, (int, float, str, list, tuple, dict, set)),
        PythonObjectHandler,
    )
