### Perché

**Prezzo mancante.** Se nel file dei prezzi del giorno manca un titolo, la riga
non resta senza prezzo: si usa l'ultimo prezzo disponibile, cioè quello scritto
nella riga del giorno precedente, e la riga viene marcata con
`FLG_PREZZO_RIPORTATO = 'S'`. Il marchio serve a chi legge il controvalore:
un numero calcolato su un prezzo vecchio va letto con cautela. Se il prezzo
manca più giorni di seguito, il marchio resta e il prezzo è sempre quello
dell'ultima quotazione vera. Un titolo mai quotato ha prezzo vuoto.

**Posizione iniziale.** Non viene letta dagli ordini, che nello staging sono
solo quelli di un giorno: è la posizione finale dell'ultimo giorno già presente
in tabella per lo stesso dossier e titolo. Le posizioni a zero non si riportano
avanti.

**Ricaricare un giorno.** La shell `lancia_di_posizioni.sh` cancella con una
`DELETE` solo le righe del giorno e dell'istituto in lavorazione, e non con un
`TRUNCATE`: la sottopartizione contiene tutto il mese della banca. Per rifare
un mese intero si svuota la coppia (mese, istituto) e si rilanciano i giorni:

```sql
ALTER TABLE DEMO_DWH.DI_FT_POSIZIONI
  TRUNCATE SUBPARTITION FOR (DATE '2026-09-15', '99001');
```

La sintassi `FOR (data, istituto)` è obbligata: le partizioni create da
`INTERVAL` hanno nomi generati dal sistema, diversi da un ambiente all'altro.

### Attenzione

- Le posizioni si calcolano una dopo l'altra: se si rilancia un giorno passato
  vanno rilanciati, in ordine, anche tutti i giorni successivi, perché ognuno
  parte dalla posizione del giorno prima.
- Un istituto che finisce nella sottopartizione `SP_DEFAULT` non si può ricaricare
  da solo (stessa avvertenza di `DC_FT_MOVIMENTI`).
