import numpy as np
from model import METHODS, forecast, evaluate, inventory, scenario
from generate_data import generate

# Controlla che tutti i metodi producano 12 previsioni e nessun valore negativo
def test_forecasts():
    # Serie di prova con 48 valori mensili crescenti
    s = np.arange(1, 49, dtype=float)
    for method in METHODS:
        assert len(forecast(s, 12, method)) == 12
        assert (forecast(s, 12, method) >= 0).all()

# Verifica la valutazione dei quattro metodi sui dati simulati della giacca da sci
def test_validation():
    s = generate().query("articolo == 'Giacca sci'")['domanda_unita'].to_numpy()
    # Il riepilogo deve contenere quattro metodi e MAE non negativi
    table, _ = evaluate(s)
    assert len(table) == 4
    assert (table['MAE'] >= 0).all()

# Verifica l'effetto di un lead time maggiore sulle scorte stimate
def test_inventory_lead():
    f = np.full(12, 100.)
    a, b = inventory(f, 20, 1), inventory(f, 20, 2)
    assert b['Pipeline'] > a['Pipeline']
    assert b['Sicurezza'] > a['Sicurezza']
    assert a['Anticipata'] == 0

# Controlla che lo scenario neutro non modifichi la serie storica.
def test_baseline():
    s = np.arange(48.) + 100
    # np.allclose confronta i valori considerando piccole tolleranze numeriche
    assert np.allclose(scenario(s), s)
