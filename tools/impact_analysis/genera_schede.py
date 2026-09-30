"""Genera le schede di oggetto in docs/oggetti/.

Modello a due livelli:
- la **scheda** la scrive solo questo script: struttura dal DDL, chi scrive,
  chi legge, chi consuma, impatti a catena. Non si modifica mai a mano;
- la **nota** la scrive solo una persona: è il file .md accanto al sorgente,
  con lo stesso nome. Lo script la legge e la copia nella scheda così com'è,
  senza mai modificarla.

L'output è deterministico: data e hash nel banner sono quelli dell'ultimo
commit che ha toccato il codice, non l'ora di esecuzione. Due esecuzioni sullo
stesso codice producono file identici.
"""

import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from scanner import (CHIAMATA, CONSUMO, DA_VERIFICARE, IDENT, LETTURA, SCRITTURA,
                     _dividi_top_level, _parentesi_chiusa, pulisci_sql)

CARTELLA = Path("docs") / "oggetti"
CATEGORIE = {
    "tabella": "Tabelle",
    "vista": "Viste di controllo",
    "package": "Package e funzioni",
    "funzione": "Package e funzioni",
    "procedura": "Package e funzioni",
    "shell": "Shell e Workflow",
    "workflow": "Shell e Workflow",
}
TITOLI = {"tabella": "Tabella", "vista": "Vista", "package": "Package", "funzione": "Funzione",
          "procedura": "Procedura", "shell": "Shell", "workflow": "Workflow"}
AVVISO_NOTA = "Codice modificato dopo l'ultima nota: verificare"
LIMITI = """## Limiti

L'analisi legge solo i file del repository. Non vede:

- **sinonimi** e **db link**: un oggetto letto tramite sinonimo o da un altro database non
  risulta collegato;
- **SQL dinamico**: le istruzioni costruite a runtime (`EXECUTE IMMEDIATE`, stringhe concatenate)
  sono segnalate come "da verificare", ma gli oggetti che toccano non sono noti;
- **oggetti non versionati**: tabelle, job o report che non stanno in questo repository
  (per esempio un cruscotto o un job di manutenzione dello schedulatore).

I risultati vanno sempre confermati con chi conosce il flusso.
"""


# --------------------------------------------------------------------------- git
def _git(radice, *argomenti):
    try:
        esito = subprocess.run(["git", "-C", str(radice), *argomenti], capture_output=True,
                               text=True, check=False)
    except OSError:
        return None
    return esito.stdout.strip() if esito.returncode == 0 else None


def commit_analizzato(radice):
    """Hash breve e data dell'ultimo commit che ha toccato il codice."""
    uscita = _git(radice, "log", "-1", "--format=%h|%cs", "--", "sql", "script", "powercenter")
    if not uscita:
        return None, None
    hash_breve, data = uscita.split("|")
    return hash_breve, data


def ultima_modifica(radice, rel):
    uscita = _git(radice, "log", "-1", "--format=%ct", "--", rel)
    return int(uscita) if uscita else None


def _data(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


# --------------------------------------------------------------------------- utilità
def slug(ogg):
    return Path(ogg.nome).stem if ogg.tipo == "shell" else ogg.nome


def ha_scheda(ogg):
    return ogg.tipo in CATEGORIE and ogg.file


def motore(ogg, aree):
    for nome_motore, regole in aree.items():
        if any(r.search(ogg.nome) or r.search(ogg.file or "") for r in regole):
            return nome_motore
    return None


def _cella(testo):
    return str(testo).replace("|", "\\|").replace("\n", " ")


def intestazione(testo, chiave):
    """Valore di una voce dell'intestazione del sorgente (es. `Descrizione :`),
    comprese le righe di continuazione."""
    righe, dentro = [], False
    for riga in testo.splitlines()[:40]:
        if riga.lstrip().startswith("<") and not riga.lstrip().startswith("<!--"):
            if dentro:
                break
            continue                      # righe XML fuori dal commento di intestazione
        fine_commento = "-->" in riga
        corpo = re.sub(r"^\s*(--|#|<!--)?", "", riga.replace("-->", "")).rstrip()
        m = re.match(r"^\s{0,3}([A-Za-z][\w ]*?)\s*:\s*(.*)$", corpo)
        if m and not corpo.startswith("    "):
            if dentro:
                break
            if m.group(1).strip().lower() == chiave.lower():
                dentro = True
                righe.append(m.group(2).strip())
            continue
        if dentro:
            if not corpo.strip() or set(corpo.strip()) <= set("-=#*"):
                break
            righe.append(corpo.strip())
            if fine_commento:
                break
    return " ".join(r for r in righe if r)


class Generatore:
    def __init__(self, indice, grafo, cfg, radice):
        self.indice, self.grafo, self.cfg, self.radice = indice, grafo, cfg, Path(radice)
        self.hash, self.data_commit = commit_analizzato(self.radice)
        self.oggetti = sorted((o for o in indice.oggetti.values() if ha_scheda(o)),
                              key=lambda o: o.nome.lower())
        self.nav = {}
        per_categoria = {}
        for o in self.oggetti:
            per_categoria.setdefault(CATEGORIE[o.tipo], []).append(o)
        for lista in per_categoria.values():
            for i, o in enumerate(sorted(lista, key=lambda o: o.nome.lower()), 1):
                self.nav[o.nome] = i

    # ---------------------------------------------------------------- link
    def link(self, nome):
        ogg = self.indice.oggetti.get(nome)
        if ogg and ha_scheda(ogg):
            return f"[`{nome}`]({slug(ogg)}.md)"
        return f"`{nome}`"

    @staticmethod
    def link_file(rel, riga=None):
        testo = f"{rel}:{riga}" if riga else rel
        return f"[`{testo}`](../../{rel})"

    # ---------------------------------------------------------------- note
    def nota(self, ogg):
        """(percorso, testo, avviso) della nota accanto al sorgente, o None."""
        rel = str(Path(ogg.file).with_suffix(".md").as_posix())
        percorso = self.radice / rel
        if not percorso.is_file():
            return None
        testo = percorso.read_text(encoding="utf-8")
        t_sorgente, t_nota = ultima_modifica(self.radice, ogg.file), ultima_modifica(self.radice, rel)
        avviso = None
        if t_sorgente and t_nota and t_sorgente > t_nota:
            avviso = (t_sorgente, t_nota)
        return rel, testo, avviso

    # ---------------------------------------------------------------- struttura
    def struttura_tabella(self, ogg):
        testo = self.indice.testi[ogg.file]
        righe = ["| Campo | Tipo | Commento |", "|---|---|---|"]
        for c in ogg.colonne:
            righe.append(f"| `{c['nome']}` | {_cella(c['tipo'])} | {_cella(c['commento'])} |")
        pulito = pulisci_sql(testo)
        m = re.search(rf"\bCREATE\s+TABLE\s+(?:{IDENT}\.)?{re.escape(ogg.nome)}\s*\(", pulito, re.I)
        if m:
            fine = _parentesi_chiusa(pulito, m.end() - 1)
            punto = pulito.find(";", fine)
            # stesse posizioni del testo pulito, ma con le stringhe letterali intatte
            originale = re.sub(r"--[^\n]*", "", testo[fine + 1:punto])
            clausola = "\n".join(r.rstrip() for r in originale.splitlines() if r.strip())
            if clausola:
                righe += ["", "**Partizionamento e memorizzazione**", "", "```sql", clausola, "```"]
        vincoli = []
        for rel, t in sorted(self.indice.testi.items()):
            if self.indice.tipi_file[rel] != "sql":
                continue
            for mv in re.finditer(
                    rf"ALTER\s+TABLE\s+(?:{IDENT}\.)?{re.escape(ogg.nome)}\s+ADD\s+CONSTRAINT\s+({IDENT})\s+"
                    r"(PRIMARY\s+KEY|UNIQUE|CHECK|FOREIGN\s+KEY)\s*(\(.*?\))\s*;", t, re.I | re.S):
                vincoli.append((mv.group(1), " ".join(mv.group(2).upper().split()),
                                " ".join(mv.group(3).split()), rel))
        if vincoli:
            righe += ["", "**Chiavi e vincoli**", "", "| Nome | Tipo | Definizione | File |", "|---|---|---|---|"]
            for nome, tipo, definizione, rel in vincoli:
                righe.append(f"| `{nome}` | {tipo} | `{_cella(definizione)}` | {self.link_file(rel)} |")
        return righe

    def struttura_vista(self, ogg):
        righe = ["| Colonna |", "|---|"]
        righe += [f"| `{c['nome']}` |" for c in ogg.colonne]
        return righe

    def _parametri(self, testo_param):
        righe = []
        for p in _dividi_top_level(testo_param):
            parti = p.split()
            if parti:
                righe.append((parti[0], " ".join(parti[1:])))
        return righe

    def struttura_plsql(self, ogg):
        testo = self.indice.testi[ogg.file]
        pulito = pulisci_sql(testo)
        if ogg.tipo == "package":
            m = re.search(rf"\bPACKAGE\s+(?!BODY\b)(?:{IDENT}\.)?{re.escape(ogg.nome)}\b", pulito, re.I)
            if not m:
                return ["Specifica del package non trovata nel sorgente."]
            fine = re.search(rf"\bEND\s+{re.escape(ogg.nome)}\s*;", pulito[m.end():], re.I)
            regione = (m.end(), m.end() + (fine.start() if fine else len(pulito)))
            righe = ["Procedure e funzioni pubbliche (dalla specifica del package):", "",
                     "| Nome | Tipo | Parametri | Restituisce | Descrizione |", "|---|---|---|---|---|"]
        else:
            regione = (0, len(pulito))
            righe = ["| Nome | Tipo | Parametri | Restituisce | Descrizione |", "|---|---|---|---|---|"]
        righe_testo = testo.splitlines()
        for ms in re.finditer(rf"\b(PROCEDURE|FUNCTION)\s+(?:{IDENT}\.)?({IDENT})",
                              pulito[regione[0]:regione[1]], re.I):
            inizio = regione[0] + ms.end()
            dopo = pulito[inizio:].lstrip()
            parametri = ""
            pos = inizio + (len(pulito[inizio:]) - len(dopo))
            if dopo.startswith("("):
                chiusa = _parentesi_chiusa(pulito, pos)
                parametri = "; ".join(f"`{n}` {t}" for n, t in self._parametri(pulito[pos + 1:chiusa]))
                pos = chiusa + 1
            rit = re.match(rf"\s*RETURN\s+({IDENT})", pulito[pos:], re.I)
            n_riga = pulito.count("\n", 0, regione[0] + ms.start())
            descrizione = []
            k = n_riga - 1
            while k >= 0 and righe_testo[k].strip().startswith("--") and not set(righe_testo[k].strip()) <= {"-"}:
                descrizione.insert(0, righe_testo[k].strip().lstrip("-").strip())
                k -= 1
            righe.append(f"| `{ms.group(2).upper()}` | {ms.group(1).lower()} | {_cella(parametri) or '—'} | "
                         f"{rit.group(1).upper() if rit else '—'} | {_cella(' '.join(descrizione)) or '—'} |")
            if ogg.tipo != "package":
                break
        return righe

    def struttura_shell(self, ogg):
        testo = self.indice.testi[ogg.file]
        righe = []
        uso = intestazione(testo, "Uso")
        if uso:
            righe += [f"**Uso:** `{uso}`", ""]
        fonti = [(ogg.file, testo)]
        for r in self.grafo.uscenti(ogg.nome, CHIAMATA):
            lib = self.indice.oggetti.get(r.oggetto_riferito)
            if lib and lib.tipo == "shell":
                fonti.append((lib.file, self.indice.testi[lib.file]))
        opzioni = []
        for rel, t in fonti:
            for mo in re.finditer(r"^\s*(-\w)\)\s*([A-Z_]\w*)=\"?([^\";]*)\"?", t, re.M):
                opzioni.append((mo.group(1), mo.group(2), mo.group(3), rel))
        if opzioni:
            righe += ["**Parametri** (letti dal codice che interpreta la riga di comando):", "",
                      "| Opzione | Variabile | Valore | Definita in |", "|---|---|---|---|"]
            for opz, var, val, rel in opzioni:
                valore = "argomento successivo" if val.startswith("$") else f"`{val}`"
                righe.append(f"| `{opz}` | `{var}` | {valore} | {self.link_file(rel)} |")
            righe.append("")
        variabili = re.findall(r"^([A-Z][A-Z0-9_]*)=(\"[^\"]*\"|'[^']*'|\S*)[ \t]*(?:#[ \t]*(.*))?$", testo, re.M)
        if variabili:
            righe += ["**Variabili impostate:**", "", "| Variabile | Valore | Commento |", "|---|---|---|"]
            for var, val, commento in variabili:
                righe.append(f"| `{var}` | `{_cella(val.strip(chr(34)))}` | {_cella(commento) or '—'} |")
            righe.append("")
        funzioni = re.findall(r"^([a-z_]\w*)\s*\(\)\s*\{", testo, re.M)
        if funzioni:
            righe += ["**Funzioni definite:** " + ", ".join(f"`{f}`" for f in funzioni), ""]
        return righe or ["Nessun parametro riconosciuto."]

    def struttura_workflow(self, ogg):
        radice = ET.fromstring(self.indice.testi[ogg.file])
        righe = []
        sessioni = [(s.get("NAME"), s.get("MAPPINGNAME"), s.get("DESCRIPTION", "")) for s in radice.iter("SESSION")]
        if sessioni:
            righe += ["**Sessioni**", "", "| Sessione | Mapping | Descrizione |", "|---|---|---|"]
            righe += [f"| `{n}` | `{m}` | {_cella(d) or '—'} |" for n, m, d in sessioni]
            righe.append("")
        for tag, titolo in (("SOURCE", "Source"), ("TARGET", "Target")):
            elementi = list(radice.iter(tag))
            if elementi:
                righe += [f"**{titolo}**", "", "| Nome | Tipo | Campi |", "|---|---|---|"]
                for e in elementi:
                    tipo = e.get("DATABASETYPE", "")
                    campi = len(list(e.iter(tag + "FIELD")))
                    righe.append(f"| {self.link(e.get('NAME', '').upper())} | {tipo} | {campi} |")
                righe.append("")
        lookup = [(t.get("NAME"), a.get("VALUE")) for t in radice.iter("TRANSFORMATION")
                  if t.get("TYPE") == "Lookup Procedure"
                  for a in t.iter("TABLEATTRIBUTE") if a.get("NAME") == "Lookup table name"]
        if lookup:
            righe += ["**Lookup**", "", "| Trasformazione | Tabella |", "|---|---|"]
            righe += [f"| `{n}` | {self.link(v.split('.')[-1].upper())} |" for n, v in lookup]
            righe.append("")
        parametri = sorted({v.get("NAME") for v in radice.iter("MAPPINGVARIABLE")} |
                           {v.get("NAME") for v in radice.iter("WORKFLOWVARIABLE")})
        if parametri:
            righe += ["**Parametri:** " + ", ".join(f"`{p}`" for p in parametri), ""]
        return righe

    # ---------------------------------------------------------------- sezioni riferimenti
    def tabella_riferimenti(self, riferimenti, colonna_oggetto, entranti=True):
        righe = [f"| {colonna_oggetto} | Contesto | Campi | Dove |", "|---|---|---|---|"]
        for r in sorted(riferimenti, key=lambda r: (r.oggetto_chiamante if entranti else r.oggetto_riferito,
                                                     r.contesto, r.file, r.riga or 0)):
            nome = r.oggetto_chiamante if entranti else r.oggetto_riferito
            if nome.startswith(("sql/", "script/", "powercenter/")):
                nome_cella = f"script {self.link_file(nome)}"
            else:
                nome_cella = self.link(nome)
            campi = ", ".join(r.campi) if r.campi else "—"
            righe.append(f"| {nome_cella} | {r.contesto} | {_cella(campi)} | {self.link_file(r.file, r.riga)} |")
        return righe

    def mermaid(self, ogg, impatti):
        nodi = [ogg.nome] + sorted(n for n, i in impatti.items() if i.livello <= 2)
        ident = {n: f"n{k}" for k, n in enumerate(nodi)}
        righe = ["```mermaid", "flowchart LR"]
        for n in nodi:
            etichetta = n.replace('"', "'")
            righe.append(f'  {ident[n]}["{etichetta}"]')
        for a, b, etichetta in self.grafo.archi(nodi):
            freccia = "-.->" if etichetta == "chiama" else "-->"
            righe.append(f"  {ident[a]} {freccia}|{etichetta}| {ident[b]}")
        righe += [f"  class {ident[ogg.nome]} centro",
                  "  classDef centro fill:#1f4e79,stroke:#1f4e79,color:#ffffff", "```"]
        return righe

    # ---------------------------------------------------------------- scheda
    def scheda(self, ogg):
        indice, grafo = self.indice, self.grafo
        testo = indice.testi[ogg.file]
        nome_motore = motore(ogg, self.cfg["aree"])
        fm = ["---", f"title: {ogg.nome}"]
        if nome_motore:
            fm += [f"parent: {CATEGORIE[ogg.tipo]}", f"grand_parent: {nome_motore}"]
        else:
            fm += ["parent: Schede di oggetto"]
        fm += [f"nav_order: {self.nav[ogg.nome]}", "---", ""]

        qualificato = f"{ogg.schema}.{ogg.nome}" if ogg.schema else ogg.nome
        r = fm + [f"# {TITOLI[ogg.tipo]}: `{qualificato}`", "", self.banner(), ""]

        # 1. Descrizione
        r += ["## Descrizione", ""]
        tipo_hdr = intestazione(testo, "Tipo")
        descr = intestazione(testo, "Descrizione")
        commento = re.search(rf"COMMENT\s+ON\s+TABLE\s+(?:{IDENT}\.)?{re.escape(ogg.nome)}\s+IS\s+'((?:[^']|'')*)'",
                             testo, re.I)
        if ogg.tipo == "workflow":
            wf = ET.fromstring(testo).find(".//WORKFLOW")
            if wf is not None and wf.get("DESCRIPTION"):
                intestazione_xml = f" Dall'intestazione dell'export: {descr}" if descr else ""
                descr = wf.get("DESCRIPTION") + "." + intestazione_xml
        if tipo_hdr:
            r += [f"**Tipo:** {tipo_hdr}", ""]
        r += [descr or (commento.group(1).replace("''", "'") if commento else "Nessuna descrizione nel sorgente."), ""]
        if commento and descr:
            r += [f"**Commento sul database:** {commento.group(1)}", ""]

        # 2. Struttura
        r += ["## Struttura", ""]
        r += {"tabella": self.struttura_tabella, "vista": self.struttura_vista,
              "package": self.struttura_plsql, "funzione": self.struttura_plsql,
              "procedura": self.struttura_plsql, "shell": self.struttura_shell,
              "workflow": self.struttura_workflow}[ogg.tipo](ogg)
        while r and r[-1] == "":
            r.pop()
        r.append("")

        # 3. Chi scrive, chi legge, chi consuma (e, per i programmi, cosa usano)
        sezioni = [
            ("Chi scrive", grafo.entranti(ogg.nome, SCRITTURA), "Chi scrive", True),
            ("Chi legge", grafo.entranti(ogg.nome, LETTURA), "Chi legge", True),
            ("Chi lo chiama", grafo.entranti(ogg.nome, CHIAMATA), "Chiamante", True),
            ("Cosa scrive", grafo.uscenti(ogg.nome, SCRITTURA), "Oggetto scritto", False),
            ("Cosa legge", grafo.uscenti(ogg.nome, LETTURA), "Oggetto letto", False),
            ("Cosa chiama", grafo.uscenti(ogg.nome, CHIAMATA), "Oggetto chiamato", False),
        ]
        for titolo, riferimenti, colonna, entranti in sezioni:
            if riferimenti:
                r += [f"## {titolo}", ""] + self.tabella_riferimenti(riferimenti, colonna, entranti) + [""]
            elif titolo in ("Chi scrive", "Chi legge") and ogg.tipo in ("tabella", "vista"):
                r += [f"## {titolo}", "", "Nessun riferimento trovato nel repository.", ""]
        consumi = grafo.entranti(ogg.nome, CONSUMO)
        if consumi or ogg.tipo == "vista":
            r += ["## Chi consuma", ""]
            if consumi:
                r += ["Schemi a cui la vista è concessa con `GRANT`:", "", "| Schema | Dove |", "|---|---|"]
                r += [f"| `{c.oggetto_chiamante}` | {self.link_file(c.file, c.riga)} |" for c in consumi]
            else:
                r.append("Nessun `GRANT` trovato: la vista non risulta concessa ad altri schemi.")
            r.append("")

        # 4. Impatti indiretti
        impatti = grafo.impatti(ogg.nome)
        indiretti = sorted((i for i in impatti.values() if i.livello > 1), key=lambda i: (i.livello, i.oggetto))
        r += ["## Impatti indiretti", ""]
        if indiretti:
            r += ["Oggetti raggiunti a catena, a valle dei riferimenti diretti:", "",
                  "| Livello | Oggetto | Ruolo | Raggiunto da |", "|---|---|---|---|"]
            r += [f"| {i.livello} | {self.link(i.oggetto)} | {i.ruolo} | {self.link(i.da)} |" for i in indiretti]
        else:
            r.append("Nessun impatto indiretto trovato nel repository.")
        r.append("")
        if impatti:
            r += ["Diagramma dei primi due livelli:", ""] + self.mermaid(ogg, impatti) + [""]

        # 5. Da verificare
        dinamici = [x for x in grafo.uscenti(ogg.nome, DA_VERIFICARE)]
        if dinamici:
            r += ["## Da verificare", "",
                  "Il sorgente contiene SQL dinamico: gli oggetti toccati da queste istruzioni non si possono "
                  "ricavare dal codice.", ""]
            r += [f"- {self.link_file(x.file, x.riga)}" for x in dinamici]
            r.append("")

        # 6. Note
        nota = self.nota(ogg)
        if nota:
            rel, contenuto, avviso = nota
            r += ["## Note", ""]
            if avviso:
                r += [f"> ⚠️ **{AVVISO_NOTA}.** Il sorgente è stato modificato il {_data(avviso[0])}, "
                      f"la nota l'ultima volta il {_data(avviso[1])}.", ""]
            # niente link: le note sono escluse dal sito, il link darebbe 404. Il percorso basta
            # per trovarla nel repository, accanto al sorgente collegato più sotto.
            r += [f"Nota scritta a mano, da modificare nel repository: `{rel}`", "",
                  contenuto.rstrip("\n"), ""]

        # 7. Sorgente
        r += ["## Sorgente", "", self.link_file(ogg.file), ""]

        # 8. Limiti
        r += [LIMITI]
        return "\n".join(r).rstrip("\n") + "\n", impatti, nota, dinamici

    def banner(self):
        if self.hash:
            origine = f"Commit analizzato `{self.hash}` del {self.data_commit}."
        else:
            origine = "Commit analizzato non disponibile (repository senza storia Git)."
        return ("> ⚙️ **Scheda generata automaticamente, non modificare a mano.** " + origine +
                " Le spiegazioni scritte a mano vanno nella nota accanto al sorgente.")

    # ---------------------------------------------------------------- indice
    def pagina_indice(self, righe_tabella):
        r = ["---", "title: Schede di oggetto", "nav_order: 4", "---", "",
             "# Schede di oggetto", "", self.banner(), "",
             "La documentazione degli oggetti è su due livelli:", "",
             "- la **scheda** di ogni oggetto la scrive uno script, a partire dal codice: struttura, "
             "chi scrive, chi legge, chi consuma e impatti a catena. Non si modifica a mano;",
             "- la **nota** la scrive una persona, solo se serve: è il file `.md` accanto al sorgente, "
             "con lo stesso nome, e contiene quello che il codice non dice (il perché delle scelte, "
             "le avvertenze). La scheda la riporta così com'è.", "",
             "Come si documenta un oggetto: vedi [come documentare](../come_documentare.md).", "",
             "| Oggetto | Tipo | Impatti diretti | Impatti indiretti | Nota | Da verificare |",
             "|---|---|---|---|---|---|"]
        r += righe_tabella
        dinamici = self.indice.da_verificare()
        if dinamici:
            r += ["", "## Riferimenti da verificare", "",
                  "Istruzioni di SQL dinamico: l'analisi non può sapere quali oggetti toccano.", ""]
            r += [f"- {self.link(x.oggetto_chiamante)}: {self.link_file(x.file, x.riga)}" for x in dinamici]
        esterni = sorted(n for n, o in self.indice.oggetti.items() if o.tipo in ("schema", "file", "esterno"))
        if esterni:
            r += ["", "## Oggetti citati ma non definiti nel repository", "",
                  "| Oggetto | Tipo | Citato da |", "|---|---|---|"]
            for n in esterni:
                chi = sorted({x.oggetto_chiamante if x.oggetto_riferito == n else x.oggetto_riferito
                              for x in self.indice.riferimenti if n in (x.oggetto_riferito, x.oggetto_chiamante)}
                             - {n})
                r.append(f"| `{n}` | {self.indice.oggetti[n].tipo} | {', '.join(self.link(c) for c in chi)} |")
        return "\n".join(r) + "\n"

    # ---------------------------------------------------------------- scrittura
    def genera(self):
        cartella = self.radice / CARTELLA
        if cartella.exists():
            shutil.rmtree(cartella)
        cartella.mkdir(parents=True)
        righe_indice, avvisi = [], 0
        for ogg in self.oggetti:
            contenuto, impatti, nota, dinamici = self.scheda(ogg)
            (cartella / f"{slug(ogg)}.md").write_text(contenuto, encoding="utf-8")
            diretti = sum(1 for i in impatti.values() if i.livello == 1)
            indiretti = len(impatti) - diretti
            segnali = []
            if nota and nota[2]:
                segnali.append("⚠️ nota")
                avvisi += 1
            if dinamici:
                segnali.append("SQL dinamico")
            righe_indice.append(f"| {self.link(ogg.nome)} | {ogg.tipo} | {diretti} | {indiretti} | "
                                f"{'sì' if nota else '—'} | {', '.join(segnali) or '—'} |")
        (cartella / "index.md").write_text(self.pagina_indice(righe_indice), encoding="utf-8")
        return {"cartella": str(CARTELLA), "schede": len(self.oggetti), "avvisi": avvisi,
                "dinamici": len(self.indice.da_verificare())}


def genera(indice, grafo, cfg, radice):
    """Cancella e ricrea docs/oggetti/ con una scheda per oggetto e l'indice."""
    return Generatore(indice, grafo, cfg, radice).genera()
