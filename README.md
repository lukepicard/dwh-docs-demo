---
title: Home
nav_order: 1
permalink: /
---

# Documentazione DWH — repository dimostrativo

> ⚠️ **Repository dimostrativo.** Tutti i nomi di schemi, tabelle, workflow e script
> sono **inventati**. Nessun contenuto proviene da sistemi reali.

Questo repository mostra come potrebbe essere organizzata la documentazione di un
data warehouse quando **codice e documentazione vivono insieme**:

1. il codice (SQL, shell, export ETL) sta in Git;
2. uno script legge il codice e genera la **scheda** di ogni oggetto, con l'analisi d'impatto;
3. le persone scrivono solo quello che il codice non dice: **note** accanto ai sorgenti e
   **pagine per argomento**;
4. GitHub Pages trasforma schede e pagine in un **sito consultabile**;
5. un **assistente AI** (AnythingLLM) indicizza gli stessi file e risponde alle domande.

## Struttura

| Cartella | Contenuto |
|---|---|
| `docs/` | Pagine per argomento: motori, glossario, come documentare |
| `docs/oggetti/` | Schede di oggetto, generate dallo script |
| `powercenter/` | Export dei workflow ETL, una cartella per area |
| `script/` | Script shell di orchestrazione |
| `sql/DEMO_DWH/` | Oggetti database per tipo (TABLES, VIEWS, PACKAGES, …) |
| `tools/impact_analysis/` | Analisi d'impatto e generatore delle schede |

## I motori di esempio

Il repository documenta due motori inventati, con le stesse categorie di oggetti:

- **DEMO_CONTI**, dai movimenti all'estratto conto: ogni giorno carica i movimenti, ogni mese
  calcola saldo iniziale, entrate, uscite e saldo finale di ogni conto. Vedi la
  [pagina del motore](docs/DEMO_CONTI.md).
- **DEMO_INVESTIMENTI**, dal dossier titoli al controvalore: ogni giorno carica ordini e prezzi
  e calcola le posizioni, a fine mese il controvalore dei dossier. Vedi la
  [pagina del motore](docs/DEMO_INVESTIMENTI.md). Usa semaforo, log e package di DEMO_CONTI:
  un esempio di oggetto condiviso tra due motori.

Vedi anche il [glossario](docs/glossario.md).

## Due livelli di documentazione

- **Scheda di oggetto** — la scrive solo lo script, dal codice: struttura, chi scrive, chi legge,
  chi consuma, impatti a catena. Vedi le [schede di oggetto](docs/oggetti/index.md).
- **Nota di oggetto e pagine per argomento** — le scrivono le persone: il perché delle scelte, le
  avvertenze, i processi dall'inizio alla fine. Vedi [come documentare](docs/come_documentare.md).
