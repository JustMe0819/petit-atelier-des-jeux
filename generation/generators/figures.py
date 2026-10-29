"""Figures géométriques simples (forme + motif + taille), lisibles en noir et blanc."""
from __future__ import annotations

from dataclasses import dataclass

FORMES = ["rond", "carré", "triangle", "étoile", "cœur", "losange"]
MOTIFS = ["vide", "plein", "rayé", "pois"]
TAILLES = ["grand", "petit"]
FEMININ = {"étoile"}
ATTRIBUTS = ("forme", "motif", "taille")


@dataclass(frozen=True, order=True)
class Figure:
    forme: str
    motif: str = "vide"
    taille: str = "grand"

    def avec(self, **kw: str) -> "Figure":
        d = {"forme": self.forme, "motif": self.motif, "taille": self.taille}
        d.update(kw)
        return Figure(**d)

    def attr(self, nom: str) -> str:
        return getattr(self, nom)


def _accorde_motif(motif: str, fem: bool) -> str:
    return {
        "vide": "vide",
        "plein": "pleine" if fem else "plein",
        "rayé": "rayée" if fem else "rayé",
        "pois": "à pois",
    }[motif]


def nom_figure(f: Figure, avec_taille: bool = False, avec_motif: bool = True,
               article: bool = True) -> str:
    """« le grand rond rayé », « l'étoile pleine », « la petite étoile à pois »…"""
    fem = f.forme in FEMININ
    mots = []
    if avec_taille:
        mots.append({"grand": "grande" if fem else "grand", "petit": "petite" if fem else "petit"}[f.taille])
    mots.append(f.forme)
    if avec_motif:
        mots.append(_accorde_motif(f.motif, fem))
    groupe = " ".join(mots)
    if not article:
        return groupe
    if groupe[0] in "aeiouéèêh":
        return "l'" + groupe
    return ("la " if fem else "le ") + groupe
