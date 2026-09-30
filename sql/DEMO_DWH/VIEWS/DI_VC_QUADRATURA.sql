--------------------------------------------------------------------------------
-- Motore      : DEMO_INVESTIMENTI
-- Oggetto     : DEMO_DWH.DI_VC_QUADRATURA
-- Tipo        : Vista di controllo
-- Descrizione : Quadratura delle posizioni, una riga per banca e giorno:
--               per ogni dossier e titolo, posizione iniziale + acquisti -
--               vendite deve dare la posizione finale.
--               ESITO: OK se tutte le righe del giorno quadrano, KO se
--               almeno una non quadra.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE OR REPLACE VIEW DEMO_DWH.DI_VC_QUADRATURA
AS
SELECT COD_ISTITUTO,
       DAT_RIFERIMENTO,
       COUNT(*)                                                     AS NUM_POSIZIONI,
       COUNT(CASE WHEN QTA_INIZIALE + QTA_ACQUISTI - QTA_VENDITE = QTA_FINALE
                  THEN 1 END)                                       AS NUM_POSIZIONI_QUADRANTI,
       CASE
           WHEN COUNT(*) = COUNT(CASE WHEN QTA_INIZIALE + QTA_ACQUISTI - QTA_VENDITE = QTA_FINALE
                                      THEN 1 END) THEN 'OK'
           ELSE 'KO'
       END                                                          AS ESITO
  FROM DEMO_DWH.DI_FT_POSIZIONI
 GROUP BY COD_ISTITUTO, DAT_RIFERIMENTO;

COMMENT ON TABLE DEMO_DWH.DI_VC_QUADRATURA IS 'DEMO_INVESTIMENTI - Quadratura delle posizioni per istituto e giorno';

-- Consumatori della vista: reportistica di controllo e utenti del motore
GRANT SELECT ON DEMO_DWH.DI_VC_QUADRATURA TO APP_REPORTING, UTENTI_INVESTIMENTI;
