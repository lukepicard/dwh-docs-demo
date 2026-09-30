"""Lettura della configurazione dell'analisi d'impatto.

Il file di configurazione (.cfg.py) ha lo stesso formato dello strumento
originale, ma qui NON viene eseguito: lo si analizza con `ast` e si valutano
solo le assegnazioni note con `ast.literal_eval`. Così un file di
configurazione non può eseguire codice arbitrario.
"""

import ast
import re
from pathlib import Path

CONFIG_DEFAULT = Path(__file__).with_name("impact_analysis.cfg.py")

# Assegnazioni lette dal file; le altre vengono ignorate.
CHIAVI = ("patterns", "IGNORE_PATH_PATTERNS", "AREE")


class ConfigError(Exception):
    """Configurazione non valida."""


def _leggi_assegnazioni(testo, nome_file):
    try:
        albero = ast.parse(testo, filename=nome_file)
    except SyntaxError as e:
        raise ConfigError(f"{nome_file}: sintassi non valida alla riga {e.lineno}") from e

    valori = {}
    for nodo in albero.body:
        if not isinstance(nodo, ast.Assign):
            continue
        for bersaglio in nodo.targets:
            if isinstance(bersaglio, ast.Name) and bersaglio.id in CHIAVI:
                try:
                    valori[bersaglio.id] = ast.literal_eval(nodo.value)
                except ValueError as e:
                    raise ConfigError(
                        f"{nome_file}, riga {nodo.lineno}: '{bersaglio.id}' deve contenere "
                        "solo valori letterali (stringhe, liste, dizionari, None)"
                    ) from e
    return valori


def _valida_pattern(p, i):
    if not isinstance(p, dict):
        raise ConfigError(f"pattern {i}: deve essere un dizionario")
    if not p.get("table_name"):
        raise ConfigError(f"pattern {i}: manca 'table_name'")
    pattern = {
        "table_name": p["table_name"],
        "field_name": p.get("field_name") or None,
        "words": list(p.get("words") or []),
    }
    for regex in [pattern["table_name"], pattern["field_name"], *pattern["words"]]:
        if regex is None:
            continue
        try:
            re.compile(regex)
        except re.error as e:
            raise ConfigError(f"pattern {i}: regex non valida {regex!r}: {e}") from e
    return pattern


def carica(percorso=None):
    """Legge il file di configurazione e restituisce un dizionario con
    `patterns`, `ignore` (IGNORE_PATH_PATTERNS) e `aree`."""
    percorso = Path(percorso) if percorso else CONFIG_DEFAULT
    if not percorso.exists():
        raise ConfigError(f"file di configurazione non trovato: {percorso}")
    valori = _leggi_assegnazioni(percorso.read_text(encoding="utf-8"), str(percorso))

    patterns = valori.get("patterns", [])
    if not isinstance(patterns, list):
        raise ConfigError("'patterns' deve essere una lista")

    ignore = valori.get("IGNORE_PATH_PATTERNS", [])
    aree = valori.get("AREE", {})
    if not isinstance(ignore, list) or not isinstance(aree, dict):
        raise ConfigError("'IGNORE_PATH_PATTERNS' deve essere una lista e 'AREE' un dizionario")

    return {
        "percorso": str(percorso),
        "patterns": [_valida_pattern(p, i) for i, p in enumerate(patterns, 1)],
        "ignore": [re.compile(r) for r in ignore],
        "aree": {motore: [re.compile(r) for r in regole] for motore, regole in aree.items()},
    }
