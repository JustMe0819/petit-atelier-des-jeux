"""Pictogrammes vectoriels simples (créations originales, formes géométriques).

Chaque fonction dessine un pictogramme centré en (cx, cy) tenant dans un carré de côté `s`.
Contours noirs francs ; aplats de couleur douce en version normale, blancs en version
économie d'encre (le dessin reste lisible en noir et blanc grâce aux contours).
"""
from __future__ import annotations

import math
from typing import Callable

from reportlab.lib.colors import white
from reportlab.pdfgen.canvas import Canvas

from generation.pdf_builder.theme import NOIR, Theme

Dessinateur = Callable[[Canvas, float, float, float, Theme], None]

C = {
    "vert": "#7BC67B", "vert_f": "#3E8E41", "marron": "#A9744F", "marron_c": "#D9B48F",
    "jaune": "#FFD43B", "orange": "#FF922B", "rouge": "#F03E3E", "rose": "#F7A1C4",
    "bleu": "#74C0FC", "bleu_f": "#339AF0", "gris": "#CED4DA", "gris_f": "#868E96",
    "beige": "#FFF3E0", "creme": "#FFF9DB", "violet": "#B197FC",
}


def _lw(s: float) -> float:
    return max(0.9, s * 0.028)


def _style(c: Canvas, t: Theme, s: float, couleur: str | None) -> None:
    c.setStrokeColor(NOIR)
    c.setLineWidth(_lw(s))
    c.setLineJoin(1)
    c.setLineCap(1)
    f = t.remplissage(C.get(couleur, couleur) if couleur else None)
    c.setFillColor(f if f is not None else white)


def _encre(c: Canvas) -> None:
    c.setFillColor(NOIR)


def lisse(c: Canvas, pts: list[tuple[float, float]], ferme: bool = True):
    """Chemin lissé (Catmull-Rom → Bézier) passant par les points."""
    p = c.beginPath()
    n = len(pts)
    p.moveTo(*pts[0])
    rng = range(n) if ferme else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (ferme or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (ferme or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        p.curveTo(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if ferme:
        p.close()
    return p


def _pts(cx: float, cy: float, s: float, rel: list[tuple[float, float]]) -> list[tuple[float, float]]:
    return [(cx + x * s, cy + y * s) for x, y in rel]


def _poly(c: Canvas, pts: list[tuple[float, float]], fill: int = 1) -> None:
    p = c.beginPath()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    p.close()
    c.drawPath(p, stroke=1, fill=fill)


def _oeil(c: Canvas, x: float, y: float, r: float) -> None:
    c.saveState()
    _encre(c)
    c.circle(x, y, r, stroke=0, fill=1)
    c.setFillColor(white)
    c.circle(x + r * 0.35, y + r * 0.35, r * 0.35, stroke=0, fill=1)
    c.restoreState()


def _union(c: Canvas, t: Theme, s: float, couleur: str, formes: list[Callable[[int, int], None]]) -> None:
    """Dessine l'union de plusieurs formes avec un seul contour extérieur."""
    c.saveState()
    c.setLineWidth(_lw(s) * 2)
    c.setStrokeColor(NOIR)
    for f in formes:
        f(1, 0)
    _style(c, t, s, couleur)
    for f in formes:
        f(0, 1)
    c.restoreState()


# =============================================================== nature / objets
def arbre(c, cx, cy, s, t):
    _style(c, t, s, "marron")
    c.rect(cx - s * 0.07, cy - s * 0.48, s * 0.14, s * 0.4, stroke=1, fill=1)
    _union(c, t, s, "vert", [
        lambda st, fi: c.circle(cx, cy + s * 0.16, s * 0.27, stroke=st, fill=fi),
        lambda st, fi: c.circle(cx - s * 0.2, cy + s * 0.02, s * 0.2, stroke=st, fill=fi),
        lambda st, fi: c.circle(cx + s * 0.2, cy + s * 0.02, s * 0.2, stroke=st, fill=fi),
    ])


def fleur(c, cx, cy, s, t):
    _style(c, t, s, "vert")
    c.line(cx, cy - s * 0.48, cx, cy)
    c.ellipse(cx, cy - s * 0.32, cx + s * 0.2, cy - s * 0.22, stroke=1, fill=1)
    _style(c, t, s, "rose")
    for i in range(5):
        a = math.pi / 2 + i * 2 * math.pi / 5
        c.circle(cx + math.cos(a) * s * 0.18, cy + s * 0.12 + math.sin(a) * s * 0.18, s * 0.13, stroke=1, fill=1)
    _style(c, t, s, "jaune")
    c.circle(cx, cy + s * 0.12, s * 0.12, stroke=1, fill=1)


def soleil(c, cx, cy, s, t):
    _style(c, t, s, "jaune")
    for i in range(8):
        a = i * math.pi / 4
        c.line(cx + math.cos(a) * s * 0.3, cy + math.sin(a) * s * 0.3,
               cx + math.cos(a) * s * 0.47, cy + math.sin(a) * s * 0.47)
    c.circle(cx, cy, s * 0.24, stroke=1, fill=1)
    _oeil(c, cx - s * 0.08, cy + s * 0.04, s * 0.03)
    _oeil(c, cx + s * 0.08, cy + s * 0.04, s * 0.03)
    c.arc(cx - s * 0.1, cy - s * 0.14, cx + s * 0.1, cy, 200, 140)


def nuage(c, cx, cy, s, t):
    _union(c, t, s, "bleu", [
        lambda st, fi: c.circle(cx - s * 0.2, cy - s * 0.04, s * 0.18, stroke=st, fill=fi),
        lambda st, fi: c.circle(cx + s * 0.02, cy + s * 0.08, s * 0.24, stroke=st, fill=fi),
        lambda st, fi: c.circle(cx + s * 0.25, cy - s * 0.05, s * 0.17, stroke=st, fill=fi),
        lambda st, fi: c.roundRect(cx - s * 0.38, cy - s * 0.22, s * 0.8, s * 0.2, s * 0.1, stroke=st, fill=fi),
    ])


def champignon(c, cx, cy, s, t):
    _style(c, t, s, "beige")
    c.roundRect(cx - s * 0.1, cy - s * 0.46, s * 0.2, s * 0.42, s * 0.06, stroke=1, fill=1)
    _style(c, t, s, "rouge")
    p = c.beginPath()
    p.moveTo(cx - s * 0.45, cy - s * 0.06)
    p.curveTo(cx - s * 0.45, cy + s * 0.45, cx + s * 0.45, cy + s * 0.45, cx + s * 0.45, cy - s * 0.06)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.saveState()
    c.setFillColor(white)
    for dx, dy, r in ((-0.2, 0.08, 0.06), (0.05, 0.2, 0.07), (0.24, 0.05, 0.05)):
        c.circle(cx + dx * s, cy + dy * s, r * s, stroke=1, fill=1)
    c.restoreState()


def maison(c, cx, cy, s, t):
    _style(c, t, s, "creme")
    c.rect(cx - s * 0.32, cy - s * 0.46, s * 0.64, s * 0.5, stroke=1, fill=1)
    _style(c, t, s, "rouge")
    _poly(c, [(cx - s * 0.44, cy + s * 0.04), (cx, cy + s * 0.46), (cx + s * 0.44, cy + s * 0.04)])
    _style(c, t, s, "marron")
    c.roundRect(cx - s * 0.08, cy - s * 0.46, s * 0.16, s * 0.28, s * 0.04, stroke=1, fill=1)
    _style(c, t, s, "bleu")
    c.rect(cx + s * 0.13, cy - s * 0.2, s * 0.12, s * 0.12, stroke=1, fill=1)


def poisson(c, cx, cy, s, t):
    _style(c, t, s, "orange")
    _poly(c, [(cx + s * 0.18, cy), (cx + s * 0.47, cy + s * 0.2), (cx + s * 0.47, cy - s * 0.2)])
    c.ellipse(cx - s * 0.45, cy - s * 0.22, cx + s * 0.25, cy + s * 0.22, stroke=1, fill=1)
    _oeil(c, cx - s * 0.25, cy + s * 0.05, s * 0.045)
    c.arc(cx - s * 0.12, cy - s * 0.12, cx + s * 0.05, cy + s * 0.12, -60, 120)


def oiseau(c, cx, cy, s, t):
    _style(c, t, s, "bleu")
    c.ellipse(cx - s * 0.38, cy - s * 0.25, cx + s * 0.18, cy + s * 0.15, stroke=1, fill=1)
    c.circle(cx + s * 0.18, cy + s * 0.17, s * 0.16, stroke=1, fill=1)
    _style(c, t, s, "orange")
    _poly(c, [(cx + s * 0.32, cy + s * 0.21), (cx + s * 0.47, cy + s * 0.15), (cx + s * 0.32, cy + s * 0.1)])
    _oeil(c, cx + s * 0.21, cy + s * 0.2, s * 0.035)
    _style(c, t, s, "bleu_f")
    c.ellipse(cx - s * 0.22, cy - s * 0.1, cx + s * 0.06, cy + s * 0.06, stroke=1, fill=1)
    c.line(cx - s * 0.05, cy - s * 0.25, cx - s * 0.05, cy - s * 0.42)
    c.line(cx - s * 0.15, cy - s * 0.24, cx - s * 0.15, cy - s * 0.42)


def etoile(c, cx, cy, s, t):
    _style(c, t, s, "jaune")
    pts = []
    for i in range(10):
        a = math.pi / 2 + i * math.pi / 5
        r = s * 0.48 if i % 2 == 0 else s * 0.2
        pts.append((cx + math.cos(a) * r, cy - s * 0.04 + math.sin(a) * r))
    _poly(c, pts)


def chemin_coeur(c: Canvas, cx: float, cy: float, s: float):
    p = c.beginPath()
    p.moveTo(cx, cy - 0.45 * s)
    p.curveTo(cx - 0.15 * s, cy - 0.3 * s, cx - 0.5 * s, cy - 0.1 * s, cx - 0.5 * s, cy + 0.15 * s)
    p.curveTo(cx - 0.5 * s, cy + 0.42 * s, cx - 0.2 * s, cy + 0.5 * s, cx, cy + 0.28 * s)
    p.curveTo(cx + 0.2 * s, cy + 0.5 * s, cx + 0.5 * s, cy + 0.42 * s, cx + 0.5 * s, cy + 0.15 * s)
    p.curveTo(cx + 0.5 * s, cy - 0.1 * s, cx + 0.15 * s, cy - 0.3 * s, cx, cy - 0.45 * s)
    p.close()
    return p


def coeur(c, cx, cy, s, t):
    _style(c, t, s, "rose")
    c.drawPath(chemin_coeur(c, cx, cy, s * 0.95), stroke=1, fill=1)


def pomme(c, cx, cy, s, t):
    _style(c, t, s, "marron")
    c.line(cx, cy + s * 0.22, cx + s * 0.05, cy + s * 0.44)
    _style(c, t, s, "vert")
    c.ellipse(cx + s * 0.06, cy + s * 0.28, cx + s * 0.3, cy + s * 0.4, stroke=1, fill=1)
    _style(c, t, s, "rouge")
    p = lisse(c, _pts(cx, cy, s, [(0, 0.24), (0.3, 0.3), (0.42, 0.02), (0.25, -0.38), (0, -0.4),
                                  (-0.25, -0.38), (-0.42, 0.02), (-0.3, 0.3)]))
    c.drawPath(p, stroke=1, fill=1)


def escargot(c, cx, cy, s, t):
    _style(c, t, s, "beige")
    p = lisse(c, _pts(cx, cy, s, [(-0.46, -0.32), (0.3, -0.32), (0.44, -0.1), (0.38, 0.08), (0.3, -0.16),
                                  (-0.4, -0.18)]))
    c.drawPath(p, stroke=1, fill=1)
    c.line(cx + s * 0.38, cy + s * 0.05, cx + s * 0.42, cy + s * 0.25)
    c.line(cx + s * 0.34, cy + s * 0.04, cx + s * 0.3, cy + s * 0.22)
    _style(c, t, s, "orange")
    c.circle(cx - s * 0.06, cy + s * 0.06, s * 0.26, stroke=1, fill=1)
    p = c.beginPath()
    p.moveTo(cx - s * 0.06, cy + s * 0.06)
    for i in range(1, 30):
        a = i * 0.45
        r = s * 0.008 * i * 0.8
        p.lineTo(cx - s * 0.06 + math.cos(a) * r, cy + s * 0.06 + math.sin(a) * r)
    c.drawPath(p, stroke=1, fill=0)


# =============================================================== animaux
def herisson(c, cx, cy, s, t):
    _style(c, t, s, "marron")
    pts = []
    for i in range(13):
        a = math.pi * (0.95 - i * 0.9 / 12)
        r = s * (0.46 if i % 2 == 0 else 0.34)
        pts.append((cx - s * 0.08 + math.cos(a) * r, cy - s * 0.28 + math.sin(a) * r * 1.05))
    pts.append((cx + s * 0.12, cy - s * 0.3))
    pts.append((cx - s * 0.5, cy - s * 0.3))
    _poly(c, pts)
    _style(c, t, s, "marron_c")
    p = lisse(c, _pts(cx, cy, s, [(0.05, -0.3), (0.06, 0.0), (0.22, 0.02), (0.47, -0.16), (0.3, -0.3)]))
    c.drawPath(p, stroke=1, fill=1)
    _encre(c)
    c.circle(cx + s * 0.46, cy - s * 0.16, s * 0.04, stroke=0, fill=1)
    _oeil(c, cx + s * 0.2, cy - s * 0.08, s * 0.035)
    _style(c, t, s, None)
    c.line(cx - s * 0.3, cy - s * 0.3, cx - s * 0.3, cy - s * 0.4)
    c.line(cx + s * 0.15, cy - s * 0.3, cx + s * 0.15, cy - s * 0.4)


def lapin(c, cx, cy, s, t):
    _style(c, t, s, "gris")
    c.ellipse(cx - s * 0.2, cy, cx - s * 0.04, cy + s * 0.5, stroke=1, fill=1)
    c.ellipse(cx + s * 0.04, cy, cx + s * 0.2, cy + s * 0.5, stroke=1, fill=1)
    c.circle(cx, cy - s * 0.15, s * 0.3, stroke=1, fill=1)
    _style(c, t, s, "rose")
    c.ellipse(cx - s * 0.16, cy + s * 0.12, cx - s * 0.08, cy + s * 0.4, stroke=0, fill=1)
    c.ellipse(cx + s * 0.08, cy + s * 0.12, cx + s * 0.16, cy + s * 0.4, stroke=0, fill=1)
    _oeil(c, cx - s * 0.11, cy - s * 0.08, s * 0.04)
    _oeil(c, cx + s * 0.11, cy - s * 0.08, s * 0.04)
    _style(c, t, s, "rose")
    _poly(c, [(cx - s * 0.05, cy - s * 0.18), (cx + s * 0.05, cy - s * 0.18), (cx, cy - s * 0.24)])
    c.arc(cx - s * 0.08, cy - s * 0.34, cx, cy - s * 0.24, 200, 140)
    c.arc(cx, cy - s * 0.34, cx + s * 0.08, cy - s * 0.24, 200, 140)


def souris(c, cx, cy, s, t):
    _style(c, t, s, "gris")
    c.circle(cx - s * 0.25, cy + s * 0.18, s * 0.2, stroke=1, fill=1)
    c.circle(cx + s * 0.25, cy + s * 0.18, s * 0.2, stroke=1, fill=1)
    _style(c, t, s, "rose")
    c.circle(cx - s * 0.25, cy + s * 0.18, s * 0.11, stroke=0, fill=1)
    c.circle(cx + s * 0.25, cy + s * 0.18, s * 0.11, stroke=0, fill=1)
    _style(c, t, s, "gris")
    p = lisse(c, _pts(cx, cy, s, [(0, 0.2), (0.27, 0.05), (0.2, -0.2), (0, -0.42), (-0.2, -0.2), (-0.27, 0.05)]))
    c.drawPath(p, stroke=1, fill=1)
    _oeil(c, cx - s * 0.1, cy - s * 0.02, s * 0.04)
    _oeil(c, cx + s * 0.1, cy - s * 0.02, s * 0.04)
    _encre(c)
    c.circle(cx, cy - s * 0.36, s * 0.05, stroke=0, fill=1)
    for dy in (-0.3, -0.36):
        c.line(cx - s * 0.08, cy + dy * s, cx - s * 0.36, cy + (dy + 0.03) * s)
        c.line(cx + s * 0.08, cy + dy * s, cx + s * 0.36, cy + (dy + 0.03) * s)


def chouette(c, cx, cy, s, t):
    _style(c, t, s, "marron")
    _poly(c, [(cx - s * 0.3, cy + s * 0.25), (cx - s * 0.28, cy + s * 0.48), (cx - s * 0.12, cy + s * 0.32)])
    _poly(c, [(cx + s * 0.3, cy + s * 0.25), (cx + s * 0.28, cy + s * 0.48), (cx + s * 0.12, cy + s * 0.32)])
    c.ellipse(cx - s * 0.33, cy - s * 0.46, cx + s * 0.33, cy + s * 0.38, stroke=1, fill=1)
    _style(c, t, s, "beige")
    c.ellipse(cx - s * 0.2, cy - s * 0.4, cx + s * 0.2, cy - s * 0.02, stroke=1, fill=1)
    c.setFillColor(white)
    c.circle(cx - s * 0.13, cy + s * 0.15, s * 0.12, stroke=1, fill=1)
    c.circle(cx + s * 0.13, cy + s * 0.15, s * 0.12, stroke=1, fill=1)
    _oeil(c, cx - s * 0.12, cy + s * 0.15, s * 0.055)
    _oeil(c, cx + s * 0.12, cy + s * 0.15, s * 0.055)
    _style(c, t, s, "orange")
    _poly(c, [(cx - s * 0.05, cy + s * 0.04), (cx + s * 0.05, cy + s * 0.04), (cx, cy - s * 0.07)])


def grenouille(c, cx, cy, s, t):
    _union(c, t, s, "vert", [
        lambda st, fi: c.ellipse(cx - s * 0.45, cy - s * 0.35, cx + s * 0.45, cy + s * 0.15, stroke=st, fill=fi),
        lambda st, fi: c.circle(cx - s * 0.22, cy + s * 0.18, s * 0.15, stroke=st, fill=fi),
        lambda st, fi: c.circle(cx + s * 0.22, cy + s * 0.18, s * 0.15, stroke=st, fill=fi),
    ])
    _style(c, t, s, None)
    c.circle(cx - s * 0.22, cy + s * 0.19, s * 0.09, stroke=1, fill=1)
    c.circle(cx + s * 0.22, cy + s * 0.19, s * 0.09, stroke=1, fill=1)
    _oeil(c, cx - s * 0.22, cy + s * 0.19, s * 0.045)
    _oeil(c, cx + s * 0.22, cy + s * 0.19, s * 0.045)
    c.arc(cx - s * 0.25, cy - s * 0.25, cx + s * 0.25, cy + s * 0.02, 205, 130)


def ours(c, cx, cy, s, t):
    _style(c, t, s, "marron")
    c.circle(cx - s * 0.27, cy + s * 0.27, s * 0.13, stroke=1, fill=1)
    c.circle(cx + s * 0.27, cy + s * 0.27, s * 0.13, stroke=1, fill=1)
    c.circle(cx, cy - s * 0.04, s * 0.38, stroke=1, fill=1)
    _style(c, t, s, "marron_c")
    c.ellipse(cx - s * 0.16, cy - s * 0.32, cx + s * 0.16, cy - s * 0.06, stroke=1, fill=1)
    _oeil(c, cx - s * 0.14, cy + s * 0.08, s * 0.045)
    _oeil(c, cx + s * 0.14, cy + s * 0.08, s * 0.045)
    _encre(c)
    c.ellipse(cx - s * 0.06, cy - s * 0.15, cx + s * 0.06, cy - s * 0.08, stroke=0, fill=1)
    c.line(cx, cy - s * 0.15, cx, cy - s * 0.22)


def tortue(c, cx, cy, s, t):
    _style(c, t, s, "vert")
    for dx in (-0.28, 0.18):
        c.roundRect(cx + dx * s, cy - s * 0.32, s * 0.12, s * 0.16, s * 0.04, stroke=1, fill=1)
    c.circle(cx + s * 0.36, cy - s * 0.04, s * 0.12, stroke=1, fill=1)
    _oeil(c, cx + s * 0.4, cy - s * 0.01, s * 0.03)
    _style(c, t, s, "vert_f")
    p = c.beginPath()
    p.moveTo(cx - s * 0.42, cy - s * 0.18)
    p.curveTo(cx - s * 0.4, cy + s * 0.32, cx + s * 0.3, cy + s * 0.32, cx + s * 0.32, cy - s * 0.18)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.line(cx - s * 0.14, cy - s * 0.18, cx - s * 0.1, cy + s * 0.18)
    c.line(cx + s * 0.06, cy - s * 0.18, cx + s * 0.02, cy + s * 0.18)
    c.line(cx - s * 0.35, cy + s * 0.0, cx + s * 0.26, cy + s * 0.0)


def poussin(c, cx, cy, s, t):
    _style(c, t, s, "orange")
    c.line(cx - s * 0.08, cy - s * 0.3, cx - s * 0.08, cy - s * 0.46)
    c.line(cx + s * 0.08, cy - s * 0.3, cx + s * 0.08, cy - s * 0.46)
    _union(c, t, s, "jaune", [
        lambda st, fi: c.circle(cx, cy - s * 0.1, s * 0.25, stroke=st, fill=fi),
        lambda st, fi: c.circle(cx + s * 0.05, cy + s * 0.22, s * 0.17, stroke=st, fill=fi),
    ])
    _oeil(c, cx + s * 0.1, cy + s * 0.26, s * 0.035)
    _style(c, t, s, "orange")
    _poly(c, [(cx + s * 0.2, cy + s * 0.24), (cx + s * 0.34, cy + s * 0.2), (cx + s * 0.2, cy + s * 0.15)])
    c.arc(cx - s * 0.18, cy - s * 0.2, cx + s * 0.06, cy + s * 0.02, 200, 120)


def chat(c, cx, cy, s, t):
    _style(c, t, s, "orange")
    _poly(c, [(cx - s * 0.36, cy + s * 0.05), (cx - s * 0.32, cy + s * 0.46), (cx - s * 0.08, cy + s * 0.25)])
    _poly(c, [(cx + s * 0.36, cy + s * 0.05), (cx + s * 0.32, cy + s * 0.46), (cx + s * 0.08, cy + s * 0.25)])
    c.ellipse(cx - s * 0.4, cy - s * 0.38, cx + s * 0.4, cy + s * 0.3, stroke=1, fill=1)
    _oeil(c, cx - s * 0.14, cy + s * 0.0, s * 0.05)
    _oeil(c, cx + s * 0.14, cy + s * 0.0, s * 0.05)
    _style(c, t, s, "rose")
    _poly(c, [(cx - s * 0.05, cy - s * 0.1), (cx + s * 0.05, cy - s * 0.1), (cx, cy - s * 0.16)])
    for dy in (-0.14, -0.2):
        c.line(cx - s * 0.1, cy + dy * s, cx - s * 0.38, cy + (dy + 0.02) * s)
        c.line(cx + s * 0.1, cy + dy * s, cx + s * 0.38, cy + (dy + 0.02) * s)


def renard(c, cx, cy, s, t):
    _style(c, t, s, "orange")
    _poly(c, [(cx - s * 0.4, cy + s * 0.12), (cx - s * 0.3, cy + s * 0.48), (cx - s * 0.08, cy + s * 0.25)])
    _poly(c, [(cx + s * 0.4, cy + s * 0.12), (cx + s * 0.3, cy + s * 0.48), (cx + s * 0.08, cy + s * 0.25)])
    p = lisse(c, _pts(cx, cy, s, [(-0.44, 0.15), (0, 0.3), (0.44, 0.15), (0.3, -0.12), (0, -0.44), (-0.3, -0.12)]))
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, None)
    for sg in (-1, 1):
        _poly(c, [(cx + sg * s * 0.4, cy + s * 0.1), (cx + sg * s * 0.05, cy - s * 0.12),
                  (cx + sg * s * 0.2, cy - s * 0.2)])
    _oeil(c, cx - s * 0.15, cy + s * 0.08, s * 0.045)
    _oeil(c, cx + s * 0.15, cy + s * 0.08, s * 0.045)
    _encre(c)
    c.circle(cx, cy - s * 0.36, s * 0.06, stroke=0, fill=1)


# =============================================================== buts des labyrinthes
def carotte(c, cx, cy, s, t):
    _style(c, t, s, "vert")
    for dx in (-0.08, 0, 0.08):
        c.ellipse(cx + dx * s - s * 0.05, cy + s * 0.2, cx + dx * s + s * 0.05, cy + s * 0.48, stroke=1, fill=1)
    _style(c, t, s, "orange")
    _poly(c, [(cx - s * 0.16, cy + s * 0.22), (cx + s * 0.16, cy + s * 0.22), (cx, cy - s * 0.48)])
    c.line(cx - s * 0.1, cy + s * 0.05, cx, cy + s * 0.05)
    c.line(cx, cy - s * 0.12, cx + s * 0.07, cy - s * 0.12)


def fromage(c, cx, cy, s, t):
    _style(c, t, s, "jaune")
    _poly(c, [(cx - s * 0.45, cy - s * 0.3), (cx + s * 0.45, cy - s * 0.3), (cx + s * 0.45, cy + s * 0.1),
              (cx - s * 0.45, cy - s * 0.05)])
    _poly(c, [(cx - s * 0.45, cy - s * 0.05), (cx + s * 0.45, cy + s * 0.1), (cx + s * 0.1, cy + s * 0.32)])
    c.setFillColor(white)
    for dx, dy, r in ((-0.2, -0.15, 0.07), (0.15, -0.12, 0.09), (0.32, -0.22, 0.04)):
        c.circle(cx + dx * s, cy + dy * s, r * s, stroke=1, fill=1)


def nid(c, cx, cy, s, t):
    _style(c, t, s, "beige")
    for dx in (-0.14, 0.0, 0.14):
        c.ellipse(cx + dx * s - s * 0.1, cy - s * 0.12, cx + dx * s + s * 0.1, cy + s * 0.2, stroke=1, fill=1)
    _style(c, t, s, "marron")
    p = c.beginPath()
    p.moveTo(cx - s * 0.46, cy)
    p.curveTo(cx - s * 0.4, cy - s * 0.4, cx + s * 0.4, cy - s * 0.4, cx + s * 0.46, cy)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    for i in range(4):
        y = cy - s * (0.06 + i * 0.07)
        c.line(cx - s * (0.38 - i * 0.05), y, cx + s * (0.38 - i * 0.05), y)


def mare(c, cx, cy, s, t):
    _style(c, t, s, "bleu")
    c.ellipse(cx - s * 0.47, cy - s * 0.3, cx + s * 0.47, cy + s * 0.18, stroke=1, fill=1)
    _style(c, t, s, "vert")
    c.wedge(cx - s * 0.2, cy - s * 0.16, cx + s * 0.08, cy + s * 0.06, 30, 320, stroke=1, fill=1)
    c.arc(cx + s * 0.12, cy - s * 0.2, cx + s * 0.38, cy - s * 0.08, 0, 180)


def miel(c, cx, cy, s, t):
    _style(c, t, s, "orange")
    p = lisse(c, _pts(cx, cy, s, [(-0.3, 0.2), (0.3, 0.2), (0.38, -0.15), (0.2, -0.42), (-0.2, -0.42), (-0.38, -0.15)]))
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "marron_c")
    c.roundRect(cx - s * 0.32, cy + s * 0.18, s * 0.64, s * 0.14, s * 0.05, stroke=1, fill=1)
    _style(c, t, s, None)
    c.roundRect(cx - s * 0.2, cy - s * 0.2, s * 0.4, s * 0.2, s * 0.04, stroke=1, fill=1)
    from generation.pdf_builder.text import ecrire
    from generation.pdf_builder import fonts
    ecrire(c, "MIEL", cx, cy - s * 0.15, fonts.TITRE, s * 0.12, align="center")


def feuille(c, cx, cy, s, t):
    _style(c, t, s, "vert")
    p = c.beginPath()
    p.moveTo(cx - s * 0.42, cy - s * 0.3)
    p.curveTo(cx - s * 0.4, cy + s * 0.35, cx + s * 0.2, cy + s * 0.45, cx + s * 0.45, cy + s * 0.4)
    p.curveTo(cx + s * 0.4, cy - s * 0.2, cx - s * 0.1, cy - s * 0.4, cx - s * 0.42, cy - s * 0.3)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.line(cx - s * 0.42, cy - s * 0.3, cx + s * 0.3, cy + s * 0.28)


def terrier(c, cx, cy, s, t):
    _style(c, t, s, "marron_c")
    p = c.beginPath()
    p.moveTo(cx - s * 0.48, cy - s * 0.3)
    p.curveTo(cx - s * 0.4, cy + s * 0.4, cx + s * 0.4, cy + s * 0.4, cx + s * 0.48, cy - s * 0.3)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    _encre(c)
    p = c.beginPath()
    p.moveTo(cx - s * 0.2, cy - s * 0.3)
    p.curveTo(cx - s * 0.2, cy + s * 0.1, cx + s * 0.2, cy + s * 0.1, cx + s * 0.2, cy - s * 0.3)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "vert")
    for dx in (-0.35, -0.3, 0.3, 0.36):
        c.line(cx + dx * s, cy - s * 0.3, cx + dx * s + s * 0.03, cy - s * 0.42)


def pelote(c, cx, cy, s, t):
    _style(c, t, s, "violet")
    c.circle(cx, cy, s * 0.36, stroke=1, fill=1)
    c.saveState()
    p = c.beginPath()
    p.circle(cx, cy, s * 0.36)
    c.clipPath(p, stroke=0, fill=0)
    for i in range(-3, 4):
        c.arc(cx - s * 0.8 + i * s * 0.12, cy - s * 0.6, cx + s * 0.2 + i * s * 0.12, cy + s * 0.6, -60, 120)
    c.restoreState()
    c.bezier(cx + s * 0.3, cy - s * 0.2, cx + s * 0.45, cy - s * 0.3, cx + s * 0.3, cy - s * 0.45, cx + s * 0.48, cy - s * 0.48)


# =============================================================== dinosaures
def trex(c, cx, cy, s, t):
    _style(c, t, s, "vert")
    p = lisse(c, _pts(cx, cy, s, [
        (-0.5, -0.02), (-0.25, 0.1), (0.0, 0.18), (0.12, 0.3), (0.2, 0.42), (0.45, 0.4), (0.47, 0.28),
        (0.3, 0.24), (0.24, 0.12), (0.2, -0.05), (0.12, -0.18), (0.14, -0.42), (0.2, -0.47), (0.04, -0.47),
        (-0.04, -0.25), (-0.16, -0.22), (-0.16, -0.42), (-0.1, -0.47), (-0.26, -0.47), (-0.28, -0.15),
        (-0.4, -0.08)]))
    c.drawPath(p, stroke=1, fill=1)
    _oeil(c, cx + s * 0.3, cy + s * 0.34, s * 0.035)
    c.line(cx + s * 0.32, cy + s * 0.27, cx + s * 0.44, cy + s * 0.28)
    c.line(cx + s * 0.2, cy + s * 0.05, cx + s * 0.3, cy - s * 0.01)


def diplodocus(c, cx, cy, s, t):
    _style(c, t, s, "bleu")
    p = lisse(c, _pts(cx, cy, s, [
        (-0.5, -0.05), (-0.2, 0.05), (0.08, 0.06), (0.22, 0.2), (0.28, 0.4), (0.4, 0.46), (0.48, 0.38),
        (0.36, 0.34), (0.32, 0.12), (0.24, -0.08), (0.22, -0.42), (0.1, -0.42), (0.08, -0.2), (-0.12, -0.2),
        (-0.14, -0.42), (-0.26, -0.42), (-0.26, -0.12), (-0.4, -0.08)]))
    c.drawPath(p, stroke=1, fill=1)
    _oeil(c, cx + s * 0.4, cy + s * 0.41, s * 0.03)


def triceratops(c, cx, cy, s, t):
    _style(c, t, s, "orange")
    p = lisse(c, _pts(cx, cy, s, [
        (-0.5, -0.05), (-0.2, 0.18), (0.1, 0.18), (0.22, 0.05), (0.18, -0.4), (0.06, -0.4), (0.04, -0.2),
        (-0.18, -0.2), (-0.2, -0.4), (-0.32, -0.4), (-0.32, -0.12)]))
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "jaune")
    c.circle(cx + s * 0.16, cy + s * 0.14, s * 0.2, stroke=1, fill=1)
    _style(c, t, s, "orange")
    p = lisse(c, _pts(cx, cy, s, [(0.18, 0.1), (0.36, 0.14), (0.48, 0.0), (0.4, -0.1), (0.24, -0.06)]))
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "beige")
    _poly(c, [(cx + s * 0.27, cy + s * 0.12), (cx + s * 0.46, cy + s * 0.3), (cx + s * 0.34, cy + s * 0.08)])
    _poly(c, [(cx + s * 0.42, cy + s * 0.0), (cx + s * 0.49, cy + s * 0.12), (cx + s * 0.46, cy - s * 0.04)])
    _oeil(c, cx + s * 0.3, cy + s * 0.02, s * 0.03)


def stegosaure(c, cx, cy, s, t):
    _style(c, t, s, "orange")
    for i, (x, h) in enumerate(((-0.3, 0.12), (-0.15, 0.2), (0.0, 0.22), (0.15, 0.16))):
        _poly(c, [(cx + (x - 0.08) * s, cy + s * 0.08), (cx + x * s, cy + (0.12 + h) * s),
                  (cx + (x + 0.08) * s, cy + s * 0.08)])
    _style(c, t, s, "vert")
    p = lisse(c, _pts(cx, cy, s, [
        (-0.5, -0.1), (-0.25, 0.12), (0.05, 0.16), (0.3, 0.02), (0.46, -0.02), (0.44, -0.12), (0.26, -0.12),
        (0.2, -0.38), (0.08, -0.38), (0.06, -0.22), (-0.16, -0.22), (-0.18, -0.38), (-0.3, -0.38),
        (-0.3, -0.16)]))
    c.drawPath(p, stroke=1, fill=1)
    _oeil(c, cx + s * 0.38, cy - s * 0.04, s * 0.025)


def oeuf(c, cx, cy, s, t):
    _style(c, t, s, "creme")
    p = lisse(c, _pts(cx, cy, s, [(0, 0.46), (0.26, 0.2), (0.32, -0.15), (0.18, -0.42), (0, -0.46),
                                  (-0.18, -0.42), (-0.32, -0.15), (-0.26, 0.2)]))
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "vert")
    for dx, dy, r in ((-0.1, 0.15, 0.06), (0.12, -0.05, 0.08), (-0.12, -0.22, 0.05), (0.08, 0.28, 0.04)):
        c.circle(cx + dx * s, cy + dy * s, r * s, stroke=1, fill=1)


def volcan(c, cx, cy, s, t):
    _style(c, t, s, "gris")
    for dx, dy, r in ((0.0, 0.3, 0.08), (0.08, 0.4, 0.06)):
        c.circle(cx + dx * s, cy + dy * s, r * s, stroke=1, fill=1)
    _style(c, t, s, "marron")
    _poly(c, [(cx - s * 0.47, cy - s * 0.42), (cx - s * 0.12, cy + s * 0.2), (cx + s * 0.12, cy + s * 0.2),
              (cx + s * 0.47, cy - s * 0.42)])
    _style(c, t, s, "rouge")
    _poly(c, [(cx - s * 0.12, cy + s * 0.2), (cx + s * 0.12, cy + s * 0.2), (cx + s * 0.06, cy + s * 0.02),
              (cx, cy + s * 0.1), (cx - s * 0.08, cy - s * 0.04)])


def fougere(c, cx, cy, s, t):
    _style(c, t, s, "vert")
    c.bezier(cx, cy - s * 0.48, cx - s * 0.02, cy - s * 0.1, cx + s * 0.05, cy + s * 0.2, cx + s * 0.02, cy + s * 0.46)
    for i in range(6):
        y = cy - s * 0.32 + i * s * 0.14
        L = s * (0.32 - i * 0.04)
        c.ellipse(cx - L, y - s * 0.035, cx, y + s * 0.035, stroke=1, fill=1)
        c.ellipse(cx, y - s * 0.035, cx + L, y + s * 0.035, stroke=1, fill=1)


def os(c, cx, cy, s, t):
    _union(c, t, s, "creme", [
        lambda st, fi: c.roundRect(cx - s * 0.32, cy - s * 0.07, s * 0.64, s * 0.14, s * 0.04, stroke=st, fill=fi),
        lambda st, fi: c.circle(cx - s * 0.36, cy + s * 0.08, s * 0.1, stroke=st, fill=fi),
        lambda st, fi: c.circle(cx - s * 0.36, cy - s * 0.08, s * 0.1, stroke=st, fill=fi),
        lambda st, fi: c.circle(cx + s * 0.36, cy + s * 0.08, s * 0.1, stroke=st, fill=fi),
        lambda st, fi: c.circle(cx + s * 0.36, cy - s * 0.08, s * 0.1, stroke=st, fill=fi),
    ])


PICTOS: dict[str, Dessinateur] = {
    "arbre": arbre, "fleur": fleur, "soleil": soleil, "nuage": nuage, "champignon": champignon,
    "maison": maison, "poisson": poisson, "oiseau": oiseau, "etoile": etoile, "coeur": coeur,
    "pomme": pomme, "escargot": escargot,
    "herisson": herisson, "lapin": lapin, "souris": souris, "chouette": chouette,
    "grenouille": grenouille, "ours": ours, "tortue": tortue, "poussin": poussin, "chat": chat,
    "renard": renard,
    "carotte": carotte, "fromage": fromage, "nid": nid, "mare": mare, "miel": miel,
    "feuille": feuille, "terrier": terrier, "pelote": pelote,
    "trex": trex, "diplodocus": diplodocus, "triceratops": triceratops, "stegosaure": stegosaure,
    "oeuf": oeuf, "volcan": volcan, "fougere": fougere, "os": os,
}


# Pictogrammes des cahiers-aventures espace, pirates et magie (module séparé).
from generation.pdf_builder.pictos_missions import PICTOS_MISSIONS  # noqa: E402

PICTOS.update(PICTOS_MISSIONS)


def dessiner(c: Canvas, kind: str, cx: float, cy: float, s: float, t: Theme) -> None:
    c.saveState()
    PICTOS[kind](c, cx, cy, s, t)
    c.restoreState()
