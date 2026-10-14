import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from model import METHODS, evaluate, forecast, inventory, scenario


st.set_page_config(page_title='Decathlon DemandLab', layout='wide')
st.title('Decathlon DemandLab')
st.caption('Laboratorio didattico: previsioni della domanda e politiche di scorta | dati sintetici, NON vendite reali Decathlon')

@st.cache_data #evita di ricaricare i dati
def load_data(): #legge il CSV e converte mese in data
    return pd.read_csv('data/domanda_sintetica.csv', parse_dates=['mese'])

data = load_data()
items = sorted(data['articolo'].unique())

with st.sidebar:
    st.header('1 · Prodotto e scenario')
    item = st.selectbox('Articolo', items)
    variability = st.slider('Variabilità casuale', 0.0, 2.5, 1.0, 0.1)
    trend = st.slider('Intensità del trend', 0.0, 2.5, 1.0, 0.1)
    seasonality = st.slider('Intensità stagionalità', 0.0, 2.5, 1.0, 0.1)
    st.header('2 · Approvvigionamento')
    lead = st.slider('Lead time (mesi)', 0.25, 4.0, 1.0, 0.25)
    service = st.select_slider('Livello servizio obiettivo', options=[0.90, 0.95, 0.975, 0.99], value=0.95, format_func=lambda x: f'{x:.1%}')
    st.caption('Review periodica fissa: 1 mese. Orizzonte previsionale: 12 mesi.')

history = data[data['articolo'] == item].sort_values('mese').copy()
actual = history['domanda_unita'].to_numpy(float)
changed = scenario(actual, variability, trend, seasonality)
score, preds = evaluate(changed)
best = score.iloc[0]['Metodo']
future = forecast(changed, 12, best)
base_score, _ = evaluate(actual)
base_method = base_score.iloc[0]['Metodo']
base_future = forecast(actual, 12, base_method)
err = score.iloc[0]['RMSE']
base_stock = inventory(base_future, base_score.iloc[0]['RMSE'], 1.0, 0.95)
stock = inventory(future, err, lead, service)

st.info(f'**Metodo migliore nello scenario:** {best} · criterio: MAE minore nel backtest rolling a 12 mesi (un mese avanti).')
c1, c2, c3, c4 = st.columns(4)
c1.metric('Domanda prevista media/mese', f'{future.mean():.0f} pz', f'{future.mean()-base_future.mean():+.0f} vs base')
c2.metric('MAE metodo migliore', f'{score.iloc[0]["MAE"]:.1f} pz')
c3.metric('Lead time', f'{lead:g} mesi')
c4.metric('Scorta di sicurezza', f'{stock["Sicurezza"]:.0f} pz', f'{stock["Sicurezza"]-base_stock["Sicurezza"]:+.0f} vs base')

st.subheader('Domanda storica e previsione (12 mesi)')
fdates = pd.date_range(history['mese'].iloc[-1] + pd.offsets.MonthBegin(1), periods=12, freq='MS')
fig = go.Figure()
fig.add_trace(go.Scatter(x=history['mese'], y=changed, mode='lines+markers', name='Storico nello scenario'))
fig.add_trace(go.Scatter(x=fdates, y=future, mode='lines+markers', name=f'Previsione: {best}'))
fig.add_trace(go.Scatter(x=fdates, y=base_future, mode='lines', line={'dash':'dot'}, name='Previsione scenario base'))
fig.update_layout(xaxis_title='Mese', yaxis_title='Unità richieste', legend_orientation='h')
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader('Accuratezza dei quattro metodi')
    st.plotly_chart(px.bar(score, x='Metodo', y='MAE', text_auto='.1f', title='MAE: più basso è meglio'), use_container_width=True)
    st.dataframe(score.style.format({'MAE':'{:.2f}', 'RMSE':'{:.2f}', 'sMAPE (%)':'{:.1f}'}), hide_index=True, use_container_width=True)
with right:
    st.subheader('Scorte: scenario base vs modificato')
    tab = pd.DataFrame({'Tipo': list(stock), 'Base': list(base_stock.values()), 'Scenario': list(stock.values())})
    st.plotly_chart(px.bar(tab.melt('Tipo', var_name='Scenario', value_name='Pezzi'), x='Tipo', y='Pezzi', color='Scenario', barmode='group'), use_container_width=True)
    st.dataframe(tab.round(1), hide_index=True, use_container_width=True)

with st.expander('Definizioni, formule e limiti della simulazione'):
    st.markdown('''
    **Media mobile:** media delle ultime 3 osservazioni. **Smorzamento esponenziale:** α = 0,35.
    **Trend:** regressione lineare sui mesi osservati. **Naive stagionale:** ripete gli ultimi 12 mesi.

    **Scorta ciclica** = domanda media × intervallo revisione / 2; revisione mensile.
    **Scorta di sicurezza** = z(livello servizio) × RMSE rolling × √(lead time + intervallo revisione).
    **Pipeline** = domanda media × lead time (merce in transito, non disponibile a scaffale).
    **Anticipata** = massimo surplus cumulato positivo della previsione rispetto alla media annuale:
    indicatore semplificato delle unità da accumulare prima dei picchi stagionali, non inventario già posseduto.

    Le componenti **non si sommano automaticamente**: pipeline è in transito, mentre le altre sono
    indicatori di pianificazione; l'anticipata può sovrapporsi a scorte disponibili.
    La formula della sicurezza assume errori indipendenti con varianza stabile e lead time deterministico;
    non è una simulazione di ordini, rotture di stock o costi.
    Scenario e benchmark ricalcolano i metodi sugli storici trasformati: cambiando l'intensità di trend,
    stagionalità o variabilità cambia la domanda stessa.
    ''')

st.download_button('Scarica previsioni e scenario (CSV)', pd.DataFrame({'mese':fdates.strftime('%Y-%m-%d'), 'articolo':item, 'previsione_scenario':np.round(future, 1), 'previsione_base':np.round(base_future,1)}).to_csv(index=False).encode(), 'previsioni_scenario.csv', 'text/csv')
