### Perché

**Doppioni.** Il file della fonte può contenere lo stesso movimento più volte.
Il flusso ne tiene uno solo, riconoscendolo dall'identificativo
(`ID_MOVIMENTO`); la deduplica sta nella query di override della source. Vale
dentro il file del giorno: se lo stesso identificativo arrivasse in un altro
giorno, non verrebbe riconosciuto.

**Causale sconosciuta.** Se la causale non è in `DC_DIM_CAUSALE`, il movimento
non viene caricato. È voluto: meglio un movimento in meno che un movimento con
il segno sbagliato, e la quadratura tra staging e movimenti (`DC_VC_QUADRATURA`)
va in `KO` e lo segnala.

### Attenzione

- Si rilancia sempre tramite la shell `lancia_dc_movimenti.sh`, che cancella
  prima i movimenti del giorno. Lanciato a mano dal client PowerCenter, il
  workflow duplicherebbe i dati, perché la sessione non tronca il target.
- Dopo un rilancio dei movimenti vanno rilanciati anche i saldi del mese.
- L'export XML è **semplificato**: non è importabile in un repository reale.
