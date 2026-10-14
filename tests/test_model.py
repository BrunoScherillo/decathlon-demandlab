import numpy as np
from model import METHODS, forecast, evaluate, inventory, scenario
from generate_data import generate

def test_forecasts():
    s = np.arange(1, 49, dtype=float)
    for method in METHODS:
        assert len(forecast(s, 12, method)) == 12
        assert (forecast(s, 12, method) >= 0).all()

def test_validation():
    s = generate().query("articolo == 'Giacca sci'")['domanda_unita'].to_numpy()
    table, _ = evaluate(s)
    assert len(table) == 4
    assert (table['MAE'] >= 0).all()

def test_inventory_lead():
    f = np.full(12, 100.)
    a, b = inventory(f, 20, 1), inventory(f, 20, 2)
    assert b['Pipeline'] > a['Pipeline']
    assert b['Sicurezza'] > a['Sicurezza']
    assert a['Anticipata'] == 0

def test_baseline():
    s = np.arange(48.) + 100
    assert np.allclose(scenario(s), s)
