#!/bin/bash
# Shell di prova: T_A citata solo in questo commento
WORKFLOW="wf_X"
. "$(dirname "$0")/lib.sh"

sqlplus -s u/p@db <<SQL
EXEC PROVA.PKG_X.ELABORA;
TRUNCATE TABLE PROVA.T_C;
SQL
lancia
