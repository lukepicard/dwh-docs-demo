### Perché

**Prezzo mancante.** Se nel file dei prezzi del giorno manca un titolo, il flusso
usa l'ultimo prezzo disponibile, cioè quello della posizione del giorno
precedente, e marca la riga con `FLG_PREZZO_RIPORTATO = 'S'`. La scelta è nella
query di override della source, che unisce ordini, posizione precedente e prezzo
del giorno. Preferiamo un numero marcato a un buco: i controvalori di fine mese
non restano senza valore, e chi li legge vede quanti titoli sono valorizzati con
un prezzo vecchio.

**Obbligazioni: si divide per 100.** Nel calcolo del controvalore, il tipo del
titolo (letto con la lookup su `DI_DIM_TITOLO`) decide la formula: quantità per
prezzo per azioni e fondi; quantità per prezzo diviso 100 per le obbligazioni,
perché il loro prezzo è una percentuale del valore nominale. Un titolo mai
quotato ha controvalore zero.

**Un workflow, due calcoli.** Le posizioni si calcolano ogni giorno, i
controvalori solo nell'ultimo giorno del mese: la seconda sessione parte solo se
il parametro `FLG_FINE_MESE` è `S` (lo imposta la shell).

### Attenzione

- Si rilancia sempre tramite la shell `lancia_di_posizioni.sh`, che cancella
  prima le posizioni del giorno (e, a fine mese, i controvalori del mese). Lanciato
  a mano dal client PowerCenter, il workflow duplicherebbe i dati, perché le
  sessioni non troncano il target.
- La posizione di un giorno parte da quella del giorno prima: dopo un rilancio
  di un giorno passato vanno rilanciati in ordine anche i giorni successivi.
- Legge e scrive `DI_FT_POSIZIONI` (la posizione precedente è in ingresso, la
  nuova in uscita): è normale, e la scheda lo elenca sia tra gli oggetti letti sia
  tra quelli scritti.
- L'export XML è **semplificato**: non è importabile in un repository reale.
