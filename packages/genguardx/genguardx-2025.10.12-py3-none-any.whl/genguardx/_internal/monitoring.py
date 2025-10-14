from __future__ import annotations

import typing as t

from genguardx._internal.mixins.auditable import Auditable
from genguardx._internal.mixins.searchable import Searchable
from genguardx._internal.mixins.simulatable import Simulatable
from genguardx._internal.mixins.with_fields import WithFields
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import Objects, URLS


class Monitoring(
    ApiBase,
    Auditable,
    Simulatable,
    Searchable,
    WithFields,
):
    """
    Represents a registered Monitoring.
    :param name:    The name of the Monitoring to fetch.
    :param id:      The ID of the Monitoring to fetch. If provided, name is not used.

    The following properties of the Foundation Model can be accessed:
    - id: integer
        The ID that is unique to every Foundation Model.
    - name: string
        The name of the Foundation Model as registered.
    - description: string
        The description registered for the Foundation Model.
    - created_by: string
        The username of the user that created the Foundation Model.
    - created_date: datetime
        The date that this Foundation Model was created.
    """

    _object_type = Objects.MONITORING.value
    _LIST_URL = URLS.MONITORING_PATH.value
    _available_filter_names = {"alias", "name"}

    _exposed_properties = {
        "id",
        "name",
        "description",
    }

    def __init__(self, name: str | None = None, id: int | None = None) -> None:
        filters: dict[str, t.Any] = {}
        if id is not None:
            filters["ids"] = id
        if name is not None:
            filters["name"] = name
        elif id is None:  # If ID is none, we need to get the "current" version
            filters["singleVersionOnly"] = True
        self._data = self._get_data(one=True, **filters)
        self._set_custom_fields()

    class Job(Simulatable.Job):
        _object_class = staticmethod(lambda: Monitoring)

    def __str__(self) -> str:
        return f'<{type(self).__name__} name="{self.name}">'
