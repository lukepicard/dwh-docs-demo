### Perché

Dopo il caricamento, la sessione esegue una **Post SQL** che normalizza
`COD_CAUSALE` (maiuscolo, senza spazi). Il sistema fonte a volte invia codici
come `'pos '` o `'Stipendio'`: senza normalizzazione il flusso dei movimenti non
li riconoscerebbe e lascerebbe fuori movimenti che hanno una causale valida.

### Attenzione

- Si rilancia sempre tramite la shell `lancia_dc_carico_movimenti.sh`, che
  svuota prima la partizione dell'istituto: la sessione non tronca il target.
- Se il file non è arrivato, la sessione fallisce e la shell esce con `3`. Prima
  di rilanciare verificare che il file sia nella cartella `DEMO_INPUT_DIR`.
- Il carico non toglie i doppioni: lo fa `wf_DC_MOVIMENTI`.
- L'export XML è **semplificato**: non è importabile in un repository reale.
