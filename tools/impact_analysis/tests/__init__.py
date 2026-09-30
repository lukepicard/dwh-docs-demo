"""Test dell'analisi d'impatto. Si lanciano dalla radice del repository con

    python -m unittest
"""

import sys
from pathlib import Path

# i moduli dello strumento si importano per nome, come fa la riga di comando
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
