"""Logica e formato dello strumento originale, per il confronto con la v2.

Regole dell'originale:
- workflow PowerCenter (XML) con tabella e campo indicati: il file è impattato
  se ha una SOURCE con quel nome e un campo che corrisponde; altrimenti, se una
  query di override (TABLEATTRIBUTE "Sql Query") contiene tutte le regex;
- tutti gli altri file: impattato se tutte le regex compaiono in un punto
  qualsiasi del file;
- per le viste (VIEWS/*.sql) si aggiungono gli schemi dei GRANT ... TO.

Usa i testi già letti dallo scanner: i file non vengono riletti.
"""

import re
import xml.etree.ElementTree as ET
from datetime import datetime

RE_GRANT_TO = re.compile(r"\bGRANT\b[^;]*?\bTO\s+([\w$#\s,]+?)\s*(?:WITH\s+GRANT\s+OPTION\s*)?;", re.I | re.S)


def _regex(pattern):
    return [r for r in [pattern["table_name"], pattern["field_name"], *pattern["words"]] if r]


def _xml_impattato(testo, pattern):
    try:
        radice = ET.fromstring(testo)
    except ET.ParseError:
        return all(re.search(r, testo) for r in _regex(pattern))
    for s in radice.iter("SOURCE"):
        if re.search(pattern["table_name"], s.get("NAME", "")) and any(
                re.search(pattern["field_name"], f.get("NAME", "")) for f in s.iter("SOURCEFIELD")):
            return True
    for a in radice.iter("TABLEATTRIBUTE"):
        if a.get("NAME") == "Sql Query" and all(re.search(r, a.get("VALUE", "")) for r in _regex(pattern)):
            return True
    return False


def grants(testo):
    schemi = []
    for m in RE_GRANT_TO.finditer(testo):
        schemi += [s for s in re.split(r"[\s,]+", m.group(1).strip()) if s]
    return schemi


def file_impattati(indice, pattern):
    """Elenco (percorso, grants) dei file che l'originale segnalerebbe."""
    risultato = []
    for rel, testo in sorted(indice.testi.items()):
        if indice.tipi_file[rel] == "xml" and pattern["field_name"]:
            impattato = _xml_impattato(testo, pattern)
        else:
            impattato = all(re.search(r, testo) for r in _regex(pattern))
        if impattato:
            vista = "/VIEWS/" in "/" + rel and rel.lower().endswith(".sql")
            risultato.append((rel, grants(testo) if vista else None))
    return risultato


def formatta(indice, patterns, adesso=None):
    """Righe nello stesso formato dell'originale."""
    adesso = adesso or datetime.now()
    righe = [f"{adesso:%Y-%m-%d %H:%M:%S} ANALISI D'IMPATTO"]
    for p in patterns:
        righe.append(f"####PATTERN {p}")
        for rel, g in file_impattati(indice, p):
            righe.append(f"{rel} grants[{', '.join(g)}]" if g is not None else rel)
    righe.append("ANALISI D'IMPATTO terminata")
    return righe
