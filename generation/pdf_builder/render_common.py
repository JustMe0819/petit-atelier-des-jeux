"""Éléments communs des pages : titre, consigne, niveau, cases réponse, étiquettes."""
from __future__ import annotations

import math

from reportlab.lib.colors import white
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from generation.pdf_builder import fonts
from generation.pdf_builder.layout import Rect
from generation.pdf_builder.text import ecrire, hauteur_paragraphe, paragraphe, taille_ajustee
from generation.pdf_builder.theme import NOIR, Theme

NOMS_NIVEAUX = {"debutant": "débutant", "intermediaire": "intermédiaire", "defi": "défi"}
ETOILES_NIVEAUX = {"debutant": 1, "intermediaire": 2, "defi": 3}


def etoile(c: Canvas, cx: float, cy: float, r: float, pleine: bool, theme: Theme) -> None:
    p = c.beginPath()
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        p.moveTo(x, y) if i == 0 else p.lineTo(x, y)
    p.close()
    c.saveState()
    c.setLineWidth(0.9)
    c.setStrokeColor(NOIR)
    if pleine:
        c.setFillColor(NOIR if theme.eco else theme.accent)
    else:
        c.setFillColor(white)
    c.drawPath(p, stroke=1, fill=1)
    c.restoreState()


def badge_niveau(c: Canvas, droite: float, y: float, niveau: str, theme: Theme) -> None:
    n = ETOILES_NIVEAUX[niveau]
    for i in range(3):
        etoile(c, droite - 7 - i * 15, y + 4, 6, (2 - i) < n, theme)
    ecrire(c, f"Niveau {NOMS_NIVEAUX[niveau]}", droite - 52, y, fonts.TITRE_DEMI, 10.5, align="right")


def bloc_titre(c: Canvas, rect: Rect, titre: str, consigne: str | None, theme: Theme,
               niveau: str | None = None, taille_titre: float = 21, taille_consigne: float = 14) -> Rect:
    """Titre de page + consigne encadrée ; renvoie la zone restante."""
    largeur_titre = rect.w - (130 if niveau else 0)
    t = taille_ajustee(titre, fonts.TITRE, taille_titre, largeur_titre, mini=13)
    y_titre = rect.top - t * 0.95
    ecrire(c, titre, rect.x, y_titre, fonts.TITRE, t)
    if niveau:
        badge_niveau(c, rect.right, y_titre + 2, niveau, theme)
    c.saveState()
    c.setStrokeColor(theme.trait_deco)
    c.setLineWidth(2.2)
    c.setLineCap(1)
    c.line(rect.x, y_titre - 6, rect.x + 22 * mm, y_titre - 6)
    c.restoreState()
    haut = rect.top - (y_titre - 10)
    if consigne:
        pad = 7
        h = hauteur_paragraphe(consigne, rect.w - 2 * pad, fonts.TEXTE, taille_consigne) + 2 * pad - 2
        boite = Rect(rect.x, y_titre - 14 - h, rect.w, h)
        c.saveState()
        c.setLineWidth(0.8)
        c.setStrokeColor(theme.trait_deco)
        if theme.aplat_deco is not None:
            c.setFillColor(theme.aplat_deco)
            c.roundRect(boite.x, boite.y, boite.w, boite.h, 8, stroke=0, fill=1)
        else:
            c.roundRect(boite.x, boite.y, boite.w, boite.h, 8, stroke=1, fill=0)
        c.restoreState()
        paragraphe(c, consigne, boite.inset(pad, pad - 1), fonts.TEXTE, taille_consigne)
        haut = rect.top - boite.y
    _, reste = rect.take_top(haut, gap=5 * mm)
    return reste


def case_reponse(c: Canvas, x: float, y: float, w: float, h: float, texte: str | None = None,
                 taille: float = 16) -> None:
    """Case à remplir par l'enfant (ou remplie dans les corrigés)."""
    c.saveState()
    c.setStrokeColor(NOIR)
    c.setLineWidth(1.3)
    c.setFillColor(white)
    c.roundRect(x, y, w, h, 4, stroke=1, fill=1)
    c.restoreState()
    if texte is not None:
        ecrire(c, texte, x + w / 2, y + h / 2 - taille * 0.35, fonts.TITRE, taille, align="center")


def etiquette(c: Canvas, cx: float, cy: float, texte: str, r: float = 8, entouree: bool = False,
              theme: Theme | None = None) -> None:
    """Petite pastille ronde avec une lettre ou un chiffre (A, B, 1, 2…)."""
    c.saveState()
    c.setLineWidth(2.2 if entouree else 1)
    c.setStrokeColor(theme.trace_solution if (entouree and theme) else NOIR)
    c.setFillColor(white)
    c.circle(cx, cy, r, stroke=1, fill=1)
    c.restoreState()
    ecrire(c, texte, cx, cy - r * 0.42, fonts.TITRE, r * 1.15, align="center")


def entourer(c: Canvas, cx: float, cy: float, rx: float, ry: float, theme: Theme) -> None:
    """Ellipse épaisse indiquant la bonne réponse dans les corrigés."""
    c.saveState()
    c.setStrokeColor(theme.trace_solution)
    c.setLineWidth(2.4)
    c.ellipse(cx - rx, cy - ry, cx + rx, cy + ry, stroke=1, fill=0)
    c.restoreState()


def cadre(c: Canvas, r: Rect, theme: Theme, rayon: float = 8, epaisseur: float = 1.2,
          deco: bool = False) -> None:
    c.saveState()
    c.setLineWidth(epaisseur)
    c.setStrokeColor(theme.trait_deco if deco else NOIR)
    c.roundRect(r.x, r.y, r.w, r.h, rayon, stroke=1, fill=0)
    c.restoreState()
