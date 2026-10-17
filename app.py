from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Importa dal motore di calcolo le funzioni usate dalla dashboard
from model import evaluate, forecast, inventory, scenario

# Variabili costanti
BLUE = "#1976f3"
ORANGE = "#ff8a1f"
GREY = "#8a94a6"
TEXT = "#3d4b61"
GRID = "#eef2f8"
BASE_DIR = Path(__file__).resolve().parent

# Configura titolo, icona e disposizione della pagina web
st.set_page_config(page_title="Decathlon DemandLab", page_icon="📊", layout="wide")

@st.cache_data
def load_css():
    return (BASE_DIR / "style.css").read_text(encoding="utf-8")
st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)

# Fornisce a tutti i grafici lo stesso aspetto (sfondo trasparente, griglia chiara)
def style_chart(figure, **layout):
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", size=12, color=TEXT),
        **layout,
    )
    figure.update_xaxes(gridcolor=GRID, zeroline=False)
    figure.update_yaxes(gridcolor=GRID, zeroline=False)
    return figure


# Formattatore in stile italiano (punto per le migliaia, virgola per i decimali)
def fmt_it(value, decimals=0):
    return f"{value:,.{decimals}f}".replace(",", "#").replace(".", ",").replace("#", ".")


# Creazione HTML di una scheda KPI (icona colorata + etichetta + valore + unità)
def kpi_card(icon, color, label, value, unit=""):
    return (
        f'<div class="kpi-card">'
        f'<div class="kpi-icon {color}">{icon}</div>'
        f'<div><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-unit">{unit}</div></div>'
        f'</div>'
    )


# Blocco titolo + icona + descrizione
st.markdown(
    """
<div class="app-header">
  <div class="app-logo">📊</div>
  <div>
    <p class="app-title">Decathlon DemandLab</p>
    <p class="app-subtitle">Previsioni e scorte - Progetto didattico con dati sintetici, non vendite reali Decathlon</p>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# Memorizza il dataset in cache per evitare di rileggerlo a ogni interazione
@st.cache_data
def load_data():
    # Il percorso è relativo alla cartella del progetto
    path = BASE_DIR / "data" / "demand_history.csv"
    return pd.read_csv(path, parse_dates=["mese"]).sort_values(["articolo", "mese"]).reset_index(drop=True)


@st.cache_data
def get_actual(item):
    data = load_data()
    return data.loc[data["articolo"] == item, "domanda_unita"].to_numpy(float)


@st.cache_data
def run_scenario(item, variability, trend, seasonality):
    changed = scenario(get_actual(item), variability, trend, seasonality)
    # Valuta i metodi e seleziona quello con MAE più basso
    score, _ = evaluate(changed)
    future = forecast(changed, 12, score.iloc[0]["Metodo"])
    return changed, score, future


@st.cache_data
def run_base(item):
    actual = get_actual(item)
    base_score, _ = evaluate(actual)
    base_future = forecast(actual, 12, base_score.iloc[0]["Metodo"])
    return base_future, base_score.iloc[0]["RMSE"]


# Funzione che evita la deselezione del pulsante nel componente segmented_control
def keep_service():
    if st.session_state["service"] is None:
        st.session_state["service"] = st.session_state["service_last"]
    else:
        st.session_state["service_last"] = st.session_state["service"]


data = load_data()

# Blocco barra laterale
# Tutti i controlli sono raccolti nella barra laterale, per mantenere pulita la schermata
with st.sidebar:
    st.header("⚙️ Impostazioni")
    item = st.selectbox("Prodotto", sorted(data["articolo"].unique()))
    st.markdown("**Domanda**")
    # I tre moltiplicatori valgono 1.0 nello scenario iniziale
    variability = st.slider("Variabilità", 0.0, 2.5, 1.0, 0.1, help="1 = scenario iniziale")
    trend = st.slider("Trend", 0.0, 2.5, 1.0, 0.1, help="1 = scenario iniziale")
    seasonality = st.slider("Stagionalità", 0.0, 2.5, 1.0, 0.1, help="1 = scenario iniziale")
    st.markdown("**Approvvigionamento**")
    lead = st.slider("Lead time (mesi)", 0.25, 4.0, 1.0, 0.25)
    st.session_state.setdefault("service", 0.95)
    st.session_state.setdefault("service_last", 0.95)

    service = st.segmented_control(
        "Livello di servizio", options=[0.90, 0.95, 0.975, 0.99],
        key="service", on_change=keep_service,
        format_func=lambda value: fmt_it(value * 100, 1).replace(",0", "") + "%",
    )

history = data.loc[data["articolo"] == item]
changed, score, future = run_scenario(item, variability, trend, seasonality)
base_future, base_rmse = run_base(item)
top = score.iloc[0]
best = top["Metodo"]
# Stima le quattro tipologie di scorte nei due scenari
stock = inventory(future, top["RMSE"], lead, service)
base_stock = inventory(base_future, base_rmse, 1.0, 0.95)
# Prepara le date dei dodici mesi successivi allo storico
fdates = pd.date_range(history["mese"].iloc[-1] + pd.offsets.MonthBegin(1), periods=12, freq="MS")

# Blocco risultati
st.subheader(f"Risultati - {item}")
st.markdown(
    '<div class="kpi-grid">'
    + kpi_card("🏆", "blue", "Metodo più preciso", best)
    + kpi_card("📊", "blue", "Domanda media prevista", fmt_it(future.mean()), "pezzi/mese")
    + kpi_card("🎯", "red", "Errore MAE", fmt_it(top["MAE"], 1), "pezzi")
    + "</div>",
    unsafe_allow_html=True,
)
st.caption("Metodo selezionato in base al MAE più basso nei test sugli ultimi 12 mesi.")

# Blocco tre grafici
with st.container(key="card_domanda"):
    st.markdown("#### 1. Domanda: storico e previsione")
    # Primo grafico: domanda dello scenario modificato e due previsioni future
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=history["mese"], y=changed, mode="lines", name="Storico", line=dict(color=BLUE)))
    fig.add_trace(go.Scatter(x=fdates, y=future, mode="lines+markers", name="Previsione", line=dict(color=ORANGE)))
    fig.add_trace(go.Scatter(x=fdates, y=base_future, mode="lines", line=dict(dash="dash", color=GREY), name="Scenario base"))
    st.plotly_chart(
        style_chart(fig, xaxis_title="Mese", yaxis_title="Pezzi", margin=dict(l=10, r=10, t=15, b=10), height=340, legend=dict(orientation="h", y=-0.3)),
        width='stretch',
    )

# I grafici degli errori e delle scorte sono affiancati
left, right = st.columns(2, gap="large")
with left:
    with st.container(key="card_metodi"):
        # Secondo grafico
        st.markdown("#### 2. Confronto dei metodi")
        # Un MAE inferiore indica maggiore accuratezza nel periodo di valutazione
        error_fig = px.bar(score, x="MAE", y="Metodo", orientation="h", text_auto=".1f", color_discrete_sequence=[BLUE])
        error_fig.update_yaxes(autorange="reversed")
        st.plotly_chart(
            style_chart(error_fig, xaxis_title="Errore MAE (pezzi)", yaxis_title=None, margin=dict(l=0, r=15, t=10, b=5), height=285),
            width='stretch',
        )
        st.caption("Barra più corta = previsione più accurata.")
with right:
    with st.container(key="card_scorte"):
        # Terzo grafico
        st.markdown("#### 3. Scorte: base vs scenario")
        # Riordina i valori delle scorte per confrontare base e scenario modificato
        stocks = pd.DataFrame({"Tipo": list(stock), "Base": [base_stock[k] for k in stock], "Modificato": list(stock.values())})
        stocks_long = stocks.melt("Tipo", var_name="Scenario", value_name="Pezzi")
        stock_fig = px.bar(stocks_long, x="Tipo", y="Pezzi", color="Scenario", barmode="group",
                           color_discrete_map={"Base": BLUE, "Modificato": ORANGE})
        st.plotly_chart(
            style_chart(stock_fig, xaxis_title=None, yaxis_title="Pezzi", margin=dict(l=0, r=10, t=10, b=5), height=285, legend=dict(orientation="h", y=-0.3)),
            width='stretch',
        )
        st.caption("Le scorte sono indicatori distinti: non vanno sommate automaticamente.")

# Blocco expander che contiene tutti i dettagli metodologici
with st.expander("Dettagli dei calcoli e tabelle"):
    st.write("**Errori dei metodi previsionali**")
    st.dataframe(score.style.format({"MAE": "{:.2f}", "RMSE": "{:.2f}", "sMAPE (%)": "{:.1f}"}), hide_index=True, width='stretch')
    st.write("**Quantità delle scorte (pezzi)**")
    st.dataframe(stocks.round(1), hide_index=True, width='stretch')
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

# Prepara il CSV esportabile con le previsioni di entrambi gli scenari
export = pd.DataFrame({
    "mese": fdates.strftime("%Y-%m-%d"),
    "articolo": item,
    "previsione_scenario": np.round(future, 1),
    "previsione_base": np.round(base_future, 1),
})
# Download del documento CSV
st.download_button("Scarica le previsioni (CSV)", export.to_csv(index=False).encode("utf-8"), "previsioni_scenario.csv", "text/csv")
