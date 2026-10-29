"""Pictogrammes des cahiers-aventures « Mission espace », « Mission pirates » et « Mission magie ».

Mêmes conventions que pictos.py : dessin centré en (cx, cy) dans un carré de côté `s`,
contours noirs francs, aplats doux (blancs en version économie d'encre).
"""
from __future__ import annotations

import math

from reportlab.lib.colors import white

from generation.pdf_builder.pictos import _encre, _lw, _oeil, _poly, _pts, _style, _union, lisse
from generation.pdf_builder.theme import NOIR


def _etoile_pts(cx, cy, r_ext, r_int, n=5, rot=math.pi / 2):
    return [(cx + math.cos(rot + i * math.pi / n) * (r_ext if i % 2 == 0 else r_int),
             cy + math.sin(rot + i * math.pi / n) * (r_ext if i % 2 == 0 else r_int)) for i in range(2 * n)]


def _sourire(c, x, y, r):
    c.arc(x - r, y - r, x + r, y + r, 200, 140)


# =============================================================== espace
def fusee(c, cx, cy, s, t):
    _style(c, t, s, "orange")  # flamme
    p = lisse(c, _pts(cx, cy, s, [(-0.08, -0.3), (0.0, -0.49), (0.08, -0.3)]))
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "rouge")  # ailerons
    _poly(c, _pts(cx, cy, s, [(-0.14, -0.06), (-0.3, -0.24), (-0.3, -0.36), (-0.12, -0.28)]))
    _poly(c, _pts(cx, cy, s, [(0.14, -0.06), (0.3, -0.24), (0.3, -0.36), (0.12, -0.28)]))
    _style(c, t, s, "gris")  # corps
    p = lisse(c, _pts(cx, cy, s, [(0.0, 0.48), (0.12, 0.3), (0.16, 0.05), (0.14, -0.3), (-0.14, -0.3),
                                  (-0.16, 0.05), (-0.12, 0.3)]))
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "rouge")  # pointe
    p = c.beginPath()
    p.moveTo(cx - s * 0.115, cy + s * 0.3)
    p.curveTo(cx - s * 0.08, cy + s * 0.4, cx - s * 0.03, cy + s * 0.46, cx, cy + s * 0.48)
    p.curveTo(cx + s * 0.03, cy + s * 0.46, cx + s * 0.08, cy + s * 0.4, cx + s * 0.115, cy + s * 0.3)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "bleu")  # hublot
    c.circle(cx, cy + s * 0.1, s * 0.085, stroke=1, fill=1)


def planete(c, cx, cy, s, t):
    def anneau(debut, etendue):
        c.saveState()
        c.translate(cx, cy)
        c.rotate(-18)
        c.setLineWidth(_lw(s) * 2.6)
        c.setStrokeColor(NOIR)
        c.arc(-s * 0.48, -s * 0.13, s * 0.48, s * 0.13, debut, etendue)
        col = t.remplissage("#FFD43B")
        c.setLineWidth(_lw(s) * 1.0)
        c.setStrokeColor(col if col is not None else white)
        c.arc(-s * 0.48, -s * 0.13, s * 0.48, s * 0.13, debut + 1, etendue - 2)
        c.restoreState()

    anneau(0, 180)  # partie arrière de l'anneau, cachée en partie par la planète
    _style(c, t, s, "violet")
    c.circle(cx, cy, s * 0.27, stroke=1, fill=1)
    anneau(180, 180)  # partie avant
    _style(c, t, s, "violet")
    for dx, dy, r in ((-0.1, 0.12, 0.05), (0.1, 0.16, 0.035)):
        c.circle(cx + dx * s, cy + dy * s, r * s, stroke=1, fill=0)


def lune(c, cx, cy, s, t):
    _style(c, t, s, "jaune")
    p = c.beginPath()
    r1, r2 = s * 0.44, s * 0.389
    p.arc(cx - r1, cy - r1, cx + r1, cy + r1, 60, 240)
    # Arc intérieur : cercle passant par les deux pointes du croissant.
    ox = cx + s * 0.3
    p.arcTo(ox - r2, cy - r2, ox + r2, cy + r2, 258.1, -156.2)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    _oeil(c, cx - s * 0.2, cy + s * 0.06, s * 0.03)
    _sourire(c, cx - s * 0.19, cy - s * 0.07, s * 0.06)


def comete(c, cx, cy, s, t):
    _style(c, t, s, "bleu")
    p = lisse(c, _pts(cx, cy, s, [(0.18, 0.28), (-0.2, 0.08), (-0.48, -0.42), (-0.06, -0.12), (0.3, 0.1)]))
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "jaune")
    _poly(c, _etoile_pts(cx + s * 0.22, cy + s * 0.22, s * 0.25, s * 0.11))


def soucoupe(c, cx, cy, s, t):
    _style(c, t, s, "bleu")
    p = c.beginPath()
    p.moveTo(cx - s * 0.2, cy + s * 0.04)
    p.curveTo(cx - s * 0.2, cy + s * 0.34, cx + s * 0.2, cy + s * 0.34, cx + s * 0.2, cy + s * 0.04)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "gris")
    c.ellipse(cx - s * 0.47, cy - s * 0.14, cx + s * 0.47, cy + s * 0.1, stroke=1, fill=1)
    _style(c, t, s, "jaune")
    for dx in (-0.28, -0.1, 0.1, 0.28):
        c.circle(cx + dx * s, cy - s * 0.02, s * 0.04, stroke=1, fill=1)
    c.line(cx - s * 0.2, cy - s * 0.12, cx - s * 0.28, cy - s * 0.3)
    c.line(cx + s * 0.2, cy - s * 0.12, cx + s * 0.28, cy - s * 0.3)


def alien(c, cx, cy, s, t):
    _style(c, t, s, "vert")
    for sx in (-1, 1):  # antennes
        c.line(cx + sx * s * 0.1, cy + s * 0.3, cx + sx * s * 0.2, cy + s * 0.44)
        c.circle(cx + sx * s * 0.2, cy + s * 0.44, s * 0.04, stroke=1, fill=1)
    c.roundRect(cx - s * 0.18, cy - s * 0.46, s * 0.36, s * 0.3, s * 0.1, stroke=1, fill=1)
    c.ellipse(cx - s * 0.28, cy - s * 0.18, cx + s * 0.28, cy + s * 0.34, stroke=1, fill=1)
    c.saveState()
    c.setFillColor(white)
    for sx in (-1, 1):
        c.ellipse(cx + sx * s * 0.12 - s * 0.07, cy + s * 0.02, cx + sx * s * 0.12 + s * 0.07, cy + s * 0.18,
                  stroke=1, fill=1)
    c.restoreState()
    for sx in (-1, 1):
        _oeil(c, cx + sx * s * 0.12, cy + s * 0.09, s * 0.035)
    _sourire(c, cx, cy - s * 0.02, s * 0.07)


def robot(c, cx, cy, s, t):
    _style(c, t, s, "gris")
    c.line(cx, cy + s * 0.32, cx, cy + s * 0.42)
    _style(c, t, s, "rouge")
    c.circle(cx, cy + s * 0.44, s * 0.04, stroke=1, fill=1)
    _style(c, t, s, "gris")
    c.roundRect(cx - s * 0.32, cy - s * 0.32, s * 0.08, s * 0.24, s * 0.03, stroke=1, fill=1)
    c.roundRect(cx + s * 0.24, cy - s * 0.32, s * 0.08, s * 0.24, s * 0.03, stroke=1, fill=1)
    c.roundRect(cx - s * 0.22, cy - s * 0.46, s * 0.44, s * 0.4, s * 0.05, stroke=1, fill=1)
    _style(c, t, s, "bleu")
    c.roundRect(cx - s * 0.2, cy - s * 0.04, s * 0.4, s * 0.36, s * 0.07, stroke=1, fill=1)
    c.saveState()
    c.setFillColor(white)
    c.circle(cx - s * 0.09, cy + s * 0.16, s * 0.055, stroke=1, fill=1)
    c.circle(cx + s * 0.09, cy + s * 0.16, s * 0.055, stroke=1, fill=1)
    c.restoreState()
    _oeil(c, cx - s * 0.09, cy + s * 0.16, s * 0.025)
    _oeil(c, cx + s * 0.09, cy + s * 0.16, s * 0.025)
    c.rect(cx - s * 0.08, cy + s * 0.02, s * 0.16, s * 0.05, stroke=1, fill=0)
    _style(c, t, s, "jaune")
    c.circle(cx, cy - s * 0.26, s * 0.06, stroke=1, fill=1)


# =============================================================== pirates
def bateau(c, cx, cy, s, t):
    _style(c, t, s, "rouge")  # drapeau
    _poly(c, _pts(cx, cy, s, [(0.02, 0.47), (0.2, 0.42), (0.02, 0.37)]))
    c.line(cx, cy - s * 0.12, cx, cy + s * 0.48)  # mât
    _style(c, t, s, "creme")
    _poly(c, _pts(cx, cy, s, [(0.03, 0.34), (0.34, -0.06), (0.03, -0.06)]))
    _poly(c, _pts(cx, cy, s, [(-0.03, 0.28), (-0.03, -0.06), (-0.28, -0.06)]))
    _style(c, t, s, "marron")
    p = c.beginPath()
    p.moveTo(cx - s * 0.47, cy - s * 0.1)
    p.lineTo(cx + s * 0.47, cy - s * 0.1)
    p.curveTo(cx + s * 0.38, cy - s * 0.32, cx + s * 0.2, cy - s * 0.36, cx, cy - s * 0.36)
    p.curveTo(cx - s * 0.2, cy - s * 0.36, cx - s * 0.38, cy - s * 0.32, cx - s * 0.47, cy - s * 0.1)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "creme")
    for dx in (-0.22, 0.0, 0.22):
        c.circle(cx + dx * s, cy - s * 0.2, s * 0.04, stroke=1, fill=1)
    _style(c, t, s, "bleu")
    c.bezier(cx - s * 0.48, cy - s * 0.44, cx - s * 0.3, cy - s * 0.38, cx - s * 0.15, cy - s * 0.5, cx, cy - s * 0.44)
    c.bezier(cx, cy - s * 0.44, cx + s * 0.15, cy - s * 0.38, cx + s * 0.3, cy - s * 0.5, cx + s * 0.48, cy - s * 0.44)


def coffre(c, cx, cy, s, t):
    _style(c, t, s, "marron")
    c.rect(cx - s * 0.42, cy - s * 0.4, s * 0.84, s * 0.42, stroke=1, fill=1)
    p = c.beginPath()
    p.moveTo(cx - s * 0.42, cy + s * 0.02)
    p.curveTo(cx - s * 0.42, cy + s * 0.36, cx + s * 0.42, cy + s * 0.36, cx + s * 0.42, cy + s * 0.02)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "jaune")
    for dx in (-0.3, 0.3):
        c.rect(cx + dx * s - s * 0.05, cy - s * 0.4, s * 0.1, s * 0.42, stroke=1, fill=1)
    c.rect(cx - s * 0.42, cy - s * 0.02, s * 0.84, s * 0.07, stroke=1, fill=1)
    c.roundRect(cx - s * 0.08, cy - s * 0.14, s * 0.16, s * 0.18, s * 0.03, stroke=1, fill=1)
    _encre(c)
    c.circle(cx, cy - s * 0.05, s * 0.025, stroke=0, fill=1)


def perroquet(c, cx, cy, s, t):
    _style(c, t, s, "bleu")
    for dx in (-0.06, 0.0, 0.06):  # queue
        p = lisse(c, _pts(cx, cy, s, [(dx - 0.03, -0.2), (dx - 0.06, -0.48), (dx + 0.02, -0.48), (dx + 0.04, -0.2)]))
        c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "rouge")
    c.ellipse(cx - s * 0.2, cy - s * 0.3, cx + s * 0.16, cy + s * 0.2, stroke=1, fill=1)
    c.circle(cx + s * 0.04, cy + s * 0.27, s * 0.17, stroke=1, fill=1)
    _style(c, t, s, "vert")
    p = lisse(c, _pts(cx, cy, s, [(-0.18, 0.08), (-0.02, 0.02), (-0.02, -0.22), (-0.16, -0.2)]))
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "jaune")
    p = c.beginPath()
    p.moveTo(cx + s * 0.17, cy + s * 0.32)
    p.curveTo(cx + s * 0.34, cy + s * 0.32, cx + s * 0.34, cy + s * 0.12, cx + s * 0.24, cy + s * 0.08)
    p.lineTo(cx + s * 0.17, cy + s * 0.2)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    c.saveState()
    c.setFillColor(white)
    c.circle(cx + s * 0.08, cy + s * 0.3, s * 0.055, stroke=1, fill=1)
    c.restoreState()
    _oeil(c, cx + s * 0.09, cy + s * 0.3, s * 0.03)
    _style(c, t, s, "marron")
    c.roundRect(cx - s * 0.3, cy - s * 0.36, s * 0.56, s * 0.06, s * 0.03, stroke=1, fill=1)


def ancre(c, cx, cy, s, t):
    def trait(largeur, couleur):
        c.saveState()
        c.setLineCap(1)
        c.setLineWidth(largeur)
        c.setStrokeColor(couleur)
        c.circle(cx, cy + s * 0.37, s * 0.08, stroke=1, fill=0)
        c.line(cx, cy + s * 0.29, cx, cy - s * 0.42)
        c.line(cx - s * 0.18, cy + s * 0.16, cx + s * 0.18, cy + s * 0.16)
        c.arc(cx - s * 0.34, cy - s * 0.44, cx + s * 0.34, cy + s * 0.24, 198, 144)
        c.restoreState()

    trait(s * 0.1, NOIR)
    col = t.remplissage("#CED4DA")
    trait(s * 0.1 - _lw(s) * 2, col if col is not None else white)
    _style(c, t, s, "gris")
    for sx in (-1, 1):
        _poly(c, _pts(cx, cy, s, [(sx * 0.42, -0.04), (sx * 0.22, -0.14), (sx * 0.4, -0.26)]))


def piece(c, cx, cy, s, t):
    _style(c, t, s, "jaune")
    c.circle(cx, cy, s * 0.42, stroke=1, fill=1)
    c.circle(cx, cy, s * 0.32, stroke=1, fill=0)
    _poly(c, _etoile_pts(cx, cy - s * 0.01, s * 0.2, s * 0.09))


def palmier(c, cx, cy, s, t):
    _style(c, t, s, "marron")
    for i in range(5):
        y = cy - s * 0.46 + i * s * 0.12
        x = cx + s * 0.03 * i
        c.roundRect(x - s * 0.06, y, s * 0.12, s * 0.13, s * 0.03, stroke=1, fill=1)
    top = (cx + s * 0.13, cy + s * 0.16)
    _style(c, t, s, "vert")
    for ang in (160, 120, 60, 20, 200, -20):
        a = math.radians(ang)
        L = s * 0.36
        ex, ey = top[0] + math.cos(a) * L, top[1] + math.sin(a) * L * 0.75
        nx, ny = -math.sin(a) * s * 0.07, math.cos(a) * s * 0.07
        mx, my = (top[0] + ex) / 2, (top[1] + ey) / 2
        p = lisse(c, [top, (mx + nx, my + ny), (ex, ey), (mx - nx * 0.3, my - ny * 0.3)])
        c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "marron_c")
    for dx, dy in ((-0.05, -0.04), (0.06, -0.06)):
        c.circle(top[0] + dx * s, top[1] + dy * s, s * 0.05, stroke=1, fill=1)


def crabe(c, cx, cy, s, t):
    _style(c, t, s, "rouge")
    for sx in (-1, 1):
        for i in range(3):
            y = cy - s * 0.08 - i * s * 0.08
            c.line(cx + sx * s * 0.22, y, cx + sx * s * 0.42, y - s * 0.1)
        c.line(cx + sx * s * 0.2, cy + s * 0.04, cx + sx * s * 0.34, cy + s * 0.2)
        p = c.beginPath()  # pince
        px, py = cx + sx * s * 0.36, cy + s * 0.3
        p.circle(px, py, s * 0.1)
        c.drawPath(p, stroke=1, fill=1)
        c.saveState()
        c.setFillColor(white)
        _poly(c, [(px, py), (px + sx * s * 0.11, py + s * 0.06), (px + sx * s * 0.02, py + s * 0.12)])
        c.restoreState()
    c.ellipse(cx - s * 0.26, cy - s * 0.26, cx + s * 0.26, cy + s * 0.1, stroke=1, fill=1)
    for sx in (-1, 1):
        c.line(cx + sx * s * 0.08, cy + s * 0.08, cx + sx * s * 0.1, cy + s * 0.18)
        c.saveState()
        c.setFillColor(white)
        c.circle(cx + sx * s * 0.1, cy + s * 0.21, s * 0.05, stroke=1, fill=1)
        c.restoreState()
        _oeil(c, cx + sx * s * 0.1, cy + s * 0.21, s * 0.025)
    _sourire(c, cx, cy - s * 0.06, s * 0.07)


def carte(c, cx, cy, s, t):
    _style(c, t, s, "creme")
    p = lisse(c, _pts(cx, cy, s, [(-0.44, 0.34), (-0.15, 0.38), (0.15, 0.33), (0.44, 0.37), (0.42, 0.0),
                                  (0.45, -0.36), (0.15, -0.32), (-0.15, -0.37), (-0.44, -0.33), (-0.41, 0.0)]))
    c.drawPath(p, stroke=1, fill=1)
    c.saveState()
    c.setDash(s * 0.04, s * 0.035)
    c.bezier(cx - s * 0.32, cy - s * 0.22, cx - s * 0.1, cy + s * 0.25, cx + s * 0.05, cy - s * 0.25, cx + s * 0.2, cy + s * 0.1)
    c.restoreState()
    c.saveState()
    c.setLineWidth(_lw(s) * 2.2)
    col = t.remplissage("#F03E3E")
    c.setStrokeColor(col if col is not None else NOIR)
    d = s * 0.07
    x, y = cx + s * 0.26, cy + s * 0.16
    c.line(x - d, y - d, x + d, y + d)
    c.line(x - d, y + d, x + d, y - d)
    c.restoreState()


# =============================================================== magie
def dragon(c, cx, cy, s, t):
    _style(c, t, s, "violet")  # aile
    _poly(c, _pts(cx, cy, s, [(-0.12, 0.12), (-0.02, 0.46), (0.06, 0.3), (0.16, 0.38), (0.12, 0.1)]))
    _style(c, t, s, "orange")  # pics
    for x in (-0.36, -0.24):
        _poly(c, _pts(cx, cy, s, [(x - 0.05, -0.02 + (x + 0.5) * 0.3), (x, 0.08 + (x + 0.5) * 0.3),
                                  (x + 0.05, 0.0 + (x + 0.5) * 0.3)]))
    _style(c, t, s, "vert")
    p = lisse(c, _pts(cx, cy, s, [
        (-0.5, -0.06), (-0.28, 0.08), (-0.05, 0.12), (0.12, 0.16), (0.2, 0.32), (0.36, 0.36), (0.47, 0.26),
        (0.42, 0.14), (0.28, 0.14), (0.24, 0.02), (0.2, -0.2), (0.18, -0.42), (0.06, -0.42), (0.04, -0.26),
        (-0.14, -0.26), (-0.16, -0.42), (-0.28, -0.42), (-0.28, -0.18), (-0.4, -0.12)]))
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "jaune")  # ventre
    c.ellipse(cx - s * 0.12, cy - s * 0.2, cx + s * 0.2, cy + s * 0.06, stroke=1, fill=1)
    _oeil(c, cx + s * 0.32, cy + s * 0.28, s * 0.035)
    _sourire(c, cx + s * 0.38, cy + s * 0.22, s * 0.05)


def baguette(c, cx, cy, s, t):
    c.saveState()
    c.translate(cx - s * 0.08, cy - s * 0.08)
    c.rotate(45)
    _style(c, t, s, "marron")
    c.roundRect(-s * 0.04, -s * 0.38, s * 0.08, s * 0.5, s * 0.03, stroke=1, fill=1)
    _style(c, t, s, "creme")
    c.roundRect(-s * 0.045, -s * 0.38, s * 0.09, s * 0.12, s * 0.03, stroke=1, fill=1)
    c.restoreState()
    _style(c, t, s, "jaune")
    _poly(c, _etoile_pts(cx + s * 0.2, cy + s * 0.2, s * 0.25, s * 0.11))
    _style(c, t, s, "rose")
    for dx, dy, r in ((-0.22, 0.34, 0.06), (0.4, -0.1, 0.05), (0.05, 0.44, 0.04)):
        _poly(c, _etoile_pts(cx + dx * s, cy + dy * s, r * s * 1.4, r * s * 0.55, n=4))


def chapeau(c, cx, cy, s, t):
    _style(c, t, s, "violet")
    c.ellipse(cx - s * 0.47, cy - s * 0.44, cx + s * 0.47, cy - s * 0.24, stroke=1, fill=1)
    p = c.beginPath()
    p.moveTo(cx - s * 0.28, cy - s * 0.34)
    p.curveTo(cx - s * 0.16, cy - s * 0.0, cx - s * 0.08, cy + s * 0.3, cx + s * 0.16, cy + s * 0.48)
    p.curveTo(cx + s * 0.08, cy + s * 0.2, cx + s * 0.2, cy - s * 0.0, cx + s * 0.28, cy - s * 0.34)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    _style(c, t, s, "jaune")
    c.roundRect(cx - s * 0.27, cy - s * 0.34, s * 0.54, s * 0.08, s * 0.03, stroke=1, fill=1)
    _poly(c, _etoile_pts(cx - s * 0.02, cy + s * 0.02, s * 0.1, s * 0.045))
    _poly(c, _etoile_pts(cx + s * 0.1, cy + s * 0.22, s * 0.06, s * 0.027))


def chateau(c, cx, cy, s, t):
    _style(c, t, s, "gris")
    c.rect(cx - s * 0.28, cy - s * 0.46, s * 0.56, s * 0.42, stroke=1, fill=1)
    for i in range(4):  # créneaux
        c.rect(cx - s * 0.26 + i * s * 0.15, cy - s * 0.04, s * 0.08, s * 0.07, stroke=1, fill=1)
    for sx in (-1, 1):
        x = cx + sx * s * 0.34
        c.rect(x - s * 0.1, cy - s * 0.46, s * 0.2, s * 0.62, stroke=1, fill=1)
        _style(c, t, s, "violet")
        _poly(c, [(x - s * 0.13, cy + s * 0.16), (x, cy + s * 0.46), (x + s * 0.13, cy + s * 0.16)])
        _style(c, t, s, "jaune")
        c.roundRect(x - s * 0.035, cy - s * 0.12, s * 0.07, s * 0.12, s * 0.03, stroke=1, fill=1)
        _style(c, t, s, "gris")
    _style(c, t, s, "marron")
    p = c.beginPath()
    p.moveTo(cx - s * 0.1, cy - s * 0.46)
    p.lineTo(cx - s * 0.1, cy - s * 0.26)
    p.curveTo(cx - s * 0.1, cy - s * 0.14, cx + s * 0.1, cy - s * 0.14, cx + s * 0.1, cy - s * 0.26)
    p.lineTo(cx + s * 0.1, cy - s * 0.46)
    p.close()
    c.drawPath(p, stroke=1, fill=1)


def potion(c, cx, cy, s, t):
    _style(c, t, s, "marron")
    c.roundRect(cx - s * 0.08, cy + s * 0.3, s * 0.16, s * 0.14, s * 0.03, stroke=1, fill=1)
    _union(c, t, s, "rose", [
        lambda st, fi: c.circle(cx, cy - s * 0.14, s * 0.32, stroke=st, fill=fi),
        lambda st, fi: c.rect(cx - s * 0.1, cy + s * 0.08, s * 0.2, s * 0.24, stroke=st, fill=fi),
    ])
    c.saveState()
    c.setFillColor(white)
    c.setStrokeColor(NOIR)
    c.setLineWidth(_lw(s))
    p = c.beginPath()  # partie vide du flacon (au-dessus du liquide)
    p.moveTo(cx - s * 0.1, cy + s * 0.31)
    p.lineTo(cx - s * 0.1, cy + s * 0.15)
    p.curveTo(cx - s * 0.2, cy + s * 0.13, cx - s * 0.27, cy + s * 0.06, cx - s * 0.3, cy - s * 0.02)
    p.lineTo(cx + s * 0.3, cy - s * 0.02)
    p.curveTo(cx + s * 0.27, cy + s * 0.06, cx + s * 0.2, cy + s * 0.13, cx + s * 0.1, cy + s * 0.15)
    p.lineTo(cx + s * 0.1, cy + s * 0.31)
    p.close()
    c.drawPath(p, stroke=0, fill=1)
    c.line(cx - s * 0.3, cy - s * 0.02, cx + s * 0.3, cy - s * 0.02)
    c.restoreState()
    for dx, dy, r in ((-0.1, -0.16, 0.04), (0.08, -0.26, 0.05), (0.12, -0.1, 0.03)):
        c.circle(cx + dx * s, cy + dy * s, r * s, stroke=1, fill=0)


def cristal(c, cx, cy, s, t):
    _style(c, t, s, "bleu")
    pts = _pts(cx, cy, s, [(-0.3, 0.2), (-0.14, 0.38), (0.14, 0.38), (0.3, 0.2), (0.0, -0.46)])
    _poly(c, pts)
    c.line(cx - s * 0.3, cy + s * 0.2, cx + s * 0.3, cy + s * 0.2)
    for a, b in (((-0.14, 0.38), (-0.08, 0.2)), ((0.14, 0.38), (0.08, 0.2)), ((-0.08, 0.2), (0.0, -0.46)),
                 ((0.08, 0.2), (0.0, -0.46))):
        c.line(cx + a[0] * s, cy + a[1] * s, cx + b[0] * s, cy + b[1] * s)


def grimoire(c, cx, cy, s, t):
    _style(c, t, s, "creme")  # tranche des pages
    c.rect(cx - s * 0.32, cy - s * 0.42, s * 0.72, s * 0.08, stroke=1, fill=1)
    _style(c, t, s, "violet")
    c.roundRect(cx - s * 0.36, cy - s * 0.34, s * 0.76, s * 0.76, s * 0.05, stroke=1, fill=1)
    _style(c, t, s, "marron")
    c.rect(cx - s * 0.36, cy - s * 0.34, s * 0.1, s * 0.76, stroke=1, fill=1)
    _style(c, t, s, "jaune")
    _poly(c, _etoile_pts(cx + s * 0.07, cy + s * 0.06, s * 0.18, s * 0.08))
    for dx, dy in ((-0.14, 0.32), (0.3, 0.32), (-0.14, -0.24), (0.3, -0.24)):
        c.circle(cx + dx * s, cy + dy * s, s * 0.03, stroke=1, fill=1)


PICTOS_MISSIONS = {
    "fusee": fusee, "planete": planete, "lune": lune, "comete": comete, "soucoupe": soucoupe,
    "alien": alien, "robot": robot,
    "bateau": bateau, "coffre": coffre, "perroquet": perroquet, "ancre": ancre, "piece": piece,
    "palmier": palmier, "crabe": crabe, "carte": carte,
    "dragon": dragon, "baguette": baguette, "chapeau": chapeau, "chateau": chateau, "potion": potion,
    "cristal": cristal, "grimoire": grimoire,
}
