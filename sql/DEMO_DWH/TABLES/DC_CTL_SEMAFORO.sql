--------------------------------------------------------------------------------
-- Motore      : DEMO_CONTI (usata anche da DEMO_INVESTIMENTI)
-- Oggetto     : DEMO_DWH.DC_CTL_SEMAFORO
-- Tipo        : Tabella di controllo
-- Descrizione : Semaforo dei flussi del motore. Una riga per ogni fonte da
--               cui dipende un flusso, per banca e data di riferimento.
--               Un flusso puo partire solo quando tutte le sue fonti sono
--               pronte (FLG_PRONTO = 'S'). Letta da DC_FN_SEMAFORO, scritta
--               da DC_PKG_ELABORAZIONE.SEGNA_PRONTO.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE TABLE DEMO_DWH.DC_CTL_SEMAFORO
(
    COD_FLUSSO            VARCHAR2(30 CHAR)   NOT NULL,
    COD_FONTE             VARCHAR2(30 CHAR)   NOT NULL,
    COD_ISTITUTO          VARCHAR2(5 CHAR)    NOT NULL,
    DAT_RIFERIMENTO       DATE                NOT NULL,
    FLG_PRONTO            CHAR(1 CHAR)        DEFAULT 'N' NOT NULL,
    DAT_AGGIORNAMENTO     DATE                DEFAULT SYSDATE NOT NULL,
    COD_UTENTE_AGG        VARCHAR2(30 CHAR)   DEFAULT USER NOT NULL
)
TABLESPACE DEMO_DWH_DATA;

COMMENT ON TABLE  DEMO_DWH.DC_CTL_SEMAFORO                   IS 'DEMO_CONTI - Semaforo dei flussi per fonte, banca e data';
COMMENT ON COLUMN DEMO_DWH.DC_CTL_SEMAFORO.COD_FLUSSO        IS 'Flusso che attende la fonte (DC_CARICO, DC_MOVIMENTI, DC_SALDI, DI_CARICO, DI_POSIZIONI)';
COMMENT ON COLUMN DEMO_DWH.DC_CTL_SEMAFORO.COD_FONTE         IS 'Fonte attesa: sistema esterno (FONTE_A, FONTE_B, FONTE_C) o flusso a monte (es. DC_CARICO)';
COMMENT ON COLUMN DEMO_DWH.DC_CTL_SEMAFORO.COD_ISTITUTO      IS 'Codice dell istituto (valori fittizi 99xxx)';
COMMENT ON COLUMN DEMO_DWH.DC_CTL_SEMAFORO.DAT_RIFERIMENTO   IS 'Data di riferimento (il giorno del file; per i saldi l ultimo giorno del mese)';
COMMENT ON COLUMN DEMO_DWH.DC_CTL_SEMAFORO.FLG_PRONTO        IS 'S = fonte pronta, N = non ancora disponibile';
COMMENT ON COLUMN DEMO_DWH.DC_CTL_SEMAFORO.DAT_AGGIORNAMENTO IS 'Data e ora dell ultimo aggiornamento';
COMMENT ON COLUMN DEMO_DWH.DC_CTL_SEMAFORO.COD_UTENTE_AGG    IS 'Utente che ha aggiornato la riga';
