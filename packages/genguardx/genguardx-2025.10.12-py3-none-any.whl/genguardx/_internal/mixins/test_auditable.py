from __future__ import annotations

from genguardx._internal.mixins.auditable import Auditable


class ExObject(Auditable):
    def __init__(self, data: dict) -> None:
        self._data = data


class TestAuditable:
    def test_creation_fields(self) -> None:
        obj = ExObject({"createdBy": "abc", "createdDate": "2020-01-01T01:01:01.111111"})
        assert obj.created_by == "abc"
        assert obj.created_date.year == 2020

    def test_modification_fields(self) -> None:
        obj = ExObject({"lastModifiedBy": "abc", "lastModifiedDate": "2020-01-01T01:01:01.111111"})
        assert obj.last_modified_by == "abc"
        assert obj.last_modified_date.year == 2020
