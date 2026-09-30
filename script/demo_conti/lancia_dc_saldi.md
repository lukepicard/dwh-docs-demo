### Perché

Gira nello schedulatore Control-M come job `DC_SALDI_MENS` (folder `DEMO_CONTI`),
mensile, dal 2° giorno lavorativo del mese, con `-i ALL`. Senza `-d` calcola i
saldi del mese precedente.

La data deve essere l'ultimo giorno del mese: la shell esce con errore se ne
riceve un'altra, per non scrivere saldi con una data di riferimento sbagliata.

### Attenzione

- Con `-i ALL` gli istituti vengono elaborati uno alla volta: se uno fallisce,
  lo script si ferma e gli istituti successivi non vengono lanciati. Dopo la
  correzione si rilancia solo l'istituto in errore con `-i <ISTITUTO>`.
- Il semaforo aspetta che siano stati caricati i movimenti dell'ultimo giorno
  del mese, ma non controlla che ci siano tutti i giorni precedenti: prima di
  forzare un lancio guardare `DC_VC_VOLUMI_GIORNALIERI`.
- Se cambiano i movimenti di un mese passato vanno rilanciati i saldi di quel
  mese e dei successivi, in ordine.

### Comandi utili

```bash
# Rilancio manuale di un solo istituto, senza semaforo
./lancia_dc_saldi.sh -i 99001 -d 20260831 -f

# Rilancio di tutti gli istituti per un mese preciso
./lancia_dc_saldi.sh -i ALL -d 20260831 -f
```
