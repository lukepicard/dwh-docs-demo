--------------------------------------------------------------------------------
-- Motore      : DEMO_CONTI
-- Oggetto     : DEMO_DWH.DC_PKG_ELABORAZIONE
-- Tipo        : Package
-- Descrizione : Gestione delle elaborazioni del motore, chiamata dalle shell
--               di lancio:
--               - APRI         apre una riga 'running' in DC_LOG_ELABORAZIONI
--               - CHIUDI       la chiude in 'succeeded' o 'failed'
--               - SEGNA_PRONTO sblocca il flusso a valle in DC_CTL_SEMAFORO
-- Note        : Oggetto INVENTATO a scopo dimostrativo.
--------------------------------------------------------------------------------

CREATE OR REPLACE PACKAGE DEMO_DWH.DC_PKG_ELABORAZIONE
AS
    -- Apre un'elaborazione e ne restituisce l'identificativo
    FUNCTION APRI
    (
        p_cod_flusso       IN VARCHAR2,
        p_cod_istituto     IN VARCHAR2,
        p_dat_riferimento  IN DATE,
        p_flg_forza        IN CHAR DEFAULT 'N'
    )
    RETURN NUMBER;

    -- Chiude un'elaborazione: p_cod_stato = 'succeeded' oppure 'failed'
    PROCEDURE CHIUDI
    (
        p_id_elaborazione  IN NUMBER,
        p_cod_stato        IN VARCHAR2,
        p_des_errore       IN VARCHAR2 DEFAULT NULL
    );

    -- Segna come pronta la fonte p_cod_fonte per il flusso p_cod_flusso
    PROCEDURE SEGNA_PRONTO
    (
        p_cod_flusso       IN VARCHAR2,
        p_cod_fonte        IN VARCHAR2,
        p_cod_istituto     IN VARCHAR2,
        p_dat_riferimento  IN DATE
    );
END DC_PKG_ELABORAZIONE;
/

CREATE OR REPLACE PACKAGE BODY DEMO_DWH.DC_PKG_ELABORAZIONE
AS
    FUNCTION APRI
    (
        p_cod_flusso       IN VARCHAR2,
        p_cod_istituto     IN VARCHAR2,
        p_dat_riferimento  IN DATE,
        p_flg_forza        IN CHAR DEFAULT 'N'
    )
    RETURN NUMBER
    IS
        v_id_elaborazione  NUMBER;
    BEGIN
        v_id_elaborazione := DEMO_DWH.DC_SEQ_ELABORAZIONE.NEXTVAL;

        INSERT INTO DEMO_DWH.DC_LOG_ELABORAZIONI
            (ID_ELABORAZIONE, COD_FLUSSO, COD_ISTITUTO, DAT_RIFERIMENTO,
             COD_STATO, FLG_FORZA, DAT_INIZIO, COD_UTENTE_OS)
        VALUES
            (v_id_elaborazione, p_cod_flusso, p_cod_istituto, p_dat_riferimento,
             'running', p_flg_forza, SYSDATE, SYS_CONTEXT('USERENV', 'OS_USER'));

        COMMIT;
        RETURN v_id_elaborazione;
    END APRI;

    PROCEDURE CHIUDI
    (
        p_id_elaborazione  IN NUMBER,
        p_cod_stato        IN VARCHAR2,
        p_des_errore       IN VARCHAR2 DEFAULT NULL
    )
    IS
    BEGIN
        IF p_cod_stato NOT IN ('succeeded', 'failed') THEN
            RAISE_APPLICATION_ERROR(-20001, 'Stato non valido: ' || p_cod_stato);
        END IF;

        UPDATE DEMO_DWH.DC_LOG_ELABORAZIONI
           SET COD_STATO  = p_cod_stato,
               DAT_FINE   = SYSDATE,
               DES_ERRORE = SUBSTR(p_des_errore, 1, 4000)
         WHERE ID_ELABORAZIONE = p_id_elaborazione;

        IF SQL%ROWCOUNT = 0 THEN
            RAISE_APPLICATION_ERROR(-20002, 'Elaborazione inesistente: ' || p_id_elaborazione);
        END IF;

        COMMIT;
    END CHIUDI;

    PROCEDURE SEGNA_PRONTO
    (
        p_cod_flusso       IN VARCHAR2,
        p_cod_fonte        IN VARCHAR2,
        p_cod_istituto     IN VARCHAR2,
        p_dat_riferimento  IN DATE
    )
    IS
    BEGIN
        MERGE INTO DEMO_DWH.DC_CTL_SEMAFORO t
        USING (SELECT p_cod_flusso      AS COD_FLUSSO,
                      p_cod_fonte       AS COD_FONTE,
                      p_cod_istituto    AS COD_ISTITUTO,
                      p_dat_riferimento AS DAT_RIFERIMENTO
                 FROM DUAL) s
           ON (    t.COD_FLUSSO      = s.COD_FLUSSO
               AND t.COD_FONTE       = s.COD_FONTE
               AND t.COD_ISTITUTO    = s.COD_ISTITUTO
               AND t.DAT_RIFERIMENTO = s.DAT_RIFERIMENTO)
        WHEN MATCHED THEN
            UPDATE SET t.FLG_PRONTO        = 'S',
                       t.DAT_AGGIORNAMENTO = SYSDATE,
                       t.COD_UTENTE_AGG    = USER
        WHEN NOT MATCHED THEN
            INSERT (COD_FLUSSO, COD_FONTE, COD_ISTITUTO, DAT_RIFERIMENTO, FLG_PRONTO)
            VALUES (s.COD_FLUSSO, s.COD_FONTE, s.COD_ISTITUTO, s.DAT_RIFERIMENTO, 'S');

        COMMIT;
    END SEGNA_PRONTO;
END DC_PKG_ELABORAZIONE;
/
