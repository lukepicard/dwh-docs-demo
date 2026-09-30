---
title: DEMO_INVESTIMENTI
nav_order: 3
has_children: true
---

# DEMO_INVESTIMENTI — Dal dossier titoli al controvalore

> **Schema target principale:** `DEMO_DWH`
>
> **Referente tecnico:** Team DWH (fittizio)
>
> **Ultima verifica:** 2026-09

---

## Panoramica

DEMO_INVESTIMENTI è il motore che, ogni giorno, carica gli ordini di acquisto e vendita
di titoli e i prezzi di chiusura, e calcola per ogni dossier quanti titoli possiede
(la **posizione**). Ogni ultimo giorno del mese calcola anche il **controvalore** del
dossier: quantità per prezzo di fine mese.
Ogni flusso può girare per una singola banca (`-i <ISTITUTO>`) o per tutte (`-i ALL`).

È un motore più piccolo di [DEMO_CONTI](DEMO_CONTI.md) e non ha semaforo, log e package
propri: usa quelli di DEMO_CONTI (vedere "Oggetti condivisi").

---

## Catena dei flussi

```
FONTE_B (ordini) + FONTE_C (prezzi), file giornalieri
   │  semaforo DI_CARICO (aspetta tutte e due le fonti)
   ▼
wf_DI_CARICO_ORDINI ──► DI_STG_ORDINI
wf_DI_CARICO_PREZZI ──► DI_STG_PREZZI
   │  semaforo DI_POSIZIONI
   ▼
wf_DI_POSIZIONI ──────► DI_FT_POSIZIONI              (ogni giorno, per dossier e titolo)
                  └───► DI_FT_CONTROVALORI_MENSILI   (solo l'ultimo giorno del mese)
```

Ogni shell, quando finisce bene una banca, segna pronto il flusso successivo in
[`DC_CTL_SEMAFORO`](oggetti/DC_CTL_SEMAFORO.md) e scrive l'esito in
[`DC_LOG_ELABORAZIONI`](oggetti/DC_LOG_ELABORAZIONI.md).

---

## Oggetti del motore

| Oggetto | Tipo | Ruolo |
|---|---|---|
| [`DI_DIM_TITOLO`](oggetti/DI_DIM_TITOLO.md) | Tabella target | Anagrafica dei titoli (ISIN, descrizione, tipo) |
| [`DI_STG_ORDINI`](oggetti/DI_STG_ORDINI.md) | Tabella work | Staging degli ordini eseguiti, partizionata per istituto |
| [`DI_STG_PREZZI`](oggetti/DI_STG_PREZZI.md) | Tabella work | Staging dei prezzi di chiusura, partizionata per istituto |
| [`DI_FT_POSIZIONI`](oggetti/DI_FT_POSIZIONI.md) | Tabella target | Posizione per dossier e titolo a fine giornata, storico mensile |
| [`DI_FT_CONTROVALORI_MENSILI`](oggetti/DI_FT_CONTROVALORI_MENSILI.md) | Tabella target | Controvalore per dossier e mese |
| [`DI_VC_QUADRATURA`](oggetti/DI_VC_QUADRATURA.md) | Vista di controllo | Posizione iniziale + acquisti − vendite = posizione finale |
| [`DI_VC_REGOLAMENTO_ORDINI`](oggetti/DI_VC_REGOLAMENTO_ORDINI.md) | Vista di controllo | Per ogni ordine, esiste l'addebito o l'accredito sul conto? |

---

## Oggetti condivisi con DEMO_CONTI

Questi oggetti sono definiti in DEMO_CONTI e non hanno una copia negli investimenti.
Le schede mostrano gli impatti verso i flussi di entrambi i motori.

| Oggetto | Tipo | Come lo usa DEMO_INVESTIMENTI |
|---|---|---|
| [`DC_CTL_SEMAFORO`](oggetti/DC_CTL_SEMAFORO.md) | Tabella di controllo | Ha le righe dei flussi `DI_CARICO` e `DI_POSIZIONI` |
| [`DC_LOG_ELABORAZIONI`](oggetti/DC_LOG_ELABORAZIONI.md) | Tabella di log | Registra le esecuzioni delle shell `lancia_di_*` |
| [`DC_PKG_ELABORAZIONE`](oggetti/DC_PKG_ELABORAZIONE.md) | Package | Apre e chiude le elaborazioni, sblocca il flusso a valle |
| [`DC_FN_SEMAFORO`](oggetti/DC_FN_SEMAFORO.md) | Funzione | Dice se `DI_CARICO` e `DI_POSIZIONI` possono partire |
| [`dc_comune.sh`](oggetti/dc_comune.md) | Libreria shell | Incluse da `lancia_di_carico.sh` e `lancia_di_posizioni.sh` |

---

## Flussi presenti

| Workflow | Tecnologia | Frequenza | Target |
|---|---|---|---|
| [`wf_DI_CARICO_ORDINI`](oggetti/wf_DI_CARICO_ORDINI.md) | PowerCenter | Giornaliera | `DEMO_DWH.DI_STG_ORDINI` |
| [`wf_DI_CARICO_PREZZI`](oggetti/wf_DI_CARICO_PREZZI.md) | PowerCenter | Giornaliera | `DEMO_DWH.DI_STG_PREZZI` |
| [`wf_DI_POSIZIONI`](oggetti/wf_DI_POSIZIONI.md) | PowerCenter | Giornaliera (controvalori: mensile) | `DEMO_DWH.DI_FT_POSIZIONI`, `DEMO_DWH.DI_FT_CONTROVALORI_MENSILI` |
| [`lancia_di_carico.sh`](oggetti/lancia_di_carico.md) | Shell | Giornaliera | Lancia `wf_DI_CARICO_ORDINI` e `wf_DI_CARICO_PREZZI` |
| [`lancia_di_posizioni.sh`](oggetti/lancia_di_posizioni.md) | Shell | Giornaliera | Lancia `wf_DI_POSIZIONI` |

---

## Dipendenze upstream

- **Sorgenti:** file giornaliero degli ordini eseguiti di `FONTE_B` e file giornaliero dei
  prezzi di chiusura di `FONTE_C`, uno per banca; il loro arrivo è segnato in
  `DC_CTL_SEMAFORO` (flusso `DI_CARICO`, fonti `FONTE_B` e `FONTE_C`)
- **Dipendenze da altri flussi:** nessuna per il calcolo di posizioni e controvalori. Il motore
  condivide con DEMO_CONTI gli oggetti di elaborazione (vedi sopra) e la vista di controllo
  [`DI_VC_REGOLAMENTO_ORDINI`](oggetti/DI_VC_REGOLAMENTO_ORDINI.md) legge
  [`DC_FT_MOVIMENTI`](oggetti/DC_FT_MOVIMENTI.md): è l'unico punto in cui i dati dei due motori si
  incontrano. Gli ordini non generano movimenti sui conti, li produce DEMO_CONTI

---

## Scheduling Control-M

- **Folder:** `DEMO_INVESTIMENTI`
- **Job giornalieri:** `DI_CARICO_GIORN` → `DI_POS_GIORN`, entrambi con `-i ALL`
- **Finestra esecuzione:** ogni giorno lavorativo, ore 08:00–18:00
- **Semaforo KO:** return code `2`, il job va in stand-by e viene ritentato

---

## Note operative

- **Rilancio di una banca:** rilanciare la shell del flusso con
  `-i <ISTITUTO> -d <YYYYMMDD> -f`, poi i flussi a valle nello stesso ordine
  della catena.
- **Dopo ogni giro:** controllare [`DI_VC_QUADRATURA`](oggetti/DI_VC_QUADRATURA.md) e
  [`DI_VC_REGOLAMENTO_ORDINI`](oggetti/DI_VC_REGOLAMENTO_ORDINI.md). Quest'ultima ha senso solo
  dopo che sono stati caricati i movimenti dei conti dello stesso giorno.
- **Prezzi mancanti:** se il prezzo di un titolo manca si usa l'ultimo disponibile e la riga è
  marcata (`FLG_PREZZO_RIPORTATO`). Nei controvalori mensili la colonna
  `NUM_TITOLI_PREZZO_RIPORTATO` dice quanti titoli del dossier sono valorizzati così.
- **Obbligazioni:** hanno il prezzo in percentuale del valore nominale, quindi il controvalore
  si divide per 100.
- Termini e sigle: vedere il [glossario](glossario.md).
- Tutti i nomi (schemi, tabelle, workflow, titoli, persone) sono **inventati** a scopo
  dimostrativo.
