--------------------------------------------------------------------------------
-- Motore      : DEMO_CONTI
-- Oggetto     : DEMO_DWH.DC_PRC_PULIZIA_STORICO
-- Tipo        : Procedura
-- Descrizione : Manutenzione mensile delle tabelle di controllo: cancella le
--               elaborazioni del log e le righe del semaforo piu vecchie di
--               p_mesi mesi, poi recupera lo spazio delle due tabelle.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE OR REPLACE PROCEDURE DEMO_DWH.DC_PRC_PULIZIA_STORICO
(
    p_mesi  IN NUMBER DEFAULT 24
)
IS
BEGIN
    -- Log: conta la data di esecuzione, non la data di riferimento elaborata
    DELETE FROM DEMO_DWH.DC_LOG_ELABORAZIONI
     WHERE DAT_INIZIO < ADD_MONTHS(TRUNC(SYSDATE), -p_mesi);

    -- Semaforo: conta la data di riferimento dei dati
    DELETE FROM DEMO_DWH.DC_CTL_SEMAFORO
     WHERE DAT_RIFERIMENTO < ADD_MONTHS(TRUNC(SYSDATE), -p_mesi);

    COMMIT;

    -- Recupero dello spazio: il nome della tabella e' costruito a runtime
    FOR t IN (SELECT 'DC_LOG_ELABORAZIONI' AS nome FROM DUAL
              UNION ALL
              SELECT 'DC_CTL_SEMAFORO' FROM DUAL)
    LOOP
        EXECUTE IMMEDIATE 'ALTER TABLE DEMO_DWH.' || t.nome || ' ENABLE ROW MOVEMENT';
        EXECUTE IMMEDIATE 'ALTER TABLE DEMO_DWH.' || t.nome || ' SHRINK SPACE';
    END LOOP;
END DC_PRC_PULIZIA_STORICO;
/
