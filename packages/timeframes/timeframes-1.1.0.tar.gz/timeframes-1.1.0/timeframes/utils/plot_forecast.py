"""
Forecast visualization utilities.

Provides simple, publication-quality plots comparing
predictions and ground truth for time series forecasts.
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def plot_forecast(
    y_true,
    y_pred,
    title="Forecast vs Actual",
    output_size: int | None = None,
    start_index: int = 0,
    show_residuals: bool = False,
    figsize=(8, 4),
):
    """
    Plot predicted vs actual values for time series forecasts.

    Parameters
    ----------
    y_true : array-like
        Ground truth values.
    y_pred : array-like
        Predicted values.
    title : str, default="Forecast vs Actual"
        Plot title.
    output_size : int, optional
        Forecast horizon (for labeling future steps).
    start_index : int, default=0
        Offset index for labeling the x-axis.
    show_residuals : bool, default=False
        Whether to plot residuals below the main chart.
    figsize : tuple, default=(8, 4)
        Figure size in inches.
    """
    y_true = np.array(y_true).flatten()
    y_pred = np.array(y_pred).flatten()
    n = len(y_true)
    x = np.arange(start_index, start_index + n)

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(x, y_true, label="Actual", color="black", lw=1.8)
    ax.plot(x, y_pred, label="Predicted", color="#1f77b4", lw=2.0, alpha=0.9)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=10)
    ax.set_xlabel("Time index")
    ax.set_ylabel("Value")
    ax.legend(frameon=False, fontsize=10)
    ax.grid(alpha=0.3, linestyle="--")

    if output_size:
        ax.axvline(x[-output_size], color="gray", lw=1, linestyle="--", alpha=0.5)
        ax.text(x[-output_size] + 0.5, np.mean(y_true), "Forecast start", fontsize=9, color="gray")

    if show_residuals:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(figsize[0], figsize[1] + 2), height_ratios=[3, 1])
        ax1.plot(x, y_true, label="Actual", color="black", lw=1.8)
        ax1.plot(x, y_pred, label="Predicted", color="#1f77b4", lw=2.0, alpha=0.9)
        ax1.set_title(title, fontsize=13, fontweight="bold")
        ax1.legend(frameon=False)
        ax1.grid(alpha=0.3, linestyle="--")

        residuals = y_true - y_pred
        ax2.axhline(0, color="gray", lw=1)
        ax2.bar(x, residuals, color="tomato", alpha=0.7)
        ax2.set_title("Residuals", fontsize=10)
        ax2.set_xlabel("Time index")
        ax2.grid(alpha=0.3, linestyle="--")

    plt.tight_layout()
    plt.show()
