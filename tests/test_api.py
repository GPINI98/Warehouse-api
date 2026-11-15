from fastapi.testclient import TestClient
from app.main import app

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