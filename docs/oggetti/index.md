---
title: Schede di oggetto
nav_order: 4
---

# Schede di oggetto

> ⚙️ **Scheda generata automaticamente, non modificare a mano.** Commit analizzato `c276f3f` del 2026-09-30. Le spiegazioni scritte a mano vanno nella nota accanto al sorgente.

La documentazione degli oggetti è su due livelli:

- la **scheda** di ogni oggetto la scrive uno script, a partire dal codice: struttura, chi scrive, chi legge, chi consuma e impatti a catena. Non si modifica a mano;
- la **nota** la scrive una persona, solo se serve: è il file `.md` accanto al sorgente, con lo stesso nome, e contiene quello che il codice non dice (il perché delle scelte, le avvertenze). La scheda la riporta così com'è.

Come si documenta un oggetto: vedi [come documentare](../come_documentare.md).

| Oggetto | Tipo | Impatti diretti | Impatti indiretti | Nota | Da verificare |
|---|---|---|---|---|---|
| [`dc_comune.sh`](dc_comune.md) | shell | 5 | 18 | sì | — |
| [`DC_CTL_SEMAFORO`](DC_CTL_SEMAFORO.md) | tabella | 3 | 24 | sì | — |
| [`DC_DIM_CAUSALE`](DC_DIM_CAUSALE.md) | tabella | 2 | 11 | sì | — |
| [`DC_FN_SEMAFORO`](DC_FN_SEMAFORO.md) | funzione | 1 | 23 | sì | — |
| [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) | tabella | 6 | 5 | sì | — |
| [`DC_FT_SALDI_MENSILI`](DC_FT_SALDI_MENSILI.md) | tabella | 3 | 2 | sì | — |
| [`DC_LOG_ELABORAZIONI`](DC_LOG_ELABORAZIONI.md) | tabella | 2 | 0 | sì | — |
| [`DC_PKG_ELABORAZIONE`](DC_PKG_ELABORAZIONE.md) | package | 3 | 24 | sì | — |
| [`DC_PRC_PULIZIA_STORICO`](DC_PRC_PULIZIA_STORICO.md) | procedura | 2 | 25 | sì | SQL dinamico |
| [`DC_STG_MOVIMENTI`](DC_STG_MOVIMENTI.md) | tabella | 4 | 10 | sì | ⚠️ nota |
| [`DC_VC_QUADRATURA`](DC_VC_QUADRATURA.md) | vista | 2 | 0 | sì | — |
| [`DC_VC_VOLUMI_GIORNALIERI`](DC_VC_VOLUMI_GIORNALIERI.md) | vista | 1 | 0 | sì | — |
| [`DI_DIM_TITOLO`](DI_DIM_TITOLO.md) | tabella | 3 | 7 | sì | — |
| [`DI_FT_CONTROVALORI_MENSILI`](DI_FT_CONTROVALORI_MENSILI.md) | tabella | 2 | 0 | sì | — |
| [`DI_FT_POSIZIONI`](DI_FT_POSIZIONI.md) | tabella | 3 | 2 | sì | — |
| [`DI_STG_ORDINI`](DI_STG_ORDINI.md) | tabella | 4 | 7 | sì | — |
| [`DI_STG_PREZZI`](DI_STG_PREZZI.md) | tabella | 3 | 6 | sì | — |
| [`DI_VC_QUADRATURA`](DI_VC_QUADRATURA.md) | vista | 2 | 0 | sì | — |
| [`DI_VC_REGOLAMENTO_ORDINI`](DI_VC_REGOLAMENTO_ORDINI.md) | vista | 1 | 0 | sì | — |
| [`lancia_dc_carico_movimenti.sh`](lancia_dc_carico_movimenti.md) | shell | 1 | 12 | sì | — |
| [`lancia_dc_movimenti.sh`](lancia_dc_movimenti.md) | shell | 1 | 9 | sì | — |
| [`lancia_dc_saldi.sh`](lancia_dc_saldi.md) | shell | 1 | 3 | sì | — |
| [`lancia_di_carico.sh`](lancia_di_carico.md) | shell | 2 | 9 | sì | — |
| [`lancia_di_posizioni.sh`](lancia_di_posizioni.md) | shell | 2 | 4 | sì | — |
| [`wf_DC_CARICO_MOVIMENTI`](wf_DC_CARICO_MOVIMENTI.md) | workflow | 2 | 12 | sì | — |
| [`wf_DC_MOVIMENTI`](wf_DC_MOVIMENTI.md) | workflow | 2 | 9 | sì | — |
| [`wf_DC_SALDI`](wf_DC_SALDI.md) | workflow | 2 | 3 | sì | — |
| [`wf_DI_CARICO_ORDINI`](wf_DI_CARICO_ORDINI.md) | workflow | 2 | 10 | sì | — |
| [`wf_DI_CARICO_PREZZI`](wf_DI_CARICO_PREZZI.md) | workflow | 2 | 10 | sì | — |
| [`wf_DI_POSIZIONI`](wf_DI_POSIZIONI.md) | workflow | 3 | 3 | sì | — |

## Riferimenti da verificare

Istruzioni di SQL dinamico: l'analisi non può sapere quali oggetti toccano.

- [`DC_PRC_PULIZIA_STORICO`](DC_PRC_PULIZIA_STORICO.md): [`sql/DEMO_DWH/PROCEDURES/DC_PRC_PULIZIA_STORICO.sql:32`](../../sql/DEMO_DWH/PROCEDURES/DC_PRC_PULIZIA_STORICO.sql)

## Oggetti citati ma non definiti nel repository

| Oggetto | Tipo | Citato da |
|---|---|---|
| `APP_CONTROLLO_TITOLI` | schema | [`DI_VC_REGOLAMENTO_ORDINI`](DI_VC_REGOLAMENTO_ORDINI.md) |
| `APP_REPORTING` | schema | [`DC_VC_QUADRATURA`](DC_VC_QUADRATURA.md), [`DC_VC_VOLUMI_GIORNALIERI`](DC_VC_VOLUMI_GIORNALIERI.md), [`DI_VC_QUADRATURA`](DI_VC_QUADRATURA.md) |
| `FF_MOVIMENTI_FONTE_A` | file | [`wf_DC_CARICO_MOVIMENTI`](wf_DC_CARICO_MOVIMENTI.md) |
| `FF_ORDINI_FONTE_B` | file | [`wf_DI_CARICO_ORDINI`](wf_DI_CARICO_ORDINI.md) |
| `FF_PREZZI_FONTE_C` | file | [`wf_DI_CARICO_PREZZI`](wf_DI_CARICO_PREZZI.md) |
| `UTENTI_CONTI` | schema | [`DC_VC_QUADRATURA`](DC_VC_QUADRATURA.md) |
| `UTENTI_INVESTIMENTI` | schema | [`DI_VC_QUADRATURA`](DI_VC_QUADRATURA.md) |
