"""Grafo delle dipendenze e analisi degli impatti a catena.

Il grafo segue il flusso dei dati: chi scrive → oggetto → chi legge.
Si aggiungono le chiamate (shell → package, shell → workflow) e i consumi
(vista → schema consumatore).

`impatti(oggetto, campo)` risponde alla domanda "se cambio questo oggetto (o
questo campo), cosa devo controllare?":
- livello 1: chi lo scrive, chi lo legge, chi lo chiama, chi lo consuma e, se
  l'oggetto è a sua volta un programma, cosa scrive;
- livelli successivi: si prosegue a valle, cioè verso gli oggetti scritti da chi
  legge, verso chi legge quegli oggetti, verso chi chiama un programma impattato,
  e così via.
Chi scrive l'oggetto è impattato (deve rispettarne la struttura) ma non si
prosegue da lui: il suo "a valle" è l'oggetto stesso.
"""

import re
from dataclasses import dataclass, field

from scanner import CHIAMATA, CONSUMO, LETTURA, SCRITTURA

# ruolo dell'oggetto impattato rispetto a quello da cui è stato raggiunto
RUOLI = {
    SCRITTURA: "scrive",
    LETTURA: "legge",
    CHIAMATA: "chiama",
    CONSUMO: "consuma",
    "SCRITTO": "è scritto da",
}


@dataclass
class Impatto:
    oggetto: str
    livello: int
    ruolo: str                    # scrive / legge / chiama / consuma / è scritto da
    da: str                       # oggetto da cui è stato raggiunto
    riferimenti: list = field(default_factory=list)


def _filtra(riferimenti, campo=None, words=()):
    """Tiene i riferimenti che citano il campo e che contengono tutte le regex
    `words` nel proprio contesto (lo statement, non tutto il file)."""
    re_campo = re.compile(campo, re.I) if campo else None
    re_words = [re.compile(w, re.I) for w in words]
    risultato = []
    for r in riferimenti:
        if re_campo and not any(re_campo.search(c) for c in r.campi):
            continue
        if not all(w.search(r.testo) for w in re_words):
            continue
        risultato.append(r)
    return risultato


class Grafo:
    def __init__(self, indice):
        self.indice = indice
        self._entranti = {}      # oggetto riferito -> riferimenti
        self._uscenti = {}       # oggetto chiamante -> riferimenti
        for r in indice.riferimenti:
            self._entranti.setdefault(r.oggetto_riferito, []).append(r)
            self._uscenti.setdefault(r.oggetto_chiamante, []).append(r)

    def entranti(self, oggetto, direzione=None):
        return [r for r in self._entranti.get(oggetto, [])
                if direzione is None or r.direzione == direzione]

    def uscenti(self, oggetto, direzione=None):
        return [r for r in self._uscenti.get(oggetto, [])
                if direzione is None or r.direzione == direzione]

    def _vicini(self, nodo, campo=None, words=()):
        """Oggetti raggiunti da `nodo` andando a valle, con ruolo e riferimenti."""
        vicini = []
        for r in _filtra(self.entranti(nodo), campo, words):
            if r.direzione in (LETTURA, CHIAMATA, CONSUMO):
                vicini.append((r.oggetto_chiamante, RUOLI[r.direzione], r))
        for r in self.uscenti(nodo, SCRITTURA):
            vicini.append((r.oggetto_riferito, RUOLI["SCRITTO"], r))
        return vicini

    def impatti(self, oggetto, campo=None, words=()):
        """Impatti di un oggetto (o di un suo campo), per livello.

        Restituisce un dizionario oggetto -> Impatto. Ogni oggetto compare una
        sola volta, al livello più basso in cui viene raggiunto: questo
        protegge anche dai cicli."""
        risultato = {}

        def registra(nome, livello, ruolo, da, rif):
            if nome == oggetto:
                return False
            if nome in risultato:
                imp = risultato[nome]
                if imp.livello == livello and rif not in imp.riferimenti:
                    imp.riferimenti.append(rif)
                return False
            risultato[nome] = Impatto(nome, livello, ruolo, da, [rif])
            return True

        # livello 1: chi scrive l'oggetto (non si prosegue da lui)
        for r in _filtra(self.entranti(oggetto, SCRITTURA), campo, words):
            registra(r.oggetto_chiamante, 1, RUOLI[SCRITTURA], oggetto, r)

        frontiera, livello = [oggetto], 0
        while frontiera:
            livello += 1
            nuova = []
            for nodo in frontiera:
                filtro_campo = campo if nodo == oggetto else None
                filtro_words = words if nodo == oggetto else ()
                for nome, ruolo, rif in self._vicini(nodo, filtro_campo, filtro_words):
                    if registra(nome, livello, ruolo, nodo, rif):
                        nuova.append(nome)
            frontiera = sorted(set(nuova))
        return risultato

    def archi(self, nodi):
        """Archi del grafo tra i nodi indicati, nel verso del flusso:
        (da, a, etichetta)."""
        nodi = set(nodi)
        archi = set()
        for r in self.indice.riferimenti:
            a, b = r.oggetto_chiamante, r.oggetto_riferito
            if a not in nodi or b not in nodi:
                continue
            if r.direzione == SCRITTURA:
                archi.add((a, b, "scrive"))
            elif r.direzione == LETTURA:
                archi.add((b, a, "letto da"))
            elif r.direzione == CHIAMATA:
                archi.add((a, b, "chiama"))
            elif r.direzione == CONSUMO:
                archi.add((b, a, "consumata da"))
        return sorted(archi)
