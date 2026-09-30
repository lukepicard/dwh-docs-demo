### Perché

**Obbligazioni: si divide per 100.** Azioni e fondi hanno il prezzo in euro per
unità, e il controvalore è quantità per prezzo. Le obbligazioni hanno il prezzo
in percentuale del valore nominale: con prezzo 98, ogni 100 euro di nominale
costano 98 euro. Se la quantità è espressa in euro di nominale, 1.000 di
nominale con prezzo 98 valgono 1.000 × 98 / 100 = 980 euro, non 98.000. Il tipo
del titolo si legge in `DI_DIM_TITOLO`.

**Prezzo di fine mese.** Il controvalore usa la posizione e il prezzo dell'ultimo
giorno del mese. Se quel giorno il prezzo di un titolo mancava, `DI_FT_POSIZIONI`
riporta l'ultimo prezzo disponibile: il controvalore è calcolato lo stesso, e
`NUM_TITOLI_PREZZO_RIPORTATO` dice su quanti titoli del dossier è successo.
Un valore diverso da zero invita a leggere il numero con cautela.

**Ricaricamento mirato.** La shell `lancia_di_posizioni.sh`, nel giorno di fine
mese, svuota solo la coppia (mese, istituto) prima di lanciare il calcolo:

```sql
ALTER TABLE DEMO_DWH.DI_FT_CONTROVALORI_MENSILI
  TRUNCATE SUBPARTITION FOR (DATE '2026-08-31', '99001');
```

Il `FOR (data, istituto)` serve perché le partizioni create da `INTERVAL`
hanno nomi generati dal sistema, diversi da un ambiente all'altro.

### Attenzione

- Il controvalore è in euro solo se il prezzo è in euro: non c'è conversione di
  divisa.
- Un istituto che finisce nella sottopartizione `SP_DEFAULT` non si può ricaricare
  da solo (stessa avvertenza di `DC_FT_MOVIMENTI`).
- La tabella alimenta la reportistica dei dossier, fuori da questo repository:
  l'analisi d'impatto non la vede.
