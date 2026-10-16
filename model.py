import numpy as np
import pandas as pd

#Metodi disponibili nella dashboard, nello stesso ordine usato dalla funzione forecast()
METHODS = ['Media mobile (3 mesi)', 'Smorzamento esponenziale', 'Trend lineare', 'Naive stagionale (12 mesi)']

#Prevede la domanda per un numero di mesi usando il metodo scelto
def forecast(train, horizon, method):
    x = np.asarray(train, dtype=float)
    #Verifica che lo storico e l'orizzonte della previsione siano validi
    if len(x) < 3 or horizon < 1:
        raise ValueError('Servono almeno 3 mesi storici e un orizzonte positivo')

    if method == METHODS[0]:
        #Media mobile: ogni nuovo mese usa gli ultimi tre valori disponibili
        values = list(x)
        for _ in range(horizon):
            values.append(max(0, np.mean(values[-3:])))
        out = values[-horizon:]
    elif method == METHODS[1]:
        #Smorzamento esponenziale semplice: i dati recenti pesano di piu'
        alpha = 0.35
        level = x[0]
        for observation in x[1:]:
            level = alpha * observation + (1 - alpha) * level
        #Senza trend o stagionalita', la previsione resta costante
        out = [max(0, level)] * horizon
    elif method == METHODS[2]:
        #Trend lineare: stima una retta e la prolunga nei mesi futuri
        t = np.arange(len(x))
        slope, intercept = np.polyfit(t, x, 1)
        out = np.maximum(0, intercept + slope * np.arange(len(x), len(x) + horizon))
    elif method == METHODS[3]:
        #Naive stagionale: ripete i valori degli stessi mesi dell'ultimo anno
        if len(x) < 12:
            raise ValueError('Servono 12 mesi per il metodo stagionale')
        out = [max(0, x[-12 + (k % 12)]) for k in range(horizon)]
    else:
        raise ValueError(f'Metodo sconosciuto: {method}')
    return np.asarray(out, dtype=float)

#Confronta i metodi sulle ultime osservazioni usando previsioni a un passo
def evaluate(series, test_months=12):
    x = np.asarray(series, dtype=float)
    if len(x) < test_months + 12:
        raise ValueError('Storico insufficiente per il test')
    rows, predictions = [], {}
    actual = x[-test_months:]
    for name in METHODS:
        #Backtesting progressivo: ogni previsione usa soltanto il passato
        pred = np.array([forecast(x[:i], 1, name)[0] for i in range(len(x) - test_months, len(x))])
        error = actual - pred

        #sMAPE: errore percentuale simmetrico, con controllo dei denominatori nulli
        denom = np.abs(actual) + np.abs(pred)
        smape = np.mean(np.divide(200 * np.abs(error), denom, out=np.zeros_like(denom), where=denom > 0))

        #MAE = errore assoluto medio; RMSE penalizza gli errori piu' grandi
        rows.append({'Metodo': name, 'MAE': np.mean(np.abs(error)), 'RMSE': np.sqrt(np.mean(error ** 2)), 'sMAPE (%)': smape})
        predictions[name] = pred

    #La prima riga identifica il metodo con MAE minimo (RMSE come spareggio)
    table = pd.DataFrame(rows).sort_values(['MAE', 'RMSE']).reset_index(drop=True)
    return table, predictions

#Modifica le componenti della domanda per simulare uno scenario alternativo
def scenario(series, variability=1.0, trend=1.0, seasonality=1.0):
    x = np.asarray(series, dtype=float)
    t = np.arange(len(x))
    months = t % 12
    base = np.mean(x)

    #Separa approssimativamente trend, stagionalità e variabilità residua.
    slope = np.polyfit(t, x, 1)[0]
    trend_part = slope * (t - t.mean())
    residual = x - trend_part - base
    monthly = np.array([residual[months == m].mean() for m in range(12)])
    seasonal = monthly[months]
    noise = x - base - trend_part - seasonal

    #Moltiplicatore 1 = componente invariata; 0 = componente eliminata
    return np.maximum(0, base + trend * trend_part + seasonality * seasonal + variability * noise)

#Stima quattro componenti distinte delle scorte usando formule semplificate
def inventory(future, residual_std, lead_months=1.0, service=0.95, review_months=1.0):
    from statistics import NormalDist
    y = np.asarray(future, dtype=float)
    avg = float(y.mean())

    #Converte il livello di servizio nel corrispondente quantile normale z
    z = NormalDist().inv_cdf(service)
    #Stima l'accumulo anticipato prima dei picchi rispetto alla domanda media
    advance = float(max(0, np.max(np.concatenate([[0.0], np.cumsum(y - avg)]))))
    return {'Ciclica': avg * review_months / 2,
            'Sicurezza': z * residual_std * np.sqrt(lead_months + review_months),
            'Anticipata': advance,
            'Pipeline': avg * lead_months}
