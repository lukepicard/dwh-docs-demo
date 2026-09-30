### Perché

Il semaforo esiste per non far partire un flusso su dati incompleti. Ogni flusso
aspetta una o più fonti, per istituto e data di riferimento, e parte solo quando
sono tutte pronte.

| Flusso (`COD_FLUSSO`) | Aspetta la fonte (`COD_FONTE`) | Chi la segna pronta |
|---|---|---|
| `DC_CARICO` | `FONTE_A` | Processo di ricezione file, fuori da questo repository |
| `DC_MOVIMENTI` | `DC_CARICO` | `lancia_dc_carico_movimenti.sh` a fine carico |
| `DC_SALDI` | `DC_MOVIMENTI` | `lancia_dc_movimenti.sh` a fine elaborazione |
| `DI_CARICO` | `FONTE_B` e `FONTE_C` | Processo di ricezione file, fuori da questo repository |
| `DI_POSIZIONI` | `DI_CARICO` | `lancia_di_carico.sh` a fine carico |

La tabella è **condivisa** con `DEMO_INVESTIMENTI`, che ha aggiunto i suoi due
flussi (`DI_CARICO` e `DI_POSIZIONI`) senza una copia propria. `DI_CARICO` ha
due fonti: per partire devono essere pronte entrambe.

### Attenzione

- La riga di `FONTE_A` non la scrive nessun oggetto del repository: arriva dal
  processo di ricezione file. Se manca, il carico resta fermo con semaforo KO.
- Carico e movimenti girano ogni giorno, i saldi una volta al mese: la riga di
  `DC_SALDI` che conta è quella dell'ultimo giorno del mese. I saldi partono
  quindi solo dopo aver caricato i movimenti di quel giorno.
- Chi modifica questa tabella o `DC_FN_SEMAFORO` cambia il comportamento di
  entrambi i motori: la scheda mostra gli impatti di tutti e due.
- Per sbloccare a mano un flusso si chiama `DC_PKG_ELABORAZIONE.SEGNA_PRONTO`,
  oppure si lancia la shell con `-f`, che salta il semaforo.
