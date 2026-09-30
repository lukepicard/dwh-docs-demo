### Come leggere gli esiti

La vista ha una riga per controllo, istituto e data: la colonna `COD_CONTROLLO`
dice di quale controllo si tratta. `NUM_ATTESO` e `NUM_TROVATO` devono essere uguali.

- `STAGING_MOVIMENTI`: `NUM_ATTESO` sono i movimenti nello staging **contati una
  sola volta** (i doppioni del file non contano), `NUM_TROVATO` sono i movimenti
  caricati per quel giorno.
  - `KO` se un istituto è nello staging ma non nei movimenti: il flusso dei
    movimenti non è girato o è fallito (vedere `DC_LOG_ELABORAZIONI`).
  - `KO` anche se i numeri sono diversi: di solito è una causale che non esiste
    in `DC_DIM_CAUSALE`, e il movimento è rimasto fuori.
  - `N/D` per i giorni passati: lo staging contiene solo l'ultimo giorno caricato
    per ogni istituto.
- `SALDI`: `NUM_ATTESO` sono i conti con un saldo nel mese, `NUM_TROVATO` quelli in
  cui saldo iniziale + entrate − uscite dà il saldo finale. `KO` se anche un solo
  conto non quadra.

### Query utili

```sql
SELECT *
  FROM DEMO_DWH.DC_VC_QUADRATURA
 WHERE ESITO = 'KO';
```

### Attenzione

La vista è letta da altri schemi (vedi "Chi consuma" nella scheda): la
reportistica di controllo e gli utenti del motore la interrogano ogni giorno.
Rinominare o togliere una colonna rompe i loro report: va concordato prima.
