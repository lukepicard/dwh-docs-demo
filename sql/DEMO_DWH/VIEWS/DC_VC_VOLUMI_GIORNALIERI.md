### Perché

Serve a intercettare un file arrivato a metà (o un giorno caricato due volte)
prima che i saldi lo ereditino. Un giorno con meno della metà dei movimenti
abituali è quasi sempre un file incompleto, non una giornata tranquilla.

### Attenzione

- La media è sugli ultimi 20 giorni **presenti in tabella**, non sui 20 giorni
  di calendario: sabati, domeniche e festività senza file non contano.
- I movimenti contati sono quelli già senza doppioni, cioè quelli di
  `DC_FT_MOVIMENTI`: un file con molti doppioni non risulta gonfiato.
- Nei primi giorni di vita di un istituto la media non esiste e l'esito è `N/D`.
- Un `KO` non è per forza un errore (es. giornata di chiusura parziale), ma va
  sempre verificato con chi gestisce il sistema fonte.
- La vista è letta dalla reportistica di controllo (vedi "Chi consuma" nella
  scheda): la soglia del 50% è concordata con loro e non va cambiata da sola.

### Query utili

```sql
SELECT *
  FROM DEMO_DWH.DC_VC_VOLUMI_GIORNALIERI
 WHERE ESITO = 'KO'
 ORDER BY DAT_CONTABILE DESC;
```
