--------------------------------------------------------------------------------
-- Motore      : DEMO_INVESTIMENTI
-- Oggetto     : DEMO_DWH.DI_VC_REGOLAMENTO_ORDINI
-- Tipo        : Vista di controllo
-- Descrizione : Una riga per ogni ordine di DI_STG_ORDINI: verifica che sul
--               conto di addebito esista il movimento corrispondente in
--               DC_FT_MOVIMENTI, cioe stesso istituto, stesso conto, stesso
--               giorno, stesso importo e causale ACQUISTO_TITOLI per un
--               acquisto oppure VENDITA_TITOLI per una vendita.
--               L'importo dell'ordine e quantita per prezzo (per le
--               obbligazioni diviso 100).
--               ESITO = KO se il movimento manca, altrimenti OK.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE OR REPLACE VIEW DEMO_DWH.DI_VC_REGOLAMENTO_ORDINI
AS
SELECT o.COD_ISTITUTO,
       o.DAT_RIFERIMENTO,
       o.ID_ORDINE,
       o.COD_DOSSIER,
       o.COD_CONTO_ADDEBITO,
       o.COD_OPERAZIONE,
       o.IMP_ORDINE,
       CASE
           WHEN EXISTS (SELECT 1
                          FROM DEMO_DWH.DC_FT_MOVIMENTI m
                         WHERE m.COD_ISTITUTO  = o.COD_ISTITUTO
                           AND m.COD_CONTO     = o.COD_CONTO_ADDEBITO
                           AND m.DAT_CONTABILE = o.DAT_RIFERIMENTO
                           AND m.IMP_MOVIMENTO = o.IMP_ORDINE
                           AND m.COD_CAUSALE   = CASE o.COD_OPERAZIONE
                                                     WHEN 'ACQUISTO' THEN 'ACQUISTO_TITOLI'
                                                     WHEN 'VENDITA'  THEN 'VENDITA_TITOLI'
                                                 END)
           THEN 'OK'
           ELSE 'KO'
       END AS ESITO
  FROM (
        SELECT s.COD_ISTITUTO,
               s.DAT_RIFERIMENTO,
               s.ID_ORDINE,
               s.COD_DOSSIER,
               s.COD_CONTO_ADDEBITO,
               s.COD_OPERAZIONE,
               ROUND(CASE WHEN t.COD_TIPO = 'OBBLIGAZIONE'
                          THEN s.QTA_ORDINE * s.IMP_PREZZO / 100
                          ELSE s.QTA_ORDINE * s.IMP_PREZZO
                     END, 2) AS IMP_ORDINE
          FROM DEMO_DWH.DI_STG_ORDINI s
          LEFT JOIN DEMO_DWH.DI_DIM_TITOLO t
            ON t.COD_TITOLO = s.COD_TITOLO
       ) o;

COMMENT ON TABLE DEMO_DWH.DI_VC_REGOLAMENTO_ORDINI IS 'DEMO_INVESTIMENTI - Ordini eseguiti con o senza il movimento di addebito o accredito sul conto';

-- Consumatore della vista: controllo ordini (schema inventato)
GRANT SELECT ON DEMO_DWH.DI_VC_REGOLAMENTO_ORDINI TO APP_CONTROLLO_TITOLI;
