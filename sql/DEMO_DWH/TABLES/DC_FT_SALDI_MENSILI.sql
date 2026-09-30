--------------------------------------------------------------------------------
-- Motore      : DEMO_CONTI
-- Oggetto     : DEMO_DWH.DC_FT_SALDI_MENSILI
-- Tipo        : Tabella target (fatti) - saldi mensili
-- Descrizione : Per ogni conto e mese: saldo iniziale, entrate, uscite e saldo
--               finale (l'estratto conto). Conserva lo storico mensile per
--               ogni banca.
--               Partizioni mensili create in automatico (INTERVAL) e
--               sottopartizioni per istituto: il ricaricamento svuota solo la
--               coppia (mese, banca) in lavorazione.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE TABLE DEMO_DWH.DC_FT_SALDI_MENSILI
(
    COD_ISTITUTO       VARCHAR2(5 CHAR)    NOT NULL,
    DAT_RIFERIMENTO    DATE                NOT NULL,
    COD_CONTO          VARCHAR2(20 CHAR)   NOT NULL,
    IMP_SALDO_INIZIALE NUMBER(18,2)        NOT NULL,
    IMP_ENTRATE        NUMBER(18,2)        NOT NULL,
    IMP_USCITE         NUMBER(18,2)        NOT NULL,
    IMP_SALDO_FINALE   NUMBER(18,2)        NOT NULL,
    ID_ELABORAZIONE    NUMBER(12)          NOT NULL,
    DAT_CARICAMENTO    DATE                DEFAULT SYSDATE NOT NULL
)
TABLESPACE DEMO_DWH_DATA
PARTITION BY RANGE (DAT_RIFERIMENTO)
INTERVAL (NUMTOYMINTERVAL(1, 'MONTH'))
SUBPARTITION BY LIST (COD_ISTITUTO)
SUBPARTITION TEMPLATE
(
    SUBPARTITION SP_99001   VALUES ('99001'),
    SUBPARTITION SP_99002   VALUES ('99002'),
    SUBPARTITION SP_99003   VALUES ('99003'),
    SUBPARTITION SP_DEFAULT VALUES (DEFAULT)
)
(
    PARTITION P_INIZIALE VALUES LESS THAN (DATE '2026-01-01')
);

COMMENT ON TABLE  DEMO_DWH.DC_FT_SALDI_MENSILI                    IS 'DEMO_CONTI - Saldi mensili per conto (estratto conto)';
COMMENT ON COLUMN DEMO_DWH.DC_FT_SALDI_MENSILI.COD_ISTITUTO       IS 'Codice dell istituto (valori fittizi 99xxx) - chiave di sottopartizione';
COMMENT ON COLUMN DEMO_DWH.DC_FT_SALDI_MENSILI.DAT_RIFERIMENTO    IS 'Data di riferimento (ultimo giorno del mese) - chiave di partizione';
COMMENT ON COLUMN DEMO_DWH.DC_FT_SALDI_MENSILI.COD_CONTO          IS 'Codice del conto';
COMMENT ON COLUMN DEMO_DWH.DC_FT_SALDI_MENSILI.IMP_SALDO_INIZIALE IS 'Saldo a inizio mese: somma dei movimenti con data contabile precedente al mese';
COMMENT ON COLUMN DEMO_DWH.DC_FT_SALDI_MENSILI.IMP_ENTRATE        IS 'Somma dei movimenti che fanno entrare denaro nel mese';
COMMENT ON COLUMN DEMO_DWH.DC_FT_SALDI_MENSILI.IMP_USCITE         IS 'Somma dei movimenti che fanno uscire denaro nel mese (importo positivo)';
COMMENT ON COLUMN DEMO_DWH.DC_FT_SALDI_MENSILI.IMP_SALDO_FINALE   IS 'Saldo a fine mese: somma di tutti i movimenti fino all ultimo giorno del mese';
COMMENT ON COLUMN DEMO_DWH.DC_FT_SALDI_MENSILI.ID_ELABORAZIONE    IS 'Identificativo dell elaborazione (DC_LOG_ELABORAZIONI)';
COMMENT ON COLUMN DEMO_DWH.DC_FT_SALDI_MENSILI.DAT_CARICAMENTO    IS 'Data e ora di caricamento del record';
