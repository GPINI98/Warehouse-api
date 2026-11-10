
from fastapi import FastAPI, HTTPException
from app.database import connessione_database

app = FastAPI(
    title="Warehouse API",
    description="API REST per la gestione di un magazzino",
    version="1.0.0"
)


@app.get("/")
def home():
    return {"messaggio": "Warehouse API attiva"}


@app.get("/articoli")
def mostra_articoli():

    connessione = None

    try:
        connessione = connessione_database()

        with connessione.cursor() as cursore:
            cursore.execute("""
                SELECT id, codice, nome, prezzo, scorta_minima
                FROM ARTICOLI
                ORDER BY id
            """)

            colonne = [colonna[0].lower() for colonna in cursore.description]
            righe = cursore.fetchall()

            articoli = [
                dict(zip(colonne, riga))
                for riga in righe
            ]

            return articoli

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Errore durante il recupero degli articoli"
        )

    finally:
        if connessione:
            connessione.close()

@app.get("/articoli/{id_articolo}")
def mostra_articoli_id(id_articolo: int):

    connessione = None

    try:
        connessione = connessione_database()

        with connessione.cursor() as cursore:
            cursore.execute("""
                SELECT id, codice, nome, prezzo, scorta_minima
                FROM ARTICOLI
                WHERE id = :id
            """, {"id" : id_articolo})

            risultato = cursore.fetchone()

            if risultato is None:
                raise HTTPException(
                    status_code=404,
                    detail="Articolo non trovato"
                )
            
            colonne = [colonna[0].lower() for colonna in cursore.description]
            return dict(zip(colonne, risultato))

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Errore durante il recupero degli articoli"
        )

    finally:
        if connessione:
            connessione.close()
