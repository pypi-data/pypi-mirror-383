"""
Handles the corridor specific template for the visualization libraries we use in reporting.
NOTE: The color pallete being used here needs to be in sync with UI.
      `VIZ_COLOR_SCHEME` at `apps/corridor-ui/src/app/shared/constants/shared.constant.ts`
"""

from __future__ import annotations

import contextlib
import typing as t

import plotly.graph_objects as go
import plotly.io as pio


def register_templates() -> None:
    """Register all templates for all libraries"""
    PlotlyTemplate.register_template()
    MatplotlibTemplate.register_template()


def set_templates() -> None:
    """Set default templates in all libraries as the corridor template"""
    PlotlyTemplate.set_template()
    MatplotlibTemplate.set_template()


@contextlib.contextmanager
def use_templates() -> t.Iterable[None]:
    """Temporarily set the default templates in all libraries as the corridor template"""
    with PlotlyTemplate(), MatplotlibTemplate():
        yield


class BaseTemplate:
    @classmethod
    def register_template(cls) -> None:
        """
        Register the corridor template as a available template to the visualization library
        NOTE: This is only required if the library has a global list of all templates
        """

    @classmethod
    def set_template(cls) -> None:
        """Sets the default template as the corridor template"""
        raise NotImplementedError(f"Needs to be implemented by {cls}")

    def __enter__(self) -> None:
        """Context manager which uses the corridor template and then resets the value back on exiting"""
        raise NotImplementedError(f"Needs to be implemented by {type(self)}")

    def __exit__(self, *args, **kwargs) -> None:
        raise NotImplementedError(f"Needs to be implemented by {type(self)}")


class PlotlyTemplate(BaseTemplate):
    template = go.layout.Template(
        data_table=[
            go.Table(
                header={
                    "line": {"width": 1, "color": "#DDDFE1"},
                    "fill": {"color": "#f1f1f1"},
                    "font": {"size": 14, "color": "#2D3138"},
                    "align": "left",
                },
                cells={
                    "line": {"width": 0.5, "color": "#DDDFE1"},
                    "fill": {"color": "#fff"},
                    "font": {"size": 12, "color": "#2D3138"},
                    "height": 30,
                    "align": "left",
                },
                columnwidth=0.5,
            )
        ],
        layout=go.Layout(
            autotypenumbers="strict",
            height=450,
            colorway=["#1aaeba", "#f5b225", "#3E9651", "#6B4C9A", "#535154", "#948B3D"],
            margin={"autoexpand": True, "t": 60, "b": 50},
            font={"family": "Open Sans"},
            title={
                "font": {
                    "size": 18,
                    "family": "Open Sans",
                    "color": "#2D3138",
                },
            },
            xaxis={"zeroline": False, "showline": True, "automargin": True, "rangeslider": {"visible": True}},
            yaxis={
                "zeroline": False,
                "showline": True,
                "automargin": True,
            },
            updatemenudefaults={
                "pad": {"r": 10, "t": 15},
                "showactive": True,
                "active": 0,
                "y": 1.2,
                "x": 1,
                "xanchor": "left",
                "yanchor": "top",
            },
        ),
    )

    @classmethod
    def register_template(cls) -> None:
        """Register the corridor template as a available template to plotly"""
        pio.templates["corridor"] = cls.template

    @classmethod
    def set_template(cls) -> None:
        """Sets the default template as the corridor template"""
        pio.templates.default = "corridor"

    def __enter__(self) -> None:
        self.original_template = pio.templates.default
        self.set_template()

    def __exit__(self, *args, **kwargs) -> None:
        pio.templates.default = self.original_template


class MatplotlibTemplate(BaseTemplate):
    @classmethod
    def register_template(cls) -> None:
        # Matplotlib does not support multiple templates. So, there is no concept of registering a template
        return

    @classmethod
    def set_template(cls) -> None:
        try:
            import matplotlib as mpl
            import matplotlib.pyplot as plt
        except ImportError:  # matplotlib not installed - cannot set the template
            return

        template = {
            "figure.autolayout": True,
            "figure.facecolor": "white",
            "figure.figsize": (6, 3),
            "figure.subplot.hspace": 0.5,
            "figure.subplot.wspace": 0.5,
            "font.family": "Sans Serif",
            "axes.axisbelow": True,
            "axes.linewidth": 0.5,
            "axes.grid": True,
            "axes.grid.which": "both",
            "axes.grid.axis": "both",
            "axes.edgecolor": "#000000",
            "axes.prop_cycle": mpl.cycler(color=["#1aaeba", "#f5b225", "#3E9651", "#6B4C9A", "#535154", "#948B3D"]),
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.titlecolor": "#2D3138",
            "axes.titlesize": 18,
            "grid.linewidth": 0.5,
            "grid.color": "#DDDFE1",
            "lines.linewidth": 1.0,
            "xtick.major.width": 0.5,
            "ytick.major.width": 0.5,
            "xtick.minor.width": 0.5,
            "ytick.minor.width": 0.5,
            "xtick.color": "#2D3138",
            "ytick.color": "#2D3138",
            "legend.frameon": False,
            "legend.edgecolor": "inherit",
            "legend.fontsize": 12,
            "legend.title_fontsize": 14,
        }
        plt.rcParams.update(template)
        # NOTE: we use the same template for seaborn too

    def __enter__(self) -> None:
        self.set_template()

    def __exit__(self, *args, **kwargs) -> None:
        try:
            import matplotlib as mpl
        except ImportError:
            return

        # FIXME: We are using the default that matplotlib provides here
        #        But if the user had changed the value before calling this function - we will
        #        be reverting the user's changes.
        mpl.rcParams.update(mpl.rcParamsDefault)
