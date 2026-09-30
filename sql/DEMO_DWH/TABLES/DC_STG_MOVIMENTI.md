### Perché

La tabella non conserva lo storico: contiene solo l'ultimo giorno caricato per
ciascun istituto. È partizionata per istituto proprio per poter ricaricare un
istituto senza toccare gli altri: con `-i 99001` la shell
`lancia_dc_carico_movimenti.sh` svuota solo quella partizione.

```sql
ALTER TABLE DEMO_DWH.DC_STG_MOVIMENTI TRUNCATE PARTITION FOR ('99001');
```

Con `-i ALL` vengono svuotati e ricaricati tutti gli istituti.

Il file può contenere lo stesso movimento due volte: lo staging lo tiene così
com'è, senza scartare nulla. I doppioni si tolgono più avanti, quando i
movimenti passano a `DC_FT_MOVIMENTI`, riconoscendoli dall'identificativo del
movimento (`ID_MOVIMENTO`).

### Attenzione

- Un istituto che finisce in `P_DEFAULT` non si può ricaricare da solo, perché il
  TRUNCATE svuoterebbe anche gli altri codici non censiti. Per ogni nuovo
  istituto va creata una partizione dedicata. Siccome esiste già `P_DEFAULT`,
  Oracle non accetta `ADD PARTITION`: bisogna dividere la partizione DEFAULT.

```sql
ALTER TABLE DEMO_DWH.DC_STG_MOVIMENTI
  SPLIT PARTITION P_DEFAULT VALUES ('99004')
  INTO (PARTITION P_99004, PARTITION P_DEFAULT);
```

- Il file sorgente arriva come `movimenti_FONTE_A_<ISTITUTO>_<YYYYMMDD>.csv`
  nella cartella indicata da `DEMO_INPUT_DIR`.
