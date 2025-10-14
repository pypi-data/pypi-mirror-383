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
from genguardx._internal.resources import GlobalFunction
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import Objects, URLS
from genguardx._internal.util.lang_utils import cast_value, parse_user_literal


if t.TYPE_CHECKING:
    import io

    from genguardx._internal.models import Model
    from genguardx._internal.rags import Rag
    from genguardx._internal.util import utils


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


class Prompt(
    ApiBase, Auditable, WithNotes, Workflowable, Searchable, Shareable, WithFields, Simulatable, WithPythonCode
):
    """
    Represents an Prompt that is registered.
    :param name:   The name of the Prompt to fetch.
    :param version: The version of the Prompt to fetch. If not provided, the latest approved version is used.
    :param id:      The ID of the Prompt to fetch. If provided, name and version are not used.
    Example:
        >>> prompt_1 = Prompt('prompt_1')
        >>> prompt_1.name
        'prompt_1'
        >>> prompt_1.version
        1
    The following properties of the Prompt can be accessed:
    - id: integer
        The ID that is unique to every Prompt. (and is different for every version of the Prompt too.)
    - version: integer
        The version of this Prompt.
    - name: string
        The name of the Prompt as registered.
    - description: string
        The description registered for the Prompt.
    - definition: string
        The definition registered for the Prompt.
    - note: string
        The note registered for the Prompt.
    - created_by: string
        The username of the user that created the Prompt.
    - created_date: datetime
        The date that this Prompt was created.
    - group: string
        The group that this Prompt belongs to.
    - current_status: string
        The current workflow status of the Prompt.
    - approval_statuses: list of ApprovalStatus objects
        The list of approval statuses for this Prompt.
    - approval_histories: list of ApprovalHistory objects
        The list of approval histories for this Prompt.
    """

    _object_type = Objects.PROMPT.value
    _LIST_URL = URLS.PROMPT_PATH.value
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
        _object_class = staticmethod(lambda: Prompt)

    @property
    def definition(self) -> CustomModelDefinition | None:
        if not self._data.get("definition"):
            return None
        file = None
        return CustomModelDefinition(
            file,
            self._data["definition"].get("initLogic"),
            self._data["definition"].get("runLogic"),
        )

    @property
    def template(self) -> str | None:
        if not self._data.get("definition"):
            return None
        return self._data["definition"].get("initLogic")

    @property
    def scoring_logic(self) -> str | None:
        if not self._data.get("definition"):
            return None
        return self._data["definition"].get("runLogic")

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
    def input_features(self) -> list[utils.FeatureBasedObjects]:
        return [GlobalFunction(id=i) for i in self._data["featureVersionIds"]]

    @property
    def input_prompts(self) -> list[Prompt]:
        return [Prompt(id=id_) for id_ in self._data["promptVersionIds"]]

    @property
    def input_models(self) -> list[Model]:
        from genguardx._internal.models import Model

        return [Model(id=id_) for id_ in self._data["foundationModelVersionIds"]]

    @property
    def input_rags(self) -> list[Rag]:
        from genguardx._internal.rags import Rag

        return [Rag(id=id_) for id_ in self._data["ragVersionIds"]]

    @classmethod
    def declare(
        cls,
        *,
        name: str | None = None,  # If not provided, use alias (function name)
        group: str | None = None,  # Optional value
        task_type: t.Literal[
            "Classification",
            "Question Answering",
            "Information Extraction",
            "Summarization",
            "Code Generation",
            "Transformation",
            "Generation",
            "Others",
        ]
        | None = None,
        prompt_type: t.Literal["System Instruction", "User Prompt", "Others"] | None = None,
        prompt_elements: t.Sequence[
            t.Literal[
                "Persona + Goal",
                "Tone",
                "Task",
                "Constraints",
                "Context",
                "Examples",
                "Reasoning Steps",
                "Output Format",
                "Recap",
            ]
        ] = (),
    ) -> t.Callable:
        def inner(func: t.Callable) -> t.Callable:
            func._corridor_metadata = {
                "cls": cls,
                "name": name,
                "group": group,
                "task_type": task_type,
                "prompt_type": prompt_type,
                "prompt_elements": prompt_elements,
            }
            return func

        return inner

    def __str__(self) -> str:
        return f'<{type(self).__name__} name="{self.name}", version={self.version}>'
