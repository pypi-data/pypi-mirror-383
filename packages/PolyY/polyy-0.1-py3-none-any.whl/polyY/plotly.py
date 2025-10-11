import plotly.graph_objects as go

class MakeFigure:
    """
    A robust wrapper for creating multi Y-axis charts in Plotly.
    Each trace gets its own Y-axis with matching color, automatically spaced.
    
    Built by : Nashat Jumaah Omar ,  2025
    """

    def __init__(self, title: str = "Multi Y-Axis Chart", template="plotly_dark"):
        self.fig = go.Figure()
        self.traces = []
        self.title = title
        self.fig.update_layout(template=template)

    def show(self):
        self._apply_layout()
        self.fig.show()

    def get_figure(self):
        self._apply_layout()
        return self.fig

    def add_trace(self, x, y, name: str, kind: str = "line", color: str = None, **kwargs):
        axis_id = len(self.traces) + 1
        yaxis_name = f"y{axis_id if axis_id > 1 else ''}"
        kind = kind.lower()

        if kind in ["line", "scatter", "step", "area"]:
            line_style = kwargs.pop("line", {})
            if color:
                line_style["color"] = color
            if kind == "step":
                line_style["shape"] = "hv"
            mode = "lines"
            if kind == "scatter":
                 mode="markers"
            

            fill = "tozeroy" if kind == "area" else None
            trace = go.Scatter(x=x, y=y, name=name, yaxis=yaxis_name,
                               mode=mode, fill=fill, line=line_style, **kwargs)
        elif kind == "bar":
            marker = kwargs.pop("marker", {})
            if color:
                marker["color"] = color
            trace = go.Bar(x=x, y=y, name=name, yaxis=yaxis_name, marker=marker, **kwargs)
        else:
            raise ValueError(f"Unsupported chart kind: {kind}")

        self.traces.append((trace, color))
        self.fig.add_trace(trace)

    def _apply_layout(self):
        n_axes = len(self.traces)
        if n_axes == 0:
            return

        # Adjust x-axis domain to leave space for right axes
        domain_right = max(0.90 - 0.05 * (n_axes - 1), 0.5)
        self.fig.update_xaxes(domain=[0, domain_right])

        n_right = n_axes - 1
        step = (1 - domain_right) / max(n_right, 1) if n_right > 0 else 0

        for i, (trace, color) in enumerate(self.traces, start=1):
            yaxis_name = f"yaxis{i if i > 1 else ''}"

            axis_dict = dict(
                title=trace.name,
                titlefont=dict(color=color, size=11),
                tickfont=dict(color=color, size=10),
                showline=True,
                linecolor=color,
                zeroline=False,
                ticks="outside",
                showgrid=(i == 1),
            )

            if i == 1:
                axis_dict["side"] = "left"
            else:
                position = domain_right + (i - 2) * step
                axis_dict.update(
                    side="right",
                    overlaying="y",
                    position=position,
                    showgrid=False,
                )
                

            # Directly assign axis in layout
            self.fig.layout[yaxis_name] = axis_dict

        # Hide legend
        self.fig.update_layout(showlegend=False)

        # General layout
        self.fig.update_layout(
            title=self.title,
            margin=dict(l=80, r=80, t=50, b=40),
        )
