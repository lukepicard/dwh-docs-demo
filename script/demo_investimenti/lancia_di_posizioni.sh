#!/bin/bash
################################################################################
# Motore      : DEMO_INVESTIMENTI
# Script      : lancia_di_posizioni.sh
# Descrizione : Lancia wf_DI_POSIZIONI per una banca (-i <ISTITUTO>) o per tutte
#               le banche attive (-i ALL): calcola le posizioni di fine giorno
#               in DI_FT_POSIZIONI e, nel giorno di fine mese, il controvalore
#               dei dossier in DI_FT_CONTROVALORI_MENSILI.
#               E' l'ultimo flusso della catena: non sblocca altri flussi.
#               Usa la libreria di DEMO_CONTI (dc_comune.sh).
# Uso         : lancia_di_posizioni.sh -i <ISTITUTO|ALL> [-d YYYYMMDD] [-f]
# Note        : Script INVENTATO a scopo dimostrativo.
################################################################################

FLUSSO="DI_POSIZIONI"
WORKFLOW="wf_DI_POSIZIONI"
FLUSSO_VALLE=""
PMCMD_CARTELLA="DEMO_INVESTIMENTI"

. "$(dirname "$0")/../demo_conti/dc_comune.sh"

# S se la data di riferimento e' l'ultimo giorno del mese, altrimenti N
fine_mese() {
    if [ "$(date -d "${DATA_RIF} +1 day" +%d)" = "01" ]; then echo S; else echo N; fi
}

# Cancella le posizioni del giorno e della banca in lavorazione; a fine mese
# svuota anche la coppia (mese, banca) dei controvalori
svuota_target() {
    esegui_sql "DELETE FROM DEMO_DWH.DI_FT_POSIZIONI WHERE COD_ISTITUTO = '$1' AND DAT_RIFERIMENTO = $(data_sql);
COMMIT;" || return 1
    if [ "$(fine_mese)" = "S" ]; then
        esegui_sql "ALTER TABLE DEMO_DWH.DI_FT_CONTROVALORI_MENSILI TRUNCATE SUBPARTITION FOR ($(data_sql), '$1');"
    fi
}

# Il workflow calcola i controvalori solo se il flag e' S
parametri_extra() {
    echo "\$\$FLG_FINE_MESE=$(fine_mese)"
}

esegui_flusso "$@"
