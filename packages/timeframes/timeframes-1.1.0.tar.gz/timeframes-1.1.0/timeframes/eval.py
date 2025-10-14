"""
Validation and backtesting routines for time series forecasting.
"""

import numpy as np
import pandas as pd

from timeframes.metrics import evaluate_metrics
from timeframes.prep import make_windowed_dataset
from timeframes.utils.flattening import _handle_overlaps
from timeframes.utils.eval_helpers import _do_splits, _fit_oos_windows, _fit_preds

def validate(model, df, target_col, method="walkforward", folds=5,
             input_size=12, output_size=1, return_preds=False, **kwargs):
    """
    Run cross-validation (walk-forward or K-Fold) using windowed datasets.
    """
    # Prepare full supervised dataset
    X, y = make_windowed_dataset(df, target_col=target_col,
                                 input_size=input_size, output_size=output_size)

    splits = _do_splits(X, method, folds=folds, **kwargs)

    preds, trues = _fit_preds(model, splits, X, y)

    y_true, y_pred = _handle_overlaps(output_size, method, preds, trues, is_validation=True, **kwargs)

    metrics = evaluate_metrics(y_true, y_pred)
    return (metrics, (y_true, y_pred)) if return_preds else metrics


def backtest(model, train_df, test_df, target_col, method="walkforward", 
             input_size=12, output_size=1, 
             return_preds=False, **kwargs):
    """
    Perform true out-of-sample (OOS) testing using continuity mode.

    Automatically stitches history_df (train) to test_df for windowing.
    Returns metrics and, optionally, the true/predicted series for visualization.
    """

    y_test, y_pred = _fit_oos_windows(model, target_col, input_size, output_size, train_df, test_df)

    y_true, y_pred = _handle_overlaps(output_size, method, y_test, y_pred, is_validation=False, **kwargs)

    metrics = evaluate_metrics(y_true, y_pred)
    return (metrics, (y_true, y_pred)) if return_preds else metrics



# ---------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------

if __name__ == "__main__":
    """
    Demonstration of Timeframes' validation and backtesting pipeline.
    """

    import random
    from sklearn.linear_model import LinearRegression
    from timeframes.validation.split import split
    from timeframes.utils.plot_forecast import plot_forecast

    SEED = 42
    np.random.seed(SEED)
    random.seed(SEED)

    # -----------------------------------------------------------------
    # 1. Synthetic dataset generation
    # -----------------------------------------------------------------
    N = 120
    harmonic = np.sin(np.linspace(0, 10 * np.pi, N))
    linear = np.linspace(0, 6, N)
    noise = np.random.normal(0, 0.3, N)

    df = pd.DataFrame({
        "x1": linear,
        "x2": harmonic,
        "y": linear + harmonic + noise
    })

    print("\n=== Synthetic time series generated ===")
    print(df.head(), "\n")

    # -----------------------------------------------------------------
    # 2. Split dataset
    # -----------------------------------------------------------------
    train, val, test = split(df, ratios=(0.6, 0.2, 0.2))
    print(f"Train: {len(train)} | Val: {len(val)} | Test: {len(test)}\n")

    # -----------------------------------------------------------------
    # 3. Walk-forward validation (cross-validation)
    # -----------------------------------------------------------------
    model = LinearRegression()
    horizon = 6

    print("=== Walk-forward cross-validation ===")
    metrics_val, (y_true_val, y_pred_val) = validate(
        model,
        train,
        target_col="y",
        method="walkforward",
        input_size=6,
        output_size=horizon,
        step=3,
        mode="expanding",
        min_train_size=10,
        return_preds=True
    )
    print("Validation metrics:", metrics_val, "\n")

    # -----------------------------------------------------------------
    # 4. True Out-of-Sample Backtest
    # -----------------------------------------------------------------
    print("=== True out-of-sample backtest ===")
    metrics_test, (y_true_test, y_pred_test) = backtest(
        model,
        pd.concat([train, val]),
        test,
        target_col="y",
        input_size=6,
        output_size=horizon,
        step=3,
        return_preds=True
    )
    print("Backtest metrics:", metrics_test, "\n")

    # -----------------------------------------------------------------
    # 5. Visualization
    # -----------------------------------------------------------------
    print("Plotting forecast results...")

    plot_forecast(
        y_true_val,
        y_pred_val,
        title="Walk-Forward Validation Forecasts",
        show_residuals=True
    )

    plot_forecast(
        y_true_test,
        y_pred_test,
        title="True Out-of-Sample Forecast",
        show_residuals=True
    )
