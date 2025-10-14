from __future__ import annotations

import io
import json
import typing as t
from collections import OrderedDict

import pandas as pd
from plotly import graph_objs as go

from genguardx._internal.mixins.auditable import Auditable
from genguardx._internal.util import utils
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import (
    DataType,
    JobType,
    Objects,
    ReportParameterType,
    URLS,
)
from genguardx._internal.util.lang_utils import parse_user_literal
from genguardx._internal.util.networking import api


try:
    from IPython.display import Image, Markdown

except ImportError:  # pragma: no cover
    # Create a dummy Image class when ipython is not available
    class Image:
        def __init__(self, data: bytes, format: str) -> None:
            self.format = format
            self.data = data

    class Markdown:
        def __init__(self, data: bytes) -> None:
            self.data = data


class Simulatable:
    """
    Represents an item that has simulated jobs.
    """

    class Job(ApiBase, Auditable):
        """
        Represents a job for the item.

        :param entity:    The entity that the Job ran on, can be either entity object or entity id
        :param name:      The name of the Job to fetch.
        :param id:        The id of the Job to fetch.

        The following properties of the Job can be accessed:
        - name: string
            The name of the Job as registered.
        - description: string
            The description that the user has entered to describe the Job.
        - created_by: string
            The username of the user that created the Job.
        - created_date: datetime
            The date that this Job was created.
        - last_modified_by: string
            The username of the user that last modified the Job.
        - last_modified_date: datetime
            The date when the Job was last modified.
        - status: string
            The status if the Job. Possible values SCHEDULED|QUEUED|COMPILING|RUNNING|COMPLETED|FAILED

        # Job type related properties
        - job_type: string
            The type of the job. Possible values: Simulation|Comparison|Validation|Verification
        - current: object
            The object that the job is running for
        - challengers: dictionary of challenger objects
            The challengers user selected when running the job. Example: {'challenger1': object, 'challenger2': object}
        - benchmarks: dictionary of benchmark jobs
            The benchmarks user selected when running the job. Example: {'benchmark1': job, 'benchmark2': job}

        # Config related properties
        - configs: string
            The configs provided when running the Job.

        # Sampling related properties
        - sample_type: string
            The sample type selected when running the job. Possible values: limit|random
        - sample_size: numeric
            The sample size provided when running the Job.
        - date_filter: object
            The date filter object selected when running the Job.
        - date_filter_from_date: datetime
            The start datetime of the date filter provided when running the Job.
        - date_filter_to_date: datetime
            The end datetime of the date filter provided when running the Job.

        # Reused job related properties
        - reused_job_object_type:
            The type of the object used in Existing Job Results
        - reused_job_object:
            The object used in Existing Job Results
        - reused_job:
            The specific job for the selected reused_job_object to run the current job

        # Job result related properties
        - inputs: dictionary
            The input data used for running the job.
        - outputs: dictionary
            The output data for the job.
        - report_dashboard: dictionary
            The dashboard results for the job
            Dictionary format: {'tab1.name': {'report1.name': plotly object, 'report2.name': plotly object}}
        - logs: string
            The logs generated when running the Job.
        - is_old: boolean
            Flag indicates whether the job is old.
        - runtime: timedelta
            The total time used to run the Job.
        """

        _object_class = None
        _exposed_properties = {"id", "name", "description", "configs", "is_old"}

        @utils.classproperty
        def _LIST_URL(cls) -> str:  # noqa: N802
            return utils.ujoin(cls._object_class()._LIST_URL, "simulations")

        def __init__(self, entity: t.Any | None = None, name: str | None = None, id: int | None = None) -> None:  # noqa: ANN401 -- Entity can vary depending on the class which uses the simulatable
            self._current = None
            entity_id = None

            if entity is not None:
                if isinstance(entity, Simulatable):
                    entity_id = entity.id
                    self._current = entity
                elif isinstance(entity, int):
                    entity_id = entity
                else:
                    raise NotImplementedError(
                        f"Expect entity to be either integer or Simulatable, got {type(entity).__name__}"
                    )

            if id is not None:
                self._data = api.response(utils.ujoin(str(self._LIST_URL), str(id)))["result"]
            else:
                filters: dict[str, t.Any] = {}
                if name is not None:
                    filters["name"] = name
                if entity_id is not None:
                    filters["entityId"] = entity_id

                # NOTE: We need to call the Item API separately as it is needed for the jobResults
                item = self._get_data(one=True, **filters)
                self._data = api.response(utils.ujoin(str(self._LIST_URL), item["id"]))["result"]

        @property
        def status(self) -> str:
            return self._data["jobStatus"]

        @property
        def job_type(self) -> str:
            return self._data["executionType"]

        @property
        def sample_size(self) -> int | None:
            sample_info = (self._data["inputData"] or {}).get("sampleInfo", {})
            if sample_info.get("type") == "Sample Size":
                return sample_info.get("numSamples")
            if sample_info.get("type") == "Sample Ratio":
                return "{:.0%}".format(float(sample_info.get("sampleRatio")) / 100.0)
            return None

        @property
        def sample_type(self) -> str:
            if self.sample_size is not None:
                return (self._data["inputData"] or {})["sampleInfo"]["order"]
            return None

        @property
        def current(self) -> t.Any:  # noqa: ANN401 -- Return type depends on the object
            if getattr(self, "_current", None) is None:
                self._current = type(self)._object_class()(id=self._data["entityId"])
            return self._current

        @property
        def challengers(self) -> dict | None:
            if self.job_type == JobType.COMPARISON.value:
                return {
                    assoc_val["label"]: type(self)._object_class()(id=assoc_val["otherEntityId"])
                    for assoc_val in self._data["challengerAssocs"]
                }
            return None

        def _parse_report_parameters(self, value: t.Any, type_: str, object_type: str | None = None) -> t.Any:  # noqa: ANN401 -- value type and return type can vary
            if value in (None, ""):
                return None
            if type_ == ReportParameterType.STRING.value:
                return parse_user_literal(value, DataType.STRING.value)
            if type_ == ReportParameterType.NUMBER.value:
                return parse_user_literal(value, DataType.NUMERICAL.value)
            if type_ == ReportParameterType.DYNAMIC_OBJECT.value:
                assert object_type is not None, (
                    "object_type should be one of Data Table, Foundation Model, Prompt, RAG or "
                    "Global Function. Got: None"
                )
                return Objects.class_mapping()[Objects(object_type)](id=int(value))
            raise TypeError(
                f"Expected report parameters to be of type: "
                f"{' or '.join([t.value for t in ReportParameterType])}. Found {type_}"
            )

        @property
        def parameters(self) -> dict:
            if self._object_class()._object_type == Objects.QUALITY_CHECK.value:
                report_data = self._data["reportData"] or {}
            else:
                report_data = {}
                for data_logic in self._data["dataLogics"] or []:
                    # FIXME: This has to be improved handle multiple dataLogics
                    # Currently if there are multiple datalogics/reports using same parameter alias
                    # the last one will override the previous ones.
                    # We need to handle this case by merging the reportData of all dataLogics
                    # and then parsing the parameters.
                    report_data.update(data_logic["reportData"] or {})
            return {
                k: self._parse_report_parameters(info["value"], info["type"], info.get("objectType", None))
                for k, info in report_data.items()
            }

        def _process_report_figure(self, name: str, mimetype: str, fig_data: bytes) -> Image:
            if mimetype == "application/vnd.plotly.v1+json":
                fig_json = json.loads(fig_data)
                fig_layout = {
                    k: v for k, v in fig_json["layout"].items() if k not in ("pyVersion", "payloadVersion", "jsVersion")
                }
                figure = go.Figure(data=fig_json["data"], layout=fig_layout)
            elif mimetype == "image/png":
                figure = Image(data=fig_data, format="png")
            elif mimetype == "application/vnd.corridor.table.v1+json":
                figure = pd.read_json(io.BytesIO(fig_data), orient="split", convert_axes=False, convert_dates=False)
            elif mimetype == "text/markdown":
                figure = Markdown(self._fig_data.decode("utf-8"))
            else:
                raise NotImplementedError(f"Unknown mimetype {mimetype}")
            return figure

        def _get_report(self, report_result: dict) -> Image | None:
            if report_result["status"] != "COMPLETED":
                return None
            fig_data = api.response(utils.ujoin(URLS.ATTACHMENTS_PATH.value, report_result["attachmentId"]), out="bin")
            return self._process_report_figure(report_result["name"], report_result["attachmentMimetype"], fig_data)

        @property
        def report_dashboard(self) -> dict:
            dashboard = OrderedDict()
            for tab_info in self._data["tabInfo"]:
                tab = OrderedDict()
                for report_name in [report["name"] for report in tab_info["data"]]:
                    result = next(
                        (
                            res
                            for res in self._data["simFigures"]
                            if (
                                res["reportOutputId"] is not None  # ui reports
                                and str(res["reportOutputId"]) == report_name
                            )
                            or res["name"] == report_name  # config reports
                        ),
                        None,
                    )  # pragma: no cover -- coverage is reported incorrectly for generators. Ref: https://github.com/nedbat/coveragepy/issues/475
                    if result is not None:
                        tab[result["name"]] = self._get_report(result)
                if tab:
                    dashboard[tab_info["text"]] = tab

            return dashboard or None

        def __str__(self) -> str:
            return f'<{type(self).__name__} job_type="{self.job_type}" name="{self.name}">'

    @property
    def jobs(self) -> list[str]:
        return [i["name"] for i in self.Job._get_data(entityId=self.id)]

    def get_job(self, name: str) -> Job:
        return self.Job(entity=self, name=name)

    @property
    def default_simulation(self) -> Job | None:
        sim = api.response(utils.ujoin(self._LIST_URL, str(self.id) + "/simulation"))["result"]
        if sim:
            return self.Job(entity=self, id=sim["id"])
        return None
