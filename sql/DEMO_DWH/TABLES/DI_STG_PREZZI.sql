--------------------------------------------------------------------------------
-- Motore      : DEMO_INVESTIMENTI
-- Oggetto     : DEMO_DWH.DI_STG_PREZZI
-- Tipo        : Tabella work (staging)
-- Descrizione : Prezzi di chiusura del giorno, uno per titolo, cosi come
--               arrivano dal sistema fonte, per l'ultimo giorno caricato di
--               ogni banca.
--               Partizionata per istituto: a ogni elaborazione si svuota
--               (TRUNCATE PARTITION) solo la banca in lavorazione.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE TABLE DEMO_DWH.DI_STG_PREZZI
(
    COD_ISTITUTO          VARCHAR2(5 CHAR)    NOT NULL,
    DAT_RIFERIMENTO       DATE                NOT NULL,
    COD_TITOLO            VARCHAR2(12 CHAR)   NOT NULL,
    IMP_PREZZO            NUMBER(18,6)        NOT NULL,
    COD_SISTEMA_FONTE     VARCHAR2(10 CHAR)   NOT NULL,
    ID_ELABORAZIONE       NUMBER(12)          NOT NULL,
    DAT_CARICAMENTO       DATE                DEFAULT SYSDATE NOT NULL
)
TABLESPACE DEMO_DWH_DATA
NOLOGGING
PARTITION BY LIST (COD_ISTITUTO)
(
    PARTITION P_99001   VALUES ('99001'),
    PARTITION P_99002   VALUES ('99002'),
    PARTITION P_99003   VALUES ('99003'),
    PARTITION P_DEFAULT VALUES (DEFAULT)
);

COMMENT ON TABLE  DEMO_DWH.DI_STG_PREZZI                   IS 'DEMO_INVESTIMENTI - Staging dei prezzi di chiusura dal sistema fonte';
COMMENT ON COLUMN DEMO_DWH.DI_STG_PREZZI.COD_ISTITUTO      IS 'Codice dell istituto (valori fittizi 99xxx)';
COMMENT ON COLUMN DEMO_DWH.DI_STG_PREZZI.DAT_RIFERIMENTO   IS 'Data di riferimento (il giorno del prezzo di chiusura)';
COMMENT ON COLUMN DEMO_DWH.DI_STG_PREZZI.COD_TITOLO        IS 'Codice ISIN del titolo, normalizzato (UPPER/TRIM) dalla Post SQL del carico';
COMMENT ON COLUMN DEMO_DWH.DI_STG_PREZZI.IMP_PREZZO        IS 'Prezzo di chiusura (per le obbligazioni in percentuale del valore nominale)';
COMMENT ON COLUMN DEMO_DWH.DI_STG_PREZZI.COD_SISTEMA_FONTE IS 'Sistema fonte che ha inviato il record (es. FONTE_C)';
COMMENT ON COLUMN DEMO_DWH.DI_STG_PREZZI.ID_ELABORAZIONE   IS 'Identificativo dell elaborazione che ha caricato il record';
COMMENT ON COLUMN DEMO_DWH.DI_STG_PREZZI.DAT_CARICAMENTO   IS 'Data e ora di caricamento del record';
