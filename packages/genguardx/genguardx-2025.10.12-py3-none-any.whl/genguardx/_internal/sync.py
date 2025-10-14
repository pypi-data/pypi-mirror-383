from __future__ import annotations

import builtins
import collections
import datetime
import enum
import inspect
import itertools
import json
import os
import sys
import textwrap
import types
import typing as t
from dataclasses import is_dataclass

import pandas as pd
import typing_extensions as te

import genguardx as ggx
from genguardx._internal.models import Model
from genguardx._internal.pipelines import PIPELINE_TYPE_DISPLAY_NAMES, Pipeline
from genguardx._internal.prompts import Prompt
from genguardx._internal.rags import Rag
from genguardx._internal.resources import AdditionalReportFigure, DataLogicExample, GlobalFunction, Report, ReportOutput
from genguardx._internal.util import utils
from genguardx._internal.util.constants import Objects, ReportOutputType, URLS
from genguardx._internal.util.get_annotations import get_annotations
from genguardx._internal.util.networking import api
from genguardx.exceptions import NotFound


try:
    __IPYTHON__  # noqa: B018 -- IPython sets this variable
except NameError:
    __IPYTHON__ = False

# We mimic django's supports_color() function to check if the terminal supports colors - but simplify it
# Ref: https://github.com/django/django/blob/5.2.1/django/core/management/color.py#L28
supports_color = ((hasattr(sys.stdout, "isatty") and sys.stdout.isatty()) or __IPYTHON__) and (
    sys.platform != "win32"
    or "ANSICON" in os.environ
    or "WT_SESSION" in os.environ  # Windows Terminal supports VT codes.
    or os.environ.get("TERM_PROGRAM") == "vscode"  # VSCode's built-in terminal supports colors.
)


# Refer: https://tforgione.fr/posts/ansi-escape-codes/
RESET = "\x1b[0m" if supports_color else ""
BOLD = "\x1b[1m" if supports_color else ""
UNDERLINE = "\x1b[4m" if supports_color else ""

RED = "\x1b[31m" if supports_color else ""
GREEN = "\x1b[32m" if supports_color else ""
BLUE = "\x1b[34m" if supports_color else ""
BLACK = "\x1b[30m" if supports_color else ""


class ModelInputType(enum.Enum):
    PYTHON_FUNCTION = "python function"  # FIXME: We should avoid spaces in enum values
    API_BASED = "api-based"
    CUSTOM = "custom"


cache = {}


def sync(obj: t.Callable) -> None:
    """Sync the declared item to the platform"""

    obj_cls = getattr(obj, "_corridor_metadata", {}).get("cls")

    # Reset the cache - this is just for slight performance improvement:
    global cache
    cache = {}

    if obj_cls == ggx.GlobalFunction:
        sync_gf(obj, prefix="")
    elif obj_cls == ggx.Report:
        sync_report(obj, prefix="")
    elif obj_cls == ggx.Model:
        sync_model(obj, prefix="")
    elif obj_cls == ggx.Rag:
        sync_rag(obj, prefix="")
    elif obj_cls == ggx.Prompt:
        sync_prompt(obj, prefix="")
    elif obj_cls == ggx.Pipeline:
        sync_pipeline(obj, prefix="")
    elif obj_cls is None:
        raise NotImplementedError(f"Unsure how to handle: {obj} - Not declared as a Corridor object")
    else:
        raise NotImplementedError(f"Unsure how to handle: {obj} with class: {obj_cls}")


def _typing_to_dtype(type_hint: t.Any) -> str | None:  # noqa: ANN401 -- Not sure how to type types !
    # FIXME: If there is a deep recursion, we do not clearly show where the error occured

    simple_types = {
        int: "Numerical",
        float: "Numerical",  # Handling double as float in Python
        str: "String",
        bool: "Boolean",
        datetime.datetime: "DateTime",
    }

    origin = t.get_origin(type_hint)
    args = t.get_args(type_hint)

    # Check for t.Optional and get the base type as we support optional for all our types by default
    # NOTE: types.UnionType is used for the `X | Y` annotation syntax - available in 3.10+
    if (origin is t.Union or (hasattr(types, "UnionType") and origin is types.UnionType)) and (
        len(args) == 2 and type(None) in args
    ):
        type_hint = next(iter(i for i in args if i is not type(None)))
        origin = t.get_origin(type_hint)
        args = t.get_args(type_hint)

    # Check if the type is in simple types
    if type_hint in simple_types:
        return simple_types[type_hint]

    # Handling list of lists, arrays
    if type_hint is list or type_hint is t.List:  # noqa: UP006 -- Need to support old typing
        raise LookupError(f"Unable to process type hint: '{type_hint}' as the list has no inner type")
    if origin is list or origin is t.List:  # noqa: UP006 -- Need to support old typing
        assert len(args) == 1, "Expected a single arg for list[] type"
        element_type = _typing_to_dtype(args[0])
        return f"Array[{element_type}]"

    # Handling dicts
    if type_hint is dict or type_hint is t.Dict or type_hint is t.Mapping:  # noqa: UP006 -- Need to support old typing
        raise LookupError(f"Unable to process type hint: '{type_hint}' as the dict has no inner type")
    if origin is dict or origin is t.Mapping or origin is t.Dict:  # noqa: UP006 -- Need to support old typing
        assert len(args) == 2, "Expected 2 args for dict[] type - a key type and a value type"
        key_type = _typing_to_dtype(args[0])
        value_type = _typing_to_dtype(args[1])
        return f"Map[{key_type}, {value_type}]"

    # Handling TypedDict (nested dictionaries)
    if te.is_typeddict(type_hint):  # NOTE: t.is_typeddict() is not available in py3.9
        field_annotations = t.get_type_hints(type_hint)
        fields = [f"{key}: {_typing_to_dtype(value)}" for key, value in field_annotations.items()]
        return f"Struct[{', '.join(fields)}]"

    if isinstance(type_hint, tuple) or is_dataclass(type_hint):
        raise LookupError(
            "Unable to parse NamedTuple - to use Corridor Struct type - define a t.TypedDict\n"
            "    For example: typing.TypedDict('custom_type', {'role': str, 'content': str})"
        )

    raise LookupError(f"Unable to map python type {type_hint!r} to corridor types")


def _get_definition_code(definition: t.Callable) -> str:
    """Take a python function object and get the definition body.

    This should only be used for loading definitions which were imported from the platform.
    We are assuming that the definition content to be loaded onto the platform starts with an anchor comment,
    "# -- BEGIN DEFINITION --"

    This approach is much more predictable. We had iterated through the following approaches before converging here,
        1. partitioning by newline
            - Fails when the function prototype is multiline
        2. Partitioning by colon (":")
            - Fails with type annotations
        3. AST parse of function body
            - Fails when docstrings are present with python3.7 (3.8 seems to have a lot of backward incompatible
              changes in std. libraries like ast, inspect etc.)
        4. Regex based parsing
            - Got too complex to handle all scenarios (docstring, type annotations, named arguments etc)
    """
    anchor_comment = "# -- BEGIN DEFINITION --"
    source = textwrap.dedent(inspect.getsource(definition).strip())

    # Add asserts to catch incorrectly written definitions
    assert anchor_comment in source, (
        f"Expected anchor comment\n    {anchor_comment}\nto be present in source. Found None"
    )

    source = source.split(anchor_comment)[-1]
    return textwrap.dedent(source).strip()


def _get_co_names(code_obj: types.CodeType) -> list[str]:
    """
    Recursively extracts all function and variable names used in a code object, including those in nested
    expressions like list comprehensions or generator expressions.
    Ref: https://stackoverflow.com/a/79117011

    :param code_obj: The code object to inspect.
    :returns:        A set of names of functions and variables used in the code object.
    """
    code_objects = {code_obj}
    co_names = set()
    while len(code_objects) > 0:
        current = code_objects.pop()
        co_names.update(current.co_names)
        code_objects.update(const for const in current.co_consts if isinstance(const, types.CodeType))
    return co_names


def _sync_inputs_from_object(function: t.Callable, *, prefix: str) -> dict[Objects, list[int]]:
    """
    look for variables and functions used inside the definition - but are declared outside
    these are the required input features (RTP, GV, GF ...)
    """
    # functions/variables called inside the definition
    input_objects = {i for i in _get_co_names(function.__code__) if not hasattr(builtins, i)}

    # Functions declared in the environment (Notebook, Shell)
    # NOTE: We assume everything it in the same notebook/shell and not in nested python modules/files
    declared_functions = {name: obj for name, obj in function.__globals__.items() if isinstance(obj, t.Callable)}

    unknown_aliases = []
    for alias in input_objects:
        if alias not in declared_functions and alias not in unknown_aliases:
            unknown_aliases.append(alias)

    if len(unknown_aliases) > 0:
        print(f"{prefix} ├ [WARN] Skipping some function calls that are not present in the global scope:")
        for unknown_alias in unknown_aliases:
            print(f"{prefix} │  - {unknown_alias}")

    input_ids = collections.defaultdict(list)
    for alias in input_objects:
        if alias in unknown_aliases:  # Skip these as we ouldn't find them and we told the user we are skipping them
            continue
        obj = declared_functions[alias]
        obj_cls = getattr(obj, "_corridor_metadata", {}).get("cls")

        input_prefix = f"{prefix} │ "
        if obj_cls == ggx.GlobalFunction:
            input_ids[Objects.GLOBAL_FUNCTION].append(sync_gf(obj, prefix=input_prefix)["result"]["id"])
        elif obj_cls == ggx.Report:
            input_ids[Objects.REPORT].append(sync_report(obj, prefix=input_prefix)["result"]["id"])
        elif obj_cls == ggx.Model:
            input_ids[Objects.FOUNDATION_MODEL].append(sync_model(obj, prefix=input_prefix)["result"]["id"])
        elif obj_cls == ggx.Rag:
            input_ids[Objects.RAG].append(sync_rag(obj, prefix=input_prefix)["result"]["id"])
        elif obj_cls == ggx.Prompt:
            input_ids[Objects.PROMPT].append(sync_prompt(obj, prefix=input_prefix)["result"]["id"])
        elif obj_cls == ggx.Pipeline:
            input_ids[Objects.PIPELINE].append(sync_pipeline(obj, prefix=input_prefix)["result"]["id"])
        elif obj_cls is None:
            print(f'{prefix} [WARN] Skipping "{alias}" - as it is not declared as a Corridor object')
        else:
            print(f'{prefix} [WARN] Skipping "{alias}" - as it is not declared as a recognized Corridor object')

    return input_ids


def _get_groups(obj_type: Objects) -> set[str]:
    global cache
    if "groups" not in cache:
        cache["groups"] = api.response(URLS.GROUP_PATH.value)["result"]
    return {g["name"] for g in cache["groups"] if g["objectType"] == obj_type.value}


###############################################################################
# Sync functions for each object
###############################################################################


def sync_gf(obj: t.Callable, *, prefix: str) -> dict[t.Str, t.Any]:
    obj_data = obj._corridor_metadata
    obj_cls = obj._corridor_metadata["cls"]

    # --------------------------------------------------------------------
    # 1. Alias: function name becomes the alias
    alias = obj.__name__
    name = obj_data["name"] if obj_data["name"] is not None else alias
    print(f"{prefix} {BLUE}Attempting to synchronize Global Function{RESET}: {alias!r}")

    try:
        existing = GlobalFunction(alias)
    except NotFound:
        existing = None

    # --------------------------------------------------------------------
    # 2. Data Type: function return type annotation becomes the data type
    annotations = get_annotations(obj, eval_str=True)
    data_type = _typing_to_dtype(annotations["return"]) if "return" in annotations else None

    # --------------------------------------------------------------------
    # 3. Description: function docstring becomes the description
    description = (
        textwrap.dedent(obj.__doc__).strip()
        if obj.__doc__ is not None
        else "Global Function imported from corridor package"
    )

    # --------------------------------------------------------------------
    # 4. Details: Extract the definition and group
    definition = {
        "id": existing._data.get("definition", {}).get("id") if existing else None,
        "runLogic": _get_definition_code(obj),
    }
    existing_groups = _get_groups(Objects.GLOBAL_FUNCTION)
    group = obj_data.get("group")
    if group not in existing_groups:
        print(f'{prefix} ├ [WARN] {RED}Group "{group}" not found{RESET}: Ignoring the group')
        group = None if existing is None else existing.group

    # --------------------------------------------------------------------
    # 6. Arguments: Get the function arguments for the Global Function
    function_inputs = []
    annotations = get_annotations(obj, eval_str=True)
    parameters = dict(inspect.signature(obj).parameters)
    parameters.pop("cache", None)  # Remove reserved keyword 'cache'
    for iparam, (param_alias, param) in enumerate(parameters.items(), start=1):
        is_mandatory = param.default is inspect.Signature.empty
        param_type = _typing_to_dtype(annotations[param_alias]) if param_alias in annotations else None
        if is_mandatory:
            default_value = None
        else:
            # We can either have a default value or it can be None
            if param.default is not None:
                assert isinstance(param.default, (list, tuple, str, float, bool, int)), (
                    f'Found unsupported default value of type "{type(param.default).__name__}" '
                    f'for argument "{param_alias}"'
                )
            # FIXME: We don't support recursive nested types :( -- need to improve this
            if isinstance(param.default, (list, tuple)):
                for val in param.default:
                    assert isinstance(val, (str, float, bool, int)), (
                        f'Found unsupported default value of type "list[{type(val).__name__}]" '
                        f'for argument "{param_alias}"'
                    )
            default_value = str(list(param.default)) if isinstance(param.default, tuple) else str(param.default)

        existing_input = (
            next((i for i in existing._data.get("functionInputs", []) if i.get("alias") == param_alias), {})
            if existing
            else {}
        )

        function_inputs.append(
            {
                "id": existing_input.get("id"),
                "inputOrder": iparam,
                "alias": param_alias,
                "inputType": param_type,
                "defaultValue": default_value,
                "isMandatory": is_mandatory,
            }
        )

    # --------------------------------------------------------------------
    # 7. Payload: Get the inputs used and create the final payload
    input_ids = _sync_inputs_from_object(obj, prefix=prefix)
    payload = {
        "name": name,
        "alias": alias,
        "type": data_type,
        "group": group,
        "description": description,
        "definition": definition,
        "featureVersionIds": input_ids[Objects.GLOBAL_FUNCTION],
        "functionInputs": function_inputs,
    }

    if existing is not None:
        final = api.response(obj_cls._LIST_URL, data={**existing._data, **payload})
        if "error" not in final:
            print(f"{prefix} {GREEN}Successfully updated existing Global Function{RESET}: {name}")
        else:
            raise RuntimeError(
                f"{RED}Error updating existing Global Function{RESET}. Got response:\n{json.dumps(final, indent=4)}"
            )
    else:
        final = api.response(obj_cls._LIST_URL, data=payload)
        if "error" not in final:
            print(f"{prefix} {GREEN}Successfully created a new Global Function{RESET}: {name}")
        else:
            raise RuntimeError(
                f"{RED}Error creating a new Global Function{RESET}. Got response:\n{json.dumps(final, indent=4)}"
            )
    return final


def sync_report(obj: t.Callable, *, prefix: str) -> dict[t.Str, t.Any]:
    import plotly.graph_objects as go

    RISK_TYPE_BACKEND_NAMES = {  # noqa: N806
        "Accuracy": "accuracy",
        "Stability": "stability",
        "Bias": "bias",
        "Vulnerability": "vulnerability",
        "Toxicity": "toxicity",
        "Others": "other",
    }
    TASK_TYPE_BACKEND_NAMES = {  # noqa: N806
        "Classification": "classification",
        "Templated Responses": "templatedResponse",
        "Generative Responses": "generativeResponse",
        "Summarization": "summarization",
        "Others": "other",
    }
    RISK_DOMAIN_BACKEND_NAMES = {  # noqa: N806
        "Model Risk Management": "modelRiskManagement",
        "Fair Lending": "fairLending",
        "Technology": "technology",
        "Infosec": "infosec",
        "Others": "other",
    }
    EVALUATION_METHOD_BACKEND_NAMES = {  # noqa: N806
        "LLM-as-a-Judge": "llm-as-judge",
        "Rule-based": "heuristic",
        "Statistical / ML Algorithms": "statistical",
        "Others": "other",
    }

    obj_data = obj._corridor_metadata
    obj_cls = obj._corridor_metadata["cls"]

    # --------------------------------------------------------------------
    # 1. Name: function name becomes the alias
    name = obj_data["name"] if obj_data["name"] is not None else obj.__name__
    print(f"{prefix} {BLUE}Attempting to synchronize Report{RESET}: {name!r}")

    try:
        existing = Report(name)
    except NotFound:
        existing = None

    # --------------------------------------------------------------------
    # 2. Object Details
    description = (  # The docstring becomes description
        textwrap.dedent(obj.__doc__).strip() if obj.__doc__ is not None else "Report imported from corridor package"
    )
    existing_groups = _get_groups(Objects.REPORT)
    group = obj_data.get("group")
    if group not in existing_groups:
        print(f'{prefix} ├ [WARN] {RED}Group "{group}" not found{RESET}: Ignoring the group')
        group = None if existing is None else existing.group

    risk_type = obj_data.get("risk_type")
    if risk_type is not None and risk_type not in RISK_TYPE_BACKEND_NAMES:
        print(f'{prefix} ├ [WARN] {RED}Risk Type "{risk_type}" is invalid{RESET}: Ignoring Risk Type')
        risk_type = None
    elif risk_type is not None:
        risk_type = RISK_TYPE_BACKEND_NAMES[risk_type]

    task_type = obj_data.get("task_type")
    if task_type is not None and task_type not in TASK_TYPE_BACKEND_NAMES:
        print(f'{prefix} ├ [WARN] {RED}Task Type "{task_type}" is invalid{RESET}: Ignoring Task Type')
        task_type = None
    elif task_type is not None:
        task_type = TASK_TYPE_BACKEND_NAMES[task_type]

    risk_domain = obj_data.get("risk_domain")
    if risk_domain is not None and risk_domain not in RISK_DOMAIN_BACKEND_NAMES:
        print(f'{prefix} ├ [WARN] {RED}Risk Domain "{risk_domain}" is invalid{RESET}: Ignoring Risk Domain')
        risk_domain = None
    elif risk_domain is not None:
        risk_domain = RISK_DOMAIN_BACKEND_NAMES[risk_domain]

    evaluation_methdology = obj_data.get("evaluation_methodology")
    if evaluation_methdology is not None and evaluation_methdology not in EVALUATION_METHOD_BACKEND_NAMES:
        print(
            f'{prefix} ├ [WARN] {RED}Evaluation Methodology "{evaluation_methdology}" is invalid{RESET}: '
            "Ignoring Evaluation Methodology"
        )
        evaluation_methdology = None
    if evaluation_methdology is not None:
        evaluation_methdology = EVALUATION_METHOD_BACKEND_NAMES[evaluation_methdology]

    report_methodology = obj_data.get("report_methodology")

    # --------------------------------------------------------------------
    # 3. definition: extract codes lines as definition
    definition = {
        "id": existing._data.get("definition", {}).get("id") if existing else None,
        "runLogic": _get_definition_code(obj),
    }
    input_ids = _sync_inputs_from_object(obj, prefix=prefix)

    # --------------------------------------------------------------------
    # 4. Report Output: Get the report output declared in the export file
    output_funcs = []
    for func in obj.__globals__.values():  # Go through any ReportOutputs defined in the same scope
        func_data = getattr(func, "_corridor_metadata", {})
        if not (inspect.isfunction(func) and func_data.get("cls") == ReportOutput and func_data.get("report") == name):
            continue
        output_funcs.append(func)

    outputs = []
    output_prefix = f"{prefix} │ "
    for output in output_funcs:
        output_data = getattr(output, "_corridor_metadata", {})
        output_name = output_data["name"] if output_data["name"] is not None else output.__name__
        print(f"{output_prefix} {BLUE}Analyzing information about Report Output{RESET}: {output_name!r}")

        existing_output = (
            next((i for i in existing._data.get("outputs", []) if i.get("name") == output_name), {}) if existing else {}
        )

        annotations = get_annotations(output, eval_str=True)
        output_return_type = annotations.get("return", None)

        # Check if the return type is a valid figure type - we search through the space or all unions of valid types
        valid_figure_types = (
            go.Figure,  # plotly figure
            pd.DataFrame,  # pandas datagrid
            str,  # markdown or html
        )
        if output_return_type in valid_figure_types or any(
            output_return_type == t.Union[comb]
            for r in range(2, len(valid_figure_types) + 1)
            for comb in itertools.combinations(valid_figure_types, r)
        ):
            output_type = ReportOutputType.FIGURE.value
        elif output_return_type == float:
            output_type = ReportOutputType.METRIC.value
        else:
            print(f"{prefix} [WARN] could not determine output type of report output - falling back to FIGURE")
            output_type = ReportOutputType.FIGURE.value
        out_input_ids = _sync_inputs_from_object(output, prefix=output_prefix)

        output_description = (  # The docstring becomes description
            textwrap.dedent(output.__doc__).strip()
            if output.__doc__ is not None
            else "Report Output imported from corridor package"
        )

        output_eval_methodology = output_data.get("evaluation_methodology")
        if output_eval_methodology is not None and output_eval_methodology not in EVALUATION_METHOD_BACKEND_NAMES:
            print(
                f'{prefix} ├ [WARN] {RED}Evaluation Methodology "{output_eval_methodology}" is invalid. {RESET}: '
                f"Available ones are: {', '.join(EVALUATION_METHOD_BACKEND_NAMES.keys())}"
                "Ignoring Evaluation Methodology"
            )
            output_eval_methodology = None
        if output_eval_methodology is not None:
            output_eval_methodology = EVALUATION_METHOD_BACKEND_NAMES[output_eval_methodology]

        outputs.append(
            {
                "id": existing_output.get("id"),
                "name": output_name,
                "type": output_type,
                "description": output_description,
                "definition": {
                    "id": existing_output.get("definition", {}).get("id"),
                    "runLogic": _get_definition_code(output),
                },
                "featureVersionIds": out_input_ids[Objects.GLOBAL_FUNCTION],
                "foundationModelVersionIds": out_input_ids[Objects.FOUNDATION_MODEL],
                "promptVersionIds": out_input_ids[Objects.PROMPT],
                "ragVersionIds": out_input_ids[Objects.RAG],
                "pipelineVersionIds": out_input_ids[Objects.PIPELINE],
                "width": output_data["width"],
                "height": output_data["height"],
                "sortOrder": len(outputs) + 1,
                "evaluationMethodology": output_eval_methodology,
            }
        )

        # Handle additional figures for this output
        additional_figures = []
        for func in obj.__globals__.values():
            func_data = getattr(func, "_corridor_metadata", {})
            if not (
                inspect.isfunction(func)
                and func_data.get("cls") == AdditionalReportFigure
                and func_data.get("report_output") == output_name
            ):
                continue

            additional_figure_data = getattr(func, "_corridor_metadata", {})
            additional_figure_name = (
                additional_figure_data["name"] if additional_figure_data["name"] is not None else func.__name__
            )

            existing_additional_figure = (
                next(
                    (
                        i
                        for i in existing_output.get("additionalFigures", [])
                        if i.get("name") == additional_figure_name
                    ),
                    {},
                )
                if existing_output
                else {}
            )

            additional_figure_input_ids = _sync_inputs_from_object(func, prefix=output_prefix)

            additional_figures.append(
                {
                    "id": existing_additional_figure.get("id"),
                    "name": additional_figure_name,
                    "icon": additional_figure_data.get("icon"),
                    "definition": {
                        "id": existing_additional_figure.get("definition", {}).get("id"),
                        "runLogic": _get_definition_code(func),
                    },
                    "featureVersionIds": additional_figure_input_ids[Objects.GLOBAL_FUNCTION],
                    "foundationModelVersionIds": additional_figure_input_ids[Objects.FOUNDATION_MODEL],
                    "promptVersionIds": additional_figure_input_ids[Objects.PROMPT],
                    "ragVersionIds": additional_figure_input_ids[Objects.RAG],
                    "pipelineVersionIds": additional_figure_input_ids[Objects.PIPELINE],
                    "sortOrder": len(additional_figures) + 1,
                }
            )

        # Add additional figures to the output
        if additional_figures:
            outputs[-1]["additionalFigures"] = additional_figures

    print(f"{output_prefix} {GREEN}All Report Outputs analyzed{RESET}")

    # --------------------------------------------------------------------
    # 5. Report Object Types: Get the report object types from the decorator
    object_types = []
    for object_type in obj_data["object_types"]:
        existing_objtype = (
            next((i for i in existing._data.get("objectTypes", []) if i.get("objectType") == object_type), {})
            if existing
            else {}
        )
        object_types.append({"id": existing_objtype.get("id"), "objectType": object_type})

    # --------------------------------------------------------------------
    # 6. Data Logic Examples: Get data logic examples from the decorator or object metadata

    data_logic_examples = []
    # Find DataLogicExample functions defined in the same scope
    example_funcs = []
    for func in obj.__globals__.values():
        func_data = getattr(func, "_corridor_metadata", {})
        if not (
            inspect.isfunction(func) and func_data.get("cls") == DataLogicExample and func_data.get("report") == name
        ):
            continue
        example_funcs.append(func)

    example_prefix = f"{prefix} │ "
    for example_func in example_funcs:
        example_data = getattr(example_func, "_corridor_metadata", {})
        example_name = example_data["name"] if example_data["name"] is not None else example_func.__name__
        print(f"{example_prefix} {BLUE}Analyzing information about Data Logic Example{RESET}: {example_name!r}")

        existing_example = (
            next((i for i in existing._data.get("dataLogicExamples", []) if i.get("name") == example_name), {})
            if existing
            else {}
        )

        example_input_ids = _sync_inputs_from_object(example_func, prefix=example_prefix)

        example_description = (
            textwrap.dedent(example_func.__doc__).strip()
            if example_func.__doc__ is not None
            else example_data.get("description", "Data Logic Example imported from corridor package")
        )

        data_logic_examples.append(
            {
                "id": existing_example.get("id"),
                "name": example_name,
                "description": example_description,
                "definition": {
                    "id": existing_example.get("definition", {}).get("id") if existing_example else None,
                    "runLogic": _get_definition_code(example_func),
                },
                "featureVersionIds": example_input_ids[Objects.GLOBAL_FUNCTION],
                "promptVersionIds": example_input_ids[Objects.PROMPT],
                "foundationModelVersionIds": example_input_ids[Objects.FOUNDATION_MODEL],
                "ragVersionIds": example_input_ids[Objects.RAG],
                "tableIds": example_data.get("table_ids", []),
                "inputData": example_data.get("input_data"),
                "sortOrder": len(data_logic_examples) + 1,
            }
        )

    if example_funcs:
        print(f"{example_prefix} {GREEN}All Data Logic Examples analyzed{RESET}")

    # --------------------------------------------------------------------
    # 7. Report Parameters: Get the report execution type from the decorator
    report_parameters = []
    for param in obj_data["parameters"]:
        existing_parameter = (
            next((i for i in existing._data.get("parameters", []) if i.get("alias") == param["alias"]), {})
            if existing
            else {}
        )
        report_parameters.append(
            {
                "id": existing_parameter.get("id"),
                **{utils.camelcase(k): v for k, v in param.items()},
            }
        )

    # --------------------------------------------------------------------
    # 8. Payload: Get the inputs used and create the final payload
    payload = {
        "name": name,
        "objectTypes": object_types,
        "group": group,
        "riskType": risk_type,
        "taskType": task_type,
        "riskDomain": risk_domain,
        "evaluationMethodology": evaluation_methdology,
        "reportMethodology": report_methodology,
        "description": description,
        "definition": definition,
        "featureVersionIds": input_ids[Objects.GLOBAL_FUNCTION],
        "foundationModelVersionIds": input_ids[Objects.FOUNDATION_MODEL],
        "promptVersionIds": input_ids[Objects.PROMPT],
        "ragVersionIds": input_ids[Objects.RAG],
        "pipelineVersionIds": input_ids[Objects.PIPELINE],
        "outputs": outputs,
        "dataLogicExamples": data_logic_examples,
        "parameters": report_parameters,
    }

    if existing is not None:
        final = api.response(obj_cls._LIST_URL, data={**existing._data, **payload})
        if "error" not in final:
            print(f"{prefix} {GREEN}Successfully updated existing Report{RESET}: {name}")
        else:
            raise RuntimeError(
                f"{RED}Error updating existing Report{RESET}. Got response:\n{json.dumps(final, indent=4)}"
            )
    else:
        final = api.response(obj_cls._LIST_URL, data=payload)
        if "error" not in final:
            print(f"{prefix} {GREEN}Successfully created a new Report{RESET}: {name}")
        else:
            raise RuntimeError(f"{RED}Error creating a new Report{RESET}. Got response:\n{json.dumps(final, indent=4)}")
    return final


def sync_model(obj: t.Callable, *, prefix: str) -> dict[t.Str, t.Any]:
    """
    Sync the declared Model to the platform.
    """
    obj_data = obj._corridor_metadata
    obj_cls = obj._corridor_metadata["cls"]

    # --------------------------------------------------------------------
    # 1. Alias: function name becomes the alias
    alias = obj.__name__
    name = obj_data["name"] if obj_data["name"] is not None else alias
    print(f"{prefix} {BLUE}Attempting to synchronize Model{RESET}: {alias!r}")

    try:
        existing = Model(alias)
    except NotFound:
        existing = None

    # --------------------------------------------------------------------
    # 2. Data Type: function return type annotation becomes the data type
    annotations = get_annotations(obj, eval_str=True)
    data_type = _typing_to_dtype(annotations["return"]) if "return" in annotations else None

    # --------------------------------------------------------------------
    # 3. Details: Description, group and dimensions
    description = (
        textwrap.dedent(obj.__doc__).strip() if obj.__doc__ is not None else "Model imported from corridor package"
    )
    existing_groups = _get_groups(Objects.FOUNDATION_MODEL)
    group = obj_data.get("group")
    if group not in existing_groups:
        print(f'{prefix} ├ [WARN] {RED}Group "{group}" not found{RESET}: Ignoring the group')
        group = None if existing is None else existing.group

    OWNERSHIP_TYPE_BACKEND_NAMES = {  # noqa: N806
        "Open Source": "opensource",
        "Proprietary": "proprietary",
    }
    MODEL_TYPE_BACKEND_NAMES = {  # noqa: N806
        "LLM": "llm",
        "Text Embedding": "text-embedding",
        "Guardrail": "guardrail",
        "Judge Model": "judge",
        "Others": "other",
    }

    ownership_type = obj_data.get("ownership_type")
    if ownership_type is not None and ownership_type not in OWNERSHIP_TYPE_BACKEND_NAMES:
        print(
            f'{prefix} ├ [WARN] {RED}Ownership Type "{ownership_type}" is invalid{RESET}: Ignoring the Ownership Type'
        )
        ownership_type = None
    elif ownership_type is not None:
        ownership_type = OWNERSHIP_TYPE_BACKEND_NAMES[ownership_type]

    model_type = obj_data.get("model_type")
    if model_type is not None and model_type not in MODEL_TYPE_BACKEND_NAMES:
        print(f'{prefix} ├ [WARN] {RED}Model Type "{model_type}" is invalid{RESET}: Ignoring the Model Type')
        model_type = None
    elif model_type is not None:
        model_type = MODEL_TYPE_BACKEND_NAMES[model_type]

    # --------------------------------------------------------------------
    # 4. Definition: Extract code lines as definition
    sig = inspect.signature(obj)
    if obj_data["provider"]:
        input_type = ModelInputType.API_BASED.value
    elif "model" in sig.parameters:
        input_type = ModelInputType.CUSTOM.value
    else:
        input_type = ModelInputType.PYTHON_FUNCTION.value

    definition = {
        "id": existing._data.get("definition", {}).get("id") if existing else None,
        "file": {"upload": sig.parameters["model"].default.read_bytes()} if "model" in sig.parameters else None,
        "fileSource": "file-upload" if "model" in sig.parameters else None,
        "fileSourceInfo": {"fileName": str(sig.parameters["model"].default)} if "model" in sig.parameters else None,
        "runLogic": _get_definition_code(obj),
    }
    input_ids = _sync_inputs_from_object(obj, prefix=prefix)

    # --------------------------------------------------------------------
    # 6. Function Inputs: Get the function arguments for the Foundation Model
    function_inputs = []
    annotations = get_annotations(obj, eval_str=True)
    parameters = dict(inspect.signature(obj).parameters)
    parameters.pop("cache", None)  # Remove reserved keyword 'cache'
    if input_type == ModelInputType.CUSTOM.value:
        parameters.pop("model", None)  # Remove reserved keyword 'model'
    for iparam, (param_alias, param) in enumerate(parameters.items(), start=1):
        param_type = _typing_to_dtype(annotations.get(param_alias))
        is_mandatory = param.default is inspect.Signature.empty
        default_value = str(param.default) if not is_mandatory else None

        existing_input = (
            next((i for i in existing._data.get("functionInputs", []) if i.get("alias") == param_alias), {})
            if existing
            else {}
        )

        function_inputs.append(
            {
                "id": existing_input.get("id"),
                "inputOrder": iparam,
                "alias": param_alias,
                "inputType": param_type,
                "defaultValue": default_value,
                "isMandatory": is_mandatory,
            }
        )

    # --------------------------------------------------------------------
    # 7. Payload: Get the inputs used and create the final payload
    payload = {
        "name": name,
        "alias": alias,
        "type": data_type,
        "inputType": input_type,
        "group": group,
        "modelType": model_type,
        "ownershipType": ownership_type,
        "description": description,
        "definition": definition,
        "provider": obj_data["provider"],
        "model": obj_data["model"],
        "featureVersionIds": input_ids[Objects.GLOBAL_FUNCTION],
        "foundationModelVersionIds": input_ids[Objects.FOUNDATION_MODEL],
        "promptVersionIds": input_ids[Objects.PROMPT],
        "ragVersionIds": input_ids[Objects.RAG],
        "functionInputs": function_inputs,
    }

    # --------------------------------------------------------------------
    # 9. Sync with the platform

    if existing is not None:
        final = api.response(obj_cls._LIST_URL, data={**existing._data, **payload})
        if "error" not in final:
            print(f"{prefix} {GREEN}Successfully updated existing Foundation Model{RESET}: {name}")
        else:
            raise RuntimeError(
                f"{RED}Error updating existing Foundation Model{RESET}. Got response:\n{json.dumps(final, indent=4)}"
            )
    else:
        final = api.response(obj_cls._LIST_URL, data=payload)
        if "error" not in final:
            print(f"{prefix} {GREEN}Successfully created a new Foundation Model{RESET}: {name}")
        else:
            raise RuntimeError(
                f"{RED}Error creating a new Foundation Model{RESET}. Got response:\n{json.dumps(final, indent=4)}"
            )
    return final


def sync_rag(obj: t.Callable, *, prefix: str) -> dict[t.Str, t.Any]:
    """
    Sync the declared RAG to the platform.
    """
    obj_data = obj._corridor_metadata
    obj_cls = obj._corridor_metadata["cls"]

    # --------------------------------------------------------------------
    # 1. Alias: function name becomes the alias
    alias = obj.__name__
    name = obj_data["name"] if obj_data["name"] is not None else alias
    print(f"{prefix} {BLUE}Attempting to synchronize RAG{RESET}: {alias!r}")

    try:
        existing = Rag(alias)
    except NotFound:
        existing = None

    # --------------------------------------------------------------------
    # 2. Data Type: function return type annotation becomes the data type
    annotations = get_annotations(obj, eval_str=True)
    data_type = _typing_to_dtype(annotations["return"]) if "return" in annotations else None

    # --------------------------------------------------------------------
    # 3. Description: function docstring becomes the description
    description = (
        textwrap.dedent(obj.__doc__).strip() if obj.__doc__ is not None else "RAG model imported from corridor package"
    )
    existing_groups = _get_groups(Objects.RAG)
    group = obj_data.get("group")
    if group not in existing_groups:
        print(f'{prefix} ├ [WARN] {RED}Group "{group}" not found{RESET}: Ignoring the group')
        group = None if existing is None else existing.group

    KNOWLEDGE_BASE_FORMAT_BACKEND_NAMES = {  # noqa: N806
        "Vector Database": "vectorDatabase",
        "Graph Database": "graphDatabase",
        "Relational Database": "relationalDatabase",
        "External Web-Search APIs": "externalWebSearchApis",
        "NoSQL": "noSql",
        "Document": "document",
        "Others": "other",
    }
    knowledge_base_format = obj_data.get("knowledge_base_format")
    if knowledge_base_format is not None and knowledge_base_format not in KNOWLEDGE_BASE_FORMAT_BACKEND_NAMES:
        print(
            f'{prefix} ├ [WARN] {RED}Knowledge Base Format "{knowledge_base_format}" is invalid{RESET}: '
            "Ignoring the Knowledge Base Format"
        )
        knowledge_base_format = None
    elif knowledge_base_format is not None:
        knowledge_base_format = KNOWLEDGE_BASE_FORMAT_BACKEND_NAMES[knowledge_base_format]

    # --------------------------------------------------------------------
    # 4. Definition: Extract code lines as definition
    sig = inspect.signature(obj)
    if obj_data["provider"]:
        input_type = ModelInputType.API_BASED.value
    elif "knowledge" in sig.parameters:
        input_type = ModelInputType.CUSTOM.value
    else:
        input_type = ModelInputType.PYTHON_FUNCTION.value

    definition = {
        "id": existing._data.get("definition", {}).get("id") if existing else None,
        "file": (
            {"upload": sig.parameters["knowledge"].default.read_bytes()} if "knowledge" in sig.parameters else None
        ),
        "fileSource": "file-upload" if "knowledge" in sig.parameters else None,
        "fileSourceInfo": (
            {"fileName": str(sig.parameters["knowledge"].default)} if "knowledge" in sig.parameters else None
        ),
        "runLogic": _get_definition_code(obj),
    }
    input_ids = _sync_inputs_from_object(obj, prefix=prefix)

    # --------------------------------------------------------------------
    # 6. Function Inputs: Get the function arguments for the RAG model
    function_inputs = []
    annotations = get_annotations(obj, eval_str=True)
    parameters = dict(inspect.signature(obj).parameters)
    parameters.pop("cache", None)  # Remove reserved keyword 'cache'
    if input_type == ModelInputType.CUSTOM.value:
        parameters.pop("knowledge", None)  # Remove reserved keyword 'knowledge'
    for iparam, (param_alias, param) in enumerate(parameters.items(), start=1):
        param_type = _typing_to_dtype(annotations.get(param_alias))
        is_mandatory = param.default is inspect.Signature.empty
        default_value = str(param.default) if not is_mandatory else None

        existing_input = (
            next((i for i in existing._data.get("functionInputs", []) if i.get("alias") == param_alias), {})
            if existing
            else {}
        )

        function_inputs.append(
            {
                "id": existing_input.get("id"),
                "inputOrder": iparam,
                "alias": param_alias,
                "inputType": param_type,
                "defaultValue": default_value,
                "isMandatory": is_mandatory,
            }
        )

    # --------------------------------------------------------------------
    # 7. Payload: Get the inputs used and create the final payload
    payload = {
        "name": name,
        "alias": alias,
        "type": data_type,
        "group": group,
        "knowledgeBaseFormat": knowledge_base_format,
        "description": description,
        "inputType": input_type,
        "definition": definition,
        "featureVersionIds": input_ids[Objects.GLOBAL_FUNCTION],
        "foundationModelVersionIds": input_ids[Objects.FOUNDATION_MODEL],
        "promptVersionIds": input_ids[Objects.PROMPT],
        "ragVersionIds": input_ids[Objects.RAG],
        "functionInputs": function_inputs,
    }

    # --------------------------------------------------------------------
    # 8. Sync with the platform

    if existing is not None:
        final = api.response(obj_cls._LIST_URL, data={**existing._data, **payload})
        if "error" not in final:
            print(f"{prefix} {GREEN}Successfully updated existing RAG{RESET}: {name}")
        else:
            raise RuntimeError(f"{RED}Error updating existing RAG{RESET}. Got response:\n{json.dumps(final, indent=4)}")
    else:
        final = api.response(obj_cls._LIST_URL, data=payload)
        if "error" not in final:
            print(f"{prefix} {GREEN}Successfully created a new RAG{RESET}: {name}")
        else:
            raise RuntimeError(f"{RED}Error creating a new RAG{RESET}. Got response:\n{json.dumps(final, indent=4)}")
    return final


def sync_prompt(obj: t.Callable, *, prefix: str) -> dict[t.Str, t.Any]:
    """
    Sync the declared PROMPT to the platform.
    """
    obj_data = obj._corridor_metadata
    obj_cls = obj._corridor_metadata["cls"]

    # --------------------------------------------------------------------
    # 1. Alias: function name becomes the alias
    alias = obj.__name__
    name = obj_data["name"] if obj_data["name"] is not None else alias
    print(f"{prefix} {BLUE}Attempting to synchronize Prompt{RESET}: {alias!r}")

    try:
        existing = Prompt(alias)
    except NotFound:
        existing = None

    # --------------------------------------------------------------------
    # 2. Description: function docstring becomes the description
    description = (
        textwrap.dedent(obj.__doc__).strip() if obj.__doc__ is not None else "RAG model imported from corridor package"
    )
    existing_groups = _get_groups(Objects.PROMPT)
    group = obj_data.get("group")
    if group not in existing_groups:
        print(f'{prefix} ├ [WARN] {RED}Group "{group}" not found{RESET}: Ignoring the group')
        group = None if existing is None else existing.group

    PROMPT_TASK_TYPE_BACKEND_NAMES = {  # noqa: N806
        "Classification": "classification",
        "Question Answering": "questionAnswering",
        "Information Extraction": "informationExtraction",
        "Summarization": "summarization",
        "Code Generation": "codeGeneration",
        "Transformation": "transformation",
        "Generation": "generation",
        "Others": "other",
    }
    PROMPT_TYPE_BACKEND_NAMES = {  # noqa: N806
        "System Instruction": "systemInstruction",
        "User Prompt": "userPrompt",
        "Others": "other",
    }
    PROMPT_ELEMENT_BACKEND_NAMES = {  # noqa: N806
        "Persona + Goal": "personaGoal",
        "Tone": "tone",
        "Task": "task",
        "Constraints": "constraints",
        "Context": "context",
        "Examples": "examples",
        "Reasoning Steps": "reasoningSteps",
        "Output Format": "outputFormat",
        "Recap": "recap",
    }
    task_type = obj_data.get("task_type")
    if task_type is not None and task_type not in PROMPT_TASK_TYPE_BACKEND_NAMES:
        print(f'{prefix} ├ [WARN] {RED}Task Type "{task_type}" is invalid{RESET}: Ignoring the Task Type')
        task_type = None
    elif task_type is not None:
        task_type = PROMPT_TASK_TYPE_BACKEND_NAMES[task_type]

    prompt_type = obj_data.get("prompt_type")
    if prompt_type is not None and prompt_type not in PROMPT_TYPE_BACKEND_NAMES:
        print(f'{prefix} ├ [WARN] {RED}Prompt Type "{prompt_type}" is invalid{RESET}: Ignoring the Prompt Type')
        prompt_type = None
    elif prompt_type is not None:
        prompt_type = PROMPT_TYPE_BACKEND_NAMES[prompt_type]

    prompt_elements = []
    for element in obj_data.get("prompt_elements"):
        if element not in PROMPT_ELEMENT_BACKEND_NAMES:
            print(f'{prefix} ├ [WARN] {RED}Prompt Element "{element}" is invalid{RESET}: Ignoring the Prompt Element')
        else:
            prompt_elements.append(PROMPT_ELEMENT_BACKEND_NAMES[element])

    # --------------------------------------------------------------------
    # 3. Definition: Extract code lines as definition
    sig = inspect.signature(obj)
    if "prompt" not in sig.parameters:
        raise ValueError(
            f'Prompt "{alias}" must be a kwarg names: "prompt" which contains the prompt template as the default value'
        )
    definition = {
        "id": existing._data.get("definition", {}).get("id") if existing else None,
        # FIXME: initLogic is only used for prompt template
        "initLogic": sig.parameters["prompt"].default,
        "runLogic": _get_definition_code(obj),
    }
    input_ids = _sync_inputs_from_object(obj, prefix=prefix)

    # --------------------------------------------------------------------
    # 5. Function Inputs: Get the function arguments for the RAG model
    function_inputs = []
    annotations = get_annotations(obj, eval_str=True)
    parameters = dict(inspect.signature(obj).parameters)
    parameters.pop("cache", None)  # Remove reserved keyword 'cache'
    parameters.pop("prompt", None)  # Remove reserved keyword 'prompt'
    for iparam, (param_alias, param) in enumerate(parameters.items(), start=1):
        param_type = _typing_to_dtype(annotations.get(param_alias))
        is_mandatory = param.default is inspect.Signature.empty
        default_value = str(param.default) if not is_mandatory else None

        existing_input = (
            next((i for i in existing._data.get("functionInputs", []) if i.get("alias") == param_alias), {})
            if existing
            else {}
        )

        function_inputs.append(
            {
                "id": existing_input.get("id"),
                "inputOrder": iparam,
                "alias": param_alias,
                "inputType": param_type,
                "defaultValue": default_value,
                "isMandatory": is_mandatory,
            }
        )

    # --------------------------------------------------------------------
    # 6. Payload: Get the inputs used and create the final payload
    payload = {
        "name": name,
        "alias": alias,
        "group": group,
        "taskType": task_type,
        "promptType": prompt_type,
        "promptElements": prompt_elements,
        "description": description,
        "definition": definition,
        "featureVersionIds": input_ids[Objects.GLOBAL_FUNCTION],
        "foundationModelVersionIds": input_ids[Objects.FOUNDATION_MODEL],
        "promptVersionIds": input_ids[Objects.PROMPT],
        "ragVersionIds": input_ids[Objects.RAG],
        "functionInputs": function_inputs,
    }

    # --------------------------------------------------------------------
    # 8. Sync with the platform
    if existing is not None:
        final = api.response(obj_cls._LIST_URL, data={**existing._data, **payload})
        if "error" not in final:
            print(f"{prefix} {GREEN}Successfully updated existing Prompt{RESET}: {name}")
        else:
            raise RuntimeError(
                f"{RED}Error updating existing Prompt{RESET}. Got response:\n{json.dumps(final, indent=4)}"
            )
    else:
        final = api.response(obj_cls._LIST_URL, data=payload)
        if "error" not in final:
            print(f"{prefix} {GREEN}Successfully created a new Prompt{RESET}: {alias!r}")
        else:
            raise RuntimeError(f"{RED}Error creating a new Prompt{RESET}. Got response:\n{json.dumps(final, indent=4)}")
    return final


def sync_pipeline(obj: t.Callable, *, prefix: str) -> dict[t.Str, t.Any]:
    """
    Sync the declared Pipeline to the platform.
    """
    obj_data = obj._corridor_metadata
    obj_cls = obj._corridor_metadata["cls"]

    # --------------------------------------------------------------------
    # 1. Alias: function name becomes the alias
    alias = obj.__name__
    name = obj_data["name"] if obj_data["name"] is not None else alias
    print(f"{prefix} {BLUE}Attempting to synchronize Pipeline{RESET}: {alias!r}")

    try:
        existing = Pipeline(alias)
    except NotFound:
        existing = None

    # --------------------------------------------------------------------
    # 2. Data Type: function return type annotation becomes the data type
    display_name_to_enum = {v: k for k, v in PIPELINE_TYPE_DISPLAY_NAMES.items()}
    assert obj_data["pipeline_type"] is not None, f"Expected pipeline_type to be declared for Pipeline: {alias}"
    assert obj_data["pipeline_type"] in display_name_to_enum, (
        f"Expected pipeline_type to be one of: {sorted(display_name_to_enum.keys())} for Pipeline: {alias}"
    )
    pipeline_type = display_name_to_enum[obj_data["pipeline_type"]]

    if pipeline_type == "FreeForm":
        annotations = get_annotations(obj, eval_str=True)
        data_type = _typing_to_dtype(annotations["return"]) if "return" in annotations else None
        interaction_type = None
        context_type = None
    else:
        annotations = get_annotations(obj, eval_str=True)
        data_type = None
        interaction_type = "Struct[role: String, content: String]"
        context_type = _typing_to_dtype(annotations["context"])

    # --------------------------------------------------------------------
    # 3. Description: function docstring becomes the description
    description = (
        textwrap.dedent(obj.__doc__).strip() if obj.__doc__ is not None else "Pipeline imported from corridor package"
    )
    existing_groups = _get_groups(Objects.PIPELINE)
    group = obj_data.get("group")
    if group not in existing_groups:
        print(f'{prefix} ├ [WARN] {RED}Group "{group}" not found{RESET}: Ignoring the group')
        group = None if existing is None else existing.group

    # --------------------------------------------------------------------
    # 4. Dimensions
    USECASE_TYPE_BACKEND_NAMES = {  # noqa: N806
        "Question Answering": "questionAnswering",
        "Summarization": "summarization",
        "Translation": "translation",
    }
    TASK_TYPE_BACKEND_NAMES = {  # noqa: N806
        "Classification": "classification",
        "Templated Responses": "templatedResponse",
        "Generative Responses": "generativeResponse",
        "Summarization": "summarization",
        "Others": "other",
    }
    IMPACT_BACKEND_NAMES = {  # noqa: N806
        "External Facing": "externalFacing",
        "Internal - with external implications": "internal",
        "Internal Only": "internalOnly",
    }
    DATA_USAGE_BACKEND_NAMES = {  # noqa: N806
        "No Additional Data": "noAdditionalData",
        "General Public Data": "generalPublicData",
        "Internal Policies/Data": "internalPoliciesData",
        "Customer Specific Data": "customerSpecificData",
    }

    usecase_type = obj_data.get("usecase_type")
    if usecase_type is not None and usecase_type not in USECASE_TYPE_BACKEND_NAMES:
        print(f'{prefix} ├ [WARN] {RED}Usecase Type "{usecase_type}" is invalid{RESET}: Ignoring the Usecase Type')
        usecase_type = None
    elif usecase_type is not None:
        usecase_type = USECASE_TYPE_BACKEND_NAMES[usecase_type]

    task_type = obj_data.get("task_type")
    if task_type is not None and task_type not in TASK_TYPE_BACKEND_NAMES:
        print(f'{prefix} ├ [WARN] {RED}Task Type "{task_type}" is invalid{RESET}: Ignoring the Task Type')
        task_type = None
    elif task_type is not None:
        task_type = TASK_TYPE_BACKEND_NAMES[task_type]

    impact = obj_data.get("impact")
    if impact is not None and impact not in IMPACT_BACKEND_NAMES:
        print(f'{prefix} ├ [WARN] {RED}Impact "{impact}" is invalid{RESET}: Ignoring the Impact')
        impact = None
    elif impact is not None:
        impact = IMPACT_BACKEND_NAMES[impact]

    data_usage = []
    for usage in obj_data.get("data_usage"):
        if usage not in DATA_USAGE_BACKEND_NAMES:
            print(f'{prefix} ├ [WARN] {RED}Data Usage "{usage}" is invalid{RESET}: Ignoring the Data Usage')
        else:
            data_usage.append(DATA_USAGE_BACKEND_NAMES[usage])

    # --------------------------------------------------------------------
    # 5. Definition: Extract code lines as definition
    sig = inspect.signature(obj)
    if obj_data["provider"]:
        input_type = ModelInputType.API_BASED.value
    elif "model" in sig.parameters:
        input_type = ModelInputType.CUSTOM.value
    else:
        input_type = ModelInputType.PYTHON_FUNCTION.value

    definition = {
        "id": existing._data.get("definition", {}).get("id") if existing else None,
        "file": {"upload": sig.parameters["model"].default.read_bytes()} if "model" in sig.parameters else None,
        "fileSource": "file-upload" if "model" in sig.parameters else None,
        "fileSourceInfo": {"fileName": str(sig.parameters["model"].default)} if "model" in sig.parameters else None,
        "runLogic": _get_definition_code(obj),
    }
    input_ids = _sync_inputs_from_object(obj, prefix=prefix)

    # --------------------------------------------------------------------
    # 6. Function Inputs: Get the function arguments for the Pipeline
    function_inputs = []
    annotations = get_annotations(obj, eval_str=True)
    parameters = dict(inspect.signature(obj).parameters)
    parameters.pop("cache", None)  # Remove reserved keyword 'cache'
    if input_type == ModelInputType.CUSTOM.value:
        parameters.pop("model", None)  # Remove reserved keyword 'model'
    if pipeline_type == "Chat":
        for key in ("user_message", "history", "context"):  # The backend automatically adds these, so we skip these
            parameters.pop(key, None)
    for iparam, (param_alias, param) in enumerate(parameters.items(), start=1):
        param_type = _typing_to_dtype(annotations.get(param_alias))
        is_mandatory = param.default is inspect.Signature.empty
        default_value = str(param.default) if not is_mandatory else None

        existing_input = (
            next((i for i in existing._data.get("functionInputs", []) if i.get("alias") == param_alias), {})
            if existing
            else {}
        )

        function_inputs.append(
            {
                "id": existing_input.get("id"),
                "inputOrder": iparam,
                "alias": param_alias,
                "inputType": param_type,
                "defaultValue": default_value,
                "isMandatory": is_mandatory,
            }
        )

    # --------------------------------------------------------------------
    # 7. Payload: Get the inputs used and create the final payload
    payload = {
        "name": name,
        "alias": alias,
        "group": group,
        "usecaseType": usecase_type,
        "taskType": task_type,
        "impact": impact,
        "dataUsage": data_usage,
        "pipelineType": pipeline_type,
        "type": data_type,
        "interactionType": interaction_type,
        "contextType": context_type,
        "description": description,
        "inputType": input_type,
        "definition": definition,
        "functionInputs": function_inputs,
        "featureVersionIds": input_ids[Objects.GLOBAL_FUNCTION],
        "foundationModelVersionIds": input_ids[Objects.FOUNDATION_MODEL],
        "promptVersionIds": input_ids[Objects.PROMPT],
        "ragVersionIds": input_ids[Objects.RAG],
        "pipelineVersionIds": input_ids[Objects.PIPELINE],
    }

    # --------------------------------------------------------------------
    # 7. Sync with the platform

    if existing is not None:
        final = api.response(obj_cls._LIST_URL, data={**existing._data, **payload})
        if "error" not in final:
            print(f"{prefix} {GREEN}Successfully updated existing Pipeline{RESET}: {alias!r}")
        else:
            raise RuntimeError(
                f"{RED}Error updating existing Pipeline{RESET}. Got response:\n{json.dumps(final, indent=4)}"
            )
    else:
        final = api.response(obj_cls._LIST_URL, data=payload)
        if "error" not in final:
            print(f"{prefix} {GREEN}Successfully created a new Pipeline{RESET}: {alias!r}")
        else:
            raise RuntimeError(
                f"{RED}Error creating a new Pipeline{RESET}. Got response:\n{json.dumps(final, indent=4)}"
            )
    return final
