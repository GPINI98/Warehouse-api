import pytest
from pydantic import ValidationError

from app.schemas import ArticoloCreate, MovimentoCreate


def test_articolo_valido():
    articolo = ArticoloCreate(
        codice="ART100",
        nome="Mouse wireless",
        prezzo=29.90,
        scorta_minima=5
    )

    assert articolo.codice == "ART100"
    assert articolo.nome == "Mouse wireless"
    assert articolo.scorta_minima == 5


def test_articolo_prezzo_negativo():
    with pytest.raises(ValidationError):
        ArticoloCreate(
            codice="ART100",
            nome="Mouse wireless",
            prezzo=-10,
            scorta_minima=5
        )


def test_movimento_valido():
    movimento = MovimentoCreate(
        articolo_id=1,
        tipo="C",
        quantita=10,
        note="Rifornimento"
    )

    assert movimento.articolo_id == 1
    assert movimento.tipo == "C"
    assert movimento.quantita == 10


def test_movimento_tipo_non_valido():
    with pytest.raises(ValidationError):
        MovimentoCreate(
            articolo_id=1,
            tipo="X",
            quantita=10
        )


def test_movimento_quantita_negativa():
    with pytest.raises(ValidationError):
        MovimentoCreate(
            articolo_id=1,
            tipo="S",
            quantita=-5
        )