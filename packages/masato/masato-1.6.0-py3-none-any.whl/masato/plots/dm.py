import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from skbio.diversity import beta_diversity
from skbio.stats.ordination import pcoa
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import seaborn as sns
import plotly.graph_objects as go

from .dm_plotly import _scatter_plot_plotly


def dm(
    df_otu_count: pd.DataFrame,
    df_meta: pd.DataFrame,
    distance: str = "braycurtis",
) -> tuple[pd.DataFrame, np.ndarray]:
    n_components = min(10, *df_otu_count.shape)
    n_pcs = min(3, n_components)
    if n_components == 1:
        raise ValueError(
            f"Minimum dimensionality of input data is 2, getting {n_components}."
        )

    if distance == "braycurtis":
        bd = beta_diversity("braycurtis", df_otu_count)
        dist_mtx = np.nan_to_num(bd.data, 0)
        pc_obj = pcoa(dist_mtx, number_of_dimensions=n_components)
        pc = pc_obj.samples.copy()
        pc.index = df_otu_count.index
        variance = pc_obj.proportion_explained.to_numpy()
    elif distance == "euclid":
        pc_obj = PCA(n_components=n_components).fit(df_otu_count)
        pc = pc_obj.transform(df_otu_count)
        pc = pd.DataFrame(
            pc,
            index=df_otu_count.index,
            columns=[f"PC{i}" for i in range(1, pc.shape[1] + 1)],
        )
        variance = pc_obj.explained_variance_ratio_
    else:
        raise NotImplementedError(f"Unsupported distance metric: {distance}")

    if n_pcs == 2:
        pc["PC3"] = 0
        variance = np.append(variance, 0)

    pc = pd.concat([pc, df_meta], axis=1)
    return pc, variance


def eigsorted(cov: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    return vals[order], vecs[:, order]


def _scatter_plot_matplotlib(
    data: pd.DataFrame,
    x1: str,
    y1: str,
    xlabel1: str,
    ylabel1: str,
    *,
    x2: str | None = None,
    y2: str | None = None,
    xlabel2: str | None = None,
    ylabel2: str | None = None,
    s: int | None = 50,
    alpha: float | None = None,
    title: str | None = None,
    annotate_dots: bool = False,
    plot_ellipses: bool = False,
    hue: str | None = None,
    hue_order: list[str] | None = None,
    hue_dict: str | dict | None = None,
    style: str | None = None,
    style_order: list[str] | None = None,
    style_dict: dict[str] | bool = True,
    fig: matplotlib.figure.Figure | None = None,
    axs: list[matplotlib.axes.Axes] | matplotlib.axes.Axes | None = None,
) -> tuple[matplotlib.figure.Figure, list[matplotlib.axes.Axes]]:
    """Plot ordination scatter(s) from prepared data.

    Args:
        data: DataFrame containing x1, y1 columns (and x2, y2 if two-panel plot), plus any metadata columns.
        x1: Column name for x-axis of first/left panel.
        y1: Column name for y-axis of first/left panel.
        xlabel1: Label for x-axis of first/left panel.
        ylabel1: Label for y-axis of first/left panel.
        x2: Column name for x-axis of second/right panel (None for single panel).
        y2: Column name for y-axis of second/right panel (None for single panel).
        xlabel2: Label for x-axis of second/right panel (None for single panel).
        ylabel2: Label for y-axis of second/right panel (None for single panel).
        s: Marker size for points.
        alpha: Passed directly to seaborn.scatterplot. (You accept responsibility for validity.)
        title: Optional figure suptitle.
        annotate_dots: If True, annotate each point with its index string.
        plot_ellipses: If True, draw 2σ covariance ellipses for each hue group (if `hue` is provided).
        hue: Column name for color grouping (or None).
        hue_order: Explicit order for hue levels (or None to infer).
        hue_dict: Palette spec for seaborn: palette name (str) or dict {level: color}.
        style: Column name for marker styles (or None).
        style_order: Explicit order for style levels (or None to infer).
        style_dict: True for seaborn defaults, or dict {level: marker}.
        fig: Optional target Figure to draw on.
        axs: Optional target Axes (single or list). Must match expected number of panels.

    Returns:
        (fig, axs): Matplotlib Figure and list of Axes.
    """
    # Constants
    axis_label_fontsize = 14
    suptitle_fontsize = 16
    legend_marker_size = 8

    # Determine if we have two panels
    plot_two_panels = x2 is not None and y2 is not None

    # Infer style/hue order if needed
    if style is not None and style_order is None:
        style_order = sorted(pd.unique(data[style]).tolist())
    if hue is not None and hue_order is None:
        hue_order = sorted(pd.unique(data[hue]).tolist())

    # Prepare figure/axes
    if fig is None or axs is None:
        if plot_two_panels:
            fig, axs = plt.subplots(1, 2, figsize=(8, 3.5))
        else:
            fig, ax = plt.subplots(1, 1, figsize=(5.5, 4))
            axs = [ax]
    else:
        expected = 2 if plot_two_panels else 1
        if isinstance(axs, matplotlib.axes.Axes):
            axs = [axs]
        if len(axs) != expected:
            raise ValueError(f"Expected {expected} axes, got {len(axs)}.")

    # Determine if we have array-like values for size/alpha (affects legend handling)
    has_array_s = hasattr(s, "__len__") and not isinstance(s, (str, int, type(None)))
    has_array_alpha = hasattr(alpha, "__len__") and not isinstance(
        alpha, (str, float, type(None))
    )
    disable_auto_legend = has_array_s or has_array_alpha

    # Left panel: first scatter plot
    sns.scatterplot(
        data=data,
        x=x1,
        y=y1,
        hue=hue,
        hue_order=hue_order,
        palette=hue_dict,
        style=style,
        style_order=style_order,
        markers=style_dict,
        linewidth=0,
        s=s,
        alpha=alpha,
        legend=False if disable_auto_legend else not plot_two_panels,
        ax=axs[0],
    )
    axs[0].set_xlabel(xlabel1, fontsize=axis_label_fontsize)
    axs[0].set_ylabel(ylabel1, fontsize=axis_label_fontsize)

    # Right panel: second scatter plot (if requested)
    if plot_two_panels:
        sns.scatterplot(
            data=data,
            x=x2,
            y=y2,
            hue=hue,
            hue_order=hue_order,
            palette=hue_dict,
            style=style,
            style_order=style_order,
            markers=style_dict,
            linewidth=0,
            s=s,
            alpha=alpha,
            legend=False if disable_auto_legend else True,
            ax=axs[1],
        )
        axs[1].set_xlabel(xlabel2, fontsize=axis_label_fontsize)
        axs[1].set_ylabel(ylabel2, fontsize=axis_label_fontsize)

    # Make axes visually square
    for ax in axs:
        xleft, xright = ax.get_xlim()
        ybottom, ytop = ax.get_ylim()
        ax.set_aspect(abs((xright - xleft) / (ybottom - ytop)), adjustable="box")

    # Place legend (if any) on the last axis, outside to the right
    legend_ax = axs[-1]
    if hue is not None and not disable_auto_legend:
        handles, labels = legend_ax.get_legend_handles_labels()
        hues = data[hue].unique().tolist()
        for h, label in zip(handles, labels):
            if label in hues:
                h.set_marker("o")
            h.set_markersize(legend_marker_size)
        legend_ax.legend(
            handles,
            labels,
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
            borderaxespad=0.0,
        )
    elif hue is not None and disable_auto_legend:
        # Create manual legend when auto legend is disabled due to array values
        import matplotlib.patches as mpatches

        hues = data[hue].unique().tolist()
        n_hues = len(hues)
        palette = (
            sns.color_palette(hue_dict, n_hues)
            if isinstance(hue_dict, str)
            else (
                list(hue_dict.values())
                if isinstance(hue_dict, dict)
                else sns.color_palette(n_colors=n_hues)
            )
        )
        patches = []
        for hue_val, color in zip(hues, palette):
            patches.append(mpatches.Patch(color=color, label=str(hue_val)))
        legend_ax.legend(
            handles=patches,
            bbox_to_anchor=(1.05, 1),
            loc="upper left",
            borderaxespad=0.0,
        )

    # Optional annotations
    if annotate_dots:
        for i, label in enumerate(data.index.astype(str)):
            axs[0].annotate(
                label, (data[x1].iloc[i], data[y1].iloc[i]), fontsize=6, alpha=0.4
            )
            if plot_two_panels and x2 in data and y2 in data:
                axs[1].annotate(
                    label, (data[x2].iloc[i], data[y2].iloc[i]), fontsize=6, alpha=0.4
                )

    # Optional 2σ covariance ellipses per hue group
    if plot_ellipses:
        if plot_two_panels:
            dims_list = [(x1, y1), (x2, y2)]
            ax_list = axs
        else:
            dims_list = [(x1, y1)]
            ax_list = [axs[0]]

        n_hues = len(hue_order)
        palette = (
            sns.color_palette(hue_dict, n_hues)
            if isinstance(hue_dict, str)
            else (
                list(hue_dict.values())
                if isinstance(hue_dict, dict)
                else sns.color_palette(n_colors=n_hues)
            )
        )
        hue_to_color = dict(zip(hue_order, palette))

        for dims, ax in zip(dims_list, ax_list):
            for group in hue_order:
                group_data = data.loc[data[hue] == group]
                x = group_data[dims[0]]
                y = group_data[dims[1]]
                if len(x) < 2:
                    continue

                mean_x, mean_y = x.mean(), y.mean()
                cov = np.cov(x, y)
                lambda_, v = eigsorted(cov)
                theta = np.degrees(np.arctan2(*v[:, 0][::-1]))
                w, h = 4 * np.sqrt(lambda_)  # 2 * std_dev
                ell = Ellipse(
                    xy=(mean_x, mean_y), width=w, height=h, angle=theta, alpha=0.2
                )
                ell.set_facecolor(hue_to_color[group])
                ell.set_edgecolor("grey")
                ax.add_artist(ell)

    if title:
        fig.suptitle(title, fontsize=suptitle_fontsize)
    fig.tight_layout()
    if title:
        fig.subplots_adjust(top=0.88)

    return fig, axs


def plot_dm(
    df_otu_count: pd.DataFrame,
    df_meta: pd.DataFrame,
    distance: str = "braycurtis",
    backend: str = "plt",
    title: str | None = None,
    hue: str | None = None,
    hue_order: list[str] | None = None,
    hue_dict: str | dict | None = None,
    style: str | None = None,
    style_order: list[str] | None = None,
    style_dict: dict[str] | bool = True,
    s: int | str | None = 50,
    alpha: float | str | None = None,
    annotate_dots: bool = False,
    plot_ellipses: bool = False,
    plot_pc3: bool = True,
    hover_cols: list[str] | None = None,
    fig: matplotlib.figure.Figure | go.Figure | None = None,
    axs: list[matplotlib.axes.Axes] | matplotlib.axes.Axes | None = None,
) -> go.Figure | tuple[matplotlib.figure.Figure, list[matplotlib.axes.Axes]]:
    """Entry point: compute ordination via `dm(...)` and plot via matplotlib or plotly backend.

    Args:
        df_otu_count: Samples x features table.
        df_meta: Metadata (index aligned to df_otu_count).
        distance: "braycurtis" (PCoA via scikit-bio) or "euclid" (PCA).
        backend: "plt" for matplotlib or "plotly" for plotly backend.
        title: Optional figure title.
        hue: Column name for color grouping (or None).
        hue_order: Explicit order for hue levels.
        hue_dict: Palette spec for seaborn/plotly (name or dict).
        style: Column name for marker styles (or None).
        style_order: Explicit order for style levels.
        style_dict: True or dict {level: marker}.
        s: Marker size (int for matplotlib) or column name (str for plotly).
        alpha: Transparency value (float for matplotlib) or column name (str for plotly).
        annotate_dots: If True, annotate each point with its index.
        plot_ellipses: If True, draw 2σ ellipses per hue group (matplotlib only).
        plot_pc3: If True, add a PC2-PC3 panel.
        hover_cols: Additional columns for hover info (plotly only).
        fig: Optional target Figure (matplotlib Figure or plotly Figure).
        axs: Optional target Axes (matplotlib only).

    Returns:
        For matplotlib: (fig, axs)
        For plotly: fig
    """
    pc, variance = dm(df_otu_count=df_otu_count, df_meta=df_meta, distance=distance)

    # Validate backend
    if backend not in ["plt", "plotly"]:
        raise ValueError(f"Backend must be 'plt' or 'plotly', got '{backend}'")

    # Handle backend-specific compatibility issues
    if backend == "plotly":
        # Warn about unsupported features for plotly
        if plot_ellipses:
            import warnings

            warnings.warn(
                "plot_ellipses is not supported with plotly backend, ignoring.",
                UserWarning,
            )
            plot_ellipses = False

        if axs is not None:
            import warnings

            warnings.warn("axs parameter is ignored with plotly backend.", UserWarning)

    elif backend == "plt":
        # Warn about unsupported features for matplotlib
        if hover_cols is not None:
            import warnings

            warnings.warn(
                "hover_cols is only supported with plotly backend, ignoring.",
                UserWarning,
            )

    # Determine if we should plot two panels
    plot_two_panels = plot_pc3

    # Prepare labels
    xlabel1 = f"PC1 ({variance[0] * 100:.2f}%)"
    ylabel1 = f"PC2 ({variance[1] * 100:.2f}%)"

    if plot_two_panels:
        xlabel2 = f"PC2 ({variance[1] * 100:.2f}%)"
        ylabel2 = f"PC3 ({variance[2] * 100:.2f}%)"
        x2, y2 = "PC2", "PC3"
    else:
        xlabel2 = ylabel2 = x2 = y2 = None

    # Call the appropriate backend function
    if backend == "plotly":
        fig = _scatter_plot_plotly(
            df=pc,
            x1="PC1",
            y1="PC2",
            x2=x2,
            y2=y2,
            xlabel1=xlabel1,
            ylabel1=ylabel1,
            xlabel2=xlabel2,
            ylabel2=ylabel2,
            size=s if isinstance(s, str) else None,
            style=style,
            hue=hue,
            alpha=alpha if isinstance(alpha, str) else None,
            hover_cols=hover_cols,
            annotate_dots=annotate_dots,
            title=title or "Interactive Scatter (Square Panels)",
            fig=fig,
        )
        return fig

    else:  # backend == "plt"
        # Convert string column names to actual values for matplotlib
        s_values = s
        alpha_values = alpha

        if isinstance(s, str):
            if s in pc.columns:
                s_values = pc[s].values
            else:
                import warnings

                warnings.warn(
                    f"Column '{s}' not found for size mapping, using default size.",
                    UserWarning,
                )
                s_values = 50

        if isinstance(alpha, str):
            if alpha in pc.columns:
                alpha_values = pc[alpha].values
            else:
                import warnings

                warnings.warn(
                    f"Column '{alpha}' not found for alpha mapping, using default alpha.",
                    UserWarning,
                )
                alpha_values = None

        fig, axs = _scatter_plot_matplotlib(
            pc,
            x1="PC1",
            y1="PC2",
            xlabel1=xlabel1,
            ylabel1=ylabel1,
            x2=x2,
            y2=y2,
            xlabel2=xlabel2,
            ylabel2=ylabel2,
            s=s_values,
            alpha=alpha_values,
            title=title,
            annotate_dots=annotate_dots,
            plot_ellipses=plot_ellipses,
            hue=hue,
            hue_order=hue_order,
            hue_dict=hue_dict,
            style=style,
            style_order=style_order,
            style_dict=style_dict,
            fig=fig,
            axs=axs,
        )
        return fig, axs
