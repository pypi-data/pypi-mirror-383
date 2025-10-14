import numpy as np
from sklearn.base import clone

from timeframes.validation.walkforward import walkforward
from timeframes.validation.kfold import kfold
from timeframes.prep import make_windowed_dataset

# ---------------------------------------------------------------------
# Cross-validation (walk-forward or kfold)
# ---------------------------------------------------------------------
def _do_splits(X, method, folds=5, **kwargs):
    if method == "walkforward":
        return walkforward(len(X), **kwargs)
    elif method == "kfold":
        return kfold(n_splits=folds).split(np.arange(len(X)))
    else:
        raise ValueError("method must be 'walkforward' or 'kfold'")

def _fit_preds(model, splits, X, y):
    preds, trues = [], []

    for train_idx, val_idx in splits:
        model_ = clone(model)
        model_.fit(X[train_idx].reshape(len(train_idx), -1), y[train_idx])
        y_pred = model_.predict(X[val_idx].reshape(len(val_idx), -1))
        preds.append(y_pred)
        trues.append(y[val_idx])

    return preds, trues

# ---------------------------------------------------------------------
# True out-of-sample backtesting
# ---------------------------------------------------------------------
def _fit_oos_windows(model, target_col, input_size, output_size, train_df, test_df):
    args = dict(target_col=target_col, input_size=input_size, output_size=output_size)
    X_train, y_train = make_windowed_dataset(train_df, **args)
    X_test, y_test = make_windowed_dataset(test_df, **args, oos_mode=True, history_df=train_df)

    model.fit(X_train.reshape(len(X_train), -1), y_train)
    y_pred = model.predict(X_test.reshape(len(X_test), -1))

    return y_test, y_pred
