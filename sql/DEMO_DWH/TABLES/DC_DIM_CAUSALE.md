### Perché

Il segno della causale decide se un movimento fa entrare o uscire denaro. Nel
file della fonte l'importo arriva sempre positivo: è la causale a dire se va
sommato o sottratto. Così il segno sta in un solo posto e non può essere
scritto diversamente da un flusso all'altro.

Causali previste nella configurazione iniziale:

| Codice | Descrizione | Segno |
|---|---|---|
| `BONIFICO_IN` | Bonifico in entrata | + |
| `BONIFICO_OUT` | Bonifico in uscita | − |
| `STIPENDIO` | Accredito dello stipendio | + |
| `POS` | Pagamento con carta | − |
| `PRELIEVO` | Prelievo di contanti | − |
| `ACQUISTO_TITOLI` | Acquisto di titoli | − |
| `VENDITA_TITOLI` | Vendita di titoli | + |
| `STORNO` | Storno di un movimento precedente | − |

### Attenzione

- La tabella si aggiorna a mano, come una dimensione storicizzata: una modifica
  chiude la riga attiva valorizzando `DAT_FINE_VALIDITA` e ne inserisce una
  nuova. Non si fanno `UPDATE` sul segno di una riga attiva, altrimenti i
  ricaricamenti dei giorni passati cambierebbero risultato.
- Una causale che qui non esiste non viene caricata dal flusso dei movimenti:
  il movimento resta fuori e la quadratura tra staging e movimenti va in `KO`.
  Prima di rilanciare si aggiunge la causale.
- Nella demo lo storno ha sempre segno −, cioè riduce il saldo.
- I valori iniziali sono nel file `sql/DEMO_DWH/DATA/DC_DIM_CAUSALE.sql`.
