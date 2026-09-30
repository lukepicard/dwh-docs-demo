--------------------------------------------------------------------------------
-- Motore      : DEMO_INVESTIMENTI
-- Oggetto     : DEMO_DWH.DI_FT_POSIZIONI
-- Tipo        : Tabella target (fatti) - posizioni
-- Descrizione : Quantita di ogni titolo in ogni dossier a fine giornata:
--               posizione iniziale, acquisti, vendite e posizione finale, con
--               il prezzo di chiusura del giorno. Conserva lo storico mensile
--               per ogni banca.
--               Partizioni mensili create in automatico (INTERVAL) e
--               sottopartizioni per istituto.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE TABLE DEMO_DWH.DI_FT_POSIZIONI
(
    COD_ISTITUTO          VARCHAR2(5 CHAR)    NOT NULL,
    DAT_RIFERIMENTO       DATE                NOT NULL,
    COD_DOSSIER           VARCHAR2(20 CHAR)   NOT NULL,
    COD_TITOLO            VARCHAR2(12 CHAR)   NOT NULL,
    QTA_INIZIALE          NUMBER(18,4)        NOT NULL,
    QTA_ACQUISTI          NUMBER(18,4)        NOT NULL,
    QTA_VENDITE           NUMBER(18,4)        NOT NULL,
    QTA_FINALE            NUMBER(18,4)        NOT NULL,
    IMP_PREZZO            NUMBER(18,6),
    FLG_PREZZO_RIPORTATO  CHAR(1 CHAR)        NOT NULL,
    ID_ELABORAZIONE       NUMBER(12)          NOT NULL,
    DAT_CARICAMENTO       DATE                DEFAULT SYSDATE NOT NULL
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

COMMENT ON TABLE  DEMO_DWH.DI_FT_POSIZIONI                      IS 'DEMO_INVESTIMENTI - Posizioni per dossier e titolo a fine giornata';
COMMENT ON COLUMN DEMO_DWH.DI_FT_POSIZIONI.COD_ISTITUTO         IS 'Codice dell istituto (valori fittizi 99xxx) - chiave di sottopartizione';
COMMENT ON COLUMN DEMO_DWH.DI_FT_POSIZIONI.DAT_RIFERIMENTO      IS 'Giorno della posizione - chiave di partizione (un mese per partizione)';
COMMENT ON COLUMN DEMO_DWH.DI_FT_POSIZIONI.COD_DOSSIER          IS 'Codice del dossier titoli';
COMMENT ON COLUMN DEMO_DWH.DI_FT_POSIZIONI.COD_TITOLO           IS 'Codice ISIN del titolo (DI_DIM_TITOLO)';
COMMENT ON COLUMN DEMO_DWH.DI_FT_POSIZIONI.QTA_INIZIALE         IS 'Quantita a inizio giornata: la posizione finale dell ultimo giorno precedente';
COMMENT ON COLUMN DEMO_DWH.DI_FT_POSIZIONI.QTA_ACQUISTI         IS 'Quantita acquistata nella giornata';
COMMENT ON COLUMN DEMO_DWH.DI_FT_POSIZIONI.QTA_VENDITE          IS 'Quantita venduta nella giornata';
COMMENT ON COLUMN DEMO_DWH.DI_FT_POSIZIONI.QTA_FINALE           IS 'Quantita a fine giornata: QTA_INIZIALE + QTA_ACQUISTI - QTA_VENDITE';
COMMENT ON COLUMN DEMO_DWH.DI_FT_POSIZIONI.IMP_PREZZO           IS 'Prezzo di chiusura usato per la riga (vuoto se il titolo non e mai stato quotato)';
COMMENT ON COLUMN DEMO_DWH.DI_FT_POSIZIONI.FLG_PREZZO_RIPORTATO IS 'S = il prezzo del giorno mancava e si e usato l ultimo disponibile, N = prezzo del giorno';
COMMENT ON COLUMN DEMO_DWH.DI_FT_POSIZIONI.ID_ELABORAZIONE      IS 'Identificativo dell elaborazione che ha caricato il record';
COMMENT ON COLUMN DEMO_DWH.DI_FT_POSIZIONI.DAT_CARICAMENTO      IS 'Data e ora di caricamento del record';
