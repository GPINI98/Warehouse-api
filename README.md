# Warehouse API

API REST per la gestione di un magazzino, sviluppata con Python, FastAPI e Oracle Database.

Il progetto consente di gestire gli articoli, registrare i movimenti di magazzino, calcolare le giacenze e consultare statistiche relative alle disponibilità.

## Tecnologie utilizzate

- **Python** – Linguaggio di programmazione principale.
- **FastAPI** – Sviluppo delle API REST.
- **Oracle Database** – Gestione del database relazionale.
- **python-oracledb** – Connessione tra Python e Oracle.
- **SQL** – Interrogazione e manipolazione dei dati.
- **Pydantic** – Validazione dei dati in ingresso.
- **Uvicorn** – Server ASGI per l'esecuzione dell'applicazione.
- **Pytest** – Test automatici.

## Funzionalità principali

### Gestione degli articoli
- Visualizzazione dell'elenco degli articoli.
- Consultazione del dettaglio di un articolo.
- Inserimento di nuovi articoli.
- Modifica dei dati esistenti.
- Eliminazione degli articoli.
- Controllo dei codici articolo duplicati.

### Gestione dei movimenti
- Registrazione dei carichi di magazzino.
- Registrazione degli scarichi.
- Consultazione dello storico dei movimenti.
- Verifica della disponibilità prima di effettuare uno scarico.
- Prevenzione delle giacenze negative.
- Gestione delle operazioni concorrenti tramite blocco delle righe del database (`SELECT FOR UPDATE`).

### Gestione delle giacenze e statistiche
- Calcolo della giacenza attuale per articolo.
- Conteggio degli articoli e dei movimenti registrati.
- Calcolo della quantità totale presente in magazzino.
- Individuazione degli articoli con giacenza pari o inferiore alla scorta minima.

## Struttura del database

Il database Oracle è organizzato in due tabelle principali.

**ARTICOLI**

Contiene le informazioni anagrafiche dei prodotti:
- `id`: identificativo univoco.
- `codice`: codice identificativo dell'articolo.
- `nome`: nome dell'articolo.
- `prezzo`: prezzo unitario.
- `scorta_minima`: soglia minima di disponibilità.

**MOVIMENTI**

Registra le operazioni effettuate sul magazzino:
- `id`: identificativo del movimento.
- `articolo_id`: riferimento all'articolo.
- `tipo`: tipologia di movimento (C = carico, S = scarico).
- `quantita`: quantità movimentata.
- `data_movimento`: data e ora del movimento.
- `note`: descrizione facoltativa.

Le due tabelle sono collegate attraverso una relazione uno-a-molti (1:N): ogni articolo può essere associato a più movimenti.

Sono stati implementati vincoli di integrità referenziale, chiavi primarie, codici univoci e controlli sui valori per garantire la coerenza dei dati.

## Endpoint API

| Metodo | Endpoint | Descrizione |
|---|---|---|
| GET | `/` | Verifica dello stato dell'API |
| GET | `/articoli` | Recupero di tutti gli articoli |
| GET | `/articoli/{id_articolo}` | Dettaglio di un articolo |
| POST | `/articoli` | Creazione di un articolo |
| PUT | `/articoli/{id_articolo}` | Modifica di un articolo |
| DELETE | `/articoli/{id_articolo}` | Eliminazione di un articolo |
| POST | `/movimenti` | Registrazione di un movimento |
| GET | `/movimenti` | Consultazione dello storico |
| GET | `/articoli/{id_articolo}/giacenza` | Calcolo della giacenza |
| GET | `/statistiche` | Recupero delle statistiche |

La documentazione interattiva delle API è disponibile tramite Swagger UI all'indirizzo `/docs`.

## Struttura del progetto

```text
warehouse-api/
│
├── app/
│   ├── main.py
│   ├── database.py
│   └── schemas.py
│
├── credentials/
│   └── File Wallet Oracle (esclusi da Git)
│
├── sql/
│   └── database.sql
│
├── tests/
│   ├── test_api.py
│   └── test_schemas.py
│
├── .env (escluso da Git)
├── .gitignore
├── requirements.txt
└── README.md
```

## Installazione e configurazione

### 1. Clonazione del repository

```bash
git clone <https://github.com/GPINI98/Warehouse-api.git>
cd warehouse-api
```

### 2. Creazione dell'ambiente virtuale

```bash
python -m venv .venv
```

Attivazione su Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Installazione delle dipendenze

```bash
pip install -r requirements.txt
```

### 4. Configurazione del database Oracle

Per utilizzare l'applicazione è necessario disporre di un'istanza Oracle Autonomous Database e del relativo Wallet.

Creare un file `.env` nella cartella principale del progetto:

```env
ORACLE_USER=utente_database
ORACLE_PASSWORD=password_database
ORACLE_DSN=whapi_low
ORACLE_CONFIG_DIR=credentials
ORACLE_WALLET_PASSWORD=password_wallet
```

Inserire i file del Wallet Oracle nella cartella `credentials/`.

**Sicurezza:** il file `.env` e i certificati del Wallet non devono essere pubblicati su GitHub.

### 5. Creazione delle tabelle

Eseguire lo script SQL presente in:

```text
sql/database.sql
```

Lo script crea le tabelle `ARTICOLI` e `MOVIMENTI`, comprese le relative chiavi e i vincoli di integrità.

### 6. Avvio dell'applicazione

```bash
uvicorn app.main:app --reload
```

L'API sarà disponibile all'indirizzo:

```text
http://127.0.0.1:8000
```

La documentazione interattiva sarà disponibile all'indirizzo:

```text
http://127.0.0.1:8000/docs
```

## Test automatici

Il progetto include una suite di test realizzata con Pytest.

Per eseguire tutti i test:

```bash
python -m pytest -v
```

La suite attuale comprende **20 test superati**, che verificano:

- Validazione dei dati in ingresso.
- Operazioni CRUD sugli articoli.
- Registrazione dei movimenti.
- Gestione delle giacenze insufficienti.
- Gestione degli errori del database.
- Commit e rollback delle transazioni.
- Gestione dei vincoli di integrità referenziale.

I test automatici degli endpoint utilizzano simulazioni del database tramite mock, consentendo di verificare la logica applicativa senza richiedere una connessione Oracle attiva.

## Obiettivi del progetto

Il progetto nasce con l'obiettivo di applicare concretamente competenze di sviluppo backend e gestione dei database relazionali.

Durante lo sviluppo sono stati approfonditi:

- Progettazione e sviluppo di API REST.
- Interazione tra Python e Oracle Database.
- Progettazione di tabelle e relazioni SQL.
- Gestione delle query e delle transazioni.
- Validazione dei dati e gestione delle eccezioni.
- Test automatici e simulazione delle interazioni con il database.