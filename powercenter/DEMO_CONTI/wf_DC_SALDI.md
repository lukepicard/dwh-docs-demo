### Perché

Saldo iniziale e saldo finale si calcolano nella query di override della source,
sommando i movimenti con segno fino alla propria data. Si usa la **data
contabile**: la data valuta serve agli interessi, non ai saldi. Per questo un
movimento contabilizzato a fine mese ma con valuta nel mese dopo conta nel mese
in cui è stato contabilizzato.

Entrate e uscite si sommano a parte, e non si ricavano per differenza: così
`DC_VC_QUADRATURA` può controllare che saldo iniziale + entrate − uscite dia il
saldo finale.

### Attenzione

- Si rilancia sempre tramite la shell `lancia_dc_saldi.sh`, che svuota prima la
  sottopartizione (mese, istituto). Lanciato a mano dal client PowerCenter, il
  workflow duplicherebbe i dati, perché la sessione non tronca il target.
- Legge tutta la storia dei movimenti dell'istituto, non solo il mese: è il
  motivo per cui un movimento in ritardo su un mese passato obbliga a
  rilanciare anche i mesi successivi.
- L'export XML è **semplificato**: non è importabile in un repository reale.
