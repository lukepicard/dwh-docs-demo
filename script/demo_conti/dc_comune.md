### Perché

La libreria è **condivisa** con `DEMO_INVESTIMENTI`: le sue shell (`lancia_di_carico.sh`
e `lancia_di_posizioni.sh`) la includono dalla cartella di `DEMO_CONTI` invece di
averne una copia. Così semaforo, log delle elaborazioni e package sono gli stessi
per i due motori. Ogni shell che la usa può scegliere la cartella PowerCenter
(`PMCMD_CARTELLA`) e, se lancia più workflow di seguito, elencarli in `WORKFLOWS`.

### Attenzione

- Una modifica a questa libreria cambia il comportamento delle shell di entrambi
  i motori: prima di committare vanno provate tutte.
- Per aggiungere un istituto bisogna aggiornare `ISTITUTI_ATTIVI` **e** creare le
  partizioni dedicate nelle tabelle di entrambi i motori (vedere la nota di
  `DC_STG_MOVIMENTI` e quella di `DI_STG_ORDINI`). Aggiornare solo la variabile fa
  finire i dati nella partizione `DEFAULT`.
- Senza `-d` le shell usano il giorno prima. `lancia_dc_saldi.sh` cambia la
  regola (ultimo giorno del mese precedente) ridefinendo `data_predefinita`.
