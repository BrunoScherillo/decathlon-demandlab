from pathlib import Path
import numpy as np
import pandas as pd

PRODUCTS = {
    'Pallone calcio': 'stazionaria',
    'Tappetino fitness': 'trend crescente',
    'Tenda campeggio': 'stagionale estiva',
    'Giacca sci': 'stagionale invernale',
}

def generate(path=None):
    rng = np.random.default_rng(2026)
    dates = pd.date_range('2022-01-01', periods=48, freq='MS')
    all_rows = []
    for item, pattern in PRODUCTS.items():
        t = np.arange(48)
        month = dates.month.to_numpy()
        if item == 'Pallone calcio':
            signal = 180 + 7 * np.sin(2 * np.pi * t / 12)
            noise = rng.normal(0, 15, 48)
        elif item == 'Tappetino fitness':
            signal = 75 + 3.1 * t
            noise = rng.normal(0, 11, 48)
        elif item == 'Tenda campeggio':
            signal = 55 + 180 * np.exp(-0.5 * ((month - 7) / 1.5)**2)
            noise = rng.normal(0, 13, 48)
        else:
            distance = np.minimum(np.abs(month - 1), 12 - np.abs(month - 1))
            signal = 35 + 200 * np.exp(-0.5 * (distance / 1.45)**2)
            noise = rng.normal(0, 12, 48)
        for date, units in zip(dates, np.maximum(0, np.rint(signal + noise)).astype(int)):
            all_rows.append({'mese': date.strftime('%Y-%m-%d'), 'articolo': item, 'domanda_unita': units, 'tipo_domanda': pattern})
    frame = pd.DataFrame(all_rows)
    if path is not None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False)
    return frame

if __name__ == '__main__':
    generate(Path(__file__).parent / 'data' / 'demand_history.csv')
