# Decathlon DemandLab

**Previsione della domanda e gestione delle scorte**

Decathlon DemandLab è un progetto universitario realizzato con **Python** e **Streamlit**. Il suo scopo è mostrare come si può prevedere la richiesta di alcuni prodotti e come queste previsioni possono aiutare a organizzare le scorte di magazzino.

> **Importante:** i dati utilizzati sono inventati e generati per questo esercizio. Non sono dati di vendita reali o ufficiali di Decathlon. L'azienda non partecipa al progetto.

---

## Indice

1. [Cosa fa il progetto](#cosa-fa-il-progetto)
2. [Tecnologie utilizzate](#tecnologie-utilizzate)
3. [Come avviare la dashboard](#come-avviare-la-dashboard)
4. [Come usare la dashboard](#come-usare-la-dashboard)
5. [Struttura del progetto](#struttura-del-progetto)
6. [Rigenerare i dati ed eseguire i test](#rigenerare-i-dati-ed-eseguire-i-test)
7. [Come vengono valutate le previsioni](#come-vengono-valutate-le-previsioni)

---

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

### 1. Installare Python (se non è già presente)

Serve **Python 3.10 o una versione successiva**. Per controllare se è già installato, aprire il terminale (su Windows: *Prompt dei comandi* o *PowerShell*) ed eseguire:

```bash
python --version
```

Se compare un numero di versione pari o superiore a 3.10, si può passare al punto successivo. Altrimenti:

- scaricare Python da <https://www.python.org/downloads/>;
- **Windows:** nella prima schermata dell'installazione spuntare **"Add Python to PATH"** prima di cliccare su *Install Now*.
- **macOS / Linux:** su alcuni sistemi il comando si chiama `python3` invece di `python`; in tal caso usare `python3` e `pip3` in tutti i comandi seguenti.

### 2. Scaricare il progetto

Scaricare la cartella del progetto (oppure clonarla con Git) e aprire il terminale al suo interno.

### 3. Installare le librerie

```bash
python -m pip install -r requirements.txt
```

### 4. Avviare l'applicazione

```bash
python -m streamlit run app.py
```

La dashboard si aprirà nel browser, normalmente all'indirizzo <http://localhost:8501>. Per chiudere l'applicazione, premere `Ctrl + C` nel terminale.

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

## Struttura del progetto

```text
decathlon-demandlab/
├── app.py                  # dashboard e gestione dei comandi
├── style.css               # stile grafico
├── model.py                # previsioni, errori e scorte
├── generate_data.py        # generazione dei dati di esempio
├── requirements.txt        # librerie da installare
├── data/
│   └── demand_history.csv  # dati mensili dei quattro prodotti
├── .streamlit/
│   └── config.toml         # colori del tema di Streamlit
└── tests/
    └── test_model.py       # test automatici
```

## Rigenerare i dati ed eseguire i test

Entrambi i passaggi sono **facoltativi**.

**Rigenerare i dati.** Per ricreare il file CSV:

```bash
python generate_data.py
```

Lo script usa un valore casuale iniziale fisso (`2026`), quindi genera sempre gli stessi dati. Non serve eseguirlo ogni volta che si apre la dashboard: il CSV è già incluso nel progetto.

**Eseguire i test.** Per verificare alcune funzioni del programma:

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