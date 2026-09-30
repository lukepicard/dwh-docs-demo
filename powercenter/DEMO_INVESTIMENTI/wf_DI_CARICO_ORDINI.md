### Perché

Il carico scarta le righe con un'operazione diversa da `ACQUISTO` o `VENDITA`
e quelle senza quantità: un ordine che non si sa se aumenti o riduca la
posizione, o senza quantità, falserebbe la quantità in modo silenzioso. Le righe
scartate non arrivano nello staging.

### Attenzione

- Si rilancia sempre tramite la shell `lancia_di_carico.sh`, che svuota prima la
  partizione dell'istituto: la sessione non tronca il target.
- Il file degli ordini e quello dei prezzi si caricano insieme, dalla stessa
  shell. Rilanciare solo questo workflow a mano lascia gli staging sfasati.
- Se il file non è arrivato, la sessione fallisce e la shell esce con `3`. Prima
  di rilanciare verificare che il file sia nella cartella `DEMO_INPUT_DIR`.
- L'export XML è **semplificato**: non è importabile in un repository reale.
