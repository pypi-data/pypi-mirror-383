from __future__ import annotations

import io
import typing as t
import warnings

import pandas as pd

from genguardx._internal.mixins.auditable import Auditable
from genguardx._internal.mixins.searchable import Searchable
from genguardx._internal.mixins.with_fields import WithFields
from genguardx._internal.util import utils
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import Objects, URLS
from genguardx._internal.util.networking import api


if t.TYPE_CHECKING:
    import pyspark.sql


class DataColumn(ApiBase, Auditable):
    """
    Represents a DataColumn in a DataTable that is registered.

    :param table:   The table that the DataColumn belongs to.
    :param alias:   The alias of the DataColumn to fetch.
    :param id:      The ID of the DataColumn to fetch.

    The following properties of the DataTable can be accessed:
    - alias: string
        The alias of the DataTable.
    - type: string
        The type of the column - int, string, date, etc.
    - table: DataTable
        The list of column names available in the DataTable.
    """

    _LIST_URL = utils.ujoin(URLS.DATA_TABLE_PATH.value, "columns")
    _exposed_properties = {"id", "type", "alias"}

    def __init__(
        self,
        table: str | DataTable | None = None,
        alias: str | None = None,
        id: int | None = None,
    ) -> None:
        self._data_table = None
        filters: dict[str, t.Any] = {}
        if table is not None:
            if isinstance(table, str):  # Assume it to be the alias
                table = DataTable(table)
            self._data_table = table
            filters["dataTableId"] = table.id
        if id is not None:
            filters["ids"] = id
        if alias is not None:
            filters["alias"] = alias
        self._data = self._get_data(one=True, **filters)

    @property
    def table(self) -> DataTable:
        if self._data_table is None:
            self._data_table = DataTable(name=self._data["dataTableName"])
        return self._data_table

    def __str__(self) -> str:
        return f'<{type(self).__name__} table="{self.table.alias}", alias="{self.alias}">'


class DataTable(ApiBase, Auditable, Searchable, WithFields):
    """
    Represents a DataTable that is registered.

    :param alias:   The alias of the DataTable to fetch.
    :param name:    The name of the DataTable to fetch.
    :param id:      The ID of the DataTable to fetch.

    Example:
        >>> loans = DataTable('issued_loans')
        >>> loans.name
        'issued_loans'
        >>> loans.columns[:2]
        ['loan_id', 'term']
        >>> loans_df = loans.to_spark()
        >>> loans_df[['loan_id', 'term']].limit(3).show()
        +-----------+----+
        |    loan_id|term|
        +-----------+----+
        |49046025365|36.0|
        |44063010810|36.0|
        |46063058132|60.0|
        +-----------+----+

    The following properties of the DataTable can be accessed:
     - name: string
        The name of the DataTable.
     - alias: string
        The alias of the DataTable.
     - type: string
        The type of the DataTable as registered. Raw, Cleansed, OnboardedEntityTable, OnboardedEntityDetailsTable, etc.
     - columns: list of string
        The list of column names available in the DataTable.
     - dtypes: dict of column-alias: column-type
        The dict with keys as the column-alias, and the value as the column-type.
     - data_columns: list of class DataColumn
        The list of DataColumn objects for each column available in the DataTable.
     - location: string
        The location string used to fetch the actual data.
     - id: integer
        The ID that is unique to every DataTable.
     - description: string
        The description for the registered DataTable.
     - is_primary_table: string
        Flag to indicate whether the registered DataTable is primary table.
     - is_manual_input: string
        Flag to indicate whether the user choose to add columns of the registered DataTable manually
    - group: string
        The group that this DataTable belongs to.

    The following function can be accessed:
     - all(): list
        Returns a list of filtered DataTable objects
        Valid filters: name, contains, alias

    """

    _object_type = Objects.DATA_TABLE.value
    _LIST_URL = URLS.DATA_TABLE_PATH.value
    _exposed_properties = {"id", "location", "name", "alias", "type", "description", "group"}
    _available_filter_names = {"alias", "name", "contains", "group"}

    @utils.classproperty
    def tables(cls) -> list[DataTable]:
        """
        List of all tables that are registered.
        """
        warnings.warn(
            "`.tables` is deprecated and will be removed in the next version. Please use `.all()` instead",
            DeprecationWarning,
            stacklevel=1,
        )

        return [table.alias for table in cls.all()]

    def __init__(
        self,
        alias: str | None = None,
        name: str | None = None,
        id: int | None = None,
    ) -> None:
        filters: dict[str, t.Any] = {}
        if alias is not None:
            filters["alias"] = alias
        if name is not None:
            filters["name"] = name
        if id is not None:
            filters["ids"] = id
        self._data = self._get_data(one=True, **filters)
        self._set_custom_fields()

    @property
    def columns(self) -> list[DataColumn]:
        return [DataColumn(table=self, id=col["id"]) for col in self._data["dataColumns"]]

    @property
    def dtypes(self) -> dict[str, str]:
        return {col["alias"]: col["type"] for col in self._data["dataColumns"]}

    def to_spark(self) -> pyspark.sql.DataFrame:
        """
        Fetch the data referenced in a DataTable and get a PySpark DataFrame from it.

        :return: A pyspark dataframe with all the columns in this :class:`DataTable`.
        """
        if self._data.get("file", {}).get("id"):
            data_file_contents = api.response(
                utils.ujoin(URLS.ATTACHMENTS_PATH.value, str(self._data["file"]["id"])), out="bin"
            )
            # NOTE: This logic is repeated in:
            #        - corridor-api's    task_utils.read_data() (for type='datafile')
            #        - corridor-python's data_tables.to_spark()
            #       Ensure any changes made here are copied to the other places
            data = pd.read_json(
                io.BytesIO(data_file_contents), orient="split", dtype=str, convert_axes=False, convert_dates=False
            )
            spark = utils.get_spark()
            return spark.createDataFrame(data)

        return utils.read_from_datasource(self._data["location"])

    def __str__(self) -> str:
        return f'<{type(self).__name__} alias="{self.alias}">'
