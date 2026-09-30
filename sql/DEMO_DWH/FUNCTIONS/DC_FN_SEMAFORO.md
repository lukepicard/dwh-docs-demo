### Attenzione

Con esito `KO` la shell di lancio esce con return code `2`: lo schedulatore mette
il job in attesa e lo ritenta più tardi.

### Query utili

```sql
SELECT DEMO_DWH.DC_FN_SEMAFORO('DC_MOVIMENTI', '99001', DATE '2026-09-29') FROM DUAL;
```
