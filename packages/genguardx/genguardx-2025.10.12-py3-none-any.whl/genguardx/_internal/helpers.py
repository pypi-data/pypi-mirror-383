"""
Helpers are functions exposed to simplify certain operations for a user of this library.
"""

from __future__ import annotations

import os
import typing as t

from genguardx._internal.util import utils


if t.TYPE_CHECKING:
    import pyspark.sql


def read_data(location: str) -> pyspark.sql.DataFrame:
    """
    Read data from the provided location.

    :param location:  The location to read data from.
    :return:          Spark DataFrame with the data at the location.
    """
    return utils.read_from_datasource(location)


def set_workspace(val: str) -> None:
    """
    Activate the workspace to use `corridor` functions with.

    :param val: The name of the workspace to be activated
    """
    os.environ["CORRIDOR_WORKSPACE"] = str(val)
