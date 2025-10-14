from __future__ import annotations

import datetime
import typing as t

import pytest
from responses.matchers import query_param_matcher

from genguardx._internal.settings import CustomField, FieldType, User
from genguardx._internal.util.constants import Objects, URLS
from genguardx_test.helpers import api_url


if t.TYPE_CHECKING:
    import responses


class TestCustomField:
    def test_custom_field_init_by_id(self, responses: responses.RequestsMock) -> None:
        responses.add(
            responses.GET,
            api_url(URLS.FIELD_PATH.value),
            json={"result": [{"id": 1, "alias": "field_test"}]},
            match=[query_param_matcher({"ids": "1"}, strict_match=False)],
        )
        assert CustomField(id=1).alias == "field_test"

    def test_custom_field_init_by_alias(self, responses: responses.RequestsMock) -> None:
        responses.add(
            responses.GET,
            api_url(URLS.FIELD_PATH.value),
            json={"result": [{"id": 1, "alias": "field_test"}]},
            match=[query_param_matcher({"alias": "field_test"}, strict_match=False)],
        )
        assert CustomField(alias="field_test").alias == "field_test"

    def test_custom_field_init_by_name(self, responses: responses.RequestsMock) -> None:
        responses.add(
            responses.GET,
            api_url(URLS.FIELD_PATH.value),
            json={"result": [{"id": 1, "alias": "field_test", "name": "Test Field"}]},
            match=[query_param_matcher({"name": "Test Field"}, strict_match=False)],
        )
        assert CustomField(name="Test Field").alias == "field_test"

    def test_custom_field_number_with_default_value(self) -> None:
        data = {
            "id": 1,
            "alias": "test_field",
            "defaultLongTextValue": None,
            "defaultShortTextValues": [{"id": 1, "defaultValue": "999"}],
            "fieldType": FieldType.NUMBER.value,
            "objectTypes": [{"id": 1, "objectType": Objects.DATA_TABLE.value}],
            "optionShortTextValues": [],
        }
        field = CustomField._from_data(data=data)

        assert field.alias == "test_field"
        assert field.default_value == pytest.approx(999)
        assert field.options is None

    def test_custom_field_number_with_no_default_value(self) -> None:
        data = {
            "id": 1,
            "alias": "test_field",
            "defaultLongTextValue": None,
            "defaultShortTextValues": [],
            "fieldType": FieldType.NUMBER.value,
            "objectTypes": [{"id": 1, "objectType": Objects.DATA_TABLE.value}],
            "optionShortTextValues": [],
        }
        field = CustomField._from_data(data=data)

        assert field.alias == "test_field"
        assert field.default_value is None
        assert field.options is None

    def test_custom_field_short_text_with_default_value(self) -> None:
        data = {
            "id": 1,
            "alias": "test_field",
            "defaultLongTextValue": None,
            "defaultShortTextValues": [{"id": 1, "defaultValue": "corridor"}],
            "fieldType": FieldType.SHORT_TEXT.value,
            "objectTypes": [{"id": 1, "objectType": Objects.DATA_TABLE.value}],
            "optionShortTextValues": [],
        }
        field = CustomField._from_data(data=data)

        assert field.alias == "test_field"
        assert field.default_value == "corridor"
        assert field.options is None

    def test_custom_field_short_text_with_no_default_value(self) -> None:
        data = {
            "id": 1,
            "alias": "test_field",
            "defaultLongTextValue": None,
            "defaultShortTextValues": [],
            "fieldType": FieldType.SHORT_TEXT.value,
            "objectTypes": [{"id": 1, "objectType": Objects.DATA_TABLE.value}],
            "optionShortTextValues": [],
        }
        field = CustomField._from_data(data=data)

        assert field.alias == "test_field"
        assert field.default_value is None
        assert field.options is None

    def test_custom_field_long_text_with_default_value(self) -> None:
        data = {
            "id": 1,
            "alias": "test_field",
            "defaultLongTextValue": {"id": 1, "defaultValue": "corridor_long"},
            "defaultShortTextValues": [],
            "fieldType": FieldType.LONG_TEXT.value,
            "objectTypes": [{"id": 1, "objectType": Objects.DATA_TABLE.value}],
            "optionShortTextValues": [],
        }
        field = CustomField._from_data(data=data)

        assert field.alias == "test_field"
        assert field.default_value == "corridor_long"
        assert field.options is None

    def test_custom_field_long_text_with_no_default_value(self) -> None:
        data = {
            "id": 1,
            "alias": "test_field",
            "defaultLongTextValue": None,
            "defaultShortTextValues": [],
            "fieldType": FieldType.LONG_TEXT.value,
            "objectTypes": [{"id": 1, "objectType": Objects.DATA_TABLE.value}],
            "optionShortTextValues": [],
        }
        field = CustomField._from_data(data=data)

        assert field.alias == "test_field"
        assert field.default_value is None
        assert field.options is None

    def test_custom_field_single_select_with_default_value(self) -> None:
        data = {
            "id": 1,
            "alias": "test_field",
            "defaultLongTextValue": None,
            "defaultShortTextValues": [{"id": 1, "defaultValue": "b"}],
            "fieldType": FieldType.SINGLE_SELECT.value,
            "objectTypes": [{"id": 1, "objectType": Objects.DATA_TABLE.value}],
            "optionShortTextValues": [
                {"id": 1, "optionValue": "a"},
                {"id": 2, "optionValue": "b"},
                {"id": 3, "optionValue": "c"},
            ],
        }
        field = CustomField._from_data(data=data)

        assert field.alias == "test_field"
        assert field.default_value == "b"
        assert field.options == ["a", "b", "c"]

    def test_custom_field_single_select_with_no_default_value(self) -> None:
        data = {
            "id": 1,
            "alias": "test_field",
            "defaultLongTextValue": None,
            "defaultShortTextValues": [],
            "fieldType": FieldType.SINGLE_SELECT.value,
            "objectTypes": [{"id": 1, "objectType": Objects.DATA_TABLE.value}],
            "optionShortTextValues": [
                {"id": 1, "optionValue": "a"},
                {"id": 2, "optionValue": "b"},
                {"id": 3, "optionValue": "c"},
            ],
        }
        field = CustomField._from_data(data=data)

        assert field.alias == "test_field"
        assert field.default_value is None
        assert field.options == ["a", "b", "c"]

    def test_custom_field_multi_select_with_default_values(self) -> None:
        data = {
            "id": 1,
            "alias": "test_field",
            "defaultLongTextValue": None,
            "defaultShortTextValues": [{"id": 1, "defaultValue": "b"}, {"id": 2, "defaultValue": "c"}],
            "fieldType": FieldType.MULTI_SELECT.value,
            "objectTypes": [{"id": 1, "objectType": Objects.DATA_TABLE.value}],
            "optionShortTextValues": [
                {"id": 1, "optionValue": "a"},
                {"id": 2, "optionValue": "b"},
                {"id": 3, "optionValue": "c"},
            ],
        }
        field = CustomField._from_data(data=data)

        assert field.alias == "test_field"
        assert field.default_value == ["b", "c"]
        assert field.options == ["a", "b", "c"]

    def test_custom_field_multi_select_with_no_default_values(self) -> None:
        data = {
            "id": 1,
            "alias": "test_field",
            "defaultLongTextValue": None,
            "defaultShortTextValues": [],
            "fieldType": FieldType.MULTI_SELECT.value,
            "objectTypes": [{"id": 1, "objectType": Objects.DATA_TABLE.value}],
            "optionShortTextValues": [
                {"id": 1, "optionValue": "a"},
                {"id": 2, "optionValue": "b"},
                {"id": 3, "optionValue": "c"},
            ],
        }
        field = CustomField._from_data(data=data)

        assert field.alias == "test_field"
        assert field.default_value is None
        assert field.options == ["a", "b", "c"]

    def test_custom_field_str_cast(self) -> None:
        field = CustomField._from_data(data={"id": 1, "name": "Test Field"})
        assert str(field) == '<CustomField name="Test Field">'


class TestUser:
    def test_user_init_with_id(self, responses: responses.RequestsMock) -> None:
        responses.add(
            responses.GET,
            api_url(URLS.USER_PATH.value),
            json={
                "result": [
                    {
                        "email": "corridorautomationHDT@mailinator.com",
                        "id": 1,
                        "isActive": True,
                        "lastLoginDate": "2024-08-21T05:51:03.324609",
                        "name": "master",
                        "roles": [4],
                        "rolesWithWorkspace": [
                            {"name": "Master", "workspace": "corridor"},
                        ],
                        "secondLastLoginDate": "2024-08-21T05:41:04.708540",
                        "visibleName": "master",
                    }
                ]
            },
            match=[query_param_matcher({"ids": 1}, strict_match=False)],
        )

        assert User(id=1).username == "master"

    def test_user_init_with_username(self, responses: responses.RequestsMock) -> None:
        responses.add(
            responses.GET,
            api_url(URLS.USER_PATH.value),
            json={
                "result": [
                    {
                        "email": "corridorautomationHDT@mailinator.com",
                        "id": 1,
                        "isActive": True,
                        "lastLoginDate": "2024-08-21T05:51:03.324609",
                        "name": "master",
                        "roles": [4],
                        "rolesWithWorkspace": [
                            {"name": "Master", "workspace": "corridor"},
                        ],
                        "secondLastLoginDate": "2024-08-21T05:41:04.708540",
                        "visibleName": "master",
                    }
                ]
            },
            match=[query_param_matcher({"name": "master"}, strict_match=False)],
        )

        assert User("master").id == 1

    def test_user_last_login_date(self) -> None:
        user = User._from_data(data={"id": 1, "name": "master", "lastLoginDate": "2024-08-21T05:51:00.000000"})

        date = user.last_login_date

        assert date == datetime.datetime(year=2024, month=8, day=21, hour=5, minute=51)

    def test_user_last_login_date_absent(self) -> None:
        user = User._from_data(data={"id": 1, "name": "master", "lastLoginDate": None})
        assert user.last_login_date is None

    def test_user_str_cast(self) -> None:
        user = User._from_data(data={"id": 1, "name": "master"})
        assert str(user) == '<User username="master">'
