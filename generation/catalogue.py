"""Lecture / mise à jour du catalogue partagé (catalogue/catalogue.json).

Seuls les champs autorisés sont modifiés : fichiers, contenu, apercus, qa, statut (par produit)
et gratuits (au niveau racine). Le statut n'est JAMAIS passé à « publie » ici : la publication
est une décision humaine. Le format d'écriture reproduit celui du fichier d'origine
(indentation de 2 espaces, objets « feuilles » sur une seule ligne, UTF-8 sans échappement).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from generation.config import CATALOGUE

CHAMPS_PRODUIT_MODIFIABLES = {"fichiers", "contenu", "apercus", "qa", "statut"}
STATUTS_AUTORISES = {"brouillon", "en_verification"}


def _scalaire(v: Any) -> str:
    return json.dumps(v, ensure_ascii=False)


def _feuille(v: Any) -> bool:
    if isinstance(v, dict):
        return all(not isinstance(x, (dict, list)) for x in v.values())
    if isinstance(v, list):
        return all(not isinstance(x, (dict, list)) for x in v)
    return True


def formater(v: Any, niveau: int = 0) -> str:
    ind = "  " * niveau
    ind2 = "  " * (niveau + 1)
    if isinstance(v, dict):
        if not v:
            return "{}"
        if niveau > 0 and _feuille(v):
            return "{ " + ", ".join(f"{_scalaire(k)}: {_scalaire(x)}" for k, x in v.items()) + " }"
        lignes = [f"{ind2}{_scalaire(k)}: {formater(x, niveau + 1)}" for k, x in v.items()]
        return "{\n" + ",\n".join(lignes) + "\n" + ind + "}"
    if isinstance(v, list):
        if not v:
            return "[]"
        if _feuille(v):
            return "[" + ", ".join(_scalaire(x) for x in v) + "]"
        lignes = [f"{ind2}{formater(x, niveau + 1)}" for x in v]
        return "[\n" + ",\n".join(lignes) + "\n" + ind + "]"
    return _scalaire(v)


def lire(chemin: Path = CATALOGUE) -> dict:
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def ecrire(donnees: dict, chemin: Path = CATALOGUE) -> None:
    texte = formater(donnees) + "\n"
    tmp = chemin.with_suffix(".json.tmp")
    tmp.write_text(texte, encoding="utf-8")
    tmp.replace(chemin)


def mettre_a_jour_produit(id_produit: str, champs: dict, chemin: Path = CATALOGUE) -> None:
    """Relit le catalogue juste avant d'écrire (pour ne pas écraser des modifications faites
    en parallèle) et ne touche qu'aux champs autorisés."""
    interdits = set(champs) - CHAMPS_PRODUIT_MODIFIABLES
    if interdits:
        raise ValueError(f"champs non modifiables par la génération : {sorted(interdits)}")
    if "statut" in champs and champs["statut"] not in STATUTS_AUTORISES:
        raise ValueError("la génération ne peut pas publier un produit")
    data = lire(chemin)
    for p in data["produits"]:
        if p["id"] == id_produit:
            if p.get("statut") == "publie" and "statut" in champs:
                # Un produit déjà publié par un humain le reste.
                champs = {k: v for k, v in champs.items() if k != "statut"}
            p.update(champs)
            break
    else:
        raise KeyError(id_produit)
    ecrire(data, chemin)


def mettre_a_jour_gratuits(gratuits: list[dict], chemin: Path = CATALOGUE) -> None:
    data = lire(chemin)
    data["gratuits"] = gratuits
    ecrire(data, chemin)
