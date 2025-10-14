from __future__ import annotations

import datetime

import dateutil.parser


class Auditable:
    """
    Represents an item that has auditing fields.

    The following properties of the item can be accessed:
     - created_by: string
        The username of the user that created the item.
     - created_date: datetime
        The date when the item was created.
     - last_modified_by: string
        The username of the user that last modified the item.
     - last_modified_date: datetime
        The date when the item was last modified.
    """

    @property
    def created_date(self) -> datetime.datetime:
        return dateutil.parser.parse(self._data["createdDate"])

    @property
    def created_by(self) -> str:
        return self._data["createdBy"]

    @property
    def last_modified_date(self) -> datetime.datetime:
        return dateutil.parser.parse(self._data["lastModifiedDate"])

    @property
    def last_modified_by(self) -> str:
        return self._data["lastModifiedBy"]
