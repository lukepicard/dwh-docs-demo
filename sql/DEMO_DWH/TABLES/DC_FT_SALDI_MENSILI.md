### Perché

**Il saldo finale non si ricava dalla formula.** Saldo iniziale e saldo finale
si calcolano entrambi sommando i movimenti, ciascuno fino alla propria data.
Entrate e uscite si sommano a parte. Per questo la vista di controllo
`DC_VC_QUADRATURA` può verificare che `saldo iniziale + entrate − uscite = saldo
finale`: sono tre calcoli indipendenti, non uno scritto in funzione dell'altro.

**Data contabile, non data valuta.** I saldi mensili usano la data contabile
del movimento. La data valuta serve al calcolo degli interessi e qui non
compare: un movimento contabilizzato il 30 con valuta 2 del mese dopo conta nel
saldo del mese in cui è stato contabilizzato.

**Ricaricamento mirato.** La shell `lancia_dc_saldi.sh` riceve `-i <ISTITUTO|ALL>`
e, prima di lanciare il workflow, svuota solo la coppia (mese, istituto) in
lavorazione, lasciando intatti gli altri mesi e gli altri istituti:

```sql
ALTER TABLE DEMO_DWH.DC_FT_SALDI_MENSILI
  TRUNCATE SUBPARTITION FOR (DATE '2026-08-31', '99001');
```

Il `FOR (data, istituto)` serve perché le partizioni create da `INTERVAL`
hanno nomi generati dal sistema (`SYS_P…`), diversi da un ambiente all'altro:
con i valori non serve conoscere il nome.

### Attenzione

- I saldi si ricalcolano sempre sull'intera storia dei movimenti. Se un mese
  passato riceve un movimento in ritardo o uno storno, vanno rilanciati i saldi
  di quel mese e dei mesi successivi, in ordine.
- Un istituto che finisce nella sottopartizione `SP_DEFAULT` non si può
  ricaricare da solo (vale la stessa avvertenza di `DC_FT_MOVIMENTI`).
- La storia parte dal 2026: per la demo non ci sono saldi di apertura, il primo
  saldo iniziale è zero.
- La tabella alimenta gli estratti conto, fuori da questo repository:
  l'analisi d'impatto non li vede.
