--------------------------------------------------------------------------------
-- Motore      : DEMO_INVESTIMENTI
-- Oggetto     : DEMO_DWH.DI_FT_CONTROVALORI_MENSILI
-- Tipo        : Tabella target (fatti) - controvalori mensili
-- Descrizione : Per ogni dossier e mese, il controvalore dei titoli posseduti
--               a fine mese: quantita per prezzo di fine mese.
--               Conserva lo storico mensile per ogni banca.
--               Partizioni mensili create in automatico (INTERVAL) e
--               sottopartizioni per istituto: il ricaricamento svuota solo la
--               coppia (mese, banca) in lavorazione.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE TABLE DEMO_DWH.DI_FT_CONTROVALORI_MENSILI
(
    COD_ISTITUTO               VARCHAR2(5 CHAR)    NOT NULL,
    DAT_RIFERIMENTO            DATE                NOT NULL,
    COD_DOSSIER                VARCHAR2(20 CHAR)   NOT NULL,
    NUM_TITOLI                 NUMBER(9)           NOT NULL,
    NUM_TITOLI_PREZZO_RIPORTATO NUMBER(9)          NOT NULL,
    IMP_CONTROVALORE           NUMBER(18,2)        NOT NULL,
    ID_ELABORAZIONE            NUMBER(12)          NOT NULL,
    DAT_CARICAMENTO            DATE                DEFAULT SYSDATE NOT NULL
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

COMMENT ON TABLE  DEMO_DWH.DI_FT_CONTROVALORI_MENSILI                             IS 'DEMO_INVESTIMENTI - Controvalore dei titoli per dossier e mese';
COMMENT ON COLUMN DEMO_DWH.DI_FT_CONTROVALORI_MENSILI.COD_ISTITUTO                IS 'Codice dell istituto (valori fittizi 99xxx) - chiave di sottopartizione';
COMMENT ON COLUMN DEMO_DWH.DI_FT_CONTROVALORI_MENSILI.DAT_RIFERIMENTO             IS 'Data di riferimento (ultimo giorno del mese) - chiave di partizione';
COMMENT ON COLUMN DEMO_DWH.DI_FT_CONTROVALORI_MENSILI.COD_DOSSIER                 IS 'Codice del dossier titoli';
COMMENT ON COLUMN DEMO_DWH.DI_FT_CONTROVALORI_MENSILI.NUM_TITOLI                  IS 'Numero di titoli diversi posseduti a fine mese';
COMMENT ON COLUMN DEMO_DWH.DI_FT_CONTROVALORI_MENSILI.NUM_TITOLI_PREZZO_RIPORTATO IS 'Quanti di questi titoli sono valorizzati con un prezzo riportato da un giorno precedente';
COMMENT ON COLUMN DEMO_DWH.DI_FT_CONTROVALORI_MENSILI.IMP_CONTROVALORE            IS 'Somma di quantita per prezzo dei titoli del dossier (obbligazioni: diviso 100)';
COMMENT ON COLUMN DEMO_DWH.DI_FT_CONTROVALORI_MENSILI.ID_ELABORAZIONE             IS 'Identificativo dell elaborazione (DC_LOG_ELABORAZIONI)';
COMMENT ON COLUMN DEMO_DWH.DI_FT_CONTROVALORI_MENSILI.DAT_CARICAMENTO             IS 'Data e ora di caricamento del record';
