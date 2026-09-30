#!/bin/bash
################################################################################
# Motore      : DEMO_CONTI
# Script      : lancia_dc_movimenti.sh
# Descrizione : Lancia wf_DC_MOVIMENTI per una banca (-i <ISTITUTO>) o per tutte
#               le banche attive (-i ALL): toglie i doppioni, assegna causale e
#               segno e scrive DC_FT_MOVIMENTI. A fine elaborazione sblocca il
#               flusso DC_SALDI.
# Uso         : lancia_dc_movimenti.sh -i <ISTITUTO|ALL> [-d YYYYMMDD] [-f]
# Note        : Script INVENTATO a scopo dimostrativo.
################################################################################

FLUSSO="DC_MOVIMENTI"
WORKFLOW="wf_DC_MOVIMENTI"
FLUSSO_VALLE="DC_SALDI"

. "$(dirname "$0")/dc_comune.sh"

# Cancella solo i movimenti del giorno e della banca in lavorazione: gli altri
# giorni del mese restano nella stessa sottopartizione
svuota_target() {
    esegui_sql "DELETE FROM DEMO_DWH.DC_FT_MOVIMENTI WHERE COD_ISTITUTO = '$1' AND DAT_CONTABILE = $(data_sql);
COMMIT;"
}

esegui_flusso "$@"
