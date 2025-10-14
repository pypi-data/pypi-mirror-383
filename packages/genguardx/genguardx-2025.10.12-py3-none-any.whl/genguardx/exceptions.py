from __future__ import annotations

import typing as t


class NotFound(Exception):
    """
    :param message: Error message (stored in Exception.args[0])
    :param filters: The filters that were being used to fetch the object
    :param name:    The name of what was not found.
                    This can be a string, a Object, or a class in corridor.
                    For example: Feature(1) will throw an error with name=Feature
    """

    def __init__(self, *args, name: str | None = None, filters: dict[str, t.Any] | None = None) -> None:
        super().__init__(*args)
        self.name = name
        self.filters = filters
