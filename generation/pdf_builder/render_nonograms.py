"""Rendu des nonogrammes : indices lisibles (≥ 11 pt), traits épais toutes les 5 cases."""
from __future__ import annotations

from reportlab.lib.colors import white
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from generation.generators.nonograms import PLEIN, VIDE, Nonogramme
from generation.pdf_builder import fonts
from generation.pdf_builder.layout import Rect
from generation.pdf_builder.text import ecrire
from generation.pdf_builder.theme import GRIS_TRES_CLAIR, NOIR, Theme

TAILLE_INDICE_MIN = 11.0


def dessiner_nonogramme(c: Canvas, rect: Rect, n: Nonogramme, theme: Theme, *, solution: bool = False,
                        etat: list[list[int]] | None = None, surligne: tuple[str, int] | None = None,
                        cell_max: float = 16 * mm, avec_indices: bool = True,
                        taille_indice: float | None = None) -> dict:
    """Dessine la grille ; renvoie les dimensions effectives (cellule, taille des indices)."""
    nb_ind_l = max(len(r) for r in n.lignes) if avec_indices else 0
    nb_ind_c = max(len(col) for col in n.colonnes) if avec_indices else 0

    deux_chiffres = any(v >= 10 for ind in n.lignes + n.colonnes for v in ind)
    facteur = 1.6 if deux_chiffres else 1.35

    def dims(cell: float) -> tuple[float, float, float]:
        ti = taille_indice or max(TAILLE_INDICE_MIN, min(17.0, cell * 0.5))
        case_ind = ti * facteur
        return ti, nb_ind_l * case_ind, nb_ind_c * case_ind

    cell = cell_max
    while cell > 2:
        ti, zl, zc = dims(cell)
        if zl + n.largeur * cell <= rect.w and zc + n.hauteur * cell <= rect.h:
            break
        cell -= 0.25
    ti, zl, zc = dims(cell)
    case_ind = ti * facteur
    tw, th = zl + n.largeur * cell, zc + n.hauteur * cell
    x0 = rect.cx - tw / 2 + zl          # bord gauche de la grille
    y0 = rect.cy + th / 2 - zc          # bord haut de la grille
    gw, gh = n.largeur * cell, n.hauteur * cell

    # Fonds légers des zones d'indices (une bande sur deux) — supprimés en version éco.
    if avec_indices and not theme.eco:
        c.saveState()
        for r in range(n.hauteur):
            if r % 2 == 0:
                c.setFillColor(theme.accent_clair)
                c.rect(x0 - zl, y0 - (r + 1) * cell, zl, cell, stroke=0, fill=1)
        for col in range(n.largeur):
            if col % 2 == 0:
                c.setFillColor(theme.accent_clair)
                c.rect(x0 + col * cell, y0, cell, zc, stroke=0, fill=1)
        c.restoreState()
    # Surlignage d'une ligne/colonne (page « comment jouer »).
    if surligne:
        c.saveState()
        c.setFillColor(GRIS_TRES_CLAIR if theme.eco else theme.accent_clair)
        typ, i = surligne
        if typ == "ligne":
            c.rect(x0 - zl, y0 - (i + 1) * cell, zl + gw, cell, stroke=0, fill=1)
        else:
            c.rect(x0 + i * cell, y0 - gh, cell, gh + zc, stroke=0, fill=1)
        c.restoreState()

    # Cases.
    grille = n.dessin if solution else etat
    if grille is not None:
        c.saveState()
        for r in range(n.hauteur):
            for col in range(n.largeur):
                v = grille[r][col]
                x, y = x0 + col * cell, y0 - (r + 1) * cell
                if v == PLEIN or (solution and v == 1):
                    c.setFillColor(NOIR)
                    c.rect(x, y, cell, cell, stroke=0, fill=1)
                elif v == VIDE and etat is not None:
                    c.setStrokeColor(NOIR)
                    c.setLineWidth(max(0.8, cell * 0.06))
                    d = cell * 0.18
                    c.line(x + cell / 2 - d, y + cell / 2 - d, x + cell / 2 + d, y + cell / 2 + d)
                    c.line(x + cell / 2 - d, y + cell / 2 + d, x + cell / 2 + d, y + cell / 2 - d)
        c.restoreState()

    # Quadrillage.
    c.saveState()
    c.setStrokeColor(NOIR)
    for r in range(n.hauteur + 1):
        c.setLineWidth(2.0 if r % 5 == 0 or r == n.hauteur else 0.7)
        c.line(x0 - (zl if avec_indices else 0), y0 - r * cell, x0 + gw, y0 - r * cell)
    for col in range(n.largeur + 1):
        c.setLineWidth(2.0 if col % 5 == 0 or col == n.largeur else 0.7)
        c.line(x0 + col * cell, y0 + (zc if avec_indices else 0), x0 + col * cell, y0 - gh)
    if avec_indices:
        c.setLineWidth(2.0)
        c.line(x0 - zl, y0, x0 - zl, y0 - gh)
        c.line(x0, y0 + zc, x0 + gw, y0 + zc)
    c.restoreState()

    # Indices.
    if avec_indices:
        for r, ind in enumerate(n.lignes):
            y = y0 - (r + 0.5) * cell - ti * 0.36
            for k, v in enumerate(reversed(ind)):
                ecrire(c, str(v), x0 - (k + 0.5) * case_ind, y, fonts.TITRE, ti, align="center")
        for col, ind in enumerate(n.colonnes):
            x = x0 + (col + 0.5) * cell
            for k, v in enumerate(reversed(ind)):
                ecrire(c, str(v), x, y0 + (k + 0.5) * case_ind - ti * 0.36, fonts.TITRE, ti, align="center")
    return {"cellule_mm": cell / mm, "taille_indices_pt": ti, "grille": Rect(x0, y0 - gh, gw, gh)}


def dessiner_mini(c: Canvas, rect: Rect, dessin: list[list[int]]) -> None:
    """Petite image pixelisée (corrigés)."""
    h, w = len(dessin), len(dessin[0])
    cell = min(rect.w / w, rect.h / h)
    x0, y0 = rect.cx - w * cell / 2, rect.cy + h * cell / 2
    c.saveState()
    c.setFillColor(NOIR)
    for r in range(h):
        for col in range(w):
            if dessin[r][col]:
                c.rect(x0 + col * cell, y0 - (r + 1) * cell, cell, cell, stroke=0, fill=1)
    c.setStrokeColor(NOIR)
    c.setLineWidth(0.3)
    for r in range(h + 1):
        c.line(x0, y0 - r * cell, x0 + w * cell, y0 - r * cell)
    for col in range(w + 1):
        c.line(x0 + col * cell, y0, x0 + col * cell, y0 - h * cell)
    c.setLineWidth(1)
    c.setFillColor(white)
    c.rect(x0, y0 - h * cell, w * cell, h * cell, stroke=1, fill=0)
    c.restoreState()

