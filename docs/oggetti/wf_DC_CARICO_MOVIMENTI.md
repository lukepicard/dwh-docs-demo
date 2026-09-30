---
title: wf_DC_CARICO_MOVIMENTI
parent: Shell e Workflow
grand_parent: DEMO_CONTI
nav_order: 7
---

# Workflow: `wf_DC_CARICO_MOVIMENTI`

> ⚙️ **Scheda generata automaticamente, non modificare a mano.** Commit analizzato `c276f3f` del 2026-09-30. Le spiegazioni scritte a mano vanno nella nota accanto al sorgente.

## Descrizione

DEMO_CONTI - carico dello staging, lanciato da lancia_dc_carico_movimenti.sh. Dall'intestazione dell'export: Export PowerCenter SEMPLIFICATO e INVENTATO a scopo dimostrativo. Contiene solo i campi principali; non e' importabile in un repository reale.

## Struttura

**Sessioni**

| Sessione | Mapping | Descrizione |
|---|---|---|
| `s_m_DC_CARICO_MOVIMENTI` | `m_DC_CARICO_MOVIMENTI` | Carico del file di una banca nello staging |

**Source**

| Nome | Tipo | Campi |
|---|---|---|
| `FF_MOVIMENTI_FONTE_A` | Flat File | 8 |

**Target**

| Nome | Tipo | Campi |
|---|---|---|
| [`DC_STG_MOVIMENTI`](DC_STG_MOVIMENTI.md) | Oracle | 10 |

**Parametri:** `$$COD_ISTITUTO`, `$$DAT_RIFERIMENTO`, `$$ID_ELABORAZIONE`

## Chi lo chiama

| Chiamante | Contesto | Campi | Dove |
|---|---|---|---|
| [`lancia_dc_carico_movimenti.sh`](lancia_dc_carico_movimenti.md) | STATEMENT | — | [`script/demo_conti/lancia_dc_carico_movimenti.sh:16`](../../script/demo_conti/lancia_dc_carico_movimenti.sh) |

## Cosa scrive

| Oggetto scritto | Contesto | Campi | Dove |
|---|---|---|---|
| [`DC_STG_MOVIMENTI`](DC_STG_MOVIMENTI.md) | POST_SQL | COD_CAUSALE, COD_ISTITUTO | [`powercenter/DEMO_CONTI/wf_DC_CARICO_MOVIMENTI.xml:106`](../../powercenter/DEMO_CONTI/wf_DC_CARICO_MOVIMENTI.xml) |
| [`DC_STG_MOVIMENTI`](DC_STG_MOVIMENTI.md) | TARGET | COD_CAUSALE, COD_CONTO, COD_ISTITUTO, COD_SISTEMA_FONTE, DAT_CONTABILE, DAT_RIFERIMENTO, DAT_VALUTA, ID_ELABORAZIONE, ID_MOVIMENTO, IMP_MOVIMENTO | [`powercenter/DEMO_CONTI/wf_DC_CARICO_MOVIMENTI.xml:28`](../../powercenter/DEMO_CONTI/wf_DC_CARICO_MOVIMENTI.xml) |

## Cosa legge

| Oggetto letto | Contesto | Campi | Dove |
|---|---|---|---|
| `FF_MOVIMENTI_FONTE_A` | SOURCE | COD_CAUSALE, COD_CONTO, COD_ISTITUTO, DATA_CONTABILE, DATA_RIFERIMENTO, DATA_VALUTA, ID_MOVIMENTO, IMP_MOVIMENTO | [`powercenter/DEMO_CONTI/wf_DC_CARICO_MOVIMENTI.xml:15`](../../powercenter/DEMO_CONTI/wf_DC_CARICO_MOVIMENTI.xml) |

## Impatti indiretti

Oggetti raggiunti a catena, a valle dei riferimenti diretti:

| Livello | Oggetto | Ruolo | Raggiunto da |
|---|---|---|---|
| 2 | [`DC_VC_QUADRATURA`](DC_VC_QUADRATURA.md) | legge | [`DC_STG_MOVIMENTI`](DC_STG_MOVIMENTI.md) |
| 2 | [`wf_DC_MOVIMENTI`](wf_DC_MOVIMENTI.md) | legge | [`DC_STG_MOVIMENTI`](DC_STG_MOVIMENTI.md) |
| 3 | `APP_REPORTING` | consuma | [`DC_VC_QUADRATURA`](DC_VC_QUADRATURA.md) |
| 3 | [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) | è scritto da | [`wf_DC_MOVIMENTI`](wf_DC_MOVIMENTI.md) |
| 3 | `UTENTI_CONTI` | consuma | [`DC_VC_QUADRATURA`](DC_VC_QUADRATURA.md) |
| 3 | [`lancia_dc_movimenti.sh`](lancia_dc_movimenti.md) | chiama | [`wf_DC_MOVIMENTI`](wf_DC_MOVIMENTI.md) |
| 4 | [`DC_VC_VOLUMI_GIORNALIERI`](DC_VC_VOLUMI_GIORNALIERI.md) | legge | [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) |
| 4 | [`DI_VC_REGOLAMENTO_ORDINI`](DI_VC_REGOLAMENTO_ORDINI.md) | legge | [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) |
| 4 | [`wf_DC_SALDI`](wf_DC_SALDI.md) | legge | [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) |
| 5 | `APP_CONTROLLO_TITOLI` | consuma | [`DI_VC_REGOLAMENTO_ORDINI`](DI_VC_REGOLAMENTO_ORDINI.md) |
| 5 | [`DC_FT_SALDI_MENSILI`](DC_FT_SALDI_MENSILI.md) | è scritto da | [`wf_DC_SALDI`](wf_DC_SALDI.md) |
| 5 | [`lancia_dc_saldi.sh`](lancia_dc_saldi.md) | chiama | [`wf_DC_SALDI`](wf_DC_SALDI.md) |

Diagramma dei primi due livelli:

```mermaid
flowchart LR
  n0["wf_DC_CARICO_MOVIMENTI"]
  n1["DC_STG_MOVIMENTI"]
  n2["DC_VC_QUADRATURA"]
  n3["lancia_dc_carico_movimenti.sh"]
  n4["wf_DC_MOVIMENTI"]
  n1 -->|letto da| n2
  n1 -->|letto da| n4
  n3 -->|scrive| n1
  n3 -.->|chiama| n0
  n0 -->|scrive| n1
  class n0 centro
  classDef centro fill:#1f4e79,stroke:#1f4e79,color:#ffffff
```

## Note

Nota scritta a mano, da modificare nel repository: `powercenter/DEMO_CONTI/wf_DC_CARICO_MOVIMENTI.md`

### Perché

Dopo il caricamento, la sessione esegue una **Post SQL** che normalizza
`COD_CAUSALE` (maiuscolo, senza spazi). Il sistema fonte a volte invia codici
come `'pos '` o `'Stipendio'`: senza normalizzazione il flusso dei movimenti non
li riconoscerebbe e lascerebbe fuori movimenti che hanno una causale valida.

### Attenzione

- Si rilancia sempre tramite la shell `lancia_dc_carico_movimenti.sh`, che
  svuota prima la partizione dell'istituto: la sessione non tronca il target.
- Se il file non è arrivato, la sessione fallisce e la shell esce con `3`. Prima
  di rilanciare verificare che il file sia nella cartella `DEMO_INPUT_DIR`.
- Il carico non toglie i doppioni: lo fa `wf_DC_MOVIMENTI`.
- L'export XML è **semplificato**: non è importabile in un repository reale.

## Sorgente

[`powercenter/DEMO_CONTI/wf_DC_CARICO_MOVIMENTI.xml`](../../powercenter/DEMO_CONTI/wf_DC_CARICO_MOVIMENTI.xml)

## Limiti

L'analisi legge solo i file del repository. Non vede:

- **sinonimi** e **db link**: un oggetto letto tramite sinonimo o da un altro database non
  risulta collegato;
- **SQL dinamico**: le istruzioni costruite a runtime (`EXECUTE IMMEDIATE`, stringhe concatenate)
  sono segnalate come "da verificare", ma gli oggetti che toccano non sono noti;
- **oggetti non versionati**: tabelle, job o report che non stanno in questo repository
  (per esempio un cruscotto o un job di manutenzione dello schedulatore).

I risultati vanno sempre confermati con chi conosce il flusso.
