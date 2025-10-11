"""Pytest tests for plot_dm functionality."""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from sklearn.datasets import make_blobs
import warnings
import pytest

from masato.plot.dm import dm, plot_dm


def create_test_data():
    """Create sample data for testing."""
    rng = np.random.default_rng(42)
    X, y = make_blobs(n_samples=30, n_features=8, centers=3, cluster_std=1.0, random_state=42)
    
    # Make all values non-negative for Bray-Curtis compatibility
    X = np.abs(X) + 1
    
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
    
    def test_dm_euclidean(self):
        """Test dm function with Euclidean distance."""
        df_otu, df_meta = create_test_data()
        pc, variance = dm(df_otu, df_meta, distance="euclid")
        
        assert isinstance(pc, pd.DataFrame)
        assert isinstance(variance, np.ndarray)
        assert "PC1" in pc.columns
        assert "group" in pc.columns
        
    def test_dm_braycurtis(self):
        """Test dm function with Bray-Curtis distance."""
        df_otu, df_meta = create_test_data()
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Ignore PCoA warnings
            pc, variance = dm(df_otu, df_meta, distance="braycurtis")
            assert isinstance(pc, pd.DataFrame)
            assert isinstance(variance, np.ndarray)


class TestPlotDmMatplotlib:
    """Test plot_dm with matplotlib backend."""
    
    def test_matplotlib_two_panels(self):
        """Test matplotlib backend with two panels."""
        df_otu, df_meta = create_test_data()
        fig, axs = plot_dm(df_otu, df_meta, backend="plt", distance="euclid", 
                          hue="group", plot_pc3=True)
        
        assert isinstance(fig, matplotlib.figure.Figure)
        assert hasattr(axs, '__len__') and len(axs) == 2
        plt.close(fig)
        
    def test_matplotlib_single_panel(self):
        """Test matplotlib backend with single panel."""
        df_otu, df_meta = create_test_data()
        fig, axs = plot_dm(df_otu, df_meta, backend="plt", distance="euclid", 
                          hue="group", plot_pc3=False)
        
        assert isinstance(fig, matplotlib.figure.Figure)
        assert hasattr(axs, '__len__') and len(axs) == 1
        plt.close(fig)


class TestPlotDmPlotly:
    """Test plot_dm with plotly backend."""
    
    def test_plotly_two_panels(self):
        """Test plotly backend with two panels."""
        df_otu, df_meta = create_test_data()
        fig = plot_dm(df_otu, df_meta, backend="plotly", distance="euclid", 
                     hue="group", plot_pc3=True)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0
        
    def test_plotly_single_panel(self):
        """Test plotly backend with single panel."""
        df_otu, df_meta = create_test_data()
        fig = plot_dm(df_otu, df_meta, backend="plotly", distance="euclid", 
                     hue="group", plot_pc3=False)
        
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0


class TestFigureHandling:
    """Test figure handling for both backends."""
    
    def test_matplotlib_existing_figure(self):
        """Test matplotlib with provided figure."""
        df_otu, df_meta = create_test_data()
        existing_fig, existing_axs = plt.subplots(1, 2, figsize=(10, 4))
        
        fig, axs = plot_dm(df_otu, df_meta, backend="plt", distance="euclid",
                          hue="group", fig=existing_fig, axs=existing_axs)
        
        assert fig is existing_fig
        plt.close(fig)
        
    def test_plotly_existing_figure(self):
        """Test plotly with provided figure."""
        df_otu, df_meta = create_test_data()
        from plotly.subplots import make_subplots
        existing_fig = make_subplots(rows=1, cols=2)
        
        fig = plot_dm(df_otu, df_meta, backend="plotly", distance="euclid",
                     hue="group", fig=existing_fig)
        
        assert fig is existing_fig


class TestStringSizeAlpha:
    """Test string size and alpha column handling."""
    
    def test_matplotlib_string_columns(self):
        """Test matplotlib handling of string size/alpha columns."""
        df_otu, df_meta = create_test_data()
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fig, axs = plot_dm(df_otu, df_meta, backend="plt", distance="euclid",
                              s="size_col", alpha="alpha_col", hue="group")
            assert isinstance(fig, matplotlib.figure.Figure)
            plt.close(fig)
    
    def test_plotly_string_columns(self):
        """Test plotly native handling of string size/alpha columns."""
        df_otu, df_meta = create_test_data()
        
        fig = plot_dm(df_otu, df_meta, backend="plotly", distance="euclid",
                     s="size_col", alpha="alpha_col", hue="group")
        assert isinstance(fig, go.Figure)


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_backend(self):
        """Test error for invalid backend."""
        df_otu, df_meta = create_test_data()
        
        with pytest.raises(ValueError, match="Backend must be 'plt' or 'plotly'"):
            plot_dm(df_otu, df_meta, backend="invalid")
            
    def test_backend_specific_warnings(self):
        """Test backend-specific feature warnings."""
        df_otu, df_meta = create_test_data()
        
        # Test ellipses warning with plotly
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            plot_dm(df_otu, df_meta, backend="plotly", distance="euclid",
                   hue="group", plot_ellipses=True)
            assert any("plot_ellipses is not supported" in str(warning.message) 
                      for warning in w)
        
        # Test hover_cols warning with matplotlib
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            fig, axs = plot_dm(df_otu, df_meta, backend="plt", distance="euclid",
                              hue="group", hover_cols=["batch"])
            assert any("hover_cols is only supported" in str(warning.message) 
                      for warning in w)
            plt.close(fig)
