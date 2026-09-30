# Configurazione dell'analisi d'impatto.
#
# Formato compatibile con lo strumento originale: una lista `patterns`, dove
# ogni pattern ha
#   - table_name: regex della tabella (obbligatoria)
#   - field_name: regex del campo, oppure None
#   - words:      altre regex, tutte obbligatorie
#
# Il file NON viene eseguito: config.py lo legge con ast.literal_eval, quindi
# sono ammessi solo valori letterali (stringhe, liste, dizionari, None).

patterns=[
  # Campo di una tabella dei fatti: chi lo scrive, chi lo legge, cosa impatta a valle
  { "words": [], "table_name": "\\bDC_FT_MOVIMENTI\\b", "field_name": "\\bIMP_MOVIMENTO\\b" },
  # Tabella intera, senza campo
  { "words": [], "table_name": "\\bDC_STG_MOVIMENTI\\b", "field_name": None },
  # Caso del falso positivo: DAT_RIFERIMENTO esiste anche in DC_CTL_SEMAFORO
  { "words": [], "table_name": "\\bDC_LOG_ELABORAZIONI\\b", "field_name": "\\bDAT_RIFERIMENTO\\b" },
  # Campo letto dalla lookup (con Lookup Sql Override) del workflow dei movimenti
  { "words": [], "table_name": "\\bDC_DIM_CAUSALE\\b", "field_name": "\\bCOD_SEGNO\\b" },
  # DEMO_INVESTIMENTI: campo dei fatti, tabella intera e campo letto dalla lookup
  { "words": [], "table_name": "\\bDI_FT_POSIZIONI\\b", "field_name": "\\bQTA_FINALE\\b" },
  { "words": [], "table_name": "\\bDI_STG_ORDINI\\b", "field_name": None },
  { "words": [], "table_name": "\\bDI_DIM_TITOLO\\b", "field_name": "\\bCOD_TIPO\\b" },
  # Oggetto condiviso: il package di elaborazione è di DEMO_CONTI ma lo usano anche le shell di DEMO_INVESTIMENTI
  { "words": [], "table_name": "\\bDC_PKG_ELABORAZIONE\\b", "field_name": None },
]

# Percorsi da ignorare (regex sul percorso del file)
IGNORE_PATH_PATTERNS=[r"_old[\\/]", r"[\\/]docs[\\/]"]

# Estensione della v2, ignorata dallo strumento originale.
# Motore di appartenenza degli oggetti, per il menu delle schede:
# regex cercate nel nome dell'oggetto e nel percorso del sorgente.
AREE={
  "DEMO_CONTI": [r"^DC_", r"^wf_DC_", r"demo_conti", r"DEMO_CONTI"],
  "DEMO_INVESTIMENTI": [r"^DI_", r"^wf_DI_", r"demo_investimenti", r"DEMO_INVESTIMENTI"],
}
