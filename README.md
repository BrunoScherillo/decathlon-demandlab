# Decathlon DemandLab

**Previsione della domanda e pianificazione delle scorte** — progetto didattico in Python/Streamlit.

> I dati delle vendite sono **interamente sintetici**, non rappresentano dati interni o ufficiali Decathlon. Decathlon non è coinvolta nel progetto.

## Avvio rapido

Prerequisito: Python 3.10+.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Il browser aprirà la dashboard (di norma http://localhost:8501). Se occorre rigenerare i dati  (file CSV salvato in "data"):

```bash
python generate_data.py
```

Per eseguire dei test (recuperati da tests/test_model):

```bash
python -m pytest -q
```

## Cosa contiene

- `app.py`: interfaccia con filtri e grafici comparativi.
- `model.py`: 4 modelli previsionali, backtest cronologico, scenari e scorte.
- `generate_data.py`: dati riproducibili (seed=2026), quattro articoli × 48 mesi.
- `data/demand_history.csv`: 192 osservazioni mensili.
- `tests/test_model.py`: test di funzionamento.

## Come usare la dashboard

1. Scegli uno dei quattro articoli.
2. Osserva il metodo vincente e l'accuratezza sullo scenario base.
3. Modifica un parametro alla volta: variabilità, trend, stagionalità o lead time.
4. Confronta le previsioni e le quattro categorie di scorte con lo scenario base.
5. Scarica il CSV delle previsioni per discutere un caso concreto nella relazione.

**Nota metodologica:** confronto di previsione: backtest rolling-origin sui 12 mesi finali, senza usare dati futuri per stimare i modelli. Selezione per MAE, RMSE e sMAPE come supporto. Le scorte sono quantità di pianificazione illustrative: non costituiscono una simulazione di inventario operativa e non vanno sommate indiscriminatamente.