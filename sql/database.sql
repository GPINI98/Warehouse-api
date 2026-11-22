-- CREAZIONE TABELLA ARTICOLI

CREATE TABLE ARTICOLI (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codice VARCHAR2(30) NOT NULL UNIQUE,
    nome VARCHAR2(100) NOT NULL,
    prezzo NUMBER(10,2) NOT NULL,
    scorta_minima NUMBER DEFAULT 0 NOT NULL,

    CONSTRAINT chk_prezzo CHECK (prezzo >= 0),
    CONSTRAINT chk_scorta CHECK (scorta_minima >= 0)
);

-- CREAZIONE TABELLA MOVIMENTI

CREATE TABLE MOVIMENTI (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    articolo_id NUMBER NOT NULL,
    tipo CHAR(1) NOT NULL,
    quantita NUMBER NOT NULL,
    data_movimento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    note VARCHAR2(200),

    CONSTRAINT fk_articolo
        FOREIGN KEY (articolo_id)
        REFERENCES ARTICOLI(id),

    CONSTRAINT chk_tipo
        CHECK (tipo IN ('C', 'S')),

    CONSTRAINT chk_quantita
        CHECK (quantita > 0)
);
