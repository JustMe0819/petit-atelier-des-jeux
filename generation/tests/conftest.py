import sys
from pathlib import Path

# Permet de lancer « pytest generation/tests » depuis la racine du dépôt.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
