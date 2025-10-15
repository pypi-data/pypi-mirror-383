from .abc import Plotter

from bokeh.plotting import figure
from bokeh.models.layouts import Column
from bokeh.plotting.figure import Figure as bokehFigure
from bokeh.plotting import show as bokehShow
from bokeh.models import Legend
from bokeh.layouts import gridplot
from bokeh.palettes import Bokeh8
from bokeh.io import curdoc

import numpy as np
import numpy.typing as npt


class Bokeh(Plotter):
    def __init__(self, theme: str = "caliber"):
        curdoc().theme = theme
        # TODO: capire come prendere la palette del tema scelto, invece che usare sempre Bokeh8.
        self.palette = Bokeh8

    def single_plot(self, position, profile, title: str = None) -> bokehFigure:
        fig = figure(
            title=title,
            x_axis_label="Position (m)",
            y_axis_label="BFS (MHz)",
            sizing_mode="stretch_width",
        )
        fig.line(position, profile)
        return fig

    def multiple_plot(
        self, position, profiles, timestamps, title: str = ""
    ) -> bokehFigure:
        fig = figure(
            title=title,
            x_axis_label="Position (m)",
            y_axis_label="BFS (MHz)",
            sizing_mode="stretch_width",
        )
        fig.add_layout(Legend(), "right")
        for i, (time, color) in enumerate(zip(timestamps, self.palette)):
            fig.line(
                x=position,
                y=profiles[:, i],
                color=color,
                legend_label=time.strftime("%m/%d/%Y, %H:%M:%S"),
            )
        return fig

    def statistics(
        self, position, mean: np.ndarray, std: np.ndarray, title: str = ""
    ) -> Column:
        f1 = figure(title=title, y_axis_label="Mean BFS (MHz)")
        f1.line(x=position, y=mean)
        f1.varea(x=position, y1=mean + std, y2=mean - std, fill_alpha=0.3)
        f2 = figure(
            x_axis_label="Position (m)", y_axis_label="Std Dev (MHz)", y_range=(0, 10)
        )
        f2.line(x=position, y=std)
        return gridplot([f1, f2], ncols=1, height=150, sizing_mode="stretch_width")

    def max_plot(self, position, max, title: str = None) -> bokehFigure:
        fig = figure(
            title=title,
            x_axis_label="Position (m)",
            y_axis_label="Max BGS Amplitude",
            sizing_mode="stretch_width",
        )
        fig.line(x=position, y=max)
        return fig

    def max_stat_plot(
        self, max_mean: np.ndarray, max_std: np.ndarray, title: str = ""
    ) -> bokehFigure:
        fig = figure(
            title=title, y_axis_label="Max BGS (Volts)", sizing_mode="stretch_width"
        )
        fig.line(y=max_mean)
        fig.varea(y1=max_mean + max_std, y2=max_mean - max_std, fill_alpha=0.3)
        return fig

    def rawBGS_plot(
        self,
        frequency,
        BGS,
        positions_m: npt.ArrayLike = None,
        index: int = None,
        title: str = None,
    ) -> bokehFigure:
        fig = figure(
            title=title,
            x_axis_label="Frequency (GHz)",
            y_axis_label="Amplitude (V)",
            sizing_mode="stretch_width",
        )
        if not index:
            for single in np.transpose(BGS):
                fig.line(x=frequency, y=single)
        else:
            for single in np.transpose(BGS):
                fig.line(x=frequency, y=single, color="rgba(175,175,175,0.15)")
            fig.line(x=frequency, y=BGS[:, index])
        return fig

    def raw3d_plot(self, position, frequency, BGS, title: str = None):
        raise NameError("Function raw3d_plot not yet defined for Bokeh plotter.")

    def raw2d_plot(self, position, frequency, BGS, title: str = None):
        raise NameError("Function raw2d_plot not yet defined for Bokeh plotter.")

    @staticmethod
    def show(fig) -> None:
        bokehShow(fig)
        pass
