--------------------------------------------------------------------------------
-- Motore      : DEMO_CONTI
-- Oggetto     : DEMO_DWH.DC_FN_SEMAFORO
-- Tipo        : Funzione
-- Descrizione : Dice se un flusso puo partire per una banca e una data di
--               riferimento. Restituisce 'OK' se in DC_CTL_SEMAFORO esiste
--               almeno una fonte per (flusso, istituto, data) e sono tutte pronte;
--               altrimenti 'KO'.
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE OR REPLACE FUNCTION DEMO_DWH.DC_FN_SEMAFORO
(
    p_cod_flusso       IN VARCHAR2,
    p_cod_istituto     IN VARCHAR2,
    p_dat_riferimento  IN DATE
)
RETURN VARCHAR2
IS
    v_num_fonti        NUMBER;
    v_num_non_pronte   NUMBER;
BEGIN
    SELECT COUNT(*),
           COUNT(CASE WHEN FLG_PRONTO <> 'S' THEN 1 END)
      INTO v_num_fonti,
           v_num_non_pronte
      FROM DEMO_DWH.DC_CTL_SEMAFORO
     WHERE COD_FLUSSO      = p_cod_flusso
       AND COD_ISTITUTO    = p_cod_istituto
       AND DAT_RIFERIMENTO = p_dat_riferimento;

    -- Nessuna fonte registrata = dati non ancora arrivati
    IF v_num_fonti = 0 OR v_num_non_pronte > 0 THEN
        RETURN 'KO';
    END IF;

    RETURN 'OK';
END DC_FN_SEMAFORO;
/
