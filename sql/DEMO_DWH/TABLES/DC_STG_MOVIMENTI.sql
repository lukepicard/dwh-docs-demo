--------------------------------------------------------------------------------
-- Motore      : DEMO_CONTI
-- Oggetto     : DEMO_DWH.DC_STG_MOVIMENTI
-- Tipo        : Tabella work (staging)
-- Descrizione : Movimenti dei conti caricati dal sistema fonte, cosi come
--               arrivano, per l'ultimo giorno caricato di ogni banca.
--               Partizionata per istituto: a ogni elaborazione si svuota
--               (TRUNCATE PARTITION) solo la banca in lavorazione.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE TABLE DEMO_DWH.DC_STG_MOVIMENTI
(
    COD_ISTITUTO          VARCHAR2(5 CHAR)    NOT NULL,
    DAT_RIFERIMENTO       DATE                NOT NULL,
    ID_MOVIMENTO          VARCHAR2(30 CHAR)   NOT NULL,
    COD_CONTO             VARCHAR2(20 CHAR)   NOT NULL,
    COD_CAUSALE           VARCHAR2(20 CHAR)   NOT NULL,
    DAT_CONTABILE         DATE                NOT NULL,
    DAT_VALUTA            DATE                NOT NULL,
    IMP_MOVIMENTO         NUMBER(18,2)        NOT NULL,
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

COMMENT ON TABLE  DEMO_DWH.DC_STG_MOVIMENTI                    IS 'DEMO_CONTI - Staging dei movimenti dal sistema fonte';
COMMENT ON COLUMN DEMO_DWH.DC_STG_MOVIMENTI.COD_ISTITUTO       IS 'Codice dell istituto (valori fittizi 99xxx)';
COMMENT ON COLUMN DEMO_DWH.DC_STG_MOVIMENTI.DAT_RIFERIMENTO    IS 'Data di riferimento (il giorno a cui si riferisce il file)';
COMMENT ON COLUMN DEMO_DWH.DC_STG_MOVIMENTI.ID_MOVIMENTO       IS 'Identificativo del movimento nel sistema fonte (puo comparire due volte nello stesso file: si deduplica in wf_DC_MOVIMENTI)';
COMMENT ON COLUMN DEMO_DWH.DC_STG_MOVIMENTI.COD_CONTO          IS 'Codice del conto';
COMMENT ON COLUMN DEMO_DWH.DC_STG_MOVIMENTI.COD_CAUSALE        IS 'Causale del movimento, normalizzata (UPPER/TRIM) dalla Post SQL del carico';
COMMENT ON COLUMN DEMO_DWH.DC_STG_MOVIMENTI.DAT_CONTABILE      IS 'Data contabile: il giorno in cui il movimento conta per il saldo';
COMMENT ON COLUMN DEMO_DWH.DC_STG_MOVIMENTI.DAT_VALUTA         IS 'Data valuta: il giorno da cui decorrono gli interessi (non conta per i saldi mensili)';
COMMENT ON COLUMN DEMO_DWH.DC_STG_MOVIMENTI.IMP_MOVIMENTO      IS 'Importo del movimento, sempre positivo: il segno lo dice la causale';
COMMENT ON COLUMN DEMO_DWH.DC_STG_MOVIMENTI.COD_SISTEMA_FONTE  IS 'Sistema fonte che ha inviato il record (es. FONTE_A)';
COMMENT ON COLUMN DEMO_DWH.DC_STG_MOVIMENTI.ID_ELABORAZIONE    IS 'Identificativo dell elaborazione che ha caricato il record';
COMMENT ON COLUMN DEMO_DWH.DC_STG_MOVIMENTI.DAT_CARICAMENTO    IS 'Data e ora di caricamento del record';
