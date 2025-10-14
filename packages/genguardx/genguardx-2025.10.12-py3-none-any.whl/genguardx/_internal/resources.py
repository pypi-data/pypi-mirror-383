from __future__ import annotations

import dataclasses
import typing as t
import warnings

from genguardx._internal.mixins.auditable import Auditable
from genguardx._internal.mixins.searchable import Searchable
from genguardx._internal.mixins.shareable import Shareable
from genguardx._internal.mixins.simulatable import Simulatable
from genguardx._internal.mixins.with_fields import WithFields
from genguardx._internal.mixins.with_notes import WithNotes
from genguardx._internal.mixins.with_python_code import WithPythonCode
from genguardx._internal.mixins.workflowable import Workflowable
from genguardx._internal.util import utils
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import Objects, ReportOutputType, ReportParameterType, SIMULATABLE_OBJECTS, URLS
from genguardx._internal.util.lang_utils import cast_value, parse_user_literal


if t.TYPE_CHECKING:
    from genguardx._internal.data_tables import DataTable
    from genguardx._internal.models import Model
    from genguardx._internal.pipelines import Pipeline
    from genguardx._internal.prompts import Prompt
    from genguardx._internal.rags import Rag


@dataclasses.dataclass(frozen=True)
class InputArgument:
    alias: str
    type: str
    is_mandatory: bool
    default_value: t.Any


@dataclasses.dataclass(frozen=True)
class Tab:
    name: str
    report_outputs: list[TabReportOutput]


@dataclasses.dataclass(frozen=True)
class TabReportOutput:
    report_output: ReportOutput
    width: str
    height: str


class GlobalFunction(ApiBase, Auditable, Workflowable, Searchable, WithNotes, Shareable, WithFields, WithPythonCode):
    """
    Represents a GlobalFunction that is registered.

    :param alias:   The alias of the GlobalFunction to fetch.
    :param name:    The name of the GlobalFunction to fetch.
    :param id:      The ID of the GlobalFunction to fetch.

    The following properties of the GlobalFunction can be accessed:
     - name: string
        The name of the GlobalFunction as registered.
     - alias: string
        The alias of the GlobalFunction as registered. This is the alias used to refer to the GlobalFunction
        when creating definitions
     - type: string
        The return type of the GlobalFunction - Numerical, String, etc.
     - description: string
        The description registered for the GlobalFunction.
     - version: integer
        The version of this GlobalFunction.
     - current_status: string
        The current workflow status of the GlobalFunction.
     - definition: string or None
        The definition for the GlobalFunction
     - note: string
        Any notes added during registration.
     - group: string
        The group that this Function belongs to.
     - id: integer
        The ID that is unique to every GlobalFunction. (and is different for every version of the GlobalFunction too.)
     - created_by: string
        The username of the user that created the GlobalFunction.
     - created_date: datetime
        The date that this GlobalFunction was created.
     - last_modified_by: string
        The username of the GlobalFunction that last modified the item.
     - last_modified_date: datetime
        The date when the GlobalFunction was last modified.
     - arguments: list
        The list of dataclasses containing alias, type and default_value for arguments of Global Function
     - inputs: list
        The list of input Global Function(s)/RTP(s) to the Global Function
     - approval_histories: list of ApprovalHistory objects
        The list of approval histories for this GlobalFunction.
     - approval_workflow: ApprovalWorkflow object
        The ApprovalWorkflow associated with this GlobalFunction.
     - approval_statuses: list of ApprovalStatus objects
        The list of approval statuses for this GlobalFunction.


    The following function can be accessed:
     - all(): list
        Returns a list of filtered GlobalFunction objects
        Valid filters: name, contains, alias, status, type
    """

    _object_type = Objects.GLOBAL_FUNCTION.value
    _LIST_URL = URLS.GLOBAL_FUNCTION_PATH.value
    _exposed_properties = {
        "id",
        "description",
        "version",
        "current_status",
        "note",
        "group",
    }
    _available_filter_names = {"status", "alias", "name", "type", "contains", "group"}

    class Job(Simulatable.Job):
        _object_class = staticmethod(lambda: GlobalFunction)

    @utils.classproperty
    def global_functions(cls) -> list[str]:
        """
        Fetch all GlobalFunctions that are registered.
        """
        warnings.warn(
            "`.global_functions` is deprecated and will be removed in the next version. Please use `.all()` instead",
            DeprecationWarning,
            stacklevel=1,
        )
        return [i.alias for i in cls.all()]

    def __init__(
        self,
        alias: str | None = None,
        version: int | None = None,
        id: int | None = None,
    ) -> None:
        filters: dict[str, t.Any] = {}
        if id is not None:
            filters["ids"] = id
        if alias is not None:
            filters["alias"] = alias
        if version is not None:
            filters["version"] = version
        elif id is None:  # If ID is none, we need to get the "current" version
            filters["singleVersionOnly"] = True
        self._data = self._get_data(one=True, **filters)
        self._set_custom_fields()

    @property
    def type(self) -> str:
        """The return type of the GlobalFunction - Numerical, String, etc."""
        return self._data["type"]

    @property
    def definition(self) -> str | None:
        if self._data.get("definition"):
            return self._data["definition"].get("runLogic")
        return None

    @property
    def alias(self) -> str:
        return self._data["alias"]

    @property
    def name(self) -> None:
        return self._data["name"]

    @property
    def parameters(self) -> list[str]:
        warnings.warn(
            "`.parameters` is deprecated and will be removed in the next version. Please use `.arguments()` instead",
            DeprecationWarning,
            stacklevel=1,
        )
        return [arg.alias for arg in self.arguments]

    @property
    def arguments(self) -> list[InputArgument]:
        """The list of namedtuples containing alias, type and default_value for arguments of Global Function."""
        return [
            InputArgument(
                inp["alias"],
                inp["inputType"],
                inp["isMandatory"],
                cast_value(
                    parse_user_literal(
                        inp["defaultValue"],
                        inp["inputType"],
                        # Datetime-as-string is fine as cast_value() will cast it to a datetime.datetime
                        datetime_check=False,
                    ),
                    inp["inputType"],
                )
                if inp["isMandatory"] is False
                else None,
            )
            for inp in self._data["functionInputs"]
        ]

    @property
    def inputs(self) -> list[GlobalFunction]:
        return [GlobalFunction(id=i) for i in self._data["featureVersionIds"]]

    def __str__(self) -> str:
        return f'<{type(self).__name__} alias="{self.alias}", version={self.version}>'

    @classmethod
    def declare(
        cls,
        *,
        name: str | None = None,  # If not provided, use alias (function name)
        group: str | None = None,  # Optional value
    ) -> t.Callable:
        def inner(func: t.Callable) -> t.Callable:
            func._corridor_metadata = {
                "cls": cls,
                "name": name,
                "group": group,
            }
            return func

        return inner


class Report(ApiBase, Auditable, Searchable, WithNotes, Workflowable, WithFields, Shareable):
    """
    Represents a Report that is registered.

    :param name:   The name of the Report to fetch.
    :param version: The version of the Report to fetch. If not provided, the latest approved version is used.
    :param id:      The ID of the Report to fetch. If provided, name and version are not used.

    Example:
        >>> report_1 = Report('report_1')
        >>> report_1.name
        'Report'
        >>> report_1.version
        1

    The following properties of the Report can be accessed:
    - id: integer
        The ID that is unique to every Report. (and is different for every version of the Report too.)
    - version: integer
        The version of this Report.
    - name: string
        The name of the Report as registered.
    - description: string
        The description registered for the Report.
    - object_types : list
        The list of objects for which the report is designed to run.
    - created_by: string
        The username of the user that created the Report.
    - created_date: datetime
        The date that this Report was created.
    - attached_files : List
        The list of attachments associated with the Report.
    - approval_statuses: list of ApprovalStatus objects
        The list of approval statuses for this Report.
    - approval_histories: list of ApprovalHistory objects
        The list of approval histories for this Report.
    - outputs: list of ReportOutput objects
        The list of report outputs for this Report.
    - group: string
        The group that this Report belongs to.
    - parameters: list of ReportParameters objects
        The list of report input parameters for the report.
    - data_logic_examples: list of DataLogicExample objects
        The list of data logic examples for this Report.
    - current_status: string
        The current workflow status of the Report.
    """

    _object_type = Objects.REPORT.value
    _LIST_URL = URLS.REPORT_PATH.value

    _exposed_properties = {
        "id",
        "name",
        "version",
        "description",
        "note",
        "group",
        "current_status",
    }
    _available_filter_names = {
        "status",
        "keyword",
        "permissible_purpose",
        "name",
        "contains",
        "group",
        "object_types",
    }
    # Object_type is mapped to object_types API parameter while filtering Reports
    FILTER_API_PARAMETER_MAPPING = {
        "status": "statuses",
        "permissible_purpose": "permissibleTags",
        "group": "group",
        "contains": "keyword",
        "object_types": "objectTypes",
    }

    class Job(Simulatable.Job):
        _object_class = staticmethod(lambda: Report)

    @utils.classproperty
    def _possible_filter_values__object_type(cls) -> set[str]:
        return {Objects.display_name(obj) for obj in SIMULATABLE_OBJECTS}

    def __init__(self, name: str | None = None, version: int | None = None, id: int | None = None) -> None:
        filters: dict[str, t.Any] = {}
        if id is not None:
            filters["ids"] = id
        if name is not None:
            filters["name"] = name
        if version is not None:
            filters["version"] = version
        elif id is None:  # If ID is none, we need to get the "current" version
            filters["singleVersionOnly"] = True
        self._data = self._get_data(one=True, **filters)
        self._set_custom_fields()

    @property
    def definition(self) -> str | None:
        if self._data.get("definition"):
            return self._data["definition"].get("runLogic")
        return None

    @property
    def object_types(self) -> list[str]:
        return [Objects.display_name(i["objectType"]) for i in self._data["objectTypes"]]

    @property
    def inputs(self) -> list[GlobalFunction]:
        return [GlobalFunction(id=i) for i in self._data["featureVersionIds"]]

    @property
    def parameters(self) -> list[ReportParameter]:
        return [ReportParameter(self, param) for param in self._data["parameters"]]

    @property
    def outputs(self) -> list[ReportOutput]:
        return [ReportOutput(self, output) for output in self._data["outputs"]]

    @property
    def data_logic_examples(self) -> list[DataLogicExample]:
        return [DataLogicExample(self, example) for example in self._data.get("dataLogicExamples", [])]

    def __str__(self) -> str:
        return f'<{type(self).__name__} name="{self.name}", version={self.version}>'

    @classmethod
    def declare(
        cls,
        *,
        object_types: list[str],
        name: str | None = None,  # If not provided, use alias (function name)
        group: str | None = None,  # Optional value
        risk_type: t.Literal["Accuracy", "Stability", "Bias", "Vulnerability", "Toxicity", "Others"] | None = None,
        task_type: t.Literal[
            "Classification",
            "Templated Responses",
            "Generative Responses",
            "Summarization",
            "Others",
        ]
        | None = None,
        risk_domain: t.Literal["Model Risk Management", "Fair Lending", "Technology", "Infosec", "Others"]
        | None = None,
        evaluation_methodology: t.Literal["LLM-as-a-Judge", "Rule-based", "NLP / ML Algorithms", "Others"]
        | None = None,
        report_methodology: str | None = None,
        parameters: list[dict] = (),
    ) -> t.Callable:
        def inner(func: t.Callable) -> t.Callable:
            func._corridor_metadata = {
                "cls": cls,
                "name": name,
                "object_types": object_types,
                "group": group,
                "risk_type": risk_type,
                "task_type": task_type,
                "risk_domain": risk_domain,
                "evaluation_methodology": evaluation_methodology,
                "report_methodology": report_methodology,
                "parameters": parameters,
            }
            return func

        return inner


class ReportOutput(ApiBase, Auditable):
    """
    Represents a Report Output that is registered.

    Example:
        >>> report_out_1 = Report('report').outputs[0]
        >>> report_out_1.name
        'Report Output 1'

    The following properties of the Report Output can be accessed:
     - id: integer
        The ID that is unique to every Report Output.
     - name: string
        The name of the Report Output as registered.
     - definition: string
        The definition for report output.
     - type: string
        The type of report output.
     - inputs:List
        The list of input Features to the Report Output.
     - created_by: string
        The username of the user that created the Report Output.
     - created_date: datetime
        The date that this Report Output was created.
    """

    _exposed_properties = {"id", "name"}

    def __init__(self, report: Report, data: dict[str, t.Any]) -> None:
        self._report = report
        self._data = data

    @property
    def type(self) -> str:
        return ReportOutputType.display_name(self._data["type"])

    @property
    def definition(self) -> str | None:
        if self._data.get("definition"):
            return self._data["definition"].get("runLogic")
        return None

    @property
    def inputs(self) -> list[GlobalFunction]:
        return [GlobalFunction(id=i) for i in self._data["featureVersionIds"]]

    @property
    def additional_figures(self) -> list[AdditionalReportFigure]:
        return [AdditionalReportFigure(self, figure) for figure in self._data.get("additionalFigures", [])]

    @property
    def report(self) -> Report:
        return self._report

    def __str__(self) -> str:
        return f'<ReportOutput report="{self.report.name}" name="{self.name}">'

    @classmethod
    def declare(
        cls,
        *,
        report: str,
        name: str | None = None,  # If not provided, use alias (function name)
        width: t.Literal["33%", "50%", "100%"] = "100%",
        height: str | None = None,
        evaluation_methodology: t.Literal["LLM-as-a-Judge", "Rule-based", "NLP / ML Algorithms", "Others"],
    ) -> t.Callable:
        def inner(func: t.Callable) -> t.Callable:
            func._corridor_metadata = {
                "cls": cls,
                "name": name,
                "report": report,
                "width": width,
                "height": height,
                "evaluation_methodology": evaluation_methodology,
            }
            return func

        return inner


class DataLogicExample(ApiBase, Auditable):
    """
    Represents a Data Logic Example for a Report that is registered.

    The following properties of the Data Logic Example can be accessed:
     - id: integer
        The ID that is unique to every Data Logic Example.
     - name: string
        The name of the Data Logic Example as registered.
     - description: string
        The description for the Data Logic Example.
     - definition: string or None
        The definition for the Data Logic Example.
     - sort_order: integer
        The sort order of this Data Logic Example.
     - input_data: dict or None
        The input data configuration for this Data Logic Example.
     - input_global_functions: list
        The list of input Global Function(s) to the Data Logic Example.
     - input_tables: list
        The list of table associated with this Data Logic Example.
     - input_prompts: list
        The list of prompts associated with this Data Logic Example.
     - input_models: list
        The list of models associated with this Data Logic Example.
     - input_rags: list
        The list of RAGs associated with this Data Logic Example.
     - created_by: string
        The username of the user that created the Data Logic Example.
     - created_date: datetime
        The date that this Data Logic Example was created.
    """

    _exposed_properties = {
        "id",
        "name",
        "description",
        "sort_order",
    }

    def __init__(self, report: Report, data: dict[str, t.Any]) -> None:
        self._report = report
        self._data = data

    @property
    def definition(self) -> str | None:
        if self._data.get("definition"):
            return self._data["definition"].get("runLogic")
        return None

    @property
    def input_global_functions(self) -> list[GlobalFunction]:
        return [GlobalFunction(id=i) for i in self._data.get("featureVersionIds", [])]

    @property
    def input_tables(self) -> list[DataTable]:
        from genguardx._internal.data_tables import DataTable

        return [DataTable(id=i) for i in self._data.get("tableIds", [])]

    @property
    def input_prompts(self) -> list[Prompt]:
        from genguardx._internal.prompts import Prompt

        return [Prompt(id=i) for i in self._data.get("promptVersionIds", [])]

    @property
    def input_models(self) -> list[Model]:
        from genguardx._internal.models import Model

        return [Model(id=i) for i in self._data.get("foundationModelVersionIds", [])]

    @property
    def input_rags(self) -> list[Rag]:
        from genguardx._internal.rags import Rag

        return [Rag(id=i) for i in self._data.get("ragVersionIds", [])]

    @property
    def report(self) -> Report:
        return self._report

    def __str__(self) -> str:
        return f'<DataLogicExample report="{self.report.name}" name="{self.name}">'

    @classmethod
    def declare(
        cls,
        *,
        report: str,
        name: str,
        description: str | None = None,
    ) -> t.Callable:
        def inner(func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:
            func._corridor_metadata = {
                "cls": cls,
                "name": name,
                "report": report,
                "description": description,
            }
            return func

        return inner


class AdditionalReportFigure(ApiBase, Auditable):
    """
    Represents an Additional Report Figure for a Report Output that is registered.

    The following properties of the Additional Report Figure can be accessed:
     - id: integer
        The ID that is unique to every Additional Report Figure.
     - name: string
        The name of the Additional Report Figure as registered.
     - icon: string or None
        The icon for the Additional Report Figure.
     - definition: string or None
        The definition for the Additional Report Figure.
     - sort_order: integer
        The sort order of this Additional Report Figure.
     - input_global_functions: list
        The list of input Global Function(s) to the Additional Report Figure.
     - input_prompts: list
        The list of prompts associated with this Additional Report Figure.
     - input_models: list
        The list of models associated with this Additional Report Figure.
     - input_rags: list
        The list of RAGs associated with this Additional Report Figure.
     - input_pipelines: list
        The list of pipelines associated with this Additional Report Figure.
     - created_by: string
        The username of the user that created the Additional Report Figure.
     - created_date: datetime
        The date that this Additional Report Figure was created.
    """

    _exposed_properties = {
        "id",
        "name",
        "icon",
        "sort_order",
    }

    def __init__(self, report_output: ReportOutput, data: dict[str, t.Any]) -> None:
        self._report_output = report_output
        self._data = data

    @property
    def definition(self) -> str | None:
        if self._data.get("definition"):
            return self._data["definition"].get("runLogic")
        return None

    @property
    def input_global_functions(self) -> list[GlobalFunction]:
        return [GlobalFunction(id=i) for i in self._data.get("featureVersionIds", [])]

    @property
    def input_prompts(self) -> list[Prompt]:
        from genguardx._internal.prompts import Prompt

        return [Prompt(id=i) for i in self._data.get("promptVersionIds", [])]

    @property
    def input_models(self) -> list[Model]:
        from genguardx._internal.models import Model

        return [Model(id=i) for i in self._data.get("foundationModelVersionIds", [])]

    @property
    def input_rags(self) -> list[Rag]:
        from genguardx._internal.rags import Rag

        return [Rag(id=i) for i in self._data.get("ragVersionIds", [])]

    @property
    def input_pipelines(self) -> list[Pipeline]:
        from genguardx._internal.pipelines import Pipeline

        return [Pipeline(id=i) for i in self._data.get("pipelineVersionIds", [])]

    @property
    def report_output(self) -> ReportOutput:
        return self._report_output

    def __str__(self) -> str:
        return f'<AdditionalReportFigure report_output="{self.report_output.name}" name="{self.name}">'

    @classmethod
    def declare(
        cls,
        *,
        report_output: str,
        name: str | None = None,  # If not provided, use alias (function name)
        icon: str | None = None,
    ) -> t.Callable:
        def inner(func: t.Callable) -> t.Callable:
            func._corridor_metadata = {
                "cls": cls,
                "name": name,
                "report_output": report_output,
                "icon": icon,
            }
            return func

        return inner


class ReportParameter(ApiBase, Auditable):
    """
    Represents a Report Parameter for a Report that is registered.

    The following properties of the Report Parameter can be accessed:
     - id: integer
        The ID that is unique to every Report Parameter.
     - alias: string
        The alias of the Report Parameter as registered.
     - name: string
        The name of the Report Parameter as registered.
     - type: string
        The type of Report Parameter.
     - created_by: string
        The username of the user that created the Report Parameter.
     - created_date: datetime
        The date that this Report Parameter was created.
     - is_mandatory: bool
        The boolian represeting if the parameter is mandatory for the Report.
     - description: string
        The description for the Report Parameter
    """

    _exposed_properties = {"id", "alias", "name", "description", "is_mandatory"}

    def __init__(self, report: Report, data: dict[str, t.Any]) -> None:
        self._report = report
        self._data = data

    @property
    def type(self) -> str:
        return ReportParameterType.display_name(self._data["type"])

    @property
    def report(self) -> Report:
        return self._report

    def __str__(self) -> str:
        return f'<ReportParameter report="{self.report.name}" name="{self.name}">'
