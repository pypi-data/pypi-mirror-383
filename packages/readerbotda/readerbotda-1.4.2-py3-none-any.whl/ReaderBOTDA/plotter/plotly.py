from .abc import Plotter

from typing import List

import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

from datetime import datetime
import numpy as np
import numpy.typing as npt


class Plotly(Plotter):

    def __init__(self, theme="ggplot2", colorscale: str = "YlGnBu") -> None:
        self.theme = theme
        self.colorscale = colorscale
        self.firstColor = pio.templates[self.theme].layout.colorway[0]
        super().__init__()
        pass

    def _applyTheme(self, fig) -> go.Figure:
        return fig.update_layout(
            template=self.theme,
            scene_xaxis=dict(separatethousands=False),
            scene_yaxis=dict(separatethousands=False),
        )

    def single_plot(self, position, profile, title: str = None) -> go.Figure:
        fig = go.Figure(
            data=go.Scatter(x=position, y=profile, name=title),
            layout=dict(
                title=title,
                xaxis=dict(title=dict(text="Position (m)")),
                yaxis=dict(title=dict(text="BFS (MHz)")),
            ),
        )
        return self._applyTheme(fig)

    def multiple_plot(
        self,
        position: np.ndarray,
        profiles: np.ndarray,
        timestamps: List[datetime],
        title: str = "",
    ) -> go.Figure:
        fig = go.Figure(
            layout=dict(
                title=title,
                xaxis=dict(title=dict(text="Position (m)")),
                yaxis=dict(title=dict(text="BFS (MHz)")),
            )
        )
        for i, time in enumerate(timestamps):
            fig.add_trace(
                go.Scatter(
                    x=position,
                    y=profiles[:, i],
                    mode="lines",
                    name=time.strftime("%m/%d/%Y, %H:%M:%S"),
                )
            )
        return self._applyTheme(fig)

    def statistics(
        self, position: np.ndarray, mean: np.ndarray, std: np.ndarray, title: str = ""
    ) -> go.Figure:

        fig = make_subplots(rows=2, cols=1, column_titles=[title])
        fig.add_trace(
            go.Scatter(
                x=position,
                y=mean,
                line=dict(color=self.firstColor),
                mode="lines",
                showlegend=False,
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                name="Upper Bound",
                x=position,
                y=mean + std,
                mode="lines",
                marker=dict(color="#444"),
                line=dict(width=0),
                showlegend=False,
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                name="Lower Bound",
                x=position,
                y=mean - std,
                marker=dict(color=self.firstColor),
                line=dict(width=0, color=self.firstColor),
                mode="lines",
                # fillcolor='rgba(68, 68, 68, 0.3)',
                fill="tonexty",
                showlegend=False,
            ),
            row=1,
            col=1,
        )

        fig.update_yaxes(title_text="BFS (MHz)", row=1, col=1)
        fig.update_layout(hovermode="x")

        fig.add_trace(
            go.Scatter(
                name="std",
                x=position,
                y=std,
                line=dict(color=self.firstColor),
                showlegend=False,
            ),
            row=2,
            col=1,
        )
        fig.update_yaxes(title_text="Std Dev (MHz)", range=[0, 10], row=2, col=1)
        fig.update_xaxes(title_text="Position (m)", matches="x", row=2, col=1)
        return self._applyTheme(fig)

    def max_stat_plot(
        self, max_mean: np.ndarray, max_std: np.ndarray, title: str = ""
    ) -> go.Figure:

        fig = go.Figure(layout=dict(title=title))
        fig.add_trace(
            go.Scatter(
                y=max_mean,
                line=dict(color=self.firstColor),
                mode="lines",
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                name="Upper Bound",
                y=max_mean + max_std,
                mode="lines",
                marker=dict(color="#444"),
                line=dict(width=0),
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                name="Lower Bound",
                y=max_mean - max_std,
                marker=dict(color=self.firstColor),
                line=dict(width=0, color=self.firstColor),
                mode="lines",
                # fillcolor='rgba(68, 68, 68, 0.3)',
                fill="tonexty",
                showlegend=False,
            )
        )

        fig.update_yaxes(title_text="Max BGS (Volts)")

        return self._applyTheme(fig)

    def raw2d_plot(self, position, frequency, BGS, title: str = None) -> go.Figure:
        fig = go.Figure(
            data=go.Contour(
                z=BGS,
                x=position,
                y=frequency,
                showscale=False,
                colorscale=self.colorscale,
                line_width=0,
            ),
            layout=dict(
                title=title,
                xaxis=dict(title=dict(text="Position (m)")),
                yaxis=dict(title=dict(text="Frequency (GHz)")),
            ),
        )
        return self._applyTheme(fig)

    def raw3d_plot(self, position, frequency, BGS, title: str = None):
        hovertemplate = "Pos: %{x:.2f} m, Freq: %{y:.3f} GHz, Ampl: %{z:.3f} V"
        fig = go.Figure(
            data=go.Surface(
                z=BGS, x=position, y=frequency, hovertemplate=hovertemplate
            ),
            layout=dict(
                title=title,
                scene=dict(
                    xaxis_title="Position (m)",
                    yaxis_title="Frequency (GHz)",
                    zaxis_title="Amplitude (V)",
                ),
            ),
        )
        return self._applyTheme(fig)

    def rawBGS_plot(
        self,
        frequency,
        BGS,
        positions_m: npt.ArrayLike,
        index: int = None,
        title: str = None,
    ) -> go.Figure:
        fig = go.Figure(
            layout=dict(
                title=title,
                # hovermode=False,
                xaxis=dict(title=dict(text="Frequency (GHz)")),
                yaxis=dict(title=dict(text="Amplitude (V)")),
            )
        )
        if not index:
            for single in np.transpose(BGS):
                fig.add_trace(
                    go.Scatter(x=frequency, y=single, mode="lines", showlegend=False)
                )
        else:
            for single in np.transpose(BGS):
                fig.add_trace(
                    go.Scatter(
                        x=frequency,
                        y=single,
                        line=dict(color="rgba(175,175,175,0.15)"),
                        mode="lines",
                        showlegend=False,
                        hovertext=[
                            f"Position: {positions_m[i]:.2f} m"
                            for _ in range(len(frequency))
                        ],
                        hoverinfo="text",
                    )
                )
            fig.add_trace(
                go.Scatter(
                    x=frequency,
                    y=BGS[:, index],
                    line=dict(color=self.firstColor),
                    mode="lines",
                    showlegend=False,
                    hovertext=[
                        f"Position: {positions_m[index]:.2f} m"
                        for _ in range(len(frequency))
                    ],
                    hoverinfo="text",
                )
            )
        return self._applyTheme(fig)

    def max_plot(self, position, max, title: str = None) -> go.Figure:
        fig = go.Figure(
            data=go.Scatter(x=position, y=max, name=title),
            layout=dict(
                title=title,
                xaxis=dict(title=dict(text="Position (m)")),
                yaxis=dict(title=dict(text="Max BGS Amplitude")),
            ),
        )
        return self._applyTheme(fig)

    @staticmethod
    def show(fig: go.Figure) -> None:
        fig.show()
        pass
