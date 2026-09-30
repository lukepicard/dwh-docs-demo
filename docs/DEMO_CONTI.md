---
title: DEMO_CONTI
nav_order: 2
has_children: true
---

# DEMO_CONTI — Dai movimenti all'estratto conto

> **Schema target principale:** `DEMO_DWH`
>
> **Referente tecnico:** Team DWH (fittizio)
>
> **Ultima verifica:** 2026-09

---

## Panoramica

DEMO_CONTI è il motore che, ogni giorno, carica i movimenti dei conti correnti
(bonifici, stipendi, pagamenti con carta, prelievi, …) e, ogni mese, calcola per
ogni conto il saldo iniziale, le entrate, le uscite e il saldo finale: cioè i dati
dell'estratto conto. Ogni movimento ha una causale, e la causale dice se il
denaro entra (+) o esce (−).
Ogni flusso può girare per una singola banca (`-i <ISTITUTO>`) o per tutte (`-i ALL`).

---

## Catena dei flussi

```
FONTE_A (file giornaliero)
   │  semaforo DC_CARICO
   ▼
wf_DC_CARICO_MOVIMENTI ──► DC_STG_MOVIMENTI     (solo l'ultimo giorno caricato)
   │  semaforo DC_MOVIMENTI
   ▼
wf_DC_MOVIMENTI ─────────► DC_FT_MOVIMENTI      (storico mensile, senza doppioni)
   │  semaforo DC_SALDI      (dall'ultimo giorno del mese)
   ▼
wf_DC_SALDI ─────────────► DC_FT_SALDI_MENSILI  (per conto e mese)
```

Ogni shell, quando finisce bene una banca, segna pronto il flusso successivo in
[`DC_CTL_SEMAFORO`](oggetti/DC_CTL_SEMAFORO.md) e scrive l'esito in
[`DC_LOG_ELABORAZIONI`](oggetti/DC_LOG_ELABORAZIONI.md).

---

## Oggetti del motore

| Oggetto | Tipo | Ruolo |
|---|---|---|
| [`DC_DIM_CAUSALE`](oggetti/DC_DIM_CAUSALE.md) | Tabella target | Anagrafica delle causali, con il segno + / − |
| [`DC_STG_MOVIMENTI`](oggetti/DC_STG_MOVIMENTI.md) | Tabella work | Staging dei movimenti dal sistema fonte, partizionata per istituto |
| [`DC_FT_MOVIMENTI`](oggetti/DC_FT_MOVIMENTI.md) | Tabella target | Movimenti con causale e segno, storico mensile per istituto |
| [`DC_FT_SALDI_MENSILI`](oggetti/DC_FT_SALDI_MENSILI.md) | Tabella target | Saldo iniziale, entrate, uscite e saldo finale per conto e mese |
| [`DC_CTL_SEMAFORO`](oggetti/DC_CTL_SEMAFORO.md) | Tabella di controllo | Semaforo dei flussi per fonte, banca e data |
| [`DC_LOG_ELABORAZIONI`](oggetti/DC_LOG_ELABORAZIONI.md) | Tabella di log | Esito di ogni esecuzione |
| [`DC_VC_QUADRATURA`](oggetti/DC_VC_QUADRATURA.md) | Vista di controllo | Quadratura staging / movimenti e quadratura dei saldi |
| [`DC_VC_VOLUMI_GIORNALIERI`](oggetti/DC_VC_VOLUMI_GIORNALIERI.md) | Vista di controllo | Movimenti del giorno rispetto alla media degli ultimi 20 giorni |
| [`DC_PKG_ELABORAZIONE`](oggetti/DC_PKG_ELABORAZIONE.md) | Package | Apertura e chiusura delle elaborazioni, sblocco del semaforo |
| [`DC_FN_SEMAFORO`](oggetti/DC_FN_SEMAFORO.md) | Funzione | Dice se un flusso può partire |
| [`DC_PRC_PULIZIA_STORICO`](oggetti/DC_PRC_PULIZIA_STORICO.md) | Procedura | Manutenzione mensile di log e semaforo |
| `DC_SEQ_ELABORAZIONE` | Sequence | Genera `ID_ELABORAZIONE` |
| [`dc_comune.sh`](oggetti/dc_comune.md) | Libreria shell | Funzioni comuni alle shell di lancio |

---

## Oggetti condivisi con DEMO_INVESTIMENTI

Semaforo, log e package di elaborazione servono anche al motore
[DEMO_INVESTIMENTI](DEMO_INVESTIMENTI.md), che non ne ha una copia:
[`DC_CTL_SEMAFORO`](oggetti/DC_CTL_SEMAFORO.md), [`DC_LOG_ELABORAZIONI`](oggetti/DC_LOG_ELABORAZIONI.md),
[`DC_PKG_ELABORAZIONE`](oggetti/DC_PKG_ELABORAZIONE.md), [`DC_FN_SEMAFORO`](oggetti/DC_FN_SEMAFORO.md)
e la libreria [`dc_comune.sh`](oggetti/dc_comune.md). Chi li modifica cambia il comportamento di
entrambi i motori: le loro schede mostrano gli impatti verso i flussi `DC_*` e `DI_*`.

---

## Flussi presenti

| Workflow | Tecnologia | Frequenza | Target |
|---|---|---|---|
| [`wf_DC_CARICO_MOVIMENTI`](oggetti/wf_DC_CARICO_MOVIMENTI.md) | PowerCenter | Giornaliera | `DEMO_DWH.DC_STG_MOVIMENTI` |
| [`wf_DC_MOVIMENTI`](oggetti/wf_DC_MOVIMENTI.md) | PowerCenter | Giornaliera | `DEMO_DWH.DC_FT_MOVIMENTI` |
| [`wf_DC_SALDI`](oggetti/wf_DC_SALDI.md) | PowerCenter | Mensile | `DEMO_DWH.DC_FT_SALDI_MENSILI` |
| [`lancia_dc_carico_movimenti.sh`](oggetti/lancia_dc_carico_movimenti.md) | Shell | Giornaliera | Lancia `wf_DC_CARICO_MOVIMENTI` |
| [`lancia_dc_movimenti.sh`](oggetti/lancia_dc_movimenti.md) | Shell | Giornaliera | Lancia `wf_DC_MOVIMENTI` |
| [`lancia_dc_saldi.sh`](oggetti/lancia_dc_saldi.md) | Shell | Mensile | Lancia `wf_DC_SALDI` |

---

## Dipendenze upstream

- **Sorgenti:** file giornaliero dei movimenti di `FONTE_A`, uno per banca;
  il suo arrivo è segnato in `DC_CTL_SEMAFORO` (flusso `DC_CARICO`, fonte `FONTE_A`)
- **Dipendenze da altri flussi:** nessuna fuori dal motore

---

## Scheduling Control-M

- **Folder:** `DEMO_CONTI`
- **Job giornalieri:** `DC_CARICO_GIORN` → `DC_MOV_GIORN`, entrambi con `-i ALL`
- **Job mensile:** `DC_SALDI_MENS`, con `-i ALL`, dal 2° giorno lavorativo del mese
- **Finestra esecuzione:** ogni giorno lavorativo, ore 08:00–18:00
- **Semaforo KO:** return code `2`, il job va in stand-by e viene ritentato

---

## Note operative

- **Rilancio di una banca:** rilanciare la shell del flusso con
  `-i <ISTITUTO> -d <YYYYMMDD> -f`, poi i flussi a valle nello stesso ordine
  della catena.
- **Dopo ogni giro:** controllare
  [`DC_VC_QUADRATURA`](oggetti/DC_VC_QUADRATURA.md) e
  [`DC_VC_VOLUMI_GIORNALIERI`](oggetti/DC_VC_VOLUMI_GIORNALIERI.md).
- **Storni:** non si cancella mai un movimento, si aggiunge uno storno. Per questo
  i saldi dei mesi passati si rifanno solo rilanciando `lancia_dc_saldi.sh`.
- Termini e sigle: vedere il [glossario](glossario.md).
- Tutti i nomi (schemi, tabelle, workflow, persone) sono **inventati** a scopo
  dimostrativo.
