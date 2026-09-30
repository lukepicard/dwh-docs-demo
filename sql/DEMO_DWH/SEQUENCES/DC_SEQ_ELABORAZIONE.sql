--------------------------------------------------------------------------------
-- Motore      : DEMO_CONTI
-- Oggetto     : DEMO_DWH.DC_SEQ_ELABORAZIONE
-- Descrizione : Genera ID_ELABORAZIONE per DC_LOG_ELABORAZIONI.
--               Usata da DC_PKG_ELABORAZIONE.APRI.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE SEQUENCE DEMO_DWH.DC_SEQ_ELABORAZIONE
    START WITH 1
    INCREMENT BY 1
    CACHE 20
    NOCYCLE;
