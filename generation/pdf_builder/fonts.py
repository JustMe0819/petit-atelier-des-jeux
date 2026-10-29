"""Enregistrement des polices TTF embarquées (licence SIL OFL 1.1, voir assets/fonts).

- Andika (SIL International) : police conçue pour les lecteurs débutants → textes et consignes.
- Nunito (ExtraBold / Bold) : police arrondie → titres.
Repli automatique sur DejaVu Sans si les fichiers sont absents.
"""
from __future__ import annotations

from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from generation.config import POLICES

TEXTE = "PAD-Texte"
TEXTE_GRAS = "PAD-TexteGras"
TITRE = "PAD-Titre"
TITRE_DEMI = "PAD-TitreDemi"

_FICHIERS = {
    TEXTE: "Andika-Regular.ttf",
    TEXTE_GRAS: "Andika-Bold.ttf",
    TITRE: "Nunito-ExtraBold.ttf",
    TITRE_DEMI: "Nunito-Bold.ttf",
}
_REPLI = {
    TEXTE: "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    TEXTE_GRAS: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    TITRE: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    TITRE_DEMI: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

_enregistrees = False


def chemin_police(nom: str) -> Path:
    p = POLICES / _FICHIERS[nom]
    return p if p.exists() else Path(_REPLI[nom])


def enregistrer_polices() -> None:
    global _enregistrees
    if _enregistrees:
        return
    for nom in _FICHIERS:
        pdfmetrics.registerFont(TTFont(nom, str(chemin_police(nom))))
    _enregistrees = True


def glyphe_disponible(nom_police: str, caractere: str) -> bool:
    enregistrer_polices()
    police = pdfmetrics.getFont(nom_police)
    return ord(caractere) in police.face.charToGlyph or caractere in "\n\r\t"
