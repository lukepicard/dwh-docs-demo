### Perché

Raccoglie in un solo punto la scrittura del log delle elaborazioni e
l'aggiornamento del semaforo, così le shell non contengono DML.

Ogni procedura fa `COMMIT` da sola: il log resta scritto anche se il workflow
lanciato subito dopo fallisce.

### Query utili

Sblocco manuale dei movimenti per l'istituto 99001 e il giorno 29/09/2026:

```sql
EXEC DEMO_DWH.DC_PKG_ELABORAZIONE.SEGNA_PRONTO('DC_MOVIMENTI', 'DC_CARICO', '99001', DATE '2026-09-29');
```
