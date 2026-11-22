from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, MagicMock
import oracledb

client = TestClient(app)


def test_home():
    risposta = client.get("/")

    assert risposta.status_code == 200
    assert risposta.json() == {
        "messaggio": "Warehouse API attiva"
    }


def test_creazione_articolo_dati_non_validi():
    risposta = client.post(
        "/articoli",
        json={
            "codice": "ART100",
            "nome": "Mouse wireless",
            "prezzo": -10,
            "scorta_minima": 5
        }
    )

    assert risposta.status_code == 422


def test_creazione_movimento_tipo_non_valido():
    risposta = client.post(
        "/movimenti",
        json={
            "articolo_id": 1,
            "tipo": "X",
            "quantita": 10
        }
    )

    assert risposta.status_code == 422

def test_mostra_articoli():

    risultati = [
        (1, "ART001", "Mouse Logitech", 24.90, 5),
        (2, "ART002", "Tastiera Logitech", 49.90, 3)
    ]

    connessione_finta = MagicMock()
    cursore_finto = MagicMock()
    connessione_finta.cursor.return_value.__enter__.return_value = cursore_finto
    cursore_finto.description = [
        ("ID",),
        ("CODICE",),
        ("NOME",),
        ("PREZZO",),
        ("SCORTA_MINIMA",)
    ]

    cursore_finto.fetchall.return_value = risultati

    with patch("app.main.connessione_database", return_value=connessione_finta):

        risposta = client.get("/articoli")

    assert risposta.status_code == 200
    assert len(risposta.json()) == 2
    assert risposta.json()[0]["nome"] == "Mouse Logitech"

def test_errore_connessione_database():

    with patch("app.main.connessione_database", side_effect=Exception("Errore di connessione")):
        risposta = client.get("/articoli")

    assert risposta.status_code == 500
    assert risposta.json() == {
        "detail": "Errore durante il recupero degli articoli"
    }


def test_creazione_articolo():

    connessione_finta = MagicMock()
    cursore_finto = MagicMock()

    connessione_finta.cursor.return_value.__enter__.return_value = cursore_finto

    cursore_finto.bindvars = {"id": MagicMock()}
    cursore_finto.bindvars["id"].getvalue.return_value = 5

    dati = {
        "codice": "ART100",
        "nome": "Mouse wireless",
        "prezzo": 29.90,
        "scorta_minima": 5
    }

    with patch("app.main.connessione_database", return_value=connessione_finta):
        risposta = client.post("/articoli", json=dati)

    assert risposta.status_code == 201
    assert risposta.json()["id"] == 5
    assert risposta.json()["codice"] == "ART100"

    connessione_finta.commit.assert_called_once()


def test_creazione_articolo_errore_database():

    connessione_finta = MagicMock()
    cursore_finto = MagicMock()

    connessione_finta.cursor.return_value.__enter__.return_value = cursore_finto

    cursore_finto.execute.side_effect = Exception("Errore database")

    dati = {
        "codice": "ART101",
        "nome": "Tastiera wireless",
        "prezzo": 49.90,
        "scorta_minima": 3
    }

    with patch("app.main.connessione_database", return_value=connessione_finta):
        
        risposta = client.post("/articoli", json=dati)

    print("Execute chiamato:", cursore_finto.execute.call_count)
    print("Commit chiamato:", connessione_finta.commit.call_count)
    print("Rollback chiamato:", connessione_finta.rollback.call_count)
    assert risposta.status_code == 500

    connessione_finta.rollback.assert_called_once()
    connessione_finta.commit.assert_not_called()


def test_creazione_articolo_codice_duplicato():

    connessione_finta = MagicMock()
    cursore_finto = MagicMock()

    connessione_finta.cursor.return_value.__enter__.return_value = cursore_finto

    errore_oracle = MagicMock()
    errore_oracle.code = 1

    cursore_finto.execute.side_effect = oracledb.DatabaseError(
        errore_oracle
    )

    dati = {
        "codice": "ART001",
        "nome": "Mouse duplicato",
        "prezzo": 29.90,
        "scorta_minima": 5
    }

    with patch(
        "app.main.connessione_database",
        return_value=connessione_finta
    ):
        risposta = client.post("/articoli", json=dati)

    assert risposta.status_code == 409
    assert risposta.json() == {
        "detail": "Codice articolo già esistente"
    }

    connessione_finta.rollback.assert_called_once()
    connessione_finta.commit.assert_not_called()



def test_creazione_movimento_articolo_inesistente():
    connessione_finta = MagicMock()
    cursore_finto = MagicMock()

    connessione_finta.cursor.return_value.__enter__.return_value = cursore_finto

    # Simuliamo un articolo che non esiste
    cursore_finto.fetchone.return_value = None

    dati = {
        "articolo_id": 999,
        "tipo": "C",
        "quantita": 5,
        "note": "Test articolo inesistente"
    }

    with patch(
        "app.main.connessione_database",
        return_value=connessione_finta
    ):
        risposta = client.post("/movimenti", json=dati)

    assert risposta.status_code == 404
    assert risposta.json() == {"detail": "Articolo non trovato"}

    connessione_finta.commit.assert_not_called()



def test_creazione_movimento_giacenza_insufficiente():
    connessione_finta = MagicMock()
    cursore_finto = MagicMock()

    connessione_finta.cursor.return_value.__enter__.return_value = cursore_finto

    # Prima fetchone: articolo esistente
    # Seconda fetchone: giacenza attuale pari a 3
    cursore_finto.fetchone.side_effect = [(21,), (3,)]

    dati = {
        "articolo_id": 21,
        "tipo": "S",
        "quantita": 10,
        "note": "Test giacenza insufficiente"
    }

    with patch("app.main.connessione_database", return_value=connessione_finta):
        risposta = client.post("/movimenti", json=dati)

    assert risposta.status_code == 409
    assert risposta.json() == {"detail": "Giacenza insufficiente"}

    # Non deve essere registrato alcun movimento
    assert cursore_finto.execute.call_count == 2
    connessione_finta.commit.assert_not_called()


def test_creazione_movimento():
    connessione_finta = MagicMock()
    cursore_finto = MagicMock()

    connessione_finta.cursor.return_value.__enter__.return_value = cursore_finto

    # Articolo esistente e giacenza attuale pari a 3
    cursore_finto.fetchone.side_effect = [(21,), (3,)]

    # Simuliamo l'ID generato da Oracle
    cursore_finto.bindvars = {"id": MagicMock()}
    cursore_finto.bindvars["id"].getvalue.return_value = 100

    dati = {
        "articolo_id": 21,
        "tipo": "C",
        "quantita": 5,
        "note": "Test carico"
    }

    with patch("app.main.connessione_database", return_value=connessione_finta):
        risposta = client.post("/movimenti", json=dati)

    assert risposta.status_code == 201
    assert risposta.json()["id"] == 100
    assert risposta.json()["articolo_id"] == 21
    assert risposta.json()["tipo"] == "C"
    assert risposta.json()["quantita"] == 5

    # Verifichiamo che il movimento sia stato registrato
    assert cursore_finto.execute.call_count == 3
    connessione_finta.commit.assert_called_once()
    connessione_finta.rollback.assert_not_called()


def test_creazione_movimento_errore_database():
    connessione_finta = MagicMock()
    cursore_finto = MagicMock()

    connessione_finta.cursor.return_value.__enter__.return_value = cursore_finto

    # Articolo esistente e giacenza pari a 3
    cursore_finto.fetchone.side_effect = [(21,), (3,)]

    # Simuliamo un errore durante l'INSERT (terza execute)
    cursore_finto.execute.side_effect = [
        None,
        None,
        Exception("Errore database")
    ]

    dati = {
        "articolo_id": 21,
        "tipo": "C",
        "quantita": 5,
        "note": "Test errore database"
    }

    with patch("app.main.connessione_database", return_value=connessione_finta):
        risposta = client.post("/movimenti", json=dati)

    assert risposta.status_code == 500
    assert risposta.json() == {
        "detail": "Errore durante la registrazione del movimento"
    }

    connessione_finta.rollback.assert_called_once()
    connessione_finta.commit.assert_not_called()


def test_elimina_articolo():
    connessione_finta = MagicMock()
    cursore_finto = MagicMock()

    connessione_finta.cursor.return_value.__enter__.return_value = cursore_finto
    cursore_finto.rowcount = 1

    with patch("app.main.connessione_database", return_value=connessione_finta):
        risposta = client.delete("/articoli/21")

    assert risposta.status_code == 200
    assert risposta.json() == {
        "messaggio": "Articolo eliminato correttamente",
        "id": 21
    }

    connessione_finta.commit.assert_called_once()
    connessione_finta.rollback.assert_not_called()



def test_elimina_articolo_inesistente():
    connessione_finta = MagicMock()
    cursore_finto = MagicMock()

    connessione_finta.cursor.return_value.__enter__.return_value = cursore_finto

    # Simuliamo che nessuna riga sia stata eliminata
    cursore_finto.rowcount = 0

    with patch("app.main.connessione_database", return_value=connessione_finta):
        risposta = client.delete("/articoli/999")

    assert risposta.status_code == 404
    assert risposta.json() == {
        "detail": "Articolo non trovato"
    }

    connessione_finta.commit.assert_not_called()
    connessione_finta.rollback.assert_called_once()


def test_elimina_articolo_con_movimenti_collegati():
    connessione_finta = MagicMock()
    cursore_finto = MagicMock()

    connessione_finta.cursor.return_value.__enter__.return_value = cursore_finto

    errore_oracle = MagicMock()
    errore_oracle.code = 2292

    cursore_finto.execute.side_effect = oracledb.DatabaseError(errore_oracle)

    with patch("app.main.connessione_database", return_value=connessione_finta):
        risposta = client.delete("/articoli/21")

    assert risposta.status_code == 409
    assert risposta.json() == {
        "detail": "Impossibile eliminare l'articolo: sono presenti movimenti collegati"
    }

    connessione_finta.rollback.assert_called_once()
    connessione_finta.commit.assert_not_called()
