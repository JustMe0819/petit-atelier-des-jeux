"""Rendu des jeux d'observation (différences, comptage) et des coloriages codés."""
from __future__ import annotations

from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from generation.generators.coloriage import ColoriageCode
from generation.generators.observation import JeuComptage, JeuDifferences, Scene, nom
from generation.pdf_builder import fonts, pictos
from generation.pdf_builder.layout import Rect
from generation.pdf_builder.render_common import case_reponse, entourer
from generation.pdf_builder.text import ecrire
from generation.pdf_builder.theme import COULEURS_CRAYON, NOIR, Theme


def dessiner_scene(c: Canvas, rect: Rect, scene: Scene, theme: Theme, cadre: bool = True) -> None:
    if cadre:
        c.saveState()
        c.setLineWidth(1.6)
        c.setStrokeColor(NOIR)
        c.roundRect(rect.x, rect.y, rect.w, rect.h, 6, stroke=1, fill=0)
        c.restoreState()
    slot = min(rect.w / scene.colonnes, rect.h / scene.lignes)
    for o in scene.objets:
        cx = rect.x + o.x * rect.w
        cy = rect.top - o.y * rect.h
        pictos.dessiner(c, o.kind, cx, cy, slot * o.taille, theme)


def positions_differences(rect: Rect, jeu: JeuDifferences) -> list[tuple[float, float, float]]:
    """Centre et rayon (dans rect) de chaque différence, pour les corrigés."""
    sc = jeu.scene_a
    slot = min(rect.w / sc.colonnes, rect.h / sc.lignes)
    pa, pb = jeu.scene_a.par_slot(), jeu.scene_b.par_slot()
    out = []
    for d in jeu.differences:
        o = pa.get(d["slot"]) or pb.get(d["slot"])
        out.append((rect.x + o.x * rect.w, rect.top - o.y * rect.h, slot * 0.48))
    return out


def dessiner_differences(c: Canvas, rect: Rect, jeu: JeuDifferences, theme: Theme,
                         solution: bool = False) -> tuple[Rect, Rect]:
    ratio = jeu.scene_a.colonnes / jeu.scene_a.lignes * 0.92
    gap = 9 * mm
    h = min((rect.h - gap) / 2, rect.w / ratio)
    w = h * ratio
    ra = Rect(rect.cx - w / 2, rect.top - h, w, h)
    rb = Rect(rect.cx - w / 2, rect.top - 2 * h - gap, w, h)
    dessiner_scene(c, ra, jeu.scene_a, theme)
    dessiner_scene(c, rb, jeu.scene_b, theme)
    ecrire(c, "Image 1", ra.x + 6, ra.top + 4, fonts.TITRE_DEMI, 10)
    ecrire(c, "Image 2", rb.x + 6, rb.top + 4, fonts.TITRE_DEMI, 10)
    if solution:
        for cx, cy, r in positions_differences(rb, jeu):
            entourer(c, cx, cy, r, r, theme)
    return ra, rb


def dessiner_comptage(c: Canvas, rect: Rect, jeu: JeuComptage, theme: Theme, solution: bool = False) -> None:
    zone_q_h = 30 * mm
    scene_h = min(rect.h - zone_q_h - 6 * mm, rect.w / jeu.ratio)
    scene_w = scene_h * jeu.ratio
    sr = Rect(rect.cx - scene_w / 2, rect.top - scene_h, scene_w, scene_h)
    c.saveState()
    c.setLineWidth(1.6)
    c.roundRect(sr.x - 4, sr.y - 4, sr.w + 8, sr.h + 8, 6, stroke=1, fill=0)
    c.restoreState()
    for o in jeu.objets:
        pictos.dessiner(c, o.kind, sr.x + o.x * sr.w, sr.top - o.y * sr.h, o.taille * sr.h, theme)
    # Questions : pictogramme + case réponse.
    n = len(jeu.kinds)
    q = Rect(rect.x, rect.y, rect.w, zone_q_h)
    largeur = q.w / n
    for i, k in enumerate(jeu.kinds):
        cx = q.x + (i + 0.5) * largeur
        pictos.dessiner(c, k, cx - 14 * mm, q.cy, 15 * mm, theme)
        case_reponse(c, cx - 2 * mm, q.cy - 8 * mm, 16 * mm, 16 * mm,
                     str(jeu.reponses[k]) if solution else None, 20)
        ecrire(c, nom(k, 2), cx + 6 * mm, q.cy - 14 * mm, fonts.TEXTE, 10, align="center")


def dessiner_coloriage(c: Canvas, rect: Rect, cc: ColoriageCode, theme: Theme, solution: bool = False,
                       avec_legende: bool = True) -> None:
    h, w = len(cc.grille), len(cc.grille[0])
    leg_h = 26 * mm if avec_legende else 0
    cell = min(rect.w / w, (rect.h - leg_h) / h, 13 * mm)
    gx = rect.cx - w * cell / 2
    gy = rect.top
    c.saveState()
    for r in range(h):
        for col in range(w):
            v = cc.grille[r][col]
            x, y = gx + col * cell, gy - (r + 1) * cell
            if solution and v:
                nomc = cc.legende[v]
                c.setFillColor(white if theme.eco else HexColor(COULEURS_CRAYON[nomc]))
                c.rect(x, y, cell, cell, stroke=0, fill=1)
            if not solution and v:
                ecrire(c, str(v), x + cell / 2, y + cell / 2 - cell * 0.2, fonts.TITRE_DEMI,
                       max(9, cell * 0.5), align="center")
            if solution and theme.eco and v:
                ecrire(c, str(v), x + cell / 2, y + cell / 2 - cell * 0.2, fonts.TITRE_DEMI,
                       max(5, cell * 0.5), align="center")
    c.setStrokeColor(NOIR)
    c.setLineWidth(0.6 if not solution else 0.3)
    for r in range(h + 1):
        c.line(gx, gy - r * cell, gx + w * cell, gy - r * cell)
    for col in range(w + 1):
        c.line(gx + col * cell, gy, gx + col * cell, gy - h * cell)
    c.setLineWidth(1.4)
    c.rect(gx, gy - h * cell, w * cell, h * cell, stroke=1, fill=0)
    c.restoreState()
    if avec_legende:
        dessiner_legende(c, Rect(rect.x, gy - h * cell - leg_h, rect.w, leg_h - 4 * mm), cc, theme)


def dessiner_legende(c: Canvas, rect: Rect, cc: ColoriageCode, theme: Theme) -> None:
    n = len(cc.legende)
    par_ligne = min(n, 3)
    lignes = (n + par_ligne - 1) // par_ligne
    lw = rect.w / par_ligne
    lh = min(rect.h / lignes, 11 * mm)
    for i, (num, nomc) in enumerate(sorted(cc.legende.items())):
        r, col = divmod(i, par_ligne)
        x = rect.x + col * lw + 8
        y = rect.top - (r + 0.5) * lh
        c.saveState()
        c.setLineWidth(1.1)
        c.setStrokeColor(NOIR)
        if theme.eco:
            c.setFillColor(white)
        else:
            c.setFillColor(HexColor(COULEURS_CRAYON[nomc]))
        c.roundRect(x, y - 4 * mm, 12 * mm, 8 * mm, 3, stroke=1, fill=1)
        c.restoreState()
        ecrire(c, f"{num} = {nomc}", x + 15 * mm, y - 2 * mm, fonts.TITRE, 14)
