"""Falso positivo dell'approccio originale: la v2 non lo segnala, --compatibile sì."""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import compat
import config
import grafo
import impact_analysis
import scanner

FIXTURES = Path(__file__).parent / "fixtures"
PKG = "sql/PROVA/PACKAGES/PKG_X.sql"


class TestFalsoPositivo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg = config.carica(FIXTURES / "prova.cfg.py")
        cls.pattern = cls.cfg["patterns"][0]          # T_A / DATA_RIF
        cls.indice = scanner.costruisci(FIXTURES)
        cls.grafo = grafo.Grafo(cls.indice)

    def test_originale_segnala_il_package(self):
        # PKG_X contiene sia T_A sia DATA_RIF, ma DATA_RIF è usato su T_B
        file = [rel for rel, _ in compat.file_impattati(self.indice, self.pattern)]
        self.assertIn(PKG, file)

    def test_v2_non_segnala_il_package(self):
        impatti = self.grafo.impatti("T_A", self.pattern["field_name"])
        self.assertNotIn("PKG_X", impatti)

    def test_v2_senza_campo_vede_il_package(self):
        # senza filtro sul campo PKG_X scrive davvero T_A
        self.assertEqual(self.grafo.impatti("T_A")["PKG_X"].ruolo, "scrive")

    def test_originale_ignora_target_lookup_pre_post(self):
        pattern = {"table_name": r"\bT_C\b", "field_name": r"\bID\b", "words": []}
        file = [rel for rel, _ in compat.file_impattati(self.indice, pattern)]
        self.assertNotIn("powercenter/PROVA/wf_X.xml", file)
        self.assertIn("wf_X", self.grafo.impatti("T_C", r"\bID\b"))

    def test_formato_compatibile(self):
        uscita = io.StringIO()
        with redirect_stdout(uscita):
            impact_analysis.main([str(FIXTURES / "prova.cfg.py"), "--compatibile", "--radice", str(FIXTURES)])
        righe = uscita.getvalue().splitlines()
        self.assertTrue(righe[0].endswith("ANALISI D'IMPATTO"))
        self.assertTrue(righe[1].startswith("####PATTERN {"))
        self.assertIn(PKG, righe)
        self.assertIn("ANALISI D'IMPATTO terminata", righe)
        self.assertIn(f"  + {PKG}", righe)          # nel confronto: segnalato in più dall'originale

    def test_grants_delle_viste(self):
        pattern = {"table_name": r"\bT_C\b", "field_name": None, "words": []}
        righe = compat.formatta(self.indice, [pattern])
        self.assertIn("sql/PROVA/VIEWS/V_A.sql grants[SCHEMA_X, SCHEMA_Y]", righe)


if __name__ == "__main__":
    unittest.main()
