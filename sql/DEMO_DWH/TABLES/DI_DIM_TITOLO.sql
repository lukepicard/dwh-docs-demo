--------------------------------------------------------------------------------
-- Motore      : DEMO_INVESTIMENTI
-- Oggetto     : DEMO_DWH.DI_DIM_TITOLO
-- Tipo        : Tabella di dimensione (anagrafica)
-- Descrizione : Anagrafica dei titoli: codice ISIN (inventato), descrizione e
--               tipo (AZIONE, OBBLIGAZIONE, FONDO).
--               Alimentata a mano (dati di configurazione), letta dal
--               workflow delle posizioni per calcolare il controvalore.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE TABLE DEMO_DWH.DI_DIM_TITOLO
(
    COD_TITOLO        VARCHAR2(12 CHAR)   NOT NULL,
    DES_TITOLO        VARCHAR2(100 CHAR)  NOT NULL,
    COD_TIPO          VARCHAR2(15 CHAR)   NOT NULL,
    DAT_INSERIMENTO   DATE                DEFAULT SYSDATE NOT NULL,
    COD_UTENTE_INS    VARCHAR2(30 CHAR)   DEFAULT USER NOT NULL
)
TABLESPACE DEMO_DWH_DATA;

COMMENT ON TABLE  DEMO_DWH.DI_DIM_TITOLO                 IS 'DEMO_INVESTIMENTI - Anagrafica dei titoli';
COMMENT ON COLUMN DEMO_DWH.DI_DIM_TITOLO.COD_TITOLO      IS 'Codice ISIN del titolo (valori inventati)';
COMMENT ON COLUMN DEMO_DWH.DI_DIM_TITOLO.DES_TITOLO      IS 'Descrizione del titolo';
COMMENT ON COLUMN DEMO_DWH.DI_DIM_TITOLO.COD_TIPO        IS 'Tipo di titolo: AZIONE, OBBLIGAZIONE o FONDO';
COMMENT ON COLUMN DEMO_DWH.DI_DIM_TITOLO.DAT_INSERIMENTO IS 'Data di inserimento del record';
COMMENT ON COLUMN DEMO_DWH.DI_DIM_TITOLO.COD_UTENTE_INS  IS 'Utente che ha inserito il record';
