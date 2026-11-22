from fastapi import FastAPI, HTTPException
from app.database import connessione_database
from app.schemas import ArticoloCreate, MovimentoCreate
import oracledb

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
        
    except oracledb.DatabaseError as errore:
        if connessione:
            connessione.rollback()

        codice_errore = errore.args[0].code

        if codice_errore == 1:
            raise HTTPException(
                status_code=409,
                detail="Codice articolo già esistente"
            )

        raise HTTPException(
            status_code=500,
            detail="Errore durante la creazione dell'articolo"
        )

    except Exception:
        if connessione:
            connessione.rollback()

        raise HTTPException(
            status_code=500,
            detail="Errore durante la creazione dell'articolo"
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
        

    except HTTPException:
        if connessione:
            connessione.rollback()
        raise

    except oracledb.DatabaseError as errore:
        if connessione:
            connessione.rollback()

        codice_errore = errore.args[0].code

        if codice_errore == 1:
            raise HTTPException(
                status_code=409,
                detail="Codice articolo già esistente"
            )

        raise HTTPException(
            status_code=500,
            detail="Errore durante la modifica dell'articolo"
        )

    except Exception:
        if connessione:
            connessione.rollback()

        raise HTTPException(
            status_code=500,
            detail="Errore durante la modifica dell'articolo"
        )

    finally:
        if connessione:
            connessione.close()




@app.delete("/articoli/{id_articolo}")
def elimina_articolo(id_articolo: int):
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
                "messaggio": "Articolo eliminato correttamente",
                "id": id_articolo
            }

    except HTTPException:
        if connessione:
            connessione.rollback()
        raise

    except oracledb.DatabaseError as errore:
        if connessione:
            connessione.rollback()

        codice_errore = errore.args[0].code

# record ancora referenziato da un'altra tabella
        if codice_errore == 2292:
            raise HTTPException(
                status_code=409,
                detail="Impossibile eliminare l'articolo: sono presenti movimenti collegati"
            )

        raise HTTPException(
            status_code=500,
            detail="Errore del database durante l'eliminazione dell'articolo"
        )

    except Exception:
        if connessione:
            connessione.rollback()

        raise HTTPException(
            status_code=500,
            detail="Errore durante l'eliminazione dell'articolo"
        )

    finally:
        if connessione:
            connessione.close()


@app.post("/movimenti", status_code=201)
def crea_movimento(movimento: MovimentoCreate):
    connessione = None

    try:
        connessione = connessione_database()

        with connessione.cursor() as cursore:

            # Verifichiamo che l'articolo esista
            cursore.execute("""
                SELECT id
                FROM ARTICOLI
                WHERE id = :id
                FOR UPDATE
            """, {"id": movimento.articolo_id})

            if cursore.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="Articolo non trovato"
                )

            # Verifichiamo la giacenza attuale
            cursore.execute("""
                SELECT NVL(
                    SUM(
                        CASE
                            WHEN tipo = 'C' THEN quantita
                            ELSE -quantita
                        END
                    ), 0
                )
                FROM MOVIMENTI
                WHERE articolo_id = :id
            """, {"id": movimento.articolo_id})

            giacenza = cursore.fetchone()[0]

            # Impediamo uno scarico superiore alla giacenza
            if movimento.tipo == "S" and movimento.quantita > giacenza:
                raise HTTPException(
                    status_code=409, #conflict
                    detail="Giacenza insufficiente"
                )

            # Registriamo il movimento
            cursore.execute("""
                INSERT INTO MOVIMENTI (
                    articolo_id,
                    tipo,
                    quantita,
                    note
                )
                VALUES (
                    :articolo_id,
                    :tipo,
                    :quantita,
                    :note
                )
                RETURNING id INTO :id
            """, {
                "articolo_id": movimento.articolo_id,
                "tipo": movimento.tipo,
                "quantita": movimento.quantita,
                "note": movimento.note,
                "id": cursore.var(int)
            })

            nuovo_id = cursore.bindvars["id"].getvalue()

            connessione.commit()

            return {
                "id": nuovo_id,
                **movimento.model_dump()
            }

    except HTTPException:
        if connessione:
            connessione.rollback()
        raise
    
    except oracledb.DatabaseError:
        if connessione:
            connessione.rollback()

        raise HTTPException(
            status_code=500,
            detail="Errore del database durante la registrazione del movimento"
        )

    except Exception:
        if connessione:
            connessione.rollback()

        raise HTTPException(
            status_code=500,
            detail="Errore durante la registrazione del movimento"
        )

    finally:
        if connessione:
            connessione.close()

        


@app.get("/movimenti")
def mostra_movimenti():
    connessione = None

    try:
        connessione = connessione_database()

        with connessione.cursor() as cursore:
            cursore.execute("""
                SELECT
                    M.id,
                    M.articolo_id,
                    A.nome AS articolo,
                    M.tipo,
                    M.quantita,
                    M.data_movimento,
                    M.note
                FROM MOVIMENTI M
                JOIN ARTICOLI A
                    ON M.articolo_id = A.id
                ORDER BY M.data_movimento DESC
            """)

            colonne = [
                colonna[0].lower()
                for colonna in cursore.description
            ]

            righe = cursore.fetchall()

            movimenti = [
                dict(zip(colonne, riga))
                for riga in righe
            ]

            return movimenti
        
    except Exception as errore:
        print(f"Errore dettagliato: {errore}")
    # except Exception:
        raise HTTPException(
            status_code=500,
            detail="Errore durante il recupero dei movimenti"
        )

    finally:
        if connessione:
            connessione.close()


@app.get("/articoli/{id_articolo}/giacenza")
def mostra_giacenza(id_articolo: int):
    connessione = None

    try:
        connessione = connessione_database()

        with connessione.cursor() as cursore:

            cursore.execute("""
                SELECT id, nome
                FROM ARTICOLI
                WHERE id = :id
            """, {"id": id_articolo})

            articolo = cursore.fetchone()

            if articolo is None:
                raise HTTPException(
                    status_code=404,
                    detail="Articolo non trovato"
                )

            cursore.execute("""
                SELECT NVL(
                    SUM(
                        CASE
                            WHEN tipo = 'C' THEN quantita
                            ELSE -quantita
                        END
                    ), 0
                )
                FROM MOVIMENTI
                WHERE articolo_id = :id
            """, {"id": id_articolo})

            giacenza = cursore.fetchone()[0]

            return {
                "articolo_id": articolo[0],
                "nome": articolo[1],
                "giacenza": giacenza
            }

    except HTTPException:
        raise

    except Exception as errore:
        print(f"Errore dettagliato: {errore}")

        raise HTTPException(
            status_code=500,
            detail="Errore durante il calcolo della giacenza"
        )

    finally:
        if connessione:
            connessione.close()

@app.get("/statistiche")
def mostra_statistiche():
    connessione = None

    try:
        connessione = connessione_database()

        with connessione.cursor() as cursore:

            # Conteggio articoli e movimenti
            cursore.execute("""
                SELECT
                    (SELECT COUNT(*) FROM ARTICOLI),
                    (SELECT COUNT(*) FROM MOVIMENTI)
                FROM DUAL
            """)

            totale_articoli, totale_movimenti = cursore.fetchone()

            # Calcolo delle giacenze
            cursore.execute("""
                SELECT
                    NVL(SUM(giacenza), 0),
                    NVL(SUM(
                        CASE
                            WHEN giacenza <= scorta_minima
                            THEN 1
                            ELSE 0
                        END
                    ), 0)
                FROM (
                    SELECT
                        A.id,
                        A.scorta_minima,
                        NVL(SUM(
                            CASE
                                WHEN M.tipo = 'C' THEN M.quantita
                                ELSE -M.quantita
                            END
                        ), 0) AS giacenza
                    FROM ARTICOLI A
                    LEFT JOIN MOVIMENTI M
                        ON A.id = M.articolo_id
                    GROUP BY A.id, A.scorta_minima
                )
            """)

            quantita_totale, articoli_sotto_scorta = cursore.fetchone()

            return {
                "totale_articoli": totale_articoli,
                "totale_movimenti": totale_movimenti,
                "quantita_totale": quantita_totale,
                "articoli_sotto_scorta": articoli_sotto_scorta
            }

    except Exception as errore:
        print(f"Errore dettagliato: {errore}")

        raise HTTPException(
            status_code=500,
            detail="Errore durante il recupero delle statistiche"
        )

    finally:
        if connessione:
            connessione.close()