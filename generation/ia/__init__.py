"""Point d'accroche optionnel pour une IA générative — DÉSACTIVÉ par défaut.

Aucune partie de la génération n'en dépend : les PDF sont produits uniquement par
des algorithmes déterministes. Voir generation/ia/README.md.
"""
from __future__ import annotations

import json
import os
import urllib.request

ACTIVE = os.environ.get("PAD_IA_ACTIVE") == "1"


def proposer(consigne: str, contexte: str = "") -> str | None:
    """Renvoie une proposition de texte (thème, consigne, description) ou None.

    Ne fait rien tant que PAD_IA_ACTIVE=1 et ANTHROPIC_API_KEY ne sont pas définis.
    Toute proposition doit être relue par un humain avant d'être copiée dans
    generation/templates/*.json : elle n'est jamais injectée directement dans un PDF.
    """
    cle = os.environ.get("ANTHROPIC_API_KEY")
    if not (ACTIVE and cle):
        return None
    corps = json.dumps({
        "model": os.environ.get("PAD_IA_MODELE", "claude-sonnet-4-5"),
        "max_tokens": 600,
        "messages": [{"role": "user", "content": f"{contexte}\n\n{consigne}".strip()}],
    }).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=corps, headers={
        "x-api-key": cle, "anthropic-version": "2023-06-01", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        rep = json.load(r)
    return "".join(b.get("text", "") for b in rep.get("content", []))
