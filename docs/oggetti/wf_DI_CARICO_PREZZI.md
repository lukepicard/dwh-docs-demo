---
title: wf_DI_CARICO_PREZZI
parent: Shell e Workflow
grand_parent: DEMO_INVESTIMENTI
nav_order: 11
---

# Workflow: `wf_DI_CARICO_PREZZI`

> ⚙️ **Scheda generata automaticamente, non modificare a mano.** Commit analizzato `c276f3f` del 2026-09-30. Le spiegazioni scritte a mano vanno nella nota accanto al sorgente.

## Descrizione

DEMO_INVESTIMENTI - carico dei prezzi, lanciato da lancia_di_carico.sh. Dall'intestazione dell'export: Export PowerCenter SEMPLIFICATO e INVENTATO a scopo dimostrativo. Contiene solo i campi principali; non e' importabile in un repository reale.

## Struttura

**Sessioni**

| Sessione | Mapping | Descrizione |
|---|---|---|
| `s_m_DI_CARICO_PREZZI` | `m_DI_CARICO_PREZZI` | Carico del file dei prezzi di una banca nello staging |

**Source**

| Nome | Tipo | Campi |
|---|---|---|
| `FF_PREZZI_FONTE_C` | Flat File | 4 |

**Target**

| Nome | Tipo | Campi |
|---|---|---|
| [`DI_STG_PREZZI`](DI_STG_PREZZI.md) | Oracle | 6 |

**Parametri:** `$$COD_ISTITUTO`, `$$DAT_RIFERIMENTO`, `$$ID_ELABORAZIONE`

## Chi lo chiama

| Chiamante | Contesto | Campi | Dove |
|---|---|---|---|
| [`lancia_di_carico.sh`](lancia_di_carico.md) | STATEMENT | — | [`script/demo_investimenti/lancia_di_carico.sh:21`](../../script/demo_investimenti/lancia_di_carico.sh) |

## Cosa scrive

| Oggetto scritto | Contesto | Campi | Dove |
|---|---|---|---|
| [`DI_STG_PREZZI`](DI_STG_PREZZI.md) | POST_SQL | COD_ISTITUTO, COD_TITOLO | [`powercenter/DEMO_INVESTIMENTI/wf_DI_CARICO_PREZZI.xml:87`](../../powercenter/DEMO_INVESTIMENTI/wf_DI_CARICO_PREZZI.xml) |
| [`DI_STG_PREZZI`](DI_STG_PREZZI.md) | TARGET | COD_ISTITUTO, COD_SISTEMA_FONTE, COD_TITOLO, DAT_RIFERIMENTO, ID_ELABORAZIONE, IMP_PREZZO | [`powercenter/DEMO_INVESTIMENTI/wf_DI_CARICO_PREZZI.xml:24`](../../powercenter/DEMO_INVESTIMENTI/wf_DI_CARICO_PREZZI.xml) |

## Cosa legge

| Oggetto letto | Contesto | Campi | Dove |
|---|---|---|---|
| `FF_PREZZI_FONTE_C` | SOURCE | COD_ISTITUTO, COD_TITOLO, DATA_RIFERIMENTO, IMP_PREZZO | [`powercenter/DEMO_INVESTIMENTI/wf_DI_CARICO_PREZZI.xml:15`](../../powercenter/DEMO_INVESTIMENTI/wf_DI_CARICO_PREZZI.xml) |

## Impatti indiretti

Oggetti raggiunti a catena, a valle dei riferimenti diretti:

| Livello | Oggetto | Ruolo | Raggiunto da |
|---|---|---|---|
| 2 | [`DI_STG_ORDINI`](DI_STG_ORDINI.md) | è scritto da | [`lancia_di_carico.sh`](lancia_di_carico.md) |
| 2 | [`wf_DI_POSIZIONI`](wf_DI_POSIZIONI.md) | legge | [`DI_STG_PREZZI`](DI_STG_PREZZI.md) |
| 3 | [`DI_FT_CONTROVALORI_MENSILI`](DI_FT_CONTROVALORI_MENSILI.md) | è scritto da | [`wf_DI_POSIZIONI`](wf_DI_POSIZIONI.md) |
| 3 | [`DI_FT_POSIZIONI`](DI_FT_POSIZIONI.md) | è scritto da | [`wf_DI_POSIZIONI`](wf_DI_POSIZIONI.md) |
| 3 | [`DI_VC_REGOLAMENTO_ORDINI`](DI_VC_REGOLAMENTO_ORDINI.md) | legge | [`DI_STG_ORDINI`](DI_STG_ORDINI.md) |
| 3 | [`lancia_di_posizioni.sh`](lancia_di_posizioni.md) | chiama | [`wf_DI_POSIZIONI`](wf_DI_POSIZIONI.md) |
| 4 | `APP_CONTROLLO_TITOLI` | consuma | [`DI_VC_REGOLAMENTO_ORDINI`](DI_VC_REGOLAMENTO_ORDINI.md) |
| 4 | [`DI_VC_QUADRATURA`](DI_VC_QUADRATURA.md) | legge | [`DI_FT_POSIZIONI`](DI_FT_POSIZIONI.md) |
| 5 | `APP_REPORTING` | consuma | [`DI_VC_QUADRATURA`](DI_VC_QUADRATURA.md) |
| 5 | `UTENTI_INVESTIMENTI` | consuma | [`DI_VC_QUADRATURA`](DI_VC_QUADRATURA.md) |

Diagramma dei primi due livelli:

```mermaid
flowchart LR
  n0["wf_DI_CARICO_PREZZI"]
  n1["DI_STG_ORDINI"]
  n2["DI_STG_PREZZI"]
  n3["lancia_di_carico.sh"]
  n4["wf_DI_POSIZIONI"]
  n1 -->|letto da| n4
  n2 -->|letto da| n4
  n3 -->|scrive| n1
  n3 -->|scrive| n2
  n3 -.->|chiama| n0
  n0 -->|scrive| n2
  class n0 centro
  classDef centro fill:#1f4e79,stroke:#1f4e79,color:#ffffff
```

## Note

Nota scritta a mano, da modificare nel repository: `powercenter/DEMO_INVESTIMENTI/wf_DI_CARICO_PREZZI.md`

### Perché

Dopo il caricamento, la sessione esegue una **Post SQL** che normalizza
`COD_TITOLO` (maiuscolo, senza spazi). Il sistema fonte a volte invia codici
ISIN con uno spazio o in minuscolo: senza normalizzazione il prezzo non
verrebbe abbinato al titolo, il flusso delle posizioni lo considererebbe mancante
e riporterebbe il prezzo del giorno prima.

### Attenzione

- Si rilancia sempre tramite la shell `lancia_di_carico.sh`, che svuota prima la
  partizione dell'istituto: la sessione non tronca il target.
- Un prezzo che manca nel file non è un errore del carico: lo gestisce il flusso
  delle posizioni, riportando l'ultimo prezzo disponibile (vedere `DI_FT_POSIZIONI`).
- Se il file non è arrivato, la sessione fallisce e la shell esce con `3`. Prima
  di rilanciare verificare che il file sia nella cartella `DEMO_INPUT_DIR`.
- L'export XML è **semplificato**: non è importabile in un repository reale.

## Sorgente

[`powercenter/DEMO_INVESTIMENTI/wf_DI_CARICO_PREZZI.xml`](../../powercenter/DEMO_INVESTIMENTI/wf_DI_CARICO_PREZZI.xml)

## Limiti

L'analisi legge solo i file del repository. Non vede:

- **sinonimi** e **db link**: un oggetto letto tramite sinonimo o da un altro database non
  risulta collegato;
- **SQL dinamico**: le istruzioni costruite a runtime (`EXECUTE IMMEDIATE`, stringhe concatenate)
  sono segnalate come "da verificare", ma gli oggetti che toccano non sono noti;
- **oggetti non versionati**: tabelle, job o report che non stanno in questo repository
  (per esempio un cruscotto o un job di manutenzione dello schedulatore).

I risultati vanno sempre confermati con chi conosce il flusso.
