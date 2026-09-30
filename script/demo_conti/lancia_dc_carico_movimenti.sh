#!/bin/bash
################################################################################
# Motore      : DEMO_CONTI
# Script      : lancia_dc_carico_movimenti.sh
# Descrizione : Carica in DC_STG_MOVIMENTI il file giornaliero dei movimenti
#               del sistema fonte FONTE_A, per banca, con wf_DC_CARICO_MOVIMENTI.
#               A fine carico sblocca il flusso DC_MOVIMENTI.
# Uso         : lancia_dc_carico_movimenti.sh -i <ISTITUTO|ALL> [-d YYYYMMDD] [-f]
# Note        : Script INVENTATO a scopo dimostrativo.
################################################################################

FLUSSO="DC_CARICO"
WORKFLOW="wf_DC_CARICO_MOVIMENTI"
FLUSSO_VALLE="DC_MOVIMENTI"

. "$(dirname "$0")/dc_comune.sh"

# Lo staging tiene un solo giorno per banca: si svuota l'intera partizione dell'istituto
svuota_target() {
    esegui_sql "ALTER TABLE DEMO_DWH.DC_STG_MOVIMENTI TRUNCATE PARTITION FOR ('$1');"
}

# File di input della banca in lavorazione
parametri_extra() {
    echo "\$InputFile_Movimenti=${DEMO_INPUT_DIR:-/tmp}/movimenti_FONTE_A_$1_${DATA_RIF}.csv"
}

esegui_flusso "$@"
