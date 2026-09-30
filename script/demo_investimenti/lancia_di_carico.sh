#!/bin/bash
################################################################################
# Motore      : DEMO_INVESTIMENTI
# Script      : lancia_di_carico.sh
# Descrizione : Carica gli staging del giorno per una banca (-i <ISTITUTO>) o
#               per tutte le banche attive (-i ALL): gli ordini eseguiti
#               (FONTE_B) in DI_STG_ORDINI con wf_DI_CARICO_ORDINI e i prezzi
#               di chiusura (FONTE_C) in DI_STG_PREZZI con wf_DI_CARICO_PREZZI.
#               A fine carico sblocca il flusso DI_POSIZIONI.
#               Usa la libreria di DEMO_CONTI (dc_comune.sh): semaforo, log
#               delle elaborazioni e package sono condivisi tra i due motori.
# Uso         : lancia_di_carico.sh -i <ISTITUTO|ALL> [-d YYYYMMDD] [-f]
# Note        : Script INVENTATO a scopo dimostrativo.
################################################################################

FLUSSO="DI_CARICO"
WORKFLOWS="wf_DI_CARICO_ORDINI wf_DI_CARICO_PREZZI"
FLUSSO_VALLE="DI_POSIZIONI"
PMCMD_CARTELLA="DEMO_INVESTIMENTI"

. "$(dirname "$0")/../demo_conti/dc_comune.sh"

# Gli staging tengono un solo giorno per banca: si svuotano le due partizioni dell'istituto
svuota_target() {
    esegui_sql "ALTER TABLE DEMO_DWH.DI_STG_ORDINI TRUNCATE PARTITION FOR ('$1');
ALTER TABLE DEMO_DWH.DI_STG_PREZZI TRUNCATE PARTITION FOR ('$1');"
}

# File di input della banca in lavorazione: uno per ogni workflow ($2)
parametri_extra() {
    case "$2" in
        wf_DI_CARICO_ORDINI) echo "\$InputFile_Ordini=${DEMO_INPUT_DIR:-/tmp}/ordini_FONTE_B_$1_${DATA_RIF}.csv" ;;
        wf_DI_CARICO_PREZZI) echo "\$InputFile_Prezzi=${DEMO_INPUT_DIR:-/tmp}/prezzi_FONTE_C_$1_${DATA_RIF}.csv" ;;
    esac
}

esegui_flusso "$@"
