### Perché

Gira nello schedulatore Control-M come job `DI_CARICO_GIORN` (folder
`DEMO_INVESTIMENTI`), ogni giorno lavorativo, con `-i ALL`. Senza `-d` carica i
file del giorno prima.

Lancia due workflow di seguito, ordini e prezzi, dentro la stessa elaborazione:
un'elaborazione è "riuscita" solo se lo sono entrambi. Il semaforo `DI_CARICO`
aspetta due fonti, gli ordini (`FONTE_B`) e i prezzi (`FONTE_C`): parte solo quando
sono arrivati tutti e due i file.

Semaforo, log delle elaborazioni e package sono quelli di `DEMO_CONTI`
(`DC_CTL_SEMAFORO`, `DC_LOG_ELABORAZIONI`, `DC_PKG_ELABORAZIONE`), raggiunti
tramite la libreria `dc_comune.sh`: non esistono copie per gli investimenti.

### Attenzione

- Con `-i ALL` gli istituti vengono elaborati uno alla volta: se uno fallisce,
  lo script si ferma e gli istituti successivi non vengono lanciati. Dopo la
  correzione si rilancia solo l'istituto in errore con `-i <ISTITUTO>`.
- Se fallisce il secondo workflow (prezzi), il primo (ordini) è già stato
  caricato, ma il rilancio svuota comunque entrambi gli staging e ricarica tutto.
- Gli staging tengono un solo giorno per banca: rilanciare il carico di un giorno
  passato cancella quello caricato dopo. Dopo un rilancio di questo tipo va
  rilanciato anche `lancia_di_posizioni.sh` per lo stesso istituto e giorno.
- Ogni istituto che si aggiunge a `ISTITUTI_ATTIVI` in `dc_comune.sh` vale per
  entrambi i motori: servono le partizioni dedicate anche in `DI_STG_ORDINI` e
  `DI_STG_PREZZI`.

### Comandi utili

```bash
# Rilancio manuale di un solo istituto, senza semaforo
./lancia_di_carico.sh -i 99001 -d 20260929 -f

# Rilancio di tutti gli istituti per un giorno preciso
./lancia_di_carico.sh -i ALL -d 20260929 -f
```
