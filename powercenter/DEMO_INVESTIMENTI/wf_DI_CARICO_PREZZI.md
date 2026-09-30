### Perché

Dopo il caricamento, la sessione esegue una **Post SQL** che normalizza
`COD_TITOLO` (maiuscolo, senza spazi). Il sistema fonte a volte invia codici
ISIN con uno spazio o in minuscolo: senza normalizzazione il prezzo non
verrebbe abbinato al titolo, il flusso delle posizioni lo considererebbe mancante
e riporterebbe il prezzo del giorno prima.

### Attenzione

- Si rilancia sempre tramite la shell `lancia_di_carico.sh`, che svuota prima la
  partizione dell'istituto: la sessione non tronca il target.
- Un prezzo che manca nel file non è un errore del carico: lo gestisce il flusso
  delle posizioni, riportando l'ultimo prezzo disponibile (vedere `DI_FT_POSIZIONI`).
- Se il file non è arrivato, la sessione fallisce e la shell esce con `3`. Prima
  di rilanciare verificare che il file sia nella cartella `DEMO_INPUT_DIR`.
- L'export XML è **semplificato**: non è importabile in un repository reale.
