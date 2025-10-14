from __future__ import annotations

import typing as t

from genguardx._internal.data_tables import DataColumn, DataTable
from genguardx._internal.mixins.auditable import Auditable
from genguardx._internal.mixins.searchable import Searchable
from genguardx._internal.mixins.simulatable import Simulatable
from genguardx._internal.mixins.with_fields import WithFields
from genguardx._internal.mixins.with_notes import WithNotes
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import Objects, URLS


class QualityCheck(ApiBase, Auditable, Simulatable, Searchable, WithNotes, WithFields):
    """
    Represents a QualityCheck that is registered.

    :param name:    The name of the QualityCheck to fetch.
    :param id:      The ID of the QualityCheck to fetch. If provided, name is not used.

    Example:
        >>> check_nulls = QualityCheck('Check Nulls in critical columns')
        >>> check_nulls.name
        'Check Nulls in critical columns'

    The following properties of the QualityCheck can be accessed:
     - name: string
        The name of the QualityCheck as registered.
     - group: string
        The group that this QualityCheck belongs to.
     - description: string
        The description registered for the QualityCheck.
     - data_table: DataTable
        The table that this QualityCheck is going to run on
     - data_columns: list of DataColumns
        The list of columns from the table that this QualityCheck is going to run on
     - note: string
        Any notes added during registration.
     - id: integer
        The ID that is unique to every QualityCheck.
     - created_by: string
        The username of the user that created the QualityCheck.
     - created_date: datetime
        The date that this QualityCheck was created.
     - last_modified_by: string
        The username of the QualityCheck that last modified the item.
     - last_modified_date: datetime
        The date when the QualityCheck was last modified.

    The following functions of the QualityCheck can be accessed:
     - all(): list
        Returns a list of filtered QualtyCheck objects
        Valid filters: name, contains, group

    """

    _object_type = Objects.QUALITY_CHECK.value
    _LIST_URL = URLS.QUALITY_PROFILE_PATH.value
    _exposed_properties = {"id", "name", "description", "note", "group"}

    _available_filter_names = {"name", "contains", "group"}

    class Job(Simulatable.Job):
        _object_class = staticmethod(lambda: QualityCheck)

    def __init__(self, name: str | None = None, id: int | None = None) -> None:
        filters: dict[str, t.Any] = {}
        if id is not None:
            filters["ids"] = id
        if name is not None:
            filters["name"] = name
        self._data = self._get_data(one=True, **filters)
        self._set_custom_fields()

    @property
    def data_columns(self) -> list[DataColumn]:
        return [DataColumn(id=i) for i in self._data["inputColumns"]]

    @property
    def data_table(self) -> DataTable:
        return DataTable(id=self._data["dataTableId"])

    def __str__(self) -> str:
        return f'<{type(self).__name__} name="{self.name}">'
