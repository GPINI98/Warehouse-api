from fastapi import FastAPI, HTTPException
from app.database import connessione_database
from app.schemas import ArticoloCreate

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

@app.post("/articoli", status_code=201)
def crea_articolo(articolo:ArticoloCreate):
    connessione = None

    try:
        connessione = connessione_database()

        with connessione.cursor() as cursore:
            cursore.execute("""
                INSERT INTO ARTICOLI (
                codice, nome, prezzo, scorta_minima
                )                
                VALUES (
                :codice, :nome, :prezzo, :scorta_minima
                )
                RETURNING id INTO :id 
                """, {
                    "codice" : articolo.codice,
                    "nome" : articolo.nome,
                    "prezzo" : articolo.prezzo,
                    "scorta_minima" : articolo.scorta_minima,
                    "id": cursore.var(int)
                    })

            nuovo_id = cursore.bindvars["id"].getvalue()

            connessione.commit()

            return {
                "id" : nuovo_id,
                "codice" : articolo.codice,
                "nome" : articolo.nome,
                "prezzo" : articolo.prezzo,
                "scorta_minima" : articolo.scorta_minima,
                }
        
    except Exception:
            if connessione:
                connessione.rollback()

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Errore durante il recupero degli articoli"
        )

    finally:
        if connessione:
            connessione.close()



@app.put("/articoli/{id_articolo}")
def modifica_articolo(id_articolo:int, articolo: ArticoloCreate):
    connessione = None

    try:
        connessione = connessione_database()

        with connessione.cursor() as cursore:
            cursore.execute("""
                UPDATE ARTICOLI 
                SET codice = :codice,
                    nome = :nome,
                    prezzo = :prezzo,
                    scorta_minima = :scorta_minima
                WHERE id = :id
                """, {
                    "codice": articolo.codice,
                    "nome": articolo.nome,
                    "prezzo": articolo.prezzo,
                    "scorta_minima": articolo.scorta_minima,
                    "id": id_articolo
                })
            if cursore.rowcount == 0: #rowcount -righe interessate dall'operazione
                raise HTTPException(
                    status_code=404,
                    detail="Articolo non trovato"
                )    
            connessione.commit()

            return {
                "messaggio":"Articolo aggiornato correttamente",
                "id": id_articolo,
                **articolo.model_dump()
                }
        
    except Exception:
        raise

    except Exception:
        if connessione:
            connessione.rollback()
            
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Errore durante il recupero degli articoli"
        )

    finally:
        if connessione:
            connessione.close()



@app.delete("/articoli/{id_articolo}")
def elimina_articolo(id_articolo:int):
    connessione = None

    try:
        connessione = connessione_database()

        with connessione.cursor() as cursore:
            cursore.execute("""
                DELETE FROM ARTICOLI 
                WHERE id = :id
                """, {"id": id_articolo})
            
            if cursore.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Articolo non trovato"
                )    
            connessione.commit()

            return {
                "messaggio":"Articolo eliminato correttamente",
                "id": id_articolo,
                }
        
    except Exception:
        raise

    except Exception:
        if connessione:
            connessione.rollback()
            
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Errore durante il recupero degli articoli"
        )

    finally:
        if connessione:
            connessione.close()