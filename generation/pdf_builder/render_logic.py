"""Rendu des activités de logique et de leurs corrigés."""
from __future__ import annotations

from reportlab.lib.colors import white
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from generation.generators.figures import Figure, nom_figure
from generation.generators.logic_puzzles import LETTRES, Activite
from generation.pdf_builder import fonts
from generation.pdf_builder.layout import Rect
from generation.pdf_builder.render_common import (
    ETOILES_NIVEAUX, case_reponse, entourer, etiquette, etoile,
)
from generation.pdf_builder.shapes import dessiner_figure
from generation.pdf_builder.text import ecrire, hauteur_paragraphe, paragraphe
from generation.pdf_builder.theme import NOIR, Theme


def entete_activite(c: Canvas, rect: Rect, a: Activite, theme: Theme, titre: str | None = None,
                    taille_consigne: float = 13.5) -> Rect:
    """« Activité 7 · Suite de formes » + étoiles + consigne. Renvoie la zone de contenu."""
    t = titre or f"Activité {a.numero} · {a.nom_type}"
    ecrire(c, t, rect.x, rect.top - 16, fonts.TITRE, 16)
    for i in range(3):
        etoile(c, rect.right - 6 - i * 13, rect.top - 11, 5.2, (2 - i) < ETOILES_NIVEAUX[a.niveau], theme)
    h = hauteur_paragraphe(a.consigne, rect.w, fonts.TEXTE, taille_consigne)
    paragraphe(c, a.consigne, Rect(rect.x, rect.top - 24 - h, rect.w, h + 2), fonts.TEXTE, taille_consigne)
    return Rect(rect.x, rect.y, rect.w, rect.h - 30 - h)


def dessiner_activite(c: Canvas, rect: Rect, a: Activite, theme: Theme, solution: bool = False) -> None:
    {
        "suite_formes": _suite_formes,
        "suite_nombres": _suite_nombres,
        "intrus": _intrus,
        "grille": _grille,
        "association": _association,
    }[a.type](c, rect, a, theme, solution)


def _point_interrogation(c: Canvas, cx: float, cy: float, s: float) -> None:
    c.saveState()
    c.setDash(3, 2)
    c.setLineWidth(1.2)
    c.setStrokeColor(NOIR)
    c.roundRect(cx - s / 2, cy - s / 2, s, s, 4, stroke=1, fill=0)
    c.restoreState()
    ecrire(c, "?", cx, cy - s * 0.25, fonts.TITRE, s * 0.7, align="center")


def _rangee_options(c: Canvas, rect: Rect, options: list[Figure], reponse: int, theme: Theme,
                    solution: bool, s_max: float = 20 * mm) -> None:
    n = len(options)
    s = min(s_max, rect.w / (n * 1.6), rect.h * 0.62)
    largeur = n * s * 1.6
    x0 = rect.cx - largeur / 2
    cy = rect.y + rect.h * 0.58
    for i, o in enumerate(options):
        cx = x0 + (i + 0.5) * s * 1.6
        dessiner_figure(c, o, cx, cy, s)
        etiquette(c, cx, cy - s * 0.5 - 12, LETTRES[i], 8)
        if solution and i == reponse:
            entourer(c, cx, cy - 6, s * 0.72, s * 0.78, theme)


def _suite_formes(c, rect, a, theme, solution):
    aff = a.donnees["affiches"]
    k = len(aff) + 1
    haut, bas = rect.split_v(2, gap=4, poids=[1, 1.15])
    s = min(19 * mm, haut.w / (k * 1.25), haut.h * 0.8)
    x0 = haut.cx - k * s * 1.25 / 2
    for i, f in enumerate(aff):
        dessiner_figure(c, f, x0 + (i + 0.5) * s * 1.25, haut.cy, s)
    cx_q = x0 + (k - 0.5) * s * 1.25
    if solution:
        dessiner_figure(c, a.donnees["options"][a.reponse], cx_q, haut.cy, s)
    else:
        _point_interrogation(c, cx_q, haut.cy, s * 1.1)
    _rangee_options(c, bas, a.donnees["options"], a.reponse, theme, solution)


def _suite_nombres(c, rect, a, theme, solution):
    termes, trous = a.donnees["termes"], a.donnees["trous"]
    n = len(termes)
    w = min(24 * mm, rect.w / (n * 1.3))
    h = min(18 * mm, rect.h * 0.5)
    x0 = rect.cx - n * w * 1.3 / 2
    y = rect.cy - h / 2
    for i, t in enumerate(termes):
        x = x0 + i * w * 1.3 + w * 0.15
        if i in trous:
            case_reponse(c, x, y, w, h, str(t) if solution else None, 20)
            if solution:
                entourer(c, x + w / 2, y + h / 2, w * 0.62, h * 0.7, theme)
        else:
            c.saveState()
            c.setFillColor(white if theme.eco else theme.accent_clair)
            c.setStrokeColor(NOIR)
            c.setLineWidth(1.3)
            c.roundRect(x, y, w, h, 4, stroke=1, fill=1)
            c.restoreState()
            ecrire(c, str(t), x + w / 2, y + h / 2 - 7, fonts.TITRE, 20, align="center")
        if i < n - 1:
            ax = x + w + w * 0.15
            c.saveState()
            c.setLineWidth(1)
            c.setStrokeColor(NOIR)
            c.line(ax - 4, y + h + 6, ax + 4, y + h + 6)
            c.line(ax + 1, y + h + 9, ax + 4, y + h + 6)
            c.line(ax + 1, y + h + 3, ax + 4, y + h + 6)
            c.restoreState()


def _intrus(c, rect, a, theme, solution):
    figs = a.donnees["figures"]
    n = len(figs)
    s = min(22 * mm, rect.w / (n * 1.45), rect.h * 0.55)
    x0 = rect.cx - n * s * 1.45 / 2
    cy = rect.cy + 8
    for i, f in enumerate(figs):
        cx = x0 + (i + 0.5) * s * 1.45
        dessiner_figure(c, f, cx, cy, s)
        etiquette(c, cx, cy - s * 0.5 - 14, LETTRES[i], 8)
        if solution and i == a.reponse:
            entourer(c, cx, cy - 6, s * 0.7, s * 0.85, theme)


def _grille(c, rect, a, theme, solution):
    grille, trou = a.donnees["grille"], a.donnees["trou"]
    g, opts = rect.split_h(2, gap=8, poids=[1.25, 1])
    cell = min(24 * mm, g.h / 3, g.w / 3)
    x0, y0 = g.cx - 1.5 * cell, g.cy + 1.5 * cell
    c.saveState()
    c.setLineWidth(1.4)
    c.setStrokeColor(NOIR)
    for i in range(4):
        c.line(x0, y0 - i * cell, x0 + 3 * cell, y0 - i * cell)
        c.line(x0 + i * cell, y0, x0 + i * cell, y0 - 3 * cell)
    c.restoreState()
    for r in range(3):
        for col in range(3):
            cx, cy = x0 + (col + 0.5) * cell, y0 - (r + 0.5) * cell
            if (r, col) == tuple(trou):
                if solution:
                    dessiner_figure(c, a.donnees["options"][a.reponse], cx, cy, cell * 0.68)
                else:
                    ecrire(c, "?", cx, cy - cell * 0.22, fonts.TITRE, cell * 0.6, align="center")
            else:
                dessiner_figure(c, grille[r][col], cx, cy, cell * 0.68)
    options = a.donnees["options"]
    n = len(options)
    cols = 2
    lignes = (n + 1) // 2
    s = min(18 * mm, opts.w / (cols * 1.9), opts.h / (lignes * 1.7))
    for i, o in enumerate(options):
        rr, cc = divmod(i, cols)
        cx = opts.cx + (cc - (cols - 1) / 2) * s * 1.6
        cy = opts.cy + ((lignes - 1) / 2 - rr) * s * 1.75 + 8
        dessiner_figure(c, o, cx, cy, s)
        etiquette(c, cx, cy - s * 0.5 - 11, LETTRES[i], 7.5)
        if solution and i == a.reponse:
            entourer(c, cx, cy - 5, s * 0.75, s * 0.85, theme)


def _points(c: Canvas, cx: float, cy: float, n: int, s: float) -> None:
    """Groupe de n points (1 à 10), disposé comme sur un domino (2 rangées de 5 max)."""
    r = s * 0.075
    pas = s * 0.21
    rangees = [n] if n <= 5 else [5, n - 5]
    c.saveState()
    c.setFillColor(NOIR)
    for j, nb in enumerate(rangees):
        y = cy + (len(rangees) - 1) * pas * 0.5 - j * pas
        for i in range(nb):
            c.circle(cx + (i - (nb - 1) / 2) * pas, y, r, stroke=0, fill=1)
    c.restoreState()


def _item_association(c: Canvas, regle: str, item, cx: float, cy: float, s: float, cote: str) -> None:
    if regle == "quantite":
        if cote == "g":
            c.saveState()
            c.setLineWidth(1)
            c.roundRect(cx - s * 0.6, cy - s * 0.35, s * 1.2, s * 0.7, 5, stroke=1, fill=0)
            c.restoreState()
            _points(c, cx, cy, item, s)
        else:
            ecrire(c, str(item), cx, cy - s * 0.2, fonts.TITRE, s * 0.6, align="center")
    else:
        dessiner_figure(c, item, cx, cy, s)


def _association(c, rect, a, theme, solution):
    g, d = a.donnees["gauche"], a.donnees["droite"]
    regle = a.donnees["regle"]
    n = len(g)
    pas = min(26 * mm, rect.h / n)
    s = min(pas * 0.8, 18 * mm)
    xg, xd = rect.x + rect.w * 0.22, rect.right - rect.w * 0.22
    y_top = rect.cy + (n - 1) * pas / 2
    pts_g, pts_d = [], []
    for i in range(n):
        y = y_top - i * pas
        _item_association(c, regle, g[i], xg, y, s, "g")
        _item_association(c, regle, d[i], xd, y, s, "d")
        etiquette(c, xg - s * 0.75 - 14, y, str(i + 1), 7.5)
        etiquette(c, xd + s * 0.75 + 14, y, LETTRES[i], 7.5)
        pts_g.append((xg + s * 0.7 + 8, y))
        pts_d.append((xd - s * 0.7 - 8, y))
    c.saveState()
    c.setFillColor(NOIR)
    for (x, y) in pts_g + pts_d:
        c.circle(x, y, 3.2, stroke=0, fill=1)
    if solution:
        c.setStrokeColor(theme.trace_solution)
        c.setLineWidth(2.2)
        for i, j in enumerate(a.reponse):
            c.line(*pts_g[i], *pts_d[j])
    c.restoreState()


# ======================================================================= corrigés (texte)
def texte_solution(a: Activite) -> str:
    if a.type in ("suite_formes", "grille"):
        f = a.donnees["options"][a.reponse]
        avec_motif = a.type == "suite_formes" or "motif" in a.donnees.get("regles", [])
        return f"Réponse {LETTRES[a.reponse]} : {nom_figure(f, avec_motif=avec_motif)}."
    if a.type == "suite_nombres":
        nb = " et ".join(str(v) for v in a.reponse)
        return f"{'Les nombres manquants sont' if len(a.reponse) > 1 else 'Le nombre manquant est'} {nb}. {a.explication}"
    if a.type == "intrus":
        return f"Réponse {LETTRES[a.reponse]} : {a.explication[0].lower()}{a.explication[1:]}"
    if a.type == "association":
        paires = ", ".join(f"{i + 1} → {LETTRES[j]}" for i, j in enumerate(a.reponse))
        return f"{paires}."
    raise ValueError(a.type)


def figure_solution(a: Activite) -> Figure | None:
    if a.type in ("suite_formes", "grille"):
        return a.donnees["options"][a.reponse]
    if a.type == "intrus":
        return a.donnees["figures"][a.reponse]
    return None
