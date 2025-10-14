from __future__ import annotations

import textwrap
import typing as t

import pytest

from genguardx import CustomField
from genguardx._internal.mixins.with_fields import FieldType, WithFields
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import Objects


if t.TYPE_CHECKING:
    import pytest_mock


class TestWithFieldsMixin:
    def test_field_property_with_multiple_objects_of_same_type(self, mocker: pytest_mock.MockerFixture) -> None:
        """Test for DEF-1056."""

        mocker.patch(
            "genguardx._internal.settings.CustomField.all",
            return_value=[CustomField._from_data(data={"alias": "field_number"})],
        )

        class Entity(ApiBase, WithFields):
            _object_type = Objects.DATA_TABLE.value  # dummy value

        entity_data_common = {
            "entityFields": [
                {
                    "field": {
                        "alias": "field_number",
                        "fieldType": FieldType.NUMBER.value,
                    },
                    "shortTextValues": [{"id": 1, "value": None}],
                }
            ],
            "externalFields": [],
        }

        entity_data_common["entityFields"][0]["shortTextValues"][0]["value"] = "999"
        obj_1 = Entity._from_data(data=entity_data_common)
        obj_1._set_custom_fields()
        assert obj_1.field_number == pytest.approx(999)

        entity_data_common["entityFields"][0]["shortTextValues"][0]["value"] = "123"
        obj_2 = Entity._from_data(data=entity_data_common)
        obj_2._set_custom_fields()
        assert obj_2.field_number == pytest.approx(123)

        # Ensure that obj_1's custom field is not overridden by obj_2
        assert obj_1.field_number == pytest.approx(999)

    @pytest.mark.parametrize("field_type", (FieldType.NUMBER, FieldType.SHORT_TEXT, FieldType.SINGLE_SELECT))
    def test_set_custom_fields_invalid_multiple_values(
        self,
        mocker: pytest_mock.MockerFixture,
        *,
        field_type: FieldType,
    ) -> None:
        mocker.patch(
            "genguardx._internal.settings.CustomField.all",
            return_value=[CustomField._from_data(data={"alias": "custom_field"})],
        )

        class Entity(ApiBase, WithFields):
            _object_type = Objects.DATA_TABLE.value  # dummy value

        entity_data = {
            "entityFields": [
                {
                    "field": {
                        "alias": "custom_field",
                        "fieldType": field_type.value,
                    },
                    "shortTextValues": [{"id": 1, "value": "111"}, {"id": 2, "value": "222"}],
                }
            ],
            "externalFields": [],
        }

        entity = Entity._from_data(data=entity_data)
        with pytest.raises(AssertionError, match="Expected length of values to be 1 or less"):
            entity._set_custom_fields()

    @pytest.mark.parametrize("field_type", (FieldType.NUMBER, FieldType.SHORT_TEXT, FieldType.SINGLE_SELECT))
    def test_set_custom_fields_with_no_shorttext_value(
        self,
        mocker: pytest_mock.MockerFixture,
        *,
        field_type: FieldType,
    ) -> None:
        mocker.patch(
            "genguardx._internal.settings.CustomField.all",
            return_value=[CustomField._from_data(data={"alias": "custom_field"})],
        )

        class Entity(ApiBase, WithFields):
            _object_type = Objects.DATA_TABLE.value  # dummy value

        entity_data = {
            "entityFields": [
                {
                    "field": {
                        "alias": "custom_field",
                        "fieldType": field_type.value,
                    },
                    "shortTextValues": [],
                }
            ],
            "externalFields": [],
        }

        entity = Entity._from_data(data=entity_data)
        entity._set_custom_fields()
        assert entity.custom_field is None

    def test_set_custom_field_with_datetime_type(self, mocker: pytest_mock.MockerFixture) -> None:
        mocker.patch(
            "genguardx._internal.settings.CustomField.all",
            return_value=[CustomField._from_data(data={"alias": "custom_field"})],
        )

        class Entity(ApiBase, WithFields):
            _object_type = Objects.DATA_TABLE.value  # dummy value

        entity_data = {
            "entityFields": [
                {
                    "field": {
                        "alias": "custom_field",
                        "fieldType": FieldType.DATE_TIME.value,
                    },
                    "datetimeValue": {"id": 1, "value": "2024-08-17T17:50:00"},
                }
            ],
            "externalFields": [],
        }

        entity = Entity._from_data(data=entity_data)
        entity._set_custom_fields()
        assert entity.custom_field == "2024-08-17T17:50:00"

    def test_custom_field_docstring(self, mocker: pytest_mock.MockerFixture) -> None:
        mocker.patch(
            "genguardx._internal.settings.CustomField.all",
            return_value=[
                CustomField._from_data(data={"alias": "custom_field", "description": "Dummy field for test"})
            ],
        )

        class Entity(ApiBase, WithFields):
            _object_type = Objects.DATA_TABLE.value  # dummy value

        docstring = Entity._get_custom_field_docstring().strip()
        expected_docstring = textwrap.dedent("""
        Admin configured fields are:

            - custom_field: dataclasses.dataclass | float | str
                Dummy field for test

        Each field is an attribute of the object, with value as,
            - for file attachments, a dataclass having attributes
                - name: filename
                - content: io.BytesIO object
            - a floating point value for field type "Number"
            - a string in all other cases""").strip()

        assert docstring == expected_docstring

    def test_custom_field_docstring_with_exception(self, mocker: pytest_mock.MockerFixture) -> None:
        mocker.patch("genguardx._internal.settings.CustomField.all", side_effect=RuntimeError("Invalid filters"))

        class Entity(ApiBase, WithFields):
            _object_type = Objects.DATA_TABLE.value  # dummy value

        docstring = Entity._get_custom_field_docstring().strip()
        assert docstring == "Admin configured fields might also be available."
