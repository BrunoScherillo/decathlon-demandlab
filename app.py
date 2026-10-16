from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

#Importa dal motore di calcolo le funzioni usate dalla dashboard
from model import evaluate, forecast, inventory, scenario

#Configura titolo, icona e disposizione della pagina web
st.set_page_config(page_title="Decathlon DemandLab", page_icon="📊", layout="wide")
st.title("📊 Decathlon DemandLab")
st.caption("Previsioni e scorte • Progetto didattico con dati sintetici, non vendite reali Decathlon")


#Memorizza il dataset in cache per evitare di rileggerlo a ogni interazione
@st.cache_data
def load_data():
    #Il percorso è relativo alla cartella del progetto
    path = Path(__file__).resolve().parent / "data" / "demand_history.csv"
    return pd.read_csv(path, parse_dates=["mese"])


data = load_data()

#Tutti i controlli sono raccolti nella barra laterale, per mantenere pulita la schermata
with st.sidebar:
    st.header("Impostazioni")
    item = st.selectbox("Prodotto", sorted(data["articolo"].unique()))
    st.markdown("**Domanda**")
    #I tre moltiplicatori valgono 1.0 nello scenario iniziale
    variability = st.slider("Variabilità", 0.0, 2.5, 1.0, 0.1, help="1 = scenario iniziale")
    trend = st.slider("Trend", 0.0, 2.5, 1.0, 0.1, help="1 = scenario iniziale")
    seasonality = st.slider("Stagionalità", 0.0, 2.5, 1.0, 0.1, help="1 = scenario iniziale")
    st.markdown("**Approvvigionamento**")
    lead = st.slider("Lead time (mesi)", 0.25, 4.0, 1.0, 0.25)
    service = st.select_slider(
        "Livello di servizio", options=[0.90, 0.95, 0.975, 0.99], value=0.95,
        format_func=lambda value: f"{value:.1%}",
    )
    st.caption("Valore 1 per domanda = scenario base. Previsione: 12 mesi.")

#Filtra i dati del prodotto selezionato e li ordina cronologicamente
history = data.loc[data["articolo"] == item].sort_values("mese")
actual = history["domanda_unita"].to_numpy(float)
#Applica allo storico le modifiche richieste nella barra laterale
changed = scenario(actual, variability, trend, seasonality)
#Valuta i metodi e seleziona quello con MAE più basso
score, _ = evaluate(changed)
best = score.iloc[0]["Metodo"]
future = forecast(changed, 12, best)
#Calcola previsione senza modifiche, da usare come riferimento
base_score, _ = evaluate(actual)
base_future = forecast(actual, 12, base_score.iloc[0]["Metodo"])
#Stima le quattro tipologie di scorte nei due scenari
stock = inventory(future, score.iloc[0]["RMSE"], lead, service)
base_stock = inventory(base_future, base_score.iloc[0]["RMSE"], 1.0, 0.95)
#Prepara le date dei dodici mesi successivi allo storico
fdates = pd.date_range(history["mese"].iloc[-1] + pd.offsets.MonthBegin(1), periods=12, freq="MS")

st.subheader(f"Risultati · {item}")
#Tabella sintetica con metodo migliore, domanda media futura e MAE
riepilogo = pd.DataFrame({
    "Indicatore": ["Metodo più preciso", "Domanda media prevista", "Errore MAE"],
    "Valore": [
        best,
        f"{future.mean():.0f} pezzi/mese",
        f"{score.iloc[0]['MAE']:.1f} pezzi",
    ],
})
st.table(riepilogo.set_index("Indicatore"))
st.caption("Metodo selezionato in base al MAE più basso nei test sugli ultimi 12 mesi.")

st.markdown("#### 1. Domanda: storico e previsione")
#Primo grafico: domanda dello scenario modificato e due previsioni future
fig = go.Figure()
fig.add_trace(go.Scatter(x=history["mese"], y=changed, mode="lines", name="Storico"))
fig.add_trace(go.Scatter(x=fdates, y=future, mode="lines+markers", name="Previsione"))
fig.add_trace(go.Scatter(x=fdates, y=base_future, mode="lines", line=dict(dash="dash"), name="Scenario base"))
fig.update_layout(xaxis_title="Mese", yaxis_title="Pezzi", margin=dict(l=10, r=10, t=15, b=10), height=340, legend=dict(orientation="h", y=-0.3))
st.plotly_chart(fig, use_container_width=True)

#I grafici degli errori e delle scorte sono affiancati
left, right = st.columns(2, gap="large")
with left:
    #Secondo grafico
    st.markdown("#### 2. Confronto dei metodi")
    #Un MAE inferiore indica maggiore accuratezza nel periodo di valutazione
    error_fig = px.bar(score, x="MAE", y="Metodo", orientation="h", text_auto=".1f")
    error_fig.update_layout(xaxis_title="Errore MAE (pezzi)", yaxis_title=None, margin=dict(l=0, r=15, t=10, b=5), height=285)
    st.plotly_chart(error_fig, use_container_width=True)
    st.caption("Barra più corta = previsione più accurata.")
with right:
    #Terzo grafico
    st.markdown("#### 3. Scorte: base vs scenario")
    #Riordina i valori delle scorte per confrontare base e scenario modificato
    stocks = pd.DataFrame({"Tipo": list(stock), "Base": list(base_stock.values()), "Modificato": list(stock.values())})
    stocks_long = stocks.melt("Tipo", var_name="Scenario", value_name="Pezzi")
    stock_fig = px.bar(stocks_long, x="Tipo", y="Pezzi", color="Scenario", barmode="group")
    stock_fig.update_layout(xaxis_title=None, yaxis_title="Pezzi", margin=dict(l=0, r=10, t=10, b=5), height=285, legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(stock_fig, use_container_width=True)
    st.caption("Le scorte sono indicatori distinti: non vanno sommate automaticamente.")

#Componente expander che contiene tutti i dettagli metodologici
with st.expander("Dettagli dei calcoli e tabelle"):
    st.write("**Errori dei metodi previsionali**")
    st.dataframe(score.style.format({"MAE": "{:.2f}", "RMSE": "{:.2f}", "sMAPE (%)": "{:.1f}"}), hide_index=True, use_container_width=True)
    st.write("**Quantità delle scorte (pezzi)**")
    st.dataframe(stocks.round(1), hide_index=True, use_container_width=True)
    st.markdown("""
    **Metodi:** media mobile a 3 mesi; smorzamento esponenziale (α=0,35);
    regressione lineare; ripetizione dei 12 mesi precedenti (naive stagionale).

    **Scorta ciclica** = domanda media x 1 mese / 2.\n
    **Scorta di sicurezza** = z(livello di servizio) x RMSE x √(lead time + 1 mese).\n
    **Scorta pipeline** = domanda media x lead time (merce in transito).\n
    **Scorta anticipata** = massimo surplus cumulato positivo della domanda prevista rispetto alla media annuale.

    La scorta anticipata è una stima semplificata dell'accumulo prima dei picchi;
    la pipeline non è merce disponibile a scaffale. La scorta di sicurezza assume
    errori indipendenti e lead time costante. Il confronto con lo scenario base
    usa variabilità, trend e stagionalità = 1, lead time = 1 mese e servizio = 95%.
    """)

#Prepara il CSV esportabile con le previsioni di entrambi gli scenari
export = pd.DataFrame({
    "mese": fdates.strftime("%Y-%m-%d"),
    "articolo": item,
    "previsione_scenario": np.round(future, 1),
    "previsione_base": np.round(base_future, 1),
})
#Download del documento CSV
st.download_button("Scarica le previsioni (CSV)", export.to_csv(index=False).encode("utf-8"), "previsioni_scenario.csv", "text/csv")
