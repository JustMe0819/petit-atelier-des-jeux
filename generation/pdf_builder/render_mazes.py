"""Rendu des labyrinthes : murs noirs épais, départ et arrivée illustrés."""
from __future__ import annotations

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from generation.generators.mazes import Labyrinthe
from generation.pdf_builder import fonts, pictos
from generation.pdf_builder.layout import Rect
from generation.pdf_builder.text import ecrire
from generation.pdf_builder.theme import NOIR, Theme


def dessiner_labyrinthe(c: Canvas, rect: Rect, lab: Labyrinthe, theme: Theme, depart: str, arrivee: str,
                        solution: bool = False, etiquettes: bool = True) -> Rect:
    """Dessine le labyrinthe centré dans rect. Renvoie le rectangle de la grille."""
    if etiquettes:
        libre = (rect.h - rect.w * lab.lignes / lab.colonnes) / 2  # place laissée par une grille « pleine largeur »
        bande = min(max(24 * mm, libre), 32 * mm, rect.h * 0.2)
    else:
        bande = min(14 * mm, rect.h * 0.14)
    cell = min(rect.w / lab.colonnes, (rect.h - 2 * bande) / lab.lignes)
    gw, gh = cell * lab.colonnes, cell * lab.lignes
    x0 = rect.cx - gw / 2
    y_haut = rect.cy + gh / 2
    grille = Rect(x0, y_haut - gh, gw, gh)

    def coin(l: int, col: int) -> tuple[float, float]:  # coin haut-gauche de la case
        return x0 + col * cell, y_haut - l * cell

    def centre(l: int, col: int) -> tuple[float, float]:
        x, y = coin(l, col)
        return x + cell / 2, y - cell / 2

    # Tracé de la solution (sous les murs).
    if solution and lab.solution:
        c.saveState()
        c.setStrokeColor(theme.trace_solution)
        c.setLineWidth(max(1.5, cell * 0.32))
        c.setLineCap(1)
        c.setLineJoin(1)
        p = c.beginPath()
        dx, dy = centre(*lab.solution[0])
        p.moveTo(dx, y_haut + cell * 0.6)
        for case in lab.solution:
            p.lineTo(*centre(*case))
        ax, _ = centre(*lab.solution[-1])
        p.lineTo(ax, y_haut - gh - cell * 0.6)
        c.drawPath(p, stroke=1, fill=0)
        c.restoreState()

    # Murs.
    c.saveState()
    c.setStrokeColor(NOIR)
    c.setLineWidth(max(1.2, min(3.2, cell * 0.09)))
    c.setLineCap(1)
    p = c.beginPath()
    for l in range(lab.lignes):
        for col in range(lab.colonnes):
            x, y = coin(l, col)
            o = lab.ouvertures[l][col]
            if "N" not in o:
                p.moveTo(x, y)
                p.lineTo(x + cell, y)
            if "O" not in o:
                p.moveTo(x, y)
                p.lineTo(x, y - cell)
            if l == lab.lignes - 1 and "S" not in o:
                p.moveTo(x, y - cell)
                p.lineTo(x + cell, y - cell)
            if col == lab.colonnes - 1 and "E" not in o:
                p.moveTo(x + cell, y)
                p.lineTo(x + cell, y - cell)
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()

    # Départ (au-dessus de l'entrée) et arrivée (sous la sortie).
    taille = min(bande * (0.7 if etiquettes else 0.85), 22 * mm)
    decal = bande * (0.58 if etiquettes else 0.5)
    dx, _ = centre(*lab.depart)
    ax, _ = centre(*lab.arrivee)
    dx_p = min(max(dx, rect.x + taille / 2), rect.right - taille / 2)
    ax_p = min(max(ax, rect.x + taille / 2), rect.right - taille / 2)
    pictos.dessiner(c, depart, dx_p, y_haut + decal, taille, theme)
    pictos.dessiner(c, arrivee, ax_p, y_haut - gh - decal, taille, theme)
    if etiquettes:
        w = min(cell * 0.3, 6)
        _fleche(c, dx, y_haut + 1.5, w)
        _fleche(c, ax, y_haut - gh - 1.5 - w * 1.2, w)
        tx = dx_p + taille / 2 + 4
        align = "left"
        if tx + 60 > rect.right:
            tx, align = dx_p - taille / 2 - 4, "right"
        ecrire(c, "Départ", tx, y_haut + decal - 4, fonts.TITRE, 13, align=align)
        tx = ax_p - taille / 2 - 4
        align = "right"
        if tx - 60 < rect.x:
            tx, align = ax_p + taille / 2 + 4, "left"
        ecrire(c, "Arrivée", tx, y_haut - gh - decal - 4, fonts.TITRE, 13, align=align)
    return grille


def _fleche(c: Canvas, x: float, y_pointe: float, w: float) -> None:
    """Petite flèche vers le bas dont la pointe est en y_pointe."""
    c.saveState()
    c.setFillColor(NOIR)
    p = c.beginPath()
    p.moveTo(x - w, y_pointe + w * 1.2)
    p.lineTo(x + w, y_pointe + w * 1.2)
    p.lineTo(x, y_pointe)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.restoreState()
