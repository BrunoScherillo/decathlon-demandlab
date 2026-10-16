import numpy as np
import pandas as pd

METHODS = ['Media mobile (3 mesi)', 'Smorzamento esponenziale', 'Trend lineare', 'Naive stagionale (12 mesi)']

def forecast(train, horizon, method):
    x = np.asarray(train, dtype=float)
    if len(x) < 3 or horizon < 1:
        raise ValueError('Servono almeno 3 mesi storici e un orizzonte positivo')
    if method == METHODS[0]:
        values = list(x)
        for _ in range(horizon):
            values.append(max(0, np.mean(values[-3:])))
        out = values[-horizon:]
    elif method == METHODS[1]:
        alpha = 0.35
        level = x[0]
        for observation in x[1:]:
            level = alpha * observation + (1 - alpha) * level
        out = [max(0, level)] * horizon
    elif method == METHODS[2]:
        t = np.arange(len(x))
        slope, intercept = np.polyfit(t, x, 1)
        out = np.maximum(0, intercept + slope * np.arange(len(x), len(x) + horizon))
    elif method == METHODS[3]:
        if len(x) < 12:
            raise ValueError('Servono 12 mesi per il metodo stagionale')
        out = [max(0, x[-12 + (k % 12)]) for k in range(horizon)]
    else:
        raise ValueError(f'Metodo sconosciuto: {method}')
    return np.asarray(out, dtype=float)

def evaluate(series, test_months=12):
    x = np.asarray(series, dtype=float)
    if len(x) < test_months + 12:
        raise ValueError('Storico insufficiente per il test')
    rows, predictions = [], {}
    actual = x[-test_months:]
    for name in METHODS:
        pred = np.array([forecast(x[:i], 1, name)[0] for i in range(len(x) - test_months, len(x))])
        error = actual - pred
        denom = np.abs(actual) + np.abs(pred)
        smape = np.mean(np.divide(200 * np.abs(error), denom, out=np.zeros_like(denom), where=denom > 0))
        rows.append({'Metodo': name, 'MAE': np.mean(np.abs(error)), 'RMSE': np.sqrt(np.mean(error ** 2)), 'sMAPE (%)': smape})
        predictions[name] = pred
    table = pd.DataFrame(rows).sort_values(['MAE', 'RMSE']).reset_index(drop=True)
    return table, predictions

def scenario(series, variability=1.0, trend=1.0, seasonality=1.0):
    x = np.asarray(series, dtype=float)
    t = np.arange(len(x))
    months = t % 12
    base = np.mean(x)
    slope = np.polyfit(t, x, 1)[0]
    trend_part = slope * (t - t.mean())
    residual = x - trend_part - base
    monthly = np.array([residual[months == m].mean() for m in range(12)])
    seasonal = monthly[months]
    noise = x - base - trend_part - seasonal
    return np.maximum(0, base + trend * trend_part + seasonality * seasonal + variability * noise)

def inventory(future, residual_std, lead_months=1.0, service=0.95, review_months=1.0):
    from statistics import NormalDist
    y = np.asarray(future, dtype=float)
    avg = float(y.mean())
    z = NormalDist().inv_cdf(service)
    advance = float(max(0, np.max(np.concatenate([[0.0], np.cumsum(y - avg)]))))
    return {'Ciclica': avg * review_months / 2,
            'Sicurezza': z * residual_std * np.sqrt(lead_months + review_months),
            'Anticipata': advance,
            'Pipeline': avg * lead_months}
