from __future__ import annotations

import typing as t

import genguardx as ggx
from genguardx import _get_version


if t.TYPE_CHECKING:
    import pytest_mock


def test_module_init() -> None:
    assert set(dir(ggx)) == {
        "CustomField",
        "DataTable",
        "GlobalFunction",
        "PlatformSetting",
        "QualityCheck",
        "Report",
        "User",
        "Attachment",
        "Rag",
        "Prompt",
        "Pipeline",
        "Model",
        "read_data",
        "register_templates",
        "set_templates",
        "set_workspace",
        "use_templates",
        "ReportOutput",
        "sync",
    }


def test_get_version_no_version_file(mocker: pytest_mock.MockerFixture) -> None:
    mocker.patch("pathlib.Path.open", side_effect=OSError("No such file or directory"))
    assert _get_version() == "0.0.0"
