# Contesto per Claude — repository dimostrativo

## Regole di lavoro
- Rispondi in italiano.
- Quando scrivi codice, procedi un sorgente alla volta: un commit per sorgente, con messaggi chiari.

## Scopo del repository
Demo di documentazione tecnica di un data warehouse Oracle inventato, in Markdown, dentro Git,
accanto al codice.
1. Uno script legge il codice e genera la **scheda** di ogni oggetto, con l'analisi d'impatto.
2. Le persone scrivono solo quello che il codice non dice: le **note** accanto ai sorgenti e le
   **pagine per argomento** in `docs/`.
3. GitHub Pages (tema Just the Docs) pubblica schede e pagine come sito. Pages è già attivo.
4. Un assistente AI (AnythingLLM) indicizza gli stessi file e risponde alle domande.

## Regola non negoziabile
**Tutto è inventato.** Nessun nome reale di aziende, clienti, schemi, tabelle, workflow,
script o persone. Questo è il repository di lavoro (privato); il front pubblico viene ricreato
periodicamente da qui con un solo commit, quindi tutto ciò che entra qui deve poter diventare
pubblico.

## Struttura
- `sql/DEMO_DWH/<TIPO>/`: oggetti database per tipo (TABLES, VIEWS, PACKAGES, FUNCTIONS,
  PROCEDURES, SEQUENCES, CONSTRAINTS, DATA)
- `script/<area>/`: shell di orchestrazione
- `powercenter/<AREA>/`: export XML dei workflow ETL (finti e semplificati)
- `docs/`: pagine per argomento (motore, categorie, glossario, come documentare) e template
  in `docs/_templates/`
- `docs/oggetti/`: **schede generate**, da non modificare a mano
- `tools/impact_analysis/`: analisi d'impatto e generatore delle schede (Python 3, solo
  libreria standard), con i test in `tests/`
- `.github/workflows/`: rigenerazione delle schede (`schede.yml`) e protezione dalle modifiche
  a mano (`protezione_schede.yml`)
- Motore inventato: **DEMO_CONTI**, "dai movimenti all'estratto conto" (carico giornaliero →
  movimenti → saldi mensili, con semaforo, log delle elaborazioni e viste di controllo). Prefisso
  degli oggetti: `DC_`. Dominio volutamente semplice: chiunque lavori in banca deve capire ogni
  oggetto senza spiegazioni, quindi niente concetti specialistici.
- Secondo motore inventato: **DEMO_INVESTIMENTI**, "dal dossier titoli al controvalore" (carico
  giornaliero di ordini e prezzi → posizioni giornaliere → controvalori mensili). Prefisso `DI_`.
  Più piccolo di DEMO_CONTI: **non ha semaforo, log e package propri**, usa `DC_CTL_SEMAFORO`,
  `DC_LOG_ELABORAZIONI`, `DC_PKG_ELABORAZIONE`, `DC_FN_SEMAFORO` e la libreria `dc_comune.sh`
  (le sue shell la includono da `script/demo_conti/`). È l'esempio di oggetto condiviso tra due
  motori: chi tocca quegli oggetti tocca entrambi. Un secondo punto di contatto: la vista
  `DI_VC_REGOLAMENTO_ORDINI` legge `DC_FT_MOVIMENTI`, quindi cambiare i movimenti impatta anche gli
  investimenti.

## Modello a due livelli
- **Scheda di oggetto** (`docs/oggetti/<OGGETTO>.md`): la scrive solo lo script
  (`python tools/impact_analysis/impact_analysis.py --tutto`). Non si tocca mai a mano.
- **Nota di oggetto**: il `.md` accanto al sorgente, con lo stesso nome. La scrive solo una
  persona, è facoltativa e contiene solo il perché delle scelte, le avvertenze e le query utili.
  Niente front matter, niente link (gli oggetti si citano per nome), titoli `###`.
  Lo script la copia nella scheda così com'è, senza modificarla.
- **Pagine per argomento** (`docs/`): le scrivono le persone e rimandano alle schede.
- Nel commit si aggiorna la nota solo se il perché cambia. Se il sorgente ha un commit più
  recente della nota, la scheda mostra "Codice modificato dopo l'ultima nota: verificare".
- Dopo una modifica al codice si possono rigenerare le schede in locale; altrimenti le
  rigenera la Action su `main`. Prima di un commit: `python -m unittest`.

## Convenzioni della documentazione
- Front matter Just the Docs nelle pagine del sito. Il menu di un motore ha tre livelli:
  1. pagina del motore (`docs/<MOTORE>.md`): `title: <MOTORE>`, `has_children: true`;
  2. pagine di categoria (`docs/<MOTORE>/*.md`): `Tabelle`, `Viste di controllo`,
     `Package e funzioni`, `Shell e Workflow`, con `parent: <MOTORE>`,
     `has_children: true` e una frase introduttiva (l'elenco lo genera il tema);
  3. schede di oggetto (generate): `parent: <categoria>`, `grand_parent: <MOTORE>`,
     `nav_order` alfabetico.
- La home è `README.md` con `permalink: /`. Le note sono escluse dal sito (`_config.yml`):
  compaiono dentro le schede.
- Template in `docs/_templates/`: `README_area.md` (pagina del motore), `README_categoria.md`,
  `nota_tabella.md`, `nota_shell.md`, `nota_workflow.md`.
- Tutti i link sono relativi, anche quelli ai sorgenti (`.sql`, `.sh`, `.xml`): nessun
  URL assoluto verso il repository. Le pagine per argomento puntano alle schede in
  `docs/oggetti/`.
- Codici istituto solo fittizi `99xxx`.
- Colori del sito: schema `dwh` (`_sass/color_schemes/dwh.scss`), primario blu
  `#1F4E79`, accento ambra `#E0A100` usato solo per bordi ed evidenziazioni
  (palette in `_sass/custom/setup.scss`). Diagrammi Mermaid abilitati.
- Indicizzazione con AnythingLLM: pagine di `docs/` (schede comprese, che contengono già le
  note) > DDL e shell > XML. `DATA/` è esclusa.

## Configurazione dell'analisi d'impatto
`tools/impact_analysis/impact_analysis.cfg.py`, stesso formato dello strumento originale
(`patterns` con `table_name`, `field_name`, `words`; `IGNORE_PATH_PATTERNS`), più `AREE` per il
motore di appartenenza. Il file non viene eseguito: lo legge `ast.literal_eval`.

## Stato
Motori DEMO_CONTI (sostituisce DEMO_RISCHIO) e DEMO_INVESTIMENTI completi, note nel modello a due
livelli, Action di rigenerazione e di protezione attive. Le schede in `docs/oggetti/` restano quelle del
vecchio motore finché la Action non le rigenera dopo il merge: non vanno rigenerate né
committate a mano.

## Prossimi passi
1. **AnythingLLM**: indicizzare il repository come sopra e verificare che le risposte citino
   le schede giuste, compresa l'analisi d'impatto.
2. **Front pubblico**: ricrearlo da questo repository con un solo commit quando serve; le
   schede vanno copiate così come sono (lì non vengono rigenerate).
