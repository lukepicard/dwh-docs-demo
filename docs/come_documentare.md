---
title: Come documentare
nav_order: 5
---

# Come documentare

La documentazione del data warehouse sta nel repository, accanto al codice, ed è divisa tra ciò
che scrive uno script e ciò che scrivono le persone. **Ognuno scrive solo nei propri file.**

| Cosa | Chi lo scrive | Dove |
|---|---|---|
| **Scheda di oggetto** | Solo lo script | `docs/oggetti/<OGGETTO>.md` |
| **Nota di oggetto** (facoltativa) | Solo una persona | Il file `.md` accanto al sorgente, con lo stesso nome |
| **Pagine per argomento** | Le persone | `docs/`: motori, categorie, glossario, procedure |

---

## Cosa genera lo script

Lo script `tools/impact_analysis/impact_analysis.py --tutto` legge il codice e scrive una scheda
per ogni tabella, vista, package, funzione, procedura, shell e workflow:

- descrizione, dall'intestazione del sorgente o dal `COMMENT ON TABLE`;
- struttura: colonne con tipi e commenti, partizionamento, chiavi e vincoli; procedure pubbliche;
  parametri delle shell; sessioni, source e target dei workflow;
- chi scrive, chi legge (con contesto e campi usati), chi consuma (`GRANT`), chi chiama;
- impatti indiretti per livello, con un diagramma dei primi due livelli;
- istruzioni di SQL dinamico da verificare;
- la nota scritta a mano, copiata così com'è;
- il link al sorgente e i limiti dell'analisi.

Le schede si rigenerano da sole a ogni modifica del codice su `main` e ogni notte. **Non si
modificano a mano**: un controllo automatico blocca i commit che le ritoccano, con il messaggio
"Le schede sono generate: modifica la nota accanto al sorgente".

---

## Cosa scrive la persona

### La nota di oggetto

È facoltativa e contiene **solo quello che il codice non dice**:

- il **perché** delle scelte (perché si partiziona così, perché gli storni non si cancellano);
- le **avvertenze** operative (cosa non fare, cosa rilanciare dopo, chi avvisare);
- le **query utili** per l'assistenza.

Non si ripetono struttura, sorgenti o destinazioni: li scrive la scheda. Se un oggetto non ha
niente da spiegare oltre al codice, la nota non serve.

Regole di forma:

- nessun front matter: la nota non è una pagina del sito, compare dentro la scheda;
- titoli di sezione di livello `###` (per esempio `### Perché`, `### Attenzione`,
  `### Query utili`), così nella scheda restano sotto "Note";
- gli altri oggetti si citano per nome (`DC_FT_MOVIMENTI`), **senza link**: la nota viene
  copiata in un'altra cartella e i link relativi si romperebbero. I collegamenti li mette la
  scheda.

I modelli sono in `docs/_templates/` (`nota_tabella.md`, `nota_shell.md`, `nota_workflow.md`).

### Le pagine per argomento

Raccontano un processo dall'inizio alla fine (il motore, la catena dei flussi, le procedure di
rilancio) e rimandano alle schede in `docs/oggetti/`. Per un nuovo motore si parte dai modelli
`README_area.md` e `README_categoria.md`.

---

## Quando aggiornare la nota

**Nel commit si aggiorna la nota solo se il perché cambia.**

Un campo aggiunto, una tabella letta in più, un nuovo consumatore: la scheda se ne accorge da
sola. La nota va toccata quando cambia una scelta o un'avvertenza: una regola di business, un
modo diverso di rilanciare, un vincolo nuovo.

---

## L'avviso "nota da verificare"

Se il sorgente di un oggetto ha un commit più recente della sua nota, la scheda mostra in cima
alle note:

> ⚠️ **Codice modificato dopo l'ultima nota: verificare.**

Non vuol dire che la nota sia sbagliata: chiede a chi conosce l'oggetto di rileggerla. Se è
ancora valida, basta un piccolo commit sulla nota (per esempio una frase precisata) e l'avviso
sparisce alla generazione successiva.

L'avviso si basa sulla storia Git. In un repository ricreato con un solo commit tutti i file
hanno la stessa data, quindi l'avviso non può comparire: lì le schede non vengono rigenerate e
restano quelle copiate dal repository di lavoro.
