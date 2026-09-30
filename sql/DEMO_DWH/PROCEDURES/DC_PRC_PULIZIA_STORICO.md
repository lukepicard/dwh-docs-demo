### Perché

Log e semaforo crescono di qualche riga per ogni istituto e ogni giorno: senza
pulizia, dopo qualche anno rallentano le query di assistenza. Due anni di storia
bastano per rispondere a qualsiasi domanda sui rilanci.

Le due tabelle si puliscono con criteri diversi, anche se entrambe hanno
`DAT_RIFERIMENTO`: il log per data di **esecuzione** (`DAT_INIZIO`), il semaforo
per data di **riferimento** dei dati.

### Attenzione

- La lancia un job di manutenzione mensile dello schedulatore, fuori da questo
  repository: nella scheda non compare nessun chiamante.
- Il recupero dello spazio usa SQL dinamico (`EXECUTE IMMEDIATE` con il nome
  della tabella costruito a runtime): l'analisi d'impatto non può sapere quali
  tabelle tocca e lo segnala come "da verificare". Le tabelle sono le stesse
  delle due `DELETE`.
