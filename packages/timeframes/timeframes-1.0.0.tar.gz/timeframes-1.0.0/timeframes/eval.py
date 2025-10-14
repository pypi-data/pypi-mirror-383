"""
Validation and backtesting routines for time series forecasting.
"""

import numpy as np
import pandas as pd
from sklearn.base import clone

from timeframes.metrics import evaluate_metrics
from timeframes.validation.walkforward import walkforward
from timeframes.validation.kfold import kfold
from timeframes.prep import make_windowed_dataset
from timeframes.utils.flattening import flatten_stepwise, _aggregate_overlaps


# ---------------------------------------------------------------------
# Cross-validation (walk-forward or kfold)
# ---------------------------------------------------------------------
def validate(model, df, target_col, method="walkforward", folds=5,
             input_size=12, output_size=1, step=1, return_preds=False, **kwargs):
    """
    Run cross-validation (walk-forward or K-Fold) using windowed datasets.
    """
    # Prepare full supervised dataset
    X, y = make_windowed_dataset(df, target_col=target_col,
                                 input_size=input_size, output_size=output_size)

    preds, trues = [], []

    if method == "walkforward":
        splits = walkforward(len(X), **kwargs)
    elif method == "kfold":
        splits = kfold(n_splits=folds).split(np.arange(len(X)))
    else:
        raise ValueError("method must be 'walkforward' or 'kfold'")

    for train_idx, val_idx in splits:
        model_ = clone(model)
        model_.fit(X[train_idx].reshape(len(train_idx), -1), y[train_idx])
        y_pred = model_.predict(X[val_idx].reshape(len(val_idx), -1))
        preds.append(y_pred)
        trues.append(y[val_idx])

    # Handle multi-step overlap averaging
    if output_size > 1 and method == "walkforward":
        step = kwargs.get("step", 1)
        _, y_pred = _aggregate_overlaps(trues, preds, step, output_size)
        y_true = np.concatenate(trues)
        y_true = flatten_stepwise(y_true,step=step, output_size=output_size)
        
        # Ensure equal length before metrics
        min_len = min(len(y_true), len(y_pred))
        y_true = y_true[:min_len]
        y_pred = y_pred[:min_len]
        print(y_true.shape, y_pred.shape)


    else:
        y_true = np.concatenate(trues)
        y_pred = np.concatenate(preds)

    metrics = evaluate_metrics(y_true, y_pred)
    return (metrics, (y_true, y_pred)) if return_preds else metrics


# ---------------------------------------------------------------------
# True out-of-sample backtesting
# ---------------------------------------------------------------------
def backtest(model, train_df, test_df, target_col,
             input_size=12, output_size=1, step=1):
    """
    Perform true out-of-sample (OOS) testing using continuity mode.

    Automatically stitches history_df (train) to test_df for windowing.
    """
    X_train, y_train = make_windowed_dataset(
        train_df, target_col=target_col, input_size=input_size, output_size=output_size
    )
    X_test, y_test = make_windowed_dataset(
        test_df, target_col=target_col, input_size=input_size, output_size=output_size,
        oos_mode=True, history_df=train_df
    )

    model.fit(X_train.reshape(len(X_train), -1), y_train)
    y_pred = model.predict(X_test.reshape(len(X_test), -1))

    # Aggregate overlaps if output_size > step
    if output_size > 1:
        y_true, y_pred = _aggregate_overlaps([y_test], [y_pred], step, output_size)
    else:
        y_true, y_pred = y_test, y_pred

    return evaluate_metrics(y_true, y_pred)


# ---------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------
if __name__ == "__main__":
    from sklearn.linear_model import LinearRegression
    from timeframes.validation.split import split
    from timeframes.utils.plot_forecast import plot_forecast

    N = 100
    harmonic = np.sin(np.linspace(0, 10*np.pi, N))
    linear = np.arange(N)*0.1
    noise = np.random.randn(N)*0.3
    df = pd.DataFrame({
        "x1": linear,
        "x2": harmonic,
        "y": linear + harmonic + noise
    })

    train, val, test = split(df, ratios=(0.6, 0.2, 0.2))
    model = LinearRegression()

    horizon = 2
    # Validate (walkforward)
    metrics, (y_true, y_pred) = validate(
        model, train, target_col="y",
        method="walkforward", input_size=6, output_size=horizon,
        step=2, mode="expanding", min_train_size=10,
        return_preds=True
    )
    print("Walk-forward CV metrics:", metrics)

    # OOS Backtest
    metrics, (y_true_oos, y_pred_oos) = validate(
        model, pd.concat([train, val]), target_col="y",
        method="walkforward", input_size=6, output_size=horizon,
        step=2, mode="expanding", min_train_size=10,
        return_preds=True
    )
    print("OOS metrics:", metrics)

    # Visualization
    plot_forecast(y_true_oos, y_pred_oos,
                  title="Out-of-Sample Forecast vs Actual",
                  show_residuals=True)
