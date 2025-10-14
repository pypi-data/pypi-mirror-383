"""
corridor - Python interface to interact with Corridor Platforms
=====================================================================

`corridor` is a Python package providing a python interface to interact
and work with various components of the Corridor Platform.

Provides:
 1. Ability to query information about registered objects
 2. Fetch datasets - raw or processed - which Corridor has access to
"""

from __future__ import annotations

import importlib
import typing as t
from pathlib import Path

from genguardx._internal.reports.templates import register_templates


_lazy_imports = {
    "genguardx._internal.data_tables": ("DataTable",),
    "genguardx._internal.helpers": ("read_data", "set_workspace"),
    "genguardx._internal.quality_check": ("QualityCheck",),
    "genguardx._internal.prompts": ("Prompt",),
    "genguardx._internal.models": ("Model",),
    "genguardx._internal.rags": ("Rag",),
    "genguardx._internal.pipelines": ("Pipeline",),
    "genguardx._internal.monitoring": ("Monitoring",),
    "genguardx._internal.attachments": ("Attachment",),
    "genguardx._internal.reports.templates": ("set_templates", "use_templates"),
    "genguardx._internal.resources": (
        "GlobalFunction",
        "Report",
        "ReportOutput",
        "DataLogicExample",
        "AdditionalReportFigure",
    ),
    "genguardx._internal.settings": ("CustomField", "PlatformSetting", "User"),
    "genguardx._internal.sync": ("sync",),
    "genguardx._internal": ("init", "whoami"),
}


def __getattr__(import_name: str) -> t.Any:  # noqa: ANN401 -- Can return any lazy loaded object
    for key, val in _lazy_imports.items():
        if import_name in val:
            class_module = importlib.import_module(key, __name__)
            return getattr(class_module, import_name)
    raise AttributeError(f"module {__name__!r} has no attribute {import_name!r}")


__all__ = ["register_templates", *list(sum(_lazy_imports.values(), ()))]  # noqa: PLE0604 -- `_lazy_imports.values()` returns list of strings


# Override the __dir__ to help with autocomplete
def __dir__() -> list[str]:
    return __all__


register_templates()
