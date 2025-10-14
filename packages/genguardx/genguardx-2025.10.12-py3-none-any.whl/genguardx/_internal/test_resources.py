from __future__ import annotations

import re
import typing as t

import pytest
from responses.matchers import query_param_matcher

from genguardx._internal.resources import (
    GlobalFunction,
    GlobalVariable,
    Report,
    ReportOutput,
    ReportParameter,
)
from genguardx._internal.util.constants import DataType, URLS
from genguardx_test.helpers import api_url


if t.TYPE_CHECKING:
    import pytest_mock
    import responses


class TestGlobalFunction:
    def test_attribute_deprecation_global_functions(self, mocker: pytest_mock.MockerFixture) -> None:
        all_mocked = mocker.patch("genguardx._internal.resources.GlobalFunction.all")

        with pytest.warns(
            DeprecationWarning,
            match=re.escape(
                "`.global_functions` is deprecated and will be removed in the next version. Please use `.all()` instead"
            ),
        ):
            GlobalFunction.global_functions  # noqa: B018 -- Trigger internal call to `.all()`

        all_mocked.assert_called_once()

    def test_init_with_alias(self, responses: responses.RequestsMock) -> None:
        responses.add(
            responses.GET,
            api_url(URLS.GLOBAL_FUNCTION_PATH.value),
            json={"result": [{"id": 999, "definitionAlias": "gf_test", "entityFields": [], "externalFields": []}]},
            match=[query_param_matcher({"alias": "gf_test"}, strict_match=False)],
        )
        responses.add(responses.GET, api_url(URLS.FIELD_PATH.value), json={"result": []})

        gf = GlobalFunction(alias="gf_test")
        assert gf.id == 999
        assert gf.alias == "gf_test"

    def test_gf_with_no_definition(self) -> None:
        gf = GlobalFunction._from_data(data={"id": 101})
        assert gf.id == 101
        assert gf.definition is None

    def test_gf_with_invalid_inputs(self, mocker: pytest_mock.MockerFixture) -> None:
        inputs_mocked = mocker.patch(
            "genguardx._internal.resources.GlobalFunction.inputs", new_callable=mocker.PropertyMock
        )
        inputs_mocked.return_value = [GlobalVariable._from_data(data={"definitionAlias": "gv1"})]

        gf_invalid = GlobalFunction._from_data(data={"definitionAlias": "gf_invalid"})

        with pytest.raises(
            ValueError,
            match="Global Functions only support Global Functions and Runtime Parameters as input",
        ):
            gf_invalid.get_python_function()

    def test_python_function_with_duplicate_inputs(self, mocker: pytest_mock.MockerFixture) -> None:
        gf_max_of_2 = GlobalFunction._from_data(
            data={
                "definitionAlias": "gf_max_of_2",
                "featureVersionIds": [],
                "functionInputs": [
                    {"alias": "num1", "isMandatory": False, "defaultValue": "0", "inputType": DataType.NUMERICAL.value},
                    {"alias": "num2", "isMandatory": False, "defaultValue": "0", "inputType": DataType.NUMERICAL.value},
                ],
                "definition": {"runLogic": "return max(num1, num2)"},
                "version": 1,
            }
        )
        gf_max_of_3 = GlobalFunction._from_data(
            data={
                "definitionAlias": "gf_max_of_3",
                "featureVersionIds": [1401],
                "functionInputs": [
                    {"alias": "num1", "isMandatory": False, "defaultValue": "0", "inputType": DataType.NUMERICAL.value},
                    {"alias": "num2", "isMandatory": False, "defaultValue": "0", "inputType": DataType.NUMERICAL.value},
                    {"alias": "num3", "isMandatory": False, "defaultValue": "0", "inputType": DataType.NUMERICAL.value},
                ],
                "definition": {"runLogic": "return max(gf_max_of_2(num1, num2), num3)"},
                "version": 1,
            }
        )

        mocker.patch("genguardx._internal.resources.GlobalFunction.inputs")
        gf_max_of_2.inputs = []
        # Add a duplicate entry to inputs. De-duping should be handled internally
        gf_max_of_3.inputs = [gf_max_of_2, gf_max_of_2]

        max_of_3 = gf_max_of_3.get_python_function()
        assert max_of_3(400, 500, 300) == 500


class TestReport:
    def test_init_with_name(self, responses: responses.RequestsMock) -> None:
        responses.add(
            responses.GET,
            api_url(URLS.REPORT_PATH.value),
            json={"result": [{"id": 999, "name": "report_test", "entityFields": [], "externalFields": []}]},
            match=[query_param_matcher({"name": "report_test"}, strict_match=False)],
        )
        responses.add(responses.GET, api_url(URLS.FIELD_PATH.value), json={"result": []})

        report = Report(name="report_test")
        assert report.id == 999
        assert report.name == "report_test"

    def test_init_with_version(self, responses: responses.RequestsMock) -> None:
        responses.add(
            responses.GET,
            api_url(URLS.REPORT_PATH.value),
            json={"result": [{"id": 999, "version": 2, "entityFields": [], "externalFields": []}]},
            match=[query_param_matcher({"version": 2}, strict_match=False)],
        )
        responses.add(responses.GET, api_url(URLS.FIELD_PATH.value), json={"result": []})

        report = Report(version=2)
        assert report.id == 999
        assert report.version == 2

    def test_attribute_definition(self) -> None:
        report = Report._from_data(data={"id": 101, "definition": {"runLogic": "return None"}})
        assert report.id == 101
        assert report.definition == "return None"

    def test_attribute_definition_absent(self) -> None:
        report = Report._from_data(data={"id": 101})
        assert report.id == 101
        assert report.definition is None

    def test_docstring_caching(self, mocker: pytest_mock.MockerFixture) -> None:
        custom_field_docstring_spy = mocker.spy(Report, "_get_custom_field_docstring")

        doc1 = Report.__doc__
        custom_field_docstring_spy.assert_called_once()

        doc2 = Report.__doc__
        custom_field_docstring_spy.assert_called_once()

        assert doc1 == doc2


class TestReportOutput:
    def test_attribute_definition_absent(self) -> None:
        report_output = ReportOutput._from_data(data={"id": 101})
        assert report_output.id == 101
        assert report_output.definition is None

    def test_str_cast(self) -> None:
        report_output = ReportOutput._from_data(
            data={"name": "Download Data Output"},
            report=Report._from_data(data={"name": "Dataset Download Data Report"}),
        )

        assert str(report_output) == '<ReportOutput report="Dataset Download Data Report" name="Download Data Output">'


class TestReportParameter:
    def test_str_cast(self) -> None:
        report_parameter = ReportParameter._from_data(
            data={"name": "ROC Parameter"},
            report=Report._from_data(data={"name": "ROC Curve"}),
        )

        assert str(report_parameter) == '<ReportParameter report="ROC Curve" name="ROC Parameter">'
