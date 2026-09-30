### Come leggere gli esiti

Una riga per istituto e giorno. `NUM_POSIZIONI` sono le righe del giorno,
`NUM_POSIZIONI_QUADRANTI` quelle in cui posizione iniziale + acquisti −
vendite dà la posizione finale: se i due numeri sono diversi l'esito è `KO`.

La posizione finale la calcola il flusso stesso con quella formula: la vista non
può accorgersi di un errore di calcolo, ma segnala righe modificate a mano o
scritte a metà da un caricamento interrotto.

### Query utili

```sql
SELECT *
  FROM DEMO_DWH.DI_VC_QUADRATURA
 WHERE ESITO = 'KO'
 ORDER BY DAT_RIFERIMENTO DESC;
```

### Attenzione

La vista è letta da altri schemi (vedi "Chi consuma" nella scheda): la
reportistica di controllo e gli utenti del motore la interrogano ogni giorno.
Rinominare o togliere una colonna rompe i loro report: va concordato prima.
