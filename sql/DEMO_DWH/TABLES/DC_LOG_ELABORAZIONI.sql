--------------------------------------------------------------------------------
-- Motore      : DEMO_CONTI (usata anche da DEMO_INVESTIMENTI)
-- Oggetto     : DEMO_DWH.DC_LOG_ELABORAZIONI
-- Tipo        : Tabella di log
-- Descrizione : Una riga per ogni esecuzione di un flusso del motore su una
--               banca e una data di riferimento. Lo stato passa da
--               'running' a 'succeeded' o 'failed'. L'identificativo
--               finisce in ID_ELABORAZIONE delle tabelle alimentate.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE TABLE DEMO_DWH.DC_LOG_ELABORAZIONI
(
    ID_ELABORAZIONE       NUMBER(12)          NOT NULL,
    COD_FLUSSO            VARCHAR2(30 CHAR)   NOT NULL,
    COD_ISTITUTO          VARCHAR2(5 CHAR)    NOT NULL,
    DAT_RIFERIMENTO       DATE                NOT NULL,
    COD_STATO             VARCHAR2(10 CHAR)   NOT NULL,
    FLG_FORZA             CHAR(1 CHAR)        DEFAULT 'N' NOT NULL,
    DAT_INIZIO            DATE                DEFAULT SYSDATE NOT NULL,
    DAT_FINE              DATE,
    DES_ERRORE            VARCHAR2(4000 CHAR),
    COD_UTENTE_OS         VARCHAR2(30 CHAR)
)
TABLESPACE DEMO_DWH_DATA;

COMMENT ON TABLE  DEMO_DWH.DC_LOG_ELABORAZIONI                 IS 'DEMO_CONTI - Log delle esecuzioni dei flussi';
COMMENT ON COLUMN DEMO_DWH.DC_LOG_ELABORAZIONI.ID_ELABORAZIONE IS 'Identificativo dell elaborazione (sequence DC_SEQ_ELABORAZIONE)';
COMMENT ON COLUMN DEMO_DWH.DC_LOG_ELABORAZIONI.COD_FLUSSO      IS 'Flusso eseguito (DC_CARICO, DC_MOVIMENTI, DC_SALDI, DI_CARICO, DI_POSIZIONI)';
COMMENT ON COLUMN DEMO_DWH.DC_LOG_ELABORAZIONI.COD_ISTITUTO    IS 'Codice dell istituto elaborato';
COMMENT ON COLUMN DEMO_DWH.DC_LOG_ELABORAZIONI.DAT_RIFERIMENTO IS 'Data di riferimento elaborata';
COMMENT ON COLUMN DEMO_DWH.DC_LOG_ELABORAZIONI.COD_STATO       IS 'running / succeeded / failed';
COMMENT ON COLUMN DEMO_DWH.DC_LOG_ELABORAZIONI.FLG_FORZA       IS 'S = lanciata con FORZA (semaforo saltato)';
COMMENT ON COLUMN DEMO_DWH.DC_LOG_ELABORAZIONI.DAT_INIZIO      IS 'Inizio dell elaborazione';
COMMENT ON COLUMN DEMO_DWH.DC_LOG_ELABORAZIONI.DAT_FINE        IS 'Fine dell elaborazione (vuota se ancora running)';
COMMENT ON COLUMN DEMO_DWH.DC_LOG_ELABORAZIONI.DES_ERRORE      IS 'Messaggio di errore se failed';
COMMENT ON COLUMN DEMO_DWH.DC_LOG_ELABORAZIONI.COD_UTENTE_OS   IS 'Utente di sistema operativo che ha lanciato la shell';
