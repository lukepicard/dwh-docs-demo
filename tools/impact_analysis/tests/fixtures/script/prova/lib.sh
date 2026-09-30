#!/bin/bash
# Libreria di prova: il workflow arriva dalla variabile di chi la include
lancia() {
    pmcmd startworkflow -d DOM -sv IS -u "$U" -p "$P" -f PROVA \
        -wait "${WORKFLOW}" >> /tmp/log 2>&1
}
