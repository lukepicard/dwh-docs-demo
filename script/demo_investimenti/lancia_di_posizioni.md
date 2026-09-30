### Perché

Gira nello schedulatore Control-M come job `DI_POS_GIORN` (folder
`DEMO_INVESTIMENTI`), ogni giorno lavorativo, con `-i ALL`.

Le posizioni sono giornaliere e il controvalore è mensile, ma il flusso è uno
solo: il workflow riceve il parametro `FLG_FINE_MESE` e calcola i controvalori
solo quando la data è l'ultimo giorno del mese. Negli altri giorni scrive solo
le posizioni.

La shell cancella con una `DELETE` le posizioni del solo giorno e istituto in
lavorazione, e non con un `TRUNCATE`: la sottopartizione contiene tutto il mese
della banca. Solo per il controvalore, che è uno per mese, si svuota la coppia
(mese, istituto).

### Attenzione

- Con `-i ALL` gli istituti vengono elaborati uno alla volta: se uno fallisce,
  lo script si ferma e gli istituti successivi non vengono lanciati. Dopo la
  correzione si rilancia solo l'istituto in errore con `-i <ISTITUTO>`.
- Legge gli staging, che contengono un solo giorno per banca: il giorno da
  elaborare deve essere quello caricato per ultimo da `lancia_di_carico.sh`.
- Le posizioni partono dal giorno precedente: se si rilancia un giorno passato
  vanno rilanciati in ordine anche tutti i successivi, compreso l'ultimo giorno
  del mese per rifare il controvalore.
- Il semaforo, il log e il package sono quelli di `DEMO_CONTI`
  (`DC_CTL_SEMAFORO`, `DC_LOG_ELABORAZIONI`, `DC_PKG_ELABORAZIONE`).

### Comandi utili

```bash
# Rilancio manuale di un solo istituto, senza semaforo
./lancia_di_posizioni.sh -i 99001 -d 20260929 -f

# Rilancio di tutti gli istituti per un giorno preciso
./lancia_di_posizioni.sh -i ALL -d 20260929 -f
```
