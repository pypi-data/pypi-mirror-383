"""Comprehensive tests for plot_dm functionality with different backends and figure scenarios."""

import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.figure
import plotly.graph_objects as go
from sklearn.datasets import make_blobs
import warnings

from masato.plot.dm import dm, plot_dm, _scatter_plot_matplotlib
from masato.plot.dm_plotly import _scatter_plot_plotly


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    rng = np.random.default_rng(42)
    X, y = make_blobs(n_samples=50, n_features=10, centers=3, cluster_std=1.0, random_state=42)
    
    sample_ids = [f"S{i:03d}" for i in range(X.shape[0])]
    df_otu = pd.DataFrame(X, index=sample_ids, columns=[f"F{j:02d}" for j in range(X.shape[1])])
    
    df_meta = pd.DataFrame(index=sample_ids)
    df_meta["group"] = pd.Series(y, index=sample_ids).map({0: "A", 1: "B", 2: "C"})
    df_meta["batch"] = rng.choice(["X", "Y"], size=X.shape[0], replace=True)
    df_meta["size_col"] = rng.integers(5, 25, size=X.shape[0])
    df_meta["alpha_col"] = rng.uniform(0.3, 1.0, size=X.shape[0])
    
    return df_otu, df_meta


class TestDmFunction:
    """Test the dm function for ordination computation."""
    
    def test_dm_braycurtis(self, sample_data):
        """Test dm function with Bray-Curtis distance."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="braycurtis")
        
        assert isinstance(pc, pd.DataFrame)
        assert isinstance(variance, np.ndarray)
        assert "PC1" in pc.columns
        assert "PC2" in pc.columns
        assert "PC3" in pc.columns
        assert "group" in pc.columns
        assert "batch" in pc.columns
        assert len(variance) >= 3
        
    def test_dm_euclidean(self, sample_data):
        """Test dm function with Euclidean distance (PCA)."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        assert isinstance(pc, pd.DataFrame)
        assert isinstance(variance, np.ndarray)
        assert "PC1" in pc.columns
        assert "PC2" in pc.columns
        assert "PC3" in pc.columns
        assert "group" in pc.columns
        assert "batch" in pc.columns
        assert len(variance) >= 3
        
    def test_dm_invalid_distance(self, sample_data):
        """Test dm function with invalid distance metric."""
        df_otu, df_meta = sample_data
        with pytest.raises(NotImplementedError):
            dm(df_otu, df_meta, distance="invalid")


class TestMatplotlibBackend:
    """Test matplotlib backend functionality."""
    
    def test_scatter_plot_matplotlib_basic(self, sample_data):
        """Test basic matplotlib scatter plot."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        fig, axs = _scatter_plot_matplotlib(
            pc, "PC1", "PC2", "PC1 (test)", "PC2 (test)"
        )
        
        assert isinstance(fig, matplotlib.figure.Figure)
        assert isinstance(axs, list)
        assert len(axs) == 1
        plt.close(fig)
        
    def test_scatter_plot_matplotlib_two_panels(self, sample_data):
        """Test matplotlib scatter plot with two panels."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        fig, axs = _scatter_plot_matplotlib(
            pc, "PC1", "PC2", "PC1 (test)", "PC2 (test)",
            x2="PC2", y2="PC3", xlabel2="PC2 (test)", ylabel2="PC3 (test)"
        )
        
        assert isinstance(fig, matplotlib.figure.Figure)
        assert isinstance(axs, list)
        assert len(axs) == 2
        plt.close(fig)
        
    def test_scatter_plot_matplotlib_with_hue_style(self, sample_data):
        """Test matplotlib scatter plot with hue and style."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        fig, axs = _scatter_plot_matplotlib(
            pc, "PC1", "PC2", "PC1 (test)", "PC2 (test)",
            hue="group", style="batch"
        )
        
        assert isinstance(fig, matplotlib.figure.Figure)
        plt.close(fig)
        
    def test_scatter_plot_matplotlib_with_array_values(self, sample_data):
        """Test matplotlib scatter plot with array values for size and alpha."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        fig, axs = _scatter_plot_matplotlib(
            pc, "PC1", "PC2", "PC1 (test)", "PC2 (test)",
            hue="group", s=pc["size_col"].values, alpha=pc["alpha_col"].values
        )
        
        assert isinstance(fig, matplotlib.figure.Figure)
        plt.close(fig)
        
    def test_scatter_plot_matplotlib_with_existing_fig(self, sample_data):
        """Test matplotlib scatter plot with existing figure."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        # Create existing figure and axes
        existing_fig, existing_ax = plt.subplots(1, 1, figsize=(6, 4))
        
        fig, axs = _scatter_plot_matplotlib(
            pc, "PC1", "PC2", "PC1 (test)", "PC2 (test)",
            fig=existing_fig, axs=existing_ax
        )
        
        assert fig is existing_fig
        assert axs[0] is existing_ax
        plt.close(fig)


class TestPlotlyBackend:
    """Test plotly backend functionality."""
    
    def test_scatter_plot_plotly_basic(self, sample_data):
        """Test basic plotly scatter plot."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        fig = _scatter_plot_plotly(
            pc, "PC1", "PC2", xlabel1="PC1 (test)", ylabel1="PC2 (test)"
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        
    def test_scatter_plot_plotly_two_panels(self, sample_data):
        """Test plotly scatter plot with two panels."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        fig = _scatter_plot_plotly(
            pc, "PC1", "PC2", x2="PC2", y2="PC3",
            xlabel1="PC1 (test)", ylabel1="PC2 (test)",
            xlabel2="PC2 (test)", ylabel2="PC3 (test)"
        )
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        
    def test_scatter_plot_plotly_with_hue_style(self, sample_data):
        """Test plotly scatter plot with hue and style."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        fig = _scatter_plot_plotly(
            pc, "PC1", "PC2", xlabel1="PC1 (test)", ylabel1="PC2 (test)",
            hue="group", style="batch"
        )
        
        assert isinstance(fig, go.Figure)
        
    def test_scatter_plot_plotly_with_size_alpha_cols(self, sample_data):
        """Test plotly scatter plot with size and alpha columns."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        fig = _scatter_plot_plotly(
            pc, "PC1", "PC2", xlabel1="PC1 (test)", ylabel1="PC2 (test)",
            size="size_col", alpha="alpha_col", hue="group"
        )
        
        assert isinstance(fig, go.Figure)
        
    def test_scatter_plot_plotly_with_existing_fig(self, sample_data):
        """Test plotly scatter plot with existing figure."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        # Create existing figure
        from plotly.subplots import make_subplots
        existing_fig = make_subplots(rows=1, cols=1)
        
        fig = _scatter_plot_plotly(
            pc, "PC1", "PC2", xlabel1="PC1 (test)", ylabel1="PC2 (test)",
            fig=existing_fig
        )
        
        assert fig is existing_fig


class TestPlotDmFunction:
    """Test the main plot_dm function with different backends and scenarios."""
    
    def test_plot_dm_matplotlib_no_fig(self, sample_data):
        """Test plot_dm with matplotlib backend, no existing figure."""
        df_otu, df_meta = sample_data
        
        fig, axs = plot_dm(
            df_otu, df_meta, backend="plt", distance="euclid",
            hue="group", style="batch"
        )
        
        assert isinstance(fig, matplotlib.figure.Figure)
        assert isinstance(axs, list)
        plt.close(fig)
        
    def test_plot_dm_matplotlib_with_fig(self, sample_data):
        """Test plot_dm with matplotlib backend, existing figure."""
        df_otu, df_meta = sample_data
        
        # Create existing figure
        existing_fig, existing_axs = plt.subplots(1, 2, figsize=(10, 4))
        
        fig, axs = plot_dm(
            df_otu, df_meta, backend="plt", distance="euclid",
            hue="group", fig=existing_fig, axs=existing_axs
        )
        
        assert fig is existing_fig
        plt.close(fig)
        
    def test_plot_dm_plotly_no_fig(self, sample_data):
        """Test plot_dm with plotly backend, no existing figure."""
        df_otu, df_meta = sample_data
        
        fig = plot_dm(
            df_otu, df_meta, backend="plotly", distance="euclid",
            hue="group", style="batch"
        )
        
        assert isinstance(fig, go.Figure)
        
    def test_plot_dm_plotly_with_fig(self, sample_data):
        """Test plot_dm with plotly backend, existing figure."""
        df_otu, df_meta = sample_data
        
        # Create existing figure
        from plotly.subplots import make_subplots
        existing_fig = make_subplots(rows=1, cols=2)
        
        fig = plot_dm(
            df_otu, df_meta, backend="plotly", distance="euclid",
            hue="group", fig=existing_fig
        )
        
        assert fig is existing_fig
        
    def test_plot_dm_string_size_alpha_matplotlib(self, sample_data):
        """Test plot_dm with string size/alpha columns in matplotlib backend."""
        df_otu, df_meta = sample_data
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Ignore expected warnings
            fig, axs = plot_dm(
                df_otu, df_meta, backend="plt", distance="euclid",
                s="size_col", alpha="alpha_col", hue="group"
            )
        
        assert isinstance(fig, matplotlib.figure.Figure)
        plt.close(fig)
        
    def test_plot_dm_string_size_alpha_plotly(self, sample_data):
        """Test plot_dm with string size/alpha columns in plotly backend."""
        df_otu, df_meta = sample_data
        
        fig = plot_dm(
            df_otu, df_meta, backend="plotly", distance="euclid",
            s="size_col", alpha="alpha_col", hue="group"
        )
        
        assert isinstance(fig, go.Figure)
        
    def test_plot_dm_ellipses_matplotlib_only(self, sample_data):
        """Test plot_dm with ellipses (matplotlib only feature)."""
        df_otu, df_meta = sample_data
        
        fig, axs = plot_dm(
            df_otu, df_meta, backend="plt", distance="euclid",
            hue="group", plot_ellipses=True
        )
        
        assert isinstance(fig, matplotlib.figure.Figure)
        plt.close(fig)
        
    def test_plot_dm_ellipses_plotly_warning(self, sample_data):
        """Test plot_dm with ellipses on plotly backend (should warn)."""
        df_otu, df_meta = sample_data
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            fig = plot_dm(
                df_otu, df_meta, backend="plotly", distance="euclid",
                hue="group", plot_ellipses=True
            )
        
        # Check that warning was issued
        assert len(w) > 0
        assert "plot_ellipses is not supported with plotly backend" in str(w[0].message)
        assert isinstance(fig, go.Figure)
        
    def test_plot_dm_hover_cols_plotly_only(self, sample_data):
        """Test plot_dm with hover_cols (plotly only feature)."""
        df_otu, df_meta = sample_data
        
        fig = plot_dm(
            df_otu, df_meta, backend="plotly", distance="euclid",
            hue="group", hover_cols=["batch", "size_col"]
        )
        
        assert isinstance(fig, go.Figure)
        
    def test_plot_dm_hover_cols_matplotlib_warning(self, sample_data):
        """Test plot_dm with hover_cols on matplotlib backend (should warn)."""
        df_otu, df_meta = sample_data
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            fig, axs = plot_dm(
                df_otu, df_meta, backend="plt", distance="euclid",
                hue="group", hover_cols=["batch", "size_col"]
            )
        
        # Check that warning was issued
        assert len(w) > 0
        assert "hover_cols is only supported with plotly backend" in str(w[0].message)
        assert isinstance(fig, matplotlib.figure.Figure)
        plt.close(fig)
        
    def test_plot_dm_invalid_backend(self, sample_data):
        """Test plot_dm with invalid backend."""
        df_otu, df_meta = sample_data
        
        with pytest.raises(ValueError, match="Backend must be 'plt' or 'plotly'"):
            plot_dm(df_otu, df_meta, backend="invalid")
            
    def test_plot_dm_single_panel(self, sample_data):
        """Test plot_dm with single panel (plot_pc3=False)."""
        df_otu, df_meta = sample_data
        
        # Matplotlib
        fig, axs = plot_dm(
            df_otu, df_meta, backend="plt", distance="euclid",
            plot_pc3=False, hue="group"
        )
        assert len(axs) == 1
        plt.close(fig)
        
        # Plotly
        fig = plot_dm(
            df_otu, df_meta, backend="plotly", distance="euclid",
            plot_pc3=False, hue="group"
        )
        assert isinstance(fig, go.Figure)
        
    def test_plot_dm_nonexistent_columns(self, sample_data):
        """Test plot_dm with nonexistent size/alpha columns."""
        df_otu, df_meta = sample_data
        
        # Should warn and use defaults
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            fig, axs = plot_dm(
                df_otu, df_meta, backend="plt", distance="euclid",
                s="nonexistent_size", alpha="nonexistent_alpha"
            )
        
        assert len(w) >= 2  # Should have warnings for both size and alpha
        plt.close(fig)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_incompatible_axes_count(self, sample_data):
        """Test matplotlib backend with wrong number of axes."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        # Create single axis but request two panels
        fig, ax = plt.subplots(1, 1)
        
        with pytest.raises(ValueError, match="Expected 2 axes, got 1"):
            _scatter_plot_matplotlib(
                pc, "PC1", "PC2", "PC1", "PC2",
                x2="PC2", y2="PC3", xlabel2="PC2", ylabel2="PC3",
                fig=fig, axs=ax
            )
        
        plt.close(fig)
        
    def test_plotly_invalid_fig_object(self, sample_data):
        """Test plotly backend with invalid figure object."""
        df_otu, df_meta = sample_data
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        # Pass invalid figure object
        invalid_fig = "not a figure"
        
        with pytest.raises(ValueError, match="Provided fig must be a plotly Figure object"):
            _scatter_plot_plotly(
                pc, "PC1", "PC2", xlabel1="PC1", ylabel1="PC2",
                fig=invalid_fig
            )
            
    def test_minimum_dimensionality_error(self):
        """Test dm function with insufficient dimensionality."""
        # Create data with only 1 feature
        df_otu = pd.DataFrame([[1], [2], [3]], columns=["F1"], index=["S1", "S2", "S3"])
        df_meta = pd.DataFrame(index=["S1", "S2", "S3"])
        
        with pytest.raises(ValueError, match="Minimum dimensionality of input data is 2"):
            dm(df_otu, df_meta)
