# Timeframes

**A lightweight framework for time series validation and evaluation.**  
Timeframes provides simple and efficient tools for splitting, validating, and backtesting forecasting models — without unnecessary dependencies or boilerplate.

---

## 🧠 Need help?

Try **[TimeframesGPT](https://chatgpt.com/g/g-68ec3fa47a808191afbe09cbd63ab611-timeframesgpt-v1-0)** —
a specialized assistant trained on the full Timeframes codices.

---


## Installation

```bash
pip install timeframes
```
---



## Quick Example

```python
import timeframes as ts
from sklearn.linear_model import LinearRegression

# Example data
X, y = ts.load_example("air_passengers")

# Split into train, validation, and test
train, val, test = ts.split(X, ratios=(0.7, 0.2, 0.1))

# Validate using walk-forward cross-validation
model = LinearRegression()
report = ts.validate(model, X, y, method="walkforward", mode="expanding", folds=5)

print(report)
# {'mae': 0.213, 'rmse': 0.322, 'smape': 3.9}
```

---

## Features

* **Minimal** — depends only on NumPy and pandas.
* **Consistent** — unified API for all validation methods.
* **Flexible** — works with any model exposing `.fit()` / `.predict()`.
* **Transparent** — every function returns clear, reproducible outputs.

---

## Supported Methods

| Function        | Description                                        |
| --------------- | -------------------------------------------------- |
| `ts.split()`    | Single train/validation/test split                 |
| `ts.validate()` | Cross-validation (walk-forward or temporal K-Fold) |
| `ts.backtest()` | Out-of-sample testing                              |
| `ts.evaluate()` | Metric evaluation (MAE, RMSE, sMAPE, rMAE)         |


---

## License

MIT License © 2025 [Andrew R. Garcia](https://github.com/andrewrgarcia)