#!/usr/bin/env python3
"""Analisi d'impatto sul codice del data warehouse (v2).

Uso:
    python tools/impact_analysis/impact_analysis.py                 # configurazione di default, output a video
    python tools/impact_analysis/impact_analysis.py mio.cfg.py      # configurazione alternativa
    python tools/impact_analysis/impact_analysis.py --compatibile   # stesso formato dello strumento originale
    python tools/impact_analysis/impact_analysis.py --tutto         # genera le schede in docs/oggetti/
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import compat          # noqa: E402
import config          # noqa: E402
import grafo           # noqa: E402
import scanner         # noqa: E402

RADICE_DEFAULT = Path(__file__).resolve().parents[2]


def oggetti_del_pattern(indice, pattern):
    re_tab = re.compile(pattern["table_name"], re.I)
    return sorted(n for n, o in indice.oggetti.items()
                  if re_tab.search(n) and o.tipo not in ("script", "schema"))


def _posizione(r):
    return f"{r.file}:{r.riga}" if r.riga else r.file


def report_v2(indice, g, patterns):
    """Righe dell'output di default: per ogni pattern, i riferimenti
    raggruppati per livello e direzione, con il contesto."""
    righe = [f"{datetime.now():%Y-%m-%d %H:%M:%S} ANALISI D'IMPATTO v2"]
    for p in patterns:
        righe.append("")
        righe.append(f"#### PATTERN {p}")
        oggetti = oggetti_del_pattern(indice, p)
        if not oggetti:
            righe.append("  nessun oggetto corrisponde a table_name")
        for nome in oggetti:
            ogg = indice.oggetti[nome]
            campo = f" — campo {p['field_name']}" if p["field_name"] else ""
            righe.append(f"Oggetto {nome} ({ogg.tipo}){campo}")
            impatti = g.impatti(nome, p["field_name"], p["words"])
            if not impatti:
                righe.append("  nessun impatto trovato")
                continue
            livelli = sorted({i.livello for i in impatti.values()})
            for liv in livelli:
                righe.append(f"  Livello {liv}")
                del_livello = [i for i in impatti.values() if i.livello == liv]
                for ruolo in ("scrive", "legge", "chiama", "consuma", "è scritto da"):
                    gruppo = sorted((i for i in del_livello if i.ruolo == ruolo), key=lambda i: i.oggetto)
                    if not gruppo:
                        continue
                    righe.append(f"    {ruolo.upper()}")
                    for i in gruppo:
                        tipo = indice.oggetti[i.oggetto].tipo if i.oggetto in indice.oggetti else "?"
                        via = f"  (via {i.da})" if liv > 1 else ""
                        righe.append(f"      {i.oggetto} [{tipo}]{via}")
                        if liv == 1:
                            for r in i.riferimenti:
                                campi = f"  campi: {', '.join(r.campi)}" if r.campi else ""
                                righe.append(f"        {r.contesto:<12} {_posizione(r)}{campi}")
    dinamici = indice.da_verificare()
    if dinamici:
        righe.append("")
        righe.append("#### DA VERIFICARE (SQL dinamico: oggetti non determinabili dal codice)")
        for r in dinamici:
            righe.append(f"  {r.oggetto_chiamante}  {_posizione(r)}")
    return righe


def confronto(indice, g, patterns):
    """Quanti file l'approccio originale segnala in più o in meno rispetto
    ai riferimenti diretti (livello 1) trovati dalla v2."""
    righe = ["", "#### CONFRONTO CON LA v2 (riferimenti diretti)"]
    for p in patterns:
        orig = {rel for rel, _ in compat.file_impattati(indice, p)}
        v2 = set()
        for nome in oggetti_del_pattern(indice, p):
            for i in g.impatti(nome, p["field_name"], p["words"]).values():
                if i.livello == 1:
                    v2 |= {r.file for r in i.riferimenti}
        in_piu, in_meno = sorted(orig - v2), sorted(v2 - orig)
        righe.append(f"PATTERN {p['table_name']}"
                     + (f" / {p['field_name']}" if p["field_name"] else ""))
        righe.append(f"  originale: {len(orig)} file, v2: {len(v2)} file, "
                     f"in più nell'originale: {len(in_piu)}, in meno nell'originale: {len(in_meno)}")
        for rel in in_piu:
            righe.append(f"  + {rel}")
        for rel in in_meno:
            righe.append(f"  - {rel}")
    return righe


def main(argv=None):
    parser = argparse.ArgumentParser(description="Analisi d'impatto sul codice del DWH (v2)")
    parser.add_argument("config", nargs="?", help="file di configurazione .cfg.py (default: impact_analysis.cfg.py)")
    parser.add_argument("--compatibile", action="store_true",
                        help="output nel formato dello strumento originale, più il confronto con la v2")
    parser.add_argument("--tutto", action="store_true",
                        help="genera le schede di tutti gli oggetti in docs/oggetti/")
    parser.add_argument("--radice", default=str(RADICE_DEFAULT), help="radice del repository")
    args = parser.parse_args(argv)

    try:
        cfg = config.carica(args.config)
    except config.ConfigError as e:
        print(f"Errore di configurazione: {e}", file=sys.stderr)
        return 2

    indice = scanner.costruisci(args.radice, cfg["ignore"])
    g = grafo.Grafo(indice)

    if args.tutto:
        import genera_schede
        esito = genera_schede.genera(indice, g, cfg, Path(args.radice))
        print(f"Schede generate in {esito['cartella']}: {esito['schede']} oggetti, "
              f"{esito['avvisi']} note da verificare, {esito['dinamici']} riferimenti da verificare")
        return 0

    righe = compat.formatta(indice, cfg["patterns"]) + confronto(indice, g, cfg["patterns"]) \
        if args.compatibile else report_v2(indice, g, cfg["patterns"])
    print("\n".join(righe))
    return 0


if __name__ == "__main__":
    sys.exit(main())
