---
title: [NOME_MOTORE]
nav_order: [N]
has_children: true
---

# \[NOME\_AREA] — \[DESCRIZIONE BREVE]

> \*\*Schema target principale:\*\* `SCHEMA.NOME`
>
> \*\*Referente tecnico:\*\* \[Nome]
>
> \*\*Ultima verifica:\*\* \[YYYY-MM]

\---

## Panoramica

\[2-3 righe che descrivono cosa fa questa area, a quale motore appartiene, e che tipo di dati gestisce.]

\---

## Flussi presenti

|Cartella / File|Tipo|Frequenza|Schema target|
|-|-|-|-|
|`NOME\_WORKFLOW`|PowerCenter|Mensile|`SCHEMA.TABELLA`|
|`nome\_script.sh`|Shell|Mensile|—|

\---

## Dipendenze upstream

* **Sorgenti:** \[elenco sorgenti da `DEMO\_DWH.DC\_CTL\_SEMAFORO`]
* **Dipendenze da altri flussi:** \[es. "gira dopo il carico delle anagrafiche"]

\---

## Scheduling Control-M

* **Folder:** `\[NOME\_MOTORE]`
* **Finestra esecuzione:** \[es. "T+5 lavorativo, ore 08:00–18:00"]
* **Alert assenza dati:** \[es. "17:30 se semaforo ancora KO"]

\---

## Note operative

* \[Nota 1 — es. rilancio di una banca: shell con `-i <ISTITUTO> -d <YYYYMMDD> -f`]
* \[Nota 2]

\---

## Riferimenti

* Documento di progetto: \[link o nome documento]
* Procedure operative: \[sezione]

