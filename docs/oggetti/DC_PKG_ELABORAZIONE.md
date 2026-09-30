---
title: DC_PKG_ELABORAZIONE
parent: Package e funzioni
grand_parent: DEMO_CONTI
nav_order: 2
---

# Package: `DEMO_DWH.DC_PKG_ELABORAZIONE`

> ⚙️ **Scheda generata automaticamente, non modificare a mano.** Commit analizzato `c276f3f` del 2026-09-30. Le spiegazioni scritte a mano vanno nella nota accanto al sorgente.

## Descrizione

**Tipo:** Package

Gestione delle elaborazioni del motore, chiamata dalle shell di lancio: - APRI         apre una riga 'running' in DC_LOG_ELABORAZIONI - CHIUDI       la chiude in 'succeeded' o 'failed' - SEGNA_PRONTO sblocca il flusso a valle in DC_CTL_SEMAFORO

## Struttura

Procedure e funzioni pubbliche (dalla specifica del package):

| Nome | Tipo | Parametri | Restituisce | Descrizione |
|---|---|---|---|---|
| `APRI` | function | `p_cod_flusso` IN VARCHAR2; `p_cod_istituto` IN VARCHAR2; `p_dat_riferimento` IN DATE; `p_flg_forza` IN CHAR DEFAULT | NUMBER | Apre un'elaborazione e ne restituisce l'identificativo |
| `CHIUDI` | procedure | `p_id_elaborazione` IN NUMBER; `p_cod_stato` IN VARCHAR2; `p_des_errore` IN VARCHAR2 DEFAULT NULL | — | Chiude un'elaborazione: p_cod_stato = 'succeeded' oppure 'failed' |
| `SEGNA_PRONTO` | procedure | `p_cod_flusso` IN VARCHAR2; `p_cod_fonte` IN VARCHAR2; `p_cod_istituto` IN VARCHAR2; `p_dat_riferimento` IN DATE | — | Segna come pronta la fonte p_cod_fonte per il flusso p_cod_flusso |

## Chi lo chiama

| Chiamante | Contesto | Campi | Dove |
|---|---|---|---|
| [`dc_comune.sh`](dc_comune.md) | STATEMENT | — | [`script/demo_conti/dc_comune.sh:96`](../../script/demo_conti/dc_comune.sh) |

## Cosa scrive

| Oggetto scritto | Contesto | Campi | Dove |
|---|---|---|---|
| [`DC_CTL_SEMAFORO`](DC_CTL_SEMAFORO.md) | STATEMENT | COD_FLUSSO, COD_FONTE, COD_ISTITUTO, COD_UTENTE_AGG, DAT_AGGIORNAMENTO, DAT_RIFERIMENTO, FLG_PRONTO | [`sql/DEMO_DWH/PACKAGES/DC_PKG_ELABORAZIONE.sql:104`](../../sql/DEMO_DWH/PACKAGES/DC_PKG_ELABORAZIONE.sql) |
| [`DC_LOG_ELABORAZIONI`](DC_LOG_ELABORAZIONI.md) | STATEMENT | COD_FLUSSO, COD_ISTITUTO, COD_STATO, COD_UTENTE_OS, DAT_FINE, DAT_INIZIO, DAT_RIFERIMENTO, DES_ERRORE, FLG_FORZA, ID_ELABORAZIONE | [`sql/DEMO_DWH/PACKAGES/DC_PKG_ELABORAZIONE.sql:59`](../../sql/DEMO_DWH/PACKAGES/DC_PKG_ELABORAZIONE.sql) |

## Cosa legge

| Oggetto letto | Contesto | Campi | Dove |
|---|---|---|---|
| `DC_SEQ_ELABORAZIONE` | STATEMENT | — | [`sql/DEMO_DWH/PACKAGES/DC_PKG_ELABORAZIONE.sql:57`](../../sql/DEMO_DWH/PACKAGES/DC_PKG_ELABORAZIONE.sql) |

## Impatti indiretti

Oggetti raggiunti a catena, a valle dei riferimenti diretti:

| Livello | Oggetto | Ruolo | Raggiunto da |
|---|---|---|---|
| 2 | [`DC_FN_SEMAFORO`](DC_FN_SEMAFORO.md) | legge | [`DC_CTL_SEMAFORO`](DC_CTL_SEMAFORO.md) |
| 2 | [`lancia_dc_carico_movimenti.sh`](lancia_dc_carico_movimenti.md) | chiama | [`dc_comune.sh`](dc_comune.md) |
| 2 | [`lancia_dc_movimenti.sh`](lancia_dc_movimenti.md) | chiama | [`dc_comune.sh`](dc_comune.md) |
| 2 | [`lancia_dc_saldi.sh`](lancia_dc_saldi.md) | chiama | [`dc_comune.sh`](dc_comune.md) |
| 2 | [`lancia_di_carico.sh`](lancia_di_carico.md) | chiama | [`dc_comune.sh`](dc_comune.md) |
| 2 | [`lancia_di_posizioni.sh`](lancia_di_posizioni.md) | chiama | [`dc_comune.sh`](dc_comune.md) |
| 3 | [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) | è scritto da | [`lancia_dc_movimenti.sh`](lancia_dc_movimenti.md) |
| 3 | [`DC_FT_SALDI_MENSILI`](DC_FT_SALDI_MENSILI.md) | è scritto da | [`lancia_dc_saldi.sh`](lancia_dc_saldi.md) |
| 3 | [`DC_STG_MOVIMENTI`](DC_STG_MOVIMENTI.md) | è scritto da | [`lancia_dc_carico_movimenti.sh`](lancia_dc_carico_movimenti.md) |
| 3 | [`DI_FT_CONTROVALORI_MENSILI`](DI_FT_CONTROVALORI_MENSILI.md) | è scritto da | [`lancia_di_posizioni.sh`](lancia_di_posizioni.md) |
| 3 | [`DI_FT_POSIZIONI`](DI_FT_POSIZIONI.md) | è scritto da | [`lancia_di_posizioni.sh`](lancia_di_posizioni.md) |
| 3 | [`DI_STG_ORDINI`](DI_STG_ORDINI.md) | è scritto da | [`lancia_di_carico.sh`](lancia_di_carico.md) |
| 3 | [`DI_STG_PREZZI`](DI_STG_PREZZI.md) | è scritto da | [`lancia_di_carico.sh`](lancia_di_carico.md) |
| 4 | [`DC_VC_QUADRATURA`](DC_VC_QUADRATURA.md) | legge | [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) |
| 4 | [`DC_VC_VOLUMI_GIORNALIERI`](DC_VC_VOLUMI_GIORNALIERI.md) | legge | [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) |
| 4 | [`DI_VC_QUADRATURA`](DI_VC_QUADRATURA.md) | legge | [`DI_FT_POSIZIONI`](DI_FT_POSIZIONI.md) |
| 4 | [`DI_VC_REGOLAMENTO_ORDINI`](DI_VC_REGOLAMENTO_ORDINI.md) | legge | [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) |
| 4 | [`wf_DC_MOVIMENTI`](wf_DC_MOVIMENTI.md) | legge | [`DC_STG_MOVIMENTI`](DC_STG_MOVIMENTI.md) |
| 4 | [`wf_DC_SALDI`](wf_DC_SALDI.md) | legge | [`DC_FT_MOVIMENTI`](DC_FT_MOVIMENTI.md) |
| 4 | [`wf_DI_POSIZIONI`](wf_DI_POSIZIONI.md) | legge | [`DI_FT_POSIZIONI`](DI_FT_POSIZIONI.md) |
| 5 | `APP_CONTROLLO_TITOLI` | consuma | [`DI_VC_REGOLAMENTO_ORDINI`](DI_VC_REGOLAMENTO_ORDINI.md) |
| 5 | `APP_REPORTING` | consuma | [`DC_VC_QUADRATURA`](DC_VC_QUADRATURA.md) |
| 5 | `UTENTI_CONTI` | consuma | [`DC_VC_QUADRATURA`](DC_VC_QUADRATURA.md) |
| 5 | `UTENTI_INVESTIMENTI` | consuma | [`DI_VC_QUADRATURA`](DI_VC_QUADRATURA.md) |

Diagramma dei primi due livelli:

```mermaid
flowchart LR
  n0["DC_PKG_ELABORAZIONE"]
  n1["DC_CTL_SEMAFORO"]
  n2["DC_FN_SEMAFORO"]
  n3["DC_LOG_ELABORAZIONI"]
  n4["dc_comune.sh"]
  n5["lancia_dc_carico_movimenti.sh"]
  n6["lancia_dc_movimenti.sh"]
  n7["lancia_dc_saldi.sh"]
  n8["lancia_di_carico.sh"]
  n9["lancia_di_posizioni.sh"]
  n1 -->|letto da| n2
  n0 -->|scrive| n1
  n0 -->|scrive| n3
  n4 -.->|chiama| n2
  n4 -.->|chiama| n0
  n5 -.->|chiama| n4
  n6 -.->|chiama| n4
  n7 -.->|chiama| n4
  n8 -.->|chiama| n4
  n9 -.->|chiama| n4
  class n0 centro
  classDef centro fill:#1f4e79,stroke:#1f4e79,color:#ffffff
```

## Note

Nota scritta a mano, da modificare nel repository: `sql/DEMO_DWH/PACKAGES/DC_PKG_ELABORAZIONE.md`

### Perché

Raccoglie in un solo punto la scrittura del log delle elaborazioni e
l'aggiornamento del semaforo, così le shell non contengono DML.

Ogni procedura fa `COMMIT` da sola: il log resta scritto anche se il workflow
lanciato subito dopo fallisce.

### Query utili

Sblocco manuale dei movimenti per l'istituto 99001 e il giorno 29/09/2026:

```sql
EXEC DEMO_DWH.DC_PKG_ELABORAZIONE.SEGNA_PRONTO('DC_MOVIMENTI', 'DC_CARICO', '99001', DATE '2026-09-29');
```

## Sorgente

[`sql/DEMO_DWH/PACKAGES/DC_PKG_ELABORAZIONE.sql`](../../sql/DEMO_DWH/PACKAGES/DC_PKG_ELABORAZIONE.sql)

## Limiti

L'analisi legge solo i file del repository. Non vede:

- **sinonimi** e **db link**: un oggetto letto tramite sinonimo o da un altro database non
  risulta collegato;
- **SQL dinamico**: le istruzioni costruite a runtime (`EXECUTE IMMEDIATE`, stringhe concatenate)
  sono segnalate come "da verificare", ma gli oggetti che toccano non sono noti;
- **oggetti non versionati**: tabelle, job o report che non stanno in questo repository
  (per esempio un cruscotto o un job di manutenzione dello schedulatore).

I risultati vanno sempre confermati con chi conosce il flusso.
