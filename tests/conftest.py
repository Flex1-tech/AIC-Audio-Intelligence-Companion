"""
tests/conftest.py
------------------
Configuration pytest : s'assure que le répertoire racine du projet
est présent dans sys.path pour tous les tests.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
