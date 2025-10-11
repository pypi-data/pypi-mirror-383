# Third-party
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def _compute_square_layout(
    width_per_panel: int,
    ncols: int,
    spacing_frac: float,
    margins: tuple[int, int, int, int],
) -> tuple[int, int, dict]:
    """Computes figure dimensions for square panels."""
    ml, mr, mt, mb = margins
    denom = max(1.0 - (ncols - 1) * spacing_frac, 1e-6)
    plot_area_width = ncols * width_per_panel / denom
    fig_width = int(round(plot_area_width + ml + mr))
    fig_height = int(round(width_per_panel + mt + mb))
    return fig_width, fig_height, {"l": ml, "r": mr, "t": mt, "b": mb}


def _scale_sizes(raw: pd.Series, min_px: int = 6, max_px: int = 24) -> pd.Series:
    """Scales a numeric series to a pixel range for marker sizes."""
    s = pd.to_numeric(raw, errors="coerce")
    if s.isna().all():
        return pd.Series(min_px, index=s.index)
    s = s.fillna(s.min())
    lo, hi = s.min(), s.max()
    if hi == lo:
        return pd.Series(int((min_px + max_px) / 2), index=s.index)
    scaled = (s - lo) / (hi - lo)
    return (min_px + scaled * (max_px - min_px)).astype(int)


def _get_axis_range(
    series: pd.Series, margin_frac: float = 0.05
) -> list[float, float] | None:
    """Calculates axis range with a given margin."""
    if series.empty or series.isna().all():
        return None
    min_val, max_val = series.min(), series.max()
    if min_val == max_val:
        return [min_val - 1, max_val + 1]
    margin = (max_val - min_val) * margin_frac
    return [min_val - margin, max_val + margin]


def _scatter_plot_plotly(
    df: pd.DataFrame,
    x1: str,
    y1: str,
    x2: str | None = None,
    y2: str | None = None,
    xlabel1: str | None = None,
    ylabel1: str | None = None,
    xlabel2: str | None = None,
    ylabel2: str | None = None,
    size: str | None = None,
    style: str | None = None,
    hue: str | None = None,
    alpha: str | None = None,
    hover_cols: list[str] | None = None,
    annotate_dots: bool = False,
    title: str = "Interactive Scatter (Square Panels)",
    panel_pixels: int = 520,
    margins: tuple[int, int, int, int] = (60, 60, 80, 60),
    horizontal_spacing: float = 0.08,
    fig: go.Figure | None = None,
) -> go.Figure:
    """
    Builds a 1 or 2-panel Plotly scatter plot with advanced styling and interactivity.
    """
    # Constants
    default_marker_size_px = 8
    default_alpha = 1.0
    default_symbol_cycle = [
        "circle",
        "square",
        "diamond",
        "cross",
        "x",
        "triangle-up",
        "star",
        "hexagon",
        "triangle-down",
        "pentagon",
    ]
    default_legend_marker_size = 12
    min_size_px = 6
    max_size_px = 24

    two_panels = x2 is not None and y2 is not None
    ncols = 2 if two_panels else 1

    # --- 1. Process Styling Inputs ---
    size_px = (
        _scale_sizes(df[size], min_size_px, max_size_px)
        if size
        else pd.Series(default_marker_size_px, index=df.index)
    )
    alpha_vals = (
        df[alpha].clip(0, 1) if alpha else pd.Series(default_alpha, index=df.index)
    )

    if style:
        style_vals = df[style]
        style_levels = list(pd.unique(style_vals))
        symbol_map = {
            lvl: default_symbol_cycle[i % len(default_symbol_cycle)]
            for i, lvl in enumerate(style_levels)
        }
    else:
        style_vals = pd.Series("circle", index=df.index)
        style_levels = []

    if hue:
        hue_vals = df[hue]
        hue_levels = list(pd.unique(hue_vals))
        qualitative = px.colors.qualitative.Plotly
        color_map = {
            lvl: qualitative[i % len(qualitative)] for i, lvl in enumerate(hue_levels)
        }
    else:
        hue_vals = pd.Series("_", index=df.index)
        hue_levels = ["_"]
        color_map = {"_": "#636EFA"}

    # --- 2. Pre-calculate fixed axis ranges ---
    x1_range = _get_axis_range(df[x1])
    y1_range = _get_axis_range(df[y1])
    x2_range = _get_axis_range(df[x2]) if two_panels else None
    y2_range = _get_axis_range(df[y2]) if two_panels else None

    # --- 3. Setup Figure and Layout ---
    if fig is not None:
        # Validate existing figure
        if not hasattr(fig, "data"):
            raise ValueError("Provided fig must be a plotly Figure object")

        # Check if figure has the expected subplot structure
        expected_cols = 2 if two_panels else 1
        if hasattr(fig, "_grid_ref") and fig._grid_ref:
            actual_cols = len(fig._grid_ref[0]) if fig._grid_ref else 1
            if actual_cols != expected_cols:
                raise ValueError(
                    f"Expected {expected_cols} subplot(s), got {actual_cols}"
                )
    else:
        # Create new figure
        fig_width, fig_height, margin_dict = _compute_square_layout(
            width_per_panel=panel_pixels,
            ncols=ncols,
            spacing_frac=horizontal_spacing,
            margins=margins,
        )
        fig = make_subplots(rows=1, cols=ncols, horizontal_spacing=horizontal_spacing)

    # --- 4. Add Data Traces (one per hue category for interactivity) ---
    for i, h_level in enumerate(hue_levels):
        subset_mask = hue_vals == h_level
        subset_df = df.loc[subset_mask]
        if subset_df.empty:
            continue

        marker_symbol = (
            style_vals.loc[subset_mask].map(symbol_map) if style else "circle"
        )
        customdata = subset_df[hover_cols].to_numpy() if hover_cols else None
        hovertemplate = (
            "<br>".join(
                [f"{col}: %{{customdata[{i}]}}" for i, col in enumerate(hover_cols)]
            )
            + "<extra></extra>"
            if hover_cols
            else None
        )

        trace_props = {
            "mode": "markers+text" if annotate_dots else "markers",
            "name": str(h_level) if hue else "Data",
            "legendgroup": str(h_level),
            "marker": {
                "color": color_map[h_level],
                "opacity": alpha_vals.loc[subset_mask].tolist(),
                "symbol": marker_symbol.tolist() if style else "circle",
                "size": size_px.loc[subset_mask].tolist(),
                "line": {"width": 0},
            },
            "textfont": {"color": color_map[h_level]},
            "text": subset_df.index.astype(str) if annotate_dots else None,
            "textposition": "top center",
            "customdata": customdata,
            "hovertemplate": hovertemplate,
        }

        if i == 0 and hue:
            trace_props["legendgrouptitle_text"] = hue

        fig.add_trace(
            go.Scatter(x=subset_df[x1], y=subset_df[y1], **trace_props), row=1, col=1
        )

        if two_panels:
            fig.add_trace(
                go.Scatter(
                    x=subset_df[x2], y=subset_df[y2], showlegend=False, **trace_props
                ),
                row=1,
                col=2,
            )

    # --- 5. Add Dummy Traces for Non-Interactive Style Legend (Refactored) ---
    if style:
        for i, s_level in enumerate(style_levels):
            trace_props = {
                "x": [None],
                "y": [None],
                "mode": "markers",
                "name": str(s_level),
                "legendgroup": "STYLE",
                "marker": dict(
                    color="rgba(80,80,80,1)",
                    symbol=symbol_map[s_level],
                    size=default_legend_marker_size,
                ),
                "hoverinfo": "skip",
            }
            if i == 0 and style:
                trace_props["legendgrouptitle_text"] = style

            fig.add_trace(go.Scatter(**trace_props))

    # --- 6. Finalize Layout, Axes, and Legend ---
    # Check if we created the figure (no existing grid reference) or if it was provided
    created_new_figure = not hasattr(fig, "_grid_ref") or fig._grid_ref is None

    if created_new_figure:
        fig_width, fig_height, margin_dict = _compute_square_layout(
            width_per_panel=panel_pixels,
            ncols=ncols,
            spacing_frac=horizontal_spacing,
            margins=margins,
        )
        fig.update_layout(
            title=title,
            width=fig_width,
            height=fig_height,
            margin=margin_dict,
            legend=dict(orientation="v", tracegroupgap=5),
            template="plotly_white",
        )
    else:  # Existing figure provided
        fig.update_layout(
            title=title,
            legend=dict(orientation="v", tracegroupgap=5),
        )

    fig.update_xaxes(
        title_text=xlabel1 or x1, range=x1_range, fixedrange=True, row=1, col=1
    )
    fig.update_yaxes(
        title_text=ylabel1 or y1,
        range=y1_range,
        fixedrange=True,
        row=1,
        col=1,
        scaleanchor="x1",
        scaleratio=1,
    )
    if two_panels:
        fig.update_xaxes(
            title_text=xlabel2 or x2, range=x2_range, fixedrange=True, row=1, col=2
        )
        fig.update_yaxes(
            title_text=ylabel2 or y2,
            range=y2_range,
            fixedrange=True,
            row=1,
            col=2,
            scaleanchor="x2",
            scaleratio=1,
        )

    return fig
