"""Test sul repository vero e sul modello a due livelli."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import config
import genera_schede
import grafo
import scanner

RADICE = Path(__file__).resolve().parents[3]
SCHEDE = RADICE / "docs" / "oggetti"
AVVISO = genera_schede.AVVISO_NOTA


def git(*argomenti, cwd=RADICE):
    esito = subprocess.run(["git", *argomenti], cwd=cwd, capture_output=True, text=True)
    # Solo il fine riga: uno strip() completo toglie lo spazio iniziale della
    # prima riga di `git status --porcelain` (" D percorso") e ne sposta le colonne
    return esito.stdout.rstrip() if esito.returncode == 0 else None


def storia_completa():
    """Vero se il repository ha una storia utilizzabile per l'avviso sulle note
    (nel front pubblico, ricreato con un solo commit, non ce l'ha)."""
    conta = git("rev-list", "--count", "HEAD")
    return conta is not None and int(conta) > 1 and git("rev-parse", "--is-shallow-repository") == "false"


class TestCatenaReale(unittest.TestCase):
    """Catena ricavata leggendo il codice:
    DC_STG_MOVIMENTI è la SOURCE di wf_DC_MOVIMENTI, che ha come TARGET
    DC_FT_MOVIMENTI; la vista DC_VC_VOLUMI_GIORNALIERI legge DC_FT_MOVIMENTI
    ed è concessa con GRANT allo schema APP_REPORTING."""

    @classmethod
    def setUpClass(cls):
        cls.indice = scanner.costruisci(RADICE, config.carica()["ignore"])
        cls.grafo = grafo.Grafo(cls.indice)
        cls.impatti = cls.grafo.impatti("DC_STG_MOVIMENTI")

    def test_catena_staging_workflow_fatti_vista_consumatore(self):
        wf = self.impatti["wf_DC_MOVIMENTI"]
        self.assertEqual((wf.livello, wf.ruolo), (1, "legge"))
        self.assertEqual([r.contesto for r in wf.riferimenti], ["SOURCE", "SQL_OVERRIDE"])
        fatti = self.impatti["DC_FT_MOVIMENTI"]
        self.assertEqual((fatti.livello, fatti.ruolo, fatti.da), (2, "è scritto da", "wf_DC_MOVIMENTI"))
        vista = self.impatti["DC_VC_VOLUMI_GIORNALIERI"]
        self.assertEqual((vista.livello, vista.ruolo, vista.da), (3, "legge", "DC_FT_MOVIMENTI"))
        consumi = {r.oggetto_chiamante for r in self.grafo.entranti("DC_VC_VOLUMI_GIORNALIERI", "CONSUMO")}
        self.assertIn("APP_REPORTING", consumi)
        self.assertIn("APP_REPORTING", self.impatti)

    def test_saldi_leggono_i_movimenti_con_query_di_override(self):
        wf = self.impatti["wf_DC_SALDI"]
        self.assertEqual(wf.livello, 3)
        self.assertEqual([r.contesto for r in wf.riferimenti], ["SOURCE", "SQL_OVERRIDE"])
        saldi = self.impatti["DC_FT_SALDI_MENSILI"]
        self.assertEqual((saldi.livello, saldi.ruolo, saldi.da), (4, "è scritto da", "wf_DC_SALDI"))

    def test_lookup_sulla_causale(self):
        # la lookup con override sta in wf_DC_MOVIMENTI e legge il segno della causale
        impatti = self.grafo.impatti("DC_DIM_CAUSALE", r"\bCOD_SEGNO\b")
        wf = impatti["wf_DC_MOVIMENTI"]
        self.assertEqual(wf.livello, 1)
        self.assertIn("LOOKUP", [r.contesto for r in wf.riferimenti])

    def test_post_sql_del_carico(self):
        # la Post SQL del carico riscrive COD_CAUSALE nello staging
        rif = [r for r in self.grafo.entranti("DC_STG_MOVIMENTI")
               if r.oggetto_chiamante == "wf_DC_CARICO_MOVIMENTI"]
        self.assertIn("POST_SQL", {r.contesto for r in rif})

    def test_vista_con_grant_verso_due_consumatori(self):
        consumi = {r.oggetto_chiamante for r in self.grafo.entranti("DC_VC_QUADRATURA", "CONSUMO")}
        self.assertEqual(consumi, {"APP_REPORTING", "UTENTI_CONTI"})

    def test_shell_chiama_package_tramite_libreria(self):
        chiamanti = {r.oggetto_chiamante for r in self.grafo.entranti("DC_PKG_ELABORAZIONE", "CHIAMATA")}
        self.assertEqual(chiamanti, {"dc_comune.sh"})
        impatti = self.grafo.impatti("DC_PKG_ELABORAZIONE")
        self.assertEqual(impatti["lancia_dc_movimenti.sh"].livello, 2)

    def test_falso_positivo_reale(self):
        # DAT_RIFERIMENTO esiste in DC_LOG_ELABORAZIONI e in DC_CTL_SEMAFORO:
        # la procedura di pulizia lo usa solo sul semaforo
        impatti = self.grafo.impatti("DC_LOG_ELABORAZIONI", r"\bDAT_RIFERIMENTO\b")
        self.assertNotIn("DC_PRC_PULIZIA_STORICO", impatti)
        self.assertIn("DC_PKG_ELABORAZIONE", impatti)

    def test_sql_dinamico_da_verificare(self):
        dinamici = {r.oggetto_chiamante for r in self.indice.da_verificare()}
        self.assertEqual(dinamici, {"DC_PRC_PULIZIA_STORICO"})


class TestSecondoMotoreReale(unittest.TestCase):
    """DEMO_INVESTIMENTI: DI_STG_ORDINI è la SOURCE di wf_DI_POSIZIONI, che scrive
    DI_FT_POSIZIONI e DI_FT_CONTROVALORI_MENSILI; la vista DI_VC_QUADRATURA legge
    DI_FT_POSIZIONI. Semaforo, log e package sono di DEMO_CONTI e li usano entrambi."""

    @classmethod
    def setUpClass(cls):
        cls.cfg = config.carica()
        cls.indice = scanner.costruisci(RADICE, cls.cfg["ignore"])
        cls.grafo = grafo.Grafo(cls.indice)
        cls.impatti = cls.grafo.impatti("DI_STG_ORDINI")

    def test_catena_ordini_workflow_posizioni_vista_consumatori(self):
        wf = self.impatti["wf_DI_POSIZIONI"]
        self.assertEqual((wf.livello, wf.ruolo), (1, "legge"))
        self.assertEqual([r.contesto for r in wf.riferimenti], ["SOURCE", "SQL_OVERRIDE"])
        for scritta in ("DI_FT_POSIZIONI", "DI_FT_CONTROVALORI_MENSILI"):
            t = self.impatti[scritta]
            self.assertEqual((t.livello, t.ruolo, t.da), (2, "è scritto da", "wf_DI_POSIZIONI"), scritta)
        vista = self.impatti["DI_VC_QUADRATURA"]
        self.assertEqual((vista.livello, vista.ruolo, vista.da), (3, "legge", "DI_FT_POSIZIONI"))
        consumi = {r.oggetto_chiamante for r in self.grafo.entranti("DI_VC_QUADRATURA", "CONSUMO")}
        self.assertEqual(consumi, {"APP_REPORTING", "UTENTI_INVESTIMENTI"})

    def test_lookup_sul_titolo(self):
        impatti = self.grafo.impatti("DI_DIM_TITOLO", r"\bCOD_TIPO\b")
        self.assertEqual(impatti["wf_DI_POSIZIONI"].livello, 1)
        self.assertIn("LOOKUP", [r.contesto for r in impatti["wf_DI_POSIZIONI"].riferimenti])

    def test_post_sql_del_carico_prezzi(self):
        contesti = {r.contesto for r in self.grafo.entranti("DI_STG_PREZZI")
                    if r.oggetto_chiamante == "wf_DI_CARICO_PREZZI"}
        self.assertEqual(contesti, {"TARGET", "POST_SQL"})

    def test_shell_lancia_due_workflow_tramite_elenco(self):
        # lancia_di_carico.sh elenca i workflow in WORKFLOWS: la scheda li deve trovare entrambi
        for wf in ("wf_DI_CARICO_ORDINI", "wf_DI_CARICO_PREZZI"):
            chiamanti = {r.oggetto_chiamante for r in self.grafo.entranti(wf, "CHIAMATA")}
            self.assertEqual(chiamanti, {"lancia_di_carico.sh"}, wf)
        self.assertEqual({r.oggetto_chiamante for r in self.grafo.entranti("wf_DI_POSIZIONI", "CHIAMATA")},
                         {"lancia_di_posizioni.sh"})
        # e le shell di DEMO_CONTI hanno mantenuto il loro workflow
        self.assertEqual({r.oggetto_chiamante for r in self.grafo.entranti("wf_DC_MOVIMENTI", "CHIAMATA")},
                         {"lancia_dc_movimenti.sh"})

    def test_movimenti_dei_conti_impattano_la_vista_degli_investimenti(self):
        # DI_VC_REGOLAMENTO_ORDINI (DEMO_INVESTIMENTI) legge DC_FT_MOVIMENTI (DEMO_CONTI):
        # cambiare i movimenti ha un impatto anche nell'altro motore
        aree = self.cfg["aree"]
        impatti = self.grafo.impatti("DC_FT_MOVIMENTI")
        vista = impatti["DI_VC_REGOLAMENTO_ORDINI"]
        self.assertEqual((vista.livello, vista.ruolo, vista.da), (1, "legge", "DC_FT_MOVIMENTI"))
        self.assertEqual(graf_motore(self.indice, "DC_FT_MOVIMENTI", aree), "DEMO_CONTI")
        self.assertEqual(graf_motore(self.indice, "DI_VC_REGOLAMENTO_ORDINI", aree), "DEMO_INVESTIMENTI")
        motori = {graf_motore(self.indice, n, aree) for n in impatti} - {None}
        self.assertEqual(motori, {"DEMO_CONTI", "DEMO_INVESTIMENTI"})
        # la vista legge anche ordini e titoli di DEMO_INVESTIMENTI, e ha il suo consumatore
        for letta in ("DI_STG_ORDINI", "DI_DIM_TITOLO"):
            self.assertIn("DI_VC_REGOLAMENTO_ORDINI", self.grafo.impatti(letta), letta)
        consumi = {r.oggetto_chiamante for r in self.grafo.entranti("DI_VC_REGOLAMENTO_ORDINI", "CONSUMO")}
        self.assertEqual(consumi, {"APP_CONTROLLO_TITOLI"})

    def test_oggetto_condiviso_impattato_da_entrambi_i_motori(self):
        aree = self.cfg["aree"]
        for condiviso in ("DC_PKG_ELABORAZIONE", "DC_CTL_SEMAFORO", "DC_FN_SEMAFORO"):
            self.assertEqual(graf_motore(self.indice, condiviso, aree), "DEMO_CONTI", condiviso)
            impatti = self.grafo.impatti(condiviso)
            motori = {graf_motore(self.indice, n, aree) for n in impatti} - {None}
            self.assertEqual(motori, {"DEMO_CONTI", "DEMO_INVESTIMENTI"}, condiviso)
        # anche il log è di DEMO_CONTI: lo scrive il package, quindi lo usano entrambi i motori
        self.assertEqual(graf_motore(self.indice, "DC_LOG_ELABORAZIONI", aree), "DEMO_CONTI")
        self.assertIn("DC_PKG_ELABORAZIONE", self.grafo.impatti("DC_LOG_ELABORAZIONI"))
        impatti = self.grafo.impatti("DC_PKG_ELABORAZIONE")
        for shell in ("lancia_dc_movimenti.sh", "lancia_di_posizioni.sh", "lancia_di_carico.sh"):
            self.assertIn(shell, impatti)
        # la libreria condivisa resta di DEMO_CONTI, anche se la include DEMO_INVESTIMENTI
        chiamanti = {r.oggetto_chiamante for r in self.grafo.entranti("dc_comune.sh", "CHIAMATA")}
        self.assertTrue({"lancia_dc_saldi.sh", "lancia_di_carico.sh", "lancia_di_posizioni.sh"} <= chiamanti)


def graf_motore(indice, nome, aree):
    """Motore di un oggetto, con la stessa regola delle schede (None se non è di un motore)."""
    ogg = indice.oggetti.get(nome)
    return genera_schede.motore(ogg, aree) if ogg else None


def stato_fuori_da_schede():
    """Righe di `git status` che riguardano file fuori da docs/oggetti/."""
    stato = git("status", "--porcelain", "--untracked-files=all")
    if stato is None:
        return None
    return sorted(r for r in stato.splitlines() if r[3:] and not r[3:].startswith("docs/oggetti/"))


class TestModelloDueLivelli(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cfg = config.carica()
        cls.indice = scanner.costruisci(RADICE, cfg["ignore"])
        # confronto prima/dopo: il test vale anche con modifiche in corso nell'albero di lavoro
        cls.stato_prima = stato_fuori_da_schede()
        genera_schede.genera(cls.indice, grafo.Grafo(cls.indice), cfg, RADICE)
        cls.stato_dopo = stato_fuori_da_schede()

    def test_nessun_file_modificato_fuori_da_docs_oggetti(self):
        if self.stato_prima is None:
            self.skipTest("git non disponibile")
        self.assertEqual(self.stato_dopo, self.stato_prima,
                         "il generatore ha scritto fuori da docs/oggetti/")

    def test_note_copiate_identiche(self):
        controllate = 0
        for ogg in self.indice.oggetti.values():
            if not genera_schede.ha_scheda(ogg):
                continue
            nota = RADICE / Path(ogg.file).with_suffix(".md")
            if nota.is_file():
                scheda = (SCHEDE / f"{genera_schede.slug(ogg)}.md").read_text(encoding="utf-8")
                self.assertIn(nota.read_text(encoding="utf-8").rstrip("\n"), scheda, ogg.nome)
                controllate += 1
        self.assertGreater(controllate, 0)

    def test_scheda_dei_movimenti_mostra_la_vista_dell_altro_motore(self):
        scheda = (SCHEDE / "DC_FT_MOVIMENTI.md").read_text(encoding="utf-8")
        self.assertIn("DI_VC_REGOLAMENTO_ORDINI", scheda)
        self.assertIn("DI_VC_REGOLAMENTO_ORDINI", (SCHEDE / "DI_STG_ORDINI.md").read_text(encoding="utf-8"))

    def test_avviso_solo_nel_caso_preparato(self):
        if not storia_completa():
            self.skipTest("storia Git minima: l'avviso non può comparire")
        con_avviso = sorted(p.stem for p in SCHEDE.glob("*.md") if AVVISO in p.read_text(encoding="utf-8"))
        self.assertEqual(con_avviso, ["DC_STG_MOVIMENTI"])


    @staticmethod
    def _front_matter(percorso):
        campi = {}
        righe = percorso.read_text(encoding="utf-8").splitlines()
        if righe and righe[0] == "---":
            for riga in righe[1:]:
                if riga == "---":
                    break
                chiave, _, valore = riga.partition(":")
                campi[chiave.strip()] = valore.strip()
        return campi

    def test_menu_a_due_motori_con_le_stesse_categorie(self):
        categorie = {"Tabelle", "Viste di controllo", "Package e funzioni", "Shell e Workflow"}
        pagine = {}
        for motore_ in ("DEMO_CONTI", "DEMO_INVESTIMENTI"):
            fm = self._front_matter(RADICE / "docs" / f"{motore_}.md")
            self.assertEqual((fm["title"], fm["has_children"]), (motore_, "true"))
            titoli = set()
            for pagina in (RADICE / "docs" / motore_).glob("*.md"):
                fm = self._front_matter(pagina)
                self.assertEqual(fm["parent"], motore_, pagina.name)
                titoli.add(fm["title"])
            pagine[motore_] = titoli
            self.assertEqual(titoli, categorie, motore_)
        # i titoli delle categorie sono uguali nei due motori: le schede si distinguono
        # perché portano parent (categoria) e grand_parent (motore)
        triple = []
        for scheda in SCHEDE.glob("*.md"):
            fm = self._front_matter(scheda)
            if "grand_parent" in fm:
                self.assertIn(fm["parent"], categorie, scheda.name)
                self.assertIn(fm["grand_parent"], pagine, scheda.name)
                triple.append((fm["title"], fm["parent"], fm["grand_parent"]))
        self.assertEqual(len(triple), len(set(triple)))
        self.assertEqual({t[2] for t in triple}, {"DEMO_CONTI", "DEMO_INVESTIMENTI"})
        # una scheda di oggetto condiviso sta sotto il motore che lo definisce
        fm = self._front_matter(SCHEDE / "DC_PKG_ELABORAZIONE.md")
        self.assertEqual((fm["parent"], fm["grand_parent"]), ("Package e funzioni", "DEMO_CONTI"))
        fm = self._front_matter(SCHEDE / "lancia_di_carico.md")
        self.assertEqual((fm["parent"], fm["grand_parent"]), ("Shell e Workflow", "DEMO_INVESTIMENTI"))


class TestStoriaMinima(unittest.TestCase):
    """Il front pubblico nasce con un solo commit: niente errori, niente avvisi."""

    def test_un_solo_commit(self):
        if git("--version") is None:
            self.skipTest("git non disponibile")
        with tempfile.TemporaryDirectory() as tmp:
            radice = Path(tmp)
            shutil.copytree(Path(__file__).parent / "fixtures", radice, dirs_exist_ok=True)
            (radice / "sql/PROVA/TABLES/T_A.md").write_text("### Perché\n\nNota di prova.\n", encoding="utf-8")
            git("init", "-q", cwd=radice)
            git("add", ".", cwd=radice)
            git("-c", "user.name=prova", "-c", "user.email=prova@example.invalid",
                "commit", "-q", "-m", "unico commit", cwd=radice)
            cfg = config.carica(radice / "prova.cfg.py")
            indice = scanner.costruisci(radice, cfg["ignore"])
            esito = genera_schede.genera(indice, grafo.Grafo(indice), cfg, radice)
            self.assertEqual(esito["avvisi"], 0)
            scheda = (radice / "docs/oggetti/T_A.md").read_text(encoding="utf-8")
            self.assertIn("Nota di prova.", scheda)
            self.assertNotIn(AVVISO, scheda)

    def test_senza_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            radice = Path(tmp)
            shutil.copytree(Path(__file__).parent / "fixtures", radice, dirs_exist_ok=True)
            cfg = config.carica(radice / "prova.cfg.py")
            indice = scanner.costruisci(radice, cfg["ignore"])
            esito = genera_schede.genera(indice, grafo.Grafo(indice), cfg, radice)
            self.assertEqual(esito["avvisi"], 0)
            self.assertIn("non disponibile", (radice / "docs/oggetti/index.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
