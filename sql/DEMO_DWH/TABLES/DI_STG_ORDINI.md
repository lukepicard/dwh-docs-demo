### Perché

La tabella non conserva lo storico: contiene solo l'ultimo giorno caricato per
ciascun istituto. È partizionata per istituto proprio per poter ricaricare un
istituto senza toccare gli altri: con `-i 99001` la shell `lancia_di_carico.sh`
svuota solo quella partizione.

```sql
ALTER TABLE DEMO_DWH.DI_STG_ORDINI TRUNCATE PARTITION FOR ('99001');
```

Con `-i ALL` vengono svuotati e ricaricati tutti gli istituti.

### Attenzione

- Un istituto che finisce in `P_DEFAULT` non si può ricaricare da solo, perché il
  TRUNCATE svuoterebbe anche gli altri codici non censiti. Per ogni nuovo
  istituto va creata una partizione dedicata, dividendo la partizione DEFAULT
  (Oracle non accetta `ADD PARTITION` se esiste già): vale la stessa procedura
  descritta in `DC_STG_MOVIMENTI`, e vale anche per `DI_STG_PREZZI`.
- Il file arriva come `ordini_FONTE_B_<ISTITUTO>_<YYYYMMDD>.csv` nella cartella
  indicata da `DEMO_INPUT_DIR`.
- Gli ordini non generano movimenti: l'addebito o l'accredito sul conto arriva
  da `DEMO_CONTI` con i suoi flussi. `DI_VC_REGOLAMENTO_ORDINI` usa il conto di
  addebito per controllare che il movimento esista in `DC_FT_MOVIMENTI`: un
  codice conto sbagliato in questo file dà un `KO` in quella vista.
