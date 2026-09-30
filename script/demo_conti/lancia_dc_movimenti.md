### Perché

Gira nello schedulatore Control-M come job `DC_MOV_GIORN` (folder `DEMO_CONTI`),
ogni giorno lavorativo, con `-i ALL`.

La shell cancella con una `DELETE` i movimenti del solo giorno e istituto in
lavorazione, e non con un `TRUNCATE`: la sottopartizione contiene tutto il mese
della banca, e svuotarla farebbe perdere i giorni già caricati. Il `TRUNCATE
SUBPARTITION FOR` si usa solo per rifare un mese intero (vedere la nota di
`DC_FT_MOVIMENTI`).

### Attenzione

- Con `-i ALL` gli istituti vengono elaborati uno alla volta: se uno fallisce,
  lo script si ferma e gli istituti successivi non vengono lanciati. Dopo la
  correzione si rilancia solo l'istituto in errore con `-i <ISTITUTO>`.
- Legge lo staging, che contiene un solo giorno per banca: il giorno da
  elaborare deve essere quello caricato per ultimo da `lancia_dc_carico_movimenti.sh`.
- Dopo un rilancio dei movimenti vanno rilanciati anche i saldi del mese, che
  li leggono.

### Comandi utili

```bash
# Rilancio manuale di un solo istituto, senza semaforo
./lancia_dc_movimenti.sh -i 99001 -d 20260929 -f

# Rilancio di tutti gli istituti per un giorno preciso
./lancia_dc_movimenti.sh -i ALL -d 20260929 -f
```
