import numpy as np

try:
    from sklearn.neighbors import KNeighborsRegressor  # type: ignore
    from sklearn.linear_model import LinearRegression  # type: ignore
    from sklearn.metrics import mean_absolute_error, mean_squared_error  # type: ignore
    SKLEARN_AVAILABLE = True
except Exception:
    KNeighborsRegressor = None
    LinearRegression = None
    mean_absolute_error = None
    mean_squared_error = None
    SKLEARN_AVAILABLE = False

try:
    from statsmodels.tsa.arima.model import ARIMA
    STATS_AVAILABLE = True
except Exception:
    ARIMA = None
    STATS_AVAILABLE = False


def _train_test_split(series, window=20, test_size=0.2):
    values = series.values.astype(float)
    if len(values) <= window + 5:
        return None, None, None, None

    X, y = [], []
    for i in range(window, len(values)):
        X.append(values[i - window:i])
        y.append(values[i])
    X = np.array(X)
    y = np.array(y)

    split_index = int(len(X) * (1 - test_size))
    return X[:split_index], X[split_index:], y[:split_index], y[split_index:]


def _evaluate(y_true, y_pred):
    if mean_squared_error is None or mean_absolute_error is None:
        y_true = np.array(y_true, dtype=float)
        y_pred = np.array(y_pred, dtype=float)
        rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
        mae = float(np.mean(np.abs(y_true - y_pred)))
        return rmse, mae

    rmse = mean_squared_error(y_true, y_pred, squared=False)
    mae = mean_absolute_error(y_true, y_pred)
    return rmse, mae


def _predict_iterative(model, last_window, horizon):
    preds = []
    window = last_window.copy()
    for _ in range(horizon):
        pred = model.predict(window.reshape(1, -1))[0]
        preds.append(float(pred))
        window = np.roll(window, -1)
        window[-1] = pred
    return preds


def run_model_suite(data, horizon=5, window=20):
    series = data["Close"].dropna()
    results = {"predictions": [], "metrics": [], "errors": []}

    X_train, X_test, y_train, y_test = _train_test_split(series, window=window)
    if X_train is None:
        results["errors"].append("Not enough data to train models.")
        return results

    last_window = series.values[-window:]

    if SKLEARN_AVAILABLE:
        try:
            knn = KNeighborsRegressor(n_neighbors=5)
            knn.fit(X_train, y_train)
            knn_pred = knn.predict(X_test)
            rmse, mae = _evaluate(y_test, knn_pred)
            results["metrics"].append({"model": "KNN", "RMSE": rmse, "MAE": mae})
            results["predictions"].append({"model": "KNN", "forecast": _predict_iterative(knn, last_window, horizon)})
        except Exception as exc:
            results["errors"].append(f"KNN failed: {exc}")
    else:
        results["errors"].append("KNN skipped: scikit-learn is not installed.")

    if SKLEARN_AVAILABLE:
        try:
            lr = LinearRegression()
            lr.fit(X_train, y_train)
            lr_pred = lr.predict(X_test)
            rmse, mae = _evaluate(y_test, lr_pred)
            results["metrics"].append({"model": "Linear Regression", "RMSE": rmse, "MAE": mae})
            results["predictions"].append({"model": "Linear Regression", "forecast": _predict_iterative(lr, last_window, horizon)})
        except Exception as exc:
            results["errors"].append(f"Linear Regression failed: {exc}")
    else:
        results["errors"].append("Linear Regression skipped: scikit-learn is not installed.")

    if STATS_AVAILABLE:
        try:
            arima = ARIMA(series, order=(5, 1, 0))
            arima_fit = arima.fit()
            forecast = arima_fit.forecast(steps=horizon)
            arima_pred = arima_fit.predict(start=series.index[int(len(series) * 0.8)], end=series.index[-1])
            rmse, mae = _evaluate(series[int(len(series) * 0.8):], arima_pred)
            results["metrics"].append({"model": "ARIMA", "RMSE": rmse, "MAE": mae})
            results["predictions"].append({"model": "ARIMA", "forecast": forecast.tolist()})
        except Exception as exc:
            results["errors"].append(f"ARIMA failed: {exc}")
    else:
        results["errors"].append("ARIMA skipped: statsmodels is not installed.")

    try:
        from tensorflow.keras.models import Sequential  # type: ignore
        from tensorflow.keras.layers import Dense, LSTM  # type: ignore

        X_train_lstm = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_test_lstm = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

        model = Sequential([
            LSTM(32, activation="relu", input_shape=(window, 1)),
            Dense(1),
        ])
        model.compile(optimizer="adam", loss="mse")
        model.fit(X_train_lstm, y_train, epochs=5, batch_size=16, verbose=0)

        lstm_pred = model.predict(X_test_lstm, verbose=0).flatten()
        rmse, mae = _evaluate(y_test, lstm_pred)
        results["metrics"].append({"model": "LSTM", "RMSE": rmse, "MAE": mae})

        last_seq = last_window.reshape((1, window, 1))
        preds = []
        seq = last_seq.copy()
        for _ in range(horizon):
            pred = model.predict(seq, verbose=0)[0][0]
            preds.append(float(pred))
            seq = np.roll(seq, -1, axis=1)
            seq[0, -1, 0] = pred
        results["predictions"].append({"model": "LSTM", "forecast": preds})
    except Exception as exc:
        results["errors"].append(f"LSTM failed: {exc}")

    return results
