"""Aides pour écrire du texte (avec journal des glyphes utilisés pour la QA)."""
from __future__ import annotations

import re

from reportlab.lib.colors import Color
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

from generation.pdf_builder import fonts
from generation.pdf_builder.layout import Rect
from generation.pdf_builder.theme import NOIR

fonts.enregistrer_polices()
registerFontFamily(fonts.TEXTE, normal=fonts.TEXTE, bold=fonts.TEXTE_GRAS,
                   italic=fonts.TEXTE, boldItalic=fonts.TEXTE_GRAS)


def _journaliser(c: Canvas, police: str, texte: str) -> None:
    journal = getattr(c, "_pad_journal", None)
    if journal is not None:
        for ch in set(texte):
            journal.add((police, ch))


def largeur(texte: str, police: str, taille: float) -> float:
    return pdfmetrics.stringWidth(texte, police, taille)


def taille_ajustee(texte: str, police: str, taille: float, largeur_max: float, mini: float = 8) -> float:
    while taille > mini and largeur(texte, police, taille) > largeur_max:
        taille -= 0.5
    return taille


def ecrire(c: Canvas, texte: str, x: float, y: float, police: str = fonts.TEXTE,
           taille: float = 12, align: str = "left", couleur: Color = NOIR) -> None:
    _journaliser(c, police, texte)
    c.setFillColor(couleur)
    c.setFont(police, taille)
    if align == "center":
        c.drawCentredString(x, y, texte)
    elif align == "right":
        c.drawRightString(x, y, texte)
    else:
        c.drawString(x, y, texte)


def paragraphe(c: Canvas, texte: str, rect: Rect, police: str = fonts.TEXTE, taille: float = 13,
               interligne: float | None = None, align: str = "left", couleur: Color = NOIR,
               depuis_haut: bool = True) -> float:
    """Écrit un paragraphe (balises <b> autorisées) dans rect ; renvoie la hauteur utilisée."""
    texte = typographie(texte)
    brut = re.sub(r"<[^>]+>", "", texte)
    _journaliser(c, police, brut)
    if "<b>" in texte:
        _journaliser(c, fonts.TEXTE_GRAS, brut)
    style = ParagraphStyle(
        "pad", fontName=police, fontSize=taille, leading=interligne or taille * 1.3,
        alignment=TA_CENTER if align == "center" else TA_LEFT, textColor=couleur,
    )
    p = Paragraph(texte, style)
    _, h = p.wrap(rect.w, rect.h)
    y = rect.top - h if depuis_haut else rect.y
    p.drawOn(c, rect.x, y)
    return h


def typographie(texte: str) -> str:
    """Espaces insécables de la typographie française (pas de « : » ou « ! » en début de ligne)."""
    for avant, apres in (("« ", "«\u00a0"), (" »", "\u00a0»"), (" :", "\u00a0:"), (" !", "\u00a0!"),
                         (" ?", "\u00a0?"), (" ;", "\u00a0;"), (" →", "\u00a0→")):
        texte = texte.replace(avant, apres)
    return texte


def hauteur_paragraphe(texte: str, largeur_dispo: float, police: str = fonts.TEXTE,
                       taille: float = 13, interligne: float | None = None) -> float:
    texte = typographie(texte)
    style = ParagraphStyle("pad", fontName=police, fontSize=taille, leading=interligne or taille * 1.3)
    _, h = Paragraph(texte, style).wrap(largeur_dispo, 10_000)
    return h
