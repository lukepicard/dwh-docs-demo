### Perché

Come `DI_STG_ORDINI`, contiene solo l'ultimo giorno caricato per ciascun
istituto ed è partizionata per istituto, per ricaricare una banca senza toccare
le altre:

```sql
ALTER TABLE DEMO_DWH.DI_STG_PREZZI TRUNCATE PARTITION FOR ('99001');
```

Ogni banca riceve il proprio file dei prezzi, anche se i prezzi di mercato sono
gli stessi per tutte: si tiene la stessa struttura degli ordini, così una banca
si ricarica per intero (ordini e prezzi) con un solo lancio.

### Attenzione

- Il file può non contenere tutti i titoli: per quelli mancanti il flusso delle
  posizioni riporta l'ultimo prezzo disponibile e marca la riga (vedere
  `DI_FT_POSIZIONI`).
- Il file arriva come `prezzi_FONTE_C_<ISTITUTO>_<YYYYMMDD>.csv` nella cartella
  indicata da `DEMO_INPUT_DIR`.
- Per un nuovo istituto vale la stessa procedura di `DI_STG_ORDINI`: partizione
  dedicata, ottenuta dividendo la partizione DEFAULT.
