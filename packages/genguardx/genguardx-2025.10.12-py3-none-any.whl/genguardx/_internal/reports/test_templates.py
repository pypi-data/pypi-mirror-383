from __future__ import annotations

import typing as t
from contextlib import nullcontext as does_not_raise

import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.io as pio
import pytest

from genguardx._internal.reports.templates import BaseTemplate, MatplotlibTemplate, PlotlyTemplate, use_templates


if t.TYPE_CHECKING:
    import pytest_mock


class TestBaseTemplate:
    def test_set_template_undefined(self) -> None:
        with pytest.raises(NotImplementedError, match="Needs to be implemented"):
            BaseTemplate.set_template()

    def test_ctx_manager_enter_undefined(self) -> None:
        with pytest.raises(NotImplementedError, match="Needs to be implemented"):
            BaseTemplate().__enter__()

    def test_ctx_manager_exit_undefined(self) -> None:
        with pytest.raises(NotImplementedError, match="Needs to be implemented"):
            BaseTemplate().__exit__()


class TestPlotlyTemplate:
    def test_plotly_template_ctx_manager(self) -> None:
        PlotlyTemplate.register_template()

        original_template = pio.templates.default
        assert original_template != "corridor"
        with PlotlyTemplate():
            assert pio.templates.default == "corridor"
        assert pio.templates.default != "corridor"

    def test_use_templates_plotly(self) -> None:
        PlotlyTemplate.register_template()

        original_template = pio.templates.default
        assert original_template != "corridor"
        with use_templates():
            assert pio.templates.default == "corridor"
        assert pio.templates.default != "corridor"


class TestMatplotlibTemplate:
    def test_mpl_set_template_mpl_not_installed(self, mocker: pytest_mock.MockerFixture) -> None:
        MatplotlibTemplate.register_template()
        mocker.patch.dict("sys.modules", {"matplotlib": None})

        with does_not_raise():
            MatplotlibTemplate.set_template()

    def test_mpl_set_template_ctx_manager_mpl_not_installed(self, mocker: pytest_mock.MockerFixture) -> None:
        MatplotlibTemplate.register_template()
        mocker.patch.dict("sys.modules", {"matplotlib": None})

        # Should not throw error
        with MatplotlibTemplate():
            pass

    def test_mpl_template_ctx_manager(self) -> None:
        MatplotlibTemplate.register_template()

        assert plt.rcParams == mpl.rcParamsDefault
        with MatplotlibTemplate():
            assert plt.rcParams != mpl.rcParamsDefault
        assert plt.rcParams == mpl.rcParamsDefault

    def test_use_templates_mpl(self) -> None:
        MatplotlibTemplate.register_template()

        assert plt.rcParams == mpl.rcParamsDefault
        with use_templates():
            assert plt.rcParams != mpl.rcParamsDefault
        assert plt.rcParams == mpl.rcParamsDefault
