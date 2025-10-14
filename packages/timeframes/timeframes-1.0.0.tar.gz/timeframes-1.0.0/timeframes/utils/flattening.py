import numpy as np

def flatten_stepwise(y_true: np.ndarray, step: int, output_size: int) -> np.ndarray:
    """
    Flatten a rolling (n_windows × output_size) array stepwise according to
    forecast output_size and step size.

    Example
    -------
    For step=2, output_size=4:
      take y[0][:2], then y[1][:2], y[2][:2], ...,
      and finally the remaining tail from the last window.

    Parameters
    ----------
    y_true : np.ndarray
        Array of shape (n_windows, output_size).
    step : int
        Step size used in the walkforward procedure.
    output_size : int
        Forecast horizon .

    Returns
    -------
    flat : np.ndarray
        1D vector reconstructed stepwise without repeats.
    """
    n_windows = y_true.shape[0]
    result = []

    for i in range(n_windows):
        # take first `step` elements of each window
        result.extend(y_true[i, :step])
    # append the final uncovered tail from the last window
    tail_start = n_windows * step - (n_windows - 1) * step
    result.extend(y_true[-1, step:])  # ensures full coverage of last forecast
    return np.array(result[: (n_windows - 1) * step + output_size])


def _aggregate_overlaps(y_seq, y_pred_seq, step: int, output_size: int):
    """
    Combine overlapping multi-step forecasts using step-aware averaging.
    """
    timeline = {}
    start_idx = 0

    for y_true, y_pred in zip(y_seq, y_pred_seq):
        seq_len = min(output_size, len(y_true), len(y_pred))
        for i in range(seq_len):
            idx = start_idx + i
            if idx not in timeline:
                timeline[idx] = {"truth": [], "pred": []}
            timeline[idx]["truth"].append(y_true[i])
            timeline[idx]["pred"].append(y_pred[i])
        start_idx += step  # advance window respecting walkforward step

    # Average overlapping predictions per index
    y_true_flat, y_pred_flat = [], []
    for i in sorted(timeline.keys()):
        y_true_flat.append(np.mean(timeline[i]["truth"]))
        y_pred_flat.append(np.mean(timeline[i]["pred"]))

    return np.array(y_true_flat), np.array(y_pred_flat)
