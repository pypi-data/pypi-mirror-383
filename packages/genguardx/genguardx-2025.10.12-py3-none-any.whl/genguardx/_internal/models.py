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
from genguardx._internal.prompts import Prompt
from genguardx._internal.resources import GlobalFunction
from genguardx._internal.util import utils
from genguardx._internal.util.base_api import ApiBase
from genguardx._internal.util.constants import Objects, URLS
from genguardx._internal.util.lang_utils import cast_value, parse_user_literal


if t.TYPE_CHECKING:
    import io

    from genguardx._internal.rags import Rag
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


class Model(
    ApiBase, Auditable, WithNotes, Workflowable, Simulatable, Searchable, Shareable, WithFields, WithPythonCode
):
    """
    Represents an Foundation Model that is registered.
    :param name:    The name of the Foundation Model to fetch.
    :param version: The version of the Foundation Model to fetch. If not provided, the latest approved
                    version is used.
    :param id:      The ID of the Foundation Model to fetch. If provided, name and version are not used.
    Example:
        >>> foundation_model_1 = Foundation Model('foundation_model_1')
        >>> foundation_model_1.name
        'foundation_model_1'
        >>> foundation_model_1.version
        1
    The following properties of the Foundation Model can be accessed:
    - id: integer
        The ID that is unique to every Foundation Model.
    - version: integer
        The version of this Foundation Model.
    - name: string
        The name of the Foundation Model as registered.
    - description: string
        The description registered for the Foundation Model.
    - definition: string
        The definition registered for the Foundation Model.
    - note: string
        The note registered for the Foundation Model.
    - created_by: string
        The username of the user that created the Foundation Model.
    - created_date: datetime
        The date that this Foundation Model was created.
    - group: string
        The group that this Foundation Model belongs to.
    - current_status: string
        The current workflow status of the Foundation Model.
    - approval_statuses: list of ApprovalStatus objects
        The list of approval statuses for this Foundation Model.
    - approval_histories: list of ApprovalHistory objects
        The list of approval histories for this Foundation Model.
    """

    _object_type = Objects.FOUNDATION_MODEL.value
    _LIST_URL = URLS.FOUNDATION_MODEL_PATH.value
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
        _object_class = staticmethod(lambda: Model)

    @property
    def provider(self) -> str:
        return self._data["provider"]

    @property
    def model(self) -> str:
        return self._data["model"]

    @property
    def definition(self) -> CustomModelDefinition:
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
        from genguardx._internal.rags import Rag

        return [Rag(id=id_) for id_ in self._data["ragVersionIds"]]

    @property
    def permissible_purpose(self) -> list[str]:
        return self._data["permissibleTags"]

    @classmethod
    def declare(
        cls,
        *,
        name: str | None = None,  # If not provided, use alias (function name)
        group: str | None = None,  # Optional value
        ownership_type: t.Literal["Open Source", "Proprietary"] | None = None,
        model_type: t.Literal["LLM", "Text Embedding", "Guardrail", "Judge Model", "Others"] | None = None,
        provider: str | None = None,  # If provided, we know the model is API Based
        model: str | None = None,  # If provided, we know the model is API Based
    ) -> t.Callable:
        def inner(func: t.Callable) -> t.Callable:
            func._corridor_metadata = {
                "cls": cls,
                "name": name,
                "group": group,
                "ownership_type": ownership_type,
                "model_type": model_type,
                "provider": provider,
                "model": model,
            }
            return func

        return inner

    def __str__(self) -> str:
        return f'<{type(self).__name__} name="{self.name}", version={self.version}>'
