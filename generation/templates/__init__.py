"""Gabarits de textes (consignes, missions, histoires) au format JSON."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def charger(nom: str) -> dict:
    with open(DOSSIER / f"{nom}.json", encoding="utf-8") as f:
        return json.load(f)
