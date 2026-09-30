--------------------------------------------------------------------------------
-- Motore      : DEMO_CONTI
-- Oggetto     : DEMO_DWH.DC_VC_VOLUMI_GIORNALIERI
-- Tipo        : Vista di controllo
-- Descrizione : Numero di movimenti per banca e giorno, confrontato con la
--               media dei 20 giorni precedenti presenti in tabella.
--               ESITO = KO se i movimenti del giorno sono meno del 50% della
--               media (il file potrebbe essere arrivato a meta).
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE OR REPLACE VIEW DEMO_DWH.DC_VC_VOLUMI_GIORNALIERI
AS
SELECT COD_ISTITUTO,
       DAT_CONTABILE,
       NUM_MOVIMENTI,
       ROUND(NUM_MEDIO_20GG, 2)                                  AS NUM_MEDIO_20GG,
       ROUND(NUM_MOVIMENTI / NUM_MEDIO_20GG * 100, 2)            AS PCT_SULLA_MEDIA,
       CASE
           WHEN NUM_MEDIO_20GG IS NULL THEN 'N/D'
           WHEN NUM_MOVIMENTI < NUM_MEDIO_20GG * 0.50 THEN 'KO'
           ELSE 'OK'
       END                                                       AS ESITO
  FROM (
        SELECT COD_ISTITUTO,
               DAT_CONTABILE,
               COUNT(*) AS NUM_MOVIMENTI,
               AVG(COUNT(*)) OVER (PARTITION BY COD_ISTITUTO
                                   ORDER BY DAT_CONTABILE
                                   ROWS BETWEEN 20 PRECEDING AND 1 PRECEDING) AS NUM_MEDIO_20GG
          FROM DEMO_DWH.DC_FT_MOVIMENTI
         GROUP BY COD_ISTITUTO, DAT_CONTABILE
       );

COMMENT ON TABLE DEMO_DWH.DC_VC_VOLUMI_GIORNALIERI IS 'DEMO_CONTI - Movimenti del giorno rispetto alla media degli ultimi 20 giorni';

-- Consumatori della vista: reportistica di controllo
GRANT SELECT ON DEMO_DWH.DC_VC_VOLUMI_GIORNALIERI TO APP_REPORTING;
