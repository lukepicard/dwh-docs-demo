--------------------------------------------------------------------------------
-- Motore      : DEMO_CONTI
-- Oggetto     : DEMO_DWH.DC_FT_MOVIMENTI
-- Tipo        : Tabella target (fatti) - movimenti
-- Descrizione : Movimenti dei conti, senza doppioni, con la causale e il segno
--               (+ entra, - esce). Conserva lo storico mensile per ogni banca.
--               Partizioni mensili create in automatico (INTERVAL) e
--               sottopartizioni per istituto: si puo svuotare solo la
--               coppia (mese, banca) da rifare.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE TABLE DEMO_DWH.DC_FT_MOVIMENTI
(
    COD_ISTITUTO       VARCHAR2(5 CHAR)    NOT NULL,
    DAT_CONTABILE      DATE                NOT NULL,
    ID_MOVIMENTO       VARCHAR2(30 CHAR)   NOT NULL,
    COD_CONTO          VARCHAR2(20 CHAR)   NOT NULL,
    COD_CAUSALE        VARCHAR2(20 CHAR)   NOT NULL,
    COD_SEGNO          CHAR(1 CHAR)        NOT NULL,
    IMP_MOVIMENTO      NUMBER(18,2)        NOT NULL,
    IMP_CON_SEGNO      NUMBER(18,2)        NOT NULL,
    DAT_VALUTA         DATE                NOT NULL,
    ID_ELABORAZIONE    NUMBER(12)          NOT NULL,
    DAT_CARICAMENTO    DATE                DEFAULT SYSDATE NOT NULL
)
TABLESPACE DEMO_DWH_DATA
PARTITION BY RANGE (DAT_CONTABILE)
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

COMMENT ON TABLE  DEMO_DWH.DC_FT_MOVIMENTI                  IS 'DEMO_CONTI - Movimenti dei conti con causale e segno';
COMMENT ON COLUMN DEMO_DWH.DC_FT_MOVIMENTI.COD_ISTITUTO     IS 'Codice dell istituto (valori fittizi 99xxx) - chiave di sottopartizione';
COMMENT ON COLUMN DEMO_DWH.DC_FT_MOVIMENTI.DAT_CONTABILE    IS 'Data contabile del movimento - chiave di partizione (un mese per partizione)';
COMMENT ON COLUMN DEMO_DWH.DC_FT_MOVIMENTI.ID_MOVIMENTO     IS 'Identificativo del movimento nel sistema fonte (unico per istituto)';
COMMENT ON COLUMN DEMO_DWH.DC_FT_MOVIMENTI.COD_CONTO        IS 'Codice del conto';
COMMENT ON COLUMN DEMO_DWH.DC_FT_MOVIMENTI.COD_CAUSALE      IS 'Causale del movimento (DC_DIM_CAUSALE)';
COMMENT ON COLUMN DEMO_DWH.DC_FT_MOVIMENTI.COD_SEGNO        IS 'Segno della causale: + entra, - esce';
COMMENT ON COLUMN DEMO_DWH.DC_FT_MOVIMENTI.IMP_MOVIMENTO    IS 'Importo del movimento, sempre positivo';
COMMENT ON COLUMN DEMO_DWH.DC_FT_MOVIMENTI.IMP_CON_SEGNO    IS 'Importo con il segno: IMP_MOVIMENTO se entra, -IMP_MOVIMENTO se esce';
COMMENT ON COLUMN DEMO_DWH.DC_FT_MOVIMENTI.DAT_VALUTA       IS 'Data valuta: il giorno da cui decorrono gli interessi';
COMMENT ON COLUMN DEMO_DWH.DC_FT_MOVIMENTI.ID_ELABORAZIONE  IS 'Identificativo dell elaborazione che ha caricato il record';
COMMENT ON COLUMN DEMO_DWH.DC_FT_MOVIMENTI.DAT_CARICAMENTO  IS 'Data e ora di caricamento del record';
