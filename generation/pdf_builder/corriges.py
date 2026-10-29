"""Corrigés : éléments de solution et mise en pages automatique (2 colonnes)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from generation.generators.coloriage import ColoriageCode
from generation.generators.enigmes import CheminNombres, CodeSecret, Probleme
from generation.generators.logic_puzzles import Activite
from generation.generators.mazes import Labyrinthe
from generation.generators.nonograms import Nonogramme
from generation.generators.observation import JeuComptage, JeuDifferences, nom
from generation.pdf_builder import fonts
from generation.pdf_builder.document import CADRE_CONTENU, PageCtx, PageSpec
from generation.pdf_builder.layout import Rect
from generation.pdf_builder.render_common import bloc_titre
from generation.pdf_builder.render_enigmes import dessiner_chemin
from generation.pdf_builder.render_logic import dessiner_activite, figure_solution, texte_solution
from generation.pdf_builder.render_mazes import dessiner_labyrinthe
from generation.pdf_builder.render_nonograms import dessiner_mini
from generation.pdf_builder.render_common import entourer
from generation.pdf_builder.render_observation import dessiner_coloriage, dessiner_scene, positions_differences
from generation.pdf_builder.shapes import dessiner_figure
from generation.pdf_builder.text import ecrire, hauteur_paragraphe, paragraphe, taille_ajustee
from generation.pdf_builder.theme import Theme

LARGEUR_COLONNE = (CADRE_CONTENU.w - 8 * mm) / 2
ESPACE = 6 * mm


@dataclass
class ElementCorrige:
    titre: str
    hauteur: float                      # hauteur du contenu (hors titre), en points
    dessin: Callable[[Canvas, Rect, Theme], None]
    ref: str | None = None              # activité corrigée (pour afficher sa page)
    large: bool = False                 # occupe toute la largeur


def _titre(ctx: PageCtx, e: ElementCorrige) -> str:
    if e.ref is None or ctx.livre is None:
        return e.titre
    try:
        return f"{e.titre} · page {ctx.page_de(e.ref)}"
    except KeyError:
        return e.titre


def paginer(elements: list[ElementCorrige], titre: str = "Corrigés", section: str = "Corrigés",
            legende: str = "Corrigés") -> list[PageSpec]:
    """Mise en pages en deux colonnes « au plus court » : chaque élément étroit va dans la
    colonne la moins remplie ; un élément large occupe toute la largeur sous les deux colonnes."""
    h_titre_page = 16 * mm
    dispo = CADRE_CONTENU.h - h_titre_page
    pages: list[list[tuple[ElementCorrige, int, float]]] = [[]]  # (élément, colonne -1/0/1, y depuis le haut)
    cols = [0.0, 0.0]
    for e in elements:
        h = e.hauteur + 9 * mm
        if e.large:
            y = max(cols)
            if pages[-1] and y + h > dispo:
                pages.append([])
                cols = [0.0, 0.0]
                y = 0.0
            pages[-1].append((e, -1, y))
            cols = [y + h + ESPACE] * 2
            continue
        ordre = sorted(range(2), key=lambda k: cols[k])
        place = next((k for k in ordre if cols[k] + h <= dispo), None)
        if place is None:
            pages.append([])
            cols = [0.0, 0.0]
            place = 0
        pages[-1].append((e, place, cols[place]))
        cols[place] += h + ESPACE
    return [_page(contenu, titre if i == 0 else f"{titre} (suite)", section, f"{legende} — page {i + 1}")
            for i, contenu in enumerate(pages)]


def _page(contenu: list[tuple[ElementCorrige, int, float]], titre: str, section: str, legende: str) -> PageSpec:
    def draw(ctx: PageCtx) -> None:
        zone = bloc_titre(ctx.c, ctx.cadre, titre, None, ctx.theme)
        for e, col, y in contenu:
            h = e.hauteur + 9 * mm
            if col < 0:
                r = Rect(zone.x, zone.top - y - h, zone.w, h)
            else:
                r = Rect(zone.x + col * (LARGEUR_COLONNE + 8 * mm), zone.top - y - h, LARGEUR_COLONNE, h)
            t = _titre(ctx, e)
            ecrire(ctx.c, t, r.x, r.top - 11, fonts.TITRE_DEMI, taille_ajustee(t, fonts.TITRE_DEMI, 11.5, r.w, 7))
            ctx.c.saveState()
            ctx.c.setLineWidth(0.5)
            ctx.c.line(r.x, r.top - 15, r.right, r.top - 15)
            ctx.c.restoreState()
            e.dessin(ctx.c, Rect(r.x, r.y, r.w, r.h - 9 * mm), ctx.theme)

    return PageSpec("solution", legende, draw, section=section)


# ======================================================================= éléments par type
def labyrinthe(lab: Labyrinthe, titre: str, ref: str, depart: str, arrivee: str,
               hauteur: float = 72 * mm) -> ElementCorrige:
    def d(c, r, t):
        dessiner_labyrinthe(c, r, lab, t, depart, arrivee, solution=True, etiquettes=False)
    return ElementCorrige(titre, hauteur, d, ref)


def logique(a: Activite, ref: str | None = None, titre: str | None = None) -> ElementCorrige:
    texte = texte_solution(a)
    fig = figure_solution(a)
    titre = titre or f"Activité {a.numero} · {a.nom_type}"
    if a.type in ("association",) or a.type == "grille":
        # Corrigé visuel (lignes tracées / case complétée).
        def d(c, r, t):
            sous = Rect(r.x, r.y, r.w, r.h - 14)
            paragraphe(c, texte, Rect(r.x, r.top - 14, r.w, 14), fonts.TEXTE, 11)
            dessiner_activite(c, sous, a, t, solution=True)
        return ElementCorrige(titre, 62 * mm if a.type == "association" else 58 * mm, d, ref or a.id)
    h_txt = hauteur_paragraphe(texte, LARGEUR_COLONNE - (16 * mm if fig else 0), fonts.TEXTE, 11.5)

    def d2(c, r, t):
        larg = r.w - (16 * mm if fig else 0)
        paragraphe(c, texte, Rect(r.x, r.y, larg, r.h - 2), fonts.TEXTE, 11.5)
        if fig:
            dessiner_figure(c, fig, r.right - 8 * mm, r.top - 9 * mm, 11 * mm)
    return ElementCorrige(titre, max(h_txt + 4, 20 * mm if fig else 0), d2, ref or a.id)


def nonogramme(n: Nonogramme, titre: str, ref: str, hauteur: float = 34 * mm) -> ElementCorrige:
    def d(c, r, t):
        img = Rect(r.x, r.y, r.h, r.h)
        dessiner_mini(c, img.inset(2), n.dessin)
        ecrire(c, n.titre, r.x + r.h + 6 * mm, r.cy - 5, fonts.TITRE, 15)
    return ElementCorrige(titre, hauteur, d, ref)


def differences(jeu: JeuDifferences, titre: str, ref: str) -> ElementCorrige:
    textes = [f"{i + 1}. {d['texte'][0].upper()}{d['texte'][1:]}." for i, d in enumerate(jeu.differences)]

    def d(c, r, t):
        gauche, droite = r.split_h(2, gap=6 * mm, poids=[1.25, 1])
        # On ne montre que l'image 2, différences entourées.
        ratio = jeu.scene_b.colonnes / jeu.scene_b.lignes * 0.92
        h = min(gauche.h, gauche.w / ratio)
        sr = Rect(gauche.x, gauche.top - h, h * ratio, h)
        dessiner_scene(c, sr, jeu.scene_b, t)
        for cx, cy, rr in positions_differences(sr, jeu):
            entourer(c, cx, cy, rr, rr, t)
        paragraphe(c, "<br/>".join(textes), droite, fonts.TEXTE, 10.5)
    return ElementCorrige(titre, 62 * mm, d, ref, large=True)


def comptage(jeu: JeuComptage, titre: str, ref: str) -> ElementCorrige:
    texte = "Il y a " + ", ".join(f"{jeu.reponses[k]} {nom(k, jeu.reponses[k])}" for k in jeu.kinds) + "."

    def d(c, r, t):
        paragraphe(c, texte, r, fonts.TEXTE, 11.5)
    return ElementCorrige(titre, hauteur_paragraphe(texte, LARGEUR_COLONNE, fonts.TEXTE, 11.5) + 4, d, ref)


def coloriage(cc: ColoriageCode, titre: str, ref: str) -> ElementCorrige:
    def d(c, r, t):
        dessiner_coloriage(c, Rect(r.x, r.y, r.h, r.h), cc, t, solution=True, avec_legende=False)
        ecrire(c, cc.titre, r.x + r.h + 6 * mm, r.cy - 5, fonts.TITRE, 15)
    return ElementCorrige(titre, 34 * mm, d, ref)


def code(cs: CodeSecret, titre: str, ref: str) -> ElementCorrige:
    def d(c, r, t):
        ecrire(c, "Le message secret est :", r.x, r.top - 14, fonts.TEXTE, 11.5)
        ecrire(c, cs.message, r.x, r.top - 34, fonts.TITRE, 18)
    return ElementCorrige(titre, 15 * mm, d, ref)


def problemes(probs: list[Probleme], titre: str, ref: str) -> ElementCorrige:
    signes = {"+": "+", "-": "−", "x": "×"}
    lignes = [f"Énigme {i + 1} : {p.a} {signes[p.operation]} {p.b} = <b>{p.reponse}</b>"
              + (f" {p.unite}" if p.unite else "") for i, p in enumerate(probs)]
    texte = "<br/>".join(lignes)

    def d(c, r, t):
        paragraphe(c, texte, r, fonts.TEXTE, 11.5)
    return ElementCorrige(titre, hauteur_paragraphe(texte, LARGEUR_COLONNE, fonts.TEXTE, 11.5) + 4, d, ref)


def chemin(ch: CheminNombres, titre: str, ref: str, depart: str, arrivee: str) -> ElementCorrige:
    def d(c, r, t):
        dessiner_chemin(c, r, ch, t, solution=True, depart=depart, arrivee=arrivee)
    return ElementCorrige(titre, 50 * mm, d, ref)
