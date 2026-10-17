# Decathlon DemandLab

**Previsione della domanda e gestione delle scorte**

Decathlon DemandLab è un progetto universitario realizzato con **Python** e **Streamlit**. Il suo scopo è mostrare come si può prevedere la richiesta di alcuni prodotti e come queste previsioni possono aiutare a organizzare le scorte di magazzino.

> **Importante:** i dati utilizzati sono inventati e generati per questo esercizio. Non sono dati di vendita reali o ufficiali di Decathlon. L'azienda non partecipa al progetto.

## Cosa fa il progetto

L'applicazione analizza la domanda di quattro articoli sportivi:

| Prodotto | Tipo di domanda simulata |
| --- | --- |
| Pallone da calcio | Abbastanza stabile durante l'anno |
| Tappetino fitness | In crescita nel tempo |
| Tenda da campeggio | Più alta in estate |
| Giacca da sci | Più alta in inverno |

Per ogni prodotto sono disponibili **48 mesi di dati**, da gennaio 2022 a dicembre 2025.

La dashboard permette di:

- confrontare quattro modi diversi di prevedere la domanda;
- individuare il metodo con l'errore medio più basso;
- prevedere la domanda dei successivi 12 mesi;
- cambiare alcuni parametri, come variabilità, trend, stagionalità e tempi di consegna;
- vedere come cambiano le scorte nello scenario iniziale e in quello modificato;
- scaricare un file CSV con le previsioni.

## Tecnologie utilizzate

- **Python:** linguaggio con cui è stato scritto il progetto.
- **Streamlit:** crea la pagina web interattiva.
- **Pandas e NumPy:** aiutano a leggere i dati e a fare i calcoli.
- **Plotly:** mostra i risultati attraverso grafici.
- **CSS:** definisce tutta la parte grafica dell'interfaccia.
- **Pytest:** permette di eseguire alcuni controlli automatici sul codice.

## Come avviare la dashboard

Serve **Python 3.10 o una versione successiva**.

1. Aprire il terminale nella cartella del progetto.
2. Installare le librerie necessarie:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Avviare l'applicazione:

   ```bash
   python -m streamlit run app.py
   ```

La dashboard si aprirà nel browser, normalmente all'indirizzo <http://localhost:8501>.

## Come usare la dashboard

1. **Scegliere un prodotto** dal menu nella barra laterale.
2. **Leggere il riepilogo:** mostra il metodo più preciso, la domanda media prevista e il valore MAE, cioè l'errore medio espresso in pezzi.
3. **Osservare il primo grafico:** confronta la domanda storica con le previsioni e con lo scenario iniziale.
4. **Osservare il secondo grafico:** confronta gli errori dei metodi previsionali. Una barra più corta indica un errore minore.
5. **Osservare il terzo grafico:** confronta le quattro tipologie di scorte nei due scenari.
6. **Provare a cambiare un parametro alla volta**, per capire quale effetto produce.
7. **Scaricare le previsioni** usando il pulsante presente in fondo alla pagina.

### Significato dei parametri

| Parametro | Che cosa cambia |
| --- | --- |
| Variabilità | Quanto la domanda oscilla in modo casuale |
| Trend | Quanto cresce o diminuisce la domanda nel tempo |
| Stagionalità | Quanto sono forti i picchi legati alle stagioni |
| Lead time | Tempo necessario per ricevere la merce ordinata |
| Livello di servizio | Obiettivo di protezione dal rischio di esaurire le scorte |

Per variabilità, trend e stagionalità, **il valore 1 mantiene lo scenario iniziale**.

## File principali

| File | A cosa serve |
| --- | --- |
| `app.py` | Mostra la dashboard e gestisce i comandi dell'utente |
| `style.css` | Definisce lo stile grafico della dashboard |
| `model.py` | Calcola previsioni, errori e scorte |
| `generate_data.py` | Genera i dati di esempio |
| `data/demand_history.csv` | Contiene i dati mensili dei quattro prodotti |
| `.streamlit/config.toml` | Imposta i colori del tema di Streamlit |
| `tests/test_model.py` | Contiene i test automatici |
| `requirements.txt` | Elenca le librerie da installare |

### Rigenerare i dati (facoltativo)

Per ricreare il file CSV, eseguire:

```bash
python generate_data.py
```

Lo script usa un valore casuale iniziale fisso (`2026`), quindi genera dati ripetibili. Non è necessario eseguire questo comando ogni volta che la dashboard viene aperta: il CSV è già incluso nel progetto.

### Eseguire i test (facoltativo)

Per verificare alcune funzioni del programma, eseguire:

```bash
python -m pytest -q
```

I test controllano, per esempio, che le previsioni abbiano la lunghezza prevista e che alcune scorte cambino in modo coerente quando aumenta il tempo di consegna.

## Come vengono valutate le previsioni

Il progetto confronta questi quattro metodi:

- media mobile a 3 mesi;
- smorzamento esponenziale;
- trend lineare;
- metodo Naive stagionale a 12 mesi.

Per confrontarli vengono usati gli ultimi 12 mesi della serie storica, facendo previsioni senza utilizzare dati dei mesi successivi. Il programma sceglie il metodo con il **MAE più basso**. Nella sezione dei dettagli sono visibili anche **RMSE** e **sMAPE**, altri due valori utili per valutare gli errori.