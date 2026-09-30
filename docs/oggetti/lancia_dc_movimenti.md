---
title: lancia_dc_movimenti.sh
parent: Shell e Workflow
grand_parent: DEMO_CONTI
nav_order: 3
---

# Shell: `lancia_dc_movimenti.sh`

> ⚙️ **Scheda generata automaticamente, non modificare a mano.** Commit analizzato `c276f3f` del 2026-09-30. Le spiegazioni scritte a mano vanno nella nota accanto al sorgente.

## Descrizione

Lancia wf_DC_MOVIMENTI per una banca (-i <ISTITUTO>) o per tutte le banche attive (-i ALL): toglie i doppioni, assegna causale e segno e scrive DC_FT_MOVIMENTI. A fine elaborazione sblocca il flusso DC_SALDI.

## Struttura

**Uso:** `lancia_dc_movimenti.sh -i <ISTITUTO|ALL> [-d YYYYMMDD] [-f]`

**Parametri** (letti dal codice che interpreta la riga di comando):

| Opzione | Variabile | Valore | Definita in |
|---|---|---|---|
| `-i` | `ISTITUTO` | argomento successivo | [`script/demo_conti/dc_comune.sh`](../../script/demo_conti/dc_comune.sh) |
| `-d` | `DATA_RIF` | argomento successivo | [`script/demo_conti/dc_comune.sh`](../../script/demo_conti/dc_comune.sh) |
| `-f` | `FORZATO` | `S` | [`script/demo_conti/dc_comune.sh`](../../script/demo_conti/dc_comune.sh) |

**Variabili impostate:**

| Variabile | Valore | Commento |
|---|---|---|
| `FLUSSO` | `DC_MOVIMENTI` | — |
| `WORKFLOW` | `wf_DC_MOVIMENTI` | — |
| `FLUSSO_VALLE` | `DC_SALDI` | — |

**Funzioni definite:** `svuota_target`

## Cosa scrive

| Oggetto scritto | Contesto | Campi | Dove |
|---|---|---|---|
| [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) | STATEMENT | COD_ISTITUTO, DAT_CONTABILE | [`script/demo_conti/lancia_dc_movimenti.sh:22`](../../script/demo_conti/lancia_dc_movimenti.sh) |

## Cosa chiama

| Oggetto chiamato | Contesto | Campi | Dove |
|---|---|---|---|
| [`dc_comune.sh`](dc_comune.md) | STATEMENT | — | [`script/demo_conti/lancia_dc_movimenti.sh:17`](../../script/demo_conti/lancia_dc_movimenti.sh) |
| [`wf_DC_MOVIMENTI`](wf_DC_MOVIMENTI.md) | STATEMENT | — | [`script/demo_conti/lancia_dc_movimenti.sh:17`](../../script/demo_conti/lancia_dc_movimenti.sh) |

## Impatti indiretti

Oggetti raggiunti a catena, a valle dei riferimenti diretti:

| Livello | Oggetto | Ruolo | Raggiunto da |
|---|---|---|---|
| 2 | [`DC_VC_QUADRATURA`](DC_VC_QUADRATURA.md) | legge | [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) |
| 2 | [`DC_VC_VOLUMI_GIORNALIERI`](DC_VC_VOLUMI_GIORNALIERI.md) | legge | [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) |
| 2 | [`DI_VC_REGOLAMENTO_ORDINI`](DI_VC_REGOLAMENTO_ORDINI.md) | legge | [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) |
| 2 | [`wf_DC_SALDI`](wf_DC_SALDI.md) | legge | [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) |
| 3 | `APP_CONTROLLO_TITOLI` | consuma | [`DI_VC_REGOLAMENTO_ORDINI`](DI_VC_REGOLAMENTO_ORDINI.md) |
| 3 | `APP_REPORTING` | consuma | [`DC_VC_QUADRATURA`](DC_VC_QUADRATURA.md) |
| 3 | [`DC_FT_SALDI_MENSILI`](DC_FT_SALDI_MENSILI.md) | è scritto da | [`wf_DC_SALDI`](wf_DC_SALDI.md) |
| 3 | `UTENTI_CONTI` | consuma | [`DC_VC_QUADRATURA`](DC_VC_QUADRATURA.md) |
| 3 | [`lancia_dc_saldi.sh`](lancia_dc_saldi.md) | chiama | [`wf_DC_SALDI`](wf_DC_SALDI.md) |

Diagramma dei primi due livelli:

```mermaid
flowchart LR
  n0["lancia_dc_movimenti.sh"]
  n1["DC_FT_MOVIMENTI"]
  n2["DC_VC_QUADRATURA"]
  n3["DC_VC_VOLUMI_GIORNALIERI"]
  n4["DI_VC_REGOLAMENTO_ORDINI"]
  n5["wf_DC_SALDI"]
  n1 -->|letto da| n2
  n1 -->|letto da| n3
  n1 -->|letto da| n4
  n1 -->|letto da| n5
  n0 -->|scrive| n1
  class n0 centro
  classDef centro fill:#1f4e79,stroke:#1f4e79,color:#ffffff
```

## Note

Nota scritta a mano, da modificare nel repository: `script/demo_conti/lancia_dc_movimenti.md`

### Perché

Gira nello schedulatore Control-M come job `DC_MOV_GIORN` (folder `DEMO_CONTI`),
ogni giorno lavorativo, con `-i ALL`.

La shell cancella con una `DELETE` i movimenti del solo giorno e istituto in
lavorazione, e non con un `TRUNCATE`: la sottopartizione contiene tutto il mese
della banca, e svuotarla farebbe perdere i giorni già caricati. Il `TRUNCATE
SUBPARTITION FOR` si usa solo per rifare un mese intero (vedere la nota di
`DC_FT_MOVIMENTI`).

### Attenzione

- Con `-i ALL` gli istituti vengono elaborati uno alla volta: se uno fallisce,
  lo script si ferma e gli istituti successivi non vengono lanciati. Dopo la
  correzione si rilancia solo l'istituto in errore con `-i <ISTITUTO>`.
- Legge lo staging, che contiene un solo giorno per banca: il giorno da
  elaborare deve essere quello caricato per ultimo da `lancia_dc_carico_movimenti.sh`.
- Dopo un rilancio dei movimenti vanno rilanciati anche i saldi del mese, che
  li leggono.

### Comandi utili

```bash
# Rilancio manuale di un solo istituto, senza semaforo
./lancia_dc_movimenti.sh -i 99001 -d 20260929 -f

# Rilancio di tutti gli istituti per un giorno preciso
./lancia_dc_movimenti.sh -i ALL -d 20260929 -f
```

## Sorgente

[`script/demo_conti/lancia_dc_movimenti.sh`](../../script/demo_conti/lancia_dc_movimenti.sh)

## Limiti

L'analisi legge solo i file del repository. Non vede:

- **sinonimi** e **db link**: un oggetto letto tramite sinonimo o da un altro database non
  risulta collegato;
- **SQL dinamico**: le istruzioni costruite a runtime (`EXECUTE IMMEDIATE`, stringhe concatenate)
  sono segnalate come "da verificare", ma gli oggetti che toccano non sono noti;
- **oggetti non versionati**: tabelle, job o report che non stanno in questo repository
  (per esempio un cruscotto o un job di manutenzione dello schedulatore).

I risultati vanno sempre confermati con chi conosce il flusso.
