# Analisi d'impatto e schede di oggetto

Strumento che legge il codice del data warehouse (`sql/`, `script/`, `powercenter/`) e risponde
a due domande:

1. **Se cambio questo oggetto (o questo campo), cosa devo controllare?** Chi lo scrive, chi lo
   legge, chi lo consuma e cosa viene impattato a catena, livello per livello.
2. **Com'è fatto questo oggetto?** Per ogni tabella, vista, package, funzione, procedura, shell
   e workflow genera una **scheda** in `docs/oggetti/`, pubblicata sul sito.

Analizza solo i file: non si collega al database. Usa solo la libreria standard di Python 3.

## Come si lancia

Dalla radice del repository:

```bash
python tools/impact_analysis/impact_analysis.py                  # configurazione di default, output a video
python tools/impact_analysis/impact_analysis.py mio.cfg.py       # configurazione alternativa (come l'originale)
python tools/impact_analysis/impact_analysis.py --compatibile    # stesso formato dell'originale + confronto
python tools/impact_analysis/impact_analysis.py --tutto          # rigenera tutte le schede in docs/oggetti/
python -m unittest                                               # test
```

- **Output di default:** per ogni pattern, gli oggetti che corrispondono a `table_name` e i loro
  impatti per livello. Al livello 1 ci sono file, riga, contesto (`SOURCE`, `TARGET`, `LOOKUP`,
  `SQL_OVERRIDE`, `PRE_SQL`, `POST_SQL`, `STATEMENT`) e campi usati.
- **`--compatibile`:** riproduce il formato dello strumento originale: data e ora,
  `####PATTERN {...}`, un file per riga, `grants[...]` per le viste, riga di chiusura. In fondo
  riporta quanti file l'approccio originale segnala in più (`+`) o in meno (`-`) rispetto ai
  riferimenti diretti della v2.
- **`--tutto`:** cancella e ricrea **solo** `docs/oggetti/`. L'output è deterministico: data e
  hash nel banner sono quelli dell'ultimo commit che ha toccato il codice, quindi due esecuzioni
  sullo stesso codice producono file identici.

## Configurazione

Il file `impact_analysis.cfg.py` ha lo stesso formato dello strumento originale:

```python
patterns=[
  { "words": [], "table_name": "\\bDC_FT_MOVIMENTI\\b", "field_name": "\\bIMP_MOVIMENTO\\b" },
  { "words": [], "table_name": "\\bDC_STG_MOVIMENTI\\b", "field_name": None },
]
IGNORE_PATH_PATTERNS=[r"_old[\\/]", r"[\\/]docs[\\/]"]
```

| Chiave | Significato |
|---|---|
| `table_name` | Regex dell'oggetto (obbligatoria) |
| `field_name` | Regex del campo, oppure `None` |
| `words` | Altre regex, tutte obbligatorie. Nella v2 devono comparire nello **stesso statement** del riferimento, non in un punto qualsiasi del file |
| `IGNORE_PATH_PATTERNS` | Regex dei percorsi da ignorare (confrontate con `/percorso/relativo`) |
| `AREE` | *Solo v2, facoltativa.* Motore di appartenenza degli oggetti, per il menu delle schede: `{"MOTORE": [regex su nome o percorso]}` |

Il file **non viene eseguito**: `config.py` lo analizza con `ast` e valuta con
`ast.literal_eval` solo le assegnazioni `patterns`, `IGNORE_PATH_PATTERNS` e `AREE`. Sono ammessi
solo valori letterali; i file dell'originale restano compatibili.

## Come funziona

| Modulo | Compito |
|---|---|
| `config.py` | Legge la configurazione senza eseguirla |
| `scanner.py` | Legge **una volta sola** tutti i file e costruisce il catalogo degli oggetti e l'indice dei riferimenti |
| `grafo.py` | Grafo nel verso del flusso (chi scrive → oggetto → chi legge, più chiamate e consumi) e funzione `impatti(oggetto, campo)` |
| `compat.py` | Logica e formato dello strumento originale, per il confronto |
| `genera_schede.py` | Schede di oggetto e indice in `docs/oggetti/` |
| `impact_analysis.py` | Riga di comando |

Ogni riferimento ha: file, tipo di file, oggetto chiamante, oggetto riferito, direzione
(`LETTURA`, `SCRITTURA`, `CHIAMATA`, `CONSUMO`, `DA_VERIFICARE`), campi citati nello stesso
contesto, contesto e riga.

Regole principali:

- **XML PowerCenter:** `SOURCE` → lettura, `TARGET` → scrittura, lookup (`Lookup table name`,
  `Lookup Sql Override`) → lettura; `Sql Query`, `Pre SQL` e `Post SQL` analizzate come SQL. Il
  chiamante è il workflow.
- **SQL:** tolti commenti e stringhe, analisi statement per statement. `INSERT INTO`, `UPDATE`,
  `MERGE INTO`, `DELETE`, `TRUNCATE`, `ALTER TABLE … TRUNCATE (SUB)PARTITION` → scrittura; le
  altre citazioni di tabelle e viste → lettura; package, funzioni e procedure → chiamata;
  `GRANT … TO X` su una vista → consumo da parte di X. Gli alias di CTE sono ignorati.
- **Shell:** librerie incluse (`.` / `source`), workflow lanciati con `pmcmd startworkflow`
  (risolvendo le variabili della shell che include la libreria; se la shell definisce
  `WORKFLOWS="wf_A wf_B"` i workflow sono tutti quelli dell'elenco), package e funzioni chiamati
  via `sqlplus`, `TRUNCATE` inline. Una libreria può essere inclusa da shell di motori diversi:
  gli impatti del suo package e delle sue tabelle attraversano entrambi i motori.
- **SQL dinamico** (`EXECUTE IMMEDIATE`, `DBMS_SQL`, nomi di tabella in variabile nelle shell):
  nessuna ipotesi, il file viene segnalato come `DA_VERIFICARE`.

## Differenze rispetto all'approccio originale

| # | Limite dell'originale | Come lo supera la v2 |
|---|---|---|
| 1 | Non distingue lettura e scrittura | Ogni riferimento ha una direzione: lettura, scrittura, chiamata, consumo |
| 2 | A livello di campo ignora `TARGET`, lookup e SQL pre/post sessione | Analizza source, target, lookup, `Sql Query`, `Pre SQL` e `Post SQL` |
| 3 | L'AND delle regex su tutto il file genera falsi positivi | I campi valgono solo nello statement del riferimento; commenti e stringhe non contano |
| 4 | Si ferma al primo livello | `impatti()` segue la catena a valle, livello per livello, protetto dai cicli |
| 5 | Il risultato non resta come documentazione | `--tutto` genera le schede pubblicate sul sito, aggiornate dalla Action |
| 6 | Esegue il file di configurazione come codice | Lo legge con `ast.literal_eval`: nessun codice eseguito |
| 7 | Rilegge tutti i file per ogni pattern | Legge i file una volta e interroga l'indice |

Con `--compatibile` le differenze si vedono sul repository stesso: per esempio sul pattern
`DC_LOG_ELABORAZIONI` / `DAT_RIFERIMENTO` l'originale segnala anche `DC_PRC_PULIZIA_STORICO`, che
usa `DAT_RIFERIMENTO` solo sul semaforo.

## Limiti

- **Sinonimi e db link:** un oggetto letto tramite sinonimo o da un altro database non risulta
  collegato.
- **SQL dinamico:** segnalato, non risolto.
- **Oggetti non versionati:** ciò che non sta nel repository (report, job dello schedulatore,
  altri sistemi) non compare. Gli oggetti citati dopo `FROM`, `JOIN`, `INTO` ma non definiti qui
  sono elencati nell'indice come "citati ma non definiti".
- **Campi per statement:** se uno statement legge due tabelle con una colonna dallo stesso nome,
  il campo viene attribuito a entrambe.
- **Workflow semplificati:** gli XML sono letti per elementi (`SOURCE`, `TARGET`,
  `TRANSFORMATION`, attributi di sessione), non per collegamenti tra porte.

Le schede riportano sempre questi limiti: i risultati vanno confermati con chi conosce il flusso.
