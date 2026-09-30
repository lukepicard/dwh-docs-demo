"""Regole dello scanner su file di prova minimi, con risultati attesi scritti a mano."""

import unittest
from pathlib import Path

import scanner

FIXTURES = Path(__file__).parent / "fixtures"

# (chiamante, riferito, direzione, contesto, campi) attesi, ricavati leggendo i file di prova
ATTESI = {
    ("PKG_X", scanner.SQL_DINAMICO, "DA_VERIFICARE", "STATEMENT", ()),
    ("PKG_X", "T_A", "SCRITTURA", "STATEMENT", ("IMPORTO",)),
    ("PKG_X", "T_B", "SCRITTURA", "STATEMENT", ("DATA_RIF", "STATO")),
    ("SCHEMA_X", "V_A", "CONSUMO", "STATEMENT", ()),
    ("SCHEMA_Y", "V_A", "CONSUMO", "STATEMENT", ()),
    ("V_A", "T_C", "LETTURA", "STATEMENT", ("ID", "IMPORTO")),
    ("lancia_x.sh", "PKG_X", "CHIAMATA", "STATEMENT", ()),
    ("lancia_x.sh", "T_C", "SCRITTURA", "STATEMENT", ()),
    ("lancia_x.sh", "lib.sh", "CHIAMATA", "STATEMENT", ()),
    ("lancia_x.sh", "wf_X", "CHIAMATA", "STATEMENT", ()),
    ("wf_X", "T_A", "LETTURA", "SOURCE", ("ID", "IMPORTO")),
    ("wf_X", "T_A", "LETTURA", "SQL_OVERRIDE", ("ID", "IMPORTO")),
    ("wf_X", "T_B", "LETTURA", "LOOKUP", ("ID", "STATO")),
    ("wf_X", "T_B", "SCRITTURA", "POST_SQL", ("STATO",)),
    ("wf_X", "T_C", "SCRITTURA", "PRE_SQL", ("ID",)),
    ("wf_X", "T_C", "SCRITTURA", "TARGET", ("ID", "IMPORTO")),
}


class TestScanner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.indice = scanner.costruisci(FIXTURES)

    def test_riferimenti_attesi(self):
        trovati = {(r.oggetto_chiamante, r.oggetto_riferito, r.direzione, r.contesto, tuple(r.campi))
                   for r in self.indice.riferimenti}
        self.assertEqual(trovati, ATTESI)

    def test_catalogo(self):
        tipi = {n: o.tipo for n, o in self.indice.oggetti.items()}
        for nome, tipo in [("T_A", "tabella"), ("V_A", "vista"), ("PKG_X", "package"),
                           ("lancia_x.sh", "shell"), ("lib.sh", "shell"), ("wf_X", "workflow"),
                           ("SCHEMA_X", "schema")]:
            self.assertEqual(tipi.get(nome), tipo, nome)
        self.assertEqual([c["nome"] for c in self.indice.oggetti["V_A"].colonne], ["ID", "IMPORTO_TOTALE"])

    def test_commenti_e_stringhe_ignorati(self):
        # PKG_X cita T_C solo in un commento e in una stringa: nessun riferimento
        self.assertFalse([r for r in self.indice.riferimenti
                          if r.oggetto_chiamante == "PKG_X" and r.oggetto_riferito == "T_C"])
        # la shell cita T_A solo in un commento
        self.assertFalse([r for r in self.indice.riferimenti
                          if r.oggetto_chiamante == "lancia_x.sh" and r.oggetto_riferito == "T_A"])

    def test_workflow_di_una_libreria_non_risolto_da_sola(self):
        # lib.sh lancia "${WORKFLOW}": il nome lo sa solo chi la include
        self.assertFalse([r for r in self.indice.riferimenti if r.oggetto_chiamante == "lib.sh"])

    def test_pulisci_sql_conserva_le_righe(self):
        sql = "SELECT 'a;b' -- commento\nFROM /* x\ny */ T"
        pulito = scanner.pulisci_sql(sql)
        self.assertEqual(pulito.count("\n"), sql.count("\n"))
        self.assertNotIn("commento", pulito)
        self.assertNotIn("a;b", pulito)
        self.assertEqual(len(scanner.spezza_statement(pulito)), 1)


if __name__ == "__main__":
    unittest.main()
