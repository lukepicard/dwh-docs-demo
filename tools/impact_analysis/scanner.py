"""Indice dei riferimenti tra oggetti, costruito leggendo il codice una volta sola.

Legge tutti i file di `sql/`, `script/` e `powercenter/` (escludendo i percorsi
di IGNORE_PATH_PATTERNS), costruisce il catalogo degli oggetti definiti nel
repository e l'elenco dei riferimenti: chi legge, chi scrive, chi chiama, chi
consuma cosa. Non si collega al database: analizza solo i file.
"""

import re
import shlex
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

CARTELLE = ("sql", "script", "powercenter")
ESTENSIONI = {
    ".sql": "sql", ".pks": "sql", ".pkb": "sql", ".prc": "sql", ".fnc": "sql", ".vw": "sql",
    ".sh": "shell", ".ksh": "shell", ".bash": "shell",
    ".xml": "xml",
}

LETTURA, SCRITTURA, CHIAMATA, CONSUMO, DA_VERIFICARE = (
    "LETTURA", "SCRITTURA", "CHIAMATA", "CONSUMO", "DA_VERIFICARE")
DIREZIONI = (SCRITTURA, LETTURA, CHIAMATA, CONSUMO, DA_VERIFICARE)
CONTESTI = ("SOURCE", "TARGET", "LOOKUP", "SQL_OVERRIDE", "PRE_SQL", "POST_SQL", "STATEMENT")

TIPI_SQL = {"TABLE": "tabella", "VIEW": "vista", "PACKAGE": "package", "PACKAGE BODY": "package",
            "FUNCTION": "funzione", "PROCEDURE": "procedura", "SEQUENCE": "sequence",
            "TRIGGER": "trigger", "TYPE": "tipo"}
TIPI_CHIAMABILI = {"package", "funzione", "procedura"}
SQL_DINAMICO = "(SQL dinamico)"

IDENT = r"[A-Za-z_][\w$#]*"
RE_IDENT = re.compile(IDENT)
RE_CREATE = re.compile(
    r"\bCREATE\s+(?:OR\s+REPLACE\s+)?(?:(?:NON)?EDITIONABLE\s+)?"
    r"(TABLE|VIEW|PACKAGE\s+BODY|PACKAGE|FUNCTION|PROCEDURE|SEQUENCE|TRIGGER|TYPE)\s+"
    rf"(?:({IDENT})\.)?({IDENT})", re.I)
RE_SCRITTURA = r"(?:INSERT\s+INTO|UPDATE|MERGE\s+INTO|DELETE\s+FROM|DELETE|TRUNCATE\s+TABLE)"
RE_ALTER_TRUNCATE = re.compile(
    rf"\bALTER\s+TABLE\s+(?:{IDENT}\.)?({IDENT})\s+(?:TRUNCATE|DROP|EXCHANGE)\s+(?:SUB)?PARTITION", re.I)
RE_ESTERNO = re.compile(
    rf"\b(FROM|JOIN|USING|INSERT\s+INTO|MERGE\s+INTO|UPDATE|DELETE\s+FROM|TRUNCATE\s+TABLE)\s+"
    rf"(?:({IDENT})\.)?({IDENT})", re.I)
RE_GRANT = re.compile(
    rf"\bGRANT\s+[\w\s,]+?\s+ON\s+(?:{IDENT}\.)?({IDENT})\s+TO\s+([\w\s,$#]+?)(?:\s+WITH\s+GRANT\s+OPTION)?\s*$",
    re.I)
RE_CTE = re.compile(rf"(?:\bWITH|,)\s*({IDENT})\s+AS\s*\(", re.I)
RE_DINAMICO = re.compile(r"\bEXECUTE\s+IMMEDIATE\b|\bDBMS_SQL\s*\.", re.I)
PAROLE_NON_OGGETTO = {"DUAL", "SELECT", "TABLE", "THE", "LATERAL", "WHERE", "SET", "VALUES"}


@dataclass
class Oggetto:
    nome: str
    tipo: str
    file: str = None
    schema: str = None
    colonne: list = field(default_factory=list)   # [{"nome", "tipo", "commento"}]


@dataclass
class Riferimento:
    file: str
    tipo_file: str
    oggetto_chiamante: str
    oggetto_riferito: str
    direzione: str
    campi: list
    contesto: str
    riga: int = None
    testo: str = ""          # testo dello statement o del contesto, per le regex `words`

    def chiave(self):
        return (self.file, self.oggetto_chiamante, self.oggetto_riferito, self.direzione, self.contesto)


# --------------------------------------------------------------------------- SQL
def pulisci_sql(testo):
    """Sostituisce con spazi commenti (`--`, `/* */`) e stringhe letterali,
    conservando gli a capo: le posizioni restano valide per il numero di riga."""
    out = list(testo)
    i, n = 0, len(testo)
    while i < n:
        c = testo[i]
        if c == "-" and testo.startswith("--", i):
            j = testo.find("\n", i)
            j = n if j < 0 else j
        elif c == "/" and testo.startswith("/*", i):
            j = testo.find("*/", i + 2)
            j = n if j < 0 else j + 2
        elif c == "'":
            j = i + 1
            while j < n:
                if testo[j] == "'":
                    if j + 1 < n and testo[j + 1] == "'":
                        j += 2
                        continue
                    j += 1
                    break
                j += 1
        else:
            i += 1
            continue
        for k in range(i, j):
            if out[k] != "\n":
                out[k] = " "
        i = j
    return "".join(out)


def spezza_statement(pulito):
    """Divide il testo SQL già pulito in statement, sul `;` o sulla riga `/`.
    Restituisce coppie (offset iniziale, testo)."""
    risultato, inizio = [], 0
    for m in re.finditer(r";|^\s*/\s*$", pulito, re.M):
        pezzo = pulito[inizio:m.start()]
        if pezzo.strip():
            risultato.append((inizio, pezzo))
        inizio = m.end()
    if pulito[inizio:].strip():
        risultato.append((inizio, pulito[inizio:]))
    return risultato


def _riga(testo, offset):
    return testo.count("\n", 0, offset) + 1


def _dividi_top_level(testo, sep=","):
    parti, prof, corrente = [], 0, []
    for c in testo:
        if c == "(":
            prof += 1
        elif c == ")":
            prof -= 1
        if c == sep and prof == 0:
            parti.append("".join(corrente))
            corrente = []
        else:
            corrente.append(c)
    parti.append("".join(corrente))
    return parti


def _parentesi_chiusa(testo, inizio):
    """Posizione della parentesi che chiude quella aperta in `inizio`."""
    prof = 0
    for k in range(inizio, len(testo)):
        if testo[k] == "(":
            prof += 1
        elif testo[k] == ")":
            prof -= 1
            if prof == 0:
                return k
    return len(testo)


def colonne_tabella(testo_originale, nome):
    """Colonne di una CREATE TABLE: nome, tipo e COMMENT ON COLUMN."""
    pulito = pulisci_sql(testo_originale)
    m = re.search(rf"\bCREATE\s+TABLE\s+(?:{IDENT}\.)?{re.escape(nome)}\s*\(", pulito, re.I)
    if not m:
        return []
    fine = _parentesi_chiusa(pulito, m.end() - 1)
    colonne = []
    for parte in _dividi_top_level(testo_originale[m.end():fine]):
        parte_pulita = pulisci_sql(parte).strip()
        if not parte_pulita:
            continue
        prima = parte_pulita.split()[0].upper()
        if prima in {"CONSTRAINT", "PRIMARY", "UNIQUE", "CHECK", "FOREIGN"}:
            continue
        tipo = " ".join(parte.strip().split()[1:])
        colonne.append({"nome": prima, "tipo": tipo, "commento": ""})
    commenti = dict(
        (c.upper(), t.replace("''", "'")) for c, t in re.findall(
            rf"COMMENT\s+ON\s+COLUMN\s+(?:{IDENT}\.)?{re.escape(nome)}\.({IDENT})\s+IS\s+'((?:[^']|'')*)'",
            testo_originale, re.I))
    for c in colonne:
        c["commento"] = commenti.get(c["nome"], "")
    return colonne


def colonne_vista(pulito, nome):
    """Colonne di una vista: gli alias (o gli ultimi identificatori) della
    SELECT più esterna."""
    m = re.search(rf"\bVIEW\s+(?:{IDENT}\.)?{re.escape(nome)}\b.*?\bAS\b", pulito, re.I | re.S)
    if not m:
        return []
    corpo = pulito[m.end():]
    corpo = corpo.split(";", 1)[0]          # solo lo statement della vista, non i GRANT che seguono
    # le SELECT delle CTE sono tra parentesi: la SELECT finale è la prima a profondità zero
    prof, pos_select = 0, None
    for mm in re.finditer(r"\(|\)|\bSELECT\b", corpo, re.I):
        tok = mm.group(0)
        if tok == "(":
            prof += 1
        elif tok == ")":
            prof -= 1
        elif prof == 0:
            pos_select = mm.end()
            break
    if pos_select is None:
        return []
    resto = corpo[pos_select:]
    prof, fine = 0, len(resto)
    for mm in re.finditer(r"\(|\)|\bFROM\b", resto, re.I):
        tok = mm.group(0)
        if tok == "(":
            prof += 1
        elif tok == ")":
            prof -= 1
        elif prof == 0:
            fine = mm.start()
            break
    colonne = []
    for voce in _dividi_top_level(resto[:fine]):
        idents = RE_IDENT.findall(voce)
        if idents:
            colonne.append({"nome": idents[-1].upper(), "tipo": "", "commento": ""})
    return colonne


# --------------------------------------------------------------------------- indice
class Indice:
    """Catalogo degli oggetti e riferimenti trovati nel codice."""

    def __init__(self, radice, ignore=()):
        self.radice = Path(radice)
        self.ignore = list(ignore)
        self.testi = {}            # percorso relativo -> testo del file
        self.tipi_file = {}        # percorso relativo -> sql / shell / xml
        self.oggetti = {}          # nome -> Oggetto
        self.definito_in = {}      # percorso relativo -> nome dell'oggetto definito
        self.riferimenti = []
        self._chiavi = {}
        self._leggi_file()
        self._costruisci_catalogo()
        self._analizza()

    # ---------------------------------------------------------------- lettura
    def _ignorato(self, rel):
        return any(r.search("/" + rel) for r in self.ignore)

    def _leggi_file(self):
        for cartella in CARTELLE:
            base = self.radice / cartella
            if not base.is_dir():
                continue
            for p in sorted(base.rglob("*")):
                if not p.is_file() or p.suffix.lower() not in ESTENSIONI:
                    continue
                rel = p.relative_to(self.radice).as_posix()
                if self._ignorato(rel):
                    continue
                self.testi[rel] = p.read_text(encoding="utf-8", errors="replace")
                self.tipi_file[rel] = ESTENSIONI[p.suffix.lower()]

    # ---------------------------------------------------------------- catalogo
    def _aggiungi_oggetto(self, nome, tipo, file=None, schema=None):
        if nome not in self.oggetti:
            self.oggetti[nome] = Oggetto(nome, tipo, file, schema)
        return self.oggetti[nome]

    def _costruisci_catalogo(self):
        for rel, testo in self.testi.items():
            tipo_file = self.tipi_file[rel]
            if tipo_file == "sql":
                pulito = pulisci_sql(testo)
                for m in RE_CREATE.finditer(pulito):
                    tipo = TIPI_SQL[re.sub(r"\s+", " ", m.group(1).upper())]
                    nome = m.group(3).upper()
                    ogg = self._aggiungi_oggetto(nome, tipo, rel, (m.group(2) or "").upper() or None)
                    self.definito_in.setdefault(rel, nome)
                    if tipo == "tabella":
                        ogg.colonne = colonne_tabella(testo, nome)
                    elif tipo == "vista":
                        ogg.colonne = colonne_vista(pulito, nome)
            elif tipo_file == "shell":
                nome = Path(rel).name
                self._aggiungi_oggetto(nome, "shell", rel)
                self.definito_in[rel] = nome
            elif tipo_file == "xml":
                try:
                    radice = ET.fromstring(testo)
                except ET.ParseError:
                    continue
                wf = [w.get("NAME") for w in radice.iter("WORKFLOW") if w.get("NAME")]
                nome = wf[0] if wf else Path(rel).stem
                self._aggiungi_oggetto(nome, "workflow", rel)
                self.definito_in[rel] = nome
        self._nomi_sql = sorted(
            (n for n, o in self.oggetti.items() if o.tipo in set(TIPI_SQL.values())),
            key=len, reverse=True)
        self._re_nomi = {
            n: re.compile(rf"(?<![\w$#])(?:{IDENT}\.)?{re.escape(n)}(?![\w$#])", re.I)
            for n in self._nomi_sql}

    # ---------------------------------------------------------------- riferimenti
    def _aggiungi(self, rif):
        """Aggiunge un riferimento, unendo i campi se esiste già."""
        k = rif.chiave()
        if k in self._chiavi:
            esistente = self._chiavi[k]
            esistente.campi = sorted(set(esistente.campi) | set(rif.campi))
            if rif.riga and (not esistente.riga or rif.riga < esistente.riga):
                esistente.riga = rif.riga
            return
        rif.campi = sorted(set(rif.campi))
        self._chiavi[k] = rif
        self.riferimenti.append(rif)

    def _campi(self, nome_oggetto, identificatori):
        ogg = self.oggetti.get(nome_oggetto)
        if not ogg or not ogg.colonne:
            return []
        return [c["nome"] for c in ogg.colonne if c["nome"] in identificatori]

    def analizza_sql(self, sql, rel, tipo_file, chiamante, contesto, riga_base=1,
                     pulito=None, oggetto_definito=None):
        """Riferimenti contenuti in un testo SQL, statement per statement.
        I campi di un riferimento sono solo quelli dello stesso statement."""
        pulito = pulisci_sql(sql) if pulito is None else pulito
        for offset, stmt in spezza_statement(pulito):
            testo_stmt = sql[offset:offset + len(stmt)]
            su = stmt.upper()
            riga_stmt = riga_base + _riga(pulito, offset + len(stmt) - len(stmt.lstrip())) - 1
            if re.match(r"\s*COMMENT\s+ON\b", su):
                continue
            if RE_DINAMICO.search(stmt):
                m = RE_DINAMICO.search(stmt)
                self._aggiungi(Riferimento(rel, tipo_file, chiamante, SQL_DINAMICO, DA_VERIFICARE, [],
                                           contesto, riga_base + _riga(pulito, offset + m.start()) - 1,
                                           testo_stmt.strip()))
                continue
            mg = RE_GRANT.search(" ".join(stmt.split()))
            if mg:
                vista = mg.group(1).upper()
                for schema in re.split(r"[\s,]+", mg.group(2).strip()):
                    if schema:
                        self._aggiungi_oggetto(schema.upper(), "schema")
                        self._aggiungi(Riferimento(rel, tipo_file, schema.upper(), vista, CONSUMO, [],
                                                   contesto, riga_stmt, testo_stmt.strip()))
                continue
            alter = re.match(r"\s*ALTER\s+TABLE\b", su)
            mt = RE_ALTER_TRUNCATE.search(stmt)
            if alter and not mt:
                continue            # vincoli e modifiche di struttura: nessun flusso di dati
            creato = RE_CREATE.search(stmt)
            escludi = {creato.group(3).upper()} if creato else set()
            if oggetto_definito:
                escludi.add(oggetto_definito)
            cte = {c.upper() for c in RE_CTE.findall(stmt)}
            identificatori = {i.upper() for i in RE_IDENT.findall(stmt)}
            trovati = set()
            for nome in self._nomi_sql:
                if nome in escludi or nome in cte:
                    continue
                for m in self._re_nomi[nome].finditer(stmt):
                    prima = stmt[:m.start()]
                    if re.search(RE_SCRITTURA + r"\s*$", prima, re.I) or (mt and mt.group(1).upper() == nome):
                        direzione = SCRITTURA
                    elif self.oggetti[nome].tipo in TIPI_CHIAMABILI:
                        direzione = CHIAMATA
                    else:
                        direzione = LETTURA
                    riga = riga_base + _riga(pulito, offset + m.start()) - 1
                    self._aggiungi(Riferimento(rel, tipo_file, chiamante, nome, direzione,
                                               self._campi(nome, identificatori), contesto, riga,
                                               testo_stmt.strip()))
                    trovati.add(nome)
            # oggetti non definiti nel repository (non versionati): solo dopo le parole chiave
            for m in RE_ESTERNO.finditer(stmt):
                parola, nome = re.sub(r"\s+", " ", m.group(1).upper()), m.group(3).upper()
                if (nome in trovati or nome in escludi or nome in cte or nome in PAROLE_NON_OGGETTO
                        or nome in self.oggetti or stmt[m.end():].lstrip().startswith(".")):
                    continue
                if parola == "USING" and not re.search(r"\bMERGE\b", su):
                    continue
                direzione = LETTURA if parola in ("FROM", "JOIN", "USING") else SCRITTURA
                self._aggiungi_oggetto(nome, "esterno")
                self._aggiungi(Riferimento(rel, tipo_file, chiamante, nome, direzione, [], contesto,
                                           riga_base + _riga(pulito, offset + m.start()) - 1,
                                           testo_stmt.strip()))

    def _analizza(self):
        for rel, testo in self.testi.items():
            tipo_file = self.tipi_file[rel]
            if tipo_file == "sql":
                chiamante = self.definito_in.get(rel)
                if not chiamante:
                    chiamante = rel             # script senza CREATE (es. DATA/): il chiamante è il file
                    self._aggiungi_oggetto(rel, "script", rel)
                # un oggetto non riferisce sé stesso (es. `END nome` di un package)
                self.analizza_sql(testo, rel, tipo_file, chiamante, "STATEMENT",
                                  oggetto_definito=chiamante)
            elif tipo_file == "xml":
                self._analizza_xml(rel, testo)
        for rel in self.testi:
            if self.tipi_file[rel] == "shell":
                self._analizza_shell(rel)

    # ---------------------------------------------------------------- XML PowerCenter
    def _riga_xml(self, testo, *indizi):
        for indizio in indizi:
            if indizio:
                pos = testo.find(indizio)
                if pos >= 0:
                    return _riga(testo, pos)
        return None

    def _analizza_xml(self, rel, testo):
        try:
            radice = ET.fromstring(testo)
        except ET.ParseError:
            return
        wf = self.definito_in[rel]
        for elem, direzione, contesto, tag_campo in (("SOURCE", LETTURA, "SOURCE", "SOURCEFIELD"),
                                                     ("TARGET", SCRITTURA, "TARGET", "TARGETFIELD")):
            for e in radice.iter(elem):
                nome = (e.get("NAME") or "").upper()
                if not nome:
                    continue
                if e.get("DATABASETYPE", "").lower() == "flat file":
                    self._aggiungi_oggetto(nome, "file")
                campi = [f.get("NAME", "").upper() for f in e.iter(tag_campo)]
                self._aggiungi_oggetto(nome, "esterno") if nome not in self.oggetti else None
                self._aggiungi(Riferimento(rel, "xml", wf, nome, direzione, campi, contesto,
                                           self._riga_xml(testo, f'<{elem} NAME="{e.get("NAME")}"'),
                                           " ".join([nome] + campi)))
        for t in radice.iter("TRANSFORMATION"):
            attributi = {a.get("NAME"): a.get("VALUE") or "" for a in t.iter("TABLEATTRIBUTE")}
            if t.get("TYPE") == "Lookup Procedure":
                tabella = attributi.get("Lookup table name", "").split(".")[-1].upper()
                if tabella:
                    porte = {f.get("NAME", "").upper() for f in t.iter("TRANSFORMFIELD")}
                    campi = self._campi(tabella, porte) or sorted(porte)
                    self._aggiungi_oggetto(tabella, "esterno") if tabella not in self.oggetti else None
                    self._aggiungi(Riferimento(rel, "xml", wf, tabella, LETTURA, campi, "LOOKUP",
                                               self._riga_xml(testo, f'VALUE="{attributi["Lookup table name"]}"'),
                                               " ".join([tabella] + sorted(porte))))
        for e in radice.iter():
            nome_attr = e.get("NAME")
            contesto = {"Sql Query": "SQL_OVERRIDE", "Lookup Sql Override": "LOOKUP",
                        "Pre SQL": "PRE_SQL", "Post SQL": "POST_SQL"}.get(nome_attr)
            valore = e.get("VALUE") or ""
            if e.tag in ("ATTRIBUTE", "TABLEATTRIBUTE") and contesto and valore.strip():
                riga = self._riga_xml(testo, valore[:40].replace("'", "&apos;"), valore[:40],
                                      f'NAME="{nome_attr}"')
                self.analizza_sql(valore, rel, "xml", wf, contesto, riga or 1)

    # ---------------------------------------------------------------- shell
    def _righe_shell(self, rel):
        """Righe logiche (continuazioni con `\\` unite), senza commenti."""
        righe, corrente, inizio = [], "", None
        for n, riga in enumerate(self.testi[rel].splitlines(), 1):
            if riga.lstrip().startswith("#"):
                riga = ""
            if inizio is None:
                inizio = n
            if riga.rstrip().endswith("\\"):
                corrente += riga.rstrip()[:-1] + " "
                continue
            righe.append((inizio, corrente + riga))
            corrente, inizio = "", None
        return righe

    def _variabili_shell(self, rel):
        variabili = {}
        for _, riga in self._righe_shell(rel):
            m = re.match(r"\s*(?:local\s+|export\s+)?([A-Za-z_]\w*)=(\"([^\"]*)\"|'([^']*)'|(\S*))\s*$", riga)
            if m:
                valore = next(v for v in (m.group(3), m.group(4), m.group(5)) if v is not None)
                variabili.setdefault(m.group(1), valore)
        return variabili

    def _inclusi(self, rel):
        inclusi = []
        for n, riga in self._righe_shell(rel):
            m = re.match(r"\s*(?:\.|source)\s+.*?([\w.-]+\.(?:sh|ksh|bash))\b", riga)
            if m:
                nome = m.group(1)
                bersaglio = self.oggetti.get(nome)
                if bersaglio and bersaglio.tipo == "shell":
                    inclusi.append((n, bersaglio))
        return inclusi

    def _workflow_lanciati(self, rel, variabili):
        """Workflow lanciati con `pmcmd startworkflow`, risolvendo le variabili."""
        trovati = []
        for n, riga in self._righe_shell(rel):
            if "pmcmd" not in riga or "startworkflow" not in riga:
                continue
            try:
                token = shlex.split(riga.split("startworkflow", 1)[1], comments=False, posix=True)
            except ValueError:
                continue
            utili, salta = [], False
            for t in token:
                if salta:
                    salta = False
                    continue
                if t in (">", ">>", "2>", "&>", "<"):
                    salta = True
                    continue
                if re.match(r"^\d?[<>]", t) or t in ("|", "||", "&&", ";"):
                    if t in ("|", "||", "&&", ";"):
                        break
                    continue
                utili.append(t)
            if not utili:
                continue
            wf = re.sub(r"\$\{?(\w+)\}?", lambda m: variabili.get(m.group(1), m.group(0)), utili[-1])
            if "$" not in wf:
                trovati.append((n, wf))
        return trovati

    def _analizza_shell(self, rel):
        nome = self.definito_in[rel]
        variabili = self._variabili_shell(rel)
        for n, lib in self._inclusi(rel):
            self._aggiungi(Riferimento(rel, "shell", nome, lib.nome, CHIAMATA, [], "STATEMENT", n,
                                       f"source {lib.nome}"))
            # i workflow lanciati dalla libreria dipendono dalle variabili di chi la include
            vars_lib = dict(self._variabili_shell(lib.file))
            vars_lib.update(variabili)
            # una shell che lancia più workflow di seguito li elenca in WORKFLOWS:
            # la libreria li lancia uno alla volta, ognuno come WORKFLOW
            for nome_wf in variabili.get("WORKFLOWS", "").split() or [None]:
                vars_wf = dict(vars_lib)
                if nome_wf:
                    vars_wf["WORKFLOW"] = nome_wf
                for _, wf in self._workflow_lanciati(lib.file, vars_wf):
                    self._aggiungi_oggetto(wf, "workflow")
                    self._aggiungi(Riferimento(rel, "shell", nome, wf, CHIAMATA, [], "STATEMENT", n,
                                               f"pmcmd startworkflow {wf} (tramite {lib.nome})"))
        for n, wf in self._workflow_lanciati(rel, variabili):
            self._aggiungi_oggetto(wf, "workflow")
            self._aggiungi(Riferimento(rel, "shell", nome, wf, CHIAMATA, [], "STATEMENT", n,
                                       f"pmcmd startworkflow {wf}"))
        for n, riga in self._righe_shell(rel):
            if not riga.strip():
                continue
            if re.search(rf"\b(FROM|JOIN|INTO|UPDATE|TABLE)\s+(?:{IDENT}\.)?\$\{{?\w+", riga, re.I):
                self._aggiungi(Riferimento(rel, "shell", nome, SQL_DINAMICO, DA_VERIFICARE, [],
                                           "STATEMENT", n, riga.strip()))
                continue
            # SQL eseguito inline (sqlplus, heredoc, funzioni che lo passano a sqlplus)
            self.analizza_sql(riga, rel, "shell", nome, "STATEMENT", riga_base=n)

    # ---------------------------------------------------------------- interrogazioni
    def riferimenti_a(self, nome):
        return [r for r in self.riferimenti if r.oggetto_riferito == nome]

    def riferimenti_da(self, nome):
        return [r for r in self.riferimenti if r.oggetto_chiamante == nome]

    def da_verificare(self):
        return [r for r in self.riferimenti if r.direzione == DA_VERIFICARE]


def costruisci(radice, ignore=()):
    """Legge i file una volta sola e restituisce l'indice."""
    return Indice(radice, ignore)
