--------------------------------------------------------------------------------
-- Motore      : DEMO_INVESTIMENTI
-- Oggetto     : DEMO_DWH.DI_STG_ORDINI
-- Tipo        : Tabella work (staging)
-- Descrizione : Ordini eseguiti nel giorno (acquisti e vendite di titoli),
--               cosi come arrivano dal sistema fonte, per l'ultimo giorno
--               caricato di ogni banca.
--               Partizionata per istituto: a ogni elaborazione si svuota
--               (TRUNCATE PARTITION) solo la banca in lavorazione.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE TABLE DEMO_DWH.DI_STG_ORDINI
(
    COD_ISTITUTO          VARCHAR2(5 CHAR)    NOT NULL,
    DAT_RIFERIMENTO       DATE                NOT NULL,
    ID_ORDINE             VARCHAR2(30 CHAR)   NOT NULL,
    COD_DOSSIER           VARCHAR2(20 CHAR)   NOT NULL,
    COD_TITOLO            VARCHAR2(12 CHAR)   NOT NULL,
    COD_OPERAZIONE        VARCHAR2(10 CHAR)   NOT NULL,
    QTA_ORDINE            NUMBER(18,4)        NOT NULL,
    IMP_PREZZO            NUMBER(18,6)        NOT NULL,
    COD_CONTO_ADDEBITO    VARCHAR2(20 CHAR),
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

COMMENT ON TABLE  DEMO_DWH.DI_STG_ORDINI                    IS 'DEMO_INVESTIMENTI - Staging degli ordini eseguiti dal sistema fonte';
COMMENT ON COLUMN DEMO_DWH.DI_STG_ORDINI.COD_ISTITUTO       IS 'Codice dell istituto (valori fittizi 99xxx)';
COMMENT ON COLUMN DEMO_DWH.DI_STG_ORDINI.DAT_RIFERIMENTO    IS 'Data di riferimento (il giorno a cui si riferisce il file)';
COMMENT ON COLUMN DEMO_DWH.DI_STG_ORDINI.ID_ORDINE          IS 'Identificativo dell ordine nel sistema fonte';
COMMENT ON COLUMN DEMO_DWH.DI_STG_ORDINI.COD_DOSSIER        IS 'Codice del dossier titoli';
COMMENT ON COLUMN DEMO_DWH.DI_STG_ORDINI.COD_TITOLO         IS 'Codice ISIN del titolo (DI_DIM_TITOLO)';
COMMENT ON COLUMN DEMO_DWH.DI_STG_ORDINI.COD_OPERAZIONE     IS 'ACQUISTO oppure VENDITA';
COMMENT ON COLUMN DEMO_DWH.DI_STG_ORDINI.QTA_ORDINE         IS 'Quantita di titoli comprata o venduta, sempre positiva';
COMMENT ON COLUMN DEMO_DWH.DI_STG_ORDINI.IMP_PREZZO         IS 'Prezzo di esecuzione (per le obbligazioni in percentuale del valore nominale)';
COMMENT ON COLUMN DEMO_DWH.DI_STG_ORDINI.COD_CONTO_ADDEBITO IS 'Conto su cui si regola l ordine (codice conto di DEMO_CONTI): DI_VC_REGOLAMENTO_ORDINI cerca su questo conto l addebito o l accredito';
COMMENT ON COLUMN DEMO_DWH.DI_STG_ORDINI.COD_SISTEMA_FONTE  IS 'Sistema fonte che ha inviato il record (es. FONTE_B)';
COMMENT ON COLUMN DEMO_DWH.DI_STG_ORDINI.ID_ELABORAZIONE    IS 'Identificativo dell elaborazione che ha caricato il record';
COMMENT ON COLUMN DEMO_DWH.DI_STG_ORDINI.DAT_CARICAMENTO    IS 'Data e ora di caricamento del record';
