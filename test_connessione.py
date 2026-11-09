from app.database import connessione_database

try:
    connessione = connessione_database()

    with connessione.cursor() as cursore:
        cursore.execute("SELECT 'Connessione riuscita!' FROM DUAL")
        risultato = cursore.fetchone()

        print(risultato[0])

    connessione.close()

except Exception as errore:
    print(f"Errore di connessione: {errore}")