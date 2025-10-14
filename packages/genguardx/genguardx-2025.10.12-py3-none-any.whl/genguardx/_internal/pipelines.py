from __future__ import annotations

import dataclasses
import typing as t

from genguardx._internal.mixins.auditable import Auditable
from genguardx._internal.mixins.searchable import Searchable
from genguardx._internal.mixins.shareable import Shareable
from genguardx._internal.mixins.simulatable import Simulatable
from genguardx._internal.mixins.with_fields import WithFields
from genguardx._internal.mixins.with_notes import WithNotes
from genguardx._internal.mixins.with_python_code import WithPythonCode
from genguardx._internal.mixins.workflowable import Workflowable
from genguardx._internal.models import Model
from genguardx._internal.prompts import Prompt
from genguardx._internal.rags import Rag
from genguardx._internal.resources import GlobalFunction
from genguardx._internal.util import utils
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import Objects, URLS
from genguardx._internal.util.lang_utils import cast_value, parse_user_literal


if t.TYPE_CHECKING:
    import io

    from genguardx._internal.util.utils import FeatureBasedObjects


@dataclasses.dataclass(frozen=True)
class InputArgument:
    alias: str
    type: str
    is_mandatory: bool
    default_value: t.Any


@dataclasses.dataclass(frozen=True)
class CustomModelDefinition:
    model_file: io.BytesIO
    initialization_logic: str
    scoring_logic: str


PIPELINE_TYPE_DISPLAY_NAMES = {
    "FreeForm": "Custom Return Type",
    "Chat": "Chat based - OpenAI Spec",
}


class Pipeline(
    ApiBase, Auditable, WithNotes, Workflowable, Simulatable, Searchable, Shareable, WithFields, WithPythonCode
):
    """
    Represents an Pipeline that is registered.
    :param name:    The name of the Pipeline to fetch.
    :param version: The version of the Pipeline to fetch. If not provided, the latest approved
                    version is used.
    :param id:      The ID of the Pipeline to fetch. If provided, name and version are not used.
    Example:
        >>> pipeline_1 = Pipeline('pipeline_1')
        >>> pipeline_1.name
        'pipeline_1'
        >>> pipeline_1.version
        1
    The following properties of the Pipeline can be accessed:
    - id: integer
        The ID that is unique to every Pipeline.
    - version: integer
        The version of this Pipeline.
    - name: string
        The name of the Pipeline as registered.
    - pipeline_type: string
        The type of the pipeline: Free Form or Chat Based
    - description: string
        The description registered for the Pipeline.
    - definition: string
        The definition registered for the Pipeline.
    - note: string
        The note registered for the Pipeline.
    - interaction_type: Any
        The data type for interaction for chat based pipeline.
    - context type: Any
        The data type for context for chat based pipeline.
    - created_by: string
        The username of the user that created the Pipeline.
    - created_date: datetime
        The date that this Pipeline was created.
    - group: string
        The group that this Pipeline belongs to.
    - current_status: string
        The current workflow status of the Pipeline.
    - approval_statuses: list of ApprovalStatus objects
        The list of approval statuses for this Pipeline.
    - approval_histories: list of ApprovalHistory objects
        The list of approval histories for this Pipeline.
    """

    _object_type = Objects.PIPELINE.value
    _LIST_URL = URLS.PIPELINE_PATH.value

    _available_filter_names = {"status", "alias", "name", "type", "contains", "group"}

    _exposed_properties = {
        "id",
        "name",
        "alias",
        "version",
        "description",
        "note",
        "group",
        "current_status",
        "type",
    }

    def __init__(
        self, alias: str | None = None, name: str | None = None, version: int | None = None, id: int | None = None
    ) -> None:
        filters: dict[str, t.Any] = {}
        if id is not None:
            filters["ids"] = id
        if alias is not None:
            filters["alias"] = alias
        if name is not None:
            filters["name"] = name
        if version is not None:
            filters["version"] = version
        elif id is None:  # If ID is none, we need to get the "current" version
            filters["singleVersionOnly"] = True
        self._data = self._get_data(one=True, **filters)
        self._set_custom_fields()

    class Job(Simulatable.Job):
        _object_class = staticmethod(lambda: Pipeline)

    @property
    def interaction_type(self) -> str | None:
        return self._data["interactionType"]

    @property
    def context_type(self) -> str | None:
        return self._data["contextType"]

    @property
    def definition(self) -> CustomModelDefinition | None:
        if not self._data.get("definition"):
            return None
        file = None
        if (
            "file" in self._data["definition"]
            and self._data["definition"]["file"] is not None
            and "id" in self._data["definition"]["file"]
        ):
            file = utils.get_model_definition("custom", self._data["definition"]["file"]["id"])
        return CustomModelDefinition(
            file,
            self._data["definition"].get("initLogic"),
            self._data["definition"].get("runLogic"),
        )

    @property
    def pipeline_type(self) -> str:
        return PIPELINE_TYPE_DISPLAY_NAMES.get(self._data["pipelineType"])

    @property
    def arguments(self) -> InputArgument:
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
    def permissible_purpose(self) -> list[str]:
        return self._data["permissibleTags"]

    @property
    def input_features(self) -> list[FeatureBasedObjects]:
        return [GlobalFunction(id=i) for i in self._data["featureVersionIds"]]

    @property
    def input_prompts(self) -> list[Prompt]:
        return [Prompt(id=id_) for id_ in self._data["promptVersionIds"]]

    @property
    def input_models(self) -> list[Model]:
        return [Model(id=id_) for id_ in self._data["foundationModelVersionIds"]]

    @property
    def input_rags(self) -> list[Rag]:
        return [Rag(id=id_) for id_ in self._data["ragVersionIds"]]

    @property
    def input_pipelines(self) -> list[Pipeline]:
        return [Pipeline(id=id_) for id_ in self._data["pipelineVersionIds"]]

    @classmethod
    def declare(
        cls,
        *,
        name: str | None = None,  # If not provided, use alias (function name)
        group: str | None = None,  # Optional value
        usecase_type: t.Literal["Question Answering", "Summarization", "Translation"] | None = None,
        task_type: t.Literal[
            "Classification",
            "Templated Responses",
            "Generative Responses",
            "Summarization",
            "Others",
        ]
        | None = None,
        impact: t.Literal["External Facing", "Internal - with external implications", "Internal Only"] | None = None,
        data_usage: t.Sequence[
            t.Literal["No Additional Data", "General Public Data", "Internal Policies/Data", "Customer Specific Data"]
        ] = (),
        pipeline_type: t.Literal[
            "Custom Return Type",
            "Chat based - OpenAI Spec",
        ] = "Chat based - OpenAI Spec",  # Assume OpenAI chat by default
        provider: str | None = None,  # If provided, we know the pipeline is an External Agent
    ) -> t.Callable:
        def inner(func: t.Callable) -> t.Callable:
            func._corridor_metadata = {
                "cls": cls,
                "name": name,
                "group": group,
                "usecase_type": usecase_type,
                "task_type": task_type,
                "impact": impact,
                "data_usage": data_usage,
                "pipeline_type": pipeline_type,
                "provider": provider,
            }
            return func

        return inner

    def __str__(self) -> str:
        return f'<{type(self).__name__} name="{self.name}", version={self.version}>'
