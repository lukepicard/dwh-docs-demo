--------------------------------------------------------------------------------
-- Motore      : DEMO_CONTI
-- Oggetto     : DEMO_DWH.DC_DIM_CAUSALE
-- Tipo        : Tabella di dimensione (anagrafica)
-- Descrizione : Causali dei movimenti (bonifico, stipendio, prelievo, ...), con
--               il segno che hanno sul saldo: + entra, - esce.
--               Alimentata a mano (dati di configurazione), letta dal
--               workflow dei movimenti.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE TABLE DEMO_DWH.DC_DIM_CAUSALE
(
    COD_CAUSALE           VARCHAR2(20 CHAR)   NOT NULL,
    DES_CAUSALE           VARCHAR2(100 CHAR)  NOT NULL,
    COD_SEGNO             CHAR(1 CHAR)        NOT NULL,
    DAT_INIZIO_VALIDITA   DATE                NOT NULL,
    DAT_FINE_VALIDITA     DATE                DEFAULT DATE '9999-12-31' NOT NULL,
    DAT_INSERIMENTO       DATE                DEFAULT SYSDATE NOT NULL,
    COD_UTENTE_INS        VARCHAR2(30 CHAR)   DEFAULT USER NOT NULL
)
TABLESPACE DEMO_DWH_DATA;

COMMENT ON TABLE  DEMO_DWH.DC_DIM_CAUSALE                     IS 'DEMO_CONTI - Anagrafica delle causali dei movimenti';
COMMENT ON COLUMN DEMO_DWH.DC_DIM_CAUSALE.COD_CAUSALE         IS 'Codice della causale (es. BONIFICO_IN, STIPENDIO, POS)';
COMMENT ON COLUMN DEMO_DWH.DC_DIM_CAUSALE.DES_CAUSALE         IS 'Descrizione della causale';
COMMENT ON COLUMN DEMO_DWH.DC_DIM_CAUSALE.COD_SEGNO           IS 'Segno sul saldo: + il movimento fa entrare denaro, - lo fa uscire';
COMMENT ON COLUMN DEMO_DWH.DC_DIM_CAUSALE.DAT_INIZIO_VALIDITA IS 'Data di inizio validita della causale';
COMMENT ON COLUMN DEMO_DWH.DC_DIM_CAUSALE.DAT_FINE_VALIDITA   IS 'Data di fine validita (9999-12-31 = attiva)';
COMMENT ON COLUMN DEMO_DWH.DC_DIM_CAUSALE.DAT_INSERIMENTO     IS 'Data di inserimento del record';
COMMENT ON COLUMN DEMO_DWH.DC_DIM_CAUSALE.COD_UTENTE_INS      IS 'Utente che ha inserito il record';
