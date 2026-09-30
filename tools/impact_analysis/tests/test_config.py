"""Il file di configurazione non viene eseguito."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import config


class TestConfig(unittest.TestCase):
    def _scrivi(self, testo):
        f = tempfile.NamedTemporaryFile("w", suffix=".cfg.py", delete=False, encoding="utf-8")
        f.write(testo)
        f.close()
        self.addCleanup(Path(f.name).unlink)
        return f.name

    def test_non_esegue_codice(self):
        percorso = self._scrivi(
            'print("ESEGUITO")\n'
            'import os\n'
            'patterns=[{"words": [], "table_name": "\\\\bT_A\\\\b", "field_name": None}]\n')
        uscita = io.StringIO()
        with redirect_stdout(uscita):
            cfg = config.carica(percorso)
        self.assertEqual(uscita.getvalue(), "")
        self.assertEqual(cfg["patterns"][0]["table_name"], r"\bT_A\b")

    def test_rifiuta_espressioni(self):
        percorso = self._scrivi('patterns=[{"table_name": "A" + "B"}]\n')
        with self.assertRaises(config.ConfigError):
            config.carica(percorso)

    def test_default_compatibile(self):
        cfg = config.carica()
        self.assertTrue(cfg["patterns"])
        for p in cfg["patterns"]:
            self.assertEqual(set(p), {"table_name", "field_name", "words"})


if __name__ == "__main__":
    unittest.main()
