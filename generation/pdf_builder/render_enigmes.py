"""Rendu des énigmes : code secret, petits problèmes, chemin des nombres."""
from __future__ import annotations

from reportlab.lib.colors import white
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from generation.generators.enigmes import CheminNombres, CodeSecret, Probleme
from generation.pdf_builder import fonts, pictos
from generation.pdf_builder.layout import Rect
from generation.pdf_builder.render_common import case_reponse
from generation.pdf_builder.shapes import dessiner_figure
from generation.pdf_builder.text import ecrire, paragraphe
from generation.pdf_builder.theme import NOIR, Theme


def dessiner_code(c: Canvas, rect: Rect, code: CodeSecret, theme: Theme, solution: bool = False) -> None:
    # Clé : lettre au-dessus de son symbole.
    lettres = sorted(code.cle)
    n = len(lettres)
    par_ligne = min(n, 7)
    lignes_cle = (n + par_ligne - 1) // par_ligne
    cw = min(22 * mm, rect.w / par_ligne)
    ch = 26 * mm
    ecrire(c, "La clé du code :", rect.x, rect.top - 12, fonts.TITRE, 14)
    y_top = rect.top - 22
    for i, l in enumerate(lettres):
        r, col = divmod(i, par_ligne)
        x = rect.cx + (col - par_ligne / 2) * cw
        y = y_top - r * ch
        c.saveState()
        c.setLineWidth(1)
        c.setFillColor(white if theme.eco else theme.accent_clair)
        c.roundRect(x + 2, y - ch + 4, cw - 4, ch - 4, 4, stroke=1, fill=1)
        c.restoreState()
        ecrire(c, l, x + cw / 2, y - 10 * mm, fonts.TITRE, 20, align="center")
        dessiner_figure(c, code.cle[l], x + cw / 2, y - 17.5 * mm, 10 * mm)
    y = y_top - lignes_cle * ch - 10 * mm
    ecrire(c, "Le message secret :", rect.x, y, fonts.TITRE, 14)
    # Message : symbole au-dessus d'une case à remplir.
    m = len(code.code)
    sw = min(22 * mm, rect.w / m)
    y_sym = y - 16 * mm
    for i, s in enumerate(code.code):
        x = rect.cx + (i - m / 2) * sw
        if s is None:
            continue
        dessiner_figure(c, s, x + sw / 2, y_sym, min(13 * mm, sw * 0.7))
        case_reponse(c, x + sw * 0.12, y_sym - 26 * mm, sw * 0.76, 16 * mm,
                     code.message[i] if solution else None, 20)


def dessiner_problemes(c: Canvas, rect: Rect, problemes: list[Probleme], theme: Theme,
                       illustrations: list[str] | None = None, solution: bool = False) -> None:
    n = len(problemes)
    zones = rect.split_v(n, gap=6 * mm)
    for i, (p, z) in enumerate(zip(problemes, zones)):
        c.saveState()
        c.setLineWidth(1.1)
        c.roundRect(z.x, z.y, z.w, z.h, 8, stroke=1, fill=0)
        c.restoreState()
        interieur = z.inset(8 * mm, 5 * mm)
        if illustrations:
            pictos.dessiner(c, illustrations[i % len(illustrations)], interieur.right - 14 * mm,
                            interieur.top - 14 * mm, 22 * mm, theme)
        texte = f"<b>Énigme {i + 1}.</b> {p.texte}"
        larg = interieur.w - (32 * mm if illustrations else 0)
        paragraphe(c, texte, Rect(interieur.x, interieur.y, larg, interieur.h), fonts.TEXTE, 14.5)
        hy = interieur.y + 2
        ecrire(c, "Ma réponse :", interieur.x, hy + 6 * mm, fonts.TITRE_DEMI, 13)
        case_reponse(c, interieur.x + 32 * mm, hy, 22 * mm, 15 * mm, str(p.reponse) if solution else None, 20)
        if p.unite:
            ecrire(c, p.unite, interieur.x + 57 * mm, hy + 5.5 * mm, fonts.TEXTE, 13)


def dessiner_chemin(c: Canvas, rect: Rect, ch: CheminNombres, theme: Theme, solution: bool = False,
                    depart: str = "trex", arrivee: str = "oeuf") -> None:
    h, w = len(ch.grille), len(ch.grille[0])
    marge_pic = 26 * mm
    cell = min((rect.w - marge_pic * 2) / w, rect.h / h, 24 * mm)
    x0 = rect.cx - w * cell / 2
    y0 = rect.cy + h * cell / 2
    c.saveState()
    for r in range(h):
        for col in range(w):
            x, y = x0 + col * cell, y0 - (r + 1) * cell
            on = solution and (r, col) in ch.chemin
            if on and not theme.eco:
                c.setFillColor(theme.accent_clair)
                c.rect(x, y, cell, cell, stroke=0, fill=1)
            ecrire(c, str(ch.grille[r][col]), x + cell / 2, y + cell / 2 - cell * 0.15, fonts.TITRE,
                   cell * 0.42, align="center")
    c.setStrokeColor(NOIR)
    c.setLineWidth(1.2)
    for r in range(h + 1):
        c.line(x0, y0 - r * cell, x0 + w * cell, y0 - r * cell)
    for col in range(w + 1):
        c.line(x0 + col * cell, y0, x0 + col * cell, y0 - h * cell)
    if solution:
        c.setStrokeColor(theme.trace_solution)
        c.setLineWidth(3)
        c.setLineCap(1)
        c.setLineJoin(1)
        p = c.beginPath()
        for i, (r, col) in enumerate(ch.chemin):
            pt = (x0 + (col + 0.5) * cell, y0 - (r + 0.5) * cell + cell * 0.25)
            p.moveTo(*pt) if i == 0 else p.lineTo(*pt)
        c.drawPath(p, stroke=1, fill=0)
    c.restoreState()
    dl, al = ch.depart[0], ch.arrivee[0]
    pictos.dessiner(c, depart, x0 - marge_pic / 2, y0 - (dl + 0.5) * cell, 20 * mm, theme)
    pictos.dessiner(c, arrivee, x0 + w * cell + marge_pic / 2, y0 - (al + 0.5) * cell, 20 * mm, theme)
    # Repères des cases de départ et d'arrivée.
    c.saveState()
    c.setLineWidth(2.6)
    c.setStrokeColor(NOIR)
    for (r, col) in (ch.depart, ch.arrivee):
        c.rect(x0 + col * cell + 2, y0 - (r + 1) * cell + 2, cell - 4, cell - 4, stroke=1, fill=0)
    c.restoreState()
