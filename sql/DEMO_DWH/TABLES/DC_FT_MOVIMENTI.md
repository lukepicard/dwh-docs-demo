### Perché

**Partizioni create da sole.** La tabella è partizionata per mese con `INTERVAL`:
il primo movimento di un nuovo mese fa creare a Oracle la partizione del mese,
con tutte le sottopartizioni per istituto del `SUBPARTITION TEMPLATE`. A inizio
mese non serve nessun intervento manuale.

**Gli storni non si cancellano.** Se un movimento va annullato, non si cancella
la riga: si aggiunge un nuovo movimento con causale `STORNO`, cioè di segno
opposto. Così lo storico resta vero: chi ha guardato il saldo ieri può
ritrovare gli stessi numeri e vedere che oggi è arrivato lo storno.

**Data contabile e data valuta.** La data contabile (`DAT_CONTABILE`) dice in
quale giorno il movimento conta per il saldo, ed è la data che partiziona la
tabella e che usano i saldi mensili. La data valuta (`DAT_VALUTA`) dice da
quando decorrono gli interessi: serve al loro calcolo, non ai saldi.

**Niente doppioni.** Il file della fonte può contenere lo stesso movimento più
volte: il flusso `wf_DC_MOVIMENTI` ne tiene uno solo, riconoscendolo
dall'identificativo (`ID_MOVIMENTO`).

**Ricaricare un mese intero.** Il rilancio di un singolo giorno cancella solo le
righe di quel giorno, e la shell `lancia_dc_movimenti.sh` lo fa da sola. Per
rifare un mese intero di una banca si svuota la sola coppia (mese, istituto):

```sql
ALTER TABLE DEMO_DWH.DC_FT_MOVIMENTI
  TRUNCATE SUBPARTITION FOR (DATE '2026-09-15', '99001');
```

Poi si rilanciano i giorni del mese. Il `FOR (data, istituto)` è una scelta
obbligata: le partizioni create da `INTERVAL` hanno nomi generati dal sistema
(`SYS_P…`), diversi da un ambiente all'altro. La sintassi `FOR` individua la
sottopartizione dai valori, con una data qualsiasi del mese, senza dover
conoscere il nome.

### Attenzione

- Un istituto che finisce nella sottopartizione `SP_DEFAULT` non si può
  ricaricare da solo (vale la stessa avvertenza di `DC_STG_MOVIMENTI`). Per un
  nuovo istituto va aggiunto il valore al `SUBPARTITION TEMPLATE`, che vale per i
  mesi futuri, e vanno divise le `SP_DEFAULT` dei mesi già esistenti con `SPLIT
  SUBPARTITION`.
- Gli importi restano nella divisa del conto: non c'è conversione.
- La tabella è letta anche da un cruscotto per il servizio clienti, fuori da
  questo repository: l'analisi d'impatto non lo vede.
