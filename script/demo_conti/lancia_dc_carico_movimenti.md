### Perché

Gira nello schedulatore Control-M come job `DC_CARICO_GIORN` (folder `DEMO_CONTI`),
ogni giorno lavorativo, con `-i ALL`. Senza `-d` carica il file del giorno prima.

### Attenzione

- Con `-i ALL` gli istituti vengono elaborati uno alla volta: se uno fallisce,
  lo script si ferma e gli istituti successivi non vengono lanciati. Dopo la
  correzione si rilancia solo l'istituto in errore con `-i <ISTITUTO>`.
- Lo staging tiene un solo giorno per banca: rilanciare il carico di un giorno
  passato cancella quello caricato dopo. Dopo un rilancio di questo tipo va
  rilanciato anche `lancia_dc_movimenti.sh` per lo stesso istituto e giorno.

### Comandi utili

```bash
# Rilancio manuale di un solo istituto, senza semaforo
./lancia_dc_carico_movimenti.sh -i 99001 -d 20260929 -f

# Rilancio di tutti gli istituti per un giorno preciso
./lancia_dc_carico_movimenti.sh -i ALL -d 20260929 -f
```
