from __future__ import annotations

import dataclasses
import enum
import re
import typing as t


if t.TYPE_CHECKING:
    import io

    from genguardx._internal.util.base_api import ApiBase


URL_PREFIX = "/api/v1"


class URLS(enum.Enum):
    GLOBAL_FUNCTION_PATH = URL_PREFIX + "/global_functions"
    SCHEDULED_JOB_PATH = URL_PREFIX + "/scheduled_jobs"
    DATA_TABLE_PATH = URL_PREFIX + "/data_tables"
    QUALITY_PROFILE_PATH = URL_PREFIX + "/quality_profiles"
    ATTACHMENTS_PATH = URL_PREFIX + "/attachments"
    USER_PATH = URL_PREFIX + "/users"
    META_PATH = URL_PREFIX + "/meta"
    PERMISSIBLE_PURPOSE_PATH = URL_PREFIX + "/permissible_tags"
    APPROVAL_WORKFLOW_PATH = URL_PREFIX + "/approval_workflows"
    LINEAGE_PATH = URL_PREFIX + "/lineage"
    GROUP_PATH = URL_PREFIX + "/groups"
    REPORT_PATH = URL_PREFIX + "/reports"
    FIELD_PATH = URL_PREFIX + "/fields"
    PLATFORM_SETTING_PATH = URL_PREFIX + "/platform_settings"
    PROMPT_PATH = URL_PREFIX + "/prompts"
    FOUNDATION_MODEL_PATH = URL_PREFIX + "/foundation_models"
    RAG_PATH = URL_PREFIX + "/rags"
    PIPELINE_PATH = URL_PREFIX + "/pipelines"
    INPUTS_PATH = URL_PREFIX + "/inputs"
    MONITORING_PATH = URL_PREFIX + "/monitoring"
    ANNOTATION_QUEUE_PATH = URL_PREFIX + "/annotation_queues"


class WorkflowStatus(enum.Enum):
    DRAFT = "Draft"
    PENDING_APPROVAL = "Pending Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class AuditAction(enum.Enum):
    CREATED = "Created"
    STATUS_CHANGED = "Status Changed"
    CHANGED = "Changed"
    DELETED = "Deleted"
    EDITED = "Edited"


def get_key_values_of_struct_type(struct_type: str) -> dict:
    """
    Given STRUCT type with keys and their value type, convert type to python dictionary
    This function handles the cases where key values can be nested types like Struct[a:Map[x,y]] having
    commas and colon inside them.

    "Struct[key1:val_type1,key2:val_type2]" -> {"key1":"val_type1", "key2":"val_type2"}

    Args:
        struct_type (str): valid STRUCT feature type.

    Returns:
        dict: with keys and their value type.
    """
    result = {}
    current_string = ""
    stack = []

    if re.compile(r"(?i)^Struct\[(.+)\]$").match(struct_type) is None:
        raise AssertionError(f"Invalid struct type '{struct_type}'")

    inner_string = struct_type[len("Struct") :].strip()[1:-1].strip()  # remove 'Struct[' and ']'
    for char in inner_string:
        if char == "[":
            stack.append("[")
        elif char == "]":
            stack.pop()
        elif char == "," and len(stack) == 0:
            key, value = current_string.split(":", 1)
            key, value = key.strip(), value.strip()
            if key in result:
                raise ValueError(f"Duplicate key '{key}' found in struct.")
            result[key] = value
            current_string = ""
            continue
        current_string += char

    if current_string:
        key, value = current_string.split(":", 1)
        key, value = key.strip(), value.strip()
        if key in result:
            raise ValueError(f"Duplicate key '{key}' found in struct.")
        result[key] = value

    return result


class DataType(enum.Enum):
    """
    Holds a list of possible types that we allow.
    If a type is a complex type (like Array<Int>)
    """

    NUMERICAL = "Numerical"
    STRING = "String"
    DATETIME = "DateTime"
    BOOLEAN = "Boolean"

    ARRAY = "Array"  # Needs a itemtype. Example: array[int]
    MAP = "Map"  # a.k.a dict. Needs a keytype, valtype. Example: map[int, str]
    STRUCT = "Struct"  # dict with multiple valtypes Needs keys and their valtype. Example: struct[key1: int, key2: str]

    @classmethod
    def get(cls, val: DataType | str | list, orig_val: DataType | str | list | None = None) -> DataType | list:
        if isinstance(val, cls):
            return val
        if isinstance(val, list):
            return [cls.get(i) for i in val]
        if isinstance(val, dict):
            return {k: cls.get(v) for k, v in val.items()}
        val = str(val).strip()
        if val == cls.NUMERICAL.value:
            return cls.NUMERICAL
        if val == cls.STRING.value:
            return cls.STRING
        if val == cls.DATETIME.value:
            return cls.DATETIME
        if val == cls.BOOLEAN.value:
            return cls.BOOLEAN
        if val.startswith(cls.ARRAY.value):
            val = val[len(cls.ARRAY.value) :].strip()
            assert val[0] == "[" and val[-1] == "]"
            val = val[1:-1].strip()
            return [cls.ARRAY, cls.get(val, orig_val=val if orig_val is None else orig_val)]
        if val.startswith(cls.MAP.value):
            val = val[len(cls.MAP.value) :].strip()
            assert val[0] == "[" and val[-1] == "]"
            val = val[1:-1].strip()

            # Need to ensure split is at same level - so we don't get confused
            # by nested complex types like: 'map[string, map[int, string]]'
            bracket_depth = 0
            splitpoints = []
            for ic, c in enumerate(val):
                if c == "[":
                    bracket_depth += 1
                if c == "]":
                    bracket_depth -= 1
                if c == "," and bracket_depth == 0:
                    splitpoints.append(ic)
                    break

            if len(splitpoints) == 1:
                val1 = val[: splitpoints[0]].strip()
                val2 = val[splitpoints[0] + len(",") :].strip()
                return [
                    cls.MAP,
                    cls.get(val1.strip(), orig_val=val if orig_val is None else orig_val),
                    cls.get(val2.strip(), orig_val=val if orig_val is None else orig_val),
                ]
        if val.startswith(cls.STRUCT.value):
            # remove 'struct[' and ']' from dtype
            return [
                cls.STRUCT,
                {
                    key: cls.get(val_type, orig_val=val if orig_val is None else orig_val)
                    for key, val_type in get_key_values_of_struct_type(val).items()
                },
            ]

        msg = f"Unknown value provided: {val}"
        if orig_val is not None:
            msg += f", got from parsing {orig_val}"
        raise ValueError(msg)

    @classmethod
    def to_python_type(cls, val: DataType | list, *, allow_missing: bool = True) -> str:
        """
        Use the python typing library. Expects `import typing as t, datetime`
        """
        val = DataType.get(val)

        if val == DataType.NUMERICAL:  # Numerical is always float - so we use that here too
            annotation = "float"
        elif val == DataType.STRING:
            annotation = "str"
        elif val == DataType.DATETIME:
            annotation = "datetime.datetime"
        elif val == DataType.BOOLEAN:
            annotation = "bool"
        elif isinstance(val, list) and val[0] == DataType.ARRAY:
            annotation = f"list[{cls.to_python_type(val[1])}]"
        elif isinstance(val, list) and val[0] == DataType.MAP:
            # Key cannot take in None values in pyspark
            key_type = cls.to_python_type(val[1], allow_missing=False)
            value_type = cls.to_python_type(val[2])
            annotation = f"dict[{key_type}, {value_type}]"
        elif isinstance(val, list) and val[0] == DataType.STRUCT:
            fields = "{" + ", ".join(f"{key!r}: {cls.to_python_type(value)}" for key, value in val[1].items()) + "}"
            annotation = f't.TypedDict("T", {fields}, total=False)'
        else:
            raise TypeError(f"Unknown data type: {val}")
        return f"t.Optional[{annotation}]" if allow_missing else annotation


# FIXME: In corridor_api, JobType is ExecutionType, inconsistency can potentially cause issues
class JobType(enum.Enum):
    SIMULATION = "Simulation"
    COMPARISON = "Comparison"
    HILL_CLIMBING = "HillClimbing"
    MONITORING = "Monitoring"


class EntityLabels(enum.Enum):
    CURRENT = "current"
    COMPARISON = "challenger"
    ITERATION_TEMPLATE = "iter_{}"


@dataclasses.dataclass(frozen=True)
class OperatorInfo:
    name: str
    arity: str


class Operator(enum.Enum):
    # supporting logical `and`, `or` operators as group operators
    AND = OperatorInfo("and", "n")
    OR = OperatorInfo("or", "n")
    ALWAYS_TRUE = OperatorInfo("always_true", "0")

    # Binary operators
    EQUAL = OperatorInfo("eq", "2")
    NOT_EQUAL = OperatorInfo("neq", "2")
    IN = OperatorInfo("in", "2")
    NOT_IN = OperatorInfo("not_in", "2")
    LESS_THAN = OperatorInfo("lt", "2")
    LESS_THAN_EQUAL = OperatorInfo("lte", "2")
    GREATER_THAN = OperatorInfo("gt", "2")
    GREATER_THAN_EQUAL = OperatorInfo("gte", "2")

    # unary operators
    IS_MISSING = OperatorInfo("is_missing", "1")
    IS_NOT_MISSING = OperatorInfo("is_not_missing", "1")
    IS_TRUE = OperatorInfo("is_true", "1")
    IS_FALSE = OperatorInfo("is_false", "1")

    NOT = OperatorInfo("not", "1")

    @classmethod
    def get(cls, val: str) -> Operator:
        for op in Operator:
            if op.value.name == val:
                return op
        raise ValueError(f"Unsupported Operator found `{val}`")

    @classmethod
    def is_group_operator(cls, operator: Operator) -> bool:
        """Operators that can have nested conditions as an operator"""
        return operator in (cls.AND, cls.OR)


class OperandType(enum.Enum):
    TEXT = "constant"
    FEATURE = "feature"


class Objects(enum.Enum):
    DATA_TABLE = "DataTable"
    QUALITY_CHECK = "QualityProfile"
    DATA_ELEMENT = "DataElement"
    FEATURE = "Feature"
    DATASET = "Dataset"
    EXPERIMENT = "Experiment"
    MODEL = "Model"
    REPORT = "Report"
    GLOBAL_FUNCTION = "GlobalFunction"
    APPROVAL_WORKFLOW = "ApprovalWorkflow"
    FIELD = "Field"
    Algorithm = "Algorithm"
    USER = "User"
    PLATFORM_SETTING = "PlatformSetting"
    PROMPT = "Prompt"
    FOUNDATION_MODEL = "FoundationModel"
    RAG = "Rag"
    PIPELINE = "Pipeline"
    MONITORING = "Monitoring"
    ANNOTATION_QUEUE = "AnnotationQueue"

    @classmethod
    def name_mapping(cls) -> dict[Objects, str]:
        """Mapping for Object names as displayed on the UI"""
        return {
            cls.DATA_TABLE: "Data Table",
            cls.QUALITY_CHECK: "Quality Profile",
            cls.GLOBAL_FUNCTION: "Global Function",
            cls.APPROVAL_WORKFLOW: "Approval Workflow",
            cls.PLATFORM_SETTING: "Platform Settings",
            cls.PROMPT: "Prompt",
            cls.FOUNDATION_MODEL: "Foundation Model",
            cls.RAG: "Rag",
            cls.ANNOTATION_QUEUE: "Annotation Queue",
            cls.MONITORING: "Monitoring",
        }

    @classmethod
    def class_mapping(cls) -> dict[Objects, ApiBase]:
        from genguardx._internal.annotation_queue import AnnotationQueue
        from genguardx._internal.data_tables import DataTable
        from genguardx._internal.models import Model
        from genguardx._internal.monitoring import Monitoring
        from genguardx._internal.pipelines import Pipeline
        from genguardx._internal.prompts import Prompt
        from genguardx._internal.quality_check import QualityCheck
        from genguardx._internal.rags import Rag
        from genguardx._internal.resources import (
            GlobalFunction,
            Report,
        )
        from genguardx._internal.settings import PlatformSetting, User

        """Mapping for corridor python class"""
        return {
            cls.DATA_TABLE: DataTable,
            cls.QUALITY_CHECK: QualityCheck,
            cls.GLOBAL_FUNCTION: GlobalFunction,
            cls.REPORT: Report,
            cls.USER: User,
            cls.PLATFORM_SETTING: PlatformSetting,
            cls.PROMPT: Prompt,
            cls.FOUNDATION_MODEL: Model,
            cls.RAG: Rag,
            cls.PIPELINE: Pipeline,
            cls.ANNOTATION_QUEUE: AnnotationQueue,
            cls.MONITORING: Monitoring,
        }

    @classmethod
    def display_name(cls, obj: str | Objects) -> str:
        """Display names for Objects"""
        return cls.name_mapping().get(Objects(obj), Objects(obj).value)


SIMULATABLE_OBJECTS = (
    Objects.QUALITY_CHECK,
    Objects.FOUNDATION_MODEL,
    Objects.PIPELINE,
    Objects.PROMPT,
    Objects.RAG,
    Objects.MONITORING,
    Objects.REPORT,
    Objects.GLOBAL_FUNCTION,
)


class LineageCases(enum.Enum):
    CHILDREN = "children"
    PARENTS = "parents"


class ReportInputTypes(enum.Enum):
    FLOAT = "float"
    STR = "str"
    FEATURE = "feature"
    ARRAY_FEATURE = "array[feature]"


class ReportParameterType(enum.Enum):
    STRING = "String"
    NUMBER = "Number"
    # user can select any DE/Feature/Model registered on the platform as report inputs
    SINGLE_OBJECT = "SingleObject"
    # user can select any prompt, foundation model, rag, global function registered on the platform
    # as report inputs
    DYNAMIC_OBJECT = "DynamicObject"

    @classmethod
    def name_mapping(cls) -> dict[ReportParameterType, str]:
        return {cls.SINGLE_OBJECT: "Single Object"}

    @classmethod
    def display_name(cls, obj: ReportParameterType | str) -> str:
        """Display names for Report Parameter Type"""
        return cls.name_mapping().get(ReportParameterType(obj), ReportParameterType(obj).value)


class DataRecordTypes(enum.Enum):
    LOCATION = "location"
    DATASET = "dataset"


@dataclasses.dataclass(frozen=True)
class AttachmentFile:
    name: str
    content: io.BytesIO


class ReportOutputType(enum.Enum):
    FIGURE = "Figure"  # plotly figure
    METRIC = "Metric"  # dict of metric for different entity

    @classmethod
    def display_name(cls, obj: ReportOutputType | str) -> str:
        """Display names for Report Output Type"""
        return ReportOutputType(obj).value


class DataTableType(enum.Enum):
    RAW = "Raw"
    CLEANSED = "Cleansed"
    DATA_FILE = "DataFile"
