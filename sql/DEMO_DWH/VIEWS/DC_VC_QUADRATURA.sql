--------------------------------------------------------------------------------
-- Motore      : DEMO_CONTI
-- Oggetto     : DEMO_DWH.DC_VC_QUADRATURA
-- Tipo        : Vista di controllo
-- Descrizione : Due controlli di quadratura, una riga per banca e data:
--               - STAGING_MOVIMENTI: i movimenti nello staging (senza
--                 doppioni) devono essere gli stessi trovati nei movimenti;
--               - SALDI: per ogni conto, saldo iniziale + entrate - uscite
--                 deve dare il saldo finale.
--               ESITO: OK / KO / N/D (dato di confronto non disponibile).
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE OR REPLACE VIEW DEMO_DWH.DC_VC_QUADRATURA
AS
WITH stg AS
(
    SELECT COD_ISTITUTO, DAT_RIFERIMENTO,
           COUNT(DISTINCT ID_MOVIMENTO) AS NUM_MOVIMENTI
      FROM DEMO_DWH.DC_STG_MOVIMENTI
     GROUP BY COD_ISTITUTO, DAT_RIFERIMENTO
),
mov AS
(
    SELECT COD_ISTITUTO, DAT_CONTABILE AS DAT_RIFERIMENTO,
           COUNT(*) AS NUM_MOVIMENTI
      FROM DEMO_DWH.DC_FT_MOVIMENTI
     GROUP BY COD_ISTITUTO, DAT_CONTABILE
),
sal AS
(
    SELECT COD_ISTITUTO, DAT_RIFERIMENTO,
           COUNT(*) AS NUM_CONTI,
           COUNT(CASE WHEN IMP_SALDO_INIZIALE + IMP_ENTRATE - IMP_USCITE = IMP_SALDO_FINALE
                      THEN 1 END) AS NUM_CONTI_QUADRANTI
      FROM DEMO_DWH.DC_FT_SALDI_MENSILI
     GROUP BY COD_ISTITUTO, DAT_RIFERIMENTO
)
SELECT 'STAGING_MOVIMENTI'                             AS COD_CONTROLLO,
       COALESCE(m.COD_ISTITUTO, s.COD_ISTITUTO)        AS COD_ISTITUTO,
       COALESCE(m.DAT_RIFERIMENTO, s.DAT_RIFERIMENTO)  AS DAT_RIFERIMENTO,
       s.NUM_MOVIMENTI                                 AS NUM_ATTESO,
       m.NUM_MOVIMENTI                                 AS NUM_TROVATO,
       -- Lo staging contiene solo l'ultimo giorno caricato: per i giorni
       -- precedenti il confronto non e' disponibile
       CASE
           WHEN s.COD_ISTITUTO IS NULL THEN 'N/D'
           WHEN m.COD_ISTITUTO IS NULL THEN 'KO'
           WHEN s.NUM_MOVIMENTI = m.NUM_MOVIMENTI THEN 'OK'
           ELSE 'KO'
       END                                             AS ESITO
  FROM stg s
  FULL OUTER JOIN mov m
    ON m.COD_ISTITUTO = s.COD_ISTITUTO
   AND m.DAT_RIFERIMENTO = s.DAT_RIFERIMENTO
UNION ALL
SELECT 'SALDI',
       COD_ISTITUTO,
       DAT_RIFERIMENTO,
       NUM_CONTI,
       NUM_CONTI_QUADRANTI,
       CASE WHEN NUM_CONTI = NUM_CONTI_QUADRANTI THEN 'OK' ELSE 'KO' END
  FROM sal;

COMMENT ON TABLE DEMO_DWH.DC_VC_QUADRATURA IS 'DEMO_CONTI - Quadratura staging / movimenti e saldi mensili, per istituto e data';

-- Consumatori della vista: reportistica di controllo e utenti del motore
GRANT SELECT ON DEMO_DWH.DC_VC_QUADRATURA TO APP_REPORTING, UTENTI_CONTI;
