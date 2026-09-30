### Perché

Il tipo del titolo serve a una cosa sola: sapere come si calcola il controvalore.
Azioni e fondi hanno il prezzo in euro per unità; le obbligazioni hanno il
prezzo in percentuale del loro valore nominale (il valore che verrà rimborsato),
per esempio 98 vuol dire 98%. Per questo il controvalore delle obbligazioni si
divide per 100.

Titoli previsti nella configurazione iniziale (codici inventati):

| Codice | Descrizione | Tipo |
|---|---|---|
| `ZZ0000000011` | Azione Demo Alfa | `AZIONE` |
| `ZZ0000000029` | Azione Demo Beta | `AZIONE` |
| `ZZ0000000037` | Obbligazione Demo 2030 | `OBBLIGAZIONE` |
| `ZZ0000000045` | Obbligazione Demo 2035 | `OBBLIGAZIONE` |
| `ZZ0000000052` | Fondo Demo Azionario | `FONDO` |
| `ZZ0000000060` | Fondo Demo Bilanciato | `FONDO` |

### Attenzione

- Un titolo che negli ordini o nei prezzi non è in questa tabella non viene
  riconosciuto dal calcolo del controvalore: se ne accorge chi legge le righe con
  tipo vuoto. Prima di caricare un titolo nuovo va inserito qui.
- Per un'obbligazione inserita per errore come `FONDO` il controvalore risulta cento
  volte più grande: il tipo va controllato a mano al momento dell'inserimento.
- I valori iniziali sono nel file `sql/DEMO_DWH/DATA/DI_DIM_TITOLO.sql`.
