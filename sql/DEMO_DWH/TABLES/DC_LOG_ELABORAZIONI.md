### Perché

È il primo posto da guardare quando qualcosa non torna. L'`ID_ELABORAZIONE` si
ritrova in ogni riga di `DC_STG_MOVIMENTI`, `DC_FT_MOVIMENTI` e
`DC_FT_SALDI_MENSILI`, e in `DI_STG_ORDINI`, `DI_STG_PREZZI`, `DI_FT_POSIZIONI`
e `DI_FT_CONTROVALORI_MENSILI`: da un dato si risale a chi l'ha caricato e quando.

La tabella è **condivisa** con `DEMO_INVESTIMENTI`: le sue elaborazioni hanno
`COD_FLUSSO` `DI_CARICO` e `DI_POSIZIONI`, negli stessi campi.

### Attenzione

- Una riga rimasta `running` senza `DAT_FINE` indica una shell interrotta
  bruscamente (es. job terminato a forza). Il rilancio apre comunque una nuova
  elaborazione; per tenere pulito il log, la riga orfana si chiude a mano con
  `DC_PKG_ELABORAZIONE.CHIUDI(<id>, 'failed', '<motivo>')`.

### Query utili

Ultima esecuzione di ogni flusso e istituto:

```sql
SELECT *
  FROM DEMO_DWH.DC_LOG_ELABORAZIONI
 WHERE (COD_FLUSSO, COD_ISTITUTO, DAT_INIZIO) IN
       (SELECT COD_FLUSSO, COD_ISTITUTO, MAX(DAT_INIZIO)
          FROM DEMO_DWH.DC_LOG_ELABORAZIONI
         GROUP BY COD_FLUSSO, COD_ISTITUTO);
```
