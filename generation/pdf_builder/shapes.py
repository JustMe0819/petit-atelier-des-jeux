"""Dessin des figures (forme + motif + taille) : lisibles en noir et blanc (motif ≠ couleur)."""
from __future__ import annotations

import math

from reportlab.lib.colors import white
from reportlab.pdfgen.canvas import Canvas

from generation.generators.figures import Figure
from generation.pdf_builder.pictos import chemin_coeur
from generation.pdf_builder.theme import NOIR

ECHELLE_PETIT = 0.58


def chemin_forme(c: Canvas, forme: str, cx: float, cy: float, s: float):
    p = c.beginPath()
    if forme == "rond":
        p.circle(cx, cy, s * 0.46)
    elif forme == "carré":
        d = s * 0.4
        p.rect(cx - d, cy - d, 2 * d, 2 * d)
    elif forme == "triangle":
        h = s * 0.86
        p.moveTo(cx - s * 0.48, cy - h * 0.42)
        p.lineTo(cx + s * 0.48, cy - h * 0.42)
        p.lineTo(cx, cy + h * 0.58)
        p.close()
    elif forme == "étoile":
        for i in range(10):
            a = math.pi / 2 + i * math.pi / 5
            r = s * 0.5 if i % 2 == 0 else s * 0.22
            x, y = cx + math.cos(a) * r, cy - s * 0.04 + math.sin(a) * r
            p.moveTo(x, y) if i == 0 else p.lineTo(x, y)
        p.close()
    elif forme == "cœur":
        return chemin_coeur(c, cx, cy, s * 0.95)
    elif forme == "losange":
        p.moveTo(cx, cy + s * 0.5)
        p.lineTo(cx + s * 0.36, cy)
        p.lineTo(cx, cy - s * 0.5)
        p.lineTo(cx - s * 0.36, cy)
        p.close()
    else:
        raise ValueError(forme)
    return p


def dessiner_figure(c: Canvas, f: Figure, cx: float, cy: float, s: float) -> None:
    """Dessine la figure dans un carré de côté s (petite taille = 58 %)."""
    if f.taille == "petit":
        s *= ECHELLE_PETIT
    lw = max(1.2, s * 0.045)
    c.saveState()
    c.setLineJoin(1)
    c.setStrokeColor(NOIR)
    c.setLineWidth(lw)
    if f.motif == "plein":
        c.setFillColor(NOIR)
        c.drawPath(chemin_forme(c, f.forme, cx, cy, s), stroke=1, fill=1)
    else:
        c.setFillColor(white)
        c.drawPath(chemin_forme(c, f.forme, cx, cy, s), stroke=0, fill=1)
        if f.motif in ("rayé", "pois"):
            c.saveState()
            c.clipPath(chemin_forme(c, f.forme, cx, cy, s), stroke=0, fill=0)
            c.setLineWidth(max(1.0, s * 0.05))
            c.setFillColor(NOIR)
            if f.motif == "rayé":
                pas = s * 0.16
                k = -s
                while k < s:
                    c.line(cx + k - s, cy - s, cx + k + s, cy + s)
                    k += pas
            else:
                pas = s * 0.19
                r = s * 0.05
                y = cy - s
                ligne = 0
                while y < cy + s:
                    x = cx - s + (pas / 2 if ligne % 2 else 0)
                    while x < cx + s:
                        c.circle(x, y, r, stroke=0, fill=1)
                        x += pas
                    y += pas * 0.87
                    ligne += 1
            c.restoreState()
        c.drawPath(chemin_forme(c, f.forme, cx, cy, s), stroke=1, fill=0)
    c.restoreState()
