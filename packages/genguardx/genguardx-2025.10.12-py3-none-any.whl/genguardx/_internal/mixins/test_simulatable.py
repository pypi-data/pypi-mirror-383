from __future__ import annotations

import typing as t

import pytest
from responses.matchers import query_param_matcher

from genguardx._internal.mixins.simulatable import Simulatable
from genguardx._internal.util import utils
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import ReportParameterType, URLS
from genguardx_test.helpers import api_url


if t.TYPE_CHECKING:
    import pytest_mock
    import responses


class TestSimulatable:
    def test_get_sim_by_name(self, responses: responses.RequestsMock) -> None:
        class CustomObject(Simulatable):
            _LIST_URL = "/api/v1/custom_object"

            class Job(Simulatable.Job):
                _object_class = staticmethod(lambda: CustomObject)

        responses.add(
            responses.GET,
            api_url(CustomObject.Job._LIST_URL),
            json={"result": [{"id": 101, "name": "sim_1"}]},
            match=[query_param_matcher({"name": "sim_1"}, strict_match=False)],
        )
        responses.add(
            responses.GET,
            utils.ujoin(api_url(CustomObject.Job._LIST_URL), 101),
            json={"result": {"id": 101, "name": "sim_1"}},
        )

        sim = CustomObject.Job(name="sim_1")
        assert sim.id == 101
        assert sim.name == "sim_1"

    def test_get_sim_by_entity_id(self, responses: responses.RequestsMock) -> None:
        class CustomObject(Simulatable):
            _LIST_URL = "/api/v1/custom_object"

            class Job(Simulatable.Job):
                _object_class = staticmethod(lambda: CustomObject)

        responses.add(
            responses.GET,
            api_url(CustomObject.Job._LIST_URL),
            json={"result": [{"id": 101, "name": "sim_1"}]},
            match=[query_param_matcher({"entityId": 1}, strict_match=False)],
        )
        responses.add(
            responses.GET,
            utils.ujoin(api_url(CustomObject.Job._LIST_URL), 101),
            json={"result": {"id": 101, "name": "sim_1"}},
        )

        sim = CustomObject.Job(entity=1)
        assert sim.id == 101
        assert sim.name == "sim_1"

    def test_get_sim_by_invalid_entity_identifier(self) -> None:
        class CustomObject(Simulatable):
            _LIST_URL = "/api/v1/custom_object"

        with pytest.raises(NotImplementedError, match="Expect entity to be either integer or Simulatable"):
            CustomObject.Job(entity="invalid")

    def test_sample_size_attr_with_sample_ratio(self) -> None:
        sim = Simulatable.Job._from_data(
            data={"inputData": {"sampleInfo": {"sampleRatio": 12, "type": "Sample Ratio"}}}
        )
        assert sim.sample_size == "12%"

    def test_runtime_attribute(self) -> None:
        sim = Simulatable.Job._from_data(data={"jobTimeInfo": {"runTime": 106.000000}})
        assert sim.runtime.seconds == 106

    def test_runtime_attribute_with_no_timeinfo(self) -> None:
        sim = Simulatable.Job._from_data(data={"jobTimeInfo": {"startTime": "2024-08-26T13:47:05.089293"}})
        assert sim.runtime is None

    def test_logs_attribute_with_no_log_attachment(self) -> None:
        sim = Simulatable.Job._from_data(data={"jobExecLogAttachment": None})
        assert sim.logs is None

    def test_logs_attribute_with_log_attachment(self, responses: responses.RequestsMock) -> None:
        sim = Simulatable.Job._from_data(data={"jobExecLogAttachment": {"id": 1}})
        responses.add(responses.GET, utils.ujoin(api_url(URLS.ATTACHMENTS_PATH.value), 1), body=b"corridor")
        assert sim.logs == "corridor"

    def test_current_attribute_with_entity_id(self, mocker: pytest_mock.MockerFixture) -> None:
        class CustomObject(Simulatable):
            _LIST_URL = "/api/v1/custom_object"

            class Job(Simulatable.Job):
                _object_class = staticmethod(lambda: CustomObject)

        constructor_mocked = mocker.patch.object(CustomObject, "__init__", return_value=None)

        sim = CustomObject.Job._from_data(data={"entityId": 101})
        sim.current  # noqa: B018 -- Access attribute to test internal call to constructor
        constructor_mocked.assert_called_once_with(id=101)

    def test_report_parameters_no_input_value(self) -> None:
        sim = Simulatable.Job._from_data(
            data={"reportData": {"weight": {"name": "Weight", "type": ReportParameterType.STRING.value, "value": ""}}}
        )
        assert sim.parameters == {"weight": None}

    def test_report_parameters_with_invalid_type(self) -> None:
        sim = Simulatable.Job._from_data(
            data={"reportData": {"weight": {"name": "Weight", "type": "invalid", "value": "19"}}}
        )
        with pytest.raises(TypeError, match=r"Expected report parameters to be of type: .*"):
            sim.parameters  # noqa: B018 -- Call property

    @pytest.mark.parametrize("ipython_available", (True, False))
    def test_process_report_figure_with_image_mimetype(
        self,
        mocker: pytest_mock.MockerFixture,
        *,
        ipython_available: bool,
    ) -> None:
        if ipython_available is False:
            mocker.patch.dict("sys.modules", {"IPython": None})

        sim = Simulatable.Job._from_data(data={})
        # Shoud not throw error with or without IPython
        sim._process_report_figure("image", mimetype="image/png", fig_data=b"")

    def test_process_report_figure_with_invalid_mimetype(self) -> None:
        sim = Simulatable.Job._from_data(data={})
        with pytest.raises(NotImplementedError, match="Unknown mimetype"):
            sim._process_report_figure("image", mimetype="text/plain", fig_data=b"")

    def test_get_report_with_incomplete_report_status(self) -> None:
        sim = Simulatable.Job._from_data(data={})
        assert sim._get_report(report_result={"status": "RUNNING"}) is None

    def test_report_dashboard_with_report_not_present_in_sim_reports(self) -> None:
        sim = Simulatable.Job._from_data(
            data={"tabInfo": [{"data": [{"name": "300"}]}], "simFigures": [{"name": "301", "reportOutputId": None}]}
        )
        assert sim.report_dashboard is None

    def test_parse_single_result_display_with_invalid_job_result(self) -> None:
        sim = Simulatable.Job._from_data(data={})
        with pytest.raises(NotImplementedError, match="Expected job result to be either `code` or `attachment`"):
            sim._parse_single_result_display(display={"invalid": {}}, entity_label="de_101")

    def test_get_object_by_colname_undefined(self) -> None:
        class CustomObject(Simulatable):
            _LIST_URL = "/api/v1/custom_object"

            class Job(Simulatable.Job):
                _object_class = staticmethod(lambda: CustomObject)

        sim = CustomObject.Job._from_data(data={})
        with pytest.raises(NotImplementedError, match="Objects are not accessible for CustomObject using column names"):
            sim.get_registered_object_by_colname("output__rule__2_1_2")

    def test_get_default_simulation(self, responses: responses.RequestsMock, mocker: pytest_mock.MockerFixture) -> None:
        class CustomObject(ApiBase, Simulatable):
            _LIST_URL = "/api/v1/custom_object"
            _exposed_properties = {"id"}

        responses.add(
            responses.GET, utils.ujoin(api_url(CustomObject._LIST_URL), "101/simulation"), json={"result": {"id": 5}}
        )
        constructor_mocked = mocker.patch.object(CustomObject.Job, "__init__", return_value=None)
        public_object = CustomObject._from_data(data={"id": 101})
        public_object.default_simulation  # noqa: B018 -- Call property

        constructor_mocked.assert_called_once_with(entity=public_object, id=5)

    def test_get_default_simulation_with_no_result(
        self, responses: responses.RequestsMock, mocker: pytest_mock.MockerFixture
    ) -> None:
        class CustomObject(ApiBase, Simulatable):
            _LIST_URL = "/api/v1/custom_object"
            _exposed_properties = {"id"}

        responses.add(
            responses.GET, utils.ujoin(api_url(CustomObject._LIST_URL), "101/simulation"), json={"result": {}}
        )
        assert CustomObject._from_data(data={"id": 101}).default_simulation is None
