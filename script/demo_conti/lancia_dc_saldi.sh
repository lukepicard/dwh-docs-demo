#!/bin/bash
################################################################################
# Motore      : DEMO_CONTI
# Script      : lancia_dc_saldi.sh
# Descrizione : Lancia wf_DC_SALDI per una banca (-i <ISTITUTO>) o per tutte
#               le banche attive (-i ALL): calcola per ogni conto saldo
#               iniziale, entrate, uscite e saldo finale del mese e scrive
#               DC_FT_SALDI_MENSILI. E' l'ultimo flusso della catena: non
#               sblocca altri flussi.
#               La data e' l'ultimo giorno del mese; senza -d si usa il mese
#               precedente.
# Uso         : lancia_dc_saldi.sh -i <ISTITUTO|ALL> [-d YYYYMMDD] [-f]
# Note        : Script INVENTATO a scopo dimostrativo.
################################################################################

FLUSSO="DC_SALDI"
WORKFLOW="wf_DC_SALDI"
FLUSSO_VALLE=""

. "$(dirname "$0")/dc_comune.sh"

# Senza -d: ultimo giorno del mese precedente
data_predefinita() { date -d "$(date +%Y%m01) -1 day" +%Y%m%d; }

# I saldi sono mensili: la data deve essere l'ultimo giorno del mese
controlla_data() {
    if [ "$(date -d "${DATA_RIF} +1 day" +%d)" != "01" ]; then
        log "La data ${DATA_RIF} non e' l'ultimo giorno del mese: i saldi sono mensili"
        return 1
    fi
}

# Svuota solo la coppia (mese, banca) in lavorazione
svuota_target() {
    esegui_sql "ALTER TABLE DEMO_DWH.DC_FT_SALDI_MENSILI TRUNCATE SUBPARTITION FOR ($(data_sql), '$1');"
}

esegui_flusso "$@"
