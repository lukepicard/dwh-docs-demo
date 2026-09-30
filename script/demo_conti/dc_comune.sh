#!/bin/bash
################################################################################
# Motore      : DEMO_CONTI (usata anche da DEMO_INVESTIMENTI)
# Script      : dc_comune.sh
# Descrizione : Funzioni comuni alle shell di lancio del motore. Non si esegue
#               da sola: viene inclusa (source) da lancia_dc_*.sh, che prima
#               definiscono FLUSSO, WORKFLOW, FLUSSO_VALLE e la funzione
#               svuota_target, poi chiamano esegui_flusso "$@".
#               Un flusso che lancia piu workflow di seguito definisce
#               WORKFLOWS (elenco separato da spazi) al posto di WORKFLOW.
#               Il motore che la usa puo definire PMCMD_CARTELLA prima di
#               includerla (default: DEMO_CONTI).
#               Ogni shell puo ridefinire data_predefinita (data usata senza -d)
#               e controlla_data (verifica della data ricevuta).
# Note        : Script INVENTATO a scopo dimostrativo.
################################################################################

# Return code (letti da Control-M)
RC_OK=0          # esecuzione completata
RC_ERRORE=1      # errore bloccante
RC_SEMAFORO=2    # semaforo KO, dati non disponibili (lo schedulatore ritenta)
RC_WORKFLOW=3    # errore nel workflow ETL

# Configurazione (valori fittizi, credenziali da variabili d'ambiente)
ISTITUTI_ATTIVI="99001 99002 99003"
PMCMD_DOMINIO="DOM_DEMO"
PMCMD_SERVIZIO="IS_DEMO"
PMCMD_CARTELLA="${PMCMD_CARTELLA:-DEMO_CONTI}"
LOG_DIR="${DEMO_LOG_DIR:-/tmp}"
LOG_FILE="${LOG_DIR}/$(basename "$0" .sh)_$(date +%Y%m%d_%H%M%S).log"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" | tee -a "${LOG_FILE}" >&2; }

esegui_sql() {
    sqlplus -s "${DEMO_DB_USER}/${DEMO_DB_PWD}@${DEMO_DB_TNS}" <<SQL
WHENEVER SQLERROR EXIT 1
SET HEADING OFF FEEDBACK OFF PAGESIZE 0
$1
EXIT
SQL
}

# Espressione SQL della data di riferimento
data_sql() { echo "TO_DATE('${DATA_RIF}','YYYYMMDD')"; }

# Data usata quando manca -d: di default il giorno prima
data_predefinita() { date -d "yesterday" +%Y%m%d; }

# --- Parametri: -i <ISTITUTO|ALL> [-d YYYYMMDD] [-f] ---------------------------
leggi_parametri() {
    ISTITUTO=""; DATA_RIF=""; FORZATO="N"
    while [ $# -gt 0 ]; do
        case "$1" in
            -i)    ISTITUTO="$2"; shift 2 ;;
            -d)    DATA_RIF="$2"; shift 2 ;;
            -f)    FORZATO="S"; shift ;;
            *)     log "Parametro non riconosciuto: $1"; exit ${RC_ERRORE} ;;
        esac
    done

    [ -z "${ISTITUTO}" ] && { log "Parametro -i obbligatorio (<ISTITUTO> oppure ALL)"; exit ${RC_ERRORE}; }

    if [ "${FORZATO}" = "S" ] && [ -z "${DATA_RIF}" ]; then
        log "-f richiede la data esatta con -d YYYYMMDD"; exit ${RC_ERRORE}
    fi

    [ -z "${DATA_RIF}" ] && DATA_RIF=$(data_predefinita)

    # Controllo facoltativo della data, se la shell lo definisce
    if declare -F controlla_data > /dev/null; then
        controlla_data || exit ${RC_ERRORE}
    fi

    if [ "${ISTITUTO}" = "ALL" ]; then ELENCO_ISTITUTI="${ISTITUTI_ATTIVI}"; else ELENCO_ISTITUTI="${ISTITUTO}"; fi
}

# --- Semaforo: tutte le banche devono essere pronte prima di partire ---------
verifica_semafori() {
    if [ "${FORZATO}" = "S" ]; then
        log "-f: controllo del semaforo saltato"
        return
    fi
    for COD_ISTITUTO in ${ELENCO_ISTITUTI}; do
        ESITO=$(esegui_sql "SELECT DEMO_DWH.DC_FN_SEMAFORO('${FLUSSO}', '${COD_ISTITUTO}', $(data_sql)) FROM DUAL;" | tr -d '[:space:]')
        if [ "${ESITO}" != "OK" ]; then
            log "Semaforo KO per ${FLUSSO}, istituto ${COD_ISTITUTO} (esito: ${ESITO}): dati non ancora disponibili"
            exit ${RC_SEMAFORO}
        fi
    done
    log "Semaforo OK per tutte le banche richieste"
}

# --- Log delle elaborazioni (DC_PKG_ELABORAZIONE) ----------------------------
apri_elaborazione() {
    esegui_sql "VARIABLE v_id NUMBER
EXEC :v_id := DEMO_DWH.DC_PKG_ELABORAZIONE.APRI('${FLUSSO}', '$1', $(data_sql), '${FORZATO}');
PRINT v_id" | tr -d '[:space:]'
}

chiudi_elaborazione() {
    esegui_sql "EXEC DEMO_DWH.DC_PKG_ELABORAZIONE.CHIUDI($1, '$2', '$3');" >> "${LOG_FILE}"
}

# Chiude l'elaborazione in errore ed esce con il return code indicato
fallisci() {
    log "$3"
    chiudi_elaborazione "$1" failed "$3"
    exit "$2"
}

# --- Lancio dei workflow PowerCenter -----------------------------------------
# Lancia un workflow: $1 istituto, $2 elaborazione, $3 nome del workflow
avvia_workflow() {
    local COD_ISTITUTO="$1" ID_ELAB="$2"
    local WORKFLOW="$3"
    local PARAM_FILE="${LOG_DIR}/${WORKFLOW}_${COD_ISTITUTO}_${DATA_RIF}.par"
    {
        echo "[${PMCMD_CARTELLA}.WF:${WORKFLOW}]"
        echo "\$\$COD_ISTITUTO=${COD_ISTITUTO}"
        echo "\$\$DAT_RIFERIMENTO=${DATA_RIF}"
        echo "\$\$ID_ELABORAZIONE=${ID_ELAB}"
        # Parametri aggiuntivi del singolo flusso, se la shell li definisce
        declare -F parametri_extra > /dev/null && parametri_extra "${COD_ISTITUTO}" "${WORKFLOW}"
    } > "${PARAM_FILE}"

    pmcmd startworkflow -d "${PMCMD_DOMINIO}" -sv "${PMCMD_SERVIZIO}" \
        -u "${DEMO_PMCMD_USER}" -p "${DEMO_PMCMD_PWD}" -f "${PMCMD_CARTELLA}" \
        -paramfile "${PARAM_FILE}" -wait "${WORKFLOW}" >> "${LOG_FILE}" 2>&1
}

# Lancia in ordine i workflow del flusso e si ferma al primo che fallisce
lancia_workflow() {
    for WORKFLOW_CORRENTE in ${WORKFLOWS:-${WORKFLOW}}; do
        avvia_workflow "$1" "$2" "${WORKFLOW_CORRENTE}" || return 1
    done
}

# --- Flusso completo ---------------------------------------------------------
esegui_flusso() {
    leggi_parametri "$@"
    log "Avvio ${WORKFLOWS:-${WORKFLOW}} - Istituti: ${ELENCO_ISTITUTI} - data riferimento: ${DATA_RIF} - forzato: ${FORZATO}"

    verifica_semafori

    for COD_ISTITUTO in ${ELENCO_ISTITUTI}; do
        ID_ELAB=$(apri_elaborazione "${COD_ISTITUTO}")
        [ -z "${ID_ELAB}" ] && { log "Istituto ${COD_ISTITUTO}: impossibile aprire l'elaborazione"; exit ${RC_ERRORE}; }
        log "Istituto ${COD_ISTITUTO}: elaborazione ${ID_ELAB} aperta"

        svuota_target "${COD_ISTITUTO}" >> "${LOG_FILE}" \
            || fallisci "${ID_ELAB}" ${RC_ERRORE} "Istituto ${COD_ISTITUTO}: errore nello svuotamento del target"

        lancia_workflow "${COD_ISTITUTO}" "${ID_ELAB}" \
            || fallisci "${ID_ELAB}" ${RC_WORKFLOW} "Istituto ${COD_ISTITUTO}: ${WORKFLOW_CORRENTE:-${WORKFLOW}} terminato in errore"

        chiudi_elaborazione "${ID_ELAB}" succeeded ""
        log "Istituto ${COD_ISTITUTO}: elaborazione ${ID_ELAB} completata"

        # Sblocca il flusso a valle per questa banca e data
        if [ -n "${FLUSSO_VALLE}" ]; then
            esegui_sql "EXEC DEMO_DWH.DC_PKG_ELABORAZIONE.SEGNA_PRONTO('${FLUSSO_VALLE}', '${FLUSSO}', '${COD_ISTITUTO}', $(data_sql));" >> "${LOG_FILE}" \
                || { log "Istituto ${COD_ISTITUTO}: errore nell'aggiornamento del semaforo di ${FLUSSO_VALLE}"; exit ${RC_ERRORE}; }
            log "Istituto ${COD_ISTITUTO}: semaforo di ${FLUSSO_VALLE} aggiornato"
        fi
    done

    log "Fine elaborazione - esito OK"
    exit ${RC_OK}
}
